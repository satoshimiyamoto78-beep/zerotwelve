"""rev. 9.3 (owner 2026-11-05, mangal):
  * the SAMARKAND sign on the dining side of the hood is removed (street-side letters stay)
  * hood walls: real brick slips 240x60 with recessed lime joints and glazed bannai headers, a frieze of real 100 mm glazed tiles framed in copper,
    copper drip edge; flue stack clad in brick
  * the pass towards the plaza seats becomes a chilled display counter: walnut base with a majolica front, stainless cold deck,
    angled front glass + top glass + end glass, LED strip; raw skewers (lamb, lula, chicken), marinated vegetables, onion,
    tomatoes, greens, lepyoshka and samsa on enamel trays — guests choose, the cook grills it behind"""
_rm('Mangal_signboard', 'Logo_Samarkand_W', 'Logo_subtitle_W', 'pass', 'glass')
import random as _rnd
CU = X['copper'] if 'copper' in X else m['brass']
MORTAR = mat('mortar_lime', (0.62, 0.56, 0.48), rough=0.95, bump=0.4)
BRK = [terracotta(f'brick_{k}', c) for k, c in enumerate(((0.58, 0.32, 0.2), (0.52, 0.28, 0.17), (0.62, 0.36, 0.22), (0.47, 0.25, 0.15)))]
GLZ = [mat('glaze_turq', (0.05, 0.45, 0.5), rough=0.15, coat=0.8), mat('glaze_cobalt', (0.04, 0.12, 0.45), rough=0.15, coat=0.8)]
TILE = [mat('tile_cobalt', (0.03, 0.1, 0.42), rough=0.12, coat=0.9), mat('tile_white', (0.88, 0.86, 0.8), rough=0.12, coat=0.9),
        mat('tile_turq', (0.06, 0.5, 0.52), rough=0.12, coat=0.9), mat('tile_ochre', (0.75, 0.52, 0.12), rough=0.15, coat=0.8)]
