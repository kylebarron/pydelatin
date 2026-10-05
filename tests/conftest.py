from pathlib import Path

import imageio.v3 as iio
import numpy as np
import pytest

from pydelatin.util import decode_ele

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def fuji() -> np.ndarray:
    """512x512 Mapbox Terrain-RGB heightmap of Mt. Fuji, in meters."""
    png = iio.imread(DATA_DIR / "fuji.png")
    return decode_ele(png, "mapbox")
