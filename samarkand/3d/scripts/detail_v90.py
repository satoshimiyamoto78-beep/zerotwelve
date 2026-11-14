"""rev. 9.0 (owner refs 2026-11-05): kids corner worked out properly — inside the existing carved fence (7.0 x 2.4 m)
  west : chalkboard wall (walnut frame, 1.8 x 1.3 board) + reading nook bench with mattress and pillows along the hall glazing,
         round kids table d 700 h 520 with 4 kids chairs (seat 280)
  middle (opposite the 900 gate, entry kept clear): coloured EPDM tiles 500x500 with a Pikler climbing triangle + slide ramp,
         low Montessori shelf with rattan baskets and wooden toys against the glazing (parents keep the view from the hall)
  east : walnut sandbox 1.5 x 1.2 with corner seats (kinetic sand, lid stored behind the shelf)
  over : festoon string lights on two masts and the chalkboard posts (lowest bulb > 2.1 m)
All timber in the chair walnut (owner rule), colour only in the tiles, cushions and table tops."""
_rm('play_block', 'play_drum', 'play_sand', 'play_seat', 'Kids_chest')
K = dict(blue=mat('k_epdm_blue', (0.04, 0.16, 0.45), rough=0.9), green=mat('k_epdm_green', (0.08, 0.36, 0.22), rough=0.9),
         yellow=mat('k_epdm_yellow', (0.78, 0.55, 0.06), rough=0.9), orange=mat('k_epdm_orange', (0.8, 0.33, 0.08), rough=0.9),
         sand=mat('k_sand', (0.78, 0.66, 0.48), rough=0.97, bump=0.6, noise_var=0.06),
         mattress=mat('k_mattress', (0.42, 0.46, 0.5), rough=0.9), c1=mat('k_cush_rose', (0.75, 0.32, 0.3), rough=0.9),
         c2=mat('k_cush_teal', (0.12, 0.38, 0.42), rough=0.9), c3=mat('k_cush_mustard', (0.75, 0.55, 0.15), rough=0.9),
         c4=mat('k_cush_sage', (0.45, 0.52, 0.4), rough=0.9), board=uvmat('k_chalkboard', 'chalkboard.png', rough=0.85, sheen=0.0),
         bulb=mat('k_bulb', (1, 0.85, 0.6), emit=(1.0, 0.7, 0.35), strength=6.0), wire=mat('k_wire', (0.02, 0.02, 0.02), rough=0.5))
WD = XW['wd']; RT = X['rattan']
KX0, KX1, KY0, KY1 = -7.19, -0.18, 1.66, 4.07                  # inside the fence posts / glazing

def kslab(b, p0, p1, w, t, mm, yc):
    """board along the x-z line p0 -> p1 (top surface), width w centred on y = yc, thickness t below the top"""
    (xa, za), (xb, zb) = p0, p1; L = math.hypot(xb - xa, zb - za); a = math.atan2(zb - za, xb - xa)
    fs = b.box(0, -w / 2, -t, L, w / 2, 0, mm)
    for v in {v for f in fs for v in f.verts}:
        x_, z_ = v.co.x, v.co.z; v.co.x, v.co.z = xa + x_ * math.cos(a) - z_ * math.sin(a), za + x_ * math.sin(a) + z_ * math.cos(a); v.co.y += yc

# ---------------------------------------------------------------- chalkboard wall (west)
mb = MB(); xb_ = -7.14
for y in (1.75, 3.55): mb.box(xb_ - 0.04, y - 0.04, TER, xb_ + 0.04, y + 0.04, TER + 2.3, WD, 0.004)
mb.box(xb_ - 0.03, 1.79, TER + 0.5, xb_ + 0.03, 3.51, TER + 0.56, WD, 0.003); mb.box(xb_ - 0.03, 1.79, TER + 1.84, xb_ + 0.03, 3.51, TER + 1.9, WD, 0.003)
mb.picture_box(xb_ - 0.012, 1.79, TER + 0.56, xb_ + 0.012, 3.51, TER + 1.84, K['board'], '+x')
mb.box(xb_ + 0.03, 1.79, TER + 0.5, xb_ + 0.09, 3.51, TER + 0.53, WD, 0.002)                        # chalk ledge
for i_, c in enumerate(('c1', 'c3', 'c2', 'c4')): mb.box(xb_ + 0.045, 2.2 + 0.1 * i_, TER + 0.53, xb_ + 0.06, 2.27 + 0.1 * i_, TER + 0.545, K[c])
inst(mb.mesh('Kids_chalkboard'), 'Kids_chalkboard', (0, 0, 0), 0, 'Kids')

