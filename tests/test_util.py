import numpy as np
import pytest

from pydelatin.util import decode_ele


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
