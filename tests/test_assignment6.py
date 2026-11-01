"""Regression tests for algorithms, duplicates, empty inputs, and every data structure."""
import random
import unittest
from selection import deterministic_select, randomized_select
from structures import DynamicArray, Matrix, ArrayStack, ArrayQueue, SinglyLinkedList


class SelectionTests(unittest.TestCase):
    """Check selection correctness against sorting, including edge cases."""
    def test_edge_cases(self):
        """Exercise singletons, duplicates, negatives, sorted, and reversed input."""
        for values in ([1], [3, 3, 3, 3], [-3, 8, -3, 2], list(range(35)), list(range(34, -1, -1))):
            for k in range(len(values)):
                expected = sorted(values)[k]
                self.assertEqual(deterministic_select(values, k), expected)
                self.assertEqual(randomized_select(values, k, seed=11), expected)

    def test_random_inputs_and_no_mutation(self):
        """Verify correct ranks and that the caller's list stays unchanged."""
        rng = random.Random(42)
        for n in [2, 5, 10, 50, 101, 300]:
            values = [rng.randint(-10, 10) for _ in range(n)]
            original = values.copy()
            for k in {0, n // 2, n - 1}:
                self.assertEqual(deterministic_select(values, k), sorted(values)[k])
                self.assertEqual(randomized_select(values, k, 22), sorted(values)[k])
            self.assertEqual(values, original)

    def test_invalid_indices(self):
        """Reject bad ranks rather than returning an arbitrary result."""
        for fn in (deterministic_select, randomized_select):
            for values, k in [([], 0), ([1], -1), ([1], 1), ([1], 0.5), ([1], True)]:
                with self.assertRaises(ValueError):
                    fn(values, k)


class StructureTests(unittest.TestCase):
    """Check ordering, index updates, growth, and empty-container errors."""
    def test_array(self):
        """Confirm insertion shifts items, deletion restores order, and bounds work."""
        a = DynamicArray()
        for n in range(100): a.append(n)
        a.insert(50, 'middle')
        self.assertEqual(a.access(50), 'middle')
        self.assertEqual(a.delete(50), 'middle')
        self.assertEqual(a.to_list(), list(range(100)))
        with self.assertRaises(IndexError): a.access(100)

    def test_matrix(self):
        """Confirm row/column edits preserve the rectangular dimensions."""
        m = Matrix(2, 2, 0)
        m.set(0, 1, 7)
        m.insert_row(1, [3, 4])
        m.insert_column(1, [9, 8, 7])
        self.assertEqual(m.shape, (3, 3))
        self.assertEqual(m.access(0, 2), 7)
        self.assertEqual(m.delete_column(1), [9, 8, 7])
        self.assertEqual(m.delete_row(1), [3, 4])

    def test_stack(self):
        """Verify last-in-first-out order and empty-pop failure."""
        s = ArrayStack()
        for n in range(60): s.push(n)
        self.assertEqual(s.peek(), 59)
        self.assertEqual([s.pop() for _ in range(60)], list(range(59, -1, -1)))
        with self.assertRaises(IndexError): s.pop()

    def test_queue_wrap_and_growth(self):
        """Force buffer growth and wrap-around while maintaining FIFO order."""
        q = ArrayQueue()
        for n in range(45): q.enqueue(n)
        for n in range(20): self.assertEqual(q.dequeue(), n)
        for n in range(45, 85): q.enqueue(n)
        self.assertEqual([q.dequeue() for _ in range(len(q))], list(range(20, 85)))
        with self.assertRaises(IndexError): q.dequeue()

    def test_linked_list(self):
        """Exercise head, middle, and tail updates, including empty-to-nonempty."""
        ll = SinglyLinkedList()
        ll.append(2); ll.prepend(1); ll.append(4); ll.insert(2, 3)
        self.assertEqual(ll.traverse(), [1, 2, 3, 4])
        self.assertEqual(ll.delete(0), 1)
        self.assertEqual(ll.delete(2), 4)
        self.assertEqual(ll.delete(1), 3)
        self.assertEqual(ll.delete(0), 2)
        self.assertEqual(ll.traverse(), [])
        ll.append(6)
        self.assertEqual(ll.traverse(), [6])


if __name__ == '__main__': unittest.main()
