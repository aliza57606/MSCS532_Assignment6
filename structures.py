"""Educational implementations of elementary data structures in pure Python.

No deque or linked-list library is used. DynamicArray uses a fixed-capacity
backing store (a Python list of placeholders) and explicitly shifts/resizes.
"""
from typing import Any


class DynamicArray:
    """Resizable indexed array, analogous to a simple vector."""
    def __init__(self):
        # Logical length and allocated capacity are deliberately separate.
        self._size, self._capacity = 0, 2
        self._data = [None] * self._capacity

    def __len__(self):
        return self._size

    def _check_index(self, index, allow_end=False):
        """Check bounds; insertion may legally target position ``size``."""
        if not isinstance(index, int) or isinstance(index, bool) or not (0 <= index <= self._size if allow_end else 0 <= index < self._size):
            raise IndexError('array index out of range')

    def _grow(self):
        """Double capacity; infrequent O(n) copies give amortized O(1) append."""
        new = [None] * (self._capacity * 2)
        for i in range(self._size):
            new[i] = self._data[i]
        self._data, self._capacity = new, len(new)

    def access(self, index):
        """Read by index in O(1) time."""
        self._check_index(index)
        return self._data[index]

    def insert(self, index, value):
        """Insert at index; shift following items right in O(n) time."""
        self._check_index(index, allow_end=True)
        if self._size == self._capacity:
            self._grow()
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def append(self, value):
        """Add at the logical end; amortized O(1) time."""
        self.insert(self._size, value)

    def delete(self, index):
        """Remove by position; close the gap by shifting remaining items left."""
        self._check_index(index)
        value = self._data[index]
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._size -= 1
        self._data[self._size] = None  # Drop stale reference after shifting.
        return value

    def to_list(self):
        """Return occupied elements only; unused capacity is not visible."""
        return self._data[:self._size]


class Matrix:
    """Rectangular matrix with indexed access and row/column insert/delete."""
    def __init__(self, rows, cols, fill=None):
        """Allocate independent rows instead of aliasing one row repeatedly."""
        if rows < 0 or cols < 0:
            raise ValueError('dimensions must be nonnegative')
        self._cols = cols
        self._rows = [[fill for _ in range(cols)] for _ in range(rows)]

    @property
    def shape(self):
        """Number of rows and columns, including for empty matrices."""
        return (len(self._rows), self._cols)

    def access(self, row, col):
        """Return an element by its row/column coordinates: O(1)."""
        return self._rows[row][col]

    def set(self, row, col, value):
        """Replace one cell without changing the matrix dimensions."""
        self._rows[row][col] = value

    def insert_row(self, index, values):
        """Insert a full-width row, preserving the rectangular shape."""
        if len(values) != self._cols:
            raise ValueError('row length mismatch')
        if not 0 <= index <= len(self._rows):
            raise IndexError('row index out of range')
        self._rows.insert(index, list(values))

    def delete_row(self, index):
        """Remove and return an entire row; following rows shift left."""
        return self._rows.pop(index)

    def insert_column(self, index, values):
        """Insert one supplied value per row at a shared column position."""
        if len(values) != len(self._rows) or not 0 <= index <= self._cols:
            raise ValueError('column shape or position mismatch')
        for row, value in zip(self._rows, values):
            row.insert(index, value)
        self._cols += 1

    def delete_column(self, index):
        """Remove a column from every row and return its former values."""
        if not 0 <= index < self._cols:
            raise IndexError('column index out of range')
        removed = [row.pop(index) for row in self._rows]
        self._cols -= 1
        return removed

    def to_list(self):
        """Return a shallow copy of each row so callers cannot change layout."""
        return [row[:] for row in self._rows]


class ArrayStack:
    """Last-in-first-out stack; append/pop at end provide amortized O(1)."""
    def __init__(self):
        self._items = []

    def push(self, value):
        """Push onto the end of the backing array (amortized O(1))."""
        self._items.append(value)

    def pop(self):
        """Remove the most recently pushed item (LIFO); reject empty stack."""
        if not self._items:
            raise IndexError('pop from empty stack')
        return self._items.pop()

    def peek(self):
        """Inspect the top element without removing it."""
        if not self._items:
            raise IndexError('peek from empty stack')
        return self._items[-1]

    def __len__(self):
        return len(self._items)


