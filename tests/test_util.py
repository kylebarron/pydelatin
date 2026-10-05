import numpy as np
import pytest

from pydelatin.util import decode_ele, latitude_adjustment, rescale_positions


def _rgb_tile(rgb) -> np.ndarray:
    # Use a tile larger than 4px so decode_ele doesn't treat it as band-first
    return np.tile(np.array(rgb, dtype=np.uint8), (8, 8, 1))


def test_decode_ele_mapbox_uint8():
    # (3776 + 10000) * 10 = 137760 = 2 * 65536 + 26 * 256 + 32
    png = _rgb_tile([2, 26, 32])
    terrain = decode_ele(png, "mapbox")
    assert terrain.shape == (8, 8)
    np.testing.assert_allclose(terrain, 3776)


def test_decode_ele_terrarium_uint8():
    # 3776.5 + 32768 = 36544.5 = 142 * 256 + 192 + 128 / 256
    png = _rgb_tile([142, 192, 128])
    terrain = decode_ele(png, "terrarium")
    np.testing.assert_allclose(terrain, 3776.5)


def test_decode_ele_invalid_encoding():
    with pytest.raises(ValueError, match="encoding must be one of"):
        decode_ele(_rgb_tile([0, 0, 0]), "unknown")


def test_rescale_positions():
    vertices = np.array([[0, 0, 5], [512, 512, 10], [256, 128, 7]], dtype=np.float32)
    out = rescale_positions(vertices, (-10, 20, 0, 40))
    expected = np.array([[-10, 20, 5], [0, 40, 10], [-5, 25, 7]])
    np.testing.assert_allclose(out, expected)


def test_rescale_positions_flip_y():
    vertices = np.array([[0, 0, 5], [512, 512, 10], [256, 128, 7]], dtype=np.float32)
    out = rescale_positions(vertices, (-10, 20, 0, 40), flip_y=True)
    expected = np.array([[-10, 40, 5], [0, 20, 10], [-5, 35, 7]])
    np.testing.assert_allclose(out, expected)


def test_latitude_adjustment():
    assert latitude_adjustment(0) == 1
    assert latitude_adjustment(60) == pytest.approx(0.5)
