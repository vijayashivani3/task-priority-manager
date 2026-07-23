"""
heap.py

A hand-built binary min-heap, implemented on top of a plain Python list.

This module intentionally does NOT use Python's built-in `heapq` module.
The point of this project is to demonstrate understanding of how a heap
works internally (array-index arithmetic, sift-up, sift-down), which is
exactly what interviewers probe for.
"""

from typing import Any, List, Tuple


class MinHeap:
    """
    A min-heap where the smallest item (by comparison) is always at the root.

    Internally stored as a flat Python list. Each element is a tuple:
        (priority, item)
    where a smaller `priority` value means "more important" / "comes first".
    Using a tuple lets us store any payload (e.g. a Task object) alongside
    the number the heap actually compares.
    """

    def __init__(self) -> None:
        self._data: List[Tuple[int, Any]] = []

    def __len__(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    # ---- index helpers -------------------------------------------------

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right(i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._data[i], self._data[j] = self._data[j], self._data[i]

    # ---- core operations -------------------------------------------------

    def push(self, priority: int, item: Any) -> None:
        """Insert a new (priority, item) pair, maintaining the heap property."""
        self._data.append((priority, item))
        self._sift_up(len(self._data) - 1)

    def pop(self) -> Tuple[int, Any]:
        """Remove and return the (priority, item) pair with the smallest priority."""
        if self.is_empty():
            raise IndexError("pop from an empty heap")

        root = self._data[0]
        last_index = len(self._data) - 1

        # Move the last element to the root, then shrink the list.
        self._data[0] = self._data[last_index]
        self._data.pop()  # remove the now-duplicated last element

        if not self.is_empty():
            self._sift_down(0)

        return root

    def peek(self) -> Tuple[int, Any]:
        """Look at the smallest (priority, item) pair without removing it."""
        if self.is_empty():
            raise IndexError("peek on an empty heap")
        return self._data[0]

    # ---- internal maintenance -------------------------------------------------

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = self._parent(i)
            if self._data[i][0] < self._data[parent][0]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self._data)
        while True:
            left = self._left(i)
            right = self._right(i)
            smallest = i

            if left < n and self._data[left][0] < self._data[smallest][0]:
                smallest = left
            if right < n and self._data[right][0] < self._data[smallest][0]:
                smallest = right

            if smallest == i:
                break

            self._swap(i, smallest)
            i = smallest
