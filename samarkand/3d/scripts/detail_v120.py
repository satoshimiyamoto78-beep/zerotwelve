"""rev. 12.0 (owner, 11 Nov) — block 1:
  * AIVAN WALL: the wall carpets run from the deck to the aivan ceiling (were 0.75..2.29 under a carved frieze); the frieze is removed;
    the same pierced star lattice as in the entrance corridor (walnut 30 mm, 160 cell) covers the wall from the bar wall to the hall
    door and the bays between the carpets
  * MANGAL: the roof beam stub west of the hood is boxed in brick (the beam disappears inside the hood masonry)
  * LIGHT: a cascade chandelier over every hall table group (the hall had only the dome chandelier), brass lantern sconces on the dome
    columns and on the street columns, recessed brass uplights at the foot of the aivan columns
  * sockets: pop-up floor boxes at the table ends (detail_v102), wall sockets on the aivan wall at +0.30"""
import math as _m0
_W = XW['wd']; _LED0 = mat('led_warm', (1.0, 0.72, 0.42), emit=(1.0, 0.72, 0.42), strength=6.0)
def _rmp(*pref):
    for o_ in [o for o in bpy.data.objects if o.name.startswith(pref)]: bpy.data.objects.remove(o_)
# ---------------- aivan wall
_rmp('Aivan_frieze_', 'Aivan_wallcarpet_')
XWALL = 0.14; ZTOPA = 2.79
def ext_safe(b, poly, a0, a1, mm, plane):
    """ext_holes that drops degenerate cap triangles / wall quads (thin slivers of the lattice union)"""
    import shapely
    V = {}
    def P(u, v, w):
        k = (round(u, 5), round(v, 5), w)
        if k not in V: V[k] = b.bm.verts.new({'xy': (u, v, w), 'xz': (u, w, v), 'yz': (w, u, v)}[plane])
        return V[k]
    lo, hi = min(a0, a1), max(a0, a1); i = b.mi(mm); fs = []
    def F(vs):
        if len(set(vs)) == len(vs):
            try: fs.append(b.bm.faces.new(vs))
            except ValueError: pass
    for t in shapely.constrained_delaunay_triangles(poly).geoms:
        c = list(t.exterior.coords)[:3]
        F([P(u, v, lo) for u, v in c]); F([P(u, v, hi) for u, v in reversed(c)])
    for r in [poly.exterior] + list(poly.interiors):
        c = list(r.coords)[:-1]
        for k in range(len(c)):
            (u0, v0), (u1, v1) = c[k], c[(k + 1) % len(c)]
            F([P(u0, v0, lo), P(u1, v1, lo), P(u1, v1, hi), P(u0, v0, hi)])
    for f in fs: f.material_index = i
    bmesh.ops.recalc_face_normals(b.bm, faces=fs)
def lat_panel(nm, y0, y1, z0, z1):
    b = MB()
    for q in lattice_poly(y0, z0, y1, z1, 'star', 0.16, 0.014, 0.06): ext_safe(b, q.simplify(0.0005), XWALL + 0.005, XWALL + 0.035, _W, 'yz')
    b.box(XWALL, y0, z0, XWALL + 0.005, y1, z1, mat('charcoal_mdf', (0.035, 0.032, 0.03), rough=0.75))        # dark backing board
    b.box(XWALL + 0.036, y0 + 0.05, z0 + 0.002, XWALL + 0.05, y1 - 0.05, z0 + 0.02, _LED0)                      # uplight at the foot
    inst(b.mesh(nm), nm, (0, 0, 0), 0, 'Aivan')
lat_panel('Aivan_lattice_0', 14.34, 15.28, TER + 0.02, ZTOPA)
lat_panel('Aivan_lattice_1', 15.32, 16.66, 0.02, ZTOPA)
lat_panel('Aivan_lattice_2', 24.06, 25.96, 0.02, ZTOPA)
lat_panel('Aivan_lattice_3', 27.82, 28.28, 0.02, ZTOPA)
for k, (y0, y1, rug) in enumerate(((18.60, 20.39, 'rug_p01_uv'), (20.41, 22.21, 'rug_p02_uv'), (22.23, 24.03, 'rug_p12_uv'), (25.99, 27.79, 'rug_p13_uv'))):
    b = MB(); rm = bpy.data.materials.get(rug) or X['oldrug_uv']
    b.picture_box(XWALL, y0 + 0.02, 0.03, XWALL + 0.015, y1 - 0.02, ZTOPA - 0.04, rm, '+x')
    b.rod((XWALL + 0.03, y0, ZTOPA - 0.03), (XWALL + 0.03, y1, ZTOPA - 0.03), 0.012, m['brass'], 10)           # hanging rod
    for yy in (y0 + 0.01, y1 - 0.01): b.box(XWALL, yy - 0.006, ZTOPA - 0.045, XWALL + 0.03, yy + 0.006, ZTOPA - 0.015, m['brass'])
    b.box(XWALL, y0 + 0.02, 0.0, XWALL + 0.02, y1 - 0.02, 0.03, _W)                                               # skirting batten
    inst(b.mesh(f'Aivan_wallcarpet_{k + 1}'), f'Aivan_wallcarpet_{k + 1}', (0, 0, 0), 0, 'Aivan')
