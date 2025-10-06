"""Agent-facing services and primitives."""

from __future__ import annotations

from .employment import EmploymentService
from .interfaces import (
    AgentRegistryProtocol,
    EmploymentServiceProtocol,
    RelationshipServiceProtocol,
)
from .registry import AgentRegistry
from .relationships_service import RelationshipService
from .snapshot import AgentSnapshot

from townlet.world.employment_runtime import EmploymentRuntime
from townlet.world.employment_service import (
    EmploymentCoordinator,
    EmploymentEngine,
    create_employment_coordinator,
)
from townlet.world.relationships import (
    RelationshipLedger,
    RelationshipParameters,
    RelationshipTie,
)

__all__ = [
    "AgentRegistry",
    "AgentSnapshot",
    "EmploymentCoordinator",
    "EmploymentEngine",
    "EmploymentRuntime",
    "EmploymentService",
    "EmploymentServiceProtocol",
    "RelationshipLedger",
    "RelationshipParameters",
    "RelationshipServiceProtocol",
    "RelationshipService",
    "RelationshipTie",
    "create_employment_coordinator",
    "AgentRegistryProtocol",
]
