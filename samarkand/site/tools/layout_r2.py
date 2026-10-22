"""Samarkand covered terrace — Layout R2 (owner markup 2026-10-22).
Geometry in local mm (origin axis 6 x axis A', x east, y north). Outputs: JSON, DXF (base + SMK-R2-*), SVG presentation plan.
"""
import sys, json, math
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import split, unary_union
from shapely import affinity
import ezdxf

Z = json.load(open(sys.argv[1])); BASE_DXF = sys.argv[2]; OUT = sys.argv[3]
L = Z['layers']; V = Z['zone_vertices']

# ---------------- site lines ----------------
Z2, Z3 = V['Z2_NE'], V['Z3_SE']
SLOPE = (Z3[0] - Z2[0]) / (Z2[1] - Z3[1])
def xb(y): return Z3[0] - (y - Z3[1]) * SLOPE
def xi(y): return xb(y) - 1500
def yr(x): return 37090.5 - 0.06542 * (x - 83.6)
def ys(x): return Z3[1] * (x - V['Z4_S'][0]) / (Z3[0] - V['Z4_S'][0])
TH = math.atan(SLOPE)
D_N = (-math.sin(TH), math.cos(TH)); N_W = (-math.cos(TH), -math.sin(TH))
zone = Polygon(Z['zone'])
U = sorted(split(zone, LineString([(-20000, yr(-20000)), (30000, yr(30000))])).geoms, key=lambda g: g.centroid.y)[0]
STAIR = (13300, 18300)
planter = Polygon([(xi(0), 0), (xb(0), 0), (xb(40000), 40000), (xi(40000), 40000)]).intersection(U)
planter = planter.difference(Polygon([(xi(STAIR[0]) - 50, STAIR[0]), (xb(STAIR[0]) + 50, STAIR[0]), (xb(STAIR[1]) + 50, STAIR[1]), (xi(STAIR[1]) - 50, STAIR[1])]))
FLOOR = U.difference(planter)

def R(x0, y0, x1, y1): return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
def C(x, y, r, n=48): return Point(x, y).buffer(r, n)
def obl(p0, s0, s1, t0, t1):
    return Polygon([(p0[0] + D_N[0] * s + N_W[0] * t, p0[1] + D_N[1] * s + N_W[1] * t) for s, t in ((s0, t0), (s1, t0), (s1, t1), (s0, t1))])
def opt(p0, s, t): return (p0[0] + D_N[0] * s + N_W[0] * t, p0[1] + D_N[1] * s + N_W[1] * t)

items = []
def add(kind, geom, layer, **kw):
    items.append(dict(kind=kind, geom=geom, layer=layer, **kw)); return geom
seats = {}
def seat(k, n): seats[k] = seats.get(k, 0) + n

# ======================= ZONES =======================
zones = {}
# --- 3 raised aivan platform (filled steps + extension) at ±0.000
PLAT = R(0, 16550, 2400, 30900)
zones['platform'] = add('zone', PLAT, 'SMK-R2-ZONE', name='Raised aivan platform ±0.000')
STEPS_A = R(2400, 16550, 3300, 19700)   # guests from the alley
STEPS_B = R(2400, 24300, 3300, 25800)   # staff from the open door
for st in (STEPS_A, STEPS_B):
    add('steps', st, 'SMK-R2-STEPS')
RAMP = R(0, 30900, 1300, 36540)          # 1:12, 470 rise, lands at the north entrance
add('ramp', RAMP, 'SMK-R2-STEPS', label='Ramp 1:12')
# railing along the platform edge (except steps)
RAIL = [((2400, 19700), (2400, 24300)), ((2400, 25800), (2400, 30900)), ((1300, 30900), (2400, 30900)), ((1300, 30900), (1300, 36540))]
# doors on the facade (from the as-built F1 plan)
DOORS = {'C–D main doors (open)': (16795, 20155, True), 'D–E south door (closed)': (22545, 24225, False),
         'D–E north door (open)': (24225, 25905, True), 'E–F back door by the lift (open)': (28663, 30363, True)}

# --- platform tables (4-tops, chairs E/W, glass behind)
def table_ew(cx, cy, tl=1200, tw=800, layer='SMK-R2-FURN', key=None):
    add('table', R(cx - tw / 2, cy - tl / 2, cx + tw / 2, cy + tl / 2), layer)
    for sx in (-1, 1):
        x0 = cx + sx * (tw / 2 + 50); x1 = x0 + sx * 450
        for sy in (-tl / 4, tl / 4):
            add('chair', R(x0, cy + sy - 225, x1, cy + sy + 225), layer)
    if key: seat(key, 4)
def table_ns(cx, cy, tl=1200, tw=800, layer='SMK-R2-FURN', key=None):
    add('table', R(cx - tl / 2, cy - tw / 2, cx + tl / 2, cy + tw / 2), layer)
    for sy in (-1, 1):
        y0 = cy + sy * (tw / 2 + 50); y1 = y0 + sy * 450
        for sx in (-tl / 4, tl / 4):
            add('chair', R(cx + sx - 225, y0, cx + sx + 225, y1), layer)
    if key: seat(key, 4)
for cy in (21000, 23400, 27000):
    table_ew(1100, cy, key='Aivan platform')
add('station', R(1700, 30300, 2300, 30880), 'SMK-R2-SERV', label='W1')

# --- 4 sea-view booths (owner's yellow)
B_Y0 = 20100; P_B = (xi(B_Y0), B_Y0); B_D = 1400; B_W = 2000; N_B = 8
for k in range(N_B):
    s0 = k * B_W
    add('rug', obl(P_B, s0 + 60, s0 + B_W, 0, B_D), 'SMK-R2-FURN')
    add('screen', obl(P_B, s0, s0 + 60, 0, B_D), 'SMK-R2-FURN')
    add('bench', obl(P_B, s0 + 90, s0 + 590, 100, 1350), 'SMK-R2-FURN')
    add('table', obl(P_B, s0 + 660, s0 + 1340, 150, 1150), 'SMK-R2-FURN')
    add('bench', obl(P_B, s0 + 1410, s0 + 1910, 100, 1350), 'SMK-R2-FURN')
    lp = opt(P_B, s0 + 1000, 650); add('lantern', C(lp[0], lp[1], 130, 16), 'SMK-R2-FURN')
    seat('Sea-view booths', 4)
