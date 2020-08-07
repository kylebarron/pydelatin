#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
namespace py = pybind11;

#include "pybind11_glm.hpp"

#include <chrono>
#include <functional>
#include <iostream>
#include <string>

#include "base.h"
#include "heightmap.h"
#include "stl.h"
#include "triangulator.h"

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

std::vector<glm::vec3> test(int width, int height, std::vector<float> data) {
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
  return points;
  // return w * h;
}

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

    m.def("test", &test, "Add two NumPy arrays");

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
