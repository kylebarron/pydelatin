# type: ignore
# pylint: disable=import-outside-toplevel
from glob import glob

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

ext_modules = [
    Pybind11Extension(
        "_pydelatin",
        sorted(glob("src/*.cpp")),  # Sort source files for reproducibility
    ),
]


setup(
    name="pydelatin",
    version="0.2.8",
    python_requires=">=3.6",
    author="Kyle Barron",
    author_email="kylebarron2@gmail.com",
    url="https://github.com/kylebarron/pydelatin",
    description="A wrapper for hmm",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["pydelatin", "pydelatin.*"]),
    ext_modules=ext_modules,
    install_requires=["numpy"],
    extras_require={"test": ["pytest", "pytest-benchmark", "imageio"]},
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
