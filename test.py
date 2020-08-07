import pydelatin
import numpy as np
import glm

dir(pydelatin)
glm.vec2()
dir(glm)

a = np.array([1, 2], dtype=np.uint8)
b = np.array([3, 4], dtype=np.uint8)

test = pydelatin.add_arrays(a, b)
test.dtype

pydelatin.test(1, 1, np.array([0]))
out = pydelatin.test(2, 20, np.array([0]))
np.array(out)

dir(pydelatin)

path = '/Users/kyle/github/mapping/pydelatin/cpp_test/pydelatin/gale.png'
pydelatin.num_pixels(path)
pydelatin.hello_world()
%timeit pydelatin.add(2, 5)
%timeit 2 + 5

help(pydelatin)
help(pydelatin)
