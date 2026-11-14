"""rev. 10.9 (owner, De Bobo refs: 'clay walls with niches, carpets and textiles in timber frames, backlight, the ceiling fully closed'):
  * coffered ceiling closing the whole covered dining area, bar zone and north end, 20 mm under the roof beams, following the 3.5 %
    fall: walnut grid 70 x 140 on a ~1.2 m module; in every coffer one of the owner's Persian carpets in a timber frame, set 100 mm
    up, with a warm hidden LED strip around it (backlit carpet coffer). Openings kept: dome ring, skylight; aivan keeps its ceiling.
    Coffers / grid segments that would meet a hanging rod or lamp are left out (the lamp drops through a clean opening).
  * the four hanging 'flying carpets' and their rods are removed — the ceiling carries the carpets now
  * walls: backlit framed carpets in walnut frames on the clay boundary wall; slatted walnut screen with framed portraits
    on the north end wall (see below)"""
from shapely.geometry import Polygon as _P9, box as _b9
from shapely.ops import unary_union as _uu9
from shapely.geometry import LineString as _LS9
_rm('Flying_carpet', 'Rod_carpet')
ZC = lambda x: top(x) - 0.70                                                    # ceiling soffit (beam underside - 20)
LED = mat('led_warm', (1.0, 0.72, 0.42), emit=(1.0, 0.72, 0.42), strength=6.0)
FRM = XW['wd']
def xmax(y):                                                                    # inside the street column line
    pts = [(9.85, 12.07), (15.3, 11.53), (18.3, 11.23), (21.35, 10.93), (25.6, 10.51), (29.1, 10.17), (32.1, 9.87), (36.3, 9.46)]
    for (ya, xa), (yb, xb) in zip(pts, pts[1:]):
        if y <= yb: return xa + (xb - xa) * (y - ya) / (yb - ya) - 0.42
    return pts[-1][1] - 0.42
Y0C, Y1C = 8.7, 36.15
outline = [(0.22, Y0C)] + [(xmax(y), y) for y in [Y0C + k * (Y1C - Y0C) / 40 for k in range(41)]] + [(0.22, Y1C)]
REG = _P9(outline).difference(_uu9([_b9(0.2, 15.2, 3.34, 28.6), _b9(3.44, 17.34, 8.55, 22.45), _b9(4.4, 11.12, 7.6, 14.32),
                                   _b9(0.0, 8.0, 0.74, 14.4),                     # bar back wall rises to the ceiling: ceiling stops at its face
                                   _b9(10.3, 14.7, 13.0, 18.9),                   # street pishtaq
                                   _b9(9.2, 9.9, 13.0, 14.65)]))                  # velvet swags at the street
