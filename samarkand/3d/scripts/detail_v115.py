"""rev. 11.5 (owner ref: arched passage — 'wind and rain will throw the fabric around, make it simpler'):
the entrance corridor becomes an arcade of 4 pointed walnut arches (160 mm face, 140 mm deep) across the passage; between them,
on both walls, pierced girih lattice panels (walnut, laser-cut pattern, frame 60 mm) with a warm uplight at the foot of each;
small cascade chandeliers hang between the arches on the centre line; only short velvet sashes tied back with brass rings at
the arch posts (no loose drapery); terracotta jug groups in the bays. The rugs stay."""
from shapely.geometry import Polygon as _P15
keep_ = ('Corridor_rug',)
for o_ in [o for o in bpy.data.collections['Corridor'].all_objects if not o.name.startswith(keep_)]: bpy.data.objects.remove(o_)
Y0c, Y1c = 15.64, 17.96; YC = (Y0c + Y1c) / 2; WOP = 2.0                       # clear opening 2.0 between the posts
ARX = [7.75, 8.6, 9.45, 10.25]; ZS_, ZA_ = TER + 2.15, TER + 2.95
def ceil_z(x): return top(x) - 0.70 - 0.05                                     # under the coffer grid (rev 10.9)
b = MB(); W_ = XW['wd']
inner = _P15([(YC - WOP / 2, TER - 0.1)] + arch_left(YC, WOP, ZS_, ZA_, 16) + [(2 * YC - u, z) for u, z in arch_left(YC, WOP, ZS_, ZA_, 16)[::-1][1:]] + [(YC + WOP / 2, TER - 0.1)])
outer = inner.buffer(0.16, join_style=1).intersection(_P15([(Y0c, TER), (Y1c, TER), (Y1c, 9), (Y0c, 9)]))
frame = outer.difference(inner)
for x in ARX:
    za_top = min(ceil_z(x) - 0.01, ZA_ + 0.16)
    fr = frame.intersection(_P15([(Y0c, TER), (Y1c, TER), (Y1c, za_top), (Y0c, za_top)]))
    for g in (getattr(fr, 'geoms', None) or [fr]):
        if g.geom_type == 'Polygon': ext_holes(b, g, x - 0.07, x + 0.07, W_, 'yz')
    b.box(x - 0.08, Y0c, TER, x + 0.08, Y0c + 0.18, TER + 0.12, m['brass'], 0.003)          # brass shoes on the posts
    b.box(x - 0.08, Y1c - 0.18, TER, x + 0.08, Y1c, TER + 0.12, m['brass'], 0.003)
inst(b.mesh('Corridor_arches'), 'Corridor_arches', (0, 0, 0), 0, 'Corridor')
# pierced lattice wall panels between the arches + uplights
b = MB(); LED_ = mat('led_warm', (1.0, 0.72, 0.42), emit=(1.0, 0.72, 0.42), strength=6.0)
bays = [(ARX[k] + 0.08, ARX[k + 1] - 0.08) for k in range(3)]
for xa, xb in bays:
    for yy, s in ((Y0c, 1), (Y1c, -1)):
        for q in lattice_poly(xa, TER + 0.06, xb, ZS_ + 0.35, 'star', 0.16, 0.014, 0.06):
            ext_holes(b, q, yy + (0.0 if s > 0 else -0.03), yy + (0.03 if s > 0 else 0.0), W_, 'xz')
        b.box(xa + 0.05, yy + (0.035 if s > 0 else -0.065), TER, xb - 0.05, yy + (0.065 if s > 0 else -0.035), TER + 0.02, LED_)   # uplight strip
inst(b.mesh('Corridor_lattice'), 'Corridor_lattice', (0, 0, 0), 0, 'Corridor')
# chandeliers between the arches
for k, (xa, xb) in enumerate(bays):
    xm = (xa + xb) / 2; zt = ceil_z(xm)
    mini_cascade(f'Corridor_lantern_hang_{k + 1}', xm, YC, zt, TER + 2.05, 'Corridor', 0.16)
# short tied-back velvet sashes at the posts (owner: a little fabric, nothing loose)
b = MB(); VELV_ = bl._mats.get('velvet_wine89') or X['velvet_wine']
for x in ARX[1:3]:
    for yy, s in ((Y0c + 0.17, 1), (Y1c - 0.17, -1)):
        poly = [(x - 0.12, ZS_ - 0.02), (x + 0.12, ZS_ - 0.02), (x + 0.04, TER + 1.05), (x + 0.06, TER + 0.55), (x - 0.06, TER + 0.55), (x - 0.04, TER + 1.05)]
        b.extrude(poly, yy + (0.0 if s > 0 else -0.04), yy + (0.04 if s > 0 else 0.0), VELV_, 'xz')
        b.lathe(x, yy + s * 0.02, TER + 1.03, [(0.0, 0.0), (0.07, 0.0), (0.075, 0.02), (0.0, 0.02)], m['brass'], 16)
inst(b.mesh('Corridor_sashes'), 'Corridor_sashes', (0, 0, 0), 0, 'Corridor')
# jug groups in the bays (clear of the rugs' walkway)
nj15 = 0
for xa, xb in bays:
    for yy, s in ((Y0c + 0.3, 1), (Y1c - 0.3, -1)):
        for h, dx in ((0.8, 0.0), (0.55, 0.22), (0.38, -0.2)):
            loc = ((xa + xb) / 2 + dx, yy + s * (0.03 if h < 0.8 else 0.0), TER)
            if _free(JUG[h], loc, skip=('Corridor_rug', 'alley', 'terrace_floor')): inst(JUG[h], f'Corridor_jug_{nj15}', loc, dx, 'Corridor'); nj15 += 1
print('rev 11.5 corridor arcade: arches', len(ARX), 'jugs', nj15)
