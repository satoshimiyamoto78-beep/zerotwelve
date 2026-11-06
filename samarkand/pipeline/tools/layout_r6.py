"""Samarkand covered terrace — Layout R6 (owner review 2026-10-22, second round).
Changes vs R5: street façade with cast-in benches, sebil fountain and photo arch; mangal kitchen shorter and wider;
aivan platform reduced to one workable row (banquette along the hall wall); draped entrance corridor; majlis tent
in place of two tapchans; 2-tops at the north entrance; new photo zone (backlit jali arch, palms, rug).
Local mm (origin axis 6 x axis A', x east, y north). Outputs: JSON + DXF + A2 SVG sheets (RU/EN) at 1:100.
"""
import sys, json, math
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import split, unary_union
import ezdxf

Z = json.load(open(sys.argv[1])); BASE_DXF = sys.argv[2]; OUT = sys.argv[3]
L = Z['layers']; V = Z['zone_vertices']
REV, DATE = 'R6', '2026-10-22'

# ---------------- site ----------------
Z2, Z3 = V['Z2_NE'], V['Z3_SE']
SLOPE = (Z3[0] - Z2[0]) / (Z2[1] - Z3[1])
def xb(y): return Z3[0] - (y - Z3[1]) * SLOPE          # east boundary (lot line to the sidewalk)
def xi(y): return xb(y) - 1500                          # planter inner face
def yr(x): return 37090.5 - 0.06542 * (x - 83.6)        # driveway edge
def ys(x): return Z3[1] * (x - V['Z4_S'][0]) / (Z3[0] - V['Z4_S'][0])
zone = Polygon(Z['zone'])
U = sorted(split(zone, LineString([(-20000, yr(-20000)), (30000, yr(30000))])).geoms, key=lambda g: g.centroid.y)[0]
def R(x0, y0, x1, y1): return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
def C(x, y, r, n=48): return Point(x, y).buffer(r, n)
def OCT(x, y, r): return Polygon([(x + r * math.cos(math.radians(22.5 + 45 * i)), y + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)])
def BP(y0, y1, d0, d1):  # strip parallel to the slanted lot line, d0..d1 mm inward from it
    return Polygon([(xb(y0) - d1, y0), (xb(y0) - d0, y0), (xb(y1) - d0, y1), (xb(y1) - d1, y1)])

items = []
def add(kind, geom, layer='SMK-R6-FURN', **kw):
    items.append(dict(kind=kind, geom=geom, layer=layer, **kw)); return geom
seats = {}
def seat(k, n): seats[k] = seats.get(k, 0) + n
tables = []                                   # (x, y, kind) for table numbers

# ---------------- fixed decisions ----------------
ENT = (15550, 18050)                          # street entrance 2500
TREE_N, TREE_S = (5999, 27097), (5999, 12722)
DOORS = {'cd_s': (16795, 18475, True), 'cd_n': (18475, 20155, False), 'de_s': (22545, 24225, False), 'de_n': (24225, 25905, True), 'ef': (28663, 30363, True)}

band = Polygon([(xi(-500), -500), (xb(-500) + 10, -500), (xb(40000) + 10, 40000), (xi(40000), 40000)]).intersection(U)
gap = R(xi(ENT[0]) - 400, ENT[0], xb(ENT[0]) + 400, ENT[1])

# ======================= SOUTH =======================
KIDS = Polygon([V['Z5_pocketSW'], V['Z4_S'], V['Z7_bldgSE'], V['Z6_pocketNW']])
# photo zone (owner ref.): freestanding backlit jali arch, palms in terracotta pots, rug, lanterns + candles
add('phscreen', R(1700, 1700, 4900, 2050), 'SMK-R6-PHOTO')
add('phrug', R(2150, 2250, 4450, 3950), 'SMK-R6-PHOTO')
for c, r in (((1250, 2400), 340), ((5350, 2400), 340), ((1800, 2950), 230), ((4800, 2950), 230)):
    add('palm', C(*c, r, 32), 'SMK-R6-PHOTO')
for c in ((2000, 3800), (4600, 3800)): add('flantern', R(c[0] - 130, c[1] - 130, c[0] + 130, c[1] + 130), 'SMK-R6-PHOTO')
for c in ((2350, 2350), (2500, 2420), (4150, 2380), (4280, 2330)): add('candle', C(*c, 45, 12), 'SMK-R6-PHOTO')
add('camera', C(3300, 5000, 160, 24), 'SMK-R6-PHOTO')
photo_plant = Polygon([(1000, ys(1000)), (5800, ys(5800)), (5800, 1650), (1000, 1650)])
# staff service station
add('shelving', R(0, 4300, 600, 8350), 'SMK-R6-SERV')
add('counter', R(1400, 5300, 2000, 8100), 'SMK-R6-SERV')
add('screenwall', R(2000, 5300, 2080, 8400), 'SMK-R6-SERV')
# bar 5.7 m
BAR = (8600, 14300)
add('backbar', R(0, BAR[0], 550, BAR[1]), 'SMK-R6-BAR')
add('barbody', R(1500, BAR[0], 2100, BAR[1]), 'SMK-R6-BAR')
add('bartop', R(2100, BAR[0] - 100, 2400, BAR[1]), 'SMK-R6-BAR')
add('barreturn', R(1500, BAR[0] - 600, 2400, BAR[0]), 'SMK-R6-BAR')
add('samovar', C(275, 9300, 210, 32), 'SMK-R6-BAR'); add('coffee', R(60, 10200, 500, 10900), 'SMK-R6-BAR')
add('sink', R(80, 12900, 480, 13400), 'SMK-R6-BAR')
add('barsteps', R(550, 14300, 1500, 15300), 'SMK-R6-STEPS')
y = BAR[0] + 400
while y + 200 <= BAR[1] - 100:
    add('stool', C(2780, y, 200, 28), 'SMK-R6-BAR'); seat('bar', 1); y += 620
# MANGAL kitchen — shorter and wider: 4.2 x 4.8 m (was 3.2 x 6.1), pass faces the entrance plaza
BX0, BX1, BY0, BY1 = 8100, 12300, 3700, 8500
add('bbqfloor', R(BX0, BY0, BX1, BY1), 'SMK-R6-BBQ')
add('firewall', R(12150, BY0, BX1, BY1), 'SMK-R6-BBQ')
add('tandoorblock', R(11200, 3850, 12150, 4950), 'SMK-R6-BBQ'); add('tandoor', C(11675, 4400, 430), 'SMK-R6-BBQ')
add('mangal', R(11200, 5150, 11750, 7150), 'SMK-R6-BBQ'); add('ledge', R(11750, 5150, 12150, 7150), 'SMK-R6-BBQ')
add('kazanblock', R(11200, 7350, 12150, 8350), 'SMK-R6-BBQ'); add('kazan', C(11675, 7850, 380), 'SMK-R6-BBQ')
add('sinkbins', R(8900, 3700, 10900, 4300), 'SMK-R6-BBQ')
add('prep', R(BX0, 4800, BX0 + 650, 7700), 'SMK-R6-BBQ')
add('pass', R(BX0, 7850, 10900, BY1), 'SMK-R6-BBQ')
add('glass', R(BX0, BY1, 10900, BY1 + 40), 'SMK-R6-BBQ')
HOOD = R(11100, 3800, 12250, 8400); add('hood', HOOD, 'SMK-R6-BBQ')
add('storage', Polygon([(BX0, ys(BX0) + 150), (12150, ys(12150) + 150), (12150, BY0 - 50), (BX0, BY0 - 50)]), 'SMK-R6-BBQ')
bbq_plant = Polygon([(BX1, BY0 - 300), (xb(BY0 - 300), BY0 - 300), (xb(BY1 + 300), BY1 + 300), (BX1, BY1 + 300)]).intersection(U)

def table_ns(cx, cy, key, tl=1200, tw=800):
    add('table', R(cx - tl / 2, cy - tw / 2, cx + tl / 2, cy + tw / 2)); tables.append((cx, cy, key))
    for sy in (-1, 1):
        for sx in (-tl / 4, tl / 4):
            y0 = cy + sy * (tw / 2 + 40); add('chair', R(cx + sx - 225, y0, cx + sx + 225, y0 + sy * 450), back=('n' if sy > 0 else 's'), t=len(tables))
    seat(key, 4)
def table2(cx, cy, key):
    add('table', R(cx - 350, cy - 350, cx + 350, cy + 350)); tables.append((cx, cy, key))
    for sy in (-1, 1):
        y0 = cy + sy * 390; add('chair', R(cx - 225, y0, cx + 225, y0 + sy * 450), back=('n' if sy > 0 else 's'), t=len(tables))
    seat(key, 2)
table_ns(6600, 3300, 'photo')
for cy in (6800, 9300):
    for cx in (5000, 7300):
        table_ns(cx, cy, 'south')
def ring(c, r0, r1, a0=0, a1=360):
    an = C(c[0], c[1], r1, 96).difference(C(c[0], c[1], r0, 96))
    if a1 - a0 >= 360: return an
    return an.intersection(Polygon([c] + [(c[0] + 6000 * math.cos(math.radians(a)), c[1] + 6000 * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 5)]))
add('pit', C(*TREE_S, 1000), 'SMK-R6-TREE'); add('ringbench', ring(TREE_S, 1000, 1450), 'SMK-R6-TREE'); seat('chinar_s', 10)
# plaza tables facing the mangal pass (first row pulled 350 south: 2.0 m waiter zone at the pass, 720 between chair backs)
for cy, cxs in ((11100, (8800, 10550)), (13600, (8400, 10300))):
    for cx in cxs:
        table_ns(cx, cy, 'plaza')
add('host', R(7000, 14700, 7600, 15250), 'SMK-R6-SERV')

# ======================= ENTRANCE CORRIDOR (owner ref.: draped velvet tunnel) =======================
TUN = (7700, 10500)
for yy in (ENT[0] + 40, ENT[1] - 40): add('curtain', LineString([(TUN[0], yy), (TUN[1], yy)]), 'SMK-R6-DECO')
add('runner', R(TUN[0] - 300, ENT[0] + 650, TUN[1] + 60, ENT[1] - 650), 'SMK-R6-DECO')
for x_, y_ in ((8150, ENT[0] + 330), (8450, ENT[0] + 300), (9900, ENT[1] - 320), (10200, ENT[1] - 300), (9150, ENT[0] + 300)):
    add('jar', C(x_, y_, 230 if x_ in (8150, 9900) else 170, 24), 'SMK-R6-DECO')
for x_ in (7900, 8900, 9700, 10400):
    for yy in (ENT[0] + 180, ENT[1] - 180):
        add('flamp', C(x_, yy, 90, 16), 'SMK-R6-DECO')

# ======================= NORTH =======================
PW = 3300
PLAT = unary_union([R(0, 15300, PW, 28500), R(0, 28500, 2400, 30900)])
add('platform', PLAT, 'SMK-R6-STEPS')
add('stepsA', R(PW, ENT[0], PW + 900, ENT[1]), 'SMK-R6-STEPS')
add('stepsB', R(PW, 24300, PW + 900, 25800), 'SMK-R6-STEPS')
RAMP = R(0, 30900, 1300, 36540); add('ramp', RAMP, 'SMK-R6-STEPS')
RAIL = [((PW, ENT[1]), (PW, 24300)), ((PW, 25800), (PW, 28500)), ((2400, 28500), (PW, 28500)), ((2400, 28500), (2400, 30900)), ((1300, 30900), (2400, 30900)), ((1300, 30900), (1300, 36540)), ((PW, 15300), (PW, ENT[0])), ((1500, 15300), (PW, 15300))]
# aivan: ONE row — built-in banquette on the hall wall (closed doors), 1200x700 tables, chairs on the aisle side, aisle 1510
BQ = [(18550, 24150), (25950, 28450)]
for a, b in BQ: add('banquette', R(0, a, 550, b))
def table_bq(cy, key='platform'):
    add('table', R(600, cy - 600, 1300, cy + 600)); tables.append((950, cy, key))
    for sy in (-1, 1):
        add('chair', R(1340, cy + sy * 75, 1790, cy + sy * 525), back='e', t=len(tables))
    seat(key, 4)
