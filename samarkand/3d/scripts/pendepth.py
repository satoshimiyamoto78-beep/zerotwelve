"""penetration depth between flagged pairs: vertices of A strictly inside closed B (ray parity), with their distance to B's surface.
Usage: bvenv/bin/python r3d/pendepth.py BLEND QA.json [max_pairs]"""
import sys, json, bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B_, Q = sys.argv[1], sys.argv[2]; NMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 400
bpy.ops.wm.open_mainfile(filepath=B_)
pairs = json.load(open(Q))['penetrations']
cache = {}
def tree(o):
    if o.name not in cache:
        mw = o.matrix_world; vs = [mw @ v.co for v in o.data.vertices]
        cache[o.name] = (BVHTree.FromPolygons(vs, [list(p.vertices) for p in o.data.polygons]), vs)
    return cache[o.name]
def inside(bt, p):
    n = 0; o = p.copy(); d = Vector((0.3141, 0.2718, 0.9)).normalized()
    for _ in range(50):
        h = bt.ray_cast(o, d)
        if h[0] is None: break
        n += 1; o = h[0] + d * 1e-5
    return n % 2 == 1
out = {}
for a, b in pairs[:NMAX]:
    oa, ob = bpy.data.objects[a], bpy.data.objects[b]
    best = 0.0
    for x, y in ((oa, ob), (ob, oa)):
        bt, _ = tree(y); _, vs = tree(x)
        for p in vs:
            if inside(bt, p):
                d = (bt.find_nearest(p)[0] - p).length
                best = max(best, d)
    k = tuple(sorted((a.split('.')[0], b.split('.')[0])))
    out.setdefault(k, []).append(round(best * 1000, 1))
for k, v in sorted(out.items(), key=lambda t: -max(t[1])): print(k, 'max mm', max(v), 'n', len(v))
