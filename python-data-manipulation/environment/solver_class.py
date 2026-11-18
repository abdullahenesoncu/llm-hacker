class Solver:
    """
    This class is for managing a version keeping data manipulation structure.
    It supports updating values and querying ranges while keeping track of all versions.
    It requires a merge function to combine items and supports querying any previous state.
    """

    def __init__(
        self,
        data,
        merge_func,
    ):
        """
        data is a one-dimensional non-empty NumPy array. Its dtype is either a primitive
        dtype (for example int64 or float64) or a structured (record) dtype.
        merge_func is a numba cfunc with the signature void(CPointer(T), CPointer(T), CPointer(T)),
        where T is the numba type of one item (numba.types.int64, numba.types.float64,
        numba.from_dtype(record_dtype), ...). It is called as merge(left, right, out) with
        pointers to items and must write the merge of left and right into out.
        merge_func.address is the address of the compiled function.

        The solver must expose the array length as the attribute `size`.
        """
        raise NotImplementedError("Solver class initialization is not implemented yet")

    def update(self, version, index, value):
        """
        Update a value in the tree, creating a new version.
        It should raise IndexError if the version or index is out of bounds.

        Args:
            version: The version to start from
            index: Index to update
            value: New value. A Python/NumPy scalar for primitive dtypes; for record dtypes
                a tuple of field values or a NumPy structured scalar.

        Returns:
            int: The new version number
        """
        raise NotImplementedError("Update method is not implemented yet")

    def query(self, version, left, right):
        """
        Query a range in a specific version of the tree.
        It should raise IndexError if the version or indices are out of bounds
        and ValueError if left > right.

        Args:
            version: The version to query
            left: Left index (inclusive)
            right: Right index (inclusive)

        Returns:
            The merge of the items in the range, in array order. A plain Python int/float
            for primitive dtypes; a NumPy structured scalar (numpy.void) for record dtypes.
        """
        raise NotImplementedError("Query method is not implemented yet")

    @property
    def version_count(self):
        """Get the number of versions in the tree."""
        raise NotImplementedError("version_count property is not implemented yet")
