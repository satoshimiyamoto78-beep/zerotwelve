"""rev. 11.2 (owner: 'joints — where the rail meets the stair, the wall, the column — must be worked out'):
  * aivan balustrade ends run into the Khiva columns: top + bottom rail stubs to the column face, brass escutcheon at the column
  * balustrade corners and free ends get walnut newel posts (90 x 90, moulded cap, turned finial)
  * stair handrails (A, B) at the top continue to the column face and fix with a brass wall flange (escutcheon)
  * corridor drapes: brass curtain rod continued to the frame with an end bracket
  * mangal west wall: the slot to the storage closed with a brick return; kids fence: end post"""
import bmesh as _bm12
from mathutils.bvhtree import BVHTree as _BV12
_T12 = {}
def _tr(o):
    if o.name not in _T12:
        b_ = _bm12.new(); b_.from_mesh(o.data); b_.transform(o.matrix_world); _T12[o.name] = _BV12.FromBMesh(b_); b_.free()
    return _T12[o.name]
def wverts(o): return [o.matrix_world @ v.co for v in o.data.vertices]
def end_pts(o, ax, which, zmin=-9, zmax=9, tol=0.03):
    V = [p for p in wverts(o) if zmin <= p.z <= zmax]
    e = (min if which == 'lo' else max)(p[ax] for p in V)
    S = [p for p in V if abs(p[ax] - e) < tol]
    return sum(S, Vector()) / len(S) if S else None
def nearest_on(p, names, maxd=0.4):
    best = (maxd, None, None)
    for o in bpy.data.objects:
        if o.type != 'MESH' or not o.name.startswith(names): continue
        lo, hi = _bb(o)
        if any(hi[i] < p[i] - maxd or lo[i] > p[i] + maxd for i in range(3)): continue
        q = _tr(o).find_nearest(p)
        if q[0] is not None and q[3] < best[0]: best = (q[3], q[0], o)
    return best
B = MB(); W = XW['wd']; BRS = m['brass']; nj = 0
def stub(p, q, w, h, mm):
    """walnut / brass bar from p to q (horizontal), cross-section w x h"""
    d = q - p; L = d.length
    if L < 0.003: return
    ang = math.atan2(d.y, d.x); c = (p + q) / 2
    me = MB(); me.box(-L / 2 - 0.0012, -w / 2, -h / 2, L / 2 + 0.0012, w / 2, h / 2, mm, 0.002)
    m_ = me.mesh('_stub')
    for v in m_.vertices:
        x, y, z = v.co; v.co = Vector((c.x + x * math.cos(ang) - y * math.sin(ang), c.y + x * math.sin(ang) + y * math.cos(ang), c.z + z))
    n0 = len(B.bm.faces); B.bm.from_mesh(m_)
    for f in list(B.bm.faces)[n0:]: f.material_index = B.mi(mm)
    bpy.data.meshes.remove(m_)
def escutcheon(q, d, r=0.04):
    """brass flange disc on a surface at q, facing -d (d = direction from the rail to the surface)"""
    d = d.normalized(); ang = math.atan2(d.y, d.x)
    me = MB(); me.lathe(0, 0, -0.008, [(0.0, 0.0), (r, 0.0), (r, 0.004), (r * 0.6, 0.008), (0.0, 0.008)], BRS, 20)
    m_ = me.mesh('_esc')
    for v in m_.vertices:                                    # disc axis z -> horizontal d
        x, y, z = v.co; xx, zz = z, x
        v.co = Vector((q.x + xx * math.cos(ang) - y * math.sin(ang), q.y + xx * math.sin(ang) + y * math.cos(ang), q.z + zz))
    n0 = len(B.bm.faces); B.bm.from_mesh(m_)
    for f in list(B.bm.faces)[n0:]: f.material_index = B.mi(BRS)
    bpy.data.meshes.remove(m_)
def newel(x, y, z0, H=1.08):
    B.box(x - 0.045, y - 0.045, z0, x + 0.045, y + 0.045, z0 + H - 0.05, W, 0.004)
    B.box(x - 0.06, y - 0.06, z0 + H - 0.05, x + 0.06, y + 0.06, z0 + H - 0.02, W, 0.006)
    B.lathe(x, y, z0 + H - 0.02, [(0.0, 0.0), (0.03, 0.0), (0.035, 0.03), (0.02, 0.06), (0.0, 0.08)], W, 16)
    B.box(x - 0.05, y - 0.05, z0, x + 0.05, y + 0.05, z0 + 0.04, BRS, 0.003)
