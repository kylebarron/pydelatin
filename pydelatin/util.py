"""Helpers for decoding elevation tiles and rescaling Delatin output."""

from __future__ import annotations

import math

import numpy as np

# Arrays with at most this many entries in the first axis are assumed to be
# band-first and are transposed to band-last
_MAX_BANDS = 4


# This is copied from pymartini
def decode_ele(png: np.ndarray, encoding: str) -> np.ndarray:
    """Decode an RGB-encoded elevation array to elevations.

    Args:
        png: Array of elevations encoded in three channels, representing red,
            green, and blue. Must be of shape (tile_size, tile_size, >=3),
            where `tile_size` is usually 256 or 512.
        encoding: Either `"mapbox"` or `"terrarium"`, the two main RGB
            encodings for elevation values.

    Returns:
        Array of shape (tile_size, tile_size) with decoded elevation values.

    """
    allowed_encodings = ["mapbox", "terrarium"]
    if encoding not in allowed_encodings:
        raise ValueError(f"encoding must be one of {allowed_encodings}")

    if png.shape[0] <= _MAX_BANDS:
        png = png.T

    # Promote to float so integer (e.g. uint8) inputs don't overflow, since
    # numpy 2 keeps the array's dtype when multiplying by a Python int
    png = png.astype(np.float64)

    # Get bands
    if encoding == "mapbox":
        red = png[:, :, 0] * (256 * 256)
        green = png[:, :, 1] * (256)
        blue = png[:, :, 2]

        # Compute float height
        terrain = (red + green + blue) / 10 - 10000
    elif encoding == "terrarium":
        red = png[:, :, 0] * (256)
        green = png[:, :, 1]
        blue = png[:, :, 2] / 256

        # Compute float height
        terrain = (red + green + blue) - 32768

    return terrain


def rescale_positions(
    vertices: np.ndarray,
    bounds: tuple[float, float, float, float],
    flip_y: bool = False,  # noqa: FBT001, FBT002 (positional for backwards compatibility)
) -> np.ndarray:
    """Rescale positions to bounding box.

    Args:
        vertices: Vertices output from Delatin.
        bounds: Linearly rescale position values to this extent, expected to
            be `[minx, miny, maxx, maxy]`.
        flip_y: Flip y coordinates. Can be useful since images' coordinate
            origin is in the top left.

    Returns:
        Array of shape (-1, 3) with positions rescaled. Each row represents a
        single 3D point.

    """
    out = np.zeros(vertices.shape, dtype=np.float32)

    tile_size = vertices[:, :2].max()
    minx, miny, maxx, maxy = bounds
    x_scale = (maxx - minx) / tile_size
    y_scale = (maxy - miny) / tile_size

    if flip_y:
        scalar = np.array([x_scale, -y_scale])
        offset = np.array([minx, maxy])
    else:
        scalar = np.array([x_scale, y_scale])
        offset = np.array([minx, miny])

    # Rescale x, y positions
    out[:, :2] = vertices[:, :2] * scalar + offset
    out[:, 2] = vertices[:, 2]
    return out


def latitude_adjustment(lat: float) -> float:
    """Latitude adjustment for web-mercator projection.

    Args:
        lat: Latitude in degrees.

    Returns:
        Scale factor to apply at this latitude.

    """
    return math.cos(math.radians(lat))
