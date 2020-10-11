import math
from typing import Tuple

import numpy as np


# This is copied from pymartini
def decode_ele(png: np.ndarray, encoding: str) -> np.ndarray:
    """Decode array to elevations
    Arguments:
        - png (np.ndarray). Ndarray of elevations encoded in three channels,
          representing red, green, and blue. Must be of shape (tile_size,
          tile_size, >=3), where `tile_size` is usually 256 or 512
        - encoding: (str): Either 'mapbox' or 'terrarium', the two main RGB
          encodings for elevation values.
    Returns:
        (np.array) Array of shape (tile_size^2) with decoded elevation values
    """
    allowed_encodings = ['mapbox', 'terrarium']
    if encoding not in allowed_encodings:
        raise ValueError(f'encoding must be one of {allowed_encodings}')

    if png.shape[0] <= 4:
        png = png.T

    # Get bands
    if encoding == 'mapbox':
        red = png[:, :, 0] * (256 * 256)
        green = png[:, :, 1] * (256)
        blue = png[:, :, 2]

        # Compute float height
        terrain = (red + green + blue) / 10 - 10000
    elif encoding == 'terrarium':
        red = png[:, :, 0] * (256)
        green = png[:, :, 1]
        blue = png[:, :, 2] / 256

        # Compute float height
        terrain = (red + green + blue) - 32768

    return terrain


def rescale_positions(
        vertices: np.ndarray,
        bounds: Tuple[float, float, float, float],
        flip_y: bool = False):
    """Rescale positions to bounding box

    Args:
        - vertices: vertices output from Delatin
        - bounds: linearly rescale position values to this extent, expected to
          be [minx, miny, maxx, maxy].
        - flip_y: (bool) Flip y coordinates. Can be useful since images'
          coordinate origin is in the top left.

    Returns:
        (np.ndarray): ndarray of shape (-1, 3) with positions rescaled. Each row
        represents a single 3D point.
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


def latitude_adjustment(lat: float):
    """Latitude adjustment for web-mercator projection

    Args:
        - lat: latitude in degrees
    """
    return math.cos(math.radians(lat))