# ---------------------------------------------------------------- reading nook bench (along the glazing)
mb = MB(); bx0, bx1, by0, by1 = -7.08, -5.45, 3.62, 4.05
mb.box(bx0, by0, TER, bx1, by1, TER + 0.25, WD, 0.006)
for k in range(3):                                                        # three basket cubbies in the front face
    cx = bx0 + (bx1 - bx0) * (k + 0.5) / 3
    mb.box(cx - 0.22, by0 + 0.02, TER + 0.04, cx + 0.22, by0 + 0.03, TER + 0.21, WD)            # recessed panel (flush detail)
    mb.box(cx - 0.18, by0 - 0.0, TER + 0.06, cx + 0.18, by0 + 0.02, TER + 0.2, RT)               # rattan basket front
mb.box(bx0, by1 - 0.05, TER + 0.25, bx1, by1, TER + 0.62, WD, 0.004)                              # low backrest (glazing stays visible above)
mb.box(bx0 + 0.02, by0 + 0.02, TER + 0.25, bx1 - 0.02, by1 - 0.05, TER + 0.32, K['mattress'], 0.02)
for i_, c in enumerate(('c1', 'c2', 'c3', 'c4')):
    cx = bx0 + 0.25 + 0.37 * i_
    mb.box(cx - 0.17, by1 - 0.17, TER + 0.32, cx + 0.17, by1 - 0.05, TER + 0.62, K[c], 0.04)
inst(mb.mesh('Kids_nook_bench'), 'Kids_nook_bench', (0, 0, 0), 0, 'Kids')

# ---------------------------------------------------------------- kids table + chairs
@cached
def a_kid_chair():
    b = MB(); s = 0.15
    for x in (-0.13, 0.13):
        for y in (-0.13, 0.13): b.box(x - 0.015, y - 0.015, 0, x + 0.015, y + 0.015, 0.26 if y < 0 else 0.56, WD, 0.003)
    b.box(-s, -s, 0.26, s, s, 0.28, WD, 0.004)
    b.box(-0.115, 0.115, 0.4, 0.115, 0.145, 0.54, WD, 0.004)                                       # back slat
    for y in (-0.13, 0.13): b.box(-0.115, y - 0.01, 0.08, 0.115, y + 0.01, 0.11, WD)
    return b.mesh('Kids_chair')
mb = MB(); TX, TY = -6.15, 2.62
mb.cyl(TX, TY, TER + 0.495, TER + 0.52, 0.35, K['c4'], 48); mb.ring(TX, TY, TER + 0.495, [(0.34, 0), (0.355, 0), (0.355, 0.025), (0.34, 0.025)], WD, 48)
for k in range(4):
    a = math.pi / 4 + k * math.pi / 2; mb.box(TX + 0.22 * math.cos(a) - 0.02, TY + 0.22 * math.sin(a) - 0.02, TER, TX + 0.22 * math.cos(a) + 0.02, TY + 0.22 * math.sin(a) + 0.02, TER + 0.495, WD, 0.003)
mb.ring(TX, TY, TER + 0.15, [(0.2, 0), (0.24, 0), (0.24, 0.03), (0.2, 0.03)], WD, 32)
inst(mb.mesh('Kids_table'), 'Kids_table', (0, 0, 0), 0, 'Kids')
for i_, (dx, dy, rz) in enumerate(((0, -0.47, 0.0), (0, 0.47, math.pi), (-0.47, 0, -math.pi / 2), (0.47, 0, math.pi / 2))):
    inst(a_kid_chair(), f'Kids_chair_{i_ + 1}', (TX + dx, TY + dy, TER), rz + math.pi, 'Kids')

# ---------------------------------------------------------------- EPDM tiles + Pikler triangle + ramp
mb = MB(); cols = ('blue', 'yellow', 'green', 'orange')
for i in range(4):
    for j in range(3):
        x0, y0 = -5.35 + 0.5 * i, 2.57 + 0.5 * j; mb.box(x0, y0, TER, x0 + 0.5, y0 + 0.5, TER + 0.02, K[cols[(i + 2 * j) % 4]], 0.003)
