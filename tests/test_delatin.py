import numpy as np
import pytest

from pydelatin import Delatin


def test_fuji_mesh(fuji):
    # Matches the benchmark output documented in the README
    tin = Delatin(fuji, max_error=30)
    assert tin.vertices.shape == (5668, 3)
    assert tin.triangles.shape == (11140, 3)


def test_output_types(fuji):
    tin = Delatin(fuji, max_error=30)
    assert tin.triangles.dtype == np.uint32
    assert tin.triangles.max() < len(tin.vertices)


def test_error_within_max_error(fuji):
    tin = Delatin(fuji, max_error=10)
    assert tin.error <= 10


def test_vertices_within_grid(fuji):
    tin = Delatin(fuji, max_error=30)
    height, width = fuji.shape
    assert tin.vertices[:, 0].min() >= 0
    assert tin.vertices[:, 0].max() <= width
    assert tin.vertices[:, 1].min() >= 0
    assert tin.vertices[:, 1].max() <= height


def test_lower_max_error_gives_more_triangles(fuji):
    coarse = Delatin(fuji, max_error=30)
    fine = Delatin(fuji, max_error=5)
    assert len(fine.triangles) > len(coarse.triangles)


def test_max_triangles(fuji):
    tin = Delatin(fuji, max_error=0, max_triangles=1000)
    assert len(tin.triangles) <= 1000


def test_flat_input_matches_2d(fuji):
    height, width = fuji.shape
    tin_2d = Delatin(fuji, max_error=30)
    tin_1d = Delatin(fuji.ravel(), height=height, width=width, max_error=30)
    np.testing.assert_array_equal(tin_1d.vertices, tin_2d.vertices)
    np.testing.assert_array_equal(tin_1d.triangles, tin_2d.triangles)


def test_flat_input_requires_dimensions(fuji):
    with pytest.raises(ValueError, match="Height and width must be passed"):
        Delatin(fuji.ravel(), max_error=30)
