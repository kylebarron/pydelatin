from typing import Optional
import numpy as np
from _pydelatin import PydelatinTriangulator


class Pydelatin:
    def __init__(self,
                 arr: np.ndarray,
                 z_scale,
                 z_exag: float=1,
                 max_error: float=0.001,
                 max_triangles: Optional[int] = None,
                 max_points: Optional[int] = None,
                 base_height: float=0,
                 level: bool=False,
                 invert: bool=False,
                 blur: int=0,
                 gamma: float=0,
                 border_size:int=0,
                 border_height: float=1):
        """

        Args:
            - arr: data array
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
        super(Pydelatin, self).__init__()
        self.arr = arr
        self.height, self.width = arr
        self.z_scale = z_scale
        self.z_exag = z_exag
        self.max_error = max_error
        self.max_triangles = max_triangles
        self.max_points = max_points
        self.base_height = base_height
        self.level = level
        self.invert = invert
        self.blur = blur
        self.gamma = gamma
        self.border_size = border_size
        self.border_height = border_height