add('screen', obl(P_B, N_B * B_W, N_B * B_W + 60, 0, B_D), 'SMK-R2-FURN')
BOOTHS = obl(P_B, 0, N_B * B_W + 60, 0, B_D)
zones['booths'] = BOOTHS
def booth_west(y): return xi(y) - B_D * math.cos(TH)

# --- trees (existing, kept): chinar courts
TREE_N, TREE_S = (5999, 27097), (5999, 12722)
def ring(c, r0, r1, a0=0, a1=360):
    an = C(c[0], c[1], r1, 72).difference(C(c[0], c[1], r0, 72))
    if a1 - a0 >= 360: return an
    pts = [c] + [(c[0] + 5000 * math.cos(math.radians(a)), c[1] + 5000 * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 5)]
    return an.intersection(Polygon(pts))
for c, a0, a1, n, key in ((TREE_N, 70, 290, 7, 'Chinar bench north'), (TREE_S, 0, 360, 10, 'Chinar bench south')):
    add('treepit', C(c[0], c[1], 1000), 'SMK-R2-TREE')
    add('ringbench', ring(c, 1000, 1450, a0, a1), 'SMK-R2-TREE')
    seat(key, n)

# --- dining north (west of the path)
for cy in (21300, 23700):
    for cx in (4300, 6400):
        table_ns(cx, cy, key='Dining north')
table_ew(3300, 27100, key='Dining north')

# --- tapchan court around a hauz (Lyabi-Hauz)
HAUZ = (4375, 32400)
hauz = Polygon([(HAUZ[0] + 700 * math.cos(math.radians(22.5 + 45 * i)), HAUZ[1] + 700 * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)])
add('hauz_border', hauz.buffer(220, join_style=2), 'SMK-R2-TREE')
add('hauz', hauz, 'SMK-R2-TREE')
for (x0, x1, y0, y1) in ((2500, 4300, 29100, 31100), (4450, 6250, 29100, 31100), (1650, 3450, 33700, 35700), (4200, 6000, 33700, 35700)):
        add('tapchan', R(x0, y0, x1, y1), 'SMK-R2-FURN')
        add('tapchan_rug', R(x0 + 150, y0 + 150, x1 - 150, y1 - 150), 'SMK-R2-FURN')
        add('tapchan_table', R(x0 + 500, y0 + 550, x1 - 500, y1 - 550), 'SMK-R2-FURN')
        seat('Tapchans around the hauz', 6)
zones['tapchan court'] = R(1500, 29000, 6100, 36300)

# --- alley + plaza + host
ALLEY = R(3300, 16300, 7600, 19700)
zones['alley'] = ALLEY
PLAZA = Polygon([(7450, 11272), (xi(11272), 11272), (xi(STAIR[0]), STAIR[0]), (xb(STAIR[0]), STAIR[0]), (xb(STAIR[1]), STAIR[1]), (xi(STAIR[1]), STAIR[1]), (xi(19900), 19900), (7600, 19900), (7600, 16300), (7450, 14172)]).intersection(U)
zones['plaza'] = PLAZA
add('host', R(9000, 19000, 9600, 19500), 'SMK-R2-SERV', label='Host')
add('bench_wait', obl((xi(18700), 18700), 0, 1150, 0, 450), 'SMK-R2-SERV')

# --- bar on the facade (unchanged from R1)
BAR_Y0, BAR_Y1 = 8600, 15200
add('backbar', R(0, BAR_Y0, 550, BAR_Y1), 'SMK-R2-BAR')
add('barcounter', R(1500, BAR_Y0, 2100, BAR_Y1), 'SMK-R2-BAR')
add('bartop', R(2100, BAR_Y0, 2400, BAR_Y1), 'SMK-R2-BAR')
y = BAR_Y0 + 450
while y + 225 <= BAR_Y1 - 150:
    add('stool', C(2750, y, 200, 24), 'SMK-R2-BAR'); seat('Bar counter', 1); y += 620
zones['bar'] = R(0, BAR_Y0, 3000, BAR_Y1)

# --- 9 staff service station (owner's blue): shelving + counter behind a carved screen
SS = R(0, 4250, 2000, 8600)
zones['service'] = SS
add('shelving', R(0, 4300, 600, 8550), 'SMK-R2-SERV', label='Shelving: glasses, napkins, cutlery, linen, menus')
add('counter', R(1400, 5400, 2000, 8200), 'SMK-R2-SERV', label='Counter: POS, water, ice, tray landing, dish drop')
add('screenwall', R(1980, 5300, 2060, 8600), 'SMK-R2-SERV')

# --- dining south
for cy in (7050, 9450):
    for cx in (4900, 7100):
        table_ns(cx, cy, key='Dining south')
for c in ((9300, 10600), (10100, 11900)):
    add('hightable', C(c[0], c[1], 350), 'SMK-R2-FURN')
    for a in (0, 180):
        add('stool', C(c[0] + 600 * math.cos(math.radians(a)), c[1] + 600 * math.sin(math.radians(a)), 190, 24), 'SMK-R2-FURN')
    seat('High tables by the BBQ', 2)