for cy in (19450, 21350, 23250, 27200): table_bq(cy)
add('station', R(1750, 30250, 2350, 30850), 'SMK-R6-SERV')
# booths: 9 orthogonal booths, 2.0 m module, depth 1.3
B_Y0, B_N, B_W, B_D = 18300, 9, 2000, 1300
booth_west = []
for k in range(B_N):
    y0, y1 = B_Y0 + k * B_W, B_Y0 + (k + 1) * B_W
    xe = xi(y1); xw = xe - B_D; booth_west.append((y0, y1, xw))
    add('rug', R(xw, y0 + 60, xe, y1))
    add('screen', R(xw, y0, xe, y0 + 60))
    add('bench', R(xw + 80, y0 + 100, xe - 60, y0 + 580))
    add('btable', R(xw + 150, y0 + 650, xe - 150, y1 - 650)); tables.append(((xw + xe) / 2, (y0 + y1) / 2, 'booths'))
    add('bench', R(xw + 80, y1 - 580, xe - 60, y1 - 100))
    add('lantern', C((xw + xe) / 2, (y0 + y1) / 2, 150, 20))
    add('sliver', Polygon([(xe, y0), (xi(y0), y0), (xi(y1), y1), (xe, y1)]))
    seat('booths', 4)
add('screen', R(booth_west[-1][2], B_Y0 + B_N * B_W, xi(B_Y0 + B_N * B_W), B_Y0 + B_N * B_W + 60))
for cy in (19300, 21600, 23900):
    for cx in (4800, 6600): table_ns(cx, cy, 'north')
add('pit', C(*TREE_N, 1000), 'SMK-R6-TREE'); add('ringbench', ring(TREE_N, 1000, 1450, 120, 290), 'SMK-R6-TREE'); seat('chinar_n', 6)
# tapchans: two kept by the aryk, open to the path
for y0 in (28700, 30600):
    add('tapchan', R(2550, y0, 4550, y0 + 1800)); add('tapchanrug', R(2700, y0 + 150, 4400, y0 + 1650)); add('tapchantable', R(3100, y0 + 500, 4000, y0 + 1300))
    tables.append((3550, y0 + 900, 'tapchans')); seat('tapchans', 6)
add('aryk', R(1700, 31100, 2000, 35500), 'SMK-R6-TREE')
hz = OCT(1850, 36000, 380)
add('hauzborder', hz.buffer(200, join_style=2), 'SMK-R6-TREE'); add('hauz', hz, 'SMK-R6-TREE')
# 2-tops at the north entrance, between the tapchans and the booths (paths 1.35 m / >=1.2 m)
for cy in (29250, 31450): table2(6250, cy, 'ntables')
# MAJLIS TENT (owner ref.): fabric canopy under the roof, U-sofa open to the east, carpet, 2 octagonal tables
TX0, TY0, TX1, TY1 = 2500, 32700, 5800, 36300
add('tentroof', R(TX0 - 50, TY0 - 50, TX1 + 50, TY1 + 50), 'SMK-R6-TENT')
add('carpet', R(3200, 33400, 5650, 35600), 'SMK-R6-TENT')
add('sofa', R(TX0, TY0, 3200, TY1), 'SMK-R6-TENT')
add('sofa', R(3200, TY0, 5550, TY0 + 700), 'SMK-R6-TENT')
add('sofa', R(3200, TY1 - 700, 5550, TY1), 'SMK-R6-TENT')
for c in ((3900, 34500), (4900, 34500)): add('otable', OCT(*c, 320), 'SMK-R6-TENT'); tables.append((c[0], c[1], 'tent'))
for c in ((TX0 - 50, TY0 - 50), (TX1 + 50, TY0 - 50), (TX0 - 50, TY1 + 50), (TX1 + 50, TY1 + 50)): add('pole', C(*c, 70, 16), 'SMK-R6-TENT')
for c in ((TX1 + 230, TY0 + 150), (TX1 + 230, TY1 - 150)): add('lantern', C(*c, 170, 20), 'SMK-R6-TENT')
seat('tent', 10)

# ======================= STREET FAÇADE (owner red strip) =======================
# outer 550: cast-in-place tinted concrete bench (seat +450 above the sidewalk), 150 back wall with majolica band, 800 planter
SB = [(9000, 12300), (18750, 21100), (21600, 25300), (28400, 31800), (32300, 35900)]
for a, b in SB:
    add('sbench', BP(a, b, 0, 550), 'SMK-R6-STREET'); add('sback', BP(a, b, 550, 700), 'SMK-R6-STREET')
SEBIL = (12700, 14300)                              # wall fountain beside the entrance
add('sebil', BP(SEBIL[0], SEBIL[1], 550, 950), 'SMK-R6-STREET'); add('sebilbasin', BP(SEBIL[0] + 250, SEBIL[1] - 250, 0, 550), 'SMK-R6-STREET')
SARCH = (25800, 27800)                              # street photo arch with a bench niche
add('sarch', BP(SARCH[0], SARCH[1], 550, 1000), 'SMK-R6-STREET'); add('sbench', BP(SARCH[0] + 250, SARCH[1] - 250, 0, 550), 'SMK-R6-STREET')
for yy in (SARCH[0] - 250, SARCH[1] + 250, 12450, 14550 + 0): add('spalm', C(xb(yy) - 300, yy, 250, 24), 'SMK-R6-STREET')
for a in (ENT[0] - 700, ENT[1]): add('portal', BP(a, a + 700, 0, 1500), 'SMK-R6-STREET')
street_seats = int(sum(it['geom'].length / 2 / 600 for it in items if it['kind'] == 'sbench'))
planter = band.difference(gap).difference(unary_union([it['geom'] for it in items if it['layer'] == 'SMK-R6-STREET']))

# ======================= ROOF =======================
TRUSS_Y = [4100, 9850, 16800, 21350, 25600, 29100, 32100, 36300]
COL_E = [4100, 9850, 15300, 18300, 21350, 25600, 29100, 32100, 36300]
cols = [(xb(y) - 750, y) for y in COL_E] + [(-7050, 200), (-350, 250)]

# ======================= ZONES =======================
ALLEY = R(PW + 900, ENT[0], xi(ENT[1]), ENT[1])
FLOOR = U.difference(band.difference(gap))
TENT = R(TX0 - 50, TY0 - 50, TX1 + 50, TY1 + 50)
zones = {'kids': KIDS, 'photo': R(1000, 1700, 5800, 4700), 'service': R(0, 4250, 2080, 8400), 'bar': R(0, 8000, 3000, 15300),
         'bbq': R(BX0, BY0, BX1, BY1), 'alley': ALLEY, 'platform': PLAT, 'booths': unary_union([R(w, a, xi(b), b) for a, b, w in booth_west]),
         'tapchan': R(2550, 28700, 4550, 32400), 'tent': TENT}
zone_m2 = {k: round(v.area / 1e6, 1) for k, v in zones.items()}

# ======================= CHECKS =======================
probs = []
FURN = ('table', 'chair', 'btable', 'bench', 'tapchan', 'stool', 'station', 'host', 'ringbench', 'shelving', 'counter', 'banquette', 'sofa', 'otable', 'phscreen', 'palm')
solid = [it for it in items if it['kind'] in FURN]
okfloor = FLOOR.union(PLAT).buffer(5)
door_clear = [R(0, a, 1500, b) for a, b, op in DOORS.values() if op]
pits = [C(*TREE_N, 1000), C(*TREE_S, 1000)]
blocked = unary_union([RAMP, R(PW, ENT[0], PW + 900, ENT[1]), R(PW, 24300, PW + 900, 25800), R(550, 14300, 1500, 15300), R(0, 15300, PW, ENT[0] + 1200)])
for it in solid:
    g = it['geom']
    if not okfloor.contains(g): probs.append(f"{it['kind']} off floor @ {g.centroid.x:.0f},{g.centroid.y:.0f}")
    if any(g.intersection(d).area > 500 for d in door_clear): probs.append(f"{it['kind']} blocks a door @ {g.centroid.y:.0f}")
    if it['kind'] != 'ringbench' and any(g.intersects(p) for p in pits): probs.append(f"{it['kind']} in a tree pit")
    if g.intersection(blocked).area > 500: probs.append(f"{it['kind']} on steps/ramp @ {g.centroid.x:.0f},{g.centroid.y:.0f}")
    if g.intersects(ALLEY) and it['kind'] not in ('host',): probs.append(f"{it['kind']} in the alley @ {g.centroid.x:.0f},{g.centroid.y:.0f}")
for i in range(len(solid)):
    for j in range(i + 1, len(solid)):
        a, b = solid[i]['geom'], solid[j]['geom']
        if a.intersection(b).area > 1500 and {solid[i]['kind'], solid[j]['kind']} not in ({'table', 'chair'}, {'btable', 'bench'}, {'otable', 'sofa'}):
            probs.append(f"overlap {solid[i]['kind']}/{solid[j]['kind']} @ {a.centroid.x:.0f},{a.centroid.y:.0f}")
# clear path in front of the booths
west = unary_union([it['geom'] for it in solid if it['geom'].centroid.y > ENT[1] and it['geom'].bounds[2] < 7800] + [C(*TREE_N, 1000), TENT])
pmin, pmin_at = 1e9, None
for a, b, xw in booth_west:
    for yy in range(int(a) + 50, int(b), 100):
        hit = LineString([(xw - 4000, yy), (xw, yy)]).intersection(west)
        xe = max([p[0] for g in getattr(hit, 'geoms', [hit]) for p in getattr(g, 'coords', [])] or [xw - 4000])
        if xw - xe < pmin: pmin, pmin_at = xw - xe, (xe, yy, xw)
# tapchan-side path for the north 2-tops
tap_path = 6250 - 350 - 4550
# chair back-to-back clearance between different tables (dining chairs only)
chairs = [it for it in items if it['kind'] == 'chair']
bb = min(chairs[i]['geom'].distance(chairs[j]['geom']) for i in range(len(chairs)) for j in range(i + 1, len(chairs)) if chairs[i]['t'] != chairs[j]['t'])
total = sum(seats.values())
res = dict(seats=seats, total=total, street_bench_seats=street_seats, zones_m2=zone_m2, path_min=round(pmin), tap_path=tap_path,
           chair_back_min=round(bb), problems=probs, entrance_width=ENT[1] - ENT[0], n_tables=len(tables))
print(json.dumps(res, indent=1, ensure_ascii=False))

def coords(g):
    if isinstance(g, LineString): return [[(round(x, 1), round(y, 1)) for x, y in g.coords]]
    return [[(round(x, 1), round(y, 1)) for x, y in p.exterior.coords] for p in getattr(g, 'geoms', [g]) if not p.is_empty]
json.dump(dict(res, columns=cols, truss_y=TRUSS_Y, items=[dict(kind=i['kind'], layer=i['layer'], poly=coords(i['geom'])) for i in items]), open(f'{OUT}/samarkand-terrace-layout-{REV}.json', 'w'), ensure_ascii=False)
doc = ezdxf.readfile(BASE_DXF); msp = doc.modelspace()
for lay, col in (('SMK-R6-FURN', 7), ('SMK-R6-BAR', 40), ('SMK-R6-BBQ', 30), ('SMK-R6-PHOTO', 5), ('SMK-R6-SERV', 4), ('SMK-R6-TREE', 3), ('SMK-R6-STEPS', 8),
                 ('SMK-R6-ROOF', 34), ('SMK-R6-PLANT', 3), ('SMK-R6-DECO', 21), ('SMK-R6-TENT', 1), ('SMK-R6-STREET', 6)):
    if lay not in doc.layers: doc.layers.add(lay, color=col)
