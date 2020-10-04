import numpy as np


# This is copied from pymartini
def decode_ele(png, encoding):
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
