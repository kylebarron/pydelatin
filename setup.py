# Project metadata lives in pyproject.toml. This file only declares the C++
# extension, which setuptools can't yet configure from pyproject.toml alone.
from glob import glob

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "_pydelatin",
        sorted(glob("src/*.cpp")),  # Sort source files for reproducibility
    ),
]

setup(ext_modules=ext_modules, cmdclass={"build_ext": build_ext})
