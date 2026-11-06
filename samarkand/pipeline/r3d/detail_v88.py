"""rev. 8.8 (owner 2026-11-05):
  * ALL timber in the chair walnut (aivan, ceiling, pergola beams + post cladding, shelves, frames)
  * mangal west wall: masonry up to the pergola beams (+3.2) with the firewood niche, staff door and the clad pergola post as a pilaster
  * tree: planter ring Ø1.8 (majolica band, stone cap) with crotons — the ring bench is gone
  * MAJLIS ZONE under the pergola (owner refs: henna-night majlis + velvet / carpet backdrop): red kilim floor rug, velvet drapes and a
    medallion carpet on the south wall, walnut bench with pillows, kilim box table with a tea set, floor cushions, poufs, olive trees"""
WD = XW['wd']
_src = {mm for mm in (HZ, HY, HX, HD, m.get('walnut'), m.get('roofwood'), m.get('oak')) if mm}
for o_ in bpy.data.objects:
    if o_.type != 'MESH' or o_.name.startswith(('roof_panel', 'Roof', 'purlin', 'roof_beam')): continue
    for i_, mm in enumerate(o_.data.materials):
        if mm in _src: o_.data.materials[i_] = WD
print('wood unified to the chair walnut')

# ---------------------------------------------------------------- mangal west wall up to the pergola beams
BX0_, BX1_, BY0_, BY1_ = D['bbq']; ZW = TER + 3.2
pp_ = D['pergola']['posts'][5]                                            # mid-east post (clad 260)
mb = MB(); BR = m['brick']
for y0_, y1_, z0_ in ((BY0_, 3.9, TER), (3.9, 4.8, TER + 2.1), (4.8, 4.9, TER), (4.9, pp_[1] - 0.135, TER + 2.08), (pp_[1] + 0.135, 8.35, TER + 2.08)):
    if y1_ - y0_ > 0.01: mb.box(BX0_, y0_, z0_, BX0_ + 0.3, y1_, ZW, BR, 0.004)
inst(mb.mesh('Mangal_west_wall'), 'Mangal_west_wall', (0, 0, 0), 0, 'Mangal')

# ---------------------------------------------------------------- tree planter ring
_rm('Chinar_ringbench')
for i_, (x, y) in enumerate(D['trees']):
    mb = MB()
    mb.ring(x, y, TER, [(0.78, 0.0), (0.9, 0.0), (0.9, 0.3), (0.78, 0.3)], X['majcobalt'] if 'majcobalt' in X else BR, 72)
    mb.ring(x, y, TER + 0.3, [(0.76, 0.0), (0.93, 0.0), (0.93, 0.05), (0.76, 0.05)], m['stone'] if 'stone' in m else WD, 72)
    inst(mb.mesh('Tree_planter_ring'), f'Tree_planter_ring_{i_ + 1}', (0, 0, 0), 0, 'Trees')
    _rm('Tree_uplight')
    for k_ in range(3):                                                  # uplights set into the soil inside the ring
        aa = 2 * math.pi * k_ / 3 + 0.5; cylinder(f'Tree_uplight_{k_ + 1}', x + 0.55 * math.cos(aa), y + 0.55 * math.sin(aa), TER + 0.06, TER + 0.15, 0.045, m['brass'], 'Lights', n=12)

# ---------------------------------------------------------------- MAJLIS ZONE under the pergola
PU_ = ((10.301 - 4.479) / 6.0, (2.604 - 1.156) / 6.0); PV_ = ((3.088 - 4.479) / 5.76, (6.745 - 1.156) / 5.76)
_ang = math.atan2(PU_[1], PU_[0])
def obb(poly):
    """pergola-aligned box: centre, size along the pergola u (along the south wall) and v, angle"""
    p = poly[0]; cx = sum(q[0] for q in p) / len(p); cy = sum(q[1] for q in p) / len(p)
    us = [q[0] * PU_[0] + q[1] * PU_[1] for q in p]; vs = [q[0] * PV_[0] + q[1] * PV_[1] for q in p]
    return cx, cy, max(us) - min(us), max(vs) - min(vs), _ang
KIL = X82['majlis']; VEL = X['velvet_wine'] if 'velvet_wine' in X else X['velvet']
RUG = X['oldrug_uv'] if 'oldrug_uv' in X else X['carpet1']
@cached
def a_floor_cushion(L, W, H=0.18):
    b = MB(); b.box(-L / 2, -W / 2, 0, L / 2, W / 2, H, KIL, 0.05); return b.mesh(f'Floor_cushion_{int(L * 1000)}')
