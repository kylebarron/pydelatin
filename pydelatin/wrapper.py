from typing import Optional

import numpy as np

from _pydelatin import PydelatinTriangulator


class Delatin:
    def __init__(
            self,
            arr: np.ndarray,
            *,
            height: Optional[int] = None,
            width: Optional[int] = None,
            z_scale: float = 1,
            z_exag: float = 1,
            max_error: float = 0.001,
            max_triangles: Optional[int] = None,
            max_points: Optional[int] = None,
            base_height: float = 0,
            level: bool = False,
            invert: bool = False,
            blur: int = 0,
            gamma: float = 0,
            border_size: int = 0,
            border_height: float = 1):
        """

        Args:
            - arr: data array. If a 2D array, dimensions are expected to be
              (height, width). If a 1D array, height and width parameters must
              be passed, and the array is assumed to be in C order.
            - height: height of array; required when arr is not 2D
            - width: width of array; required when arr is not 2D
            - z_scale: z scale relative to x & y
            - z_exag: z exaggeration
            - max_error: maximum triangulation error
            - max_triangles: maximum number of triangles
            - max_points: maximum number of vertices
            - base_height: solid base height
            - level: auto level input to full grayscale range
            - invert: invert heightmap
            - blur: gaussian blur sigma
            - gamma: gamma curve exponent
            - border_size: border size in pixels
            - border_height: border z height
        """
        super(Delatin, self).__init__()

        max_triangles = max_triangles if max_triangles is not None else 0
        max_points = max_points if max_points is not None else 0

        if len(arr.shape) != 2:
            if height is None or width is None:
                msg = 'Height and width must be passed when arr is not 2D'
                raise ValueError(msg)
        else:
            height, width = arr.shape

        self.tri = PydelatinTriangulator(
            width, height, max_error, z_scale, z_exag, max_triangles,
            max_points, level, invert, blur, gamma, border_size, border_height,
            base_height)
        self.tri.setData(arr.flatten())
        self.tri.run()

    @property
    def vertices(self):
        return self.tri.getPoints().reshape(-1, 3)

    @property
    def triangles(self):
        return self.tri.getTriangles().reshape(-1, 3).astype(np.uint32)

    @property
    def error(self):
        return self.tri.getError()