class ArrayQueue:
    """Circular buffer queue: O(1) amortized enqueue, O(1) dequeue."""
    def __init__(self):
        self._data = [None] * 2
        self._front, self._size = 0, 0

    def __len__(self):
        return self._size

    def _grow(self):
        """Double storage and linearize wrapped items in FIFO order."""
        bigger = [None] * (len(self._data) * 2)
        for i in range(self._size):
            bigger[i] = self._data[(self._front + i) % len(self._data)]
        self._data, self._front = bigger, 0

    def enqueue(self, value):
        """Add at the logical back using circular-index arithmetic."""
        if self._size == len(self._data):
            self._grow()
        # Modulo wraps the tail index when it reaches the end of the buffer.
        index = (self._front + self._size) % len(self._data)
        self._data[index] = value
        self._size += 1

    def dequeue(self):
        """Remove from the logical front in O(1), without shifting items."""
        if not self._size:
            raise IndexError('dequeue from empty queue')
        value = self._data[self._front]
        self._data[self._front] = None  # Release the vacated slot.
        self._front = (self._front + 1) % len(self._data)
        self._size -= 1
        return value

    def peek(self):
        """Read the next FIFO value without changing the queue."""
        if not self._size:
            raise IndexError('peek from empty queue')
        return self._data[self._front]


class _Node:
    """Private linked-list element storing a value and its next pointer."""
    def __init__(self, value, next_node=None):
        self.value, self.next = value, next_node


class SinglyLinkedList:
    """Head/tail pointers permit O(1) prepend/append, O(n) traversal."""
    def __init__(self):
        self.head, self.tail, self._size = None, None, 0

    def __len__(self):
        return self._size

    def prepend(self, value):
        """Add a head node in O(1); update tail for the empty-list case."""
        self.head = _Node(value, self.head)
        if self.tail is None:
            self.tail = self.head
        self._size += 1

    def append(self, value):
        """Append in O(1) by retaining the tail pointer."""
        node = _Node(value)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1

    def insert(self, index, value):
        """Insert at a zero-based position; middle insertion needs traversal."""
        if not 0 <= index <= self._size:
            raise IndexError('index out of range')
        if index == 0:
            return self.prepend(value)
        if index == self._size:
            return self.append(value)
        # Reach the predecessor, then reconnect pointers around the new node.
        previous = self.head
        for _ in range(index - 1):
            previous = previous.next
        previous.next = _Node(value, previous.next)
        self._size += 1

    def delete(self, index):
        """Unlink and return a node; fix head/tail when endpoints change."""
        if not 0 <= index < self._size:
            raise IndexError('index out of range')
        if index == 0:
            value = self.head.value
            self.head = self.head.next
            self._size -= 1
            if self._size == 0:
                self.tail = None
            return value
        previous = self.head
        for _ in range(index - 1):
            previous = previous.next
        removed = previous.next
        previous.next = removed.next
        self._size -= 1
        if previous.next is None:
            self.tail = previous
        return removed.value

    def traverse(self):
        """Visit nodes from head to tail in O(n), returning their values."""
        result, current = [], self.head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result


if __name__ == '__main__':
    # Minimal manual smoke test for each implementation. Full tests are in tests/.
    arr = DynamicArray()
    for item in [10, 20, 30]:
        arr.append(item)
    arr.insert(1, 15)
    print('Dynamic array:', arr.to_list())
    m = Matrix(2, 2, 0)
    m.set(0, 1, 9)
    print('Matrix:', m.to_list())
    s = ArrayStack()
    s.push('first'); s.push('second')
    print('Stack pop:', s.pop())
    q = ArrayQueue()
    q.enqueue('first'); q.enqueue('second')
    print('Queue dequeue:', q.dequeue())
    ll = SinglyLinkedList()
    ll.append(10); ll.append(30); ll.insert(1, 20)
    print('Linked list:', ll.traverse())