for it in items:
    for p in coords(it['geom']):
        if isinstance(it['geom'], LineString): msp.add_lwpolyline(p, dxfattribs={'layer': it['layer']})
        else: msp.add_lwpolyline(p[:-1], close=True, dxfattribs={'layer': it['layer']})
for p in coords(planter): msp.add_lwpolyline(p[:-1], close=True, dxfattribs={'layer': 'SMK-R6-PLANT'})
for a, b in RAIL: msp.add_line(a, b, dxfattribs={'layer': 'SMK-R6-STEPS'})
for c in cols: msp.add_lwpolyline(list(R(c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150).exterior.coords)[:-1], close=True, dxfattribs={'layer': 'SMK-R6-ROOF'})
for yy in TRUSS_Y: msp.add_line((0, yy), (xb(yy) - 750, yy), dxfattribs={'layer': 'SMK-R6-ROOF'})
for c in (TREE_N, TREE_S): msp.add_circle(c, 1400, dxfattribs={'layer': 'SMK-R6-ROOF'})
doc.saveas(f'{OUT}/samarkand-terrace-layout-{REV}.dxf')

# ======================= TEXT =======================
T = {
 'ru': dict(sub='Крытая терраса  ·  планировка R6', cuisine='Таджикская и узбекская кухня  ·  Võ Nguyên Giáp, 254, Дананг',
            hall='ОСНОВНОЙ ЗАЛ  ·  ±0.000', drive='ПОДЪЕЗД 8% → ПАРКОВКА', street='УЛ. ВÕ NGUYÊN GIÁP  ·  15 М  ·  → МОРЕ', sidewalk='ТРОТУАР',
            zones='ЗОНЫ', seats='ПОСАДКА', total='Итого мест в ресторане', key='ОБОЗНАЧЕНИЯ', erg='ЭРГОНОМИКА  ·  норма / по плану',
            L=[('Главный вход · портал-пештак', 'проём 2,5 м, 4 ступени с тротуара'), ('Коридор-драпировка', 'бархат, ковровая дорожка, хумы, фонари'),
               ('Аллея к залу', 'гирих, 2,5 м, хостес у выхода'), ('Айван-платформа ±0.000', 'один ряд: банкетка у стены, 4 стола, проход 1,5 м'),
               ('Кабинки с видом на улицу', '9 кабинок, резные ширмы, фонари'), ('Чинар-дворик (север)', 'дерево сохранено, скамья-полукольцо'),
               ('Топчаны у арыка', '2 топчана, открыты к проходу'), ('Шатёр-маджлис', 'П-диван, ковёр, 2 стола, на 10 гостей'),
               ('Столики у северного входа', '2 стола на 2'), ('Северный вход + пандус 1:12', 'с парковки, без ступеней, хауз'),
               ('Зал север', '6 столов на 4'), ('Бар', 'чай, самовар, кофе · 9 стульев'), ('Станция персонала', 'стеллажи, касса, вода, лёд, посуда'),
               ('Зал юг', '4 стола на 4'), ('Чинар-дворик (юг) + столы у входа', 'круглая скамья, 4 стола напротив мангала'),
               ('Мангальная 4,2 × 4,8 м', 'тандыр · мангал · казан · раздача к гостям'), ('Фотозона', 'арка-джали с подсветкой, пальмы, ковёр, свечи'),
               ('Детская зона', 'ограждение, мягкое покрытие'), ('Уличные скамьи', 'литой бетон в стенке клумбы, майолика'),
               ('Фонтан-себиль', 'майоликовая стена, латунный носик, чаша'), ('Уличная фото-арка', 'ниша со скамьёй, подсветка, пальмы')],
            S={'platform': 'Айван-платформа', 'booths': 'Кабинки', 'north': 'Зал север', 'chinar_n': 'Скамья у чинара (север)', 'tapchans': 'Топчаны (2)',
               'ntables': 'Столики у северного входа', 'tent': 'Шатёр-маджлис', 'photo': 'Стол у фотозоны', 'bar': 'Барная стойка', 'south': 'Зал юг',
               'chinar_s': 'Скамья у чинара (юг)', 'plaza': 'Столы у входа'},
            street_seats='+ уличные скамьи (вне счёта)',
            K=['Колонна навеса (сталь, обшивка деревом)', 'Линия фермы навеса', 'Ось здания', 'Вход гостей', 'Маршрут персонала', 'Дверь зала открыта',
               'Дверь зала закрыта', 'Вытяжной зонт', 'Размер, мм', '№ стола'],
            E=[('Главный проход / аллея', '≥1500', '2500'), ('Проход к кабинкам', '≥1200', '{pmin}'), ('Проход у топчанов', '≥1200', '{tap}'),
               ('Проход на айване', '≥1200', '1510'), ('Край стола → спинка стула', '450–600', '490'), ('Спинка–спинка (без прохода)', '≥450', '{bb}'),
               ('Барная стойка: высота / вынос', '1050 / 250–300', '1050 / 300'), ('Шаг барных стульев', '600–650', '620'),
               ('Рабочая зона повара', '≥1200', '2450'), ('Раздача → гости', '≥1500', '1710'), ('Пандус: уклон / ширина', '1:12 / ≥1200', '1:12 / 1300'),
               ('Уличная скамья: h / глубина', '420–460 / ≥450', '450 / 550')],
            notes=['Основа: исполнительный DWG (Long House, 10.07.2024) 1:1. Отметки: тротуар −1.170, терраса −0.470, айван и зал ±0.000.',
                   'Навес: стальные фермы по осям; колонны у улицы замоноличены в стенку клумбы за скамьями. Внутри обеденной зоны колонн нет.',
                   'Деревья сохранены, проходят через проёмы в кровле Ø2,8 м. Шатёр — тканевый, под навесом, огнезащитная пропитка.',
                   'Двери: C–D южная открыта; C–D северная и D–E южная закрыты (банкетка); D–E северная и E–F у лифта открыты.',
                   'Скамьи и себиль — в границе участка, не выступают на тротуар. Мангальная: зонт и труба выше кровли.'],
            foot='Концепция для согласования с заказчиком · размеры уточнить на месте', ph='ФОТОЗОНА', barlbl='БАР', ent='ВХОД', scale='Масштаб 1:100 · A2',
            lv_t='терраса −0.470', lv_p='±0.000', lv_s='тротуар −1.170', tunnel='КОРИДОР',
            i_bbq='МАНГАЛЬНАЯ  ·  1:75', i_tent='ШАТЁР-МАДЖЛИС  ·  1:75', i_st='УЛИЧНАЯ СКАМЬЯ  ·  РАЗРЕЗ 1:60', i_pl='АЙВАН  ·  РАЗРЕЗ 1:60',
            bbqL=['Тандыр Ø900', 'Мангал 2,0 м, угли', 'Казан Ø800, газ', 'Мойка · уголь · зола', 'Заготовка, холод', 'Раздача 2,8 м, лампы', 'Огнестойкая стена', 'Склад угля и тары'],
            tentL=['П-диван h 400, глуб. 700', 'Ковёр 2,4 × 2,2 м', 'Столики Ø640, 8 граней', 'Стойки, ткань-драпировка', 'Фонари у входа', 'Вход 1,6 м'],
            stL=['Скамья: литой бетон', 'Спинка + майолика', 'Клумба, колонна в стенке', 'Кабинка −0.470', 'Тротуар −1.170'],
            plL=['Банкетка', 'Стол 1200×700', 'Стул', 'Проход', 'Перила h1000', 'Терраса −0.470']),
 'en': dict(sub='Covered terrace  ·  Layout R6', cuisine='Tajik & Uzbek national cuisine  ·  254 Võ Nguyên Giáp, Đà Nẵng',
            hall='MAIN HALL  ·  ±0.000', drive='DRIVEWAY 8% → PARKING', street='VÕ NGUYÊN GIÁP  ·  15 M  ·  → SEA', sidewalk='SIDEWALK',
            zones='ZONES', seats='SEATS', total='Total restaurant seats', key='KEY', erg='ERGONOMICS  ·  standard / as planned',
            L=[('Street entrance · pishtaq portal', '2.5 m opening, 4 steps from the sidewalk'), ('Draped corridor', 'velvet swags, runner, clay jars, lanterns'),
               ('Alley to the hall', 'girih paving, 2.5 m, host at the exit'), ('Aivan platform ±0.000', 'one row: wall banquette, 4 tables, 1.5 m aisle'),
               ('Street-view booths', '9 booths, carved screens, lanterns'), ('Chinar court north', 'tree kept, half-ring bench'),
               ('Tapchans by the aryk', '2 tapchans, open to the path'), ('Majlis tent', 'U-sofa, carpet, 2 tables, 10 guests'),
               ('Tables at the north entrance', '2 tables for 2'), ('North entrance + ramp 1:12', 'from parking, step-free, hauz'),
               ('Dining north', '6 tables for 4'), ('Bar', 'tea, samovar, coffee · 9 stools'), ('Staff station', 'shelving, POS, water, ice, dishes'),
               ('Dining south', '4 tables for 4'), ('Chinar court south + entrance tables', 'round bench, 4 tables facing the mangal'),
               ('Mangal kitchen 4.2 × 4.8 m', 'tandoor · mangal · kazan · pass to guests'), ('Photo zone', 'backlit jali arch, palms, rug, candles'),
               ('Kids zone', 'fenced, soft floor'), ('Street benches', 'cast concrete in the planter wall, majolica'),
               ('Sebil fountain', 'majolica wall, brass spout, basin'), ('Street photo arch', 'bench niche, uplight, palms')],
            S={'platform': 'Aivan platform', 'booths': 'Booths', 'north': 'Dining north', 'chinar_n': 'Chinar bench north', 'tapchans': 'Tapchans (2)',
               'ntables': 'Tables at the north entrance', 'tent': 'Majlis tent', 'photo': 'Table by the photo zone', 'bar': 'Bar counter', 'south': 'Dining south',
               'chinar_s': 'Chinar bench south', 'plaza': 'Entrance tables'},
            street_seats='+ street benches (not counted)',
            K=['Roof column (steel, wood-clad)', 'Roof truss line', 'Building axis', 'Guest entrance', 'Staff route', 'Hall door, open',
               'Hall door, closed', 'Exhaust hood', 'Dimension, mm', 'Table no.'],
            E=[('Main path / alley', '≥1500', '2500'), ('Path to the booths', '≥1200', '{pmin}'), ('Path by the tapchans', '≥1200', '{tap}'),
               ('Aivan aisle', '≥1200', '1510'), ('Table edge → chair back', '450–600', '490'), ('Chair back to back (no path)', '≥450', '{bb}'),
               ('Bar counter: height / overhang', '1050 / 250–300', '1050 / 300'), ('Bar stool pitch', '600–650', '620'),
               ('Cook work aisle', '≥1200', '2450'), ('Pass → guests', '≥1500', '1710'), ('Ramp: slope / width', '1:12 / ≥1200', '1:12 / 1300'),
               ('Street bench: h / depth', '420–460 / ≥450', '450 / 550')],
            notes=['Base: as-built DWG (Long House, 10-07-2024) 1:1. Levels: sidewalk −1.170, terrace −0.470, aivan and hall ±0.000.',
                   'Roof: steel trusses on the grid; street-side columns cast into the planter wall behind the benches. No columns in the dining.',
                   'Trees kept, through Ø2.8 m roof oculi. The tent is fabric under the roof, fire-retardant treated.',
                   'Doors: C–D south open; C–D north and D–E south closed (banquette); D–E north and E–F by the lift open.',
                   'Benches and sebil stay inside the lot line, nothing projects onto the sidewalk. Mangal: hood + stack above the roof.'],
            foot='Concept for client review · dimensions to verify on site', ph='PHOTO ZONE', barlbl='BAR', ent='ENTRANCE', scale='Scale 1:100 · A2',
            lv_t='terrace −0.470', lv_p='±0.000', lv_s='sidewalk −1.170', tunnel='CORRIDOR',
            i_bbq='MANGAL KITCHEN  ·  1:75', i_tent='MAJLIS TENT  ·  1:75', i_st='STREET BENCH  ·  SECTION 1:60', i_pl='AIVAN  ·  SECTION 1:60',
            bbqL=['Tandoor Ø900', 'Mangal 2.0 m, charcoal', 'Kazan Ø800, gas', 'Sink · charcoal · ash', 'Cold prep, fridges', 'Pass 2.8 m, heat lamps', 'Fire wall', 'Charcoal + crate store'],
            tentL=['U-sofa h 400, depth 700', 'Carpet 2.4 × 2.2 m', 'Octagonal tables Ø640', 'Posts, draped fabric', 'Lanterns at the entry', 'Entry 1.6 m'],
            stL=['Bench: cast concrete', 'Back + majolica band', 'Planter, column in wall', 'Booth −0.470', 'Sidewalk −1.170'],
            plL=['Banquette', 'Table 1200×700', 'Chair', 'Aisle', 'Rail h1000', 'Terrace −0.470'])}

