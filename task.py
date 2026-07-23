"""
task.py

Defines the Task data model and the priority-label-to-number mapping
that connects human-friendly priority names to the numeric priorities
our MinHeap (see heap.py) understands.
"""

from dataclasses import dataclass, field
from typing import Optional

# Lower number = more urgent = closer to the root of the min-heap.
# Keeping this mapping in one place means if we ever want to add a new
# priority level (e.g. "critical"), we only change it here.
PRIORITY_LEVELS = {
    "urgent": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def priority_label_to_value(label: str) -> int:
    """Translate a human-friendly priority label into the numeric value
    the heap compares. Raises a clear error for typos instead of failing
    silently or crashing deep inside the heap."""
    label = label.lower().strip()
    if label not in PRIORITY_LEVELS:
        valid = ", ".join(PRIORITY_LEVELS.keys())
        raise ValueError(f"Unknown priority '{label}'. Valid options: {valid}")
    return PRIORITY_LEVELS[label]


@dataclass
class Task:
    """
    A single task.

    `completed` starts False and is flipped to True in place when the
    user finishes the task — see TaskManager's lazy-deletion pattern
    in manager.py for why we mutate this flag rather than physically
    removing the task from the heap immediately.
    """

    id: int
    description: str
    priority_label: str
    due_date: Optional[str] = None
    completed: bool = False

    def mark_done(self) -> None:
        self.completed = True

    def __str__(self) -> str:
        status = "[x]" if self.completed else "[ ]"
        due = f" (due {self.due_date})" if self.due_date else ""
        return f"{status} #{self.id} ({self.priority_label}){due}: {self.description}"