from shapely.geometry import Point as _Pt9
for o_ in [o for o in bpy.data.objects if o.name.startswith('Bar_drum_pendant')]:          # pendant rods drop through 120 mm openings
    lo_, hi_ = _bb(o_); REG = REG.difference(_Pt9((lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2).buffer(0.06, 12))
def sbox(b, x0, y0, x1, y1, dz0, dz1, mm):
    """box following the ceiling slope: z = ZC(x) + dz"""
    i = b.mi(mm); bm_ = b.bm
    V = [bm_.verts.new((x, y, ZC(x) + dz)) for dz in (dz0, dz1) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        f = bm_.faces.new([V[k] for k in q]); f.material_index = i
def _flat(g):
    """polygons without holes: multi -> parts; a hole is opened by splitting through its centre"""
    from shapely.ops import split as _split
    from shapely.geometry import LineString as _L
    out = []
    for p_ in (getattr(g, 'geoms', None) or [g]):
        if p_.geom_type != 'Polygon' or p_.area < 1e-5: continue
        if not p_.interiors: out.append(p_); continue
        cx = p_.interiors[0].centroid.x; x0_, y0_, x1_, y1_ = p_.bounds
        for q in _split(p_, _L([(cx, y0_ - 1), (cx, y1_ + 1)])).geoms: out += _flat(q)
    return out
def spoly(b, poly, dz0, dz1, mm):
    for q in _flat(poly): _spoly(b, q, dz0, dz1, mm)
def _spoly(b, poly, dz0, dz1, mm):
    """prism from a shapely polygon following the slope (top/bottom ngons + sides)"""
    i = b.mi(mm); bm_ = b.bm; ring = list(poly.exterior.coords)[:-1]
    lo = [bm_.verts.new((x, y, ZC(x) + dz0)) for x, y in ring]; hi = [bm_.verts.new((x, y, ZC(x) + dz1)) for x, y in ring]
    fs = [bm_.faces.new(lo[::-1]), bm_.faces.new(hi)]
    for k in range(len(ring)): fs.append(bm_.faces.new((lo[k], lo[(k + 1) % len(ring)], hi[(k + 1) % len(ring)], hi[k])))
    x0_, y0_, x1_, y1_ = poly.bounds
    for f in fs:
        f.material_index = i
        for lp in f.loops: lp[b.uv].uv = ((lp.vert.co.x - x0_) / max(1e-6, x1_ - x0_), (lp.vert.co.y - y0_) / max(1e-6, y1_ - y0_))
    return fs
M = 1.2; BW = 0.07; BD = 0.14
xs = [0.22 + k * M for k in range(10)]; ys = [Y0C + k * (Y1C - Y0C) / round((Y1C - Y0C) / M) for k in range(round((Y1C - Y0C) / M) + 1)]
grid = MB(); parts9 = []                                                        # (MB, name) per piece for culling
nco = 0
pieces9 = []
def piece(name, fn):
    b = MB(); fn(b); pieces9.append((name, b))
for ya, yb in zip(ys, ys[1:]):
    for xa, xb in zip(xs, xs[1:] + [xs[-1] + M]):
        cell = _b9(xa + BW / 2, ya + BW / 2, xb - BW / 2, yb - BW / 2).intersection(REG.buffer(-0.072, join_style=2))
        if cell.is_empty or cell.area < 0.25: continue
        for g in (getattr(cell, 'geoms', None) or [cell]):
            if g.geom_type != 'Polygon' or g.area < 0.25: continue
            k = (int(xa / M) * 7 + int(ya / M) * 3) % 19 + 1; nco += 1
            kind = (int(xa / M) * 5 + int(ya / M) * 3 + int(ya / M) // 2) % 5    # rev 11.6: mixed coffers (owner refs) — carpet / slats / ribbed / dropped
            def mk(b, g=g, k=k, kind=kind):
                ring = g.buffer(-0.003, join_style=2).difference(g.buffer(-0.045, join_style=2))
                if kind == 1:                                                                          # timber slat box dropped 150, lit from above
                    spoly(b, ring, -0.15, 0.10, FRM)
                    spoly(b, g.buffer(-0.045, join_style=2), 0.112, 0.122, CHAR if 'CHAR' in globals() else FRM)
                    spoly(b, g.buffer(-0.05, join_style=2).difference(g.buffer(-0.09, join_style=2)), 0.10, 0.112, LED)
                    x0_, y0_, x1_, y1_ = g.bounds; inner = g.buffer(-0.046, join_style=2)
                    along = (x1_ - x0_) < (y1_ - y0_)
                    n_ = int(((x1_ - x0_) if along else (y1_ - y0_)) / 0.075)
                    for s_ in range(n_):
                        c_ = (x0_ if along else y0_) + 0.0375 + s_ * 0.075
                        sl = (_b9(c_ - 0.016, y0_, c_ + 0.016, y1_) if along else _b9(x0_, c_ - 0.016, x1_, c_ + 0.016)).intersection(inner)
                        if not sl.is_empty: spoly(b, sl, -0.13, -0.02, FRM)
                    return
                spoly(b, g.buffer(-0.06, join_style=2), 0.10, 0.112, rugmat(k, False))                     # carpet panel up in the coffer
                spoly(b, g.buffer(-0.03, join_style=2).difference(g.buffer(-0.07, join_style=2)), 0.112, 0.124, LED)   # LED strip behind
                spoly(b, ring, -0.10 if kind == 3 else 0.0, 0.10, FRM)                                   # timber frame lining the coffer (deeper on 3)
                if kind in (2, 3):                                                                      # diagonal walnut ribs under the carpet
                    x0_, y0_, x1_, y1_ = g.buffer(-0.045, join_style=2).bounds
                    for p0_, p1_ in (((x0_, y0_), (x1_, y1_)), ((x0_, y1_), (x1_, y0_))):
                        rib = _LS9([p0_, p1_]).buffer(0.022, cap_style=2).intersection(g.buffer(-0.046, join_style=2))
                        if not rib.is_empty: spoly(b, rib, 0.04, 0.098, FRM)
            piece(f'Ceiling_coffer_{nco:03d}', mk)
# walnut grid beams (segments between nodes, clipped to the region)
for x in xs:
    for ya, yb in zip(ys, ys[1:]):
        seg = _b9(x - BW / 2, ya - BW / 2, x + BW / 2, yb + BW / 2).intersection(REG)
        for g in (getattr(seg, 'geoms', None) or [seg]):
            if g.geom_type == 'Polygon' and g.area > 0.01: piece('Ceiling_grid', lambda b, g=g: spoly(b, g, -BD + 0.10, 0.10, FRM))
for y in ys:
    for xa, xb in zip(xs, xs[1:] + [xs[-1] + M]):
        seg = _b9(xa - BW / 2, y - BW / 2, xb + BW / 2, y + BW / 2).intersection(REG)
        for g in (getattr(seg, 'geoms', None) or [seg]):
            if g.geom_type == 'Polygon' and g.area > 0.01: piece('Ceiling_grid', lambda b, g=g: spoly(b, g, -BD + 0.10, 0.10, FRM))
# perimeter edge trim (closes the coffers at the region boundary)
edge = REG.difference(REG.buffer(-0.07, join_style=2))
for g in (getattr(edge, 'geoms', None) or [edge]):
    if g.geom_type == 'Polygon' and g.area > 0.005: piece('Ceiling_edge', lambda b, g=g: spoly(b, g, -BD + 0.10, 0.10, FRM))
# cull pieces that would meet anything (rods, lamps, columns, walls) — the lamp drops through an opening instead
from mathutils.bvhtree import BVHTree as _BV9
import bmesh as _bm9
def _tree(me, mw=None):
    b_ = _bm9.new(); b_.from_mesh(me)
    if mw: b_.transform(mw)
    b_.normal_update()
    for v_ in b_.verts: v_.co -= v_.normal * 0.002
    t = _BV9.FromBMesh(b_); b_.free(); return t
cands = []
for o in bpy.data.objects:
    if o.type != 'MESH' or 'foliage' in o.data.name or o.name.startswith(('roof_panel', 'purlin', 'flashing', 'gutter')): continue
    lo, hi = _bb(o)
    if hi[2] < 2.6 or lo[2] > 3.4: continue
    cands.append((o, lo, hi, [None]))
HIT9 = {}
keep = {'Ceiling_coffers': MB(), 'Ceiling_grid': MB()}; nkill = 0
for name, b in pieces9:
    me = b.mesh('_c9'); vs = [v.co for v in me.vertices]
    lo = [min(v[i] for v in vs) for i in range(3)]; hi = [max(v[i] for v in vs) for i in range(3)]
    t = None; bad = False
    for o, l2, h2, tc in cands:
        if any(h2[i] < lo[i] or l2[i] > hi[i] for i in range(3)): continue
        t = t or _tree(me); tc[0] = tc[0] or _tree(o.data, o.matrix_world)
        if t.overlap(tc[0]): bad = True; HIT9[o.name.rstrip('0123456789.')] = HIT9.get(o.name.rstrip('0123456789.'), 0) + 1; break
    if bad: nkill += 1; bpy.data.meshes.remove(me); continue
    dst = keep['Ceiling_coffers' if name.startswith('Ceiling_coffer') else 'Ceiling_grid']
    bm_ = dst.bm; n0 = len(bm_.faces); bm_.from_mesh(me)
    for f in list(bm_.faces)[n0:]:
        mm = me.materials[f.material_index]; f.material_index = dst.mi(mm)
    bpy.data.meshes.remove(me)
for nm_, b in keep.items(): inst(b.mesh(nm_), nm_, (0, 0, 0), 0, 'Carpet_ceiling')
print('rev 10.9 ceiling coffers', nco, 'pieces left out at hangers', nkill, HIT9)
# ---------------------------------------------------------------- framed backlit carpets on the clay boundary wall (De Bobo)
A9 = (-0.1675, 0.0); a9 = math.atan2(3.3892, 13.626); U9 = Vector((math.cos(a9), math.sin(a9), 0)); N9 = Vector((-math.sin(a9), math.cos(a9), 0))
dg9 = bpy.context.evaluated_depsgraph_get(); sc9 = bpy.context.scene
def a_framed_carpet(W, H, k):
    """walnut frame 70 x 50 with a moulded lip, carpet panel inside, warm LED halo 30 mm behind (wall-wash backlight);
    local: x along the wall, y = 0 wall face, +y into the room, z up from the bottom"""
    b = MB(); F = 0.07
    b.box(-W / 2 + 0.03, 0.0, 0.03, W / 2 - 0.03, 0.03, H - 0.03, LED)                       # LED box: lights the wall around
    for (x0, z0, x1, z1) in ((-W / 2, 0, W / 2, F), (-W / 2, H - F, W / 2, H), (-W / 2, F, -W / 2 + F, H - F), (W / 2 - F, F, W / 2, H - F)):
        b.box(x0, 0.03, z0, x1, 0.08, z1, FRM, 0.006)
    b.box(-W / 2 + F, 0.045, F, W / 2 - F, 0.06, H - F, rugmat(k, True))
    b.box(-W / 2 + 0.01, 0.08, H - 0.012, W / 2 - 0.01, 0.09, H - 0.002, m['brass'])               # brass lip on the head
    me = b.mesh(f'Framed_carpet_{int(W * 100)}x{int(H * 100)}_{k}')
    for p in me.polygons:                                                                        # carpet image over the panel face
        if me.materials[p.material_index].name.startswith('rug_p') and p.normal.y > 0.5:
            for li in p.loop_indices:
                v = me.vertices[me.loops[li].vertex_index].co
                me.uv_layers.active.data[li].uv = ((v.x + W / 2 - F) / (W - 2 * F), (v.z - F) / (H - 2 * F))
    return me
nfc9 = 0
for k_, s_ in enumerate((1.6, 3.4, 5.2, 7.0, 8.8)):
    p0 = Vector((A9[0], A9[1], 2.75)) + U9 * s_ + N9 * 1.5
    hit, loc, nrm, idx, ob, mx = sc9.ray_cast(dg9, p0, -N9)
    if not hit or not ob.name.startswith('Boundary_clay_wall') or (loc - p0).length > 1.6: continue
    rz = math.atan2(N9.y, N9.x) - math.pi / 2
    o_ = inst(a_framed_carpet(1.3, 0.7, (k_ * 4 + 2) % 19 + 1), f'Wall_framed_carpet_{k_ + 1}', (loc.x + N9.x * 0.001, loc.y + N9.y * 0.001, 2.32), rz, 'Photo_lounge')
    bpy.context.view_layer.update()
    lo_, hi_ = _bb(o_); bad = False; t1 = _tree(o_.data, o_.matrix_world)
    for o2 in bpy.data.objects:
        if o2 is o_ or o2.type != 'MESH' or 'foliage' in o2.data.name: continue
        l2, h2 = _bb(o2)
        if any(h2[i] < lo_[i] or l2[i] > hi_[i] for i in range(3)): continue
        if t1.overlap(_tree(o2.data, o2.matrix_world)): bad = True; break
    if bad: bpy.data.objects.remove(o_); continue
    nfc9 += 1
print('rev 10.9 framed backlit carpets on the clay wall', nfc9)
