"""Benchmark deterministic and randomized selection on several data patterns.

Run: ``python benchmark.py --repeats 7 --seed 2026``

Each implementation receives the same data for a given size/distribution.
Timing uses ``perf_counter_ns`` and records both mean and median runtime.
Results are exported to ``results/benchmark.csv`` without extra packages.
"""
import argparse
import csv
from pathlib import Path
import random
import statistics
import time
from selection import deterministic_select, randomized_select


def make_data(n, distribution, rng):
    """Generate an input pattern to probe different pivot behavior.

    ``duplicates`` deliberately draws from just ten values, so equal elements
    occur frequently. ``rng`` is supplied by the caller for reproducibility.
    """
    if distribution == 'random':
        return [rng.randrange(-n * 10, n * 10) for _ in range(n)]
    if distribution == 'sorted':
        return list(range(n))
    if distribution == 'reversed':
        return list(range(n - 1, -1, -1))
    if distribution == 'duplicates':
        return [rng.randrange(0, 10) for _ in range(n)]
    raise ValueError('unknown distribution')


def run(sizes=(100, 500, 1000, 3000), repeats=7, seed=2026):
    """Time both algorithms, validate answers, and write a CSV summary.

    Only selection is timed: input generation and reference sorting happen
    outside the timing loop. Repeats reduce sensitivity to scheduling noise.
    The test compares the result with a sorted copy, not with the other
    algorithm, so shared algorithmic mistakes are less likely to go unnoticed.
    """
    rng = random.Random(seed)
    records = []
    for distribution in ('random', 'sorted', 'reversed', 'duplicates'):
        for n in sizes:
            data = make_data(n, distribution, rng)
            k, correct = n // 2, sorted(data)[n // 2]
            for name, algorithm in [('median_of_medians', deterministic_select), ('randomized_quickselect', randomized_select)]:
                times = []
                for trial in range(repeats):
                    start = time.perf_counter_ns()
                    # Change the randomized seed per trial to sample pivot choices.
                    found = algorithm(data, k) if name == 'median_of_medians' else algorithm(data, k, seed=seed + trial)
                    elapsed = time.perf_counter_ns() - start
                    assert found == correct, f'{name} incorrect for {distribution} n={n}'
                    times.append(elapsed / 1_000_000)  # Nanoseconds -> milliseconds.

                # Median is less affected by occasional system interruptions.
                row = {'distribution': distribution, 'n': n, 'algorithm': name,
                       'repeats': repeats, 'median_ms': round(statistics.median(times), 5),
                       'mean_ms': round(statistics.mean(times), 5)}
                records.append(row)
                print(f'{distribution:10} n={n:5} {name:23} median={row["median_ms"]:.5f} ms')

    # Create the results directory automatically for a fresh repository clone.
    path = Path(__file__).resolve().parent / 'results' / 'benchmark.csv'
    path.parent.mkdir(exist_ok=True)
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print('Saved:', path)
    return records


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Benchmark two k-th-element selection algorithms.')
    p.add_argument('--repeats', type=int, default=7, help='timed trials per input and algorithm')
    p.add_argument('--seed', type=int, default=2026, help='seed for data and pivot reproducibility')
    args = p.parse_args()
    if args.repeats < 1:
        p.error('--repeats must be >= 1')
    run(repeats=args.repeats, seed=args.seed)
