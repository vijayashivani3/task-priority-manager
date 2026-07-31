# Task Priority Manager

A command-line task manager built around a **hand-implemented binary
min-heap** (no built-in `heapq`), with a lazy-deletion strategy for
efficient task completion and JSON-based persistence across runs.

## Why this project

Most simple to-do tools just show you everything and let you scroll.
This one is built around a single question: **what should I actually
do next?** — answered efficiently using a priority queue, the same
core data structure behind OS process schedulers, hospital triage
systems, and print queues.

The min-heap is implemented from scratch specifically to demonstrate
the underlying mechanics (array-based storage, sift-up/sift-down),
rather than relying on Python's `heapq` module.

## Features

- Add tasks with a priority (`urgent`, `high`, `medium`, `low`) and
  an optional due date
- Instantly retrieve the highest-priority pending task — O(log n)
- Mark tasks complete by ID
- List all pending tasks, sorted by priority
- State persists across runs via a local JSON file — no database
  required

## Tech / concepts demonstrated

| Area | What's used |
|---|---|
| Data structures | Hand-built binary min-heap (array-based, sift-up/sift-down) |
| OOP | `Task` as a `@dataclass`, `TaskManager` encapsulating heap + dict |
| Algorithm design | Lazy deletion (heaps can't cheaply delete arbitrary elements) |
| Systems | JSON serialization for state persistence between process runs |
| CLI | `argparse` with subcommands (`add`, `next`, `complete`, `list`) |
| Testing | 22 automated tests — unit tests (heap, manager) + subprocess-based end-to-end CLI tests |

## Project structure

```
task-manager-cli/
├── heap.py          # Hand-built MinHeap (push, pop, peek)
├── task.py           # Task dataclass + priority label mapping
├── manager.py        # TaskManager: wires Task <-> MinHeap, lazy deletion
├── persistence.py    # JSON save/load for cross-run state
├── main.py            # CLI entry point (argparse subcommands)
├── tests/
│   ├── test_heap.py     # Unit tests for MinHeap
│   ├── test_manager.py  # Unit tests for TaskManager (incl. lazy deletion)
│   └── test_cli.py       # End-to-end subprocess tests for the CLI
└── .gitignore
```

## Installation

Requires Python 3.8+. No external dependencies — standard library only.

```bash
git clone https://github.com/vijayashivani3/task-priority-manager.git
cd task-priority-manager
```

## Usage

```bash
# Add a task
python main.py add "Fix production bug" --priority urgent
python main.py add "Write weekly report" --priority low --due 2026-08-05

# See what's most urgent right now
python main.py next

# List all pending tasks, sorted by priority
python main.py list

# Mark a task complete by its ID
python main.py complete 1
```

Priority options: `urgent`, `high`, `medium`, `low` (default: `medium`).

Tasks are saved to `tasks.json` in the project directory and persist
between runs.

## Running the tests

```bash
python tests/test_heap.py
python tests/test_manager.py
python tests/test_cli.py
```

Each file is self-checking and prints `PASS: <test_name>` for every
test, ending with a summary line. No external testing framework
required (though the tests are also `pytest`-compatible — run `pytest`
from the project root if you have it installed).

## Design notes

**Why a hand-built heap instead of `heapq`?** To demonstrate the
underlying mechanics — array-index arithmetic for parent/child
relationships, and the sift-up/sift-down operations that maintain the
heap property — rather than treating it as a black box.

**Why lazy deletion?** A heap only gives efficient (O(1)) access to
its *minimum* element. Finding and removing an arbitrary element
elsewhere in the heap is expensive and error-prone. Instead, completing
a task just flips a `completed` flag on the shared `Task` object; the
heap entry becomes stale but harmless, and is only discarded the next
time it would otherwise surface as "the next task."

**Why JSON persistence?** Each CLI invocation is a separate process
with no memory of the last one. A JSON file on disk acts as the
"memory" that survives between runs.

## Possible extensions

- Secondary tiebreaker (insertion order) for deterministic ordering
  among equal priorities
- Graceful handling of a corrupted `tasks.json`
- Due-date-aware sorting alongside priority
- Swap JSON for SQLite to support safe concurrent access