@cached
def a_kilim_pouf(s=0.4):
    b = MB(); b.box(-s / 2, -s / 2, 0, s / 2, s / 2, s, KIL, 0.03); b.box(-s / 2 + 0.01, -s / 2 + 0.01, s, s / 2 - 0.01, s / 2 - 0.01, s + 0.012, WD, 0.004)
    return b.mesh(f'Kilim_pouf_{int(s * 1000)}')
@cached
def a_kilim_table(L, W, H=0.4):
    b = MB(); b.box(-L / 2, -W / 2, 0, L / 2, W / 2, H - 0.02, KIL, 0.01); b.box(-L / 2 - 0.01, -W / 2 - 0.01, H - 0.02, L / 2 + 0.01, W / 2 + 0.01, H, WD, 0.004)
    b.lathe(0, 0, H, [(0.0, 0.0), (0.22, 0.0), (0.23, 0.012), (0.21, 0.015), (0.0, 0.004)], m['brass'], 40)
    _choynak(b, -0.06, 0.0, H + 0.006, 0.9); _piala2(b, 0.1, 0.08, H + 0.006); _piala2(b, 0.1, -0.08, H + 0.006)
    return b.mesh(f'Kilim_table_{int(L * 1000)}')
@cached
def a_majlis_bench(L, W):
    """walnut bench (turned legs, slatted back) with a long seat cushion and two kilim pillows; local x along the bench, back at -y"""
    b = MB(); hl, hw = L / 2, W / 2
    for sx in (-1, 1):
        for sy in (-1, 1): b.lathe(sx * (hl - 0.05), sy * (hw - 0.05), 0, [(0.0, 0.0), (0.03, 0.0), (0.03, 0.05), (0.022, 0.12), (0.03, 0.25), (0.022, 0.38), (0.03, 0.42), (0.0, 0.42)], WD, 16)
    b.box(-hl, -hw, 0.42, hl, hw, 0.47, WD, 0.006)
    for sx in (-1, 1): b.box(sx * (hl - 0.05) - 0.025, -hw, 0.47, sx * (hl - 0.05) + 0.025, -hw + 0.05, 0.95, WD, 0.004)
    b.box(-hl, -hw, 0.9, hl, -hw + 0.05, 0.96, WD, 0.006)
    for k in range(9): xx = -hl + 0.12 + k * (L - 0.24) / 8; b.box(xx - 0.012, -hw + 0.01, 0.47, xx + 0.012, -hw + 0.04, 0.9, WD)
    b.box(-hl + 0.04, -hw + 0.06, 0.47, hl - 0.04, hw - 0.02, 0.56, X['velvet'], 0.03)
    for sx in (-1, 1): b.box(sx * hl * 0.45 - 0.22, -hw + 0.06, 0.56, sx * hl * 0.45 + 0.22, -hw + 0.2, 0.95, KIL, 0.04)
    return b.mesh(f'Majlis_bench_{int(L * 1000)}')
@cached
def a_backdrop(L, H=2.7):
    """south-wall backdrop, local x 0..L along the wall, y 0..0.1 off it: pleated wine velvet drapes on both thirds, a medallion carpet in the
    middle, brass rod on brackets"""
    b = MB(); third = L / 3.4
    for x0, x1 in ((0.0, third * 1.2), (L - third * 1.2, L)):
        n = int((x1 - x0) / 0.12); pts = [(x0, 0.02)]
        for k in range(n + 1): pts.append((x0 + (x1 - x0) * k / n, 0.02 + (0.07 if k % 2 else 0.0)))
        pts += [(x1, 0.0), (x0, 0.0)]
        b.extrude(pts, 0.0, H - 0.1, VEL, 'xy')
    b.picture_box(third * 1.2 + 0.05, 0.03, 0.35, L - third * 1.2 - 0.05, 0.045, H - 0.2, RUG, '+y')
    b.rod((0.0, 0.08, H - 0.05), (L, 0.08, H - 0.05), 0.018, m['brass'], 12)
    for xx in (0.05, L / 2, L - 0.05): b.box(xx - 0.02, 0.0, H - 0.08, xx + 0.02, 0.08, H - 0.02, m['brass'])
    return b.mesh(f'Majlis_backdrop_{int(L * 1000)}')
