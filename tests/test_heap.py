"""
tests/test_heap.py

Self-checking tests for heap.MinHeap. Run with:
    python -m tests.test_heap
from the project root, or `pytest` if pytest is installed.
"""

import random
import sys
import os

# Allow running this file directly (python tests/test_heap.py) by adding
# the project root to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from heap import MinHeap


def test_push_pop_returns_sorted_order():
    """Pushing a jumbled set of priorities, then popping repeatedly,
    should return them in strictly non-decreasing order — that's the
    fundamental contract of a min-heap."""
    h = MinHeap()
    values = [5, 3, 8, 1, 9, 2, 7, 4, 6, 0]
    for v in values:
        h.push(v, f"item-{v}")

    popped = []
    while not h.is_empty():
        priority, item = h.pop()
        popped.append(priority)
        assert item == f"item-{priority}", "payload didn't travel with its priority"

    assert popped == sorted(values), f"expected sorted order, got {popped}"


def test_peek_does_not_remove():
    h = MinHeap()
    h.push(10, "a")
    h.push(5, "b")
    assert h.peek() == (5, "b")
    assert len(h) == 2, "peek should not remove the element"


def test_pop_empty_raises():
    h = MinHeap()
    try:
        h.pop()
        assert False, "popping an empty heap should raise IndexError"
    except IndexError:
        pass  # expected


def test_peek_empty_raises():
    h = MinHeap()
    try:
        h.peek()
        assert False, "peeking an empty heap should raise IndexError"
    except IndexError:
        pass  # expected


def test_random_stress():
    """Randomized test: push a large random batch, verify pop order
    always matches Python's own sorted() as ground truth."""
    random.seed(42)
    for _ in range(20):  # run 20 randomized trials
        h = MinHeap()
        values = [random.randint(-1000, 1000) for _ in range(200)]
        for v in values:
            h.push(v, v)

        popped = [h.pop()[0] for _ in range(len(values))]
        assert popped == sorted(values), "heap pop order diverged from sorted ground truth"


def test_duplicate_priorities():
    """Ties should be handled without crashing or losing items."""
    h = MinHeap()
    for _ in range(5):
        h.push(3, "same-priority")
    assert len(h) == 5
    results = [h.pop() for _ in range(5)]
    assert all(p == 3 for p, _ in results)
    assert h.is_empty()


if __name__ == "__main__":
    tests = [
        test_push_pop_returns_sorted_order,
        test_peek_does_not_remove,
        test_pop_empty_raises,
        test_peek_empty_raises,
        test_random_stress,
        test_duplicate_priorities,
    ]
    for t in tests:
        t()
        print(f"PASS: {t.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
