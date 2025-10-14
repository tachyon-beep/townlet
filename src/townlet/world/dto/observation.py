"""Legacy location for observation DTOs (deprecated).

This module provides backward compatibility. New code should import from:
    from townlet.dto.observations import ObservationEnvelope, AgentObservationDTO

This shim will be removed in a future release.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "townlet.world.dto.observation is deprecated. "
    "Import from townlet.dto.observations instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from townlet.dto.observations import (
    AgentObservationDTO,
    DTO_SCHEMA_VERSION,
    GlobalObservationDTO,
    ObservationEnvelope,
    ObservationMetadata,
)

__all__ = [
    "ObservationEnvelope",
    "AgentObservationDTO",
    "GlobalObservationDTO",
    "ObservationMetadata",
    "DTO_SCHEMA_VERSION",
]
