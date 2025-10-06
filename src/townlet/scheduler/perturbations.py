"""Perturbation scheduler scaffolding."""

from __future__ import annotations

import random
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from townlet.config import (
    ArrangedMeetEventConfig,
    BlackoutEventConfig,
    OutageEventConfig,
    PerturbationEventConfig,
    PerturbationKind,
    PerturbationSchedulerConfig,
    PriceSpikeEventConfig,
    SimulationConfig,
)
from townlet.utils import decode_rng_state, encode_rng_state
from townlet.world.grid import WorldState


@dataclass
class ScheduledPerturbation:
    """Represents a perturbation that is pending or active in the world."""

    event_id: str
    spec_name: str
    kind: PerturbationKind
    started_at: int
    ends_at: int
    payload: dict[str, object] = field(default_factory=dict)
    targets: list[str] = field(default_factory=list)


class PerturbationScheduler:
    """Injects bounded random events into the world."""

    def __init__(
        self,
        config: SimulationConfig,
        *,
        rng: random.Random | None = None,
    ) -> None:
        self.config = config
        self.settings: PerturbationSchedulerConfig = config.perturbations
        self._random = rng or random.Random()
        hybrid_cfg = getattr(config, "observations_config", None)
        if hybrid_cfg is not None:
            ticks_per_day = getattr(hybrid_cfg.hybrid, "time_ticks_per_day", 1440)
        else:
            ticks_per_day = 1440
        self._ticks_per_day = max(1, int(ticks_per_day))
        self.specs: dict[str, PerturbationEventConfig] = self.settings.events
        self._pending: list[ScheduledPerturbation] = []
        self._active: dict[str, ScheduledPerturbation] = {}
        self._event_cooldowns: dict[str, int] = {}
        self._agent_cooldowns: dict[str, int] = {}
        self._window_events: list[tuple[int, str]] = []
        self._next_id: int = 1

    def pending_count(self) -> int:
        return len(self._pending)

    def active_count(self) -> int:
        return len(self._active)

    # ------------------------------------------------------------------
    # Tick lifecycle
    # ------------------------------------------------------------------
    def tick(self, world: WorldState, current_tick: int) -> None:
        self._expire_active(current_tick, world)
        self._expire_cooldowns(current_tick)
        self._expire_window_events(current_tick)
        self._drain_pending(world, current_tick)
        self._maybe_schedule(world, current_tick)

    def _expire_active(self, current_tick: int, world: WorldState) -> None:
        to_remove: list[str] = []
        for event_id, event in list(self._active.items()):
            if current_tick >= event.ends_at:
                to_remove.append(event_id)
        for event_id in to_remove:
            event = self._active.pop(event_id)
            self._on_event_concluded(world, event)

    def _expire_cooldowns(self, current_tick: int) -> None:
        self._event_cooldowns = {
            name: tick
            for name, tick in self._event_cooldowns.items()
            if tick > current_tick
        }
        self._agent_cooldowns = {
            agent: tick
            for agent, tick in self._agent_cooldowns.items()
            if tick > current_tick
        }

    def _expire_window_events(self, current_tick: int) -> None:
        window = self.settings.window_ticks
        if window <= 0:
            self._window_events.clear()
            return
        cutoff = current_tick - window
        self._window_events = [
            (tick, name) for tick, name in self._window_events if tick > cutoff
        ]

    def _drain_pending(self, world: WorldState, current_tick: int) -> None:
        if not self._pending:
            return
        ready: list[ScheduledPerturbation] = []
        for event in list(self._pending):
            if event.started_at <= current_tick:
                ready.append(event)
        for event in ready:
            self._pending.remove(event)
            self._activate(world, event)

    def _maybe_schedule(self, world: WorldState, current_tick: int) -> None:
        if not self.specs:
            return
        if (
            self.settings.max_concurrent_events
            and len(self._active) >= self.settings.max_concurrent_events
        ):
            return
        for name, spec in self.specs.items():
            if not self._can_fire_spec(name, spec, current_tick):
                continue
            probability = self._per_tick_probability(spec)
            if probability <= 0.0:
                continue
            if self._random.random() > probability:
                continue
            event = self._generate_event(name, spec, current_tick, world)
            if event is None:
                continue
            self._activate(world, event)
            if (
                self.settings.max_concurrent_events
                and len(self._active) >= self.settings.max_concurrent_events
            ):
                break

    def schedule_manual(
        self,
        world: WorldState,
        spec_name: str,
        current_tick: int,
        *,
        starts_in: int = 0,
        duration: int | None = None,
        targets: list[str] | None = None,
        payload_overrides: dict[str, object] | None = None,
    ) -> ScheduledPerturbation:
        spec = self.spec_for(spec_name)
        if spec is None:
            raise KeyError(spec_name)
        start_tick = current_tick + max(0, int(starts_in))
        event = self._generate_event(
            spec_name,
            spec,
            start_tick,
            world,
            duration_override=duration,
            targets_override=targets,
            payload_override=payload_overrides,
        )
        if event is None:
            raise ValueError("Unable to schedule perturbation; insufficient targets")
        if start_tick > current_tick:
            self._pending.append(event)
        else:
            self._pending.append(event)
            self._drain_pending(world, current_tick)
        return event

    def cancel_event(self, world: WorldState, event_id: str) -> bool:
        for index, event in enumerate(list(self._pending)):
            if event.event_id == event_id:
                self._pending.pop(index)
                world._emit_event(
                    "perturbation_cancelled",
                    {
                        "event_id": event.event_id,
                        "spec": event.spec_name,
                        "kind": event.kind.value,
                        "pending": True,
                    },
                )
                return True
        event = self._active.pop(event_id, None)
        if event is None:
            return False
        world._emit_event(
            "perturbation_cancelled",
            {
                "event_id": event.event_id,
                "spec": event.spec_name,
                "kind": event.kind.value,
                "pending": False,
            },
        )
        self._on_event_concluded(world, event)
        return True

    def _activate(self, world: WorldState, event: ScheduledPerturbation) -> None:
        self._active[event.event_id] = event
        spec = self.spec_for(event.spec_name)
        cooldown = (
            spec.cooldown_ticks if spec else 0
        ) + self.settings.global_cooldown_ticks
        if cooldown > 0:
            self._event_cooldowns[event.spec_name] = event.ends_at + cooldown
        for agent in event.targets:
            per_agent_cd = self.settings.per_agent_cooldown_ticks
            if per_agent_cd > 0:
                expiry = event.ends_at + per_agent_cd
                current = self._agent_cooldowns.get(agent, 0)
                if expiry > current:
                    self._agent_cooldowns[agent] = expiry
        self._window_events.append((event.started_at, event.spec_name))
        self._apply_event(world, event)
        world._emit_event(
            "perturbation_started",
            {
                "event_id": event.event_id,
                "spec": event.spec_name,
                "kind": event.kind.value,
                "targets": list(event.targets),
                "ends_at": event.ends_at,
            },
        )

    def _apply_event(self, world: WorldState, event: ScheduledPerturbation) -> None:
        if event.kind is PerturbationKind.PRICE_SPIKE:
            magnitude = float(event.payload.get("magnitude", 1.0))
            world.perturbation_service.apply_price_spike(
                event.event_id, magnitude=magnitude, targets=event.targets or ["global"]
            )
            for target in event.targets or ["global"]:
                world._emit_event(
                    "perturbation_price_spike",
                    {
                        "target": target,
                        "magnitude": magnitude,
                        "event_id": event.event_id,
                        "ends_at": event.ends_at,
                    },
                )
        elif event.kind is PerturbationKind.BLACKOUT:
            utility = str(event.payload.get("utility", "power"))
            world.perturbation_service.apply_utility_outage(event.event_id, utility)
            world._emit_event(
                "perturbation_blackout",
                {
                    "utility": utility,
                    "event_id": event.event_id,
                    "ends_at": event.ends_at,
                },
            )
        elif event.kind is PerturbationKind.OUTAGE:
            utility = str(event.payload.get("utility", "water"))
            world.perturbation_service.apply_utility_outage(event.event_id, utility)
            world._emit_event(
                "perturbation_outage",
                {
                    "utility": utility,
                    "event_id": event.event_id,
                    "ends_at": event.ends_at,
                },
            )
        elif event.kind is PerturbationKind.ARRANGED_MEET:
            location_label = event.payload.get("location")
            world.perturbation_service.apply_arranged_meet(
                location=location_label, targets=event.targets
            )
            world._emit_event(
                "perturbation_arranged_meet",
                {
                    "location": location_label,
                    "targets": list(event.targets),
                    "event_id": event.event_id,
                    "ends_at": event.ends_at,
                },
            )

    def _on_event_concluded(
        self, world: WorldState, event: ScheduledPerturbation
    ) -> None:
        if event.kind is PerturbationKind.PRICE_SPIKE:
            world.perturbation_service.clear_price_spike(event.event_id)
        elif event.kind in {PerturbationKind.BLACKOUT, PerturbationKind.OUTAGE}:
            utility = str(event.payload.get("utility", "power"))
            world.perturbation_service.clear_utility_outage(event.event_id, utility)
        world._emit_event(
            "perturbation_ended",
            {
                "event_id": event.event_id,
                "spec": event.spec_name,
                "kind": event.kind.value,
            },
        )

    def seed(self, value: int) -> None:
        self._random.seed(value)

    # ------------------------------------------------------------------
    # Scheduling helpers
    # ------------------------------------------------------------------
    def _can_fire_spec(
        self,
        name: str,
        spec: PerturbationEventConfig,
        current_tick: int,
    ) -> bool:
        if (
            self.settings.max_concurrent_events
            and len(self._active) >= self.settings.max_concurrent_events
        ):
            return False
        cooldown_until = self._event_cooldowns.get(name, 0)
        if cooldown_until > current_tick:
            return False
        if self.settings.max_events_per_window > 0:
            recent_count = sum(
                1 for _, spec_name in self._window_events if spec_name == name
            )
            if recent_count >= self.settings.max_events_per_window:
                return False
        if spec.probability_per_day <= 0.0:
            return False
        return True

    def _per_tick_probability(self, spec: PerturbationEventConfig) -> float:
        return min(1.0, max(0.0, spec.probability_per_day) / float(self._ticks_per_day))

    def _generate_event(
        self,
        name: str,
        spec: PerturbationEventConfig,
        current_tick: int,
        world: WorldState,
        *,
        duration_override: int | None = None,
        targets_override: list[str] | None = None,
        payload_override: dict[str, object] | None = None,
    ) -> ScheduledPerturbation | None:
        duration_range = spec.duration
        if duration_override is not None:
            length = max(int(duration_override), 0)
        else:
            length = max(duration_range.min, 0)
            if duration_range.max > duration_range.min:
                length = self._random.randint(duration_range.min, duration_range.max)
        ends_at = current_tick + max(length, 0)
        payload: dict[str, object] = dict(payload_override or {})
        targets: list[str] = list(targets_override or [])

        if isinstance(spec, PriceSpikeEventConfig):
            if "magnitude" in payload:
                magnitude = float(payload["magnitude"])
            else:
                magnitude = spec.magnitude.min
                if spec.magnitude.max > spec.magnitude.min:
                    magnitude = self._random.uniform(
                        spec.magnitude.min, spec.magnitude.max
                    )
                payload["magnitude"] = magnitude
            if not targets:
                targets = list(spec.targets)
        elif isinstance(spec, BlackoutEventConfig):
            payload.setdefault("utility", spec.utility)
        elif isinstance(spec, OutageEventConfig):
            payload.setdefault("utility", spec.utility)
        elif isinstance(spec, ArrangedMeetEventConfig):
            payload.setdefault("location", spec.location)
            payload.setdefault("target_label", spec.target)
            if not targets:
                candidates = self._eligible_agents(world, current_tick)
                if len(candidates) < 2:
                    return None
                self._random.shuffle(candidates)
                participants = candidates[: spec.max_participants]
                if len(participants) < 2:
                    return None
                targets = participants

        event = ScheduledPerturbation(
            event_id=self.allocate_event_id(),
            spec_name=name,
            kind=spec.kind,
            started_at=current_tick,
            ends_at=ends_at,
            payload=payload,
            targets=targets,
        )
        return event

    def _eligible_agents(self, world: WorldState, current_tick: int) -> list[str]:
        blocked = {
            agent
            for agent, expiry in self._agent_cooldowns.items()
            if expiry > current_tick
        }
        return [agent_id for agent_id in world.agents if agent_id not in blocked]

    # ------------------------------------------------------------------
    # Queue management
    # ------------------------------------------------------------------
    def enqueue(
        self, events: Iterable[ScheduledPerturbation | Mapping[str, object]]
    ) -> None:
        for event in events:
            if isinstance(event, ScheduledPerturbation):
                self._pending.append(event)
            else:
                converted = self._coerce_event(event)
                self._pending.append(converted)

    @property
    def pending(self) -> list[ScheduledPerturbation]:
        return list(self._pending)

    @property
    def active(self) -> dict[str, ScheduledPerturbation]:
        return dict(self._active)

    # ------------------------------------------------------------------
    # State persistence helpers
    # ------------------------------------------------------------------
    def export_state(self) -> dict[str, object]:
        return {
            "pending": [self._serialize_event(event) for event in self._pending],
            "active": {
                event_id: self._serialize_event(event)
                for event_id, event in self._active.items()
            },
            "event_cooldowns": dict(self._event_cooldowns),
            "agent_cooldowns": dict(self._agent_cooldowns),
            "window_events": list(self._window_events),
            "next_id": self._next_id,
            "rng_state": encode_rng_state(self._random.getstate()),
        }

    def import_state(self, payload: dict[str, object]) -> None:
        self._pending = [
            self._coerce_event(entry)
            for entry in payload.get("pending", [])
            if isinstance(entry, Mapping)
        ]
        active_payload = payload.get("active", {})
        self._active = {}
        if isinstance(active_payload, Mapping):
            for event_id, entry in active_payload.items():
                if isinstance(entry, Mapping):
                    event = self._coerce_event(entry)
                    self._active[str(event_id)] = event
        event_cooldowns = payload.get("event_cooldowns", {})
        if isinstance(event_cooldowns, Mapping):
            self._event_cooldowns = {
                str(name): int(tick) for name, tick in event_cooldowns.items()
            }
        else:
            self._event_cooldowns = {}

        agent_cooldowns = payload.get("agent_cooldowns", {})
        if isinstance(agent_cooldowns, Mapping):
            self._agent_cooldowns = {
                str(agent): int(tick) for agent, tick in agent_cooldowns.items()
            }
        else:
            self._agent_cooldowns = {}

        window_events = payload.get("window_events", [])
        if isinstance(window_events, list):
            self._window_events = [
                (int(tick), str(name))
                for tick, name in window_events
                if isinstance(tick, int)
            ]
        else:
            self._window_events = []

        next_id = payload.get("next_id")
        self._next_id = int(next_id) if isinstance(next_id, int) and next_id > 0 else 1

        rng_payload = payload.get("rng_state")
        if isinstance(rng_payload, str):
            self.set_rng_state(decode_rng_state(rng_payload))

    def reset_state(self) -> None:
        self._pending.clear()
        self._active.clear()
        self._event_cooldowns.clear()
        self._agent_cooldowns.clear()
        self._window_events.clear()
        self._next_id = 1

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def allocate_event_id(self) -> str:
        event_id = f"evt_{self._next_id}"
        self._next_id += 1
        return event_id

    def spec_for(self, name: str) -> PerturbationEventConfig | None:
        return self.specs.get(name)

    def rng_state(self) -> tuple:
        return self._random.getstate()

    def set_rng_state(self, state: tuple) -> None:
        self._random.setstate(state)

    @property
    def rng(self) -> random.Random:
        return self._random

    def _coerce_event(self, data: Mapping[str, object]) -> ScheduledPerturbation:
        spec_name = str(
            data.get("spec_name")
            or data.get("event")
            or data.get("kind")
            or "price_spike"
        )
        kind_value = data.get("kind", spec_name)
        try:
            kind = PerturbationKind(kind_value)
        except (ValueError, TypeError):
            kind = PerturbationKind.PRICE_SPIKE
            if spec_name == "price_spike":
                pass
            else:
                spec_name = spec_name
        event_id = str(data.get("event_id", self.allocate_event_id()))
        started_at = int(data.get("started_at", 0))
        ends_at = int(data.get("ends_at", started_at))
        payload = dict(data.get("payload", {}))
        targets_data = data.get("targets", [])
        if isinstance(targets_data, (list, tuple)):
            targets = [str(entry) for entry in targets_data]
        else:
            targets = []
        return ScheduledPerturbation(
            event_id=event_id,
            spec_name=spec_name,
            kind=kind,
            started_at=started_at,
            ends_at=ends_at,
            payload=payload,
            targets=targets,
        )

    @staticmethod
    def _serialize_event(event: ScheduledPerturbation) -> dict[str, object]:
        return {
            "event_id": event.event_id,
            "spec_name": event.spec_name,
            "kind": event.kind.value,
            "started_at": event.started_at,
            "ends_at": event.ends_at,
            "payload": dict(event.payload),
            "targets": list(event.targets),
        }

    def serialize_event(self, event: ScheduledPerturbation) -> dict[str, object]:
        return self._serialize_event(event)

    def latest_state(self) -> dict[str, object]:
        return {
            "active": {
                event_id: self._serialize_event(event)
                for event_id, event in self._active.items()
            },
            "pending": [self._serialize_event(evt) for evt in self._pending],
            "cooldowns": {
                "spec": dict(self._event_cooldowns),
                "agents": dict(self._agent_cooldowns),
            },
        }
