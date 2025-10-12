"""Affordance precondition compilation and evaluation helpers."""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

__all__ = [
    "CompiledPrecondition",
    "PreconditionEvaluationError",
    "PreconditionSyntaxError",
    "compile_preconditions",
    "evaluate_preconditions",
]


class PreconditionSyntaxError(ValueError):
    """Raised when a manifest precondition has invalid syntax."""


class PreconditionEvaluationError(RuntimeError):
    """Raised when evaluation fails due to missing context or type errors."""


_ALLOWED_COMPARE_OPS = (
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
)
_ALLOWED_BOOL_OPS = (ast.And, ast.Or)
_ALLOWED_UNARY_OPS = (ast.Not, ast.USub, ast.UAdd)
_ALLOWED_NODE_TYPES = (
    ast.Expression,
    ast.BoolOp,
    ast.Compare,
    ast.Name,
    ast.Attribute,
    ast.Subscript,
    ast.Constant,
    ast.UnaryOp,
    ast.Tuple,
    ast.List,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.And,
    ast.Or,
    ast.Load,
    ast.USub,
    ast.UAdd,
    ast.Not,
)
_name_pattern = re.compile(r"\b(true|false|null)\b", re.IGNORECASE)
_name_replacements = {
    "true": "True",
    "false": "False",
    "null": "None",
}


@dataclass(frozen=True)
class CompiledPrecondition:
    """Stores the parsed AST and metadata for a precondition."""

    source: str
    tree: ast.AST
    identifiers: tuple[str, ...]


class _IdentifierCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    # pylint: disable=invalid-name
    def visit_Name(self, node: ast.Name) -> None:
        """Collect bare identifiers used in the expression."""

        self.names.add(node.id)
        self.generic_visit(node)


def _normalize_expression(expression: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        token = match.group(0)
        return _name_replacements.get(token.lower(), token)

    return _name_pattern.sub(_replace, expression)


def _validate_tree(tree: ast.AST, source: str) -> tuple[str, ...]:
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODE_TYPES):
            raise PreconditionSyntaxError(
                f"Unsupported syntax in precondition '{source}':"
                f" {type(node).__name__}"
            )
        if isinstance(node, ast.Call):
            raise PreconditionSyntaxError(
                f"Function calls are not permitted in precondition '{source}'"
            )
        if isinstance(node, ast.BoolOp) and not isinstance(node.op, _ALLOWED_BOOL_OPS):
            raise PreconditionSyntaxError(
                f"Unsupported boolean operator in precondition '{source}'"
            )
        if isinstance(node, ast.UnaryOp) and not isinstance(
            node.op, _ALLOWED_UNARY_OPS
        ):
            raise PreconditionSyntaxError(
                f"Unsupported unary operator in precondition '{source}'"
            )
        if isinstance(node, ast.Compare):
            for op in node.ops:
                if not isinstance(op, _ALLOWED_COMPARE_OPS):
                    raise PreconditionSyntaxError(
                        f"Unsupported comparison operator in precondition '{source}'"
                    )
    collector = _IdentifierCollector()
    collector.visit(tree)
    return tuple(sorted(collector.names))


def compile_preconditions(expressions: Iterable[str]) -> tuple[CompiledPrecondition, ...]:
    """Compile manifest preconditions, raising on syntax errors."""

    compiled: list[CompiledPrecondition] = []
    for raw in expressions:
        expression = str(raw or "").strip()
        if not expression:
            continue
        normalized = _normalize_expression(expression)
        try:
            tree = ast.parse(normalized, mode="eval")
        except SyntaxError as exc:  # pragma: no cover - defensive
            raise PreconditionSyntaxError(
                f"Invalid syntax in precondition '{expression}': {exc.msg}"
            ) from exc
        identifiers = _validate_tree(tree, expression)
        compiled.append(
            CompiledPrecondition(source=expression, tree=tree, identifiers=identifiers)
        )
    return tuple(compiled)


def compile_precondition(expression: str) -> CompiledPrecondition:
    """Compile a single precondition expression."""

    return compile_preconditions([expression])[0]


