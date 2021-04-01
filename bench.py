from time import time

from imageio import imread

from pydelatin import Delatin
from pydelatin.util import decode_ele

path = './test/data/fuji.png'
fuji = imread(path)
terrain = decode_ele(fuji, 'mapbox')

start = time()
tin = Delatin(terrain, max_error=30)
vertices, triangles = tin.vertices, tin.triangles
end = time()

print(f'mesh (max_error=30m): {(end - start) * 1000:.3f}ms')
print(f'vertices: {vertices.shape[0]}, triangles: {triangles.shape[0]}\n')

for i in range(1, 21):
    start = time()
    Delatin(terrain, max_error=i)
    end = time()
    print(f'mesh (max_error={i}m): {(end - start) * 1000:.3f}ms')
