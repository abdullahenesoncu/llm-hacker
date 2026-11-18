#include "segment_tree_persistent.hpp"
#include <algorithm>
#include <cstring>
#include <stdexcept>

namespace solver {
namespace datastructures {

SegmentTreePersistent::SegmentTreePersistent(const void* data, size_t size, size_t element_size, MergeFunction merge_func)
    : element_size_(element_size), n_(size), merge_func_(merge_func) {
    if (size == 0) {
        throw std::invalid_argument("Input array size cannot be zero");
    }
    
    if (element_size == 0) {
        throw std::invalid_argument("Element size cannot be zero");
    }
    
    if (!merge_func) {
        throw std::invalid_argument("Merge function cannot be null");
    }

    // Copy original data
    orig_data_.resize(size * element_size);
    std::memcpy(orig_data_.data(), data, size * element_size);
    
    // Allocate temporary buffer for merge operations
    temp_buffer_.resize(element_size);
    
    // Build the initial segment tree (version 0)
    int root = build(0, n_ - 1);
    roots_.push_back(root);
}

SegmentTreePersistent::~SegmentTreePersistent() = default;

int SegmentTreePersistent::build(size_t start, size_t end) {
    // Create a new node
    nodes_.emplace_back(element_size_);
    int node_idx = static_cast<int>(nodes_.size()) - 1;
    
    if (start == end) {
        // Leaf node, copy the original value
        std::memcpy(nodes_[node_idx].data.data(), orig_data_.data() + (start * element_size_), element_size_);
        return node_idx;
    }
    
    size_t mid = start + (end - start) / 2;
    
    // Recursively build left and right subtrees
    int left_child = build(start, mid);
    int right_child = build(mid + 1, end);
    
    nodes_[node_idx].left_child = left_child;
    nodes_[node_idx].right_child = right_child;
    
    // Merge the results from left and right children
    merge_func_(
        nodes_[left_child].data.data(),
        nodes_[right_child].data.data(),
        nodes_[node_idx].data.data()
    );
    
    return node_idx;
}

int SegmentTreePersistent::clone_node(int node_idx) {
    if (node_idx == -1) return -1;
    
    // Create a new node as a copy of the existing one
    nodes_.emplace_back(element_size_);
    int new_idx = static_cast<int>(nodes_.size()) - 1;
    
    // Copy data and child pointers
    std::memcpy(nodes_[new_idx].data.data(), nodes_[node_idx].data.data(), element_size_);
    nodes_[new_idx].left_child = nodes_[node_idx].left_child;
    nodes_[new_idx].right_child = nodes_[node_idx].right_child;
    
    return new_idx;
}

int SegmentTreePersistent::update(int version, size_t idx, const void* value) {
    if (version < 0 || version >= static_cast<int>(roots_.size())) {
        throw std::out_of_range("Version out of bounds");
    }
    
    if (idx >= n_) {
        throw std::out_of_range("Index out of bounds");
    }
    
    // Update original data for potential future versions
    std::memcpy(orig_data_.data() + (idx * element_size_), value, element_size_);
    
    // Create a new version by updating from the specified version
    int new_root = update(roots_[version], 0, n_ - 1, idx, value);
    roots_.push_back(new_root);
    
    return static_cast<int>(roots_.size()) - 1; // Return the new version number
}

int SegmentTreePersistent::update(int node_idx, size_t start, size_t end, size_t idx, const void* value) {
    // Create a new node
    int new_idx = clone_node(node_idx);
    
    if (start == end) {
        // Leaf node, update the value
        std::memcpy(nodes_[new_idx].data.data(), value, element_size_);
        return new_idx;
    }
    
    size_t mid = start + (end - start) / 2;
    
    // Recursively update the appropriate subtree
    if (idx <= mid) {
        int new_left = update(nodes_[new_idx].left_child, start, mid, idx, value);
        nodes_[new_idx].left_child = new_left;
    } else {
        int new_right = update(nodes_[new_idx].right_child, mid + 1, end, idx, value);
        nodes_[new_idx].right_child = new_right;
    }
    
    // Re-compute the value for the current node
    merge_func_(
        nodes_[nodes_[new_idx].left_child].data.data(),
        nodes_[nodes_[new_idx].right_child].data.data(),
        nodes_[new_idx].data.data()
    );
    
    return new_idx;
}

void SegmentTreePersistent::query(int version, size_t left, size_t right, void* result) {
    if (version < 0 || version >= static_cast<int>(roots_.size())) {
        throw std::out_of_range("Version out of bounds");
    }
    
    if (left > right || left >= n_ || right >= n_) {
        throw std::out_of_range("Query range out of bounds");
    }
    
    // Call the recursive query function on the root of the specified version
    query(roots_[version], 0, n_ - 1, left, right, result);
}

void SegmentTreePersistent::query(int node_idx, size_t start, size_t end, size_t left, size_t right, void* result) {
    if (node_idx == -1 || start > right || end < left) {
        // No overlap
        std::memset(result, 0, element_size_);
        return;
    }

    if (start >= left && end <= right) {
        // Complete overlap
        std::memcpy(result, nodes_[node_idx].data.data(), element_size_);
        return;
    }

    // Partial overlap
    size_t mid = start + (end - start) / 2;
    int left_child = nodes_[node_idx].left_child;
    int right_child = nodes_[node_idx].right_child;

    if (right <= mid) {
        // Only left child overlaps
        query(left_child, start, mid, left, right, result);
    } else if (left > mid) {
        // Only right child overlaps
        query(right_child, mid + 1, end, left, right, result);
    } else {
        // Both children overlap
        std::vector<uint8_t> left_result(element_size_);
        std::vector<uint8_t> right_result(element_size_);
        query(left_child, start, mid, left, right, left_result.data());
        query(right_child, mid + 1, end, left, right, right_result.data());
        merge_func_(left_result.data(), right_result.data(), result);
    }
}


} // namespace datastructures
} // namespace solver
