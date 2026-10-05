"""Build configuration for the `_pydelatin` C++ extension.

Project metadata lives in pyproject.toml. This file only declares the C++
extension, which setuptools can't yet configure from pyproject.toml alone.
"""

from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "_pydelatin",
        # Sort source files for reproducibility
        sorted(str(path) for path in Path("src").glob("*.cpp")),
    ),
]

setup(ext_modules=ext_modules, cmdclass={"build_ext": build_ext})