# ======================= SVG (A2 portrait, plan 1:100) =======================
W, H = 420, 594
S_ = 100.0; PX0, PY0 = 14.0, 64.0; XMIN, YMAX = -8600.0, 39400.0
def P(x, y): return (PX0 + (x - XMIN) / S_, PY0 + (YMAX - y) / S_)
OX, OY = P(0, 0)
def d_of(g, M=P):
    out = []
    if isinstance(g, LineString):
        return 'M' + 'L'.join(f'{M(x, y)[0]:.2f},{M(x, y)[1]:.2f}' for x, y in g.coords)
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty: continue
        out.append('M' + 'L'.join(f'{M(x, y)[0]:.2f},{M(x, y)[1]:.2f}' for x, y in p.exterior.coords) + 'Z')
        for r in p.interiors: out.append('M' + 'L'.join(f'{M(x, y)[0]:.2f},{M(x, y)[1]:.2f}' for x, y in r.coords) + 'Z')
    return ''.join(out)

def tile_pat(pid, size_mm, body, bg):
    s = size_mm / S_
    return f'<pattern id="{pid}" x="{OX % s:.3f}" y="{OY % s:.3f}" width="{s:.3f}" height="{s:.3f}" patternUnits="userSpaceOnUse"><rect width="{s:.3f}" height="{s:.3f}" fill="{bg}"/>{body(s)}</pattern>'
def terr(s):
    c = s * .16
    return (f'<path d="M0 0H{s:.3f}M0 0V{s:.3f}" stroke="#d5c09c" stroke-width=".12"/>'
            + ''.join(f'<path d="M{x:.3f} {y - c:.3f}L{x + c:.3f} {y:.3f}L{x:.3f} {y + c:.3f}L{x - c:.3f} {y:.3f}Z" fill="#b5653a"/>' for x in (0, s) for y in (0, s)))
def girih(s):
    h = s / 2; a = s * .26
    return (f'<path d="M0 0H{s:.3f}M0 0V{s:.3f}" stroke="#a4643c" stroke-width=".12"/><rect x="{h - a:.3f}" y="{h - a:.3f}" width="{2 * a:.3f}" height="{2 * a:.3f}" fill="#1F3F8A"/>'
            f'<rect x="{h - a:.3f}" y="{h - a:.3f}" width="{2 * a:.3f}" height="{2 * a:.3f}" fill="#1F3F8A" transform="rotate(45 {h:.3f} {h:.3f})"/>'
            f'<circle cx="{h:.3f}" cy="{h:.3f}" r="{s * .11:.3f}" fill="#2A9DA8"/><circle cx="{h:.3f}" cy="{h:.3f}" r="{s * .05:.3f}" fill="#efe6d8"/>')
def slate(s): return f'<path d="M0 0H{s:.3f}M0 0V{s:.3f}" stroke="#5f5b56" stroke-width=".12"/>'
def rubber(s): h = s / 2; return f'<rect width="{h:.3f}" height="{h:.3f}" fill="#f6c25a"/><rect x="{h:.3f}" y="{h:.3f}" width="{h:.3f}" height="{h:.3f}" fill="#f6c25a"/><path d="M0 0H{s:.3f}M0 0V{s:.3f}" stroke="#e0a83e" stroke-width=".1"/>'
deck_s = 150 / S_
DEFS = ('<defs>' + tile_pat('terr', 600, terr, '#efe1c6') + tile_pat('alley', 600, girih, '#c98b62') + tile_pat('slate', 600, slate, '#7a756e') + tile_pat('rubber', 500, rubber, '#ffd978') +
        f'<pattern id="deck" x="{OX % (2400 / S_):.3f}" y="{OY % deck_s:.3f}" width="{deck_s:.3f}" height="{2400 / S_:.3f}" patternUnits="userSpaceOnUse"><rect width="{deck_s:.3f}" height="{2400 / S_:.3f}" fill="#c69c6d"/><path d="M{deck_s:.3f} 0V{2400 / S_:.3f}M0 {1200 / S_:.3f}H{deck_s / 2:.3f}" stroke="#9b7148" stroke-width=".1"/></pattern>'
        '<pattern id="ikat" width="2.4" height="2.4" patternUnits="userSpaceOnUse"><rect width="2.4" height="2.4" fill="#8E1F24"/><path d="M1.2 .25L1.95 1.2L1.2 2.15L.45 1.2Z" fill="#d9a23a"/><path d="M1.2 .8L1.5 1.2L1.2 1.6L.9 1.2Z" fill="#1F3F8A"/></pattern>'
        '<pattern id="suzani" width="3.2" height="3.2" patternUnits="userSpaceOnUse"><rect width="3.2" height="3.2" fill="#f1e5d0"/><circle cx="1.6" cy="1.6" r=".95" fill="#b8323a"/><circle cx="1.6" cy="1.6" r=".42" fill="#d9a23a"/><circle cx="0" cy="0" r=".4" fill="#2a6f4a"/><circle cx="3.2" cy="0" r=".4" fill="#2a6f4a"/><circle cx="0" cy="3.2" r=".4" fill="#2a6f4a"/><circle cx="3.2" cy="3.2" r=".4" fill="#2a6f4a"/></pattern>'
        '<pattern id="majolica" width="1.8" height="1.8" patternUnits="userSpaceOnUse"><rect width="1.8" height="1.8" fill="#1F3F8A"/><path d="M.9 .15L1.15 .65L1.65 .9L1.15 1.15L.9 1.65L.65 1.15L.15 .9L.65 .65Z" fill="#2A9DA8"/><circle cx=".9" cy=".9" r=".2" fill="#efe6d8"/></pattern>'
        '<pattern id="lattice" width=".9" height=".9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width=".9" height=".9" fill="#4a2f1c"/><rect x=".22" y=".22" width=".46" height=".46" fill="#9a6a40"/></pattern>'
        '<pattern id="jali" width="1.4" height="1.4" patternUnits="userSpaceOnUse"><rect width="1.4" height="1.4" fill="#f6e7c8"/><path d="M.7 .1L.9 .5L1.3 .7L.9 .9L.7 1.3L.5 .9L.1 .7L.5 .5Z" fill="none" stroke="#c9a15a" stroke-width=".12"/></pattern>'
        '<pattern id="stripe" width="2.2" height="2.2" patternUnits="userSpaceOnUse"><rect width="2.2" height="2.2" fill="#b8323a"/><rect x=".55" width=".3" height="2.2" fill="#efe6d8"/><rect x="1.05" width=".25" height="2.2" fill="#6b6f73"/><rect x="1.55" width=".35" height="2.2" fill="#8E1F24"/><rect x="1.9" width=".12" height="2.2" fill="#d9a23a"/></pattern>'
        '<pattern id="carpet" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="3" fill="#8E1F24"/><path d="M1.5 .35L2.65 1.5L1.5 2.65L.35 1.5Z" fill="#a8323a" stroke="#d9a23a" stroke-width=".12"/><circle cx="1.5" cy="1.5" r=".35" fill="#1F3F8A"/><circle cx="0" cy="0" r=".25" fill="#d9a23a"/><circle cx="3" cy="3" r=".25" fill="#d9a23a"/><circle cx="0" cy="3" r=".25" fill="#d9a23a"/><circle cx="3" cy="0" r=".25" fill="#d9a23a"/></pattern>'
        '<pattern id="concrete" width="2" height="2" patternUnits="userSpaceOnUse"><rect width="2" height="2" fill="#d8c8b2"/><circle cx=".5" cy=".6" r=".08" fill="#b9a68c"/><circle cx="1.4" cy="1.3" r=".1" fill="#b9a68c"/><circle cx="1.6" cy=".3" r=".06" fill="#a8957b"/></pattern>'
        '<pattern id="hatch" width="2" height="2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="2" height="2" fill="#e6e0d6"/><path d="M0 0V2" stroke="#d4ccbf" stroke-width=".22"/></pattern>'
        '<pattern id="hatchS" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1.2" height="1.2" fill="#ece6dc"/><path d="M0 0V1.2" stroke="#9a8f80" stroke-width=".15"/></pattern>'
        '<pattern id="soil" width="2" height="2" patternUnits="userSpaceOnUse"><rect width="2" height="2" fill="#8a6a4a"/><circle cx=".6" cy=".7" r=".15" fill="#6b4f35"/><circle cx="1.5" cy="1.4" r=".12" fill="#a4835e"/></pattern>'
        '<pattern id="green" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#a7c38a"/><circle cx="1.5" cy="1.6" r="1.25" fill="#8cb06b"/><circle cx="4.4" cy="4.1" r="1.5" fill="#7aa35c"/><circle cx="1.9" cy="4.8" r=".8" fill="#93b874"/><circle cx="4.9" cy="1.1" r=".75" fill="#6e9752"/></pattern>'
        '<radialGradient id="water" cx="45%" cy="40%" r="65%"><stop offset="0" stop-color="#c9eef4"/><stop offset="1" stop-color="#3a98b2"/></radialGradient>'
        '<radialGradient id="leaf" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#9cc86c"/><stop offset=".7" stop-color="#5f9442"/><stop offset="1" stop-color="#3f6e2c"/></radialGradient>'
        '<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffd27a" stop-opacity=".95"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="brass" cx="40%" cy="35%" r="65%"><stop offset="0" stop-color="#f0d184"/><stop offset="1" stop-color="#a87a2a"/></radialGradient>'
        '<linearGradient id="velvet" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b5652e"/><stop offset=".5" stop-color="#7a3518"/><stop offset="1" stop-color="#b5652e"/></linearGradient>'
        '<filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx=".25" dy=".35" stdDeviation=".25" flood-color="#2b1d12" flood-opacity=".32"/></filter>'
        '<filter id="tsh" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="1.2" dy="1.4" stdDeviation="1" flood-color="#1f2d14" flood-opacity=".35"/></filter>'
        '<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="#2e7d3a"/></marker>'
        '<marker id="arrS" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="#d9731a"/></marker>'
        '</defs>')

