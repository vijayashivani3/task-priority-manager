"""
persistence.py

Handles converting Task objects to/from JSON, so the CLI's state
survives between separate process invocations. Each time main.py
runs, it's a brand-new Python process with no memory of the previous
run -- this module is what lets the tool "remember" tasks across
separate command invocations by reading/writing a JSON file on disk.
"""

import json
import os
from typing import List

from task import Task


def tasks_to_dicts(tasks: List[Task]) -> List[dict]:
    """Convert Task objects into plain dicts (JSON can only store
    plain data -- strings, numbers, booleans, lists, dicts -- not
    custom Python objects directly)."""
    return [
        {
            "id": t.id,
            "description": t.description,
            "priority_label": t.priority_label,
            "due_date": t.due_date,
            "completed": t.completed,
        }
        for t in tasks
    ]


def dicts_to_tasks(dicts: List[dict]) -> List[Task]:
    """Convert plain dicts (loaded from JSON) back into real Task
    objects. `Task(**d)` unpacks a dict's keys as keyword arguments --
    this works because our dict keys exactly match Task's field names."""
    return [Task(**d) for d in dicts]


def save_tasks(tasks: List[Task], filepath: str) -> None:
    """Write the full task list to a JSON file, pretty-printed
    (indent=2) so it's readable if you open it manually."""
    with open(filepath, "w") as f:
        json.dump(tasks_to_dicts(tasks), f, indent=2)


def load_tasks(filepath: str) -> List[Task]:
    """Read tasks back from a JSON file. If the file doesn't exist yet
    (e.g. this is the very first time the tool has been run), return
    an empty list instead of crashing."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        data = json.load(f)
    return dicts_to_tasks(data)
