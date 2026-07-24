"""
manager.py

TaskManager ties together:
  - heap.MinHeap        (fast access to "what's most urgent right now")
  - task.Task            (the data model for a single task)

Design note — lazy deletion:
A heap has no efficient way to delete or update an arbitrary element
buried in the middle of it. So instead of trying to remove a task from
the heap the moment it's completed, we just flip a flag on the shared
Task object (`task.completed = True`). The heap entry becomes "stale"
but harmless. Only when that stale entry would otherwise be returned
as "the next task" do we actually pop and discard it. This is the
standard "lazy deletion" pattern used in real-world priority-queue-
based schedulers.
"""

from typing import Dict, List, Optional

from heap import MinHeap
from task import Task, priority_label_to_value


class TaskManager:
    def __init__(self) -> None:
        self._heap = MinHeap()
        self._tasks_by_id: Dict[int, Task] = {}
        self._next_id = 1  # simple auto-incrementing ID generator

    def add_task(self, description: str, priority_label: str,
                 due_date: Optional[str] = None) -> Task:
        """Create a new Task, store it, and push it into the heap."""
        priority_value = priority_label_to_value(priority_label)  # validates label

        task = Task(
            id=self._next_id,
            description=description,
            priority_label=priority_label.lower().strip(),
            due_date=due_date,
        )
        self._next_id += 1

        self._tasks_by_id[task.id] = task
        self._heap.push(priority_value, task)
        return task

    def get_next_task(self) -> Optional[Task]:
        """Return the highest-priority PENDING task without removing it
        from the manager (a non-destructive peek). Stale (already-
        completed) entries at the top of the heap are discarded here —
        this is where lazy deletion actually happens."""
        while not self._heap.is_empty():
            _, task = self._heap.peek()
            if task.completed:
                self._heap.pop()  # discard the stale entry, then loop again
                continue
            return task
        return None  # heap is empty (or only had completed tasks)

    def complete_task(self, task_id: int) -> bool:
        """Mark a task done by ID. Returns True if the task existed,
        False if the ID is unknown. Does NOT touch the heap directly —
        see the module docstring for why."""
        task = self._tasks_by_id.get(task_id)
        if task is None:
            return False
        task.mark_done()
        return True

    def list_pending(self) -> List[Task]:
        """Return all pending tasks, sorted by priority (most urgent first).

        Note: unlike get_next_task (O(log n)), this is O(n log n) because
        listing everything in order isn't the operation a heap is built
        to accelerate — we simply filter and sort the dict's values
        directly. That's a fine trade: we only pay this cost when the
        user actually asks to see the full list, not on every lookup."""
        pending = [t for t in self._tasks_by_id.values() if not t.completed]
        return sorted(pending, key=lambda t: priority_label_to_value(t.priority_label))

    def list_completed(self) -> List[Task]:
        return [t for t in self._tasks_by_id.values() if t.completed]

    def load(self, tasks: List[Task]) -> None:
        """Rebuild this manager's internal heap and dict from a list of
        previously-saved Task objects (see persistence.py). Only PENDING
        tasks go into the heap -- a completed task doesn't need "next
        task" ordering, so there's no need to recreate stale entries the
        way lazy deletion handles them during a single run."""
        self._heap = MinHeap()
        self._tasks_by_id = {}
        max_id_seen = 0

        for task in tasks:
            self._tasks_by_id[task.id] = task
            max_id_seen = max(max_id_seen, task.id)
            if not task.completed:
                priority_value = priority_label_to_value(task.priority_label)
                self._heap.push(priority_value, task)

        self._next_id = max_id_seen + 1

    def all_tasks(self) -> List[Task]:
        """All tasks, pending and completed -- used when saving to disk."""
        return list(self._tasks_by_id.values())
