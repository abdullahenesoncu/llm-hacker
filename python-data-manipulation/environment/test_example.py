"""
Outline of what the real tests check. These are not runnable tests:
each function only describes a behavior that will be verified.
"""

import unittest


class TestSolverOutline(unittest.TestCase):

    def test_initial_state(self):
        """After construction, version_count is 1, size equals the array length, and version 0 answers queries."""
        raise NotImplementedError()

    def test_update_returns_new_version_id(self):
        """update() returns the previous version_count and increases version_count by 1, also when updating old versions."""
        raise NotImplementedError()

    def test_update_does_not_modify_given_version(self):
        """The version an update starts from never changes; the new version differs only at the updated index."""
        raise NotImplementedError()

    def test_all_ranges_small_sizes(self):
        """For several small array sizes (including 1), every [left, right] range of version 0 matches the brute-force result."""
        raise NotImplementedError()

    def test_random_online_operations(self):
        """Random interleaved updates (on random existing versions) and queries match brute-force copies of every version, using a sum merge on int64 items."""
        raise NotImplementedError()

    def test_other_primitive_merge_functions(self):
        """Other merge functions on int64 items (max, and a non-commutative 'keep left') give correct results on many versions and ranges."""
        raise NotImplementedError()

    def test_merge_order_is_preserved(self):
        """With a non-commutative merge on record items (e.g. a polynomial hash), results on many versions and ranges equal the left-to-right fold."""
        raise NotImplementedError()

    def test_record_update_values_and_query_type(self):
        """For record items, update accepts a tuple or a NumPy structured scalar, and query returns a structured scalar with the field names."""
        raise NotImplementedError()

    def test_float_items(self):
        """float64 items work with another merge function (e.g. min) and queries return plain Python floats."""
        raise NotImplementedError()

    def test_int_query_returns_plain_int(self):
        """Queries on int64 items return a plain Python int."""
        raise NotImplementedError()

    def test_input_data_is_copied(self):
        """Changing the caller's array after construction does not change the solver."""
        raise NotImplementedError()

    def test_query_index_out_of_range(self):
        """IndexError for an out-of-range (including negative) version, left or right in query."""
        raise NotImplementedError()

    def test_update_index_out_of_range(self):
        """IndexError for an out-of-range (including negative) version or index in update."""
        raise NotImplementedError()

    def test_left_greater_than_right(self):
        """ValueError when left > right and both are in range."""
        raise NotImplementedError()

    def test_failed_calls_do_not_change_state(self):
        """A failed call creates no version and changes no result."""
        raise NotImplementedError()

    def test_build_updates_and_queries_performance(self):
        """With N=200,000: build + 250,000 updates and 250,000 queries on random versions finish under the time limit, peak memory stays under the limit, and sampled answers are correct."""
        raise NotImplementedError()

    def test_build_and_queries_only_performance(self):
        """With N=200,000: build + 500,000 range queries on version 0 finish under the time limit, peak memory stays under the limit, and all answers are correct."""
        raise NotImplementedError()


if __name__ == "__main__":
    unittest.main()
