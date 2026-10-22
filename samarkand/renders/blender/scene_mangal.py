import sys, os, math, random
sys.path.insert(0, os.path.dirname(__file__))
from bl import *
sc = reset(); m = M()
OUT, W, H, S = sys.argv[-4], int(sys.argv[-3]), int(sys.argv[-2]), int(sys.argv[-1])
slate = mat('slatef', (0.18, 0.17, 0.16), rough=0.6, noise_var=0.03)
box(-5, -2, -0.05, 9, 7, 0, m['floor']); box(-0.2, -1.6, 0.0, 6.4, 1.6, 0.004, slate)
slat_ceiling(m, -5, 9, -2, 7, 3.5)
# brick fire wall
box(-0.2, -1.6, 0, 6.4, -1.35, 3.5, m['brick'])
for z in [0.075 * k for k in range(1, 46)]: box(-0.2, -1.36, z, 6.4, -1.345, z + 0.006, mat('mortar', (0.7, 0.62, 0.52), rough=0.95))
# tandoor: clay dome in a tiled block
box(0.0, -1.35, 0, 1.1, -0.25, 0.85, m['majolica'], bevel=0.01)
lathe(0.55, -0.8, 0.85, [(0.42, 0), (0.42, 0.12), (0.34, 0.32), (0.2, 0.42), (0.16, 0.44), (0.16, 0.46), (0, 0.46)], m['clay'])
cyl(0.55, -0.8, 1.31, 0.17, 0.03, m['black'])
# mangal: black steel trough with glowing coals and skewers
box(1.4, -1.3, 0, 3.8, -0.75, 0.72, m['black'], bevel=0.01)
box(1.42, -1.28, 0.72, 3.78, -0.77, 0.86, m['black'])
coal = mat('coal', (0.1, 0.03, 0.0), emit=(1.0, 0.25, 0.04), strength=6.0, rough=0.9)
rr = random.Random(5)
for k in range(140): sphere(1.5 + rr.random() * 2.2, -1.22 + rr.random() * 0.4, 0.74 + rr.random() * 0.04, 0.03 + rr.random() * 0.02, coal)
meat = mat('meat', (0.32, 0.12, 0.05), rough=0.6)
for k in range(14):
    x = 1.6 + k * 0.155
    cyl(x, -1.0, 0.9, 0.004, 0.75, m['steel'], axis='Y', verts=8)
    for j in range(5): sphere(x, -1.2 + j * 0.08, 0.9, 0.025, meat)
point(2.6, -1.0, 0.85, 60, color=(1.0, 0.4, 0.12), radius=0.3)
# kazan on a brick burner
box(4.1, -1.35, 0, 5.2, -0.25, 0.7, m['brick'], bevel=0.01)
lathe(4.65, -0.8, 0.7, [(0.1, -0.05), (0.38, 0.05), (0.48, 0.22), (0.5, 0.3), (0.47, 0.3), (0.45, 0.22), (0.36, 0.08), (0, 0.06)], m['black'])
plov = mat('plov', (0.85, 0.5, 0.15), rough=0.8, noise_var=0.08)
cyl(4.65, -0.8, 0.94, 0.42, 0.04, plov, verts=48)
point(4.65, -0.8, 0.3, 15, color=(0.4, 0.6, 1.0))
# sink + bins
box(5.4, -1.35, 0, 6.3, -0.75, 0.9, m['steel'], bevel=0.005)
# hood: black steel with brass band, over the hot line
box(-0.1, -1.35, 2.35, 5.3, -0.0, 2.75, m['black'], bevel=0.01)
box(-0.1, -0.02, 2.35, 5.3, 0.0, 2.45, m['brass'])
box(2.2, -1.2, 2.75, 2.8, -0.6, 3.5, m['black'])
for x in (0.6, 2.6, 4.6): area(x, -0.7, 2.33, 0.5, 20, rot=(0, 0, 0))
# pass counter with glass guard, heat lamps and bread
box(0.8, 0.85, 0, 6.3, 1.5, 0.9, m['steel'], bevel=0.005)
box(0.75, 0.82, 0.9, 6.35, 1.55, 0.95, m['terrazzo'], bevel=0.005)
box(0.8, 1.48, 0.95, 6.3, 1.5, 1.35, m['glass'])
for x in (2.2, 3.6, 5.0):
    cyl(x, 1.15, 1.7, 0.01, 0.8, m['brass'], verts=10); lathe(x, 1.15, 1.25, [(0.12, 0), (0.06, 0.1), (0.01, 0.15)], m['brass']); point(x, 1.15, 1.22, 18, color=(1, 0.55, 0.25))
non = mat('non', (0.78, 0.5, 0.25), rough=0.7, noise_var=0.06)
for k in range(6): cyl(3.0 + k * 0.32, 1.15, 0.97, 0.13, 0.03, non, verts=32)
for k in range(4): lathe(1.3 + k * 0.3, 1.1, 0.95, [(0, 0), (0.1, 0), (0.12, 0.03), (0, 0.03)], m['majolica'], steps=32)
# lanterns and context
for x in (-2.5, 8.5): lantern(m, x, 2.9, 2.5, s=1.0, rod_top=3.5, energy=22)
for x in (-1.5, 7.5): potted_tree(m, x, 1.5, s=1.0, seed=int(x * 3) + 30)
area(3, 4, 3.3, 5, 60, rot=(0, 0, 0))
camera((5.6, 4.3, 2.35), (2.4, -0.9, 0.9), lens=24)
render(OUT, W, H, S)
