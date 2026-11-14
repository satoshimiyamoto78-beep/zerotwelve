"""Vector hidden-line engine driven by cd/spec.json (same cameras as the raster set).
out: hlr/out/<name>.json {cam,right,up,scale,W,H, vis:[[h0,v0,h1,v1],...], cut:[[obj,[segs]],...]}  (view metres from camera centre)
usage: bvenv/bin/python hlr/hlr2.py -- spec.json name [name ...]"""
import bpy, bmesh, json, sys, math, time, os
from mathutils import Vector, Euler
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
args = sys.argv[sys.argv.index('--') + 1:]; SPEC = json.load(open(args[0])); want = args[1:]
SKIPC = {'People', 'Context', 'Cameras'}
SOFT = ('foliage', 'leaf', 'Banana', 'shrub', 'flowers', 'Jasmine', 'Bougain', 'Herbs', 'canopy', 'Areca', 'frond', 'Topiary', 'Olive_foliage', 'Ficus', 'Palm_', 'Sansevieria', 'Chinar_crown', 'Model_palm', 'Olive_tree', 'Chinar')
def coll(o): return o.users_collection[0].name if o.users_collection else ''
OBJ = [o for o in bpy.data.objects if o.type == 'MESH' and coll(o) not in SKIPC and not o.hide_render and not any(s in o.name for s in SOFT)]
t0 = time.time(); V = []; P = []; PO = []; META = []
for oi, o in enumerate(OBJ):
    mw = o.matrix_world; me = o.data; base = len(V)
    V.extend([mw @ v.co for v in me.vertices]); P.extend([[base + i for i in p.vertices] for p in me.polygons]); PO.extend([oi] * len(me.polygons))
    cs = [mw @ Vector(c) for c in o.bound_box]
    META.append((Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs))), Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))))