inst(mb.mesh('Kids_epdm_tiles'), 'Kids_epdm_tiles', (0, 0, 0), 0, 'Kids')
ZT_ = TER + 0.02; PA, PB, PH, PY0, PY1 = -5.1, -4.3, 0.85, 3.15, 3.85
PM = (PA + PB) / 2
mb = MB()
for y in (PY0, PY1):                                                       # two A-frames (40 x 30 rails)
    kslab(mb, (PA, ZT_ + 0.045), (PM, ZT_ + PH), 0.03, 0.04, WD, y); kslab(mb, (PM, ZT_ + PH), (PB, ZT_ + 0.045), 0.03, 0.04, WD, y)
    mb.box(PA - 0.02, y - 0.015, ZT_, PB + 0.02, y + 0.015, ZT_ + 0.03, WD, 0.002)                 # foot rail
for k in range(1, 7):                                                      # beech-dowel rungs, both slopes
    t = k / 7
    for xx in (PA + (PM - PA) * t, PB - (PB - PM) * t):
        zz = ZT_ + 0.02 + (PH - 0.02) * t - 0.03
        mb.rod((xx, PY0 + 0.015, zz), (xx, PY1 - 0.015, zz), 0.016, WD, 12)
mb.rod((PM, PY0 + 0.015, ZT_ + PH - 0.03), (PM, PY1 - 0.015, ZT_ + PH - 0.03), 0.018, WD, 12)
t_ = 5 / 7; xr, zr = PB - (PB - PM) * t_, ZT_ + 0.02 + (PH - 0.02) * t_ - 0.03 + 0.016    # ramp hooks over the 5th rung
kslab(mb, (xr, zr + 0.029), (xr + 1.0, ZT_ + 0.025), 0.45, 0.025, WD, (PY0 + PY1) / 2)
mb.box(xr - 0.04, (PY0 + PY1) / 2 - 0.2, zr - 0.035, xr - 0.02, (PY0 + PY1) / 2 + 0.2, zr + 0.0, WD)   # hook cleat behind the rung
for k in range(1, 5):                                                      # climbing cleats
    t = k / 5.0; xx = xr + 1.0 * t; zz = zr + 0.025 + (ZT_ + 0.025 - zr - 0.025) * t
    mb.box(xx - 0.015, (PY0 + PY1) / 2 - 0.18, zz, xx + 0.015, (PY0 + PY1) / 2 + 0.18, zz + 0.02, WD)
for y in ((PY0 + PY1) / 2 - 0.2, (PY0 + PY1) / 2 + 0.2):
    mb.box(xr + 0.98, y - 0.02, ZT_, xr + 1.02, y + 0.02, ZT_ + 0.01, K['c2'])                    # rubber feet
inst(mb.mesh('Kids_pikler'), 'Kids_pikler', (0, 0, 0), 0, 'Kids')     # triangle + ramp, one assembly

# ---------------------------------------------------------------- Montessori shelf with baskets + toys (against the glazing)
mb = MB(); sx0, sx1, sy0, sy1, SH = -3.25, -2.35, 3.74, 4.05, 0.62
side = SBox(sy0, TER, sy1, TER + SH - 0.1).union(SPt((sy0 + sy1) / 2, TER + SH - 0.1).buffer((sy1 - sy0) / 2, 16))
for x in (sx0, sx1 - 0.025): ext_holes(mb, side, x, x + 0.025, WD, 'yz')
for z in (0.0, 0.3, 0.58): mb.box(sx0 + 0.025, sy0, TER + z, sx1 - 0.025, sy1, TER + z + 0.02, WD, 0.002)
mb.box(sx0 + 0.025, sy1 - 0.012, TER + 0.02, sx1 - 0.025, sy1, TER + 0.58, WD)
for k in range(3):
    cx = sx0 + 0.16 + 0.29 * k
    mb.box(cx - 0.12, sy0 + 0.04, TER + 0.02, cx + 0.12, sy1 - 0.03, TER + 0.2, RT, 0.01)
