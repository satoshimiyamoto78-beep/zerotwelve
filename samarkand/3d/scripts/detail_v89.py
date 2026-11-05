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
    b.inputs['Sheen Weight'].default_value = 0.55; b.inputs['Sheen Tint'].default_value = (*tint, 1); b.inputs['Sheen Roughness'].default_value = 0.35
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6.0; nz.inputs['Detail'].default_value = 4
    Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (*[c * 0.75 for c in base], 1); cr.color_ramp.elements[1].color = (*[min(1, c * 1.2) for c in base], 1)
    Lk.new(nz.outputs['Fac'], cr.inputs['Fac'])
    lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.45
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; Lk.new(lw.outputs['Facing'], mx.inputs['Factor'])
    dk = N.new('ShaderNodeMix'); dk.data_type = 'RGBA'; dk.inputs['Factor'].default_value = 0.45; Lk.new(cr.outputs['Color'], dk.inputs[6]); dk.inputs[7].default_value = (0, 0, 0, 1)
    lt = N.new('ShaderNodeMix'); lt.data_type = 'RGBA'; lt.inputs['Factor'].default_value = 0.16; Lk.new(cr.outputs['Color'], lt.inputs[6]); lt.inputs[7].default_value = (*tint, 1)
    Lk.new(dk.outputs[2], mx.inputs[6]); Lk.new(lt.outputs[2], mx.inputs[7]); Lk.new(mx.outputs[2], b.inputs['Base Color'])   # dark face-on, glowing at grazing angles
    fb = N.new('ShaderNodeTexNoise'); fb.inputs['Scale'].default_value = 900.0; Lk.new(tc.outputs['Object'], fb.inputs['Vector'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.12; bp.inputs['Distance'].default_value = 0.001; Lk.new(fb.outputs['Fac'], bp.inputs['Height']); Lk.new(bp.outputs['Normal'], b.inputs['Normal'])
    bl._mats[name] = mm; return mm
V89 = dict(rust=velvet_mat('velvet_rust', (0.24, 0.07, 0.025), (1.0, 0.55, 0.3)),
           copper=velvet_mat('velvet_copper', (0.34, 0.13, 0.045), (1.0, 0.7, 0.42)),
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


# ================================================================ rev. 9.1 (owner: "посмотри ещё раз на референс")
# curtain portals at every frame bay (soft copper velvet drawn to the sides, tent-like pointed openings), heavy transverse swags,
# Persian rugs laid end to end down the path, low black candle lanterns on the floor, terracotta jar clusters at the far portal.
DS, DN = e0 + 0.18, e1 - 0.18                                  # aisle faces of the wall drapes (fold crests)
# ---------------------------------------------------------------- wall drapes: big soft folds
for nm, yb_, sg in (('S', e0 + 0.09, 1), ('N', e1 - 0.09, -1)):
    n_ = int((t1 - t0) / 0.01); front = []
    for j in range(n_ + 1):
        x = t0 + (t1 - t0) * j / n_
        front.append((x, yb_ + sg * (0.05 + 0.035 * math.cos(2 * math.pi * (x - t0) / 0.29) + 0.008 * math.sin(2 * math.pi * (x - t0) / 0.11 + 0.7))))
    poly = [(t0, yb_), (t1, yb_)] + front[::-1] if sg > 0 else front + [(t1, yb_), (t0, yb_)]
    mb = MB(); mb.extrude(poly, TER, ZB - 0.035, V89['copper'])
    yr = yb_ + sg * 0.035
    mb.rod((t0 + 0.01, yr, ZB - 0.02), (t1 - 0.01, yr, ZB - 0.02), 0.015, V89['steel'], 12)
    for x in PX: mb.box(x - 0.015, min(yr, YS + 0.03 if sg > 0 else YN - 0.03), ZB - 0.02, x + 0.015, max(yr, YS + 0.03 if sg > 0 else YN - 0.03), ZB, V89['steel'])
    inst(mb.mesh(f'Corridor_velvet_wall_{nm}'), f'Corridor_velvet_wall_{nm}', (0, 0, 0), 0, 'Corridor')

def swag3(b, p0, p1, sag, width, mm, wdir, folds=6, n=22, gather=0.06, depth=0.045):
    rows = []; wd = Vector((wdir[0], wdir[1], 0.0))
    for k in range(n + 1):
        t = k / n; c = Vector(p0).lerp(Vector(p1), t); c.z -= sag * math.sin(math.pi * t)
        w = gather + (width - gather) * math.sin(math.pi * t) ** 0.6; row = []
        for j in range(folds * 2 + 1):
            u = -w / 2 + w * j / (folds * 2); q = c + wd * u
            row.append((q.x, q.y, q.z + depth * (0.5 + 0.5 * math.cos(math.pi * j)) * math.sin(math.pi * t) ** 0.5 - depth * 0.5 * (u / max(w, 1e-3)) ** 2))
        rows.append(row)
    b.sheet(rows, mm, 0.006, picture=False)
def portal(b, xp, side, mm):
    """one curtain panel hung at x = xp from the wall (y = DS / DN) towards the centre; inner edge sweeps from 0.36 m at the floor
    to 0.25 m short of the centre line at the top (pointed tent opening), soft folds of +-50 mm in x"""
    yw = DS + 0.006 if side > 0 else DN - 0.006; ytop = YC - side * 0.25; Hz = ZB - 0.012 - TER
    rows = []; NZ, NY = 30, 14
    for k in range(NZ + 1):
        sz = k / NZ; z = TER + 0.002 + Hz * sz
        yin = yw + side * 0.36 + (ytop - yw - side * 0.36) * sz ** 2.2
        row = []
        for j in range(NY + 1):
            t = j / NY; y = yw + (yin - yw) * t
            dx = (0.05 - 0.02 * sz) * math.sin(2 * math.pi * 2.5 * t + 0.4 * side) * (0.4 + 0.6 * t)
            row.append((xp + dx, y, z))
        rows.append(row)
    b.sheet(rows, mm, 0.006, picture=False)
mb = MB(); ZE = ZB - 0.006
mb.box(t0, DS, ZB - 0.004, t1, DN, ZB, V89['wine'])                                       # tent ceiling (hides frame + roof)
for y0_, sg_ in ((DS + 0.004, 1), (DN - 0.004, -1)):                                     # pleated pelmet over the track
    poly = [(t0, y0_), (t1, y0_)] + [(t0 + (t1 - t0) * j / 200, y0_ + sg_ * (0.012 + 0.012 * math.sin(2 * math.pi * j / 200 * (t1 - t0) / 0.08))) for j in range(201)][::-1]
    mb.extrude(poly if sg_ > 0 else poly[::-1], ZB - 0.2, ZB - 0.004, V89['copper'])
cols = [V89['copper'], V89['rust'], V89['ochre'], V89['copper'], V89['wine']]
xs_ = [t0 + 0.1 + k * 0.2 for k in range(int((t1 - t0 - 0.2) / 0.2) + 1)]
for k, x in enumerate(xs_):                                                               # heavy transverse swags, wall to wall, layered
    swag3(mb, (x, DS + 0.03, ZE - 0.012 * (k % 3)), (x, DN - 0.03, ZE - 0.012 * (k % 3)), (0.34, 0.5, 0.42)[k % 3], 0.42, cols[k % 5], (1, 0))
for i_, xp in enumerate(PX):
    for side in (1, -1): portal(mb, xp, side, V89['copper'] if i_ % 2 else V89['rust'])
inst(mb.mesh('Corridor_swag_ceiling'), 'Corridor_swag_ceiling', (0, 0, 0), 0, 'Corridor')

# ---------------------------------------------------------------- rugs end to end down the path
X['rug_persian_navy'] = uvmat('rug_persian_navy_uv', 'rug_persian_navy.png'); pile_shader(X['rug_persian_navy'])
X['rug_old_crop'] = uvmat('rug_old_crop_uv', 'rug_oldpersian_crop.jpg'); pile_shader(X['rug_old_crop'])
def rug(name, cx, cy, L, W, ang, mm, layer):
    mb = MB(); zb = TER + 0.008 * layer
    fs = mb.picture_box(-L / 2, -W / 2, zb, L / 2, W / 2, zb + 0.008, mm, '+z')
    for v in {v for f in fs for v in f.verts}:
        x_, y_ = v.co.x, v.co.y; v.co.x, v.co.y = cx + x_ * math.cos(ang) - y_ * math.sin(ang), cy + x_ * math.sin(ang) + y_ * math.cos(ang)
    inst(mb.mesh(name), name, (0, 0, 0), 0, 'Corridor')
rug('Corridor_rug_1', 9.98, YC + 0.02, 0.95, 1.0, 0.03, X['rug_persian'], 0)
rug('Corridor_rug_2', 9.12, YC - 0.03, 1.0, 0.95, -0.045, X['rug_old_crop'], 1)
rug('Corridor_rug_3', 8.28, YC + 0.03, 0.95, 1.0, 0.05, X['rug_persian_navy'], 0)

# ---------------------------------------------------------------- terracotta jar clusters at the far portal
@cached
def a_jar91(h):
    b = MB(); s = h / 0.8; T_ = TC['orange']
    b.lathe(0, 0, 0, [(0.0, 0), (0.07 * s, 0), (0.09 * s, 0.03 * s), (0.19 * s, 0.25 * s), (0.2 * s, 0.4 * s), (0.15 * s, 0.6 * s), (0.08 * s, 0.7 * s), (0.065 * s, 0.75 * s),
                      (0.085 * s, 0.79 * s), (0.08 * s, 0.8 * s), (0.055 * s, 0.77 * s), (0.0, 0.74 * s)], T_, 32)
    for sg in (-1, 1): _curve(b, [(sg * 0.07 * s, 0, 0.72 * s), (sg * 0.13 * s, 0, 0.73 * s), (sg * 0.16 * s, 0, 0.66 * s), (sg * 0.155 * s, 0, 0.6 * s)], 0.012 * s, 0.012 * s, T_, 8)
    return b.mesh(f'Jar91_{int(h * 100)}')
nj = 0
for side in (1, -1):
    for x, dy, h in ((8.30, 0.02 + 0.2, 0.8), (7.96, 0.02 + 0.1375, 0.55), (8.05, 0.43, 0.38)):
        nj += 1; inst(a_jar91(h), f'Corridor_amphora_{nj}', (x, YC - side * (YC - DS - dy) if side > 0 else YC + (DN - dy - YC), TER), 0.9 * nj + 0.3, 'Corridor')
# ---------------------------------------------------------------- low black candle lanterns along the floor
@cached
def a_floorlantern(H):
    """black powder-coated steel tube d 150, open top, LED pillar candle inside glowing up the tube"""
    b = MB(); I = V89['iron']
    b.ring(0, 0, 0, [(0.065, 0.0), (0.075, 0.0), (0.075, H), (0.065, H)], I, 32)
    b.cyl(0, 0, 0.0, 0.012, 0.065, I, 32)
    b.cyl(0, 0, H - 0.17, H - 0.03, 0.045, X82['candle'], 24); b.cyl(0, 0, H - 0.03, H - 0.026, 0.04, X82['flame'], 24)
    b.lathe(0, 0, 0.012, [(0.0, 0.0), (0.045, 0.0), (0.045, H - 0.17 - 0.012), (0.0, H - 0.17 - 0.012)], I, 16)    # stand for the candle
    return b.mesh(f'Floor_lantern_{int(H * 100)}')
nl = 0
for side in (1, -1):
    for x, H in ((8.92, 0.42), (9.3, 0.34), (9.86, 0.46), (10.12, 0.36)):
        y = DS + 0.1 if side > 0 else DN - 0.1; nl += 1
        inst(a_floorlantern(H), f'Corridor_lantern_{nl}', (x, y, TER), 0, 'Corridor')
        L_ = bpy.data.lights.new('lant91', 'POINT'); L_.energy = 7; L_.color = (1.0, 0.58, 0.26); L_.shadow_soft_size = 0.05
        lo_ = bpy.data.objects.new('Corridor_candle_light', L_); lo_.location = (x, y, TER + H + 0.08); coll('Lights').objects.link(lo_)
L_ = bpy.data.lights.new('corr_fill', 'POINT'); L_.energy = 25; L_.color = (1.0, 0.55, 0.3); L_.shadow_soft_size = 0.4
lo_ = bpy.data.objects.new('Corridor_fill_light', L_); lo_.location = ((t0 + t1) / 2, YC, TER + 2.0); coll('Lights').objects.link(lo_)
print('rev 9.1 corridor ok', nj, nl)
