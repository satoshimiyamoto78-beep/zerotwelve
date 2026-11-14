"""rev. 9.2 (owner: "каркас висит в воздухе — как это будет работать?"): every roof member now has a load path to the ground.
STRUCTURE (to be verified by the structural engineer; loads: Klip-Lok + purlins ~0.25 kPa, services 0.1, live 0.25, typhoon uplift):
  1. facade line x = 0: PFC 180 ledger hung from the F2 balcony slab soffit (z 3.85) with 100x12 hanger plates @1200 on 150x150x12
     anchor plates, 4 x M12 chemical anchors each; IPE 300 beams bolted to it with 100x10 fin plates (4 x M16)
  2. street line: SHS 150 columns on 350x350x20 base plates (4 x M20 cast-in anchors, 30 mm grout) and 250x250x20 cap plates;
     the two entrance columns are cast inside the portal pylons
  3. dome: the IPE 300 ring girder sits on four SHS 150 columns at the beam / ring junctions (chartaq: four piers carry the dome),
     walnut-cased with brass bands, base + cap plates
  4. south lot line west of the pergola: IPE 200 edge beam on two SHS 100 posts (clay pilasters) carries the purlin ends
     (they were cantilevering 3-4 m) and the W trimmer
  5. pocket over the kids corner / staff passage (x -7.25..0): IPE 200 edge beam on three SHS 120 columns along the passage,
     PFC 200 wall ledger on the hall's south wall (M16 chemical anchors @600), seven C200 purlins @1000 between them
  6. aivan: the coffered ceiling hangs from the purlins on M10 drop rods (top cleat + bottom nut plate) @~1.2 m; the arcade beam is
     tied to every roof beam it passes under with a 100x8 angle cleat (lateral restraint only, no roof load on the timber)"""
