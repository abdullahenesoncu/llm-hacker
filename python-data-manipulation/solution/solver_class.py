import numpy as np

from _solver import _SegmentTreePersistent


class Solver:
    """
    Persistent segment tree over a NumPy array (primitive or structured dtype).

    merge_func is a numba cfunc void(T*, T*, T*) called as merge(left, right, out).
    """

    def __init__(
        self,
        data,
        merge_func,
    ):
        data = np.array(data)
        if data.ndim != 1:
            raise ValueError("Data must be a one-dimensional array")
        if len(data) == 0:
            raise ValueError("Data array cannot be empty")

        self._dtype = data.dtype
        self._tree = _SegmentTreePersistent(
            np.frombuffer(np.ascontiguousarray(data).tobytes(), dtype=np.uint8),
            self._dtype.itemsize,
            merge_func.address,
        )
        # Keep the cfunc alive for as long as the tree may call it.
        self._merge_func = merge_func

        self.size = len(data)

    def update(self, version, index, value):
        """
        Update a value in the tree, creating a new version.

        Returns:
            int: The new version number
        """
        if version < 0 or version >= self.version_count:
            raise IndexError(f"Version {version} out of bounds")

        if index < 0 or index >= self.size:
            raise IndexError(f"Index {index} out of bounds")

        item = np.array([value], dtype=self._dtype)
        return self._tree.update(version, index, np.frombuffer(item.tobytes(), dtype=np.uint8))

    def query(self, version, left, right):
        """
        Query an inclusive range in a specific version of the tree.
        """
        if version < 0 or version >= self.version_count:
            raise IndexError(f"Version {version} out of bounds")

        if left < 0 or left >= self.size:
            raise IndexError(f"Left index {left} out of bounds")

        if right < 0 or right >= self.size:
            raise IndexError(f"Right index {right} out of bounds")

        if left > right:
            raise ValueError("Left index must be <= right index")

        result = np.frombuffer(self._tree.query(version, left, right).tobytes(), dtype=self._dtype)[0]
        return result if self._dtype.names else result.item()

    @property
    def version_count(self):
        """Get the number of versions in the tree."""
        return self._tree.version_count()
