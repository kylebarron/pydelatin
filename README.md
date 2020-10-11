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
- `error` (`float`): the maximum error of the mesh.

#### `util.rescale_positions`

A helper function to rescale the `vertices` output to a new bounding box.
Returns an `ndarray` of shape `(-1, 3)` with positions rescaled. Each row
represents a single 3D point.

##### Arguments

- `vertices`: (`np.ndarray`) vertices output from Delatin
- `bounds`: (`Tuple[float]`) linearly rescale position values to this extent.
  Expected to be `[minx, miny, maxx, maxy]`.
- `flip_y`: (`bool`, default `False`) Flip y coordinates. Can be useful since
  images' coordinate origin is in the top left.

### Saving to mesh formats

#### Quantized Mesh

A common mesh format for the web is the [Quantized Mesh][quantized-mesh-spec]
format, which is supported in Cesium and deck.gl (via
[loaders.gl][loaders.gl-quantized-mesh]). You can use
[`quantized-mesh-encoder`][quantized-mesh-encoder] to save in this format:

```py
import quantized_mesh_encoder
from pydelatin import Delatin
from pydelatin.util import rescale_positions

tin = Delatin(terrain, max_error=30)
vertices, triangles = tin.vertices, tin.triangles

# Rescale vertices linearly from pixel units to world coordinates
rescaled_vertices = rescale_positions(vertices, bounds)

with open('output.terrain', 'wb') as f:
    quantized_mesh_encoder.encode(f, rescaled_vertices, triangles)
```

[quantized-mesh-spec]: https://github.com/CesiumGS/quantized-mesh
[quantized-mesh-encoder]: https://github.com/kylebarron/quantized-mesh-encoder
[loaders.gl-quantized-mesh]: https://loaders.gl/modules/terrain/docs/api-reference/quantized-mesh-loader

#### Meshio

Alternatively, you can save to a variety of mesh formats using
[`meshio`][meshio]:

```py
from pydelatin import Delatin
import meshio

tin = Delatin(terrain, max_error=30)
vertices, triangles = tin.vertices, tin.triangles

cells = [("triangle", triangles)]
mesh = meshio.Mesh(vertices, cells)
# Example output format
# Refer to meshio documentation
mesh.write('foo.vtk')
```

[meshio]: https://github.com/nschloe/meshio

## `Martini` or `Delatin`?

Two popular algorithms for terrain mesh generation are the **"Martini"**
algorithm, found in the JavaScript [`martini`][martini] library and the Python
[`pymartini`][pymartini] library, and the **"Delatin"** algorithm, found in the
C++ [`hmm`][hmm] library, this Python `pydelatin` library, and the JavaScript
[`delatin`][delatin] library.

Which to use?

For most purposes, use `pydelatin` over `pymartini`. A good breakdown from [a
Martini issue][martini_desc_issue]:

> Martini:
>
> - Only works on square 2^n+1 x 2^n+1 grids.
> - Generates a hierarchy of meshes (pick arbitrary detail after a single run)
> - Optimized for meshing speed rather than quality.
>
> Delatin:
>
> - Works on arbitrary raster grids.
> - Generates a single mesh for a particular detail.
> - Optimized for quality (as few triangles as possible for a given error).

[martini]: https://github.com/mapbox/martini
[pymartini]: https://github.com/kylebarron/pymartini
[martini_desc_issue]: https://github.com/mapbox/martini/issues/15#issuecomment-700475731

## Benchmark

The following uses the same dataset as the [`pymartini`
benchmarks][pymartini_bench], a 512x512 pixel heightmap of Mt. Fuji.

[pymartini_bench]: https://github.com/kylebarron/pymartini#benchmark

For the 30-meter mesh, `pydelatin` is 25% slower than `pymartini`, but the mesh
is much more efficient: it has 40% fewer vertices and triangles.

`pydelatin` is 4-5x faster than the JavaScript `delatin` package.

### Python

```bash
git clone https://github.com/kylebarron/pydelatin
cd pydelatin
pip install '.[test]'
python bench.py
```

```
mesh (max_error=30m): 27.322ms
vertices: 5668, triangles: 11140

mesh (max_error=1m): 282.946ms
mesh (max_error=2m): 215.839ms
mesh (max_error=3m): 163.424ms
mesh (max_error=4m): 127.203ms
mesh (max_error=5m): 106.596ms
mesh (max_error=6m): 91.868ms
mesh (max_error=7m): 82.572ms
mesh (max_error=8m): 74.335ms
mesh (max_error=9m): 65.893ms
mesh (max_error=10m): 60.999ms
mesh (max_error=11m): 55.213ms
mesh (max_error=12m): 54.475ms
mesh (max_error=13m): 48.662ms
mesh (max_error=14m): 47.029ms
mesh (max_error=15m): 44.517ms
mesh (max_error=16m): 42.059ms
mesh (max_error=17m): 39.699ms
mesh (max_error=18m): 37.657ms
mesh (max_error=19m): 36.333ms
mesh (max_error=20m): 34.131ms
```

### JS (Node)

This benchmarks against the [`delatin`][delatin] JavaScript module.

```bash
git clone https://github.com/kylebarron/pydelatin
cd test/bench_js/
yarn
wget https://raw.githubusercontent.com/mapbox/delatin/master/index.js
node -r esm bench.js
```

```
mesh (max_error=30m): 143.038ms
vertices: 5668
triangles: 11140

mesh (max_error=0m): 1169.226ms
mesh (max_error=1m): 917.290ms
mesh (max_error=2m): 629.776ms
mesh (max_error=3m): 476.958ms
mesh (max_error=4m): 352.907ms
mesh (max_error=5m): 290.946ms
mesh (max_error=6m): 240.556ms
mesh (max_error=7m): 234.181ms
mesh (max_error=8m): 188.273ms
mesh (max_error=9m): 162.743ms
mesh (max_error=10m): 145.734ms
mesh (max_error=11m): 130.119ms
mesh (max_error=12m): 119.865ms
mesh (max_error=13m): 114.645ms
mesh (max_error=14m): 101.390ms
mesh (max_error=15m): 100.065ms
mesh (max_error=16m): 96.247ms
mesh (max_error=17m): 89.508ms
mesh (max_error=18m): 85.754ms
mesh (max_error=19m): 79.838ms
mesh (max_error=20m): 75.607ms
```

## License

This package wraps \@fogleman's [`hmm`][hmm], a C++ library that is also
MIT-licensed.
