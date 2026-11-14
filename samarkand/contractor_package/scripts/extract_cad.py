import bpy, bmesh, json, collections
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
TER = -0.45
SKIPC = {'People', 'Context'}
SOFT = ('foliage', 'leaf', 'Banana', 'shrub', 'flowers', 'Jasmine', 'Bougain', 'Herbs', 'canopy', 'Areca', 'frond', 'Topiary', 'Olive_foliage', 'Ficus', 'Palm_', 'Sansevieria', 'Chinar_crown', 'Model_palm')
def skip(o):
    c = o.users_collection[0].name if o.users_collection else ''
    return o.type != 'MESH' or c in SKIPC or o.name.endswith(('_real', 'realc')) or '_real.' in o.name or any(s in o.name for s in SOFT) or o.hide_render
objs = [o for o in bpy.data.objects if not skip(o)]
def bb(o):
    P = [o.matrix_world @ Vector(c) for c in o.bound_box]; return [min(p[i] for p in P) for i in range(3)], [max(p[i] for p in P) for i in range(3)]
def cut(o, co, no):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no)
    segs = [[list(e.verts[0].co), list(e.verts[1].co)] for e in r['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
    bm.free(); return segs
out = {'plan': {}, 'sec': {}, 'inv': [], 'area': {}}
HS = [0.10, 0.40, 0.55, 0.73, 0.88, 1.20, 1.65, 2.60]
for o in objs:
    lo, hi = bb(o); c = o.users_collection[0].name if o.users_collection else ''
    out['inv'].append([o.name, c, [round(v, 3) for v in lo], [round(v, 3) for v in hi], len(o.data.polygons)])
    if c in ('Roof_skin', 'Carpet_ceiling', 'Floors') or len(o.data.polygons) > 400000: continue
    for h in HS:
        z = TER + h
        if lo[2] < z < hi[2]:
            s = cut(o, (0, 0, z), (0, 0, 1))
            if s: out['plan'].setdefault(str(h), []).append([o.name, c, [[round(a[0], 4), round(a[1], 4), round(b[0], 4), round(b[1], 4)] for a, b in s]])
SEC = {'A': ('x', 6.0), 'B': ('y', 19.9), 'C': ('y', 29.7), 'aivan': ('x', 1.0), 'bar': ('y', 11.6), 'booth': ('y', 25.2), 'portal': ('y', 16.8), 'portalx': ('x', 11.35), 'north': ('y', 33.0), 'photo': ('x', 6.86)}
for k, (ax, v) in SEC.items():
    i = 'xyz'.index(ax); co = [0, 0, 0]; co[i] = v; no = [0, 0, 0]; no[i] = 1
    for o in objs:
        lo, hi = bb(o); c = o.users_collection[0].name if o.users_collection else ''
        if not (lo[i] < v < hi[i]): continue
        s = cut(o, co, no)
        if s:
            u, w = [j for j in range(3) if j != i]
            out['sec'].setdefault(k, []).append([o.name, c, [[round(a[u], 4), round(a[w], 4), round(b[u], 4), round(b[w], 4)] for a, b in s]])
# surface areas by collection / material / orientation (up, down, vertical), all objects incl. laid tiles
A = collections.defaultdict(float)
for o in bpy.data.objects:
    if o.type != 'MESH' or o.hide_render: continue
    c = o.users_collection[0].name if o.users_collection else ''
    if c in SKIPC: continue
    mw = o.matrix_world; rot = mw.to_3x3(); mats = [m.name if m else '-' for m in o.data.materials] or ['-']
    base = o.name.split('.')[0]
    for p in o.data.polygons:
        n = (rot @ p.normal).normalized(); ori = 'up' if n.z > 0.7 else ('down' if n.z < -0.7 else 'side')
        sc = mw.to_scale(); ar = p.area * (abs(sc.x * sc.y * sc.z) ** (2 / 3))
        A[(c, base, mats[min(p.material_index, len(mats) - 1)], ori)] += ar
out['area'] = [[k[0], k[1], k[2], k[3], round(v, 4)] for k, v in A.items() if v > 0.002]
json.dump(out, open('cad/cad_data.json', 'w'))
print('objs', len(objs), 'plan', {k: len(v) for k, v in out['plan'].items()}, 'sec', {k: len(v) for k, v in out['sec'].items()}, 'area rows', len(out['area']))
