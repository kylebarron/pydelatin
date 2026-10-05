"""Terrain mesh generation from a heightmap."""

from __future__ import annotations

import numpy as np
from _pydelatin import PydelatinTriangulator


class Delatin:
    """Triangulated irregular network (TIN) generated from a heightmap."""

    def __init__(  # noqa: PLR0913
        self,
        arr: np.ndarray,
        *,
        height: int | None = None,
        width: int | None = None,
        z_scale: float = 1,
        z_exag: float = 1,
        max_error: float = 0.001,
        max_triangles: int | None = None,
        max_points: int | None = None,
        base_height: float = 0,
        level: bool = False,
        invert: bool = False,
        blur: int = 0,
        gamma: float = 0,
        border_size: int = 0,
        border_height: float = 1,
    ) -> None:
        """Generate a mesh from a heightmap.

        Args:
            arr: Data array. If a 2D array, dimensions are expected to be
                (height, width). If a 1D array, height and width parameters
                must be passed, and the array is assumed to be in C order.

        Keyword Args:
            height: Height of array; required when arr is not 2D.
            width: Width of array; required when arr is not 2D.
            z_scale: Z scale relative to x & y.
            z_exag: Z exaggeration.
            max_error: Maximum triangulation error.
            max_triangles: Maximum number of triangles.
            max_points: Maximum number of vertices.
            base_height: Solid base height.
            level: Auto level input to full grayscale range.
            invert: Invert heightmap.
            blur: Gaussian blur sigma.
            gamma: Gamma curve exponent.
            border_size: Border size in pixels.
            border_height: Border z height.

        """
        max_triangles = max_triangles if max_triangles is not None else 0
        max_points = max_points if max_points is not None else 0

        if arr.ndim != 2:  # noqa: PLR2004
            if height is None or width is None:
                msg = "Height and width must be passed when arr is not 2D"
                raise ValueError(msg)
        else:
            height, width = arr.shape

        self.tri = PydelatinTriangulator(
            width,
            height,
            max_error,
            z_scale,
            z_exag,
            max_triangles,
            max_points,
            level,
            invert,
            blur,
            gamma,
            border_size,
            border_height,
            base_height,
        )
        self.tri.setData(arr.flatten())
        self.tri.run()

    @property
    def vertices(self) -> np.ndarray:
        """Mesh vertices, as an array of shape (-1, 3) of x, y, z positions."""
        return self.tri.getPoints().reshape(-1, 3)

    @property
    def triangles(self) -> np.ndarray:
        """Mesh triangles, as an array of shape (-1, 3) of vertex indices."""
        return self.tri.getTriangles().reshape(-1, 3).astype(np.uint32)

    @property
    def error(self) -> float:
        """Maximum error of the generated mesh."""
        return self.tri.getError()