def brick_face(b, axis, c, s, a0, a1, z0, z1, rnd, glaze=True):
    """real brick slips 240 x 60 x 20, 12 mm recessed lime joints, stretcher bond; bannai: glazed headers in a diamond lattice.
    axis 'x': face plane x = c (bricks grow towards s), runs along y a0..a1; axis 'y': plane y = c, runs along x"""
    BL, BH, J = 0.24, 0.06, 0.012; row = 0; z = z0
    while z + BH <= z1 + 1e-6:
        off = (BL + J) / 2 if row % 2 else 0.0; u = a0 - off
        k = 0
        while u < a1:
            ua, ub = max(a0, u), min(a1, u + BL)
            if ub - ua > 0.03:
                diag = glaze and (k + row // 2) % 4 == 0 and row % 2 == 0
                mm = GLZ[(k // 4) % 2] if diag else BRK[rnd.randrange(4)]
                d = 0.02 + rnd.uniform(-0.002, 0.002)
                if axis == 'x': b.box(min(c, c + s * d), ua, z, max(c, c + s * d), ub, z + BH, mm, 0.002)
                else: b.box(ua, min(c, c + s * d), z, ub, max(c, c + s * d), z + BH, mm, 0.002)
            u += BL + J; k += 1
        z += BH + J; row += 1
def tile_band(b, axis, c, s, a0, a1, z0, z1, T=0.1, J=0.003):
    """glazed 100 mm tiles, 3 mm grout, cobalt/white/turquoise eight-point-star rhythm"""
    n = int((a1 - a0) / (T + J)); m0 = a0 + ((a1 - a0) - n * (T + J)) / 2; rows = int((z1 - z0) / (T + J))
    for i in range(n):
        for j in range(rows):
            ua, za = m0 + i * (T + J), z0 + j * (T + J)
            pat = ((i % 4) in (1, 2)) == ((j % 4) in (1, 2))
            mm = TILE[0] if pat else (TILE[2] if (i + j) % 2 else TILE[1])
            if axis == 'x': b.box(min(c, c + s * 0.012), ua, za, max(c, c + s * 0.012), ua + T, za + T, mm, 0.002)
            else: b.box(ua, min(c, c + s * 0.012), za, ua + T, max(c, c + s * 0.012), za + T, mm, 0.002)
o_ = bpy.data.objects.get('Mangal_hood_wall')
if o_:
    for i_ in range(len(o_.data.materials)): o_.data.materials[i_] = MORTAR
rnd_ = _rnd.Random(7); mb = MB(); HZ0, HZ1 = TER + 2.0, 3.32
brick_face(mb, 'x', 11.0, -1, 3.15, 8.05, HZ0, TER + 2.39, rnd_)                            # west face below the frieze
brick_face(mb, 'x', 11.0, -1, 3.15, 8.05, TER + 2.83, HZ1 - 0.01, rnd_)                     # above
brick_face(mb, 'y', 8.05, 1, 11.0, 12.13, HZ0, TER + 2.39, rnd_)
brick_face(mb, 'y', 8.05, 1, 11.0, 12.13, TER + 2.83, HZ1 - 0.01, rnd_)
tile_band(mb, 'x', 11.0, -1, 3.17, 8.03, TER + 2.415, TER + 2.81)
tile_band(mb, 'y', 8.05, 1, 11.02, 12.13, TER + 2.415, TER + 2.81)
for z in (TER + 2.39, TER + 2.81):                                                          # copper bands framing the frieze
    mb.box(10.97, 3.15, z, 11.0, 8.05, z + 0.022, CU, 0.002); mb.box(11.0, 8.05, z, 12.14, 8.08, z + 0.022, CU, 0.002)
mb.box(10.975, 3.15, HZ0 - 0.04, 11.0, 8.05, HZ0, CU, 0.002); mb.box(11.0, 8.05, HZ0 - 0.04, 12.14, 8.075, HZ0, CU, 0.002)   # drip edge
inst(mb.mesh('Mangal_hood_brick'), 'Mangal_hood_brick', (0, 0, 0), 0, 'Mangal')
st = bpy.data.objects.get('mangal_stack')                                                    # flue: real brick on all four faces
if st:
    bpy.context.view_layer.update(); cs = [st.matrix_world @ Vector(c_) for c_ in st.bound_box]
    x0_, x1_, y0_, y1_ = min(c_.x for c_ in cs), max(c_.x for c_ in cs), min(c_.y for c_ in cs), max(c_.y for c_ in cs); z0_, z1_ = max(min(c_.z for c_ in cs), 3.45), max(c_.z for c_ in cs)
    for i_ in range(len(st.data.materials)): st.data.materials[i_] = MORTAR
    mb = MB()
    brick_face(mb, 'x', x0_, -1, y0_, y1_, top(x0_ - 0.02) + 0.002, z1_, rnd_, False); brick_face(mb, 'x', x1_, 1, y0_, y1_, top(x1_) + 0.002, z1_, rnd_, False)
    brick_face(mb, 'y', y0_, -1, x0_ - 0.02, x1_ + 0.02, top(x0_ - 0.02) + 0.002, z1_, rnd_, False); brick_face(mb, 'y', y1_, 1, x0_ - 0.02, x1_ + 0.02, top(x0_ - 0.02) + 0.002, z1_, rnd_, False)
    mb.box(x0_ - 0.04, y0_ - 0.04, z1_ + 0.001, x1_ + 0.04, y1_ + 0.04, z1_ + 0.05, CU, 0.004)
    inst(mb.mesh('Mangal_flue_brick'), 'Mangal_flue_brick', (0, 0, 0), 0, 'Mangal')
MAJ = TILE[0]

# ---------------------------------------------------------------- chilled display counter (the pass)
K93 = dict(raw=mat('meat_raw', (0.5, 0.09, 0.1), rough=0.45, coat=0.3), fat=mat('meat_fat', (0.86, 0.76, 0.66), rough=0.5),
           lula=mat('meat_lula', (0.55, 0.2, 0.15), rough=0.55), chick=mat('meat_chicken', (0.86, 0.58, 0.4), rough=0.5, coat=0.2),
           tomato=mat('veg_tomato', (0.72, 0.06, 0.03), rough=0.25, coat=0.5), onion=mat('veg_onion', (0.55, 0.22, 0.45), rough=0.4),
           green=mat('veg_green', (0.12, 0.38, 0.08), rough=0.6), pepper=mat('veg_pepper', (0.15, 0.45, 0.1), rough=0.3, coat=0.4),
           bread=mat('lepyoshka', (0.72, 0.45, 0.18), rough=0.7), samsa=mat('samsa', (0.8, 0.55, 0.25), rough=0.6),
           enamel=mat('tray_enamel', (0.92, 0.92, 0.9), rough=0.2, coat=0.6), ice=mat('cold_deck', (0.75, 0.78, 0.8), rough=0.25, metal=0.8),
           led=mat('display_led', (1, 1, 0.95), emit=(1.0, 0.95, 0.85), strength=6.0))
DX0, DX1, DY0, DY1 = 9.38, 12.12, 8.42, 8.98; ZF = TER; ZD = TER + 0.86
mb = MB(); WD = XW['wd']
mb.box(DX0 + 0.05, DY0 + 0.05, ZF, DX1 - 0.05, DY1 - 0.08, ZF + 0.1, m['black'])                          # toe kick
mb.box(DX0, DY0, ZF + 0.1, DX1, DY1, ZD - 0.04, WD, 0.004)                                                 # walnut base
nP = 4; pw = (DX1 - DX0 - 0.1) / nP
for k in range(nP):                                                                                        # framed majolica front panels
    a = DX0 + 0.05 + k * pw
    tile_band(mb, 'y', DY1, 1, a + 0.04, a + pw - 0.04, ZF + 0.2, ZD - 0.14)
    mb.box(a + 0.02, DY1, ZF + 0.18, a + pw - 0.02, DY1 + 0.008, ZF + 0.2, CU); mb.box(a + 0.02, DY1, ZD - 0.14, a + pw - 0.02, DY1 + 0.008, ZD - 0.12, CU)
mb.box(DX0 - 0.01, DY0, ZD - 0.04, DX1 + 0.01, DY1 + 0.02, ZD, m['steel'], 0.003)                         # stainless deck rim
mb.box(DX0 + 0.04, DY0 + 0.04, ZD, DX1 - 0.04, DY1 - 0.04, ZD + 0.004, K93['ice'])                        # cold well plate
for x in (DX0 + 0.005, DX1 - 0.005): mb.box(x - 0.012, DY0 + 0.01, ZD, x + 0.012, DY1 - 0.005, ZD + 0.44, m['steel'], 0.002)   # end posts
inst(mb.mesh('Mangal_display_base'), 'Mangal_display_base', (0, 0, 0), 0, 'Mangal')
mb = MB(); G = m['glass']; ZG = ZD + 0.42
pts_f = [(DY1 - 0.01, ZD + 0.01), (DY1 - 0.24, ZG)]                                                       # angled front glass
(ya3, za3), (yb3, zb3) = pts_f; L = math.hypot(yb3 - ya3, zb3 - za3); an = math.atan2(zb3 - za3, yb3 - ya3)
fs = mb.box(DX0 + 0.02, 0, -0.006, DX1 - 0.02, L, 0.0, G)
for v in {v for f in fs for v in f.verts}:
    y_, z_ = v.co.y, v.co.z; v.co.y, v.co.z = ya3 + y_ * math.cos(an) - z_ * math.sin(an), za3 + y_ * math.sin(an) + z_ * math.cos(an)
mb.box(DX0 + 0.02, DY0 + 0.03, ZG + 0.001, DX1 - 0.02, DY1 - 0.24, ZG + 0.009, G)                                # top glass (serving shelf)
mb.box(DX0 + 0.02, DY1 - 0.26, ZG - 0.02, DX1 - 0.02, DY1 - 0.245, ZG - 0.005, K93['led'])               # LED strip under the top
for x in (DX0 + 0.024, DX1 - 0.024): mb.box(x - 0.003, DY0 + 0.03, ZD + 0.005, x + 0.003, DY1 - 0.03, ZG - 0.001, G)   # end glass
inst(mb.mesh('Mangal_display_glass'), 'Mangal_display_glass', (0, 0, 0), 0, 'Mangal')

# products on enamel trays (left -> right: lamb shashlik, lula, chicken, vegetables + salads, bread + samsa)
mb = MB(); z0 = ZD + 0.004; TY0, TY1 = DY0 + 0.07, DY1 - 0.12
trays = [(9.45, 9.98), (10.03, 10.56), (10.61, 11.14), (11.19, 11.62), (11.67, 12.05)]
for a, b in trays: mb.box(a, TY0, z0, b, TY1, z0 + 0.018, K93['enamel'], 0.004)
zt = z0 + 0.018
def skewer(b, x, y0, y1, z, kind):
    b.rod((x, y0 - 0.03, z + 0.015), (x, y1 + 0.03, z + 0.015), 0.0025, m['steel'], 6)
    y = y0
    while y < y1 - 0.02:
        if kind == 'lamb':
            b.box(x - 0.016, y, z, x + 0.016, y + 0.032, z + 0.03, K93['raw'], 0.004)
            b.box(x - 0.013, y + 0.032, z + 0.003, x + 0.013, y + 0.042, z + 0.026, K93['fat'] if int(y * 100) % 3 else K93['onion'], 0.003); y += 0.046
        elif kind == 'chick':
            b.box(x - 0.017, y, z, x + 0.017, y + 0.034, z + 0.03, K93['chick'], 0.005); y += 0.04
        else: break
    if kind == 'lula': b.rod((x, y0 + 0.01, z + 0.016), (x, y1 - 0.01, z + 0.016), 0.016, K93['lula'], 10)
    b.box(x - 0.012, y1 + 0.03, z + 0.008, x + 0.012, y1 + 0.075, z + 0.022, WD)                           # wooden handle
for (a, b), kind in zip(trays[:3], ('lamb', 'lula', 'chick')):
    for k in range(7): skewer(mb, a + 0.04 + k * 0.075, TY0 + 0.03, TY1 - 0.09, zt, kind)
a, b = trays[3]                                                                                            # vegetables
for k in range(6): mb.lathe(a + 0.06 + (k % 3) * 0.12, TY0 + 0.07 + (k // 3) * 0.12, zt, [(0.0, 0.0), (0.03, 0.005), (0.04, 0.03), (0.03, 0.055), (0.0, 0.06)], K93['tomato'], 14)
for k in range(5): mb.ring(a + 0.06 + k * 0.08, TY1 - 0.08, zt, [(0.018, 0.0), (0.03, 0.0), (0.03, 0.006), (0.018, 0.006)], K93['onion'], 16)
for k in range(4): mb.rod((a + 0.05 + k * 0.1, TY1 - 0.04, zt + 0.01), (a + 0.12 + k * 0.1, TY1 - 0.03, zt + 0.012), 0.012, K93['pepper'], 8)
mb.lathe(a + 0.36, TY0 + 0.1, zt, [(0.0, 0.0), (0.05, 0.0), (0.06, 0.04), (0.0, 0.04)], K93['green'], 14)
a, b = trays[4]                                                                                            # lepyoshka stack + samsa
for k in range(4): mb.lathe(a + 0.12, TY0 + 0.14, zt + 0.022 * k, [(0.0, 0.0), (0.1, 0.0), (0.11, 0.012), (0.08, 0.02), (0.03, 0.016), (0.0, 0.02)], K93['bread'], 24)
for k in range(5):
    x, y = a + 0.27 + (k % 2) * 0.06, TY0 + 0.05 + k * 0.05
    mb.extrude([(x - 0.03, y - 0.02), (x + 0.03, y - 0.02), (x, y + 0.03)], zt, zt + 0.035, K93['samsa'])
inst(mb.mesh('Mangal_display_food'), 'Mangal_display_food', (0, 0, 0), 0, 'Mangal')
print('rev 9.3 mangal display ok')
