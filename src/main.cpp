#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

// No longer needed because I'm creating numpy arrays to pass back
// #include "pybind11_glm.hpp"

#include <chrono>
#include <functional>
#include <iostream>
#include <string>

#include "base.h"
#include "heightmap.h"
#include "triangulator.h"

namespace py = pybind11;

struct PydelatinTriangulator {
    PydelatinTriangulator(
      const int width, const int height,
      const float maxError, const float zScale, const float zExaggeration,
      const int maxTriangles, const int maxPoints, const bool level,
      const bool invert, const int blurSigma, const float gamma,
      const int borderSize, const float borderHeight, const float baseHeight
    ) :
      width(width), height(height), maxError(maxError), zScale(zScale),
      zExaggeration(zExaggeration), maxTriangles(maxTriangles), maxPoints(maxPoints),
      level(level), invert(invert), blurSigma(blurSigma), gamma(gamma),
      borderSize(borderSize), borderHeight(borderHeight), baseHeight(baseHeight)
      { }

    void setWidth(const int &width_) { width = width_; }
    const int &getWidth() const { return width; }

    void setHeight(const int &height_) { height = height_; }
    const int &getHeight() const { return height; }

    void setMaxError(const float &maxError_) { maxError = maxError_; }
    const float &getMaxError() const { return maxError; }

    void setData(const py::array_t<float> &data_) {
      // x must have ndim = 1; can be non-writeable
      auto r = data_.unchecked<1>();
      ssize_t size = r.shape(0);

      std::vector<float> data__(size);

      for (size_t i = 0; i < size; i++) {
          data__[i] = r(i);
      }

      data = data__;
    }

    // https://stackoverflow.com/a/49693704
    const py::array_t<float> getPoints() const {
      /* No pointer is passed, so NumPy will allocate the buffer */
      auto result = py::array_t<float>(points.size() * 3);

      py::buffer_info buf = result.request();

      float *ptr1 = (float *) buf.ptr;

      for (size_t i = 0; i < points.size(); i++) {
        const auto &p = points[i];
        ptr1[i * 3 + 0] = p.x;
        ptr1[i * 3 + 1] = p.y;
        ptr1[i * 3 + 2] = p.z;
      }

      return result;
    }

    const py::array_t<int32_t> getTriangles() const {
      /* No pointer is passed, so NumPy will allocate the buffer */
      auto result = py::array_t<int32_t>(triangles.size() * 3);

      py::buffer_info buf = result.request();

      int32_t *ptr1 = (int32_t *) buf.ptr;

      for (size_t i = 0; i < triangles.size(); i++) {
        const auto &p = triangles[i];
        ptr1[i * 3 + 0] = p.x;
        ptr1[i * 3 + 1] = p.y;
        ptr1[i * 3 + 2] = p.z;
      }

      return result;
    }

    const float &getError() const { return error; }

    void run() {
        const auto hm = std::make_shared<Heightmap>(width, height, data);
        // auto level heightmap
        if (level) {
            hm->AutoLevel();
        }

        // invert heightmap
        if (invert) {
            hm->Invert();
        }

        // blur heightmap
        if (blurSigma > 0) {
            hm->GaussianBlur(blurSigma);
        }

        // apply gamma curve
        if (gamma > 0) {
            hm->GammaCurve(gamma);
        }

        // add border
        if (borderSize > 0) {
            hm->AddBorder(borderSize, borderHeight);
        }

        // get updated size
        int w = hm->Width();
        int h = hm->Height();

        Triangulator tri(hm);
        tri.Run(maxError, maxTriangles, maxPoints);
        points = tri.Points(zScale * zExaggeration);
        triangles = tri.Triangles();
        error = tri.Error();

        // add base
        if (baseHeight > 0) {
            const float z = -baseHeight * zScale * zExaggeration;
            AddBase(points, triangles, w, h, z);
        }
    }

    int width;
    int height;
    float maxError;
    float zScale;
    float zExaggeration;
    int maxTriangles;
    int maxPoints;
    bool level;
    bool invert;
    int blurSigma;
    float gamma;
    int borderSize;
    float borderHeight;
    float baseHeight;

    std::vector<float> data;
    std::vector<glm::vec3> points;
    std::vector<glm::ivec3> triangles;
    float error;
};

PYBIND11_MODULE(_pydelatin, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------

        .. currentmodule:: python_example

        .. autosummary::
           :toctree: _generate

           add
           subtract
    )pbdoc";

    py::class_<PydelatinTriangulator>(m, "PydelatinTriangulator")
        .def(py::init<
          const int, const int,
          const float, const float, const float,
          const int, const int, const bool, const bool, const int,
          const float, const int, const float, const float
          >())
        .def("setWidth", &PydelatinTriangulator::setWidth)
        .def("getWidth", &PydelatinTriangulator::getWidth)
        .def("setHeight", &PydelatinTriangulator::setHeight)
        .def("getHeight", &PydelatinTriangulator::getHeight)
        .def("setMaxError", &PydelatinTriangulator::setMaxError)
        .def("getMaxError", &PydelatinTriangulator::getMaxError)
        .def("setData", &PydelatinTriangulator::setData)
        .def("getPoints", &PydelatinTriangulator::getPoints)
        .def("getTriangles", &PydelatinTriangulator::getTriangles)
        .def("getError", &PydelatinTriangulator::getError)
        .def("run", &PydelatinTriangulator::run)
        ;

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