import bmesh
STL = m['bronze']; PLT = m['steel']; NUT = m['steel']
def prism8(name, quad, zt_fn, dep, mm, cname):
    """closed prism over a 4-point footprint whose top follows zt_fn(x, y) and whose bottom is dep below it"""
    bm = bmesh.new()
    a = [bm.verts.new((x, y, zt_fn(x, y) - dep)) for x, y in quad]; b = [bm.verts.new((x, y, zt_fn(x, y))) for x, y in quad]
    bm.faces.new(list(reversed(a))); bm.faces.new(b)
    for i in range(4): bm.faces.new((a[i], a[(i + 1) % 4], b[(i + 1) % 4], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return new_obj(name, bm, [mm], cname)
def plates(name, x, y, zb, sz, tz, cname, nuts=True, zcap=None, csz=0.25):
    """base plate (sz square, tz thick) at zb with 4 anchor nuts; optional cap plate (csz) ending at zcap"""
    bl_ = [(x - sz / 2, y - sz / 2, zb, x + sz / 2, y + sz / 2, zb + tz)]
    if zcap is not None: bl_.append((x - csz / 2, y - csz / 2, zcap - 0.02, x + csz / 2, y + csz / 2, zcap))
    boxes(name, bl_, PLT, cname)
    if nuts:
        for dx in (-1, 1):
            for dy in (-1, 1): cylinder(name + '_nut', x + dx * (sz / 2 - 0.05), y + dy * (sz / 2 - 0.05), zb + tz, zb + tz + 0.018, 0.016, NUT, cname, n=6)

# ---------------------------------------------------------------- 1. facade ledger hangers + beam fin plates
SOF = 3.85; LT = top(0) - 0.05
for k in range(int((37.1 - 4.1 - 0.3) / 1.2) + 1):
    y = 4.35 + 1.2 * k
    if y > 36.9: break
    boxes('Ledger_hanger', [(0.03, y - 0.006, LT, 0.15, y + 0.006, SOF - 0.012), (0.015, y - 0.075, SOF - 0.012, 0.165, y + 0.075, SOF)], PLT, 'Roof_structure')
for y, xe in D['beams']:
    if y < 4.1: continue
    zt = top(0.18) - 0.25 - 0.0107
    boxes('Beam_fin_plate', [(0.18, y + 0.0036, zt - 0.25, 0.29, y + 0.0136, zt - 0.03)], PLT, 'Roof_structure')

# ---------------------------------------------------------------- 2. street columns: plates; entrance columns inside the pylons
for x, y in D['cols']:
    if y < 0.6 and x < 0: continue
    zt = top(x) - 0.55
    if any(a <= y <= b for a, b in ((D['ent'][0] - 0.7, D['ent'][0]), (D['ent'][1], D['ent'][1] + 0.7))):
        boxes(f'column_portal_{y:.1f}', [(x - 0.075, y - 0.075, TER, x + 0.075, y + 0.075, zt)], STL, 'Roof_structure'); continue
    plates('Column_plates', x, y, TER, 0.35, 0.02, 'Roof_structure', zcap=zt)

# ---------------------------------------------------------------- 3. four columns under the dome ring girder
WD = XW['wd']
for d in D.get('domes', []):
    cx, cy = d['c']; Rg = RING_R(d)
    for yb in (18.3, 21.35):
        dy = yb - cy
        if abs(dy) >= Rg: continue
        h = math.sqrt(Rg ** 2 - dy ** 2)
        for sx in (-1, 1):
            x, y = cx + sx * h, yb; zt = top(x) - 0.25 - 0.3
            boxes('Dome_column', [(x - 0.075, y - 0.075, TER + 0.02, x + 0.075, y + 0.075, zt - 0.02)], STL, 'Roof_structure')
            plates('Dome_column_plates', x, y, TER, 0.22, 0.02, 'Roof_structure', nuts=False, zcap=zt, csz=0.22)
            mb = MB(); z0, z1 = TER + 0.02, zt - 0.02
            for (a0, b0, a1, b1) in ((-0.115, -0.115, 0.115, -0.085), (-0.115, 0.085, 0.115, 0.115), (-0.115, -0.085, -0.085, 0.085), (0.085, -0.085, 0.115, 0.085)):
                mb.box(x + a0, y + b0, z0, x + a1, y + b1, z1, WD)                                                   # walnut casing
            for zb in (TER + 0.12, TER + 1.1, zt - 0.3):
                mb.box(x - 0.125, y - 0.125, zb, x + 0.125, y + 0.125, zb + 0.03, m['brass'], 0.004)                # brass bands
            inst(mb.mesh('Dome_column_casing'), f'Dome_column_casing_{sx}_{yb:.0f}', (0, 0, 0), 0, 'Roof_structure')

# ---------------------------------------------------------------- 4. south lot line: IPE 200 edge beam on two SHS 100 posts
A_ = (-0.1675, 0.0); ANG_ = math.atan2(3.3892, 13.4586 + 0.1675); PU_ = (math.cos(ANG_), math.sin(ANG_)); PV_ = (-math.sin(ANG_), math.cos(ANG_))
def W(u, v): return (A_[0] + PU_[0] * u + PV_[0] * v, A_[1] + PU_[1] * u + PV_[1] * v)
VB = 0.12                                            # beam / post centre line just in front of the clay skin
bt = lambda x, y: top(x) - 0.25                               # purlin underside = edge beam top
for n_ in ('photo_plant', 'photo_plant_soil'):                # planter bed ends 0.25 short of the east post
    o_ = bpy.data.objects.get(n_)
    if o_:
        bpy.context.view_layer.update(); vs = [o_.matrix_world @ v.co for v in o_.data.vertices]
        us = [(v.x - A_[0]) * PU_[0] + (v.y - A_[1]) * PU_[1] for v in vs]; u0, u1 = min(us), max(us)
        if u1 > 4.25:
            k_ = (4.25 - u0) / (u1 - u0)
            for v in o_.data.vertices:
                w_ = o_.matrix_world @ v.co; uu = (w_.x - A_[0]) * PU_[0] + (w_.y - A_[1]) * PU_[1]; du = (uu - u0) * (k_ - 1)
                w_.x += PU_[0] * du; w_.y += PU_[1] * du; v.co = o_.matrix_world.inverted() @ w_
for nm, (ua, ub) in (('Edge_beam_S', (0.05, 4.62)),):
    q = [W(ua, VB - 0.05), W(ub, VB - 0.05), W(ub, VB + 0.05), W(ua, VB + 0.05)]
    prism8(nm, q, bt, 0.2, STL, 'Roof_structure')
CLAY_ = bl._mats.get('clay_plaster_relief', m['white'])
for i_, up in enumerate((0.15, 4.5)):
    x, y = W(up, VB); zt = bt(x, y) - 0.2
    q = [W(up - 0.05, VB - 0.05), W(up + 0.05, VB - 0.05), W(up + 0.05, VB + 0.05), W(up - 0.05, VB + 0.05)]
    prism8(f'Edge_post_S{i_ + 1}', q, lambda xx, yy, z_=zt: z_, zt - TER, STL, 'Roof_structure')
    mb = MB()                                                                                 # clay pilaster casing round the post
    for (a0, a1, b0, b1) in ((-0.1, 0.1, 0.047, 0.067), (-0.1, 0.1, 0.175, 0.195), (-0.1, -0.06, 0.067, 0.175), (0.06, 0.1, 0.067, 0.175)):
        mb.box(up + a0, b0, TER, up + a1, b1, TER + 2.35, CLAY_, 0.004)
    inst(mb.mesh('Edge_pilaster'), f'Edge_pilaster_S{i_ + 1}', (A_[0], A_[1], 0.0), ANG_, 'Street_facade')

# ---------------------------------------------------------------- 5. pocket roof over the kids corner / staff passage
PY = 0.15
prism8('Edge_beam_pocket', [(-7.25, PY - 0.05), (-0.25, PY - 0.05), (-0.25, PY + 0.05), (-7.25, PY + 0.05)], bt, 0.2, STL, 'Roof_structure')
for x in (-7.05, -3.7, -0.35):
    zt = top(x) - 0.45
    boxes('Pocket_column', [(x - 0.06, PY - 0.06, TER + 0.02, x + 0.06, PY + 0.06, zt - 0.02)], STL, 'Roof_structure')
    plates('Pocket_column_plates', x, PY, TER, 0.3, 0.02, 'Roof_structure', zcap=zt, csz=0.2)
prism8('Wall_ledger_pocket', [(-7.25, 3.98), (0.0, 3.98), (0.0, 4.1), (-7.25, 4.1)], bt, 0.2, STL, 'Roof_structure')
for k in range(7):
    x = -6.75 + k * 1.0
    boxes('Pocket_purlin', [(x - 0.04, PY - 0.05, top(x) - 0.25, x + 0.04, 4.1, top(x) - 0.05)], STL, 'Roof_structure')

# ---------------------------------------------------------------- 6. aivan: ceiling drop rods + arcade-beam tie cleats
from mathutils.bvhtree import BVHTree
ce = bpy.data.objects.get('Aivan_ceiling'); nr = 0
if ce:
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); T = BVHTree.FromObject(ce, dg); inv = ce.matrix_world.inverted()
    cs = [ce.matrix_world @ Vector(c) for c in ce.bound_box]; ya, yb_ = min(c.y for c in cs), max(c.y for c in cs)
    bl_ = []
    for x, y0, y1 in D['purlins']:
        if x > 3.3: continue
        y = max(ya, y0) + 0.3
        while y < min(yb_, y1) - 0.2:
            if all(abs(y - by) > 0.15 for by, _ in D['beams']):
                zp = top(x) - 0.25; o_ = inv @ Vector((x, y, zp - 0.001)); hit = T.ray_cast(o_, inv.to_3x3() @ Vector((0, 0, -1)), 0.6)
                if hit[0] is not None:
                    zh = (ce.matrix_world @ hit[0]).z
                    if zp - zh > 0.03:
                        cylinder('Aivan_ceiling_rod', x, y, zh, zp - 0.008, 0.005, PLT, 'Aivan', n=8)
                        bl_.append((x - 0.04, y - 0.025, zp - 0.008, x + 0.04, y + 0.025, zp)); nr += 1
            y += 1.2
    if bl_: boxes('Aivan_ceiling_rod_cleat', bl_, PLT, 'Aivan')
ab = bpy.data.objects.get('Khiva_arcade_beam')
if ab:
    cs = [ab.matrix_world @ Vector(c) for c in ab.bound_box]; xa_, xb2_ = min(c.x for c in cs), max(c.x for c in cs); za_ = max(c.z for c in cs)
    for y, xe in D['beams']:
        if min(c.y for c in cs) < y < max(c.y for c in cs):
            zb_ = top((xa_ + xb2_) / 2) - 0.55
            if zb_ - za_ > 0.005: boxes('Aivan_tie_cleat', [(xa_ + 0.02, y - 0.05, za_, xb2_ - 0.02, y + 0.05, zb_)], PLT, 'Aivan')
print('rev 9.2 structure ok, aivan rods', nr)
