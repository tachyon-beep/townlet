"""Queue management placeholder package.

Maintains compatibility by re-exporting the existing queue modules until the
full extraction is complete.
"""

from __future__ import annotations

from townlet.world.queue_conflict import QueueConflictTracker
from townlet.world.queue_manager import QueueManager

__all__ = ["QueueConflictTracker", "QueueManager"]