# --- 12 BBQ / mangal kitchen
P0 = (xi(3600), 3600)
BBQ = obl(P0, 0, 6100, 0, 3000); zones['bbq'] = BBQ
add('bbq_floor', BBQ, 'SMK-R2-BBQ')
add('firewall', obl(P0, 0, 6100, 0, 150), 'SMK-R2-BBQ', label='Brick fire wall h 1.8')
add('tandoor_block', obl(P0, 150, 1350, 150, 1250), 'SMK-R2-BBQ')
tp = opt(P0, 750, 700); add('tandoor', C(tp[0], tp[1], 450), 'SMK-R2-BBQ', label='Tandoor Ø900')
add('mangal', obl(P0, 1500, 3900, 150, 750), 'SMK-R2-BBQ', label='Mangal 2400 × 600, charcoal')
add('kazan_block', obl(P0, 4050, 5050, 150, 1150), 'SMK-R2-BBQ')
kp = opt(P0, 4550, 650); add('kazan', C(kp[0], kp[1], 400), 'SMK-R2-BBQ', label='Kazan Ø800 on gas burner (plov)')
add('sinkbins', obl(P0, 5200, 6100, 150, 750), 'SMK-R2-BBQ', label='Hand sink · charcoal · ash bin')
add('prep', obl(P0, 900, 3700, 2350, 3000), 'SMK-R2-BBQ', label='Cold prep: u/c fridges (skewers), prep sink')
add('pass', obl(P0, 3700, 6100, 2350, 3000), 'SMK-R2-BBQ', label='Pass: heat lamps, bread display')
add('glass', obl(P0, 3700, 6100, 2980, 3030), 'SMK-R2-BBQ')
add('hood', obl(P0, 50, 5150, 50, 1350), 'SMK-R2-BBQ', label='Exhaust hood + stack above roof')
VIEW = obl(P0, 900, 6100, 3030, 3800); zones['bbq view'] = VIEW
# service corridor from the station to the BBQ entry
CORR = Polygon([(2000, 4750), (8000, 4750), (opt(P0, 450, 3000)[0], opt(P0, 450, 3000)[1]), (opt(P0, 450, 3600)[0], opt(P0, 450, 3600)[1]), (8000, 5800), (2000, 5800)])

# --- 13 photo zone + 14 kids zone
ang = math.atan2(Z3[1], Z3[0] - V['Z4_S'][0])
def on_south(x, off): y = ys(x); return (x - math.sin(ang) * off, y + math.cos(ang) * off)
add('backdrop', Polygon([on_south(1300, 250), on_south(5700, 250), on_south(5700, 650), on_south(1300, 650)]), 'SMK-R2-PHOTO', label='Pishtaq backdrop')
rp = on_south(3500, 2400); add('rosette', C(rp[0], rp[1], 900, 64), 'SMK-R2-PHOTO')
PHOTO = Polygon([on_south(1100, 0), on_south(6400, 0), (6400, 4700), (1100, 4700)]).intersection(FLOOR); zones['photo'] = PHOTO
KIDS = Polygon([V['Z5_pocketSW'], V['Z4_S'], V['Z7_bldgSE'], V['Z6_pocketNW']]); zones['kids'] = KIDS
add('play', R(-6900, 300, -3900, 1900), 'SMK-R2-KIDS'); add('play2', R(-3500, 2700, -800, 3800), 'SMK-R2-KIDS'); add('play3', C(-5400, 3100, 600), 'SMK-R2-KIDS')

# ======================= ROOF =======================
TRUSS_Y = [4100, 9850, 15600, 21350, 25600, 29100, 32100, 36300]
COL_E = [4100, 9850, 13000, 18600, 21350, 25600, 29100, 32100, 36300]
cols = [(xb(y) - 750, y) for y in COL_E] + [(-7050, 200), (-350, 250)]
OCULI = [(TREE_N, 1400), (TREE_S, 1400)]

# ======================= CHECKS =======================
probs = []
furn = [it for it in items if it['kind'] in ('table', 'chair', 'bench', 'tapchan', 'stool', 'hightable', 'station', 'host', 'ringbench', 'shelving', 'counter')]
door_clear = [R(0, a, 1500, b) for k, (a, b, op) in DOORS.items() if op]
pits = [C(*TREE_N, 1000), C(*TREE_S, 1000)]
okfloor = FLOOR.union(PLAT).buffer(5)
for it in furn:
    g = it['geom']
    if not okfloor.contains(g): probs.append(f"{it['kind']} off floor @ {g.centroid.x:.0f},{g.centroid.y:.0f}")
    for d in door_clear:
        if g.intersection(d).area > 500: probs.append(f"{it['kind']} blocks open door @ {g.centroid.y:.0f}")
    if it['kind'] != 'ringbench':
        for p in pits:
            if g.intersects(p): probs.append(f"{it['kind']} in tree pit @ {g.centroid.x:.0f},{g.centroid.y:.0f}")
    if g.intersects(RAMP) or (g.intersects(STEPS_A) or g.intersects(STEPS_B)) and g.intersection(STEPS_A.union(STEPS_B)).area > 500:
        probs.append(f"{it['kind']} on ramp/steps @ {g.centroid.x:.0f},{g.centroid.y:.0f}")
    if g.intersects(CORR) and it['kind'] in ('table', 'chair'): probs.append(f"{it['kind']} in service corridor @ {g.centroid.x:.0f},{g.centroid.y:.0f}")
# pairwise overlaps between solid furniture
solid = [it for it in furn]
for i in range(len(solid)):
    for j in range(i + 1, len(solid)):
        a, b = solid[i]['geom'], solid[j]['geom']
        if a.intersection(b).area > 2000 and {solid[i]['kind'], solid[j]['kind']} != {'table', 'chair'}:
            probs.append(f"overlap {solid[i]['kind']}/{solid[j]['kind']} @ {a.centroid.x:.0f},{a.centroid.y:.0f}")
# path clear width west of the booths (main N–S path)
west_furn = unary_union([it['geom'] for it in furn if it['geom'].centroid.x < 7300 and it['geom'].centroid.y > 19800] + [C(*TREE_N, 1000)])
path_min = 1e9; path_at = None
for yy in range(20200, 36200, 100):
    xw = booth_west(yy)
    seg = LineString([(xw - 3000, yy), (xw, yy)])
    hit = seg.intersection(west_furn)
    xe = max([p[0] for g in getattr(hit, 'geoms', [hit]) for p in getattr(g, 'coords', [])] or [xw - 3000])
    w = xw - xe
    if w < path_min: path_min, path_at = w, yy
