import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from bl import *
sc = reset(); m = M()
OUT, W, H, S = sys.argv[-4], int(sys.argv[-3]), int(sys.argv[-2]), int(sys.argv[-1])
# alley runs along +x from the street (x=0) to the hall (x=13); width 2.5 (y -1.25..1.25)
box(-2, -8, -0.05, 16, 8, 0, m['floor'])
box(0, -1.25, 0.0, 9.6, 1.25, 0.004, m['girih'])
slat_ceiling(m, -1, 16, -8, 8, 3.7, axis='Y')
# street entrance portal: two clad columns + lintel with majolica band
for sy in (-1, 1):
    box(-0.35, sy * 1.25 - (0.35 if sy > 0 else 0), 0, 0.05, sy * 1.25 + (0 if sy > 0 else 0.35) - (0 if sy > 0 else 0), 3.3, m['walnut'])
box(-0.35, -1.6, 3.3, 0.05, 1.6, 3.7, m['band'])
# three pointed portals over the alley (plaster with lapis reveal) + lanterns
for x0 in (2.3, 5.2, 8.1):
    fr = box(x0 - 0.15, -1.75, 0, x0 + 0.15, 1.75, 3.45, m['plaster_l'], name='p')
    cut(fr, prism_xz([(p[0], p[1]) for p in arch_pts(0, 2.5, -0.1, 2.45, 3.15)], -0.5, 0.5, None, 'c'))
    fr.rotation_euler[2] = 0
    # rotate cutter approach: build arch in YZ by prism in XZ then rotate 90
    bpy.data.objects.remove(fr, do_unlink=True)
    o = prism_xz(arch_pts(0, 3.5, 0, 3.45, 3.46), -0.15, 0.15, m['plaster_l'], 'pf')
    c = prism_xz(arch_pts(0, 2.5, -0.1, 2.45, 3.15), -0.3, 0.3, None, 'pc'); cut(o, c)
    o.rotation_euler[2] = math.pi / 2; o.location = (x0, 0, 0)
    r = pointed_frame(m['lapis'], 0, -0.16, 0.16, 2.5, 2.45, 3.15, t=0.06, z0=0)
    r.rotation_euler[2] = math.pi / 2; r.location = (x0, 0, 0)
    lantern(m, x0 + 1.45, 0, 2.6, s=1.1, rod_top=3.7, energy=28)
# raised aivan platform + steps + glass facade with doors at the end
for k in range(3): box(9.6 + k * 0.3, -1.6, 0, 10.5, 1.6, 0.157 * (k + 1), m['oak'], bevel=0.004)
box(10.5, -4, 0, 13, 4, 0.47, m['oak'], bevel=0.004)
for yy in (-4, -1.6, 1.6, 4):
    if abs(yy) > 2: box(10.5, yy - 0.03, 0.47, 10.55, yy + 0.03, 1.37, m['brass'])
box(10.5, -4, 1.33, 10.56, -1.6, 1.37, m['walnut']); box(10.5, 1.6, 1.33, 10.56, 4, 1.37, m['walnut'])
box(13, -6, 0.47, 13.05, 6, 3.6, m['glass'])
for yy in (-3.4, -1.7, 0, 1.7, 3.4): box(12.97, yy - 0.04, 0.47, 13.08, yy + 0.04, 3.6, m['walnut'])
box(12.97, -6, 3.0, 13.08, 6, 3.08, m['walnut'])
box(14, -6, 0.47, 16, 6, 3.6, m['plaster'])
for yy in (-2.5, 0, 2.5): lantern(m, 13.6, yy, 2.6, s=1.2, rod_top=3.6, energy=20)                                                # warm hall beyond
area(14.5, 0, 3.0, 4, 110, color=(1, 0.8, 0.55), rot=(0, 0, 0))
# left: chinar court south (tree + round bench); right: booth screens + planter
tx_, ty_ = 3.6, -3.8
cyl(tx_, ty_, 2.2, 0.28, 4.4, mat('bark', (0.30, 0.24, 0.18), rough=0.9, bump=0.3), verts=24)
for k in range(9): bush(m, tx_ + 1.4 * math.cos(k * 0.7), ty_ + 1.4 * math.sin(k * 0.7), 3.2, 1.1, n=8, seed=60 + k)
torus(tx_, ty_, 0.45, 1.2, 0.2, m['walnut'])
for k, x in enumerate((6.5, 8.5)):
    for sy in (-1, 1): chair(m, x, -3.0 + sy * 0.62, face=-sy * math.pi / 2)
    table(m, x, -3.0, 1.2, 0.8)
for k in range(4):
    yy = 2.4
    xs = 1.0 + k * 2.0
    o = prism_xz(arch_pts(0, 1.3, 0, 1.75, 2.15), -0.03, 0.03, m['jali'], 'scr'); o.location = (xs, yy + 0.65, 0)
    o.rotation_euler[2] = 0
for x in range(0, 9): bush(m, x, 4.6, 0.0, 0.8, n=6, seed=x + 90)
point(1.5, 0.0, 0.15, 10)
area(4, 0, 3.5, 6, 80, rot=(0, 0, 0))
camera((-0.9, 0.25, 1.6), (10, -0.15, 1.45), lens=22)
render(OUT, W, H, S)
