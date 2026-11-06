"""rev. 11.0 (owner: 'beams and columns outside, on the facade'): the street eave is finished like an aivan eave
  * every roof beam that runs out past the street columns gets a walnut casing (sides chip-carved with the star band, real relief)
    with a stepped carved corbel under its end and a brass end cap
  * a walnut fascia hangs under the gutter along the whole street front, faced with real 100 mm glazed tiles (cobalt / white /
    turquoise rhythm), and below it a carved walnut fringe of pointed drops (the Khiva / Bukhara eave lambrequin)
  * pieces that would meet the pishtaq / sebil / columns are left out (the eave dies into the pishtaq cleanly)"""
from shapely.geometry import Polygon as _P10
G0 = Vector((13.709, 3.39, 3.07)); G1 = Vector((10.452, 36.43, 3.184))              # gutter outer bottom edge
GD = (G1 - G0); GL = GD.length; GU = GD.normalized(); GN = Vector((GU.y, -GU.x, 0)).normalized()   # outward = towards the street (+x side)
if GN.x < 0: GN = -GN
BEAMCV = mat('walnut_beam', (0.2, 0.12, 0.07), rough=0.5); BEAMCV.node_tree.nodes  # replaced by real carving below
_wdn = XW['wd']
COLS = {4.1: 12.64, 9.85: 12.07, 15.3: 11.53, 18.3: 11.23, 21.35: 10.93, 25.6: 10.51, 29.1: 10.17, 32.1: 9.87, 36.3: 9.46}
pieces10 = []
def bottom_z(x): return top(x) - 0.55
for o_ in [o for o in bpy.data.objects if o.name.startswith('roof_beam_y')]:
    P = [o_.matrix_world @ v.co for v in o_.data.vertices]
    xe = max(p.x for p in P); y0_ = min(p.y for p in P); y1_ = max(p.y for p in P); yc = (y0_ + y1_) / 2
    if xe < 9.0: continue
    xc = min(COLS.items(), key=lambda kv: abs(kv[0] - yc))[1] + 0.39           # casing starts just outside the column capital
    if xe - xc < 0.3: continue
    b = MB(); hw = (y1_ - y0_) / 2 + 0.035
    bm_ = b.bm; i_s = b.mi(BEAMCV); i_w = b.mi(_wdn)
    def V(x, y, dz): return bm_.verts.new((x, y, bottom_z(x) + dz))
    # casing: U-shape box around the beam (sides + soffit), top stops 5 mm under the beam top (purlins pass over)
    for (ya, yb, mi_) in ((yc - hw, yc - hw + 0.03, i_s), (yc + hw - 0.03, yc + hw, i_s)):
        vs = [V(xc, ya, -0.03), V(xe, ya, -0.03), V(xe, yb, -0.03), V(xc, yb, -0.03), V(xc, ya, 0.295), V(xe, ya, 0.295), V(xe, yb, 0.295), V(xc, yb, 0.295)]
        for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm_.faces.new([vs[k] for k in q]).material_index = mi_
    vs = [V(xc, yc - hw + 0.03, -0.03), V(xe, yc - hw + 0.03, -0.03), V(xe, yc + hw - 0.03, -0.03), V(xc, yc + hw - 0.03, -0.03),
          V(xc, yc - hw + 0.03, -0.002), V(xe, yc - hw + 0.03, -0.002), V(xe, yc + hw - 0.03, -0.002), V(xc, yc + hw - 0.03, -0.002)]
    for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm_.faces.new([vs[k] for k in q]).material_index = i_w
    # stepped carved corbel under the beam end + brass end cap
    zb = bottom_z(xe) - 0.03
    for k, (L, h) in enumerate(((0.42, 0.05), (0.32, 0.05), (0.22, 0.05), (0.12, 0.05))):
        L = min(L, (xe - xc) * (1 - 0.2 * k) - 0.02)
        if L < 0.05: break
        b.box(xe - L, yc - hw + 0.01 + 0.006 * k, zb - h * (k + 1), xe - 0.0, yc + hw - 0.01 - 0.006 * k, zb - h * k, _wdn, 0.004)
    b.box(xe - 0.002, yc - hw, zb - 0.2, xe + 0.006, yc + hw, bottom_z(xe) + 0.295, m['brass'], 0.002)
    pieces10.append((f'Facade_beam_casing_{yc:.1f}', b))