for k, yy in enumerate((19.0, 20.8, 22.6, 26.4)):                                                                # wall sockets by the settees
    inst(a_wallsocket(), f'Aivan_wallsocket_{k + 1}', (XWALL + 0.02, yy + 0.9, 0.30), _m0.pi, 'Lights')
# ---------------- mangal: beam stub in brick
_bk = bpy.data.materials.get('brick_1') or X['bannai']
b = MB(); b.box(10.26, 3.95, TER + 2.66, 11.0, 4.26, TER + 3.22, _bk); inst(b.mesh('Mangal_beam_casing'), 'Mangal_beam_casing', (0, 0, 0), 0, 'Mangal')
# ---------------- light
dg = bpy.context.evaluated_depsgraph_get(); dg.update(); _sc = bpy.context.scene
def ceil_at(x, y, z0=TER + 2.2):
    h = _sc.ray_cast(dg, (x, y, z0), (0, 0, 1), distance=3.0); return h[1].z if h[0] else None
_have = [(o.location.x, o.location.y) for o in bpy.data.objects if 'chandelier' in o.name.lower() or 'pendant' in o.name.lower() or 'lantern_hang' in o.name]
_have += [((_bb(o)[0][0] + _bb(o)[1][0]) / 2, (_bb(o)[0][1] + _bb(o)[1][1]) / 2) for o in bpy.data.objects if o.type == 'MESH' and ('chandelier' in o.name.lower() or 'pendant' in o.name.lower() or 'Cascade' in o.name)]
nh = 0; _put = []
for o_ in sorted([o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('Table_') and not o.name.endswith('_real')], key=lambda o: o.name):
    lo_, hi_ = _bb(o_); cx, cy = (lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2
    if lo_[2] > TER + 0.05 or not (2.8 < cx < 8.2 and 7.0 < cy < 36.0): continue
    if any((cx - x) ** 2 + (cy - y) ** 2 < 1.5 ** 2 for x, y in _have + _put): continue
    if (cx - 6.0) ** 2 + (cy - 19.9) ** 2 < 3.0 ** 2: continue                                                   # under the dome: its own cascade
    zc = ceil_at(cx, cy)
    if zc is None or zc - TER < 2.9: continue
    nh += 1; mini_cascade(f'Hall_chandelier_{nh:02d}', cx, cy, zc, TER + 2.05, 'Lights', 0.2); _put.append((cx, cy))
@cached
def a_sconce():
    """brass lantern sconce: back plate 90 x 180, arm, pierced lantern h 260; origin = wall point, +x out of the wall"""
    b = MB(); B_ = m['brass']; P_ = bpy.data.materials.get('pierced_brass') or B_
    b.box(0.0, -0.045, -0.09, 0.012, 0.045, 0.09, B_, 0.002)
    b.rod((0.012, 0, 0.03), (0.11, 0, 0.08), 0.008, B_, 8); b.rod((0.11, 0, 0.08), (0.11, 0, 0.05), 0.005, B_, 6)
    b.lathe(0.11, 0, -0.21, [(0.0, 0.0), (0.03, 0.0), (0.055, 0.05), (0.06, 0.13), (0.045, 0.2), (0.02, 0.24), (0.012, 0.26), (0.0, 0.26)], P_, 16)
    b.cyl(0.11, 0, -0.17, -0.02, 0.025, _LED0, 10)
    return b.mesh('Sconce_lantern')
ns_ = 0
for (cx, cy, half) in ((4.13, 18.3, 0.16), (7.87, 18.3, 0.16), (4.01, 21.35, 0.16), (7.99, 21.35, 0.16)):       # dome columns: face to the dome centre
    a = _m0.atan2(19.9 - cy, 6.0 - cx); a = round(a / (_m0.pi / 2)) * (_m0.pi / 2)
    h = _sc.ray_cast(dg, (cx + 0.6 * _m0.cos(a), cy + 0.6 * _m0.sin(a), TER + 1.95), (-_m0.cos(a), -_m0.sin(a), 0), distance=0.7)
    if h[0]: ns_ += 1; inst(a_sconce(), f'Sconce_dome_{ns_}', (h[1].x, h[1].y, TER + 1.95), a, 'Lights')
for k, (cx, cy) in enumerate(((12.07, 9.85), (10.94, 21.35), (10.52, 25.6), (10.17, 29.1), (9.88, 32.1), (9.46, 36.3))):   # street columns, inner face
    h = _sc.ray_cast(dg, (cx - 0.6, cy, TER + 2.0), (1, 0, 0), distance=0.7)
    if h[0]: inst(a_sconce(), f'Sconce_col_{k + 1}', (h[1].x, h[1].y, TER + 2.0), _m0.pi, 'Lights')
@cached
def a_uplight():
    b = MB(); b.cyl(0, 0, 0.0, 0.006, 0.05, m['brass'], 20); b.cyl(0, 0, 0.006, 0.008, 0.036, _LED0, 20); return b.mesh('Floor_uplight')
nu = 0
for o_ in sorted([o for o in bpy.data.objects if o.name.startswith('Khiva_column_') and not o.name.endswith('_real')], key=lambda o: o.name)[::2]:
    lo_, hi_ = _bb(o_); nu += 1
    inst(a_uplight(), f'Aivan_uplight_{nu:02d}', (hi_[0] + 0.16, (lo_[1] + hi_[1]) / 2, TER), 0, 'Lights')
print('rev 12.0 block 1: hall chandeliers', nh, 'sconces', ns_ + 6, 'uplights', nu)
