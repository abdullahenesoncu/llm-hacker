from setuptools import setup, find_packages, Extension
import os
import platform
import sys
from setuptools.command.build_ext import build_ext

# Custom build_ext command to handle compilation
class BuildExt(build_ext):
    def finalize_options(self):
        build_ext.finalize_options(self)
        # Import numpy here, when it's definitely installed
        import numpy
        import pybind11
        for ext in self.extensions:
            ext.include_dirs.append(pybind11.get_include())
        # Add numpy headers to include dirs
        for ext in self.extensions:
            # Always use string literal for numpy include
            numpy_include = numpy.get_include()
            if os.path.isabs(numpy_include):
                # Convert to relative if needed
                numpy_include = os.path.relpath(numpy_include)
            ext.include_dirs.append(numpy_include)
    
    def build_extensions(self):
        # Determine correct compiler options for the platform
        c_opts = []
        l_opts = []

        if sys.platform == 'darwin':
            darwin_opts = ['-stdlib=libc++', '-mmacosx-version-min=10.14']
            c_opts += darwin_opts
            l_opts += darwin_opts

        # Apply compiler options
        for ext in self.extensions:
            ext.extra_compile_args += c_opts
            ext.extra_link_args += l_opts
        
        build_ext.build_extensions(self)

# Define the extension module directly with hardcoded relative paths
ext_modules = [
    Extension(
        '_solver',  # Extension name
        sources=[
            # Use explicit relative paths
            'cpp/bindings.cpp',
            'cpp/segment_tree_persistent.cpp',
        ],
        include_dirs=[
            'cpp/include',  # Our C++ headers
        ],
        language='c++',
        extra_compile_args=['-std=c++17', '-O3'] if platform.system() != 'Windows' else ['/std:c++17', '/O2'],
    ),
]

setup(
    name="solver",
    version="0.1.0",
    author="Solver Team",
    author_email="example@example.com",
    description="Fast algorithms in C++ with Python bindings",
    url="https://github.com/abdullahenesoncu/solver",
    packages=["solver"],
    package_dir={"solver": "./"},
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExt},
    install_requires=[
        'numpy>=1.20.0',
        'numba>=0.53.0',
        'pybind11>=2.6.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
