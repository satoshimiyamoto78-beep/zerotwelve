import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bl
from bl import *

sc = reset(); m = M()
OUT, W, H, S = sys.argv[-4], int(sys.argv[-3]), int(sys.argv[-2]), int(sys.argv[-1])

# floor + ceiling
box(-3, -2.2, -0.05, 10, 8, 0, m['floor'])
box(-3, -2.2, -0.05, -0.9, 8, 0.002, m['terrazzo'])
slat_ceiling(m, -3, 10, -2.2, 8, 3.55)
for yb in (-1.5, 1.6, 4.7): box(-3, yb - 0.1, 3.35, 10, yb + 0.1, 3.55, m['walnut'])

# ---- back wall: lime plaster with three mihrab niches + majolica frieze ----
wall = box(-1.2, -1.85, 0, 7.2, -1.45, 3.35, m['plaster'], name='wall')
NICH = [(1.0, 1.25, 2.25, 2.85, 'side'), (3.0, 1.55, 2.35, 3.08, 'mid'), (5.0, 1.25, 2.25, 2.85, 'side')]
for cx, w, zs, za, kind in NICH:
    cut(wall, prism_xz(arch_pts(cx, w, 1.02, zs, za), -1.70, -1.40, None, 'c'))
    if kind == 'mid':
        prism_xz(arch_pts(cx, w, 1.02, zs, za), -1.70, -1.69, m['majolica'], 'back')
        pointed_frame(m['brass'], cx, -1.46, -1.43, w, zs, za, t=0.035, z0=1.02)
    else:
        prism_xz(arch_pts(cx, w, 1.02, zs, za), -1.70, -1.69, m['plaster_l'], 'back')
        pointed_frame(m['lapis'], cx, -1.46, -1.42, w, zs, za, t=0.05, z0=1.02)
        for zz in (1.45, 1.9):
            box(cx - w / 2 + 0.02, -1.69, zz - 0.02, cx + w / 2 - 0.02, -1.46, zz, m['brass'])
            for k in range(6):
                bottle(m, cx - w / 2 + 0.16 + k * (w - 0.3) / 5, -1.58, zz, k)
        for k in range(5): bottle(m, cx - w / 2 + 0.2 + k * (w - 0.4) / 4, -1.58, 1.02, k + 1)
    area(cx, -1.50, zs + 0.2, 0.5, 9 if kind == 'side' else 14, rot=(math.radians(-90 - 25), 0, 0))
samovar(m, 3.0, -1.56, 1.02, s=1.15)
for k, dx in enumerate((-0.45, 0.45)):
    lathe(3.0 + dx, -1.56, 1.02, [(0, 0), (0.05, 0), (0.08, 0.05), (0.075, 0.1), (0.04, 0.13), (0.02, 0.16), (0, 0.17)], m['turq'])
box(-1.2, -1.45, 3.12, 7.2, -1.42, 3.35, m['band'])                     # majolica frieze
box(-1.2, -1.45, 3.08, 7.2, -1.40, 3.12, m['brass'])

# ---- back counter: walnut cabinetry with brass pulls, terrazzo top ----
box(-1.1, -1.45, 0, 7.1, -0.9, 0.9, m['walnut'], bevel=0.005)
for k in range(12):
    x0 = -1.05 + k * 0.68
    box(x0 + 0.02, -0.905, 0.12, x0 + 0.64, -0.895, 0.86, m['oak'], bevel=0.003)
    box(x0 + 0.3, -0.89, 0.62, x0 + 0.36, -0.87, 0.7, m['brass'])
box(-1.15, -1.47, 0.9, 7.15, -0.86, 0.95, m['terrazzo'], bevel=0.004)
box(1.9, -1.2, 0.95, 2.3, -0.95, 1.35, m['steel'], bevel=0.01)          # espresso machine
box(1.85, -1.22, 1.35, 2.35, -0.93, 1.38, m['brass'])