BVH = BVHTree.FromPolygons(V, P, all_triangles=False, epsilon=0.0)
print('bvh', len(V), len(P), round(time.time() - t0, 1), flush=True)
def run(name):
    S = SPEC[name]; t0 = time.time()
    C = Vector(S['cam'])
    if 'rot' in S: q = Euler([math.radians(v) for v in S['rot']]).to_quaternion()
    else: q = (Vector(S['tgt']) - C).to_track_quat('-Z', 'Y')
    R = q @ Vector((1, 0, 0)); U = q @ Vector((0, 1, 0)); d = q @ Vector((0, 0, -1))
    s = S['scale']; Hm = s * S['H'] / S['W']; hw = s / 2 + 0.3; hh = Hm / 2 + 0.3
    cd0 = C.dot(d); cut = None
    if S.get('cut'):
        ax = 'xyz'.index(S['cut'][0]); val = float(S['cut'][1]); n = Vector((0, 0, 0)); n[ax] = 1.0
        cut = val * d[ax]                                  # plane p·d = cut (d is axis aligned for all cut views)
        assert abs(abs(d[ax]) - 1) < 1e-3 and ((S['cut'][2] == '-') == (d[ax] < 0)), name
    near = cut if cut is not None else cd0
    dmax = S.get('depth', 400.0)
    HC = set(S.get('hide_coll', [])); HP = tuple(S.get('hide_prefix', [])); HS = tuple(S.get('hide_suffix', [])); ONLY = S.get('only')
    hid = set()
    for oi, o in enumerate(OBJ):
        if coll(o) in HC or (HP and o.name.startswith(HP)) or (HS and (o.name.endswith(HS) or o.data.name.endswith(HS))) or (ONLY and o.name not in ONLY): hid.add(oi)
    bvh = BVH; po = PO
    if ONLY:
        V2 = []; P2 = []
        for oi, o in enumerate(OBJ):
            if oi in hid: continue
            b = len(V2); V2.extend([o.matrix_world @ v.co for v in o.data.vertices]); P2.extend([[b + i for i in p.vertices] for p in o.data.polygons])
        bvh = BVHTree.FromPolygons(V2, P2, all_triangles=False, epsilon=0.0); po = None
    step = max(0.004, min(0.05, s / 700.0)); ang = math.cos(math.radians(S.get('angle', 28)))
    def visible(p):
        dist = p.dot(d) - near - 0.004
        if dist <= 0: return True
        o_ = p - d * 0.003
        for _ in range(12):
            loc, _n, idx, dd = bvh.ray_cast(o_, -d, dist)
            if loc is None: return True
            if po is None or po[idx] not in hid: return False
            dist -= dd + 0.002; o_ = loc - d * 0.002
            if dist <= 0: return True
        return False
    vis = []; cuts = []
    for oi, o in enumerate(OBJ):
        if oi in hid: continue
        blo, bhi = META[oi]
        cs = [Vector((x, y, z)) for x in (blo.x, bhi.x) for y in (blo.y, bhi.y) for z in (blo.z, bhi.z)]
        ds = [c.dot(d) for c in cs]; hs = [(c - C).dot(R) for c in cs]; vs = [(c - C).dot(U) for c in cs]
        if max(ds) < near or min(ds) > near + dmax or max(hs) < -hw or min(hs) > hw or max(vs) < -hh or min(vs) > hh: continue
        bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.normal_update()
        if cut is not None and min(ds) < cut < max(ds):
            b2 = bm.copy(); r = bmesh.ops.bisect_plane(b2, geom=b2.verts[:] + b2.edges[:] + b2.faces[:], plane_co=d * cut, plane_no=d)
            cs_ = [[round((e.verts[0].co - C).dot(R), 4), round((e.verts[0].co - C).dot(U), 4), round((e.verts[1].co - C).dot(R), 4), round((e.verts[1].co - C).dot(U), 4)] for e in r['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
            b2.free()
            if cs_: cuts.append([o.name, cs_])
        for e in bm.edges:
            fs = e.link_faces
            if len(fs) == 0: continue
            if len(fs) >= 2:
                f0 = fs[0].normal.dot(d) < 1e-6; f1 = fs[1].normal.dot(d) < 1e-6
                if not f0 and not f1: continue
                if f0 == f1 and fs[0].normal.dot(fs[1].normal) >= ang: continue
            a, b = e.verts[0].co, e.verts[1].co; da, db = a.dot(d), b.dot(d)
            if max(da, db) <= near + 1e-4 or min(da, db) > near + dmax: continue
            if da < near: a = a + (b - a) * ((near - da) / (db - da))
            elif db < near: b = b + (a - b) * ((near - db) / (da - db))
            ha, va, hb, vb = (a - C).dot(R), (a - C).dot(U), (b - C).dot(R), (b - C).dot(U)
            if max(ha, hb) < -hw or min(ha, hb) > hw or max(va, vb) < -hh or min(va, vb) > hh: continue
            L = (b - a).length
            if L < 1e-4: continue
            if math.hypot(hb - ha, vb - va) < 1e-4: continue          # edge seen end-on
            n = max(1, min(240, int(L / step) + 1)); k = 0; ok = []
            for k in range(n):
                t = (k + 0.5) / n; h_ = ha + (hb - ha) * t; v_ = va + (vb - va) * t
                ok.append(abs(h_) <= hw and abs(v_) <= hh and visible(a + (b - a) * t))
            k = 0
            while k < n:
                if ok[k]:
                    j = k
                    while j + 1 < n and ok[j + 1]: j += 1
                    t0_, t1_ = k / n, (j + 1) / n
                    vis.append([round(ha + (hb - ha) * t0_, 4), round(va + (vb - va) * t0_, 4), round(ha + (hb - ha) * t1_, 4), round(va + (vb - va) * t1_, 4), round(min(da, db) - cd0, 2)]); k = j + 1
                else: k += 1
        bm.free()
    json.dump({'cam': list(C), 'right': list(R), 'up': list(U), 'scale': s, 'W': S['W'], 'H': S['H'], 'vis': vis, 'cut': cuts}, open(f'hlr/out/{name}.json', 'w'))
    print('ok', name, len(vis), sum(len(c[1]) for c in cuts), round(time.time() - t0, 1), flush=True)
os.makedirs('hlr/out', exist_ok=True)
for nm in want:
    try: run(nm)
    except Exception as e:
        import traceback; traceback.print_exc(); print('FAIL', nm, e, flush=True)
