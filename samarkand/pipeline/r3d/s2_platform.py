import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from bl2 import *
sc = reset(); m = M2()
OUT, W, H, S = sys.argv[-4], int(sys.argv[-3]), int(sys.argv[-2]), int(sys.argv[-1])
# aivan platform 3.3 m wide along the facade (x 0 = glass facade, x 3.3 = rail), looking along it
box(-1, -2, -0.05, 12, 18, 0, m['floor'])
box(0, -2, 0, 3.3, 16, 0.47, m['deck'])
slat_ceiling(m, -1, 12, -2, 18, 3.9)
box(-1, -2, 3.6, 1.55, 18, 3.9, m['plaster_l'])                              # balcony soffit above
# glass facade with walnut mullions, two open doors, one closed (table in front)
box(-0.05, -2, 0.47, 0.0, 16, 3.6, m['glass'])
for y in [-2 + k * 1.68 for k in range(11)]: box(-0.08, y - 0.04, 0.47, 0.04, y + 0.04, 3.6, m['walnut'])
box(-0.08, -2, 2.9, 0.04, 16, 2.98, m['walnut'])
for y0 in (1.4, 9.8):
    for k, sgn in enumerate((-1, 1)):
        o = box(0.0, y0 + (0 if sgn < 0 else 0.8), 0.47, 0.6, y0 + (0.04 if sgn < 0 else 0.84), 2.6, m['glass'])
        box(0.0, y0 + (0 if sgn < 0 else 0.8), 2.55, 0.6, y0 + (0.05 if sgn < 0 else 0.85), 2.6, m['walnut'])
box(-3, -2, 0.47, -0.1, 18, 3.6, m['plaster'])
for y in (1.0, 6.0, 11.0): lantern(m, -1.5, y, 2.6, s=1.2, rod_top=3.6, energy=25)
# rail: walnut handrail on jali panels with brass posts
for y0 in [-1.6 + k * 1.2 for k in range(14)]:
    if 6.5 < y0 < 8.4: continue                                                # gap for the staff steps
    box(3.22, y0, 0.47, 3.28, y0 + 1.15, 1.3, m['jali'])
    cyl(3.25, y0, 0.9, 0.025, 0.9, m['brass'], verts=16)
box(3.18, -1.6, 1.3, 3.34, 6.5, 1.36, m['walnut']); box(3.18, 8.4, 1.3, 3.34, 15.5, 1.36, m['walnut'])
for k in range(3): box(3.3 + k * 0.3, 6.5, 0, 4.2, 8.4, 0.47 - 0.157 * (k + 1) + 0.157, m['oak'])
# tables for 4 on the deck (chairs N/S), set for dinner
for y in (2.9, 5.1, 10.0, 12.2):
    for x in (0.85, 2.45):
        before = set(bpy.data.objects)
        table4(m, x, y, w=1.2, d=0.8, h=0.75, chairs='NS', seed=int(x * 10 + y))
        for o in set(bpy.data.objects) - before: o.location.z += 0.47
# terrace below: chinar tree, tables, lanterns
cyl(7.0, 6.5, 2.0, 0.3, 4.0, mat('bark', (0.30, 0.24, 0.18), rough=0.9, bump=0.3), verts=24)
for k in range(8): bush(m, 7.0 + 1.5 * math.cos(k * 0.8), 6.5 + 1.5 * math.sin(k * 0.8), 2.6, 1.2, seed=400 + k)
torus(7.0, 6.5, 0.45, 1.2, 0.2, m['walnut'])
for y in (1.5, 11.5): table4(m, 6.2, y, chairs='NS', seed=int(y))
for y in (3.0, 9.0, 14.0): lantern(m, 5.5, y, 2.6, s=1.1, rod_top=3.9, energy=25)
area(1.6, 7, 3.55, 4, 90, rot=(0, 0, 0))
camera((1.9, -1.9, 2.15), (1.4, 9.0, 1.1), lens=24, fstop=5.6, focus=6.0)
render(OUT, W, H, S)
