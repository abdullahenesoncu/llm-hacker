cmake_minimum_required(VERSION 3.14)
project(solver VERSION 0.1.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find Python
find_package(Python 3.9 REQUIRED COMPONENTS Interpreter Development)

# Find pybind11
set(PYBIND11_PYTHON_VERSION 3.9)
if(NOT pybind11_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG        v2.11.1  # Update to latest stable version
    )
    FetchContent_MakeAvailable(pybind11)
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Gather source files
file(GLOB_RECURSE SOURCES 
    "${CMAKE_CURRENT_SOURCE_DIR}/datastructures/*.cpp"
)

# Add the Python module
pybind11_add_module(_solver 
    ${SOURCES}
    "${CMAKE_CURRENT_SOURCE_DIR}/bindings.cpp"
)

# Set properties for the Python module
set_target_properties(_solver PROPERTIES 
    OUTPUT_NAME "_solver"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/../python/solver"
)

# Add compiler flags
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(_solver PRIVATE -Wall -Wextra -O3)
elseif(MSVC)
    target_compile_options(_solver PRIVATE /W4 /O2)
endif()
