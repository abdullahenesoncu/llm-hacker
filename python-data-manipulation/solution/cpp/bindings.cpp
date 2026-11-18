#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>
#include <cstdint>  // for uintptr_t

#include "segment_tree_persistent.hpp"

namespace py = pybind11;
using namespace solver::datastructures;

// Function pointer types
using MergeFuncType = void (*)(const void*, const void*, void*);
using PropagateFuncType = void (*)(void*, const void*, void*, size_t, size_t);
using MergeLazyFuncType = void (*)(void*, const void*, void*);

PYBIND11_MODULE(_solver, m) {
    m.doc() = "C++ implementation of fast algorithms and data structures for Python";

    // SegmentTreePersistent
    py::class_<SegmentTreePersistent>(m, "_SegmentTreePersistent")
        .def(py::init([](py::array_t<uint8_t> data, size_t element_size, uintptr_t merge_func_addr) {
            if (!data.request().ptr) throw std::runtime_error("Empty input array");
            py::buffer_info buf = data.request();
            size_t size = buf.size / element_size;

            MergeFuncType merge_func = reinterpret_cast<MergeFuncType>(merge_func_addr);
            return new SegmentTreePersistent(buf.ptr, size, element_size, merge_func);
        }),
        py::arg("data"), py::arg("element_size"), py::arg("merge_func_addr"))
        .def("update", [](SegmentTreePersistent& self, int version, size_t idx, py::array_t<uint8_t> value) {
            py::buffer_info buf = value.request();
            if (buf.size != self.element_size()) throw std::runtime_error("Value size mismatch");
            return self.update(version, idx, buf.ptr);
        })
        .def("query", [](SegmentTreePersistent& self, int version, size_t left, size_t right) {
            py::array_t<uint8_t> result(self.element_size());
            py::buffer_info buf = result.request();
            self.query(version, left, right, buf.ptr);
            return result;
        })
        .def("size", &SegmentTreePersistent::size)
        .def("element_size", &SegmentTreePersistent::element_size)
        .def("version_count", &SegmentTreePersistent::version_count);
}
