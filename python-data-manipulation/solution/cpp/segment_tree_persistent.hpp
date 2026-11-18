#pragma once
#ifndef SOLVER_SEGMENT_TREE_PERSISTENT_HPP
#define SOLVER_SEGMENT_TREE_PERSISTENT_HPP

#include <cstdint>
#include <cstring>
#include <vector>
#include <memory>
#include <stdexcept>
#include <functional>
#include <unordered_map>

namespace solver {
namespace datastructures {

/**
 * @brief A persistent segment tree implementation that maintains all historical versions.
 * 
 * This class implements a persistent segment tree where each update creates a new version
 * of the tree without modifying the previous versions. This allows querying any historical
 * version of the tree.
 */
class SegmentTreePersistent {
public:
    /**
     * @brief Function pointer type for merge operations
     * 
     * @param left Pointer to the left node's data
     * @param right Pointer to the right node's data
     * @param result Pointer to where the merged result should be stored
     */
    using MergeFunction = void (*)(const void* left, const void* right, void* result);

    /**
     * @brief Struct representing a node in the persistent segment tree
     */
    struct Node {
        std::vector<uint8_t> data;  // Node data
        int left_child;             // Index of left child node
        int right_child;            // Index of right child node
        
        Node(size_t element_size) : data(element_size, 0), left_child(-1), right_child(-1) {}
    };

    /**
     * @brief Constructor for SegmentTreePersistent
     * 
     * @param data Pointer to the input array data
     * @param size Number of elements in the input array
     * @param element_size Size of each element in bytes
     * @param merge_func Function pointer to the merge operation
     */
    SegmentTreePersistent(const void* data, size_t size, size_t element_size, MergeFunction merge_func);
    
    /**
     * @brief Destructor
     */
    virtual ~SegmentTreePersistent();
    
    /**
     * @brief Update a single element in the segment tree, creating a new version
     * 
     * @param idx Index of the element to update
     * @param value New value for the element
     * @return Version number of the new tree
     */
    int update(int version, size_t idx, const void* value);
    
    /**
     * @brief Query the segment tree for a range in a specific version
     * 
     * @param version Version of the tree to query
     * @param left Left boundary of the range (inclusive)
     * @param right Right boundary of the range (inclusive)
     * @param result Pointer to where the query result should be stored
     */
    void query(int version, size_t left, size_t right, void* result);

    /**
     * @brief Get the number of versions in the persistent segment tree
     * 
     * @return Number of versions
     */
    int version_count() const { return static_cast<int>(roots_.size()); }
    
    /**
     * @brief Get the size of the underlying array
     * 
     * @return Size of the array
     */
    size_t size() const { return n_; }
    
    /**
     * @brief Get the size of each element in bytes
     * 
     * @return Size of each element in bytes
     */
    size_t element_size() const { return element_size_; }

protected:
    /**
     * @brief Build the initial segment tree
     * 
     * @param start Start of the current segment
     * @param end End of the current segment
     * @return Index of the root node
     */
    int build(size_t start, size_t end);
    
    /**
     * @brief Update the segment tree recursively, creating a new path
     * 
     * @param node_idx Index of the current node
     * @param start Start of the current segment
     * @param end End of the current segment
     * @param idx Index to update
     * @param value New value
     * @return Index of the new or reused node
     */
    int update(int node_idx, size_t start, size_t end, size_t idx, const void* value);
    
    /**
     * @brief Query the segment tree recursively
     * 
     * @param node_idx Index of the current node
     * @param start Start of the current segment
     * @param end End of the current segment
     * @param left Left boundary of the query
     * @param right Right boundary of the query
     * @param result Pointer to where the query result should be stored
     */
    void query(int node_idx, size_t start, size_t end, size_t left, size_t right, void* result);

    /**
     * @brief Create a new node with the same data as an existing node
     * 
     * @param node_idx Index of the node to clone
     * @return Index of the new node
     */
    int clone_node(int node_idx);

    // Original data array
    std::vector<uint8_t> orig_data_;
    
    // All nodes in the persistent segment tree
    std::vector<Node> nodes_;
    
    // Root node indices for each version
    std::vector<int> roots_;
    
    // Size of each element in bytes
    size_t element_size_;
    
    // Size of the original array
    size_t n_;
    
    // Merge function pointer
    MergeFunction merge_func_;
    
    // Temporary buffer for merge operations
    std::vector<uint8_t> temp_buffer_;
};

} // namespace datastructures
} // namespace solver

#endif // SOLVER_SEGMENT_TREE_PERSISTENT_HPP
