"""rev. 9.8 (owner 2026-11-05):
  * mangal west wall (facing the dining): the firewood is gone; one solid wall in Samarkand hazarbaf brickwork — buff brick slips
    with a cobalt diamond lattice and nested turquoise diamonds (glazed bricks, real joints), cream stone dado with glazed
    eight-point stars, walnut staff door in a tiled frame; the clad pergola post stays as a pilaster
  * the boundary wall behind the majlis / mangal closes the interior to the ceiling (pergola slab / under the purlins + infill)
  * kilims and suzanis replaced by the owner's Persian rugs (upholstery, tent rug, majlis rug, wall carpets)"""
_rm('Firewood_wall', 'Mangal_west_wall')
BX0_, BX1_, BY0_, BY1_ = D['bbq']; ZW = TER + 3.2
pp_ = D['pergola']['posts'][5]; PY0, PY1 = pp_[1] - 0.135, pp_[1] + 0.135
BUFF = [terracotta(f'brick_buff_{k}', c) for k, c in enumerate(((0.74, 0.6, 0.44), (0.7, 0.56, 0.4), (0.77, 0.63, 0.47)))]
GT, GC = GLZ[0], GLZ[1]
CREAM = mat('stone_cream', (0.85, 0.78, 0.64), rough=0.6, bump=0.3, noise_var=0.05)
# ---------------------------------------------------------------- core
mb = MB()
segs = [(BY0_, 3.9, TER), (3.9, 4.8, TER + 2.1), (4.8, PY0, TER), (PY1, 8.35, TER + 2.08)]   # owner: firewood again from the post to the end
for y0_, y1_, z0_ in segs: mb.box(BX0_ + 0.02, y0_, z0_, BX0_ + 0.3, y1_, ZW, MORTAR, 0.003)
inst(mb.mesh('Mangal_west_wall'), 'Mangal_west_wall', (0, 0, 0), 0, 'Mangal')
# ---------------------------------------------------------------- hazarbaf face (x = BX0 + 0.02, bricks towards the dining, -x)
def haz(u, z):
    P = 1.2; d1 = (u + z) % P; d2 = (u - z) % P
    if min(d1, P - d1, d2, P - d2) < 0.055: return GC                                  # cobalt lattice lines
    uc = (math.floor((u + z) / P) + 0.5) * P; vc = (math.floor((u - z) / P) + 0.5) * P
    cu, cz = (uc + vc) / 2, (uc - vc) / 2; r = abs(u - cu) + abs(z - cz)
    if r < 0.07: return GC
    if r < 0.5 and int(r / 0.14) % 2 == 0: return GT                                    # nested turquoise diamonds
    return None
rnd9 = _rnd.Random(9)
def face_haz(b, y0, y1, z0, z1):
    BL, BH, J = 0.24, 0.06, 0.012; row = 0; z = z0; c = BX0_ + 0.02
    while z + BH <= z1 + 1e-6:
        off = (BL + J) / 2 if row % 2 else 0.0; u = y0 - off
        while u < y1:
            ua, ub = max(y0, u), min(y1, u + BL)
            if ub - ua > 0.03:
                mm = haz((ua + ub) / 2 - 3.0, z + BH / 2 - TER) or BUFF[rnd9.randrange(3)]
                d = 0.02 + (0.002 if mm in (GT, GC) else rnd9.uniform(-0.002, 0.002))
                b.box(c - d, ua, z, c, ub, z + BH, mm, 0.002)
            u += BL + J
        z += BH + J; row += 1
