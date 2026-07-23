"""
tests/test_manager.py

Self-checking tests for manager.TaskManager, focused especially on the
lazy-deletion behavior since that's the trickiest part of this module.

Run with:  python tests/test_manager.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from manager import TaskManager


def test_add_and_get_next_respects_priority():
    m = TaskManager()
    m.add_task("Write report", "low")
    m.add_task("Fix production bug", "urgent")
    m.add_task("Reply to email", "medium")

    next_task = m.get_next_task()
    assert next_task.description == "Fix production bug", \
        f"expected the urgent task first, got {next_task.description}"


def test_get_next_is_non_destructive():
    """Calling get_next_task twice in a row should return the SAME task
    both times, since peeking shouldn't remove anything."""
    m = TaskManager()
    m.add_task("Only task", "high")

    first = m.get_next_task()
    second = m.get_next_task()
    assert first.id == second.id, "get_next_task should be non-destructive (peek, not pop)"


def test_complete_task_by_id():
    m = TaskManager()
    t1 = m.add_task("Task A", "urgent")
    m.add_task("Task B", "high")

    ok = m.complete_task(t1.id)
    assert ok is True

    next_task = m.get_next_task()
    assert next_task.description == "Task B", \
        "completed task should no longer be returned as next"


def test_complete_unknown_id_returns_false():
    m = TaskManager()
    m.add_task("Task A", "urgent")
    assert m.complete_task(9999) is False


def test_lazy_deletion_cleans_up_stale_root():
    """This is the core lazy-deletion scenario: complete the task that's
    CURRENTLY at the top of the heap, then verify the manager correctly
    skips past it to find the next real task, discarding the stale
    entry along the way."""
    m = TaskManager()
    urgent_task = m.add_task("Urgent thing", "urgent")
    m.add_task("High priority thing", "high")
    m.add_task("Medium priority thing", "medium")

    # Complete the task that is currently the heap's root (most urgent).
    m.complete_task(urgent_task.id)

    next_task = m.get_next_task()
    assert next_task.description == "High priority thing", \
        f"expected lazy deletion to skip the completed root, got {next_task.description}"


def test_list_pending_excludes_completed_and_is_sorted():
    m = TaskManager()
    m.add_task("Low task", "low")
    urgent = m.add_task("Urgent task", "urgent")
    m.add_task("Medium task", "medium")
    m.complete_task(urgent.id)

    pending = m.list_pending()
    descriptions = [t.description for t in pending]
    assert descriptions == ["Medium task", "Low task"], \
        f"expected medium then low (urgent completed, excluded), got {descriptions}"


def test_invalid_priority_label_raises():
    m = TaskManager()
    try:
        m.add_task("Bad task", "super-urgent")
        assert False, "expected ValueError for an invalid priority label"
    except ValueError:
        pass  # expected


def test_get_next_on_empty_manager_returns_none():
    m = TaskManager()
    assert m.get_next_task() is None


if __name__ == "__main__":
    tests = [
        test_add_and_get_next_respects_priority,
        test_get_next_is_non_destructive,
        test_complete_task_by_id,
        test_complete_unknown_id_returns_false,
        test_lazy_deletion_cleans_up_stale_root,
        test_list_pending_excludes_completed_and_is_sorted,
        test_invalid_priority_label_raises,
        test_get_next_on_empty_manager_returns_none,
    ]
    for t in tests:
        t()
        print(f"PASS: {t.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
