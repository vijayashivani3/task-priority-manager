"""
tests/test_cli.py

End-to-end tests for main.py. Since this is a CLI, we test it the way
a real user would use it: by actually launching it as a subprocess and
checking what it prints, rather than calling its functions directly in
the same process.

Each test uses a temporary directory + TASK_MANAGER_DATA_FILE override
(see main.py) so tests never touch your real tasks.json, and different
tests never interfere with each other.

Run with:  python tests/test_cli.py
"""

import os
import subprocess
import sys
import tempfile

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
MAIN_SCRIPT = os.path.join(PROJECT_ROOT, "main.py")


def run_cli(args, data_file):
    """Launch `python main.py <args>` as a real subprocess, pointed at
    an isolated data file via environment variable, and capture what
    it prints."""
    env = os.environ.copy()
    env["TASK_MANAGER_DATA_FILE"] = data_file
    result = subprocess.run(
        [sys.executable, MAIN_SCRIPT] + args,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    return result


def test_add_and_list():
    with tempfile.TemporaryDirectory() as tmp:
        data_file = os.path.join(tmp, "tasks.json")

        result = run_cli(["add", "Fix bug", "--priority", "urgent"], data_file)
        assert result.returncode == 0, result.stderr
        assert "Added task #1: Fix bug (urgent)" in result.stdout

        result = run_cli(["list"], data_file)
        assert "Fix bug" in result.stdout
        assert "urgent" in result.stdout


def test_default_priority_is_medium():
    with tempfile.TemporaryDirectory() as tmp:
        data_file = os.path.join(tmp, "tasks.json")
        result = run_cli(["add", "No priority specified"], data_file)
        assert "(medium)" in result.stdout, \
            "expected default priority to be 'medium' when --priority is omitted"


def test_next_respects_priority_order():
    with tempfile.TemporaryDirectory() as tmp:
        data_file = os.path.join(tmp, "tasks.json")
        run_cli(["add", "Low priority task", "--priority", "low"], data_file)
        run_cli(["add", "Urgent task", "--priority", "urgent"], data_file)

        result = run_cli(["next"], data_file)
        assert "Urgent task" in result.stdout


def test_complete_then_next_skips_it():
    with tempfile.TemporaryDirectory() as tmp:
        data_file = os.path.join(tmp, "tasks.json")
        run_cli(["add", "Task A", "--priority", "urgent"], data_file)
        run_cli(["add", "Task B", "--priority", "high"], data_file)

        run_cli(["complete", "1"], data_file)

        result = run_cli(["next"], data_file)
        assert "Task B" in result.stdout
        assert "Task A" not in result.stdout


def test_persistence_across_separate_processes():
    """The core proof of Module 3: state must survive between
    completely separate process launches."""
    with tempfile.TemporaryDirectory() as tmp:
        data_file = os.path.join(tmp, "tasks.json")

        run_cli(["add", "Persisted task", "--priority", "medium"], data_file)
        # This is a brand new subprocess -- it has no in-memory
        # connection whatsoever to the one that ran "add" above.
        result = run_cli(["list"], data_file)
        assert "Persisted task" in result.stdout


def test_complete_unknown_id_reports_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        data_file = os.path.join(tmp, "tasks.json")
        result = run_cli(["complete", "999"], data_file)
        assert "No task found with id 999" in result.stdout


def test_invalid_priority_rejected_by_argparse():
    with tempfile.TemporaryDirectory() as tmp:
        data_file = os.path.join(tmp, "tasks.json")
        result = run_cli(["add", "Bad task", "--priority", "super-urgent"], data_file)
        assert result.returncode != 0, "argparse should reject an invalid --priority choice"


def test_empty_list_message():
    with tempfile.TemporaryDirectory() as tmp:
        data_file = os.path.join(tmp, "tasks.json")
        result = run_cli(["list"], data_file)
        assert "No pending tasks." in result.stdout


if __name__ == "__main__":
    tests = [
        test_add_and_list,
        test_default_priority_is_medium,
        test_next_respects_priority_order,
        test_complete_then_next_skips_it,
        test_persistence_across_separate_processes,
        test_complete_unknown_id_reports_not_found,
        test_invalid_priority_rejected_by_argparse,
        test_empty_list_message,
    ]
    for t in tests:
        t()
        print(f"PASS: {t.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
