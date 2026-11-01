# Assignment 6 — Medians, Order Statistics & Elementary Data Structures

Python 3 standard-library implementation for **MSCS-532**. Both required parts are implemented, tested, and discussed in `Assignment6_Report_APA7.docx`.

## Repository structure

```text
MSCS532_Assignment6/
├── selection.py                 # Median-of-medians and randomized quickselect
├── structures.py                # Dynamic array, matrix, stack, circular queue, singly linked list
├── benchmark.py                 # Reproducible median timings and correctness assertions
├── tests/test_assignment6.py   # unittest tests (8 test methods)
├── results/
│   ├── benchmark.csv            # Actual experiment measurements, milliseconds
│   └── benchmark_output.txt     # Captured terminal output
├── Assignment6_Report_APA7.docx # APA-style analysis and empirical findings
└── README.md
```

## Requirements

- Python 3.10+; no third-party packages required.
- Run all commands from the repository root.

## Commands

```bash
python selection.py
python structures.py
python -m unittest discover -s tests -v
python benchmark.py --repeats 7 --seed 2026
```

`benchmark.py` overwrites `results/benchmark.csv` with your machine's measurements. Timings vary by CPU, background load, and Python version.

## Selection interface

```python
from selection import deterministic_select, randomized_select
nums = [8, 3, 3, -1, 10]
print(deterministic_select(nums, 2))      # 3
print(randomized_select(nums, 2, seed=42))# 3
```

**Important:** `k` is **zero-based** (`k=0` selects the minimum). Inputs are not modified. An empty array or invalid `k` raises `ValueError`. For even-length lists, the benchmark uses `k = n // 2`, the **upper median**.

## Data structures

- `DynamicArray`: `.append(value)`, `.insert(index, value)`, `.access(index)`, `.delete(index)`, `.to_list()`.
- `Matrix`: `.access(r,c)`, `.set(r,c,value)`, `.insert_row`, `.delete_row`, `.insert_column`, `.delete_column`, `.shape`.
- `ArrayStack`: `.push`, `.pop`, `.peek`.
- `ArrayQueue`: `.enqueue`, `.dequeue`, `.peek`; circular buffer avoids O(n) shifting.
- `SinglyLinkedList`: `.append`, `.prepend`, `.insert(index,value)`, `.delete(index)`, `.traverse`.

## Findings

- Median of Medians uses fixed-size groups of five and guarantees worst-case **O(n)** selection.
- Randomized Quickselect has **expected O(n)** time but **O(n²)** worst-case time; its lower typical constant factor often makes it faster in this Python implementation.
- Both selection methods use **O(n)** auxiliary memory because they form new partition lists; this is an explicit readability/implementation choice.
- Direct array access is O(1), but inserting into the middle requires shifting O(n) values. Singly linked lists have O(1) head insertion but O(n) indexed search.
- Array stacks and circular-buffer queues support O(1) amortized updates (worst-case O(n) on a resize).

See the report for methodology, observed timings, trade-offs, applications, and references.