# ---- bar counter: fluted lapis glaze, brass, terrazzo top ----
BX0, BX1 = 0.0, 6.0
box(BX0, 0.0, 0.12, BX1, 0.6, 1.02, m['walnut'])
box(BX0 + 0.02, 0.0, 0.0, BX1 - 0.02, 0.52, 0.12, m['black'])          # recessed kick
x = BX0 + 0.045
while x < BX1 - 0.04:
    cyl(x, 0.6, 0.57, 0.043, 0.9, m['lapis'], verts=20)
    x += 0.09
for xe in (BX0 - 0.05, BX1 + 0.05):                                      # plaster end caps with brass reveal
    box(xe - 0.1 if xe < 1 else xe - 0.05, -0.05, 0, xe + 0.05 if xe < 1 else xe + 0.1, 0.7, 1.02, m['plaster_l'], bevel=0.01)
box(BX0, 0.55, 1.0, BX1, 0.66, 1.03, m['brass'])
box(BX0 - 0.2, -0.08, 1.03, BX1 + 0.2, 0.98, 1.09, m['terrazzo'], bevel=0.006)
box(BX0 - 0.2, 0.98, 1.03, BX1 + 0.2, 0.995, 1.09, m['brass'])
box(BX0 + 0.05, 0.7, 0.11, BX1 - 0.05, 0.72, 0.125, m['glow'])         # warm toe-kick LED
cyl((BX0 + BX1) / 2, 0.84, 0.25, 0.022, BX1 - BX0 - 0.3, m['brass'], axis='X')
for xb in (0.4, 2.0, 4.0, 5.6):
    cyl(xb, 0.73, 0.25, 0.012, 0.22, m['brass'], axis='Y')
# working surface behind
box(BX0, -0.5, 0.86, BX1, 0.0, 0.9, m['steel'])
for k in range(9):
    stool(m, 0.45 + k * 0.64, 1.38)

# ---- suspended walnut canopy + lanterns over the counter ----
for yy in (0.15, 0.85):
    box(-0.3, yy - 0.04, 2.5, 6.3, yy + 0.04, 2.58, m['walnut'])
for xx in [-0.3 + k * 0.33 for k in range(20)]:
    box(xx, 0.11, 2.58, xx + 0.04, 0.89, 2.61, m['oak'])
for xx in (0.0, 6.0):
    for yy in (0.15, 0.85): cyl(xx, yy, 3.0, 0.008, 0.9, m['brass'], verts=10)
for xx in (0.9, 2.3, 3.7, 5.1):
    lantern(m, xx, 0.5, 2.05, s=1.0, rod_top=2.5, energy=28)

# ---- context: wood-clad column, plants, a glimpse of the dining ----
box(7.25, 1.5, 0, 7.55, 1.8, 3.35, m['walnut'])
potted_tree(m, -0.75, 1.2, s=1.1, seed=4)
potted_tree(m, 6.85, 0.5, s=0.9, seed=7)
for xx, yy in ((8.5, 3.6),):
    box(xx - 0.6, yy - 0.4, 0.73, xx + 0.6, yy + 0.4, 0.77, m['oak'], bevel=0.01)
area(3.0, 2.5, 3.3, 5.0, 45, color=(1, 0.82, 0.62), rot=(0, 0, 0))
for yy in range(-1, 7):
    bush(m, 9.6, yy, 0.0, 0.7, n=5, seed=yy + 20)
for yy in (-0.5, 3.0, 6.5):
    box(8.7, yy - 0.15, 0, 9.0, yy + 0.15, 3.35, m['walnut'])
box(9.0, -2, 0, 12, 8, 0.6, m['brick'])
area(3.0, 7.5, 2.0, 6.0, 60, color=(0.55, 0.65, 1.0), rot=(math.radians(80), 0, math.radians(180)))

camera((7.4, 5.3, 1.55), (2.7, -0.7, 1.45), lens=24)
render(OUT, W, H, S)
