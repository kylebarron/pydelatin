# pydelatin

A Python wrapper of [`hmm`][hmm] (of which [Delatin][delatin] is a port) for fast terrain mesh generation.

[hmm]: https://github.com/fogleman/hmm
[delatin]: https://github.com/mapbox/delatin

## Install

```
pip install pydelatin
```

Binary wheels are provided for macOS and Linux. On Windows, [`glm`][glm] is a
prerequisite for building from source.

[glm]: https://glm.g-truc.net/

## Using

### Example

```py
from pydelatin import Delatin

tin = Delatin(terrain, width, height)
# Mesh vertices
tin.vertices
# Mesh triangles
tin.triangles
```

### API

The API is similar to that of [`hmm`][hmm].

Additionally I include a helper function: `decode_ele`, to decode a Mapbox
Terrain RGB or Terrarium PNG array to elevations.

#### `Delatin`

##### Arguments

- `arr` (numpy `ndarray`): data array. If a 2D array, dimensions are expected to be (height, width). If a 1D array, height and width parameters must be passed, and the array is assumed to be in C order.
- `height` (`int`, default: `None`): height of array; required when arr is not 2D
- `width` (`int`, default: `None`): width of array; required when arr is not 2D
- `z_scale` (`float`, default: `1`): z scale relative to x & y
- `z_exag` (`float`, default: `1`): z exaggeration
- `max_error` (`float`, default: `0.001`): maximum triangulation error
- `max_triangles` (`int`, default: `None`): maximum number of triangles
- `max_points` (`int`, default: `None`): maximum number of vertices
- `base_height` (`float`, default: `0`): solid base height
- `level` (`bool`, default: `False`): auto level input to full grayscale range
- `invert` (`bool`, default: `False`): invert heightmap
- `blur` (`int`, default: `0`): gaussian blur sigma
- `gamma` (`float`, default: `0`): gamma curve exponent
- `border_size` (`int`, default: `0`): border size in pixels
- `border_height` (`float`, default: `1`): border z height

##### Attributes

- `vertices` (`ndarray` of shape `(-1, 3)`): the interleaved 3D coordinates of each vertex, e.g. `[[x0, y0, z0], [x1, y1, z1], ...]`.
- `triangles` (`ndarray` of shape `(-1, 3)`): represents _indices_ within the `vertices` array. So `[0, 1, 3, ...]` would use the first, second, and fourth vertices within the `vertices` array as a single triangle.