for k, c in enumerate(('c1', 'c3', 'c2', 'c4', 'c1')):                     # wooden blocks + stacking ring on the top shelf
    mb.box(sx0 + 0.08 + 0.09 * k, sy0 + 0.1, TER + 0.6, sx0 + 0.15 + 0.09 * k, sy0 + 0.17, TER + 0.67, K[c] if k % 2 else WD, 0.004)
mb.box(sx0 + 0.08, sy0 + 0.08, TER + 0.32, sx0 + 0.36, sy0 + 0.22, TER + 0.36, WD, 0.004)
for k, c in enumerate(('c1', 'c3', 'c2')): mb.ring(sx0 + 0.6, sy0 + 0.15, TER + 0.32 + 0.035 * k, [(0.02, 0), (0.07 - 0.012 * k, 0), (0.07 - 0.012 * k, 0.035), (0.02, 0.035)], K[c], 24)
inst(mb.mesh('Kids_shelf'), 'Kids_shelf', (0, 0, 0), 0, 'Kids')

# ---------------------------------------------------------------- sandbox with corner seats
mb = MB(); qx0, qx1, qy0, qy1, QH = -1.95, -0.45, 2.55, 3.75, 0.28
for (a0, a1, b0, b1) in ((qx0, qx1, qy0, qy0 + 0.04), (qx0, qx1, qy1 - 0.04, qy1), (qx0, qx0 + 0.04, qy0 + 0.04, qy1 - 0.04), (qx1 - 0.04, qx1, qy0 + 0.04, qy1 - 0.04)):
    mb.box(a0, b0, TER, a1, b1, TER + QH, WD, 0.006)
mb.box(qx0 + 0.04, qy0 + 0.04, TER, qx1 - 0.04, qy1 - 0.04, TER + 0.2, K['sand'])
for cx, cy, sx, sy in ((qx0, qy0, 1, 1), (qx1, qy0, -1, 1), (qx0, qy1, 1, -1), (qx1, qy1, -1, -1)):
    tri = [(cx + sx * 0.04, cy + sy * 0.04), (cx + sx * 0.3, cy + sy * 0.04), (cx + sx * 0.04, cy + sy * 0.3)]
    if sx * sy < 0: tri = tri[::-1]
    mb.extrude(tri, TER + QH - 0.025, TER + QH, WD)
inst(mb.mesh('Kids_sandbox'), 'Kids_sandbox', (0, 0, 0), 0, 'Kids')
mb = MB()                                                                  # bucket + spade
mb.lathe(-0.9, 3.0, TER + 0.2, [(0.0, 0.0), (0.06, 0.0), (0.075, 0.12), (0.07, 0.12), (0.055, 0.005), (0.0, 0.005)], K['orange'], 20)
kslab(mb, (-1.4, TER + 0.215), (-1.15, TER + 0.215), 0.06, 0.015, K['blue'], 3.3)
inst(mb.mesh('Kids_sand_toys'), 'Kids_sand_toys', (0, 0, 0), 0, 'Kids')

# ---------------------------------------------------------------- festoon string lights
mb = MB()
for y in (1.72, 4.0): mb.box(-0.27, y - 0.025, TER, -0.22, y + 0.025, TER + 2.45, WD, 0.004)
for (p0, p1) in (((-7.097, 1.75, TER + 2.28), (-0.273, 1.72, TER + 2.43)), ((-7.097, 3.55, TER + 2.28), (-0.273, 4.0, TER + 2.43))):
    P0, P1 = Vector(p0), Vector(p1); n_ = 24; pts = []
    for k in range(n_ + 1):
        t = k / n_; q = P0.lerp(P1, t); q.z -= 0.16 * math.sin(math.pi * t); pts.append(q)
    for qa, qb in zip(pts[:-1], pts[1:]): mb.rod(qa, qb, 0.003, K['wire'], 6)
    for k in range(2, n_ - 1, 2):
        q = pts[k]; mb.rod(q, q - Vector((0, 0, 0.05)), 0.003, K['wire'], 6)
        mb.lathe(q.x, q.y, q.z - 0.11, [(0.0, 0.0), (0.022, 0.012), (0.03, 0.035), (0.02, 0.055), (0.0, 0.06)], K['bulb'], 12)
inst(mb.mesh('Kids_festoon'), 'Kids_festoon', (0, 0, 0), 0, 'Kids')
print('rev 9.0 kids corner ok')