def _resolve_name(name: str, context: Mapping[str, Any]) -> Any:
    if name in context:
        return context[name]
    # Dotted identifiers are not expected here; they are handled via Attribute nodes.
    return None


def _resolve_attr(value: Any, attr: str) -> Any:
    if isinstance(value, Mapping):
        return value.get(attr)
    if hasattr(value, attr):
        return getattr(value, attr)
    return None


def _resolve_subscript(value: Any, key: Any) -> Any:
    try:
        return value[key]
    except (KeyError, TypeError, IndexError):
        return None


def _evaluate(node: ast.AST, context: Mapping[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body, context)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return _resolve_name(node.id, context)
    if isinstance(node, ast.Attribute):
        base = _evaluate(node.value, context)
        return _resolve_attr(base, node.attr)
    if isinstance(node, ast.Subscript):
        base = _evaluate(node.value, context)
        if isinstance(node.slice, ast.Slice):
            raise PreconditionEvaluationError("Slices are not supported in preconditions")
        key = _evaluate(node.slice, context)
        return _resolve_subscript(base, key)
    if isinstance(node, ast.UnaryOp):
        operand = _evaluate(node.operand, context)
        if isinstance(node.op, ast.Not):
            return not bool(operand)
        if isinstance(node.op, ast.USub):
            return -float(operand)
        if isinstance(node.op, ast.UAdd):
            return +float(operand)
        raise PreconditionEvaluationError(
            f"Unsupported unary operator: {type(node.op).__name__}"
        )
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            for value in node.values:
                if not bool(_evaluate(value, context)):
                    return False
            return True
        if isinstance(node.op, ast.Or):
            for value in node.values:
                if bool(_evaluate(value, context)):
                    return True
            return False
        raise PreconditionEvaluationError(
            f"Unsupported boolean operator: {type(node.op).__name__}"
        )
    if isinstance(node, ast.Compare):
        left = _evaluate(node.left, context)
        for operator, comparator in zip(node.ops, node.comparators):
            right = _evaluate(comparator, context)
            result = _apply_compare(operator, left, right)
            if not result:
                return False
            left = right
        return True
    if isinstance(node, (ast.Tuple, ast.List)):
        return [_evaluate(element, context) for element in node.elts]
    raise PreconditionEvaluationError(
        f"Unsupported AST node during evaluation: {type(node).__name__}"
    )


def _apply_compare(operator: ast.cmpop, left: Any, right: Any) -> bool:
    if isinstance(operator, ast.Eq):
        return bool(left == right)
    if isinstance(operator, ast.NotEq):
        return bool(left != right)
    if isinstance(operator, ast.Lt):
        return bool(left is not None and right is not None and left < right)
    if isinstance(operator, ast.LtE):
        return bool(left is not None and right is not None and left <= right)
    if isinstance(operator, ast.Gt):
        return bool(left is not None and right is not None and left > right)
    if isinstance(operator, ast.GtE):
        return bool(left is not None and right is not None and left >= right)
    if isinstance(operator, ast.In):
        if isinstance(right, (str, bytes)):
            return str(left) in right
        if isinstance(right, Mapping):
            return left in right
        if isinstance(right, (Sequence, set, frozenset)):
            return left in right
        return False
    if isinstance(operator, ast.NotIn):
        if isinstance(right, (str, bytes)):
            return str(left) not in right
        if isinstance(right, Mapping):
            return left not in right
        if isinstance(right, (Sequence, set, frozenset)):
            return left not in right
        return True
    raise PreconditionEvaluationError(
        f"Unsupported comparison operator: {type(operator).__name__}"
    )


def evaluate_preconditions(
    preconditions: Sequence[CompiledPrecondition],
    context: Mapping[str, Any],
) -> tuple[bool, CompiledPrecondition | None]:
    """Evaluate compiled preconditions against the provided context.

    Returns
    -------
    tuple
        ``(True, None)`` if all preconditions pass, otherwise ``(False, failed)``
        where ``failed`` references the first failing precondition.
    """

    for compiled in preconditions:
        try:
            result = bool(_evaluate(compiled.tree, context))
        except PreconditionEvaluationError:
            return False, compiled
        if not result:
            return False, compiled
    return True, None