mb = MB(); ZD = TER + 0.9
FACE = {0: (BY0_, 3.78), 1: (3.9, 4.8), 2: (4.92, PY0), 3: (PY1, 8.35)}
for si_, (y0_, y1_, z0_) in enumerate(segs):
    fa, fb = FACE[si_]
    if z0_ > TER: face_haz(mb, fa, fb, (TER + 2.226) if si_ == 1 else (z0_ + 0.01), ZW - 0.01); continue
    face_haz(mb, fa, fb, ZD + 0.03, ZW - 0.01)
    if si_ == 0: face_haz(mb, 3.78, 3.9, TER + 2.226, ZW - 0.01)
    if si_ == 2: face_haz(mb, 4.8, 4.92, TER + 2.226, ZW - 0.01)
    y0_, y1_ = fa, fb
    mb.box(BX0_ - 0.02, y0_, TER, BX0_ + 0.02, y1_, TER + 0.12, CREAM, 0.004)                   # stone plinth
    mb.box(BX0_ - 0.01, y0_, TER + 0.12, BX0_ + 0.02, y1_, ZD, CREAM, 0.003)                     # cream stone dado
    mb.box(BX0_ - 0.026, y0_, ZD, BX0_ + 0.02, y1_, ZD + 0.03, GT, 0.002)                         # turquoise rail
    n = int((y1_ - y0_) / 0.42)
    for k in range(n):                                                                          # glazed eight-point stars in the dado
        yc = y0_ + (y1_ - y0_ - n * 0.42) / 2 + 0.21 + k * 0.42; zc = TER + 0.12 + (ZD - TER - 0.12) / 2
        st = [(yc + (0.13 if i % 2 == 0 else 0.07) * math.cos(math.pi * i / 8), zc + (0.13 if i % 2 == 0 else 0.07) * math.sin(math.pi * i / 8)) for i in range(16)]
        mb.extrude(st, BX0_ - 0.022, BX0_ - 0.01, GC if k % 2 else GT, 'yz')
        mb.extrude([(yc + 0.04 * math.cos(math.pi * i / 4), zc + 0.04 * math.sin(math.pi * i / 4)) for i in range(8)], BX0_ - 0.026, BX0_ - 0.022, CU, 'yz')
inst(mb.mesh('Mangal_west_hazarbaf'), 'Mangal_west_hazarbaf', (0, 0, 0), 0, 'Mangal')
# firewood stack in a walnut frame between the post and the wall end (it shows to the dining)
mb = MB(); x0w, x1w, y0w, y1w = BX0_, BX0_ + 0.3, PY1, 8.35; r = 0.0625
mb.box(x0w, y0w, TER, x1w, y1w, TER + 0.08, XW['wd'], 0.003); mb.box(x0w, y0w, TER + 2.0, x1w, y1w, TER + 2.08, XW['wd'], 0.003)
mb.box(x0w, y0w, TER + 0.08, x1w, y0w + 0.06, TER + 2.0, XW['wd'], 0.003); mb.box(x0w, y1w - 0.06, TER + 0.08, x1w, y1w, TER + 2.0, XW['wd'], 0.003)
row = 0; zz = TER + 0.08 + r
while zz + r <= TER + 2.0 + 1e-6:
    yy = y0w + 0.06 + r + (r if row % 2 else 0)
    while yy + r <= y1w - 0.06 + 1e-6: mb.rod((x0w + 0.01, yy, zz), (x1w - 0.01, yy, zz), r - 0.001, m['oak'], 8); yy += 2 * r
    zz += r * math.sqrt(3); row += 1
inst(mb.mesh('Firewood_wall'), 'Firewood_wall', (0, 0, 0), 0, 'Mangal')
# staff door: walnut double door with fielded panels in a tiled frame
mb = MB(); WD = XW['wd']
mb.box(BX0_ + 0.12, 3.92, TER, BX0_ + 0.16, 4.78, TER + 2.08, WD, 0.004)
for yy in (3.95, 4.37):
    for zz in (0.15, 0.8, 1.45): mb.box(BX0_ + 0.112, yy, TER + zz, BX0_ + 0.12, yy + 0.38, TER + zz + 0.55, WD, 0.006)
mb.box(BX0_ + 0.11, 4.345, TER + 0.05, BX0_ + 0.12, 4.355, TER + 2.05, m['black'])
for yy in (4.31, 4.39): mb.box(BX0_ + 0.095, yy - 0.006, TER + 1.0, BX0_ + 0.112, yy + 0.006, TER + 1.15, m['brass'], 0.002)
for y0_, y1_ in ((3.78, 3.9), (4.8, 4.92)): mb.box(BX0_ - 0.03, y0_, TER, BX0_ + 0.02, y1_, TER + 2.22, GC, 0.003)
mb.box(BX0_ - 0.03, 3.78, TER + 2.1, BX0_ + 0.02, 4.92, TER + 2.22, GC, 0.003)
inst(mb.mesh('Mangal_staff_door'), 'Mangal_staff_door', (0, 0, 0), 0, 'Mangal')

# ---------------------------------------------------------------- boundary wall up to the ceiling
A_ = (-0.1675, 0.0); ANG_ = math.atan2(3.3892, 13.4586 + 0.1675); cA, sA = math.cos(ANG_), math.sin(ANG_)
def Wp(u, v): return (A_[0] + cA * u - sA * v, A_[1] + sA * u + cA * v)
def prism_z(b, quad, zb, ztf, mm):
    bm_ = b.bm; i = b.mi(mm)
    lo = [bm_.verts.new((x, y, zb)) for x, y in quad]; hi = [bm_.verts.new((x, y, ztf(x))) for x, y in quad]
    fs = [bm_.faces.new(list(reversed(lo))), bm_.faces.new(hi)] + [bm_.faces.new((lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k])) for k in range(4)]
    for f in fs: f.material_index = i
    bmesh.ops.recalc_face_normals(bm_, faces=fs)