DIMC = '#7a2e1f'
STY = {'table': ('#a87444', '#5a3a22', 'sh'), 'btable': ('#a87444', '#5a3a22', 'sh'), 'rug': ('#f0dfc2', 'none', ''), 'bench': ('url(#ikat)', '#3b2a1e', 'sh'),
       'screen': ('url(#lattice)', '#2b1d12', 'sh'), 'tapchan': ('#b88a58', '#5a3a22', 'sh'), 'tapchanrug': ('url(#suzani)', 'none', ''), 'tapchantable': ('#6b4429', '#3b2a1e', 'sh'),
       'stool': ('#8a5a36', '#3b2a1e', 'sh'), 'storage': ('#8a7f70', '#3b2a1e', 'sh'), 'station': ('#2A9DA8', '#1d6f77', ''), 'host': ('#2A9DA8', '#1d6f77', 'sh'),
       'backbar': ('#4a2f1c', '#2b1d12', 'sh'), 'barbody': ('#A4482B', '#5a2a18', 'sh'), 'bartop': ('#efe6d8', '#8a7f70', ''), 'barreturn': ('#efe6d8', '#8a7f70', 'sh'),
       'samovar': ('url(#brass)', '#7a5a1a', ''), 'coffee': ('#2f2f2f', '#111', ''), 'sink': ('#c9ccd0', '#6b6f73', ''),
       'shelving': ('url(#lattice)', '#2b1d12', 'sh'), 'counter': ('#c9ccd0', '#6b6f73', 'sh'), 'screenwall': ('#4a2f1c', 'none', ''),
       'firewall': ('#A4482B', '#5a2a18', ''), 'tandoorblock': ('#c98b62', '#5a3a22', 'sh'), 'tandoor': ('#7a3d22', '#3b1d10', ''), 'mangal': ('#333', '#111', 'sh'), 'ledge': ('#9a9590', '#55524e', ''),
       'kazanblock': ('#9a9590', '#55524e', 'sh'), 'kazan': ('#1d1d1d', '#b8893a', ''), 'sinkbins': ('#c9ccd0', '#6b6f73', 'sh'), 'prep': ('#d7dadd', '#6b6f73', 'sh'), 'pass': ('#e9ebed', '#6b6f73', 'sh'), 'glass': ('#bfe0ea', 'none', ''),
       'phscreen': ('url(#jali)', '#b8893a', 'sh'), 'phrug': ('url(#carpet)', '#5a1a1c', ''), 'palm': ('#b5653a', '#6b3a1e', 'sh'), 'flantern': ('url(#brass)', '#7a5a1a', 'sh'), 'candle': ('#fff3c4', '#d9a23a', ''),
       'camera': ('#3b2a1e', 'none', ''),
       'pit': ('#6b5a48', '#4a3b2c', ''), 'ringbench': ('#9a6a40', '#4a2f1c', 'sh'), 'aryk': ('url(#water)', '#1F3F8A', ''), 'hauzborder': ('url(#majolica)', '#13285a', 'sh'), 'hauz': ('url(#water)', 'none', ''),
       'lantern': ('url(#glow)', 'none', ''), 'banquette': ('url(#ikat)', '#3b2a1e', 'sh'),
       'carpet': ('url(#carpet)', '#5a1a1c', ''), 'sofa': ('url(#stripe)', '#5a1a1c', 'sh'), 'otable': ('#f4efe6', '#b8893a', 'sh'), 'pole': ('#4a2f1c', 'none', ''),
       'runner': ('url(#carpet)', '#5a1a1c', ''), 'jar': ('#c4703f', '#7a3d22', 'sh'), 'flamp': ('url(#glow)', 'none', ''),
       'sbench': ('url(#concrete)', '#6b5a48', 'sh'), 'sback': ('url(#majolica)', '#13285a', ''), 'sebil': ('url(#majolica)', '#13285a', 'sh'), 'sebilbasin': ('url(#water)', '#1F3F8A', 'sh'),
       'sarch': ('url(#jali)', '#b8893a', 'sh'), 'spalm': ('#b5653a', '#6b3a1e', 'sh'), 'portal': ('#A4482B', '#5a2a18', 'sh')}
ORDER = ['rug', 'tapchan', 'tapchanrug', 'carpet', 'runner', 'phrug', 'aryk', 'hauzborder', 'hauz', 'pit', 'ringbench', 'banquette', 'table', 'btable', 'bench', 'screen', 'tapchantable',
         'sofa', 'otable', 'stool', 'station', 'host', 'backbar', 'barbody', 'bartop', 'barreturn', 'samovar', 'coffee', 'sink', 'shelving', 'counter', 'screenwall',
         'firewall', 'tandoorblock', 'tandoor', 'mangal', 'ledge', 'kazanblock', 'kazan', 'sinkbins', 'prep', 'pass', 'glass', 'storage', 'phscreen', 'camera',
         'sbench', 'sback', 'sebil', 'sebilbasin', 'sarch', 'portal', 'jar', 'pole', 'flantern', 'candle', 'lantern', 'flamp']


