"""rev. 8.9 (owner ref 2026-11-05, "коридорчик со входа"): the entrance corridor becomes a velvet tent-tunnel
  * hidden frame: black SHS 60x60 posts behind the drapes, 60x60 side rails + cross beams at +2.84..2.90
  * full-height rust / copper velvet walls (pleated, on a curtain track under the rails), hem on the floor
  * dense layered swag ceiling: lengthwise swags on top, crossing diagonals under them, transverse swags along every beam,
    gold rosettes + tassels at the gathers (all fabric, FR-treated velvet)
  * layered Persian rugs over a Malayer runner
  * ribbed terracotta amphora clusters at the far (dining) end, both sides
  * black iron floor candlesticks (0.6 / 0.9 / 1.2 m) with LED pillar candles in groups near the entrance; warm light
Replaces the arches, sagging ceiling, museum niches, khums, old swags/rugs/jars/candles of rev. 7-8.2."""
_rm('Corridor_arch', 'Corridor_velvet_ceiling', 'Corridor_niche', 'Corridor_khum', 'Corridor_swag', 'Corridor_rug', 'Corridor_amphora',
    'Corridor_candle', 'corridor_curtain', 'Corridor_runner')

def velvet_mat(name, base, tint):
    if name in bl._mats: return bl._mats[name]
    mm = bpy.data.materials.new(name); mm.use_nodes = True; N = mm.node_tree.nodes; Lk = mm.node_tree.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = 0.72
    b.inputs['Sheen Weight'].default_value = 1.0; b.inputs['Sheen Tint'].default_value = (*tint, 1); b.inputs['Sheen Roughness'].default_value = 0.35
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6.0; nz.inputs['Detail'].default_value = 4
    Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (*[c * 0.75 for c in base], 1); cr.color_ramp.elements[1].color = (*[min(1, c * 1.2) for c in base], 1)
    Lk.new(nz.outputs['Fac'], cr.inputs['Fac']); Lk.new(cr.outputs['Color'], b.inputs['Base Color'])
    bl._mats[name] = mm; return mm
V89 = dict(rust=velvet_mat('velvet_rust', (0.2, 0.055, 0.022), (1.0, 0.55, 0.3)),
           copper=velvet_mat('velvet_copper', (0.28, 0.095, 0.03), (1.0, 0.65, 0.4)),
           wine=velvet_mat('velvet_wine89', (0.15, 0.022, 0.028), (1.0, 0.5, 0.45)),
           ochre=velvet_mat('velvet_ochre', (0.36, 0.19, 0.04), (1.0, 0.8, 0.5)),
           steel=mat('steel_black_matt', (0.02, 0.02, 0.02), rough=0.6),
           iron=mat('iron_black_satin', (0.025, 0.022, 0.02), rough=0.38, metal=0.6),
           gold=m['brass'])
for k_, f_ in (('persian', 'rug_persian.png'), ('bukhara', 'rug_bukhara.png')):
    X['rug_' + k_] = uvmat(f'rug_{k_}_uv', f_); pile_shader(X['rug_' + k_])

e0, e1 = D['ent']; t0, t1 = D['tun']                       # 15.55 / 18.05, 7.70 / 10.50
YC = (e0 + e1) / 2
ZB, ZT = TER + 2.84, TER + 2.90                              # frame rails
PX = [t0 + 0.03, t0 + (t1 - t0) / 3, t0 + 2 * (t1 - t0) / 3, t1 - 0.22]   # last one clear of the pishtaq plinth   # post / cross-beam centres
YS, YN = e0 + 0.04, e1 - 0.04                                # post centre lines (behind the drapes)
# ---------------------------------------------------------------- 1. hidden frame
mb = MB(); S_ = V89['steel']
for x in PX:
    for y in (YS, YN): mb.box(x - 0.03, y - 0.03, TER, x + 0.03, y + 0.03, ZB, S_)
    mb.box(x - 0.03, YS - 0.03, ZB, x + 0.03, YN + 0.03, ZT, S_)                       # cross beam
for y in (YS, YN): mb.box(t0, y - 0.03, ZB, t1, y + 0.03, ZT, S_)                       # side rails
for x in PX:
    for y in (YS, YN): mb.box(x - 0.07, y - 0.03, TER, x + 0.07, y + 0.03, TER + 0.008, S_)   # base plates 140x60 (2 x M10 anchors along the wall)
inst(mb.mesh('Corridor_frame'), 'Corridor_frame', (0, 0, 0), 0, 'Corridor')