PZT = TER + D['pergola']['top']; HW0 = TER + 2.7
cuts_ = sorted(to_uv(*[p / 1000 for p in pp])[0] for pp in ((4552, 1277), (10180, 2677)))
purl_x = sorted({x for x, a, b in D['purlins']} | {x for x in [-6.75 + k for k in range(7)]})
mb = MB()
uSW, uSE = to_uv(4.479, 1.156)[0], to_uv(10.301, 2.604)[0]          # the room on the pergola starts at these outline corners
SP = [(0.0, cuts_[0] - 0.17, 'roof'), (cuts_[0] + 0.18, cuts_[1] - 0.18, 'perg'), (cuts_[1] + 0.18, U1, 'roof')]   # the kept pergola beams pass through the post cuts
for i_, (ua, ub, kind) in enumerate(SP):
    if ub - ua < 0.02: continue
    tv = 0.03 if kind == 'perg' else TV
    if kind == 'perg':
        prism_z(mb, [Wp(ua, 0), Wp(ub, 0), Wp(ub, tv), Wp(ua, tv)], HW0, lambda x: PZT, CLAY); continue
    # wall to just under the purlins, then infill between the purlins up to the sheeting
    prism_z(mb, [Wp(ua, 0), Wp(ub, 0), Wp(ub, tv), Wp(ua, tv)], HW0, lambda x: top(x) - 0.255, CLAY)
    stops = [ua]
    for xp in purl_x:
        for s_ in (-1, 1):                                      # u where the lot line meets the purlin flanks
            uu = (xp + s_ * 0.05 - A_[0]) / cA
            if ua < uu < ub: stops.append(uu)
    stops = sorted(stops + [ub])
    for a_, b_ in zip(stops[:-1], stops[1:]):
        xm = Wp((a_ + b_) / 2, 0)[0]
        if any(abs(xm - xp) < 0.05 for xp in purl_x) or b_ - a_ < 0.02: continue
        bm_ = mb.bm; q_ = [Wp(a_, 0), Wp(b_, 0), Wp(b_, tv), Wp(a_, tv)]; i_m = mb.mi(CLAY)
        lo_ = [bm_.verts.new((x, y, top(x) - 0.255)) for x, y in q_]; hi_ = [bm_.verts.new((x, y, top(x) - 0.06)) for x, y in q_]
        fs_ = [bm_.faces.new(list(reversed(lo_))), bm_.faces.new(hi_)] + [bm_.faces.new((lo_[k], lo_[(k + 1) % 4], hi_[(k + 1) % 4], hi_[k])) for k in range(4)]
        for f in fs_: f.material_index = i_m
        bmesh.ops.recalc_face_normals(bm_, faces=fs_)
inst(mb.mesh('Boundary_clay_wall_upper'), 'Boundary_clay_wall_upper', (0, 0, 0), 0, 'Street_facade')

# ---------------------------------------------------------------- kilims + suzanis -> the owner's Persian rugs
BOXMATS = ('kilim_f_t', 'kilim2_f_t', 'kilimref_f_t', 'kilimref2_f_t', 'majlis_t', 'suzani2_f_t', 'suzani2_t', 'kilim_t', 'kilim2_t')
UVM = {'carpet3_uv', 'carpet4_uv'}
kk = 0
for mm in list(bpy.data.materials):
    if mm.name in BOXMATS and mm.use_nodes:
        for n_ in mm.node_tree.nodes:
            if n_.type == 'TEX_IMAGE':
                kk += 1; n_.image = bpy.data.images.load(os.path.join(TEX2, f'rug_p{(kk * 7) % NRUG + 1:02d}.jpg'), check_existing=True)
for o_ in sorted([o for o in bpy.data.objects if o.type == 'MESH'], key=lambda o: o.name):
    for si, mm in enumerate(o_.data.materials):
        if mm and (mm.name in UVM or (o_.name.startswith('Majlis_rug') and mm.name == 'majlis_t')):
            Lu, Lv = uv_aspect(o_, si)
            if o_.data.users > 1: o_.data = o_.data.copy()
            o_.data.materials[si] = rugmat(k_ % NRUG + 1, Lu > Lv * 1.05); k_ += 1
print('rev 9.8 ok: box rug images', kk, 'uv rugs total', k_)