# ---- aivan balustrades
bal = {o.name: o for o in bpy.data.objects if o.name.startswith('Aivan_balustrade') and o.type == 'MESH'}
for o in bal.values():
    lo, hi = _bb(o); ax = 0 if hi[0] - lo[0] > hi[1] - lo[1] else 1
    for which in ('lo', 'hi'):
        pt = end_pts(o, ax, which, zmin=0.85)
        pb = end_pts(o, ax, which, zmax=0.25)
        if pt is None: continue
        dist, q, tgt = nearest_on(pt, ('Khiva_column',), 0.2)
        if tgt is not None:                                                     # into the column: rail stubs + escutcheon
            for p_ in (pt, pb):
                if p_ is None: continue
                d_, q_, t_ = nearest_on(p_, ('Khiva_column',), 0.25)
                if t_ is None: continue
                q_ = Vector((q_.x, q_.y, p_.z)); stub(p_, q_, 0.05, 0.05, W); escutcheon(q_, q_ - p_, 0.045); nj += 1
            continue
        dist2, q2, tgt2 = nearest_on(pt, ('Aivan_balustrade',), 0.12)
        if tgt2 is not None and tgt2 is not o:                                  # corner with the next run: one newel on the corner
            stub(pt, Vector((q2.x, q2.y, pt.z)), 0.05, 0.05, W)
            if pb is not None:
                d4, q4, t4 = nearest_on(pb, ('Aivan_balustrade',), 0.12)
                if t4 is not None and t4 is not o: stub(pb, Vector((q4.x, q4.y, pb.z)), 0.05, 0.05, W)
            nj += 1; continue
        d3, q3, t3 = nearest_on(pt, ('Aivan_ramp_handrail_posts', 'stepsA', 'stepsB'), 0.06)
        if t3 is None:                                                          # free end: newel post just beyond the end
            off = Vector((0, 0, 0)); off[ax] = -0.047 if which == 'lo' else 0.047
            newel(pt.x + off.x, pt.y + off.y, 0.0); nj += 1
# (stair handrails removed in rev 11.3 at the owner's request: decorative jugs instead)
# (corridor drapes replaced by the arch corridor in rev 11.5)
# ---- mangal west wall: brick return closing the slot to the storage
o = bpy.data.objects.get('Mangal_west_wall'); st_ = bpy.data.objects.get('storage')
if o and st_:
    lo, hi = _bb(o); l2, h2 = _bb(st_)
    if h2[1] < lo[1] + 0.001 and lo[1] - h2[1] < 0.2:
        rb = MB(); y0_, y1_ = h2[1] + 0.001, lo[1] - 0.001; rnd12 = _rnd.Random(12); row = 0; z = TER
        while z + 0.06 < hi[2]:
            rb.box(lo[0], y0_, z, hi[0], y1_, z + 0.06, BUFF[rnd12.randrange(3)], 0.002); z += 0.072
        inst(rb.mesh('Mangal_wall_return'), 'Mangal_wall_return', (0, 0, 0), 0, 'Mangal'); nj += 1
# ---- kids fence free end
o = bpy.data.objects.get('Kids_fence_carved')
if o:
    pt = end_pts(o, 0, 'hi', zmin=0.3)
    if pt is not None:
        lo, hi = _bb(o); newel(pt.x + 0.045, pt.y, lo[2], hi[2] - lo[2] + 0.05); nj += 1
inst(B.mesh('Joints_rev112'), 'Joints_rev112', (0, 0, 0), 0, 'Aivan')
print('rev 11.2 joints made', nj)
# ---- street bench pads -> real sewn cushions (owner: 'cushions everywhere')
nsp = 0
for o in [o for o in bpy.data.objects if o.name.startswith('Street_bench_pads') and o.type == 'MESH']:
    b_ = _bm12.new(); b_.from_mesh(o.data); b_.verts.ensure_lookup_table()
    parts = []; seen = set()
    for v in b_.verts:
        if v.index in seen: continue
        stack = [v]; comp = []
        while stack:
            q = stack.pop()
            if q.index in seen: continue
            seen.add(q.index); comp.append(q)
            for e in q.link_edges: stack.append(e.other_vert(q))
        fs = {f for q in comp for f in q.link_faces}
        mi_ = max(set(f.material_index for f in fs), key=lambda k: sum(1 for f in fs if f.material_index == k)) if fs else 0
        parts.append(([q.co.copy() for q in comp], mi_))
    b_.free()
    pieces = []
    for P, mi_ in parts:
        lo = [min(p[i] for p in P) for i in range(3)]; hi = [max(p[i] for p in P) for i in range(3)]
        w, d, h = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]
        if min(w, d, h) < 0.01: continue
        mm_ = o.data.materials[mi_]
        if not (h < 0.08 and w > 0.3 and d > 0.25): continue           # keep only the seat pads (the old folded flap goes)
        pl = pillow('_sbp', w, d, h + 0.02, mm_, soft=0.4, pipe=PIPE, cuts=4)
        pieces.append(at(pl, (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2] + (h + 0.02) / 2, '_sbp2'))
    if pieces: o.data = merge(o.data.name + '_soft', pieces); nsp += 1
print('rev 11.2 street bench pads -> cushions', nsp)
