#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "pybind11_glm.hpp"

#include <chrono>
#include <functional>
#include <iostream>
#include <string>

#include "base.h"
#include "heightmap.h"
#include "triangulator.h"

namespace py = pybind11;

int num_pixels(std::string inFile) {
    const auto hm = std::make_shared<Heightmap>(inFile);
    int w = hm->Width();
    int h = hm->Height();
    return w * h;
}

py::array_t<double> add_arrays(py::array_t<double> input1, py::array_t<double> input2) {
    py::buffer_info buf1 = input1.request(), buf2 = input2.request();

    if (buf1.ndim != 1 || buf2.ndim != 1)
        throw std::runtime_error("Number of dimensions must be one");

    if (buf1.size != buf2.size)
        throw std::runtime_error("Input shapes must match");

    /* No pointer is passed, so NumPy will allocate the buffer */
    auto result = py::array_t<double>(buf1.size);

    py::buffer_info buf3 = result.request();

    double *ptr1 = (double *) buf1.ptr,
           *ptr2 = (double *) buf2.ptr,
           *ptr3 = (double *) buf3.ptr;

    for (size_t idx = 0; idx < buf1.shape[0]; idx++)
        ptr3[idx] = ptr1[idx] + ptr2[idx];

    return result;
}

Triangulator create_mesh(int width, int height, std::vector<float> data) {
  const auto hm = std::make_shared<Heightmap>(width, height, data);
  int w = hm->Width();
  int h = hm->Height();

  const float maxError = 0.001;
  const float zScale = 1;
  const float zExaggeration = 1;
  const int maxTriangles = 0;
  const int maxPoints = 0;

  Triangulator tri(hm);
  tri.Run(maxError, maxTriangles, maxPoints);
  auto points = tri.Points(zScale * zExaggeration);
  auto triangles = tri.Triangles();
  return tri;
}

struct Pet {
    Pet(const std::string &name) : name(name) { }
    void setName(const std::string &name_) { name = name_; }
    const std::string &getName() const { return name; }

    std::string name;
};

struct PydelatinTriangulator {
    PydelatinTriangulator(const int &width, const int &height) : width(width), height(height) { }

    void setWidth(const int &width_) { width = width_; }
    const int &getWidth() const { return width; }

    void setHeight(const int &height_) { height = height_; }
    const int &getHeight() const { return height; }

    int width;
    int height;
};

PYBIND11_MODULE(pydelatin, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------

        .. currentmodule:: python_example

        .. autosummary::
           :toctree: _generate

           add
           subtract
    )pbdoc";

    py::class_<Pet>(m, "Pet")
        .def(py::init<const std::string &>())
        .def("setName", &Pet::setName)
        .def("getName", &Pet::getName);

    py::class_<PydelatinTriangulator>(m, "PydelatinTriangulator")
        .def(py::init<const int &, const int &>())
        .def("setWidth", &PydelatinTriangulator::setWidth)
        .def("getWidth", &PydelatinTriangulator::getWidth)
        .def("setHeight", &PydelatinTriangulator::setHeight)
        .def("getHeight", &PydelatinTriangulator::getHeight)
        ;

    // m.def("add", &add, R"pbdoc(
    //     Add two numbers
    //
    //     Some other explanation about the add function.
    // )pbdoc");

    m.def("num_pixels", &num_pixels, R"pbdoc(
        Say Hello world!

        Some other explanation about the add function.
    )pbdoc");

    m.def("add_arrays", &add_arrays, "Add two NumPy arrays");

    m.def("create_mesh", &create_mesh, "Add two NumPy arrays");

    // m.def("test", &test, R"pbdoc(
    //     Test!
    //
    //     Some other explanation about the add function.
    // )pbdoc");

    m.def("subtract", [](int i, int j) { return i - j; }, R"pbdoc(
        Subtract two numbers

        Some other explanation about the subtract function.
    )pbdoc");

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