# ---------------------------------------------------------------- 2. full-height velvet walls on a track
for nm, yb_, sg in (('S', e0 + 0.09, 1), ('N', e1 - 0.09, -1)):          # back face of the drape, sg = towards the aisle
    n_ = int((t1 - t0) / 0.01); front = []
    for j in range(n_ + 1):
        x = t0 + (t1 - t0) * j / n_
        front.append((x, yb_ + sg * (0.035 + 0.016 * math.sin(2 * math.pi * (x - t0) / 0.1) + 0.009 * math.sin(2 * math.pi * (x - t0) / 0.37 + 1.3))))   # irregular pleats
    poly = [(t0, yb_), (t1, yb_)] + front[::-1] if sg > 0 else front + [(t1, yb_), (t0, yb_)]
    mb = MB(); mb.extrude(poly, TER, ZB - 0.035, V89['rust'])                                # hem on the floor
    yr = yb_ + sg * 0.035
    mb.rod((t0 + 0.01, yr, ZB - 0.02), (t1 - 0.01, yr, ZB - 0.02), 0.015, V89['steel'], 12)             # curtain track (hidden by the swags)
    for x in PX: mb.box(x - 0.015, min(yr, YS + 0.03 if sg > 0 else YN - 0.03), ZB - 0.02, x + 0.015, max(yr, YS + 0.03 if sg > 0 else YN - 0.03), ZB, V89['steel'])
    inst(mb.mesh(f'Corridor_velvet_wall_{nm}'), f'Corridor_velvet_wall_{nm}', (0, 0, 0), 0, 'Corridor')
DS, DN = e0 + 0.09 + 0.06, e1 - 0.09 - 0.06                 # aisle faces of the drapes (pleat crests)

# ---------------------------------------------------------------- 3. dense layered swag ceiling
def swag3(b, p0, p1, sag, width, mm, wdir, folds=5, n=18, gather=0.07):
    """gathered velvet swag from p0 to p1 sagging `sag`; width laid along the horizontal unit vector wdir; ends gathered"""
    rows = []; wd = Vector((wdir[0], wdir[1], 0.0))
    for k in range(n + 1):
        t = k / n; c = Vector(p0).lerp(Vector(p1), t); c.z -= sag * math.sin(math.pi * t)
        w = gather + (width - gather) * math.sin(math.pi * t) ** 0.7; row = []
        for j in range(folds * 2 + 1):
            u = -w / 2 + w * j / (folds * 2); q = c + wd * u; row.append((q.x, q.y, q.z + (0.03 if j % 2 else 0.0) * math.sin(math.pi * t) ** 0.5))
        rows.append(row)
    b.sheet(rows, mm, 0.006, picture=False)
def tassel(b, x, y, z, L=0.24):
    b.lathe(x, y, z - 0.07, [(0.0, 0.0), (0.03, 0.0), (0.035, 0.03), (0.02, 0.06), (0.012, 0.07), (0.0, 0.07)], V89['gold'], 16)   # rosette knot
    b.lathe(x, y, z - L, [(0.0, 0.0), (0.028, 0.0), (0.022, L - 0.12), (0.01, L - 0.07), (0.0, L - 0.07)], V89['ochre'], 16)        # fringe
mb = MB(); ZE = ZB - 0.006
cols = [V89['rust'], V89['wine'], V89['copper'], V89['wine'], V89['rust']]
for i_, (xa, xb_) in enumerate(zip(PX[:-1], PX[1:])):
    x0, x1 = xa + 0.035, xb_ - 0.035
    # layer 1 (top): seven lengthwise swags, overlapping, beam to beam
    for j_, y in enumerate([DS + 0.3 + (DN - DS - 0.6) * j / 6 for j in range(7)]):
        swag3(mb, (x0, y, ZE - 0.01 * (j_ % 2)), (x1, y, ZE - 0.01 * (j_ % 2)), 0.15 + 0.03 * (j_ % 2), 0.56, cols[(j_ + i_) % 5], (0, 1), folds=6)
    # mid-bay transverse swag
    xm = (x0 + x1) / 2
    swag3(mb, (xm, DS + 0.02, ZE - 0.1), (xm, DN - 0.02, ZE - 0.1), 0.42, 0.34, V89['copper'], (1, 0), folds=4)
    # layer 2: crossing diagonals
    swag3(mb, (x0, DS + 0.25, ZE - 0.05), (x1, DN - 0.25, ZE - 0.05), 0.3, 0.6, V89['copper'] if i_ % 2 else V89['wine'], (0, 1))
    swag3(mb, (x0, DN - 0.25, ZE - 0.08), (x1, DS + 0.25, ZE - 0.08), 0.27, 0.58, V89['ochre'], (0, 1))
