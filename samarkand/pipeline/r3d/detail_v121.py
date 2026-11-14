"""rev. 12.0 block 2 — BAR (owner: 'the bar texture is still a photo; ugly things stand on it instead of equipment, cups and
tableware; work out the shelves and the fridge'):
  * back wall laid brick by brick: buff facing brick 230 x 65, 10 mm recessed joints, running bond, a diamond lattice of turquoise /
    cobalt glazed headers (hazarbaf), soldier course at the top
  * back bar: 4 glass-door under-counter fridges with bottles inside, ice maker, 3 walnut door cabinets, walnut worktop +0.90
  * equipment modelled as what it is: 2-group espresso machine (groups, portafilters, steam wands, gauge, cup rail with cups),
    2 grinders with bean hoppers, knock box, 2 blenders, citrus press, 2 glass drink dispensers with taps, kettle, POS
  * three walnut shelves 40 mm on brass brackets with a brass gallery rail: stacked cups and saucers, glass rows, syrup bottles with
    pumps, tea tins, jars, a small plant; warm LED under every shelf
  * tall glass-door bottle cooler at the north end"""
import random as _r1
_rmp('Bar_backbar')
_r = _r1.Random(7); F0 = TER
_WD = XW['wd']; _ST = mat('stainless_brushed', (0.62, 0.63, 0.64), rough=0.28, metal=1.0); _BK = m['black']; _BR = m['brass']
_GL = mat('bar_glass_clear', (0.92, 0.96, 0.97), rough=0.03, transmission=0.92)
_PO = mat('porcelain_white', (0.93, 0.93, 0.9), rough=0.15)
_BUFF = [mat(f'brick_face_{k}', c, rough=0.85) for k, c in enumerate(((0.72, 0.56, 0.38), (0.66, 0.5, 0.34), (0.76, 0.61, 0.43)))]
_GLZ = [mat('glaze_turq_bar', (0.05, 0.5, 0.52), rough=0.12), mat('glaze_cob_bar', (0.03, 0.1, 0.42), rough=0.12)]
_MORT = mat('mortar_joint', (0.5, 0.46, 0.4), rough=0.95)
_DR = [mat(f'syrup_amber_{k}', c, rough=0.08, transmission=0.35) for k, c in enumerate(((0.62, 0.3, 0.08), (0.78, 0.55, 0.16), (0.42, 0.2, 0.06), (0.5, 0.1, 0.1), (0.85, 0.78, 0.6), (0.2, 0.1, 0.04)))]
# ---- brick wall x 0.14..0.22, y 8.60..14.30, floor..+3.55
b = MB(); X0w, X1w = 0.14, 0.215; b.box(X0w, 8.6, F0, X1w - 0.012, 14.3, 3.10, _MORT)
BL, BH, J = 0.23, 0.065, 0.01; row = 0; z = F0 + 0.005
while z + BH <= 3.10 - 0.11:
    off = (BL + J) / 2 if row % 2 else 0.0; y = 8.6 - off; col = 0
    while y < 14.3:
        y0, y1 = max(y, 8.6), min(y + BL, 14.3)
        if y1 - y0 > 0.03:
            g = (col * 2 + row) % 8 == 0 or (col * 2 - row) % 8 == 0
            mm = _GLZ[(row // 4) % 2] if (g and row % 2 == 0) else _BUFF[_r.randrange(3)]
            b.box(X1w - 0.012, y0, z, X1w + (0.004 if mm in _GLZ else _r.uniform(-0.002, 0.002)), y1, z + BH, mm, 0.0015)
        y += BL + J; col += 1
    z += BH + J; row += 1
y = 8.6
while y < 14.3 - 0.02:                                                                     # soldier course
    b.box(X1w - 0.012, y, z, X1w, min(y + BH, 14.3), 3.10, _BUFF[_r.randrange(3)], 0.0015); y += BH + J
inst(b.mesh('Bar_brickwall'), 'Bar_brickwall', (0, 0, 0), 0, 'Bar')
# ---- cornice
b = MB(); b.box(0.215, 8.6, 2.90, 0.33, 14.3, 3.08, _WD, 0.004); b.box(0.215, 8.6, 2.88, 0.35, 14.3, 2.90, _BR)
inst(b.mesh('Bar_cornice'), 'Bar_cornice', (0, 0, 0), 0, 'Bar')
# ---- back bar units
b = MB(); XF = 0.70
def bottle(bb, x, y, z, h, mm, r=0.03):
    bb.cyl(x, y, z, z + h * 0.62, r, mm, 10); bb.cyl(x, y, z + h * 0.62, z + h * 0.78, r, mm, 10, r2=r * 0.4); bb.cyl(x, y, z + h * 0.78, z + h, r * 0.4, mm, 8)
    bb.cyl(x, y, z + h, z + h + 0.012, r * 0.45, _BK, 8)
def fridge(y0, y1):
    b.box(0.225, y0 + 0.004, F0 + 0.10, XF - 0.02, y1 - 0.004, F0 + 0.86, _ST, 0.003)
    for k in range(4):                                                                   # bottles behind the glass
        bottle(b, XF - 0.05, y0 + 0.1 + k * (y1 - y0 - 0.2) / 3, F0 + 0.16, 0.24, _DR[k % 6]); bottle(b, XF - 0.05, y0 + 0.1 + k * (y1 - y0 - 0.2) / 3, F0 + 0.5, 0.24, _DR[(k + 3) % 6])
    b.box(XF - 0.1, y0 + 0.05, F0 + 0.46, XF - 0.02, y1 - 0.05, F0 + 0.47, _ST)
    for (a0, a1, c0, c1) in ((y0 + 0.02, y1 - 0.02, F0 + 0.12, F0 + 0.16), (y0 + 0.02, y1 - 0.02, F0 + 0.80, F0 + 0.84), (y0 + 0.02, y0 + 0.06, F0 + 0.16, F0 + 0.80), (y1 - 0.06, y1 - 0.02, F0 + 0.16, F0 + 0.80)):
        b.box(XF - 0.02, a0, c0, XF, a1, c1, _BK)                                         # door frame
    b.box(XF - 0.012, y0 + 0.06, F0 + 0.16, XF - 0.006, y1 - 0.06, F0 + 0.80, _GL)
    b.rod((XF + 0.02, y1 - 0.09, F0 + 0.3), (XF + 0.02, y1 - 0.09, F0 + 0.66), 0.008, _ST); b.box(XF - 0.018, y0 + 0.07, F0 + 0.775, XF - 0.014, y1 - 0.07, F0 + 0.79, _LED0)
    b.box(0.25, y0, F0, XF - 0.06, y1, F0 + 0.10, _BK)
def cabinet(y0, y1):
    n_ = max(1, round((y1 - y0) / 0.6)); w_ = (y1 - y0) / n_
    b.box(0.225, y0, F0 + 0.10, XF - 0.02, y1, F0 + 0.86, _WD)
    for k in range(n_):
        ya = y0 + k * w_
        b.box(XF - 0.02, ya + 0.006, F0 + 0.11, XF, ya + w_ - 0.006, F0 + 0.85, _WD, 0.003)
        b.box(XF, ya + 0.06, F0 + 0.17, XF + 0.006, ya + w_ - 0.06, F0 + 0.79, _WD, 0.002)   # raised panel
        b.rod((XF + 0.022, ya + w_ - 0.07, F0 + 0.42), (XF + 0.022, ya + w_ - 0.07, F0 + 0.56), 0.006, _BR)
    b.box(0.25, y0, F0, XF - 0.06, y1, F0 + 0.10, _BK)
def icemaker(y0, y1):
    b.box(0.225, y0 + 0.004, F0 + 0.10, XF, y1 - 0.004, F0 + 0.86, _ST, 0.004)
    b.box(XF, y0 + 0.05, F0 + 0.5, XF + 0.012, y1 - 0.05, F0 + 0.82, _ST, 0.003); b.rod((XF + 0.03, y0 + 0.1, F0 + 0.54), (XF + 0.03, y1 - 0.1, F0 + 0.54), 0.008, _BK)
    for k in range(6): b.box(XF, y0 + 0.06, F0 + 0.16 + k * 0.035, XF + 0.004, y1 - 0.06, F0 + 0.18 + k * 0.035, _BK)   # grille
    b.box(0.25, y0, F0, XF - 0.06, y1, F0 + 0.10, _BK)
icemaker(8.62, 9.22); fridge(9.22, 9.82); fridge(9.82, 10.42); cabinet(10.42, 12.22); fridge(12.22, 12.82); fridge(12.82, 13.42)
b.box(0.215, 8.62, F0 + 0.86, 0.73, 13.42, F0 + 0.90, _WD, 0.004); b.box(0.215, 8.62, F0 + 0.90, 0.235, 13.42, F0 + 1.0, _WD)   # worktop + upstand
ZT = F0 + 0.90
# tall cooler
b.box(0.225, 13.44, F0, 0.70, 14.28, F0 + 2.05, _ST, 0.004)
for (a0, a1, c0, c1) in ((13.47, 14.25, F0 + 0.1, F0 + 0.16), (13.47, 14.25, F0 + 1.93, F0 + 1.99), (13.47, 13.53, F0 + 0.16, F0 + 1.93), (14.19, 14.25, F0 + 0.16, F0 + 1.93)):
    b.box(0.70, a0, c0, 0.72, a1, c1, _BK)
b.box(0.705, 13.53, F0 + 0.16, 0.711, 14.19, F0 + 1.93, _GL); b.rod((0.74, 13.6, F0 + 0.8), (0.74, 13.6, F0 + 1.3), 0.009, _ST)
for r_, zz in enumerate((0.2, 0.55, 0.9, 1.25, 1.6)):
    b.box(0.26, 13.5, F0 + zz - 0.012, 0.69, 14.22, F0 + zz, _ST)
    for k in range(8): bottle(b, 0.62, 13.56 + k * 0.088, F0 + zz, 0.26, _DR[(k // 2 + r_) % 6])
b.box(0.69, 13.52, F0 + 1.9, 0.7, 14.2, F0 + 1.92, _LED0)
inst(b.mesh('Bar_backbar'), 'Bar_backbar', (0, 0, 0), 0, 'Bar')
# ---- equipment on the worktop
b = MB()
def cup(bb, x, y, z, s=1.0):
    bb.lathe(x, y, z, [(0.0, 0.0), (0.022 * s, 0.0), (0.034 * s, 0.045 * s), (0.036 * s, 0.06 * s), (0.031 * s, 0.06 * s), (0.02 * s, 0.01 * s), (0.0, 0.01 * s)], _PO, 14)
def saucers(bb, x, y, z, n):
    for k in range(n): bb.lathe(x, y, z + k * 0.008, [(0.0, 0.0), (0.03, 0.0), (0.065, 0.01), (0.065, 0.014), (0.03, 0.006), (0.0, 0.006)], _PO, 16)
def glass(bb, x, y, z, h=0.12, r=0.032):
    bb.lathe(x, y, z, [(0.0, 0.0), (r * 0.8, 0.0), (r, h), (r - 0.003, h), (r * 0.8 - 0.003, 0.006), (0.0, 0.006)], _GL, 12)
# espresso machine, y 10.55..11.30
y0, y1 = 10.55, 11.30; ym = (y0 + y1) / 2
b.box(0.26, y0, ZT + 0.03, 0.68, y1, ZT + 0.40, _ST, 0.012); b.box(0.26, y0 + 0.02, ZT, 0.66, y1 - 0.02, ZT + 0.03, _BK)
b.box(0.28, y0 + 0.02, ZT + 0.40, 0.66, y1 - 0.02, ZT + 0.425, _BK); b.box(0.275, y0 + 0.015, ZT + 0.425, 0.665, y1 - 0.015, ZT + 0.44, _ST)   # cup warmer + rail
for yy in (y0 + 0.02, y1 - 0.02): b.rod((0.28, yy, ZT + 0.47), (0.66, yy, ZT + 0.47), 0.005, _ST)
for k in range(8): cup(b, 0.34 + 0.085 * (k % 4), y0 + 0.2 + 0.32 * (k // 4), ZT + 0.44)
b.box(0.56, y0 + 0.04, ZT + 0.03, 0.74, y1 - 0.04, ZT + 0.06, _ST, 0.004); b.box(0.565, y0 + 0.05, ZT + 0.06, 0.735, y1 - 0.05, ZT + 0.064, _BK)   # drip tray + grate
for yy in (ym - 0.17, ym + 0.17):                                                           # group heads + portafilters
    b.cyl(0.70, yy, ZT + 0.22, ZT + 0.30, 0.04, _ST, 16); b.cyl(0.70, yy, ZT + 0.195, ZT + 0.22, 0.036, _BK, 16)
    b.rod((0.70, yy, ZT + 0.205), (0.83, yy + 0.02, ZT + 0.195), 0.011, _BK); b.cyl(0.70, yy, ZT + 0.17, ZT + 0.195, 0.012, _ST, 8)
    cup(b, 0.70, yy, ZT + 0.064, 0.8)
for yy, s_ in ((y0 + 0.07, 1), (y1 - 0.07, -1)):                                           # steam wands
    b.rod((0.69, yy, ZT + 0.3), (0.74, yy, ZT + 0.26), 0.006, _ST); b.rod((0.74, yy, ZT + 0.26), (0.76, yy + s_ * 0.03, ZT + 0.1), 0.005, _ST)
b.cyl(0.681, ym, ZT + 0.31, ZT + 0.37, 0.03, _BK, 16); b.cyl(0.683, ym, ZT + 0.315, ZT + 0.365, 0.024, _PO, 16)     # gauge (on the face)
for yy in (ym - 0.3, ym + 0.3): b.cyl(0.69, yy, ZT + 0.33, ZT + 0.36, 0.016, _BK, 10)                                # knobs
# grinders with hoppers, y 11.5 / 11.78; knock box
for yy in (11.52, 11.80):
    b.box(0.33, yy - 0.085, ZT, 0.53, yy + 0.085, ZT + 0.33, _BK, 0.012); b.lathe(0.43, yy, ZT + 0.33, [(0.0, 0.0), (0.045, 0.0), (0.085, 0.14), (0.085, 0.17), (0.0, 0.17)], _GL, 14)
    b.lathe(0.43, yy, ZT + 0.335, [(0.0, 0.0), (0.04, 0.0), (0.07, 0.1), (0.0, 0.1)], _DR[5], 12)                 # beans
    b.box(0.53, yy - 0.03, ZT + 0.16, 0.60, yy + 0.03, ZT + 0.20, _BK); b.rod((0.53, yy, ZT + 0.07), (0.62, yy, ZT + 0.07), 0.009, _ST)
b.box(0.36, 12.0, ZT, 0.52, 12.16, ZT + 0.1, _ST, 0.006); b.rod((0.36, 12.08, ZT + 0.085), (0.52, 12.08, ZT + 0.085), 0.012, _BK)
# blenders y 9.45 / 9.75
for yy in (9.42, 9.72):
    b.box(0.34, yy - 0.09, ZT, 0.52, yy + 0.09, ZT + 0.16, _BK, 0.015); b.box(0.52, yy - 0.05, ZT + 0.04, 0.526, yy + 0.05, ZT + 0.1, _ST)
    b.lathe(0.43, yy, ZT + 0.16, [(0.0, 0.0), (0.05, 0.0), (0.068, 0.24), (0.064, 0.24), (0.046, 0.008), (0.0, 0.008)], _GL, 12); b.cyl(0.43, yy, ZT + 0.40, ZT + 0.42, 0.07, _BK, 12)
    b.box(0.495, yy - 0.012, ZT + 0.22, 0.53, yy + 0.012, ZT + 0.38, _BK, 0.004)                                 # handle
# citrus press y 10.1, kettle 8.95, dispensers 12.5 / 12.85, fruit bowl 13.15
b.cyl(0.43, 10.1, ZT, ZT + 0.03, 0.09, _ST, 20); b.cyl(0.43, 10.1, ZT + 0.03, ZT + 0.2, 0.03, _ST, 12); b.lathe(0.43, 10.1, ZT + 0.2, [(0.0, 0.0), (0.07, 0.02), (0.075, 0.05), (0.0, 0.09)], _ST, 16)
b.rod((0.36, 10.1, ZT + 0.36), (0.52, 10.1, ZT + 0.3), 0.01, _ST); b.rod((0.36, 10.1, ZT + 0.03), (0.36, 10.1, ZT + 0.36), 0.012, _ST)
b.lathe(0.42, 8.95, ZT, [(0.0, 0.0), (0.075, 0.0), (0.085, 0.1), (0.06, 0.2), (0.03, 0.22), (0.0, 0.22)], _ST, 16); b.rod((0.49, 8.95, ZT + 0.12), (0.58, 8.95, ZT + 0.19), 0.01, _ST); b.rod((0.42, 8.87, ZT + 0.22), (0.42, 9.03, ZT + 0.22), 0.008, _BK)
for k, yy in enumerate((12.5, 12.86)):
    b.cyl(0.42, yy, ZT, ZT + 0.06, 0.1, _BK, 20); b.cyl(0.42, yy, ZT + 0.06, ZT + 0.36, 0.105, _GL, 20); b.cyl(0.42, yy, ZT + 0.065, ZT + 0.30, 0.098, _DR[(1, 2)[k]], 20)
    b.cyl(0.42, yy, ZT + 0.36, ZT + 0.39, 0.11, _ST, 20); b.rod((0.52, yy, ZT + 0.09), (0.57, yy, ZT + 0.09), 0.01, _ST); b.rod((0.57, yy, ZT + 0.09), (0.57, yy, ZT + 0.05), 0.007, _ST)
b.lathe(0.42, 13.2, ZT, [(0.0, 0.0), (0.05, 0.0), (0.12, 0.07), (0.115, 0.075), (0.045, 0.012), (0.0, 0.012)], _BR, 18)
for k in range(5):
    a = k * 1.26; b.lathe(0.42 + 0.05 * math.cos(a), 13.2 + 0.05 * math.sin(a), ZT + 0.04, [(0.0, 0.0), (0.03, 0.01), (0.035, 0.035), (0.03, 0.06), (0.0, 0.07)], _DR[(1, 0)[k % 2]], 10)
for k in range(6): glass(b, 0.36 + 0.07 * (k % 2), 9.0 + 0.0 + 0.08 * (k // 2) + 0.2, ZT)
inst(b.mesh('Bar_equipment'), 'Bar_equipment', (0, 0, 0), 0, 'Bar')
# ---- shelves
b = MB(); XS0, XS1 = 0.215, 0.50
SEG = ((8.72, 10.24), (10.30, 11.82), (11.88, 13.36))
for si, zz in enumerate((1.50, 1.90, 2.30)):
    zs = F0 + zz
    for (ya, yb) in SEG:
        b.box(XS0, ya, zs - 0.04, XS1, yb, zs, _WD, 0.004); b.box(XS1 - 0.03, ya + 0.02, zs - 0.05, XS1 - 0.012, yb - 0.02, zs - 0.04, _LED0)
        for yy in (ya + 0.12, yb - 0.12):                                                  # brass brackets
            b.box(XS0, yy - 0.01, zs - 0.2, XS0 + 0.012, yy + 0.01, zs - 0.04, _BR); b.rod((XS0 + 0.012, yy, zs - 0.19), (XS1 - 0.06, yy, zs - 0.045), 0.006, _BR)
        b.rod((XS1 - 0.012, ya + 0.02, zs + 0.05), (XS1 - 0.012, yb - 0.02, zs + 0.05), 0.004, _BR)   # gallery rail
        for yy in (ya + 0.02, (ya + yb) / 2, yb - 0.02): b.rod((XS1 - 0.012, yy, zs), (XS1 - 0.012, yy, zs + 0.05), 0.004, _BR)
        L = yb - ya; kind = (si + SEG.index((ya, yb))) % 3
        if kind == 0:                                                                       # cups + saucers
            for k in range(int((L - 0.2) / 0.105)):
                yy = ya + 0.12 + k * 0.105
                if k % 5 == 4: saucers(b, 0.36, yy, zs, 8)
                else:
                    cup(b, 0.36, yy, zs); cup(b, 0.36, yy, zs + 0.062)
        elif kind == 1:                                                                     # syrups with pumps + tins
            for k in range(int((L - 0.2) / 0.1)):
                yy = ya + 0.12 + k * 0.1
                if k % 6 == 5: b.box(0.3, yy - 0.04, zs, 0.42, yy + 0.04, zs + 0.14, _BR, 0.004)
                else:
                    bottle(b, 0.36, yy, zs, 0.26, _DR[k % 6]); b.rod((0.36, yy, zs + 0.27), (0.36, yy, zs + 0.31), 0.004, _BK); b.rod((0.36, yy, zs + 0.31), (0.4, yy, zs + 0.305), 0.004, _BK)
        else:                                                                               # glasses + jars + a plant
            n = int((L - 0.2) / 0.085)
            for k in range(n):
                yy = ya + 0.12 + k * 0.085
                if k == n // 2:
                    b.lathe(0.36, yy, zs, [(0.0, 0.0), (0.045, 0.0), (0.06, 0.1), (0.0, 0.1)], mat('pot_terracotta', (0.62, 0.33, 0.2), rough=0.85), 14)
                    b.lathe(0.36, yy, zs + 0.1, [(0.0, 0.0), (0.07, 0.03), (0.09, 0.1), (0.05, 0.17), (0.0, 0.19)], mat('herb_green', (0.12, 0.35, 0.1), rough=0.7), 10)
                elif k % 7 == 6: b.cyl(0.36, yy, zs, zs + 0.16, 0.038, _GL, 12); b.cyl(0.36, yy, zs + 0.16, zs + 0.175, 0.04, _BR, 12)
                else:
                    glass(b, 0.33, yy, zs); glass(b, 0.41, yy, zs)
for yd in (8.70, 10.27, 11.85, 13.38):
    b.box(XS0, yd - 0.015, F0 + 1.46, XS1, yd + 0.015, F0 + 2.36, _WD, 0.002)
inst(b.mesh('Bar_shelves'), 'Bar_shelves', (0, 0, 0), 0, 'Bar')
print('rev 12.0 block 2: bar wall bricks rows', row)
