"""Queue management placeholder package.

Maintains compatibility by re-exporting the existing queue modules until the
full extraction is complete.
"""

from __future__ import annotations

from .conflict import QueueConflictTracker
from .manager import QueueManager

__all__ = ["QueueConflictTracker", "QueueManager"]