# layer 3 (lowest): a transverse swag along every cross beam, wall to wall
for i_, x in enumerate(PX):
    xx = x + (0.05 if i_ == 0 else -0.05 if i_ == 3 else 0.0)
    swag3(mb, (xx, DS + 0.02, ZE - 0.12), (xx, DN - 0.02, ZE - 0.12), 0.34, 0.3 if 0 < i_ < 3 else 0.2, V89['wine'] if i_ % 2 else V89['rust'], (1, 0), folds=4)
    for y in (DS + 0.04, DN - 0.04): tassel(mb, x, y, ZE - 0.1, 0.5)                     # long tassels where the swag meets the wall
    if 0 < i_ < 3: tassel(mb, x, YC, ZE - 0.12 - 0.34 + 0.02, 0.22)                      # tassel at the low point of the swag
# flat velvet tent ceiling hides the frame + roof; pleated pelmets cover the track along both walls
mb.box(t0, DS, ZB - 0.004, t1, DN, ZB, V89['wine'])
for y0_, y1_ in ((DS + 0.004, DS + 0.03), (DN - 0.03, DN - 0.004)):
    pts = [(t0 + (t1 - t0) * j / 200, 0.0) for j in range(201)]
    sg_ = 1 if y0_ < YC else -1; yb0 = y0_ if sg_ > 0 else y1_
    poly = [(t0, yb0), (t1, yb0)] + [(x, yb0 + sg_ * (0.012 + 0.012 * math.sin(2 * math.pi * (x - t0) / 0.08))) for x, _ in pts][::-1]
    if sg_ < 0: poly = poly[::-1]
    mb.extrude(poly, ZB - 0.2, ZB - 0.004, V89['wine'])
    mb.box(t0, yb0 + sg_ * 0.024 if sg_ > 0 else yb0 - 0.03, ZB - 0.215, t1, yb0 + sg_ * 0.03 if sg_ > 0 else yb0 - 0.024, ZB - 0.2, V89['gold'])   # gold braid
inst(mb.mesh('Corridor_swag_ceiling'), 'Corridor_swag_ceiling', (0, 0, 0), 0, 'Corridor')

# ---------------------------------------------------------------- 4. layered rugs: Malayer runner + three Persian rugs on top
RUGS_ = []
def rug(name, cx, cy, L, W, ang, mm, layer):
    mb = MB(); zb = TER + 0.008 * layer
    fs = mb.picture_box(-L / 2, -W / 2, zb, L / 2, W / 2, zb + 0.008, mm, '+z')
    for v in {v for f in fs for v in f.verts}:
        x_, y_ = v.co.x, v.co.y; v.co.x, v.co.y = cx + x_ * math.cos(ang) - y_ * math.sin(ang), cy + x_ * math.sin(ang) + y_ * math.cos(ang)
    inst(mb.mesh(name), name, (0, 0, 0), 0, 'Corridor'); RUGS_.append((cx, cy, ang, L / 2, W / 2, zb + 0.008))
rug('Corridor_rug_base', (t0 + t1) / 2, YC, t1 - t0 - 0.04, DN - DS - 0.04, 0.0, X['oldrug_uv'], 0)     # wall-to-wall old Persian
rug('Corridor_rug_runner', (t0 + t1) / 2, YC, t1 - t0 - 0.1, 0.9, 0.0, X['runner_uv'], 1)
rug('Corridor_rug_1', 8.3, YC + 0.03, 1.15, 1.15, 0.035, X['rug_persian'], 2)
rug('Corridor_rug_2', 9.25, YC - 0.04, 1.0, 1.2, -0.05, X['carpet2'], 3)
rug('Corridor_rug_3', 10.05, YC + 0.02, 0.8, 1.15, 0.04, X['rug_bukhara'], 2)
ZF = TER + 0.008                                     # side objects stand on the base rug
RUGY = (YC - 0.68, YC + 0.68)                                 # rug band (incl. rotation) — side objects stay outside it