# ---------------------------------------------------------------- eave fascia + tile band + carved fringe (local frame: x along gutter)
FT = mat('fascia_tile', (0.03, 0.1, 0.42), rough=0.12, coat=0.9)
n_seg = int(GL / 1.0); ang = math.atan2(GU.y, GU.x)
for s in range(n_seg):
    b = MB(); u0, u1 = s * GL / n_seg + 0.002, (s + 1) * GL / n_seg - 0.002
    b.box(u0, -0.04, -0.30, u1, 0.0, -0.002, _wdn, 0.003)                        # fascia board under the gutter
    b.box(u0, 0.0, -0.27, u1, 0.012, -0.03, MORTAR)                              # tile bed
    T, J = 0.1, 0.004; n_ = int((u1 - u0) / (T + J))
    for i in range(n_):
        for j in range(2):
            ua = u0 + 0.01 + i * (T + J); za = -0.265 + j * (T + J) + 0.017
            k_ = (s * n_ + i + j) % 4
            b.box(ua, 0.012, za, ua + T, 0.02, za + T, (TILE[0], TILE[1], TILE[2], TILE[0])[k_], 0.002)
    # carved fringe: pointed drops every 0.25 with a round hole, 25 mm walnut plate
    drops = []
    for i in range(int((u1 - u0) / 0.25)):
        c = u0 + 0.125 + i * 0.25
        drops += [(c - 0.125, -0.30), (c - 0.07, -0.33), (c - 0.03, -0.37), (c, -0.42), (c + 0.03, -0.37), (c + 0.07, -0.33)]
    drops = [(u0, -0.30)] + drops + [(u1, -0.33), (u1, -0.30)]
    poly = _P10(drops + [(u1, -0.295), (u0, -0.295)]).buffer(0)
    for g in (getattr(poly, 'geoms', None) or [poly]):
        if g.geom_type == 'Polygon': b.extrude(list(g.exterior.coords)[:-1], -0.035, -0.01, _wdn, 'xz')
    me = b.mesh(f'_fas{s}')
    k_fall = (G1.z - G0.z) / GL
    for v in me.vertices:                                                       # built with the street at +y: mirror to the frame (street = -y local)
        x, y, z = v.co; v.co = Vector((x, -y, z + k_fall * x))
    me.flip_normals()
    pieces10.append((f'Facade_fascia', me))
# ---------------------------------------------------------------- place + cull
def _tree10(me, mw):
    b_ = _bm9.new(); b_.from_mesh(me); b_.transform(mw); b_.normal_update()
    for v_ in b_.verts: v_.co -= v_.normal * 0.002
    t = _BV9.FromBMesh(b_); b_.free(); return t
from mathutils import Matrix as _Mx
MWF = _Mx.Translation(G0) @ _Mx.Rotation(ang, 4, 'Z')
cands10 = []
for o in bpy.data.objects:
    if o.type != 'MESH' or 'foliage' in o.data.name or o.name.startswith(('roof_beam_y', 'roof_panel', 'purlin', 'gutter_street')): continue
    lo, hi = _bb(o)
    if hi[0] < 9.0 or lo[2] > 3.6 or hi[2] < 2.2: continue
    cands10.append((o, lo, hi, [None]))
HIT10 = []
keep10 = {'Facade_beam_casing': MB(), 'Facade_fascia': MB()}; nk10 = 0
for name, src in pieces10:
    me = src.mesh('_p10') if isinstance(src, MB) else src
    mw = MWF if name == 'Facade_fascia' else _Mx.Identity(4)
    P = [mw @ v.co for v in me.vertices]; lo = [min(p[i] for p in P) for i in range(3)]; hi = [max(p[i] for p in P) for i in range(3)]
    t = None; bad = False
    for o, l2, h2, tc in cands10:
        if any(h2[i] < lo[i] or l2[i] > hi[i] for i in range(3)): continue
        t = t or _tree10(me, mw); tc[0] = tc[0] or _tree10(o.data, o.matrix_world)
        if t.overlap(tc[0]): bad = True; HIT10.append((name, o.name)); break
    if bad: nk10 += 1; continue
    dst = keep10['Facade_fascia' if name == 'Facade_fascia' else 'Facade_beam_casing']
    me2 = me.copy(); me2.transform(mw)
    n0 = len(dst.bm.faces); dst.bm.from_mesh(me2)
    for f in list(dst.bm.faces)[n0:]: f.material_index = dst.mi(me2.materials[f.material_index])
for nm_, b in keep10.items(): inst(b.mesh(nm_), nm_, (0, 0, 0), 0, 'Street_facade')
# real chip carving on the casing sides
PAT.clear(); PAT['walnut_beam'] = (WDARK, 0.005, _stars_d(0.12, 0.045, XW['wd']), XW['wd'], 0.07); SIDES.clear()
realize_all(skip=('Booth',))
print('rev 11.0 facade eave: pieces', len(pieces10), 'left out', nk10, 'carved', nobj, HIT10)