def build(lang):
    t = T[lang]; out = []
    def sh(g, fill='none', stroke='none', sw=.12, extra='', M=P):
        out.append(f'<path d="{d_of(g, M)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" fill-rule="evenodd" {extra}/>')
    def ln(a, b, stroke, sw, extra='', M=P):
        (x1, y1), (x2, y2) = M(*a), M(*b); out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
    def tx(x, y, s, size=2.2, fill='#3b2a1e', anchor='middle', weight=400, family='Inter', extra='', page=False, M=P):
        if not page: x, y = M(x, y)
        out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>')
    def num(x, y, n, page=False, r=2.4):
        if not page: x, y = P(x, y)
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="#1F3F8A" stroke="#fbf6ec" stroke-width=".45"/><text x="{x:.2f}" y="{y + r * .42:.2f}" font-family="Inter" font-size="{r * 1.1:.2f}" font-weight="700" fill="#fff" text-anchor="middle">{n}</text>')
    def dim(a, b, off=0.0, label=None, M=P, size=1.75, col=DIMC, ext=True):
        """aligned dimension: a, b real points; off = page-mm offset to the left of a->b"""
        (x1, y1), (x2, y2) = M(*a), M(*b); dx, dy = x2 - x1, y2 - y1; Ld = math.hypot(dx, dy); ux, uy = dx / Ld, dy / Ld; nx, ny = uy, -ux
        X1, Y1, X2, Y2 = x1 + nx * off, y1 + ny * off, x2 + nx * off, y2 + ny * off
        if ext and abs(off) > .3:
            for (px, py), (qx, qy) in (((x1, y1), (X1, Y1)), ((x2, y2), (X2, Y2))):
                out.append(f'<line x1="{px + nx * .4 * math.copysign(1, off):.2f}" y1="{py + ny * .4 * math.copysign(1, off):.2f}" x2="{qx + nx * .6 * math.copysign(1, off):.2f}" y2="{qy + ny * .6 * math.copysign(1, off):.2f}" stroke="{col}" stroke-width=".1"/>')
        out.append(f'<line x1="{X1 - ux * .8:.2f}" y1="{Y1 - uy * .8:.2f}" x2="{X2 + ux * .8:.2f}" y2="{Y2 + uy * .8:.2f}" stroke="{col}" stroke-width=".13"/>')
        for X, Y in ((X1, Y1), (X2, Y2)):
            out.append(f'<line x1="{X - (ux + nx) * .55:.2f}" y1="{Y - (uy + ny) * .55:.2f}" x2="{X + (ux + nx) * .55:.2f}" y2="{Y + (uy + ny) * .55:.2f}" stroke="{col}" stroke-width=".3"/>')
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90.1 or ang < -89.9: ang -= 180 if ang > 0 else -180
        mx, my = (X1 + X2) / 2, (Y1 + Y2) / 2
        s = label if label is not None else f'{round(math.dist(a, b)):d}'
        # text sits on the side away from the measured object
        sgn = 1 if off >= 0 else -1
        tnx, tny = nx * sgn, ny * sgn
        ox, oy = mx + tnx * .55, my + tny * .55
        # baseline offset: place glyphs outward
        rot_n = (-math.sin(math.radians(ang)), math.cos(math.radians(ang)))     # text "down" direction
        if rot_n[0] * tnx + rot_n[1] * tny > 0: ox, oy = mx + tnx * (size * .95 + .3), my + tny * (size * .95 + .3)
        out.append(f'<text x="{ox:.2f}" y="{oy:.2f}" font-family="Inter" font-size="{size}" font-weight="500" fill="{col}" text-anchor="middle" transform="rotate({ang:.2f} {ox:.2f} {oy:.2f})" paint-order="stroke" stroke="#f7f1e6" stroke-width=".5">{s}</text>')
    def level(x, y, s, page=False, M=P, size=1.9):
        X, Y = (x, y) if page else M(x, y)
        out.append(f'<path d="M{X:.2f} {Y:.2f}l-1 -1.5h2z" fill="#3b2a1e"/><line x1="{X - 1.4:.2f}" y1="{Y:.2f}" x2="{X + 1.4:.2f}" y2="{Y:.2f}" stroke="#3b2a1e" stroke-width=".15"/>')
        tx(X + 1.4, Y - .4, s, size, '#3b2a1e', anchor='start', weight=600, page=True)

    out.append(f'<rect width="{W}" height="{H}" fill="#f7f1e6"/><rect x="7" y="7" width="{W - 14}" height="{H - 14}" fill="none" stroke="#5A3A22" stroke-width=".7"/><rect x="8.6" y="8.6" width="{W - 17.2}" height="{H - 17.2}" fill="none" stroke="#b8893a" stroke-width=".25"/>')
    # ---------- context
    sh(R(XMIN + 300, 4100, 0, 37100), 'url(#hatch)')
    hx, hy = P(-5300, 24000); tx(hx, hy, t['hall'], 4.0, '#8a7f70', weight=600, page=True, extra=f'transform="rotate(-90 {hx:.2f} {hy:.2f})" letter-spacing="1"')
    sx0, sx1 = P(14900, 0)[0], P(18600, 0)[0]
    out.append(f'<rect x="{sx0:.2f}" y="{PY0:.2f}" width="{sx1 - sx0:.2f}" height="{P(0, -1800)[1] - PY0:.2f}" fill="#d3d9dd"/>')
    for yy in range(-1200, 39000, 3000): ln((16750, yy), (16750, yy + 1500), '#f4f6f7', .5)
    mx, my = P(17650, 26000); tx(mx, my, t['street'], 3.4, '#5d6a74', weight=700, page=True, extra=f'transform="rotate(-90 {mx:.2f} {my:.2f})" letter-spacing="1"')
    sidewalk = Polygon([(xb(-1800), -1800), (14900, -1800), (14900, 39400), (xb(39400), 39400)])
    sh(sidewalk, '#e4ddd1')
    mx, my = P(14000, 7000); tx(mx, my, t['sidewalk'], 2.4, '#9a8f80', weight=600, page=True, extra=f'transform="rotate(-90 {mx:.2f} {my:.2f})" letter-spacing="1.2"')
    sh(Polygon([(0, yr(0)), (xb(36500), yr(xb(36500))), tuple(Z2), (0, V['Z1_NW'][1])]), '#dcd7ce')
    tx(4800, 38200, t['drive'], 2.4, '#8a8178', weight=600, extra='letter-spacing=".4"')
    out.append('<path d="M' + 'L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in L['LOT'][0] if -8600 < x < 15000 and -1800 < y < 39500) + '" fill="none" stroke="#c0392b" stroke-width=".3" stroke-dasharray="3 1 .6 1"/>')
    # ---------- floors
    sh(FLOOR, 'url(#terr)')
    sh(ALLEY, 'url(#alley)', '#7a4a2c', .2)
    sh(PLAT, 'url(#deck)', '#6b4429', .3)
    sh(KIDS, 'url(#rubber)', '#c98a1c', .3)
    sh(R(BX0, BY0, BX1, BY1), 'url(#slate)', '#3b2a1e', .25)
    sh(planter.union(photo_plant).union(bbq_plant.difference(R(BX0, BY0, BX1, BY1))), 'url(#green)', '#5f8a44', .2)
    for it in items:
        if it['kind'] == 'sliver': sh(it['geom'], 'url(#green)', 'none')
    # ---------- steps / ramp / rails
    for k in ('stepsA', 'stepsB', 'barsteps'):
        g = [i for i in items if i['kind'] == k][0]['geom']; x0, y0, x1, y1 = g.bounds
        sh(g, '#dccbb0', '#6b4429', .2)
        if k == 'barsteps':
            for j in (1, 2): ln((x0, y0 + j * (y1 - y0) / 3), (x1, y0 + j * (y1 - y0) / 3), '#6b4429', .15)
        else:
            for j in (1, 2): ln((x0 + j * 300, y0), (x0 + j * 300, y1), '#6b4429', .15)
    sh(RAMP, '#d2bd99', '#6b4429', .25)
    for j in range(1, 12): ln((0, 30900 + j * 470), (1300, 30900 + j * 470), '#ad9470', .08)
    a, b = P(650, 31400), P(650, 36100); out.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#6b4429" stroke-width=".3" marker-end="url(#arrS)"/>')
    for a_, b_ in RAIL: ln(a_, b_, '#3b2a1e', .55)
    xs0, xs1 = xi(ENT[0]) - 200, xb(ENT[0]) + 300
    sh(R(xs0, ENT[0], xs1, ENT[1]), '#d8c9ae', '#6b4429', .2)
    for j in range(1, 5): ln((xs0 + j * (xs1 - xs0) / 5, ENT[0]), (xs0 + j * (xs1 - xs0) / 5, ENT[1]), '#6b4429', .15)
    for (a_, b_, op) in DOORS.values(): ln((-70, a_), (-70, b_), '#2A9DA8' if op else '#9a9a9a', 1.0)
    # ---------- tent canopy (under furniture)
    tr = [i for i in items if i['kind'] == 'tentroof'][0]['geom']
    sh(tr, '#f3dcc0', '#8a4a22', .3, 'opacity=".55"')
    # ---------- chairs
    def chair(g, back):
        sh(g, '#efe2c8', '#5a3a22', .1, 'filter="url(#sh)"')
        x0, y0, x1, y1 = g.bounds; bw = 90
        bb_ = {'n': R(x0, y1 - bw, x1, y1), 's': R(x0, y0, x1, y0 + bw), 'e': R(x1 - bw, y0, x1, y1), 'w': R(x0, y0, x0 + bw, y1)}[back]
        sh(bb_, '#8a5a36')
    for it in items:
        if it['kind'] == 'chair': chair(it['geom'], it['back'])
    for k in ORDER:
        for it in items:
            if it['kind'] == k:
                f, s_, fx = STY[k]; sh(it['geom'], f, s_, .14, 'filter="url(#sh)"' if fx else '')
    # ---------- details
    for yy in range(9800, 12800, 260):
        if not (10150 < yy < 10950): out.append(f'<circle cx="{P(380, yy)[0]:.2f}" cy="{P(380, yy)[1]:.2f}" r=".5" fill="#2A9DA8" opacity=".85"/>')
    for f_ in (.15, .38, .62, .85):
        ln((11250, 5150 + 2000 * f_ - 100), (11700, 5150 + 2000 * f_ + 100), '#ec5a2a', .6)
    for c_, r_ in (((11675, 4400), 4.3), ((11675, 7850), 3.8)):
        cx, cy = P(*c_); out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r_ * .7:.2f}" fill="none" stroke="#d9a23a" stroke-width=".35"/>')
    sh(HOOD, 'none', '#8E1F24', .3, 'stroke-dasharray="1.2 .8"')
    for xx in range(8400, 10900, 600): ln((xx, 8180), (xx + 300, 8180), '#ec8a2a', .5, 'opacity=".8"')   # heat lamps
    # photo arch: lit pointed arch on the jali screen + glow
    ax_, ay_ = P(2300, 2050); bx_, by_ = P(4300, 2050)
    cx, cy = P(3300, 2400); out.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="16" ry="7" fill="url(#glow)" opacity=".55"/>')
    out.append(f'<path d="M{ax_:.2f} {ay_:.2f}V{ay_ - 1.6:.2f}Q{ax_:.2f} {ay_ - 3.3:.2f} {(ax_ + bx_) / 2:.2f} {ay_ - 3.5:.2f}Q{bx_:.2f} {ay_ - 3.3:.2f} {bx_:.2f} {ay_ - 1.6:.2f}V{ay_:.2f}" fill="none" stroke="#d9a23a" stroke-width=".45"/>')
    cx, cy = P(3300, 5000); out.append(f'<path d="M{cx:.2f} {cy:.2f}L{cx - 3:.2f} {cy - 8.5:.2f}M{cx:.2f} {cy:.2f}L{cx + 3:.2f} {cy - 8.5:.2f}" stroke="#3b2a1e" stroke-width=".18" stroke-dasharray=".6 .5"/>')
    # palms (fronds over the pots)
    def palm(c, r, M=P, sc=S_):
        cx, cy = M(*c); rr = r / sc
        for a in range(0, 360, 40):
            ex, ey = cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a))
            out.append(f'<path d="M{cx:.2f} {cy:.2f}Q{(cx + ex) / 2 + rr * .25 * math.cos(math.radians(a + 90)):.2f} {(cy + ey) / 2 + rr * .25 * math.sin(math.radians(a + 90)):.2f} {ex:.2f} {ey:.2f}" stroke="#4f8a3a" stroke-width="{max(.35, rr * .14):.2f}" fill="none" stroke-linecap="round" opacity=".9"/>')
        out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rr * .18:.2f}" fill="#6b8a3a"/>')
    for it in items:
        if it['kind'] in ('palm', 'spalm'):
            c = it['geom'].centroid; palm((c.x, c.y), it['geom'].bounds[2] - c.x + 380)
    # tent: ridge lines + curtains on the open side + label
    tx0, ty0, tx1, ty1 = tr.bounds
    for (px, py) in ((tx0, ty0), (tx1, ty0), (tx0, ty1), (tx1, ty1)): ln((px, py), ((tx0 + tx1) / 2, (ty0 + ty1) / 2), '#8a4a22', .15, 'stroke-dasharray="1 .6" opacity=".7"')
    for yy in ((ty0, ty0 + 900), (ty1 - 900, ty1)):
        p = 'M' + ' '.join(f'{P(tx1 + 40 * math.sin(k * 1.3), yy[0] + k * 75)[0]:.2f},{P(tx1, yy[0] + k * 75)[1]:.2f}' for k in range(13)); out.append(f'<path d="{p}" fill="none" stroke="#7a3518" stroke-width=".55"/>')
    cx, cy = P(4400, 34500); out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="2.6" fill="url(#glow)"/>')
    # corridor: wavy velvet curtains, overhead swags
    for yy in (ENT[0] + 40, ENT[1] - 40):
        p = 'M' + ' '.join(f'{P(TUN[0] + k * 70, yy)[0]:.2f},{P(TUN[0], yy + 55 * math.sin(k * 1.2))[1]:.2f}' for k in range(int((TUN[1] - TUN[0]) / 70) + 1))
        out.append(f'<path d="{p}" fill="none" stroke="url(#velvet)" stroke-width="1.3" stroke-linecap="round"/><path d="{p}" fill="none" stroke="#5a2410" stroke-width=".18"/>')
    for xx in range(TUN[0] + 300, TUN[1], 700):
        a, b = P(xx, ENT[0] + 80), P(xx, ENT[1] - 80)
        out.append(f'<path d="M{a[0]:.2f} {a[1]:.2f}Q{a[0] - 2.4:.2f} {(a[1] + b[1]) / 2:.2f} {b[0]:.2f} {b[1]:.2f}" fill="none" stroke="#a0522d" stroke-width=".45" opacity=".55" stroke-dasharray="1.2 .5"/>')
    tx((TUN[0] + TUN[1]) / 2 + 600, ENT[0] + 1030, t['tunnel'], 1.8, '#f7e6c8', weight=700, extra='letter-spacing=".6" opacity=".95"')
    # street façade: sebil spout + basin ripple, arch outline on the street photo arch
    for it in items:
        if it['kind'] == 'sebilbasin':
            c = it['geom'].centroid; cx, cy = P(c.x, c.y)
            for r_ in (.8, 1.6, 2.4): out.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{r_ * .6:.2f}" ry="{r_:.2f}" fill="none" stroke="#e8fbff" stroke-width=".15" opacity=".8"/>')
    for it in items:
        if it['kind'] == 'sarch':
            c = it['geom'].centroid; cx, cy = P(c.x, c.y); out.append(f'<ellipse cx="{cx + 3:.2f}" cy="{cy:.2f}" rx="4" ry="9" fill="url(#glow)" opacity=".6"/>')
    # play elements
    for g, c in ((R(-6800, 400, -4200, 1700), '#f39a5c'), (R(-3400, 2600, -900, 3700), '#7fc3d4'), (C(-5400, 3000, 550), '#9bd27f'), (C(-2200, 1100, 450), '#f3d35c')):
        sh(g, c, '#7a5a1a', .15, 'filter="url(#sh)"')
    # ---------- roof
    for yy in TRUSS_Y: ln((0, yy), (xb(yy) - 750, yy), '#5A3A22', .12, 'stroke-dasharray="2 1.2" opacity=".4"')
    for c in cols: sh(R(c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150), '#2b1d12')
    # ---------- trees
    for c, r in ((TREE_N, 3200), (TREE_S, 3000)):
        lobes = unary_union([C(c[0], c[1], r * .72, 64)] + [C(c[0] + r * .52 * math.cos(math.radians(a)), c[1] + r * .52 * math.sin(math.radians(a)), r * .44, 48) for a in range(0, 360, 36)])
        sh(lobes, 'url(#leaf)', '#355e25', .3, 'opacity=".45" filter="url(#tsh)"')
        for a in range(18, 360, 72):
            g = C(c[0] + r * .35 * math.cos(math.radians(a)), c[1] + r * .35 * math.sin(math.radians(a)), r * .2, 32); sh(g, '#b4d987', 'none', 0, 'opacity=".25"')
        cx, cy = P(*c); out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{1400 / S_:.2f}" fill="none" stroke="#fbf6ec" stroke-width=".3" stroke-dasharray="1 .7" opacity=".9"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{320 / S_:.2f}" fill="#5a4636"/>')
    # ---------- axes (building grid) in the hall band
    AX = [("A'", 0), ('A', 4100), ('B', 9850), ('C', 15600), ('D', 21350), ('E', 27100), ('F', 32100), ('G', 37100)]
    for nm, yy in AX:
        ln((-8000, yy), (0, yy), '#8a7f70', .14, 'stroke-dasharray="4 .8 .6 .8"')
        X, Y = P(-8100, yy); out.append(f'<circle cx="{X:.2f}" cy="{Y:.2f}" r="2.3" fill="#f7f1e6" stroke="#5a4a3a" stroke-width=".25"/>'); tx(X, Y + .8, nm, 2.2, '#3b2a1e', weight=600, page=True)
    for nm, xx in (('5', -7250), ('6', 0)):
        ln((xx, 37300), (xx, 38700), '#8a7f70', .14, 'stroke-dasharray="4 .8 .6 .8"')
        X, Y = P(xx, 38950); out.append(f'<circle cx="{X:.2f}" cy="{Y:.2f}" r="2.3" fill="#f7f1e6" stroke="#5a4a3a" stroke-width=".25"/>'); tx(X, Y + .8, nm, 2.2, '#3b2a1e', weight=600, page=True)
    for (a_, ya), (b_, yb_) in zip(AX[:-1], AX[1:]): dim((-1300, ya), (-1300, yb_), 0)
    dim((-2900, 0), (-2900, 37100), 0)
    dim((-7250, 37900), (0, 37900), 0, col='#5a4a3a')
    # ---------- dimensions (plan)
    dim((0, 22300), (550, 22300), 0, size=1.4); dim((550, 22300), (1790, 22300), 0, '1240', size=1.4); dim((1790, 22300), (PW, 22300), 0, size=1.4)
    dim((0, 29300), (2400, 29300), 0, size=1.4)
    dim((-500, BAR[0]), (-500, BAR[1]), 0)
    dim((2950, BAR[0]), (2950, BAR[1]), 0, '9 × 620', size=1.4)
    dim((BX0, 9100), (BX1, 9100), 0)
    dim((12500, BY0), (12500, BY1), 0)
    dim((9400, BY1), (9400, 10210), 0, size=1.4, col='#1d6f77')
    dim((xb(ENT[0]) + 900, ENT[0]), (xb(ENT[0]) + 900, ENT[1]), 0)
    yb0, yb1, xwb = booth_west[4]
    dim((xwb - 250, yb0), (xwb - 250, yb1), 0, size=1.4); dim((xwb, yb1 + 300), (xi(yb1), yb1 + 300), 0, size=1.4)
    if pmin_at: dim((pmin_at[0], pmin_at[1]), (pmin_at[2], pmin_at[1]), 0, size=1.4, col='#1d6f77')
    dim((4550, 30550), (5900, 30550), 0, size=1.4, col='#1d6f77')
    dim((TX0 - 50, TY1 + 450), (TX1 + 50, TY1 + 450), 0, size=1.4)
    dim((2550, 28450), (4550, 28450), 0, size=1.4)
    dim((-150, 31000), (1300, 31000), 0, '1300', size=1.3)
    dim((xb(23000) - 1500, 23000), (xb(23000), 23000), 0, '1500', size=1.3, col='#5f6a3a')
    dim((3300, 1350), (5300, 1350), 0, size=1.3) if False else None
    dim((1700, 1450), (4900, 1450), 0, size=1.4)
    # ---------- flows
    def arrow(pts_, color, sw, marker, dash=''):
        out.append(f'<path d="M' + 'L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in pts_) + f'" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#{marker})" {dash}/>')
    arrow([(14300, 16800), (xi(16800) - 300, 16800), (3700, 16800)], '#2e7d3a', .75, 'arr')
    arrow([(6900, 39000), (6900, 36800), (7000, 33000)], '#2e7d3a', .75, 'arr')
    arrow([(-600, 25050), (2850, 25050), (6500, 25050)], '#d9731a', .45, 'arrS', 'stroke-dasharray="1 .8"')
    arrow([(1000, 14800), (1000, 4700), (1000, 5250), (7700, 5250), (8000, 4250)], '#d9731a', .45, 'arrS', 'stroke-dasharray="1 .8"')
    # ---------- table numbers
    for i, (x, y, k) in enumerate(tables):
        X, Y = P(x, y); out.append(f'<text x="{X:.2f}" y="{Y + .6:.2f}" font-family="Inter" font-size="1.65" font-weight="700" fill="#fff7e6" text-anchor="middle" paint-order="stroke" stroke="#3b2a1e" stroke-width=".35">{i + 1}</text>')
    # ---------- labels
    bx_, by_ = P(1800, 11450); tx(bx_ + .9, by_, t['barlbl'], 3.0, '#fbf6ec', weight=700, page=True, extra=f'transform="rotate(-90 {bx_ + .9:.2f} {by_:.2f})" letter-spacing="1.4"')
    tx(3300, 4700, t['ph'], 2.3, '#1F3F8A', weight=700, extra='letter-spacing=".6"')
    tx(xb(16800) + 2200, 17150, t['ent'], 2.6, '#2e7d3a', weight=700)
    level(-1500, 26500, t['lv_p']); level(3500, 14700, t['lv_t']); level(xb(20000) + 900, 20000, t['lv_s'])
    NUM = [(1, (xb(ENT[0]) + 2300, ENT[0] - 900)), (2, (9000, 16800)), (3, (5600, 17550)), (4, (2550, 20400)), (5, (xi(28300) - 650, 27300)), (6, (4300, 26000)),
           (7, (3550, 29600)), (8, (4400, 35050)), (9, (5600, 30600)), (10, (3400, 37300)), (11, (5700, 20450)), (12, (3400, 12600)), (13, (1000, 4700)),
           (14, (6150, 8050)), (15, (6300, 14300)), (16, (9800, 6100)), (17, (5600, 3950)), (18, (-3600, 2200)), (19, (xb(33600) + 800, 33600)),
           (20, (xb(SEBIL[0] + 800) + 900, SEBIL[0] + 800)), (21, (xb(26800) + 900, 26800))]
    for n, (x, y) in NUM: num(x, y, n)
    # ---------- scale bar, north
    sx, sy = 14, 481
    for k in range(5):
        out.append(f'<rect x="{sx + k * 1000 / S_:.2f}" y="{sy}" width="{1000 / S_:.2f}" height="1.3" fill="{"#3b2a1e" if k % 2 == 0 else "#f7f1e6"}" stroke="#3b2a1e" stroke-width=".15"/>')
    tx(sx, sy + 4.4, '0', 2.0, page=True, anchor='start'); tx(sx + 5000 / S_, sy + 4.4, '5 m' if lang == 'en' else '5 м', 2.0, page=True)
    tx(sx + 5000 / S_ + 5, sy + 1.3, t['scale'], 2.2, '#6b5a48', anchor='start', page=True)
    nx, ny = 268, 462; out.append(f'<path d="M{nx} {ny - 7}L{nx - 2.8} {ny + 2.4}L{nx} {ny + .8}L{nx + 2.8} {ny + 2.4}Z" fill="#3b2a1e"/>'); tx(nx, ny - 8.6, 'N' if lang == 'en' else 'С', 3.2, page=True, weight=700)
    # ---------- title
    tx(14, 30, 'SAMARKAND', 19, '#3b2a1e', anchor='start', family='Bitstream Charter', weight=700, page=True, extra='letter-spacing="3"')
    tx(14, 41, t['sub'], 6.2, '#8E1F24', anchor='start', family='Bitstream Charter', page=True)
    tx(14, 48.5, t['cuisine'], 3.4, '#6b5a48', anchor='start', page=True)
    tx(W - 14, 30, 'R6', 14, '#d9c9ad', anchor='end', family='Bitstream Charter', weight=700, page=True)
    tx(W - 14, 41, DATE, 3.0, '#6b5a48', anchor='end', page=True)
    out.append(f'<rect x="14" y="53" width="{W - 28}" height="1.8" fill="url(#majolica)"/>')
    # ---------- right column
    lx = 298; rx = W - 14
    def head(y, s): tx(lx, y, s, 3.1, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".6"'); out.append(f'<line x1="{lx}" y1="{y + 1.4}" x2="{rx}" y2="{y + 1.4}" stroke="#b8893a" stroke-width=".2"/>')
    ly = 66; head(ly, t['zones'])
    for i, (t1, t2) in enumerate(t['L']):
        yy = ly + 7 + i * 6.25; num(lx + 2.1, yy - .9, i + 1, page=True, r=2.0)
        tx(lx + 5.6, yy - .55, t1, 2.25, '#3b2a1e', anchor='start', weight=600, page=True); tx(lx + 5.6, yy + 1.95, t2, 1.8, '#6b5a48', anchor='start', page=True)
    sy0 = ly + 7 + len(t['L']) * 6.25 + 3; head(sy0, t['seats'])
    order = ['plaza', 'chinar_s', 'south', 'photo', 'bar', 'platform', 'north', 'chinar_n', 'booths', 'tapchans', 'tent', 'ntables']
    for i, k in enumerate(order):
        yy = sy0 + 6 + i * 3.9
        tx(lx, yy, t['S'][k], 2.1, '#3b2a1e', anchor='start', page=True); tx(rx, yy, str(seats[k]), 2.1, '#3b2a1e', anchor='end', weight=600, page=True)
    yt = sy0 + 6 + len(order) * 3.9 + .6
    out.append(f'<line x1="{lx}" y1="{yt - 2.6}" x2="{rx}" y2="{yt - 2.6}" stroke="#3b2a1e" stroke-width=".25"/>')
    tx(lx, yt + .8, t['total'], 2.7, '#8E1F24', anchor='start', weight=700, page=True); tx(rx, yt + .8, str(total), 3.4, '#8E1F24', anchor='end', weight=700, page=True)
    tx(lx, yt + 5, t['street_seats'], 2.0, '#6b5a48', anchor='start', page=True); tx(rx, yt + 5, f'~{street_seats}', 2.0, '#6b5a48', anchor='end', page=True)
    ey = yt + 13; head(ey, t['erg'])
    for i, (nm, norm, fact) in enumerate(t['E']):
        yy = ey + 6 + i * 3.8
        fact = fact.format(pmin=round(pmin), tap=tap_path, bb=round(bb))
        tx(lx, yy, nm, 1.95, '#3b2a1e', anchor='start', page=True); tx(rx - 17, yy, norm, 1.95, '#6b5a48', anchor='end', page=True)
        tx(rx, yy, fact, 1.95, '#1d6f77', anchor='end', weight=700, page=True)
    ky = ey + 6 + len(t['E']) * 3.8 + 4; head(ky, t['key'])
    kinds = ['sq', 'dash', 'axis', 'arr', 'dot', 'door', 'door2', 'hood', 'dim', 'tno']
    for i, (kind, s) in enumerate(zip(kinds, t['K'])):
        col_ = i % 2; row_ = i // 2
        kx = lx + col_ * 55; yy = ky + 6 + row_ * 4.2
        if kind == 'sq': out.append(f'<rect x="{kx}" y="{yy - 2}" width="2" height="2" fill="#2b1d12"/>')
        elif kind == 'arr': out.append(f'<line x1="{kx}" y1="{yy - 1}" x2="{kx + 5}" y2="{yy - 1}" stroke="#2e7d3a" stroke-width=".75" marker-end="url(#arr)"/>')
        elif kind in ('door', 'door2'): out.append(f'<line x1="{kx}" y1="{yy - 1}" x2="{kx + 5}" y2="{yy - 1}" stroke="{"#2A9DA8" if kind == "door" else "#9a9a9a"}" stroke-width="1"/>')
        elif kind == 'dim':
            out.append(f'<line x1="{kx}" y1="{yy - 1}" x2="{kx + 5}" y2="{yy - 1}" stroke="{DIMC}" stroke-width=".13"/>' + ''.join(f'<line x1="{x_ - .5}" y1="{yy - .5}" x2="{x_ + .5}" y2="{yy - 1.5}" stroke="{DIMC}" stroke-width=".3"/>' for x_ in (kx, kx + 5)))
        elif kind == 'tno': out.append(f'<text x="{kx + 2.5}" y="{yy - .3}" font-family="Inter" font-size="1.9" font-weight="700" fill="#fff7e6" text-anchor="middle" paint-order="stroke" stroke="#3b2a1e" stroke-width=".35">12</text>')
        elif kind == 'axis': out.append(f'<line x1="{kx}" y1="{yy - 1}" x2="{kx + 5}" y2="{yy - 1}" stroke="#8a7f70" stroke-width=".2" stroke-dasharray="1.6 .4 .3 .4"/>')
        else: out.append(f'<line x1="{kx}" y1="{yy - 1}" x2="{kx + 5}" y2="{yy - 1}" stroke="{ {"dash": "#5A3A22", "dot": "#d9731a", "hood": "#8E1F24"}[kind]}" stroke-width=".4" stroke-dasharray="{"1 .8" if kind == "dot" else "1.6 .9"}"/>')
        tx(kx + 7, yy - .2, s, 1.95, '#3b2a1e', anchor='start', page=True)
    ny_ = ky + 6 + 5 * 4.2 + 3
    for i, s in enumerate(t['notes']):
        # wrap notes at ~62 chars
        words, lines, cur = s.split(' '), [], ''
        for w_ in words:
            if len(cur) + len(w_) > 64: lines.append(cur); cur = w_
            else: cur = (cur + ' ' + w_).strip()
        lines.append(cur)
        for j, l_ in enumerate(lines):
            tx(lx + (0 if j == 0 else 2.2), ny_, ('· ' if j == 0 else '') + l_, 1.85, '#4b3a2e', anchor='start', page=True); ny_ += 2.9
        ny_ += .6

    # ======================= INSETS (bottom strip) =======================
    iy = 495
    out.append(f'<line x1="14" y1="{iy - 6}" x2="{W - 14}" y2="{iy - 6}" stroke="#b8893a" stroke-width=".25"/>')
    def mapper(ox, oy, x0, y1, sc):
        return lambda x, y: (ox + (x - x0) / sc, oy + (y1 - y) / sc)
    def callouts(M, pts, labels, ex, y0_, step=6.2):
        order_ = sorted(range(len(pts)), key=lambda i: M(*pts[i])[1])
        for j, i in enumerate(order_):
            cx, cy = M(*pts[i]); ty = y0_ + j * step
            out.append(f'<path d="M{cx:.2f} {cy:.2f}L{ex - 1:.2f} {ty - .7:.2f}" stroke="#8a7f70" stroke-width=".13" fill="none"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r=".45" fill="#8E1F24"/>')
            tx(ex, ty, labels[i], 1.85, '#3b2a1e', anchor='start', page=True)
    # (a) mangal 1:75
    ax0 = 14; sc = 75.0
    tx(ax0, iy, t['i_bbq'], 2.6, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".5"')
    M = mapper(ax0, iy + 4, BX0, BY1 + 100, sc)
    sh(R(BX0, BY0, BX1, BY1), 'url(#slate)', '#3b2a1e', .3, M=M)
    stor = [i for i in items if i['kind'] == 'storage'][0]['geom'].intersection(R(BX0, BY0 - 1500, BX1, BY0))
    for k in ('firewall', 'tandoorblock', 'tandoor', 'mangal', 'ledge', 'kazanblock', 'kazan', 'sinkbins', 'prep', 'pass', 'glass'):
        g = [i for i in items if i['kind'] == k][0]['geom']; f, s_, _ = STY[k]; sh(g, f, s_, .15, M=M)
    sh(HOOD, 'none', '#8E1F24', .3, 'stroke-dasharray="1.2 .8"', M=M)
    for f_ in (.15, .38, .62, .85): ln((11250, 5150 + 2000 * f_ - 100), (11700, 5150 + 2000 * f_ + 100), '#ec5a2a', .5, M=M)
    ln((BX0, 3800), (BX0, 4700), '#f7f1e6', .8, M=M)                      # staff door
    dim((BX0, BY1 + 60), (BX1, BY1 + 60), 2.2, M=M, size=1.5); dim((BX0, BY0), (BX0, BY1), 2.2, M=M, size=1.5)
    dim((8750, 6000), (11200, 6000), 0, M=M, size=1.4, col='#1d6f77')
    pts = [(11675, 4400), (11475, 6150), (11675, 7850), (9900, 4000), (8425, 6250), (9500, 8175), (12225, 6100), (8600, BY0 - 50)]
    callouts(M, pts, t['bbqL'], ax0 + (BX1 - BX0) / sc + 5, iy + 6, 6.6)
    # (b) tent 1:75
    bx0 = 112
    tx(bx0, iy, t['i_tent'], 2.6, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".5"')
    M = mapper(bx0, iy + 6, TX0 - 300, TY1 + 300, sc)
    sh(R(TX0 - 300, TY0 - 300, TX1 + 600, TY1 + 300), 'url(#terr)', 'none', M=M)
    sh(tr, '#f3dcc0', '#8a4a22', .3, 'opacity=".6"', M=M)
    for k in ('carpet', 'sofa', 'otable', 'pole'):
        for it in items:
            if it['kind'] == k and it['geom'].intersects(TENT.buffer(100)): f, s_, _ = STY[k]; sh(it['geom'], f, s_, .15, M=M)
    for it in items:
        if it['kind'] == 'lantern' and it['layer'] == 'SMK-R6-TENT': sh(it['geom'], 'url(#glow)', M=M)
    for (px, py) in ((tx0, ty0), (tx1, ty0), (tx0, ty1), (tx1, ty1)): ln((px, py), ((tx0 + tx1) / 2, (ty0 + ty1) / 2), '#8a4a22', .15, 'stroke-dasharray="1 .6"', M=M)
    dim((TX0 - 50, TY0 - 50), (TX1 + 50, TY0 - 50), -2.0, M=M, size=1.5); dim((TX0 - 50, TY0 - 50), (TX0 - 50, TY1 + 50), 2.0, M=M, size=1.5)
    dim((TX1 - 250, TY0 + 700), (TX1 - 250, TY1 - 700), 0, M=M, size=1.3, col='#1d6f77')
    pts = [(2850, 34500), (4400, 33550), (4900, 34500), (TX0 - 50, TY1 + 50), (TX1 + 230, TY0 + 150), (TX1 + 50, 34500)]
    callouts(M, pts, t['tentL'], bx0 + (TX1 - TX0 + 900) / sc + 4, iy + 8, 6.6)
    # (c) street bench section 1:50 (s = distance from lot line, + = sidewalk; z = level in mm)
    cx0 = 208; sc2 = 60.0
    tx(cx0, iy, t['i_st'], 2.6, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".5"')
    Ms = mapper(cx0 + 2, iy + 6, -2400, 1500, sc2)
    def rect(s0, z0, s1, z1, f, st='#3b2a1e', sw=.15, M=Ms): sh(R(s0, z0, s1, z1), f, st, sw, M=M)
    rect(0, -1600, 900, -1170, 'url(#hatchS)')                  # sidewalk
    rect(-2400, -1600, -1500, -470, 'url(#hatchS)')             # terrace slab
    rect(-550, -1170, 0, -720, 'url(#concrete)', '#3b2a1e', .25)      # bench
    rect(-700, -1170, -550, -170, 'url(#concrete)', '#3b2a1e', .25)   # back wall
    rect(-695, -600, -555, -250, 'url(#majolica)', 'none')
    rect(-1500, -1170, -1350, -170, 'url(#concrete)', '#3b2a1e', .25)  # inner planter wall
    rect(-1350, -1170, -700, -270, 'url(#soil)', '#3b2a1e', .15)
    rect(-900, -270, -600, 1400, '#a87444', '#3b2a1e', .2)            # wood-clad column
    rect(-850, -270, -650, 1400, '#4a4a4a', 'none')
    for c_, r_ in (((-1150, 150), 330), ((-1050, 450), 260), ((-1300, -20), 220)):
        X, Y = Ms(*c_); out.append(f'<circle cx="{X:.2f}" cy="{Y:.2f}" r="{r_ / sc2:.2f}" fill="url(#leaf)" opacity=".85"/>')
    rect(-2300, -470, -1820, -20, '#c98b62', '#3b2a1e')                # booth bench (end view)
    rect(-1780, -470, -1720, 1000, 'url(#lattice)', 'none')           # booth screen
    X1_, Y1_ = Ms(-1000, 1400); X2_, Y2_ = Ms(-500, 1400)
    out.append(f'<path d="M{X1_ - 2:.2f} {Y1_:.2f}H{X1_ + 2.5:.2f}l.6 -1.2l.8 2.4l.6 -1.2H{X2_ + 2:.2f}" fill="none" stroke="#3b2a1e" stroke-width=".2"/>')
    dim((-550, -1170), (0, -1170), -4.6, M=Ms, size=1.4); dim((-700, -1170), (-550, -1170), -4.6, M=Ms, size=1.2, ext=True)
    dim((-1500, -1170), (-700, -1170), -4.6, M=Ms, size=1.4); dim((-1500, -1170), (0, -1170), -8.2, M=Ms, size=1.4)
    dim((0, -1170), (0, -720), -2.0, M=Ms, size=1.4); dim((-550, -720), (-550, -170), 0, '550', M=Ms, size=1.2) if False else None
    for zz, s in ((-1170, '−1.170'), (-470, '−0.470'), (-170, '−0.170'), (-720, '−0.720')):
        X, Y = Ms(300 if zz in (-1170, -720) else -2350, zz); level(X, Y, s, page=True, size=1.6)
    callouts(Ms, [(-275, -950), (-625, -400), (-1050, -700), (-2100, -300), (450, -1400)], t['stL'], cx0 + 3900 / sc2 + 5, iy + 8, 6.4)
    # (d) aivan section 1:50
    dx0 = 310
    tx(dx0, iy, t['i_pl'], 2.6, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".5"')
    Mp = mapper(dx0 + 1, iy + 6, -300, 1300, sc2)
    rect(-300, -900, 0, 1300, 'url(#hatchS)', M=Mp)                  # hall wall
    rect(0, -900, 3300, 0, '#c69c6d', '#3b2a1e', .2, M=Mp)            # deck + structure
    rect(0, -900, 3300, -470, 'url(#hatchS)', 'none', M=Mp)
    rect(3300, -900, 3900, -470, 'url(#hatchS)', M=Mp)
    rect(0, 0, 550, 450, 'url(#ikat)', '#3b2a1e', .2, M=Mp); rect(0, 450, 120, 900, 'url(#ikat)', '#3b2a1e', .2, M=Mp)
    rect(600, 710, 1300, 750, '#a87444', '#3b2a1e', .2, M=Mp); rect(920, 0, 980, 710, '#5a3a22', 'none', M=Mp); rect(820, 0, 1080, 30, '#5a3a22', 'none', M=Mp)
    rect(1340, 430, 1790, 470, '#efe2c8', '#3b2a1e', .15, M=Mp); rect(1700, 470, 1790, 880, '#8a5a36', 'none', M=Mp)
    for xx in (1360, 1760): rect(xx, 0, xx + 30, 430, '#5a3a22', 'none', M=Mp)
    rect(3250, 0, 3300, 1000, 'url(#lattice)', '#2b1d12', .15, M=Mp); rect(3200, 980, 3320, 1040, '#5a3a22', 'none', M=Mp)
    dim((0, 0), (550, 0), -5.2, M=Mp, size=1.3); dim((600, 0), (1300, 0), -5.2, M=Mp, size=1.3); dim((1340, 0), (1790, 0), -5.2, M=Mp, size=1.3)
    dim((1790, 0), (3300, 0), -5.2, M=Mp, size=1.3); dim((0, 0), (3300, 0), -14.6, M=Mp, size=1.4)
    dim((3500, 0), (3500, 1000), 0, M=Mp, size=1.3); dim((450, 0), (450, 450), 0, '450', M=Mp, size=1.2) if False else None
    dim((1150, 0), (1150, 750), 0, M=Mp, size=1.2, col='#1d6f77')
    level(*Mp(-250, 0), '±0.000', page=True, size=1.6); level(*Mp(3420, -470), '−0.470', page=True, size=1.6)
    callouts(Mp, [(275, 300), (950, 730), (1560, 450), (2550, 100), (3275, 600), (3600, -600)], t['plL'], dx0 + 4300 / sc2 + 3, iy + 8, 6.4)

    # ---------- footer
    out.append(f'<rect x="14" y="{H - 20}" width="{W - 28}" height="1.4" fill="url(#majolica)"/>')
    tx(14, H - 12.5, f'SAMARKAND  ·  {REV}  ·  {DATE}', 2.5, '#3b2a1e', anchor='start', weight=600, page=True)
    tx(W / 2, H - 12.5, t['foot'], 2.3, '#6b5a48', page=True)
    tx(W - 14, H - 12.5, 'designed by Nomad Group', 2.1, '#8a7f70', anchor='end', page=True, extra='font-style="italic" letter-spacing=".3"')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">{DEFS}{"".join(out)}</svg>'

for lang in ('ru', 'en'):
    open(f'{OUT}/samarkand-terrace-layout-{REV}-{lang}.svg', 'w').write(build(lang))
print('svg ok')
