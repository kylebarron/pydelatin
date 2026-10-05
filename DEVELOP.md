## Install

Building the C++ extension requires the [`glm`](https://github.com/g-truc/glm) headers.

On macOS:

```
brew install glm
export CPLUS_INCLUDE_PATH=$(brew --prefix glm)/include:$CPLUS_INCLUDE_PATH
```

On Debian/Ubuntu:

```
sudo apt-get install libglm-dev
```

Then install the package and development dependencies:

```
uv sync
```

After changing any C++ source under `src/`, rebuild with:

```
uv sync --reinstall-package pydelatin
```

## Benchmark

```
uv run python bench.py
```