clear = {'Main path west of booths (min)': round(path_min), 'Behind bar stools': 4300 - 2950, 'Bartender aisle': 950,
         'Service station aisle': 800, 'BBQ cook aisle': 1100, 'Service corridor': 1050, 'Alley': 3400, 'Ramp': '1300 (1:12)'}
total = sum(seats.values())
zone_m2 = {k: round(v.area / 1e6, 1) for k, v in zones.items()}
res = dict(seats=seats, total=total, zones_m2=zone_m2, clear=clear, path_min_at_y=path_at, problems=probs)
print(json.dumps(res, indent=1, ensure_ascii=False))

# ======================= EXPORT JSON + DXF =======================
def coords(g):
    gs = getattr(g, 'geoms', [g]); return [[(round(x, 1), round(y, 1)) for x, y in p.exterior.coords] for p in gs]
json.dump(dict(res, columns=cols, truss_y=TRUSS_Y, oculi=[[list(c), r] for c, r in OCULI], doors=DOORS,
               items=[dict(kind=i['kind'], layer=i['layer'], label=i.get('label'), poly=coords(i['geom'])) for i in items]),
          open(f'{OUT}/samarkand-terrace-layout-R2.json', 'w'), ensure_ascii=False)
doc = ezdxf.readfile(BASE_DXF); msp = doc.modelspace()
for lay, col in (('SMK-R2-ZONE', 8), ('SMK-R2-FURN', 7), ('SMK-R2-BAR', 40), ('SMK-R2-BBQ', 30), ('SMK-R2-PHOTO', 5), ('SMK-R2-KIDS', 2),
                 ('SMK-R2-SERV', 4), ('SMK-R2-TREE', 3), ('SMK-R2-STEPS', 7), ('SMK-R2-ROOF', 34)):
    if lay not in doc.layers: doc.layers.add(lay, color=col)
for it in items:
    for p in coords(it['geom']): msp.add_lwpolyline(p[:-1], close=True, dxfattribs={'layer': it['layer']})
for a, b in RAIL: msp.add_line(a, b, dxfattribs={'layer': 'SMK-R2-STEPS'})
for c in cols: msp.add_lwpolyline(list(R(c[0] - 125, c[1] - 125, c[0] + 125, c[1] + 125).exterior.coords)[:-1], close=True, dxfattribs={'layer': 'SMK-R2-ROOF'})
for yy in TRUSS_Y: msp.add_line((0, yy), (xb(yy) - 750, yy), dxfattribs={'layer': 'SMK-R2-ROOF'})
for c, r in OCULI: msp.add_circle(c, r, dxfattribs={'layer': 'SMK-R2-ROOF'})
doc.saveas(f'{OUT}/samarkand-terrace-layout-R2.dxf')

