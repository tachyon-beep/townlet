"""Telemetry transform pipeline primitives."""

from __future__ import annotations

import copy
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.telemetry.interfaces import TelemetryEvent, TelemetryTransformProtocol

__all__ = [
    "TransformPipelineConfig",
    "TelemetryTransformPipeline",
    "SnapshotEventNormalizer",
]


@dataclass(slots=True)
class TransformPipelineConfig:
    """Configuration describing the ordered telemetry transforms to apply."""

    transforms: Sequence["TelemetryTransformProtocol"] = ()

    def build_pipeline(self) -> "TelemetryTransformPipeline":
        """Construct a pipeline instance from the configured transforms."""

        return TelemetryTransformPipeline(self.transforms)


class TelemetryTransformPipeline:
    """Applies telemetry transforms in sequence to an event stream."""

    def __init__(self, transforms: Sequence["TelemetryTransformProtocol"]) -> None:
        self._transforms: list["TelemetryTransformProtocol"] = list(transforms)

    def process(self, events: Iterable["TelemetryEvent"]) -> list["TelemetryEvent"]:
        """Run the configured transforms over the provided events."""

        processed: list["TelemetryEvent"] = []
        for event in events:
            current: "TelemetryEvent" | None = event
            for transform in self._transforms:
                if current is None:
                    break
                current = transform.process(current)
            if current is not None:
                processed.append(current)
        for transform in self._transforms:
            for pending in transform.flush():
                processed.append(pending)
        return processed


class SnapshotEventNormalizer:
    """Ensures snapshot payloads are detached copies for downstream consumers."""

    def process(self, event: "TelemetryEvent") -> "TelemetryEvent" | None:
        if event.kind != "snapshot":
            return event
        payload_copy = copy.deepcopy(event.payload)
        metadata_copy = dict(event.metadata)
        from townlet.telemetry.interfaces import TelemetryEvent

        return TelemetryEvent(
            tick=int(event.tick),
            kind=event.kind,
            payload=payload_copy,
            metadata=metadata_copy,
        )

    def flush(self) -> Iterable["TelemetryEvent"]:  # pragma: no cover - no buffering
        return ()
