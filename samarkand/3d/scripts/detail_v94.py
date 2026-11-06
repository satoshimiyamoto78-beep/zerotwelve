"""rev. 9.4 (owner ref: Moorish courtyard fountain, "no photo textures — real tiles, real bricks"):
fountain court rebuilt in real pieces inside the old medallion
  * eight-point-star basin (two squares, tips R 0.95): wall clad in 50 mm glazed tiles, white stone cap, turquoise mosaic floor,
    water at +0.30; central scalloped bowl on a turned pedestal with a jet
  * zellige cross: 40 mm glazed pieces with 3 mm grout in a cobalt/white/turquoise/ochre star rhythm, a mosaic band round the
    star; the north arm runs along the existing aryk channel
  * the rest of the court in 200 mm terracotta floor tiles laid diagonally, 5 mm joints, cut at every edge"""
from shapely.geometry import Polygon as SP_, box as SB_
from shapely.ops import unary_union as SU_
from shapely import affinity as SAff
_rm('hauz', 'hauz_rim', 'Hauz_coping', 'Hauz_lotus_jet')
HX, HY = D['hzc']; R = 0.95
star = SU_([SAff.rotate(SB_(HX - R / 2 ** 0.5, HY - R / 2 ** 0.5, HX + R / 2 ** 0.5, HY + R / 2 ** 0.5), a, origin=(HX, HY)) for a in (0, 45)])
inner = star.buffer(-0.1, join_style=2, mitre_limit=5)
MED = SP_(D['inlays']['medallion'][0])
ZG = mat('zellige_green', (0.05, 0.3, 0.15), rough=0.12, coat=0.9)
ZC = [TILE[0], TILE[1], TILE[2], TILE[3], ZG]
TERR = [terracotta(f'floor_terra_{k}', c, bump=0.3) for k, c in enumerate(((0.6, 0.32, 0.2), (0.56, 0.29, 0.18), (0.64, 0.36, 0.23)))]
STONE = mat('cap_stone_white', (0.86, 0.84, 0.79), rough=0.35, bump=0.15, noise_var=0.04)
# ---------------------------------------------------------------- lower the old medallion slab: it becomes the grout bed
md = bpy.data.objects.get('medallion_mosaic')
if md:
    for v in md.data.vertices:
        if abs((md.matrix_world @ v.co).z - TER) < 1e-4: v.co.z -= 0.015
    for i_ in range(len(md.data.materials)): md.data.materials[i_] = MORTAR
ZT0, ZT1 = TER - 0.015, TER - 0.003
def lay(b, region, pitch, size, ang, mats, pick, minfrac=0.25):
    """lay square tiles of `size` on a grid of `pitch` rotated by ang about the hauz centre; cut to `region`"""
    if region.is_empty: return 0
    n = int(2.2 / pitch) + 2; c, s = math.cos(ang), math.sin(ang); cnt = 0
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            u, v = i * pitch, j * pitch
            sq = [(u + du, v + dv) for du, dv in ((0, 0), (size, 0), (size, size), (0, size))]
            pg = SP_([(HX + x * c - y * s, HY + x * s + y * c) for x, y in sq])
            if not pg.intersects(region): continue
            cut = pg.intersection(region)
            for q in ([cut] if cut.geom_type == 'Polygon' else [g for g in getattr(cut, 'geoms', []) if g.geom_type == 'Polygon']):
                if q.area < size * size * minfrac * 0.2: continue
                b.extrude(list(q.exterior.coords)[:-1], ZT0, ZT1, mats[pick(i, j)]); cnt += 1
    return cnt
aryk_buf = SB_(5.84, 30.1, 6.30, 40.0)
W2 = 0.3
arms = SU_([SB_(HX, HY - W2, 9.0, HY + W2), SB_(3.0, HY - W2, HX, HY + W2), SB_(HX - W2, 26.0, HX + W2, HY), SB_(HX - W2, HY, HX + W2, 33.0)])
band = star.buffer(0.14, join_style=2, mitre_limit=5).difference(star)
Z = SU_([arms, band]).intersection(MED).difference(star.buffer(0.005, join_style=2)).difference(aryk_buf)
T = MED.difference(star.buffer(0.005, join_style=2)).difference(Z.buffer(0.004)).difference(aryk_buf)
def zpick(i, j):
    a, b_ = i % 6, j % 6
    if (a in (2, 3)) and (b_ in (2, 3)): return 3                     # ochre star centres
    if (a in (1, 4) and b_ in (2, 3)) or (b_ in (1, 4) and a in (2, 3)): return 0   # cobalt star points
    if a == 0 or b_ == 0: return 1 if (i + j) % 2 else 2               # white / turquoise lattice
    return 4 if (a + b_) % 2 else 1
mb = MB(); nz = lay(mb, Z, 0.043, 0.04, 0.0, ZC, zpick)
inst(mb.mesh('Court_zellige'), 'Court_zellige', (0, 0, 0), 0, 'Fountain')
mb = MB(); _r = _rnd.Random(4); nt = lay(mb, T, 0.205, 0.2, math.pi / 4, TERR, lambda i, j: _r.randrange(3))
inst(mb.mesh('Court_terracotta'), 'Court_terracotta', (0, 0, 0), 0, 'Fountain')