# ======================= SVG PRESENTATION =======================
S = 150.0; PX0, PY0 = 14.0, 66.0; XMIN, YMAX = -8600.0, 39600.0
def P(x, y): return (PX0 + (x - XMIN) / S, PY0 + (YMAX - y) / S)
def pts(g): return ' '.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in g.exterior.coords)
def path_d(g):
    out = []
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty: continue
        out.append('M' + ' L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in p.exterior.coords) + 'Z')
        for r in p.interiors: out.append('M' + ' L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in r.coords) + 'Z')
    return ' '.join(out)
svg = []
def shape(g, fill='none', stroke='none', sw=.15, extra=''):
    svg.append(f'<path d="{path_d(g)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" fill-rule="evenodd" {extra}/>')
def line(a, b, stroke='#333', sw=.2, extra=''):
    (x1, y1), (x2, y2) = P(*a), P(*b); svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def text(x, y, s, size=2.2, fill='#3b2a1e', anchor='middle', weight=400, family='Inter', extra='', page=False):
    if not page: x, y = P(x, y)
    svg.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>')
def num(x, y, n, page=False):
    if not page: x, y = P(x, y)
    svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.3" fill="#1F3F8A" stroke="#f7f1e6" stroke-width=".5"/>')
    svg.append(f'<text x="{x:.2f}" y="{y + 1.05:.2f}" font-family="Inter" font-size="2.7" font-weight="700" fill="#fff" text-anchor="middle">{n}</text>')

DEFS = '''<defs>
<pattern id="girih" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="#efe2c8"/><g fill="none" stroke="#dcc6a0" stroke-width=".18"><rect x="1.1" y="1.1" width="1.8" height="1.8"/><rect x="1.1" y="1.1" width="1.8" height="1.8" transform="rotate(45 2 2)"/><path d="M0 0L.6 .6M4 0L3.4 .6M0 4L.6 3.4M4 4L3.4 3.4"/></g><circle cx="2" cy="2" r=".35" fill="#c98b62" opacity=".55"/></pattern>
<pattern id="paving" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="3" fill="#d6a77e"/><path d="M0 0H1.5V.75H0zM1.5 .75H3V1.5H1.5zM0 1.5H1.5V2.25H0zM1.5 2.25H3V3H1.5z" fill="#cc9670"/><path d="M0 .75H3M0 1.5H3M0 2.25H3" stroke="#b8805a" stroke-width=".08"/></pattern>
<pattern id="deck" width="6" height="1.2" patternUnits="userSpaceOnUse"><rect width="6" height="1.2" fill="#c49a6c"/><path d="M0 1.15H6M3 0V1.2" stroke="#9b7148" stroke-width=".12"/><path d="M0 .4H6" stroke="#b78c5f" stroke-width=".06"/></pattern>
<pattern id="slate" width="2.4" height="2.4" patternUnits="userSpaceOnUse"><rect width="2.4" height="2.4" fill="#8d877f"/><path d="M0 0H2.4V2.4" fill="none" stroke="#6d6862" stroke-width=".12"/></pattern>
<pattern id="ikat" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="3" fill="#8E1F24"/><path d="M1.5 .2L2.4 1.5L1.5 2.8L.6 1.5Z" fill="#d9a23a"/><path d="M1.5 .9L1.95 1.5L1.5 2.1L1.05 1.5Z" fill="#1F3F8A"/></pattern>
<pattern id="suzani" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="#efe3cf"/><circle cx="2" cy="2" r="1.15" fill="#b8323a"/><circle cx="2" cy="2" r=".55" fill="#d9a23a"/><circle cx="0" cy="0" r=".5" fill="#2a6f4a"/><circle cx="4" cy="0" r=".5" fill="#2a6f4a"/><circle cx="0" cy="4" r=".5" fill="#2a6f4a"/><circle cx="4" cy="4" r=".5" fill="#2a6f4a"/></pattern>
<pattern id="soft" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="3" fill="#ffd978"/><circle cx=".8" cy=".8" r=".35" fill="#ef8a5b"/><circle cx="2.2" cy="2.1" r=".35" fill="#5bb7c9"/><circle cx="2.3" cy=".7" r=".25" fill="#8ccf6f"/></pattern>
<pattern id="majolica" width="2.2" height="2.2" patternUnits="userSpaceOnUse"><rect width="2.2" height="2.2" fill="#1F3F8A"/><path d="M1.1 .2L1.4 .8L2 1.1L1.4 1.4L1.1 2L.8 1.4L.2 1.1L.8 .8Z" fill="#2A9DA8"/><circle cx="1.1" cy="1.1" r=".25" fill="#efe6d8"/></pattern>
<pattern id="hatch" width="2" height="2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="2" height="2" fill="#e2dbd0"/><path d="M0 0V2" stroke="#cfc6b8" stroke-width=".25"/></pattern>
<pattern id="lattice" width="1" height="1" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1" height="1" fill="#5A3A22"/><rect x=".25" y=".25" width=".5" height=".5" fill="#8a5a36"/></pattern>
<pattern id="plants" width="7" height="7" patternUnits="userSpaceOnUse"><rect width="7" height="7" fill="#9dbb7c"/><circle cx="1.8" cy="2" r="1.4" fill="#7fa45e"/><circle cx="5" cy="4.6" r="1.7" fill="#6f9a50"/><circle cx="2.4" cy="5.6" r=".9" fill="#86ad66"/><circle cx="5.6" cy="1.3" r=".8" fill="#5f8a44"/></pattern>
<radialGradient id="water" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#bfe8f0"/><stop offset="1" stop-color="#3f9fb8"/></radialGradient>
<radialGradient id="canopy" cx="45%" cy="40%" r="60%"><stop offset="0" stop-color="#8fbf63" stop-opacity=".75"/><stop offset="1" stop-color="#4e7d36" stop-opacity=".6"/></radialGradient>
<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffd27a" stop-opacity=".95"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>
<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx=".35" dy=".45" stdDeviation=".35" flood-color="#3b2a1e" flood-opacity=".35"/></filter>
<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="#2e7d3a"/></marker>
<marker id="arrS" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="#d9731a"/></marker>
</defs>'''

W, H = 297, 420
svg.append(f'<rect width="{W}" height="{H}" fill="#f7f1e6"/>')
svg.append(f'<rect x="7" y="7" width="{W - 14}" height="{H - 14}" fill="none" stroke="#5A3A22" stroke-width=".6"/><rect x="8.4" y="8.4" width="{W - 16.8}" height="{H - 16.8}" fill="none" stroke="#b8893a" stroke-width=".25"/>')
# building + context
shape(R(XMIN + 200, 4100, 0, 37100), fill='url(#hatch)')
text(-4300, 21000, 'MAIN HALL  ·  ±0.000', 3.0, '#8a7f70', extra=f'transform="rotate(-90 {P(-4300, 21000)[0]:.2f} {P(-4300, 21000)[1]:.2f})" letter-spacing=".6"', weight=600)
lot = Polygon(L['LOT'][0]) if len(L['LOT'][0]) > 3 else None
svg.append('<path d="M' + ' L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in L['LOT'][0] if -8600 < x < 16000 and -3000 < y < 39600) + '" fill="none" stroke="#c0392b" stroke-width=".3" stroke-dasharray="3 1 .6 1"/>')
# car ramp context
shape(Polygon([(0, yr(0)), (xb(37000), yr(xb(37000))), (Z2[0], Z2[1]), (0, V['Z1_NW'][1])]), fill='#d9d4cb')
text(4800, 38150, 'DRIVEWAY 8% → PARKING', 2.0, '#8a8178', weight=600, extra='letter-spacing=".4"')
# street
svg.append(f'<rect x="{P(15000, 0)[0]:.2f}" y="{PY0 - 2:.2f}" width="{P(18700, 0)[0] - P(15000, 0)[0]:.2f}" height="{P(0, -3000)[1] - PY0 + 2:.2f}" fill="#cfd6db"/>')
mx, my = P(17900, 20000); text(mx, my, 'VÕ NGUYÊN GIÁP 15M  ·  → SEA', 3.0, '#5d6a74', weight=700, page=True, extra=f'transform="rotate(-90 {mx:.2f} {my:.2f})" letter-spacing=".8"')
# floor
shape(FLOOR, fill='url(#girih)')
shape(planter, fill='url(#plants)', stroke='#5f8a44', sw=.2)
shape(PLAT, fill='url(#deck)', stroke='#7a5230', sw=.3)
shape(ALLEY, fill='url(#paving)'); shape(PLAZA, fill='url(#paving)')
shape(KIDS, fill='url(#soft)', stroke='#d59a1f', sw=.35, extra='stroke-dasharray="1 .6"')
shape(PHOTO, fill='#f3dfe4', extra='opacity=".75"')
shape(CORR, fill='#efe4d2', stroke='#d9731a', sw=.15, extra='stroke-dasharray=".8 .6" opacity=".9"')
shape(SS, fill='#e3d8c6', stroke='#8a7f70', sw=.2)
shape(VIEW, fill='#f1d7c0')
# steps + ramp + rail
for st, horiz in ((STEPS_A, False), (STEPS_B, False)):
    shape(st, fill='#d8c9ae', stroke='#7a5230', sw=.2)
    x0, y0, x1, y1 = st.bounds
    for k in (1, 2): line((x0 + k * 300, y0), (x0 + k * 300, y1), '#7a5230', .15)
shape(RAMP, fill='#cdb795', stroke='#7a5230', sw=.25)
for k in range(1, 12): line((0, 30900 + k * 470), (1300, 30900 + k * 470), '#a68b66', .08)
svg.append(f'<line x1="{P(650, 31300)[0]:.2f}" y1="{P(650, 31300)[1]:.2f}" x2="{P(650, 36200)[0]:.2f}" y2="{P(650, 36200)[1]:.2f}" stroke="#5A3A22" stroke-width=".3" marker-end="url(#arrS)"/>')
for a, b in RAIL: line(a, b, '#3b2a1e', .45)
# doors
for k, (a, b, op) in DOORS.items():
    line((-60, a), (-60, b), '#2A9DA8' if op else '#9a9a9a', .9)
    if not op: text(-1500, (a + b) / 2, 'closed', 1.6, '#8a7f70', extra=f'transform="rotate(-90 {P(-1500, (a + b) / 2)[0]:.2f} {P(-1500, (a + b) / 2)[1]:.2f})"')
# furniture & objects
FILL = {'table': '#a87444', 'chair': '#ead9bd', 'bench': 'url(#ikat)', 'rug': '#f3e3c6', 'screen': 'url(#lattice)', 'tapchan': '#b88a58', 'tapchan_rug': 'url(#suzani)',
        'tapchan_table': '#6b4429', 'stool': '#8a5a36', 'hightable': '#a87444', 'station': '#2A9DA8', 'host': '#2A9DA8', 'bench_wait': 'url(#ikat)',
        'backbar': '#5A3A22', 'barcounter': '#A4482B', 'bartop': '#efe6d8', 'shelving': 'url(#lattice)', 'counter': '#c9ccd0', 'screenwall': '#5A3A22',
        'bbq_floor': 'url(#slate)', 'firewall': '#A4482B', 'tandoor_block': '#c98b62', 'tandoor': '#7a3d22', 'mangal': '#3a3a3a', 'kazan_block': '#9a9590', 'kazan': '#1d1d1d',
        'sinkbins': '#c9ccd0', 'prep': '#d7dadd', 'pass': '#e6e8ea', 'glass': '#bfe0ea', 'backdrop': 'url(#majolica)', 'rosette': 'url(#majolica)', 'play': '#f6a96b', 'play2': '#7fc3d4', 'play3': '#9bd27f',
        'treepit': '#6b5a48', 'ringbench': '#8a5a36', 'hauz_border': 'url(#majolica)', 'hauz': 'url(#water)', 'lantern': 'url(#glow)'}
SHADOW = {'table', 'tapchan', 'bench', 'backbar', 'barcounter', 'shelving', 'counter', 'tandoor_block', 'kazan_block', 'mangal', 'ringbench', 'screen', 'hightable', 'backdrop', 'play', 'play2', 'play3'}
ORDER = ['bbq_floor', 'rug', 'tapchan', 'tapchan_rug', 'hauz_border', 'hauz', 'rosette', 'treepit', 'ringbench', 'chair', 'table', 'bench', 'screen', 'tapchan_table', 'stool', 'hightable',
         'station', 'host', 'bench_wait', 'backbar', 'barcounter', 'bartop', 'shelving', 'counter', 'screenwall', 'firewall', 'tandoor_block', 'tandoor', 'mangal', 'kazan_block', 'kazan',
         'sinkbins', 'prep', 'pass', 'glass', 'backdrop', 'play', 'play2', 'play3', 'lantern']
for k in ORDER:
    for it in items:
        if it['kind'] != k: continue
        shape(it['geom'], fill=FILL.get(k, '#ccc'), stroke='#3b2a1e' if k not in ('lantern', 'rug', 'bbq_floor', 'hauz', 'glass') else 'none', sw=.12, extra='filter="url(#sh)"' if k in SHADOW else '')
# mangal embers + tandoor/kazan details
mg = [it for it in items if it['kind'] == 'mangal'][0]['geom']
for f in (.15, .35, .55, .75):
    a = opt(P0, 1500 + 2400 * f - 100, 300); b = opt(P0, 1500 + 2400 * f + 100, 600); line(a, b, '#e8562a', .5)
for it in items:
    if it['kind'] in ('tandoor', 'kazan'):
        c = it['geom'].centroid; svg.append(f'<circle cx="{P(c.x, c.y)[0]:.2f}" cy="{P(c.x, c.y)[1]:.2f}" r="{(1.8 if it["kind"] == "tandoor" else 2.1):.2f}" fill="none" stroke="#b8893a" stroke-width=".35"/>')
hd = [it for it in items if it['kind'] == 'hood'][0]['geom']; shape(hd, stroke='#8E1F24', sw=.3, extra='stroke-dasharray="1.2 .8"')
# roof: trusses, columns, oculi (light, on top)
for yy in TRUSS_Y: line((0, yy), (xb(yy) - 750, yy), '#5A3A22', .12, 'stroke-dasharray="2 1.2" opacity=".55"')
for c in cols: shape(R(c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150), fill='#3b2a1e')
# trees: canopy above everything, translucent
for c, r in ((TREE_N, 3800), (TREE_S, 3600)):
    cx, cy = P(*c); rr = r / S
    svg.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rr:.2f}" fill="url(#canopy)" stroke="#4e7d36" stroke-width=".25" opacity=".55"/>')
    for a in range(0, 360, 30):
        svg.append(f'<circle cx="{cx + rr * .62 * math.cos(math.radians(a)):.2f}" cy="{cy + rr * .62 * math.sin(math.radians(a)):.2f}" r="{rr * .32:.2f}" fill="#7fae55" opacity=".22"/>')
    svg.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{1400 / S:.2f}" fill="none" stroke="#5A3A22" stroke-width=".2" stroke-dasharray="1 .7"/>')
    svg.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{350 / S:.2f}" fill="#5a4636"/>')
# flows: entrances (green), staff (orange)
def arrow(pts_, color, sw, marker, dash=''):
    d = 'M' + ' L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in pts_)
    svg.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#{marker})" {dash}/>')
arrow([(xb(15800) + 2600, 15800), (xb(15800) - 400, 15800), (8200, 17900), (3700, 17900)], '#2e7d3a', .7, 'arr')
arrow([(5200, 39200), (6700, 36600), (7600, 33000)], '#2e7d3a', .7, 'arr')
arrow([(-600, 25000), (2000, 25050), (3700, 25050), (6900, 24900)], '#d9731a', .4, 'arrS', 'stroke-dasharray="1 .8"')
arrow([(1000, 7000), (1000, 5000), (2500, 5250), (7900, 5250), (opt(P0, 450, 3300)[0], opt(P0, 450, 3300)[1])], '#d9731a', .4, 'arrS', 'stroke-dasharray="1 .8"')

# numbers on the plan
NUM = [(1, (10200, 15900)), (2, (5400, 18850)), (3, (1150, 18000)), (4, opt(P_B, 7000, 700)), (5, (4300, 25950)), (6, (2950, 32400)), (7, (2700, 37400)),
       (8, (3350, 13600)), (9, (1000, 4600)), (10, (6000, 8250)), (11, (6000, 10650)), (12, (opt(P0, 3000, 1800)[0], opt(P0, 3000, 1800)[1])), (13, (3500, 2000)), (14, (-3600, 2200)), (15, (5350, 22500))]
for n, (x, y) in NUM: num(x, y, n)
LEG = [(1, 'East entrance & host', 'street stair, plaza under the chinar'), (2, 'Alley', 'patterned paving to the hall doors'),
       (3, 'Raised aivan platform ±0.000', 'filled steps + extension, 3 tables, rail'), (4, 'Sea-view booths', '8 enclosed booths, carved screens, lanterns'),
       (5, 'Chinar court north', 'tree kept, bench around it, roof oculus'), (6, 'Lyabi-Hauz tapchan court', '4 hybrid tapchans around a fountain'),
       (7, 'North entrance + ramp 1:12', 'from parking, step-free to the hall'), (8, 'Bar', 'tea, samovar, coffee · 10 stools'),
       (9, 'Staff service station', 'shelving, POS, water, ice, dish drop'), (10, 'Dining south', '4 tables for 4'), (11, 'Chinar court south', 'tree kept, round bench'),
       (12, 'Mangal kitchen', 'tandoor · mangal · kazan · prep · pass'), (13, 'Photo zone', 'majolica pishtaq + floor rosette'), (14, 'Kids zone', 'fenced, soft floor, play'),
       (15, 'Dining north', '5 tables for 4')]

# scale bar + north
sx, sy_ = 14, 352
for k in range(5):
    svg.append(f'<rect x="{sx + k * 1000 / S:.2f}" y="{sy_}" width="{1000 / S:.2f}" height="1.2" fill="{"#3b2a1e" if k % 2 == 0 else "#f7f1e6"}" stroke="#3b2a1e" stroke-width=".15"/>')
text(sx, sy_ + 4.2, '0', 2.0, page=True, anchor='start'); text(sx + 5000 / S, sy_ + 4.2, '5 m', 2.0, page=True)
text(sx + 5000 / S + 4, sy_ + 1.2, 'Scale 1:150 @ A3', 2.0, '#6b5a48', anchor='start', page=True)
nx, ny = 150, 352
svg.append(f'<path d="M{nx} {ny - 6}L{nx - 2.4} {ny + 2}L{nx} {ny + .6}L{nx + 2.4} {ny + 2}Z" fill="#3b2a1e"/>'); text(nx, ny - 7.5, 'N', 2.8, page=True, weight=700)

# title
text(14, 26, 'SAMARKAND', 15, '#3b2a1e', anchor='start', family='Bitstream Charter', weight=700, page=True, extra='letter-spacing="2.5"')
text(14, 34.5, 'Covered terrace  ·  Layout R2  ·  presentation plan', 5.0, '#8E1F24', anchor='start', family='Bitstream Charter', page=True)
text(14, 41, 'Tajik & Uzbek national cuisine  ·  254 Võ Nguyên Giáp, Đà Nẵng', 3.0, '#6b5a48', anchor='start', page=True)
svg.append(f'<rect x="14" y="45" width="{W - 28}" height="1.6" fill="url(#majolica)"/>')
# legend column
lx, ly = 203, 64
text(lx, ly, 'ZONES', 3.0, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".6"')
for i, (n, t1, t2) in enumerate(LEG):
    yy = ly + 6 + i * 7.1
    num(lx + 2.3, yy - .9, n, page=True)
    text(lx + 6, yy - .5, t1, 2.5, '#3b2a1e', anchor='start', weight=600, page=True)
    text(lx + 6, yy + 2.4, t2, 2.0, '#6b5a48', anchor='start', page=True)
sy0 = ly + 6 + len(LEG) * 7.1 + 4
text(lx, sy0, 'SEATS', 3.0, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".6"')
for i, (k, v) in enumerate(seats.items()):
    text(lx, sy0 + 5 + i * 4.2, k, 2.3, '#3b2a1e', anchor='start', page=True); text(W - 14, sy0 + 5 + i * 4.2, str(v), 2.3, '#3b2a1e', anchor='end', weight=600, page=True)
yt = sy0 + 5 + len(seats) * 4.2 + 1
svg.append(f'<line x1="{lx}" y1="{yt - 2.6}" x2="{W - 14}" y2="{yt - 2.6}" stroke="#3b2a1e" stroke-width=".2"/>')
text(lx, yt + .6, 'Total', 2.8, '#8E1F24', anchor='start', weight=700, page=True); text(W - 14, yt + .6, str(total), 3.2, '#8E1F24', anchor='end', weight=700, page=True)
# key
ky = yt + 9
text(lx, ky, 'KEY', 3.0, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".6"')
KEYS = [('#3b2a1e', 'sq', 'Roof column (steel, wood-clad)'), ('#5A3A22', 'dash', 'Roof truss line'), ('#2e7d3a', 'arr', 'Guest entrance'),
        ('#d9731a', 'dot', 'Staff route'), ('#2A9DA8', 'door', 'Hall door, open'), ('#9a9a9a', 'door', 'Hall door, closed'), ('#8E1F24', 'dash', 'Exhaust hood')]
for i, (c, kind, t) in enumerate(KEYS):
    yy = ky + 4.5 + i * 4.2
    if kind == 'sq': svg.append(f'<rect x="{lx}" y="{yy - 2}" width="2" height="2" fill="{c}"/>')
    elif kind == 'arr': svg.append(f'<line x1="{lx}" y1="{yy - 1}" x2="{lx + 5}" y2="{yy - 1}" stroke="{c}" stroke-width=".7" marker-end="url(#arr)"/>')
    elif kind == 'door': svg.append(f'<line x1="{lx}" y1="{yy - 1}" x2="{lx + 5}" y2="{yy - 1}" stroke="{c}" stroke-width=".9"/>')
    else: svg.append(f'<line x1="{lx}" y1="{yy - 1}" x2="{lx + 5}" y2="{yy - 1}" stroke="{c}" stroke-width=".4" stroke-dasharray="{"1 .8" if kind == "dot" else "1.6 .9"}"/>')
    text(lx + 7, yy - .2, t, 2.2, '#3b2a1e', anchor='start', page=True)

# BBQ detail inset (1:50)
IS = 50.0; ix0, iy0 = 203, 276
text(ix0, iy0 - 4, 'MANGAL KITCHEN  ·  1:100', 3.0, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".5"')
IS = 100.0
bx0, by0, bx1, by1 = BBQ.union(VIEW).bounds
def Pi(x, y): return (ix0 + (x - bx0) / IS, iy0 + 2 + (by1 - y) / IS)
def ishape(g, fill, stroke='#3b2a1e', sw=.15, extra=''):
    for p in getattr(g, 'geoms', [g]):
        d = 'M' + ' L'.join(f'{Pi(x, y)[0]:.2f},{Pi(x, y)[1]:.2f}' for x, y in p.exterior.coords) + 'Z'
        svg.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
ishape(VIEW, '#f1d7c0', 'none'); ishape(BBQ, 'url(#slate)', '#3b2a1e', .2)
for k in ('firewall', 'tandoor_block', 'tandoor', 'mangal', 'kazan_block', 'kazan', 'sinkbins', 'prep', 'pass', 'glass'):
    for it in items:
        if it['kind'] == k: ishape(it['geom'], FILL[k], '#3b2a1e', .15)
ishape(hd, 'none', '#8E1F24', .3, 'stroke-dasharray="1.2 .8"')
LBL = [('sinkbins', 'Hand sink, charcoal, ash'), ('kazan', 'Kazan Ø800, gas (plov)'), ('pass', 'Pass, heat lamps, bread'), ('mangal', 'Mangal 2.4 m, charcoal'),
       ('prep', 'Cold prep, fridges, sink'), ('firewall', 'Brick fire wall'), ('tandoor', 'Tandoor Ø900')]
ex = ix0 + (bx1 - bx0) / IS + 3
for i, (k, t) in enumerate(LBL):
    g = [it for it in items if it['kind'] == k][0]['geom']; c = g.centroid; cx, cy = Pi(c.x, c.y)
    ty = iy0 + 6 + i * 8.2
    svg.append(f'<path d="M{cx:.2f} {cy:.2f}L{ex - 1:.2f} {ty - .8:.2f}" stroke="#8a7f70" stroke-width=".15" fill="none"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r=".45" fill="#8E1F24"/>')
    text(ex, ty, t, 1.9, '#3b2a1e', anchor='start', page=True)
text(ix0, iy0 + 73, 'Cook aisle 1.1–1.6 m · hood + stack above the roof', 1.9, '#6b5a48', anchor='start', page=True)
text(ix0, iy0 + 76.2, 'Extinguisher + blanket · gas shut-off · floor drain', 1.9, '#6b5a48', anchor='start', page=True)
text(ix0, iy0 + 79.4, 'Glass screen to guests · non-slip slate floor', 1.9, '#6b5a48', anchor='start', page=True)

# footer notes
fy = 372
NOTES = ['Base: as-built DWG (Long House, 10-07-2024), measured 1:1. Origin = axis 6 × axis A\'. Terrace floor −0.470, platform and hall ±0.000.',
         'Roof: steel trusses on the building grid, supported by columns hidden in the street planters and a ledger on the façade columns (engineer to confirm).',
         'No columns inside the dining. Two trees are kept and grow through roof oculi Ø2.8. The driveway ramp and street planters are kept.',
         'Booths face the sea over the planter. Carved panjara screens h 2.1 m, lanterns over each table, suzani and ikat textiles.',
         'One D–E door stays closed (tables in front). The D–E north door and the back door by the lift open onto the platform.']
for i, t in enumerate(NOTES): text(14, fy + i * 4.3, t, 2.15, '#4b3a2e', anchor='start', page=True)
svg.append(f'<rect x="14" y="{H - 22}" width="{W - 28}" height="1.2" fill="url(#majolica)"/>')
text(14, H - 14.5, 'SAMARKAND  ·  Layout R2  ·  2026-10-22', 2.4, '#3b2a1e', anchor='start', weight=600, page=True)
text(W - 14, H - 14.5, 'Concept for client review  ·  dimensions to verify on site', 2.4, '#6b5a48', anchor='end', page=True)

open(f'{OUT}/samarkand-terrace-layout-R2.svg', 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">{DEFS}{"".join(svg)}</svg>')
print('svg ok')
