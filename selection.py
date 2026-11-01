"""Selection algorithms for finding an order statistic without sorting the input.

An order statistic is the value that would appear at index ``k`` in a sorted
copy of the data. Both public functions use ZERO-BASED indexing: ``k=0``
requests the smallest element. Neither function modifies the caller's input.

The implementations use three-way partitioning, which groups values equal to
the pivot and correctly handles duplicate-heavy datasets.
"""
from random import Random
from typing import Sequence


def _validate(values: Sequence[int], k: int) -> list[int]:
    """Validate the request and return an independent, mutable copy of data.

    Reject empty inputs, negative/out-of-range indices, and non-integer k.
    ``bool`` is rejected explicitly because it is a subclass of ``int``.
    """
    if not values:
        raise ValueError('Cannot select from an empty collection')
    if isinstance(k, bool) or not isinstance(k, int) or not 0 <= k < len(values):
        raise ValueError('k must be a zero-based index within the input')
    return list(values)


def _partition_three(items: list[int], pivot: int) -> tuple[list[int], list[int], list[int]]:
    """Partition items into less-than, equal-to, and greater-than buckets.

    Unlike a two-way partition, the equal bucket can contain many elements.
    If the desired rank falls inside that bucket, selection can stop at once.
    Partitioning inspects each value once: O(n) time and O(n) extra space.
    """
    lower, equal, higher = [], [], []
    for value in items:
        if value < pivot:
            lower.append(value)
        elif value > pivot:
            higher.append(value)
        else:
            equal.append(value)
    return lower, equal, higher


def _det_select(items: list[int], k: int) -> int:
    """Recursive median-of-medians selection on an already validated input."""
    # Base case: sorting at most five elements takes constant time.
    if len(items) <= 5:
        return sorted(items)[k]

    # Split into groups of at most five and find each group's middle value.
    # The group size is fixed, so processing all groups costs O(n) total.
    medians = [sorted(items[i:i + 5])[len(items[i:i + 5]) // 2]
               for i in range(0, len(items), 5)]

    # Recursively choose a balanced pivot from those small-group medians.
    # This avoids the consistently bad pivots possible in ordinary Quickselect.
    pivot = _det_select(medians, len(medians) // 2)
    lower, equal, higher = _partition_three(items, pivot)

    # k is measured relative to the CURRENT subproblem, not the original data.
    if k < len(lower):
        return _det_select(lower, k)
    if k < len(lower) + len(equal):
        return pivot  # The selected rank falls among values equal to the pivot.

    # Discard all lower/equal elements and translate k into the upper bucket.
    return _det_select(higher, k - len(lower) - len(equal))


def deterministic_select(values: Sequence[int], k: int) -> int:
    """Return the k-th smallest element using the median-of-medians pivot.

    Complexity: O(n) worst-case time, O(n) auxiliary space in this version,
    which creates fresh partition lists rather than partitioning in place.
    """
    return _det_select(_validate(values, k), k)


def randomized_select(values: Sequence[int], k: int, seed: int | None = None) -> int:
    """Return the k-th smallest element with randomized Quickselect.

    Expected time is O(n); an unlucky sequence of pivots can take O(n^2).
    Three-way partitions use O(n) auxiliary space. Supply ``seed`` for
    repeatable tests and benchmarks; omit it for an arbitrary pivot sequence.
    """
    items = _validate(values, k)
    rng = Random(seed)  # Dedicated generator does not alter global random state.

    # Only one side of each partition can contain the requested rank.
    # Continue on that side instead of sorting or recursing into both sides.
    while True:
        if len(items) <= 1:
            return items[0]
        pivot = items[rng.randrange(len(items))]
        lower, equal, higher = _partition_three(items, pivot)
        if k < len(lower):
            items = lower
        elif k < len(lower) + len(equal):
            return pivot
        else:
            k -= len(lower) + len(equal)  # Adjust rank after discarding buckets.
            items = higher


if __name__ == '__main__':
    # Simple standalone demonstration; the test suite checks many more cases.
    sample = [7, 2, 9, 2, 5, 1]
    k = len(sample) // 2  # Upper median when the input has an even length.
    print('Input:', sample, 'zero-based k:', k)
    print('Deterministic:', deterministic_select(sample, k))
    print('Randomized:', randomized_select(sample, k, seed=42))
