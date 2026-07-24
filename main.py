"""
main.py

The command-line entry point for the task manager. Each invocation is
a fresh Python process, so every command:
  1. Loads the saved task list from a JSON file (persistence.py)
  2. Rebuilds a TaskManager from it (manager.py's load())
  3. Performs the requested action
  4. If anything changed, saves the updated task list back to disk

Usage:
    python main.py add "Fix the bug" --priority urgent --due 2026-08-01
    python main.py next
    python main.py complete 3
    python main.py list
"""

import argparse
import os

from manager import TaskManager
from persistence import save_tasks, load_tasks

# Allow overriding the data file location via an environment variable --
# this is what lets our automated tests (tests/test_cli.py) point the
# CLI at a temporary, isolated file instead of your real tasks.json.
DATA_FILE = os.environ.get("TASK_MANAGER_DATA_FILE") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "tasks.json"
)


def build_manager() -> TaskManager:
    """Load the saved tasks from disk into a fresh TaskManager."""
    manager = TaskManager()
    manager.load(load_tasks(DATA_FILE))
    return manager


def save_manager(manager: TaskManager) -> None:
    """Persist the manager's current task list back to disk."""
    save_tasks(manager.all_tasks(), DATA_FILE)


def cmd_add(args: argparse.Namespace) -> None:
    manager = build_manager()
    task = manager.add_task(args.description, args.priority, args.due)
    save_manager(manager)
    print(f"Added task #{task.id}: {task.description} ({task.priority_label})")


def cmd_next(args: argparse.Namespace) -> None:
    manager = build_manager()
    task = manager.get_next_task()
    if task is None:
        print("No pending tasks. You're all caught up!")
    else:
        print(f"Next task: {task}")


def cmd_complete(args: argparse.Namespace) -> None:
    manager = build_manager()
    ok = manager.complete_task(args.id)
    if ok:
        save_manager(manager)
        print(f"Marked task #{args.id} as complete.")
    else:
        print(f"No task found with id {args.id}.")


def cmd_list(args: argparse.Namespace) -> None:
    manager = build_manager()
    pending = manager.list_pending()
    if not pending:
        print("No pending tasks.")
        return
    print("Pending tasks (most urgent first):")
    for t in pending:
        print(f"  {t}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task-manager",
        description="A priority-queue-based CLI task manager.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", help="Task description")
    add_parser.add_argument(
        "--priority", "-p", default="medium",
        choices=["urgent", "high", "medium", "low"],
        help="Task priority (default: medium)",
    )
    add_parser.add_argument("--due", "-d", default=None, help="Optional due date, e.g. 2026-08-01")
    add_parser.set_defaults(func=cmd_add)

    next_parser = subparsers.add_parser("next", help="Show the highest-priority pending task")
    next_parser.set_defaults(func=cmd_next)

    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_parser.add_argument("id", type=int, help="Task ID to complete")
    complete_parser.set_defaults(func=cmd_complete)

    list_parser = subparsers.add_parser("list", help="List all pending tasks")
    list_parser.set_defaults(func=cmd_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