OLV = [mat('olive_leaf_a', (0.30, 0.36, 0.22), rough=0.6), mat('olive_leaf_b', (0.40, 0.44, 0.30), rough=0.6)]
@cached
def a_olive(seed=5):
    import random; R_ = random.Random(seed); b = MB()
    b.lathe(0, 0, 0, [(0.0, 0.0), (0.2, 0.0), (0.24, 0.05), (0.22, 0.38), (0.25, 0.42), (0.0, 0.42)], TC['red'], 32)       # terracotta pot
    b.lathe(0, 0, 0.42, [(0.0, 0.0), (0.2, 0.0), (0.2, 0.01), (0.0, 0.01)], m['soil'] if 'soil' in m else TC['rust'], 24)
    tips = []
    for k in range(3):
        a = 2 * math.pi * k / 3 + R_.uniform(-0.3, 0.3); p1 = (0.12 * math.cos(a), 0.12 * math.sin(a), 1.25 + R_.uniform(0, 0.25))
        b.rod((0, 0, 0.43), p1, 0.022, MBARK, 8)
        for j in range(4):
            a2 = a + R_.uniform(-0.8, 0.8); p2 = (p1[0] + 0.35 * math.cos(a2), p1[1] + 0.35 * math.sin(a2), p1[2] + R_.uniform(0.1, 0.45))
            b.rod(p1, p2, 0.008, MBARK, 6); tips.append(p2)
    wood = b.mesh('Olive_wood')
    bm = bmesh.new()
    for p in tips:
        for _ in range(45):
            d = Vector((R_.gauss(0, 1), R_.gauss(0, 1), R_.gauss(0, 0.8))).normalized(); c = Vector(p) + d * R_.uniform(0.0, 0.2)
            t_ = (d + Vector((0, 0, -0.2))).normalized(); n_ = Vector((R_.gauss(0, 0.5), R_.gauss(0, 0.5), 1)).normalized()
            if abs(n_.dot(t_)) < 0.95: _leaf(bm, R_.randrange(2), c, n_, t_, R_.uniform(0.06, 0.09), 0.014)
    me = bpy.data.meshes.new('Olive_foliage'); bm.to_mesh(me); bm.free()
    for mm in OLV: me.materials.append(mm)
    me['kit'] = 1
    return wood, me

_rm('Photo_', 'Lounge')
nz_ = {}
for it in D['items']:
    k = it['kind']
    if not k.startswith('m') or k not in ('mrug', 'mdrape', 'mbench', 'mtable_low', 'mcushion', 'mpouf'): continue
    cx, cy, L, W, a = obb(it['poly']); nz_[k] = nz_.get(k, 0) + 1; nm = f'Majlis_{k[1:]}_{nz_[k]}'
    if k == 'mrug':
        mb = MB(); mb.picture_box(-L / 2, -W / 2, 0, L / 2, W / 2, 0.012, KIL, '+z'); inst(mb.mesh('Majlis_rug'), nm, (cx, cy, TER), a, 'Photo_lounge')
    elif k == 'mdrape':
        ca, sa = math.cos(a), math.sin(a); x0, y0 = cx - ca * L / 2 + sa * W / 2, cy - sa * L / 2 - ca * W / 2
        inst(a_backdrop(round(L, 3)), nm, (x0, y0, TER), a, 'Photo_lounge')
    elif k == 'mbench': inst(a_majlis_bench(round(L, 3), round(W, 3)), nm, (cx, cy, TER), a, 'Photo_lounge')
    elif k == 'mtable_low': inst(a_kilim_table(round(L, 3), round(W, 3)), nm, (cx, cy, TER + 0.012), a, 'Photo_lounge')
    elif k == 'mcushion': inst(a_floor_cushion(round(L, 3), round(W, 3)), nm, (cx, cy, TER + 0.012), a + 0.1 * nz_[k], 'Photo_lounge')
    elif k == 'mpouf': inst(a_kilim_pouf(), nm, (cx, cy, TER), a, 'Photo_lounge')
for j_, (u, v) in enumerate(((0.35, 4.6), (4.25, 4.6))):                 # flanking the open (north) side of the zone
    wd_, fo_ = a_olive(5 + j_)
    x, y = 4.479 + PU_[0] * u + PV_[0] * v, 1.156 + PU_[1] * u + PV_[1] * v
    inst(wd_, f'Olive_tree_{j_ + 1}', (x, y, TER), _ang, 'Planting'); inst(fo_, f'Olive_foliage_{j_ + 1}', (x, y, TER), _ang, 'Planting')
print('rev 8.8 majlis zone ok', nz_)
