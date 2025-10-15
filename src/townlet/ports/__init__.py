"""Protocol definitions for Townlet runtime ports.

These ports form the public surface consumed by the simulation loop and other
high-level coordinators. Concrete implementations live behind adapters and
factories so the loop depends only on behaviour contracts.
"""

from .policy import PolicyBackend
from .telemetry import TelemetrySink
from .world import WorldRuntime

__all__ = [
    "PolicyBackend",
    "TelemetrySink",
    "WorldRuntime",
]