# ---------------------------------------------------------------- 5. ribbed terracotta amphorae (far end, both sides)
@cached
def a_amph89(h, kind):
    """thrown terracotta amphora with real horizontal ribs (5 mm, every 35 mm) on the belly; origin = bottom centre"""
    s = h / 0.9; prof = []
    base = [(0.0, 0.0), (0.075, 0.0), (0.085, 0.02), (0.16, 0.12), (0.2, 0.3), (0.205, 0.42), (0.18, 0.56), (0.12, 0.68), (0.075, 0.76),
            (0.07, 0.83), (0.09, 0.87), (0.09, 0.9), (0.0, 0.9)] if kind == 'tall' else \
           [(0.0, 0.0), (0.07, 0.0), (0.08, 0.02), (0.18, 0.15), (0.21, 0.32), (0.19, 0.5), (0.13, 0.62), (0.085, 0.68), (0.08, 0.74), (0.095, 0.77), (0.0, 0.77)]
    zs = [z for r, z in base]
    def R(z):
        for (r0, z0), (r1, z1) in zip(base[:-1], base[1:]):
            if z0 <= z <= z1 and z1 > z0: return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
        return base[-2][0]
    zmax_rib = base[-5][1] if kind == 'tall' else base[-4][1]
    prof.append(base[0]); prof.append(base[1]); prof.append(base[2])
    z = base[2][1] + 0.01
    while z < zmax_rib:
        prof.append((R(z), z)); prof.append((R(z + 0.012) + 0.007, z + 0.012)); prof.append((R(z + 0.028) + 0.007, z + 0.028)); z += 0.04
    prof += [p for p in base if p[1] >= zmax_rib and p[0] > 0] + [base[-1]]
    prof = [(r * s, z * s) for r, z in prof]
    b = MB(); b.lathe(0, 0, 0, prof, TC['orange'] if kind == 'tall' else TC['rust'], 40)
    return b.mesh(f'Amphora89_{kind}_{int(h * 100)}')
AMPH = [(0.45, 'tall'), (1.0, 'tall'), (0.72, 'round'), (0.5, 'round')]          # packed along each wall from the dining end
na = 0
for side, yw in ((1, DS), (-1, DN)):
    x = t0 + 0.05
    for h, kind in (AMPH if side > 0 else AMPH[::-1][:1] + AMPH[:1] + AMPH[1:3]):     # the two sides mirror loosely, not exactly
        rmax = (0.205 * h / 0.9) if kind == 'tall' else (0.21 * h / 0.77)
        x += rmax; na += 1
        inst(a_amph89(h, kind), f'Corridor_amphora_{na}', (x, yw + side * (rmax + 0.02), ZF), 0.7 * na, 'Corridor')
        x += rmax + 0.02
    print('amphora run ends at', round(x, 2))

# ---------------------------------------------------------------- 6. black iron floor candlesticks with LED pillar candles
@cached
def a_candlestick(H):
    """forged iron floor candlestick: round base 240, turned collar, 20 mm stem, drip dish 150, LED pillar candle 90 x 150"""
    b = MB(); I = V89['iron']
    b.lathe(0, 0, 0, [(0.0, 0.0), (0.12, 0.0), (0.12, 0.012), (0.07, 0.03), (0.03, 0.06), (0.0, 0.06)], I, 32)
    b.lathe(0, 0, 0.06, [(0.0, 0.0), (0.025, 0.0), (0.03, 0.03), (0.018, 0.06), (0.0, 0.06)], I, 24)
    b.cyl(0, 0, 0.12, H - 0.03, 0.01, I, 16)
    b.lathe(0, 0, H - 0.03, [(0.0, 0.0), (0.02, 0.0), (0.075, 0.02), (0.075, 0.03), (0.0, 0.03)], I, 32)
    b.cyl(0, 0, H, H + 0.15, 0.045, X82['candle'], 24); b.cyl(0, 0, H + 0.15, H + 0.154, 0.04, X82['flame'], 24)
    return b.mesh(f'Candlestick_{int(H * 100)}')
nc = 0
for gx in (9.5, 10.16):
    for side, yw in ((1, DS), (-1, DN)):
        for dx, dy, H in ((-0.2, 0.15, 1.2), (0.2, 0.15, 0.9), (0.0, 0.33, 0.6)):
            x, y = gx + dx, yw + side * dy; nc += 1
            inst(a_candlestick(H), f'Corridor_candlestick_{nc}', (x, y, ZF), 0, 'Corridor')
            L_ = bpy.data.lights.new('cand89', 'POINT'); L_.energy = 8; L_.color = (1.0, 0.6, 0.28); L_.shadow_soft_size = 0.04
            lo_ = bpy.data.objects.new('Corridor_candle_light', L_); lo_.location = (x, y, ZF + H + 0.22); coll('Lights').objects.link(lo_)
L_ = bpy.data.lights.new('corr_fill', 'POINT'); L_.energy = 30; L_.color = (1.0, 0.55, 0.3); L_.shadow_soft_size = 0.4
lo_ = bpy.data.objects.new('Corridor_fill_light', L_); lo_.location = ((t0 + t1) / 2, YC, TER + 2.1); coll('Lights').objects.link(lo_)
print('rev 8.9 corridor ok', na, nc)
