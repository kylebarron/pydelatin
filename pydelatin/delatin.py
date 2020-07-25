from math import sqrt

import numpy as np


class Delatin:
    def __init__(self, data, width, height):
        # Height data
        self.data = data
        self.width = width
        self.height = height

        # vertex coordinates (x, y)
        self.coords = []
        # mesh triangle indices
        self.triangles = []

        # additional triangle data
        self._halfedges = []
        self._candidates = []
        self._queueIndices = []

        # queue of added triangles
        self._queue = []
        self._errors = []
        self._rms = []
        # triangles pending addition to queue
        self._pending = []
        self._pendingLen = 0

        self._rmsSum = 0

        x1 = width - 1
        y1 = height - 1
        p0 = self._addPoint(0, 0)
        p1 = self._addPoint(x1, 0)
        p2 = self._addPoint(0, y1)
        p3 = self._addPoint(x1, y1)

        # add initial two triangles
        t0 = self._addTriangle(p3, p0, p2, -1, -1, -1)
        self._addTriangle(p0, p3, p1, t0, -1, -1)
        self._flush()

    def run(self, maxError=1):
        """refine the mesh until its maximum error gets below the given one
        """
        while self.getMaxError() > maxError:
            self.refine()

    def refine(self):
        """refine the mesh with a single point
        """
        self._step()
        self._flush()

    def getMaxError(self):
        """max error of the current mesh
        """
        return self._errors[0]

    def getRMSD(self):
        """root-mean-square deviation of the current mesh
        """
        if self._rmsSum > 0:
            return sqrt(self._rmsSum / (self.width * self.height))

        return 0

    def heightAt(self, x, y):
        """height value at a given position
        """
        return self.data[self.width * y + x]

    def _flush(self):
        """rasterize and queue all triangles that got added or updated in _step
        """
        coords = self.coords

        for i in range(self._pendingLen):
            t = self._pending[i]

            # rasterize triangle to find maximum pixel error
            a = 2 * self.triangles[t * 3 + 0]
            b = 2 * self.triangles[t * 3 + 1]
            c = 2 * self.triangles[t * 3 + 2]

            self._findCandidate(
                coords[a], coords[a + 1], coords[b], coords[b + 1], coords[c],
                coords[c + 1], t)

        self._pendingLen = 0

    def _findCandidate(self, p0x, p0y, p1x, p1y, p2x, p2y, t):
        """rasterize a triangle, find its max error, and queue it for processing
        """
        # triangle bounding box
        minX = min(p0x, p1x, p2x)
        minY = min(p0y, p1y, p2y)
        maxX = max(p0x, p1x, p2x)
        maxY = max(p0y, p1y, p2y)

        # forward differencing variables
        let w00 = orient(p1x, p1y, p2x, p2y, minX, minY)
        let w01 = orient(p2x, p2y, p0x, p0y, minX, minY)
        let w02 = orient(p0x, p0y, p1x, p1y, minX, minY)
        a01 = p1y - p0y
        b01 = p0x - p1x
        a12 = p2y - p1y
        b12 = p1x - p2x
        a20 = p0y - p2y
        b20 = p2x - p0x

        # pre-multiplied z values at vertices
        a = orient(p0x, p0y, p1x, p1y, p2x, p2y)
        z0 = this.heightAt(p0x, p0y) / a
        z1 = this.heightAt(p1x, p1y) / a
        z2 = this.heightAt(p2x, p2y) / a

        # iterate over pixels in bounding box
        let maxError = 0
        let mx = 0
        let my = 0
        let rms = 0
        for (let y = minY; y <= maxY; y++) {
            # compute starting offset
            let dx = 0
            if (w00 < 0 && a12 !== 0) {
                dx = max(dx, Math.floor(-w00 / a12))
            }
            if (w01 < 0 && a20 !== 0) {
                dx = max(dx, Math.floor(-w01 / a20))
            }
            if (w02 < 0 && a01 !== 0) {
                dx = max(dx, Math.floor(-w02 / a01))
            }

            let w0 = w00 + a12 * dx
            let w1 = w01 + a20 * dx
            let w2 = w02 + a01 * dx

            let wasInside = false

            for (let x = minX + dx; x <= maxX; x++) {
                # check if inside triangle
                if (w0 >= 0 && w1 >= 0 && w2 >= 0) {
                    wasInside = true

                    # compute z using barycentric coordinates
                    z = z0 * w0 + z1 * w1 + z2 * w2
                    dz = Math.abs(z - this.heightAt(x, y))
                    rms += dz * dz
                    if (dz > maxError) {
                        maxError = dz
                        mx = x
                        my = y
                    }
                } else if (wasInside) {
                    break
                }

                w0 += a12
                w1 += a20
                w2 += a01
            }

            w00 += b12
            w01 += b20
            w02 += b01
        }

        if (mx === p0x && my === p0y || mx === p1x && my === p1y || mx === p2x && my === p2y) {
            maxError = 0
        }

        # update triangle metadata
        this._candidates[2 * t] = mx
        this._candidates[2 * t + 1] = my
        this._rms[t] = rms

        # add triangle to priority queue
        this._queuePush(t, maxError, rms)

    def _step(self):
        """process the next triangle in the queue, splitting it with a new point
        """
        # pop triangle with highest error from priority queue
        t = self._queuePop()

        e0 = t * 3 + 0
        e1 = t * 3 + 1
        e2 = t * 3 + 2

        p0 = self.triangles[e0]
        p1 = self.triangles[e1]
        p2 = self.triangles[e2]

        ax = self.coords[2 * p0]
        ay = self.coords[2 * p0 + 1]
        bx = self.coords[2 * p1]
        by = self.coords[2 * p1 + 1]
        cx = self.coords[2 * p2]
        cy = self.coords[2 * p2 + 1]
        px = self._candidates[2 * t]
        py = self._candidates[2 * t + 1]

        pn = self._addPoint(px, py)

        if orient(ax, ay, bx, by, px, py) == 0:
            self._handleCollinear(pn, e0)

        elif orient(bx, by, cx, cy, px, py) == 0:
            self._handleCollinear(pn, e1)

        elif orient(cx, cy, ax, ay, px, py) == 0:
            self._handleCollinear(pn, e2)

        else:
            h0 = self._halfedges[e0]
            h1 = self._halfedges[e1]
            h2 = self._halfedges[e2]

            t0 = self._addTriangle(p0, p1, pn, h0, -1, -1, e0)
            t1 = self._addTriangle(p1, p2, pn, h1, -1, t0 + 1)
            t2 = self._addTriangle(p2, p0, pn, h2, t0 + 2, t1 + 1)

            self._legalize(t0)
            self._legalize(t1)
            self._legalize(t2)

    def _addPoint(self, x, y):
        """add coordinates for a new vertex
        """
        i = len(self.coords) >> 1
        self.coords.append(x)
        self.coords.append(y)
        return i

    def _addTriangle(self, a, b, c, ab, bc, ca, e = len(self.triangles)):
        """add or update a triangle in the mesh
        """
        # new triangle index
        t = e / 3

        # add triangle vertices
        self.triangles[e + 0] = a
        self.triangles[e + 1] = b
        self.triangles[e + 2] = c

        # add triangle halfedges
        self._halfedges[e + 0] = ab
        self._halfedges[e + 1] = bc
        self._halfedges[e + 2] = ca

        # link neighboring halfedges
        if ab >= 0:
            self._halfedges[ab] = e + 0

        if bc >= 0:
            self._halfedges[bc] = e + 1

        if ca >= 0:
            self._halfedges[ca] = e + 2

        # init triangle metadata
        self._candidates[2 * t + 0] = 0
        self._candidates[2 * t + 1] = 0
        self._queueIndices[t] = -1
        self._rms[t] = 0

        # add triangle to pending queue for later rasterization
        # TODO(kyle): fix this ++
        self._pending[this._pendingLen++] = t

        # return first halfedge index
        return e

    def _legalize(self, a):
        """
        if the pair of triangles doesn't satisfy the Delaunay condition
        (p1 is inside the circumcircle of [p0, pl, pr]), flip them,
        then do the same check/flip recursively for the new pair of triangles

                  pl                    pl
                 /||\                  /  \
              al/ || \bl            al/    \a
               /  ||  \              /      \
              /  a||b  \    flip    /___ar___\
            p0\   ||   /p1   =>   p0\---bl---/p1
               \  ||  /              \      /
              ar\ || /br             b\    /br
                 \||/                  \  /
                  pr                    pr
        """
        b = self._halfedges[a]

        if b < 0:
            return

        a0 = a - a % 3
        b0 = b - b % 3
        al = a0 + (a + 1) % 3
        ar = a0 + (a + 2) % 3
        bl = b0 + (b + 2) % 3
        br = b0 + (b + 1) % 3
        p0 = self.triangles[ar]
        pr = self.triangles[a]
        pl = self.triangles[al]
        p1 = self.triangles[bl]
        coords = self.coords

        if not inCircle(
            coords[2 * p0], coords[2 * p0 + 1],
            coords[2 * pr], coords[2 * pr + 1],
            coords[2 * pl], coords[2 * pl + 1],
            coords[2 * p1], coords[2 * p1 + 1]):
            return

        hal = self._halfedges[al]
        har = self._halfedges[ar]
        hbl = self._halfedges[bl]
        hbr = self._halfedges[br]

        self._queueRemove(a0 / 3)
        self._queueRemove(b0 / 3)

        t0 = self._addTriangle(p0, p1, pl, -1, hbl, hal, a0)
        t1 = self._addTriangle(p1, p0, pr, t0, har, hbr, b0)

        self._legalize(t0 + 1)
        self._legalize(t1 + 2)

    def _handleCollinear(self, pn, a):
        """handle a case where new vertex is on the edge of a triangle
        """
        a0 = a - a % 3
        al = a0 + (a + 1) % 3
        ar = a0 + (a + 2) % 3
        p0 = self.triangles[ar]
        pr = self.triangles[a]
        pl = self.triangles[al]
        hal = self._halfedges[al]
        har = self._halfedges[ar]

        b = self._halfedges[a]

        if b < 0:
            t0 = self._addTriangle(pn, p0, pr, -1, har, -1, a0)
            t1 = self._addTriangle(p0, pn, pl, t0, -1, hal)
            self._legalize(t0 + 1)
            self._legalize(t1 + 2)
            return

        b0 = b - b % 3
        bl = b0 + (b + 2) % 3
        br = b0 + (b + 1) % 3
        p1 = self.triangles[bl]
        hbl = self._halfedges[bl]
        hbr = self._halfedges[br]

        self._queueRemove(b0 / 3)

        t0 = self._addTriangle(p0, pr, pn, har, -1, -1, a0)
        t1 = self._addTriangle(pr, p1, pn, hbr, -1, t0 + 1, b0)
        t2 = self._addTriangle(p1, pl, pn, hbl, -1, t1 + 1)
        t3 = self._addTriangle(pl, p0, pn, hal, t0 + 2, t2 + 1)

        self._legalize(t0)
        self._legalize(t1)
        self._legalize(t2)
        self._legalize(t3)

    # priority queue methods

    def _queuePush(self, t, error, rms):
        i = len(self._queue)
        self._queueIndices[t] = i
        self._queue.push(t)
        self._errors.push(error)
        self._rmsSum += rms
        self._queueUp(i)

    def _queuePop(self):
        n = len(self._queue) - 1
        self._queueSwap(0, n)
        self._queueDown(0, n)
        return self._queuePopBack()

    def _queuePopBack(self) {
        t = self._queue.pop()
        self._errors.pop()
        self._rmsSum -= self._rms[t]
        self._queueIndices[t] = -1
        return t

    def _queueRemove(self, t):
        i = self._queueIndices[t]
        if i < 0:
            it = self._pending.index(t)
            if it != -1:
                self._pending[it] = self._pending[--self._pendingLen]
            else:
                raise ValueError('Broken triangulation (something went wrong).')

            return

        n = len(self._queue) - 1
        if n != i:
            self._queueSwap(i, n)
            if not self._queueDown(i, n):
                self._queueUp(i)

        self._queuePopBack()

    def _queueLess(self, i, j):
        return self._errors[i] > self._errors[j]

    def _queueSwap(self, i, j) {
        pi = self._queue[i]
        pj = self._queue[j]
        self._queue[i] = pj
        self._queue[j] = pi
        self._queueIndices[pi] = j
        self._queueIndices[pj] = i
        e = self._errors[i]
        self._errors[i] = self._errors[j]
        self._errors[j] = e

    def _queueUp(self, j0):
        j = j0
        while True:
            i = (j - 1) >> 1
            if i == j or not self._queueLess(j, i):
                break

            self._queueSwap(i, j)
            j = i

    def _queueDown(self, i0, n):
        i = i0
        while True:
            j1 = 2 * i + 1
            if j1 >= n or j1 < 0:
                break

            j2 = j1 + 1
            j = j1

            if j2 < n and self._queueLess(j2, j1):
                j = j2

            if not self._queueLess(j, i):
                break

            self._queueSwap(i, j)
            i = j

        return i > i0


def orient(ax, ay, bx, by, cx, cy):
    return (bx - cx) * (ay - cy) - (by - cy) * (ax - cx)


def inCircle(ax, ay, bx, by, cx, cy, px, py):
    dx = ax - px
    dy = ay - py
    ex = bx - px
    ey = by - py
    fx = cx - px
    fy = cy - py

    ap = dx * dx + dy * dy
    bp = ex * ex + ey * ey
    cp = fx * fx + fy * fy

    return dx * (ey * cp - bp * fy) -
           dy * (ex * cp - bp * fx) +
           ap * (ex * fy - ey * fx) < 0