# ---------------------------------------------------------------- star basin
ring = star.difference(inner)
mb = MB(); ZW, ZC_ = TER + 0.40, TER + 0.43
for q in ([ring] if ring.geom_type == 'Polygon' else list(ring.geoms)): ext_holes(mb, q, TER, ZW, MORTAR, 'xy')
capr = star.buffer(0.015, join_style=2, mitre_limit=5).difference(inner.buffer(-0.01, join_style=2, mitre_limit=5))
for q in ([capr] if capr.geom_type == 'Polygon' else list(capr.geoms)): ext_holes(mb, q, ZW, ZC_, STONE, 'xy')
inst(mb.mesh('Hauz_star_wall'), 'Hauz_star_wall', (0, 0, 0), 0, 'Fountain')
mb = MB(); pts = list(star.exterior.coords)[:-1]; TS = 0.05
if not SP_(pts).exterior.is_ccw: pts = pts[::-1]
for k in range(len(pts)):                                                                        # 50 mm glazed tiles on every outer face
    (xa4, ya4), (xb4, yb4) = pts[k], pts[(k + 1) % len(pts)]; L = math.hypot(xb4 - xa4, yb4 - ya4); an = math.atan2(yb4 - ya4, xb4 - xa4)
    nx, ny = math.sin(an), -math.cos(an)                                                          # outward normal of a CCW ring
    n = max(1, int(L / (TS + 0.003))); st_ = (L - n * (TS + 0.003)) / 2 + (TS + 0.003) / 2
    for i in range(n):
        t = st_ + i * (TS + 0.003); cx, cy = xa4 + (xb4 - xa4) * t / L + nx * 0.004, ya4 + (yb4 - ya4) * t / L + ny * 0.004
        for j in range(7):
            z0 = TER + j * (TS + 0.003)
            mm = TILE[0] if j in (0, 6) else (TILE[2] if (i + j) % 2 else TILE[1])
            if j == 3: mm = TILE[3]
            mb.obox(cx, cy, z0, z0 + TS, TS, 0.007, an, mm)
inst(mb.mesh('Hauz_star_tiles'), 'Hauz_star_tiles', (0, 0, 0), 0, 'Fountain')
mb = MB()
for q in ([inner] if inner.geom_type == 'Polygon' else list(inner.geoms)): ext_holes(mb, q, TER, TER + 0.05, TILE[2], 'xy')   # turquoise mosaic floor
inst(mb.mesh('Hauz_star_floor'), 'Hauz_star_floor', (0, 0, 0), 0, 'Fountain')
mb = MB(); wat = inner.difference(SP_([(HX + 0.052 * math.cos(2 * math.pi * k / 24), HY + 0.052 * math.sin(2 * math.pi * k / 24)) for k in range(24)]))
for q in ([wat] if wat.geom_type == 'Polygon' else list(wat.geoms)): ext_holes(mb, q, TER + 0.29, TER + 0.30, m['water'], 'xy')
inst(mb.mesh('Hauz_star_water'), 'Hauz_star_water', (0, 0, 0), 0, 'Fountain')
mb = MB()                                                                                         # central scalloped bowl + jet
mb.lathe(HX, HY, TER + 0.05, [(0.0, 0.0), (0.12, 0.0), (0.12, 0.03), (0.06, 0.06), (0.05, 0.3), (0.07, 0.34), (0.0, 0.34)], STONE, 24)
prof = [(0.0, 0.0), (0.06, 0.0), (0.16, 0.05), (0.24, 0.09), (0.25, 0.11), (0.0, 0.11)]
mb.lathe(HX, HY, TER + 0.39, prof, STONE, 32)
for k in range(16):
    a = 2 * math.pi * k / 16; mb.lathe(HX + 0.245 * math.cos(a), HY + 0.245 * math.sin(a), TER + 0.47, [(0.0, 0.0), (0.035, 0.0), (0.04, 0.02), (0.0, 0.035)], STONE, 10)
mb.lathe(HX, HY, TER + 0.5, [(0.0, 0.0), (0.03, 0.0), (0.02, 0.08), (0.008, 0.25), (0.0, 0.28)], m['glass'], 12)
inst(mb.mesh('Hauz_star_bowl'), 'Hauz_star_bowl', (0, 0, 0), 0, 'Fountain')
# aryk starts at the north tip
ytip = HY + R
for n_ in ('aryk_channel', 'aryk_water', 'Aryk_edges'):
    o_ = bpy.data.objects.get(n_)
    if o_:
        for v in o_.data.vertices:
            w_ = o_.matrix_world @ v.co
            if w_.y < ytip + 0.005: w_.y = ytip + 0.005; v.co = o_.matrix_world.inverted() @ w_
print('rev 9.4 fountain ok: zellige', nz, 'terracotta', nt)
