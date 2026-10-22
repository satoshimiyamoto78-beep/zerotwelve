"""Samarkand terrace — layout R1 on the precise base plan (local mm, origin axis 6 x axis A').
Produces: layout JSON, A3 sheet (PDF/PNG) and DXF = base drawing + SMK-L-* layers.
"""
import sys, json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union, split
import ezdxf
from ezdxf.enums import TextEntityAlignment

Z = json.load(open(sys.argv[1])); BASE_DXF = sys.argv[2]; OUT = sys.argv[3]
L = Z['layers']; V = Z['zone_vertices']

# ---------------- site lines ----------------
Z2, Z3 = V['Z2_NE'], V['Z3_SE']
SLOPE = (Z3[0] - Z2[0]) / (Z2[1] - Z3[1])          # x decreases northwards
def xb(y): return Z3[0] - (y - Z3[1]) * SLOPE      # east boundary
PL_W = 1500                                         # existing planter width
def xi(y): return xb(y) - PL_W                      # planter inner face
def yr(x): return 37090.5 - 0.06542 * (x - 83.6)    # car-ramp south edge
def ys(x): return Z3[1] * (x - V['Z4_S'][0]) / (Z3[0] - V['Z4_S'][0])  # south edge
TH = math.atan(SLOPE)
D_N = (-math.sin(TH), math.cos(TH))                 # along planter, northwards
N_W = (-math.cos(TH), -math.sin(TH))                # away from planter, westwards

zone = Polygon(Z['zone'])
ramp_cut = LineString([(-20000, yr(-20000)), (30000, yr(30000))])
U = sorted(split(zone, ramp_cut).geoms, key=lambda g: g.centroid.y)[0]   # usable (car ramp kept)
STAIR = (13300, 18300)                               # existing street stair between planters
planter = Polygon([(xi(0), 0), (xb(0), 0), (xb(40000), 40000), (xi(40000), 40000)]).intersection(U)
stair_gap = Polygon([(xi(STAIR[0]) - 50, STAIR[0]), (xb(STAIR[0]) + 50, STAIR[0]), (xb(STAIR[1]) + 50, STAIR[1]), (xi(STAIR[1]) - 50, STAIR[1])])
planter = planter.difference(stair_gap)
FLOOR = U.difference(planter)

# ---------------- helpers ----------------
items = []     # dicts: kind, layer, poly(list), label
def add(kind, layer, poly, **kw):
    p = poly if isinstance(poly, Polygon) else Polygon(poly)
    items.append(dict(kind=kind, layer=layer, poly=[(round(x, 1), round(y, 1)) for x, y in p.exterior.coords], **kw)); return p
def R(x0, y0, x1, y1): return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
def obl(p0, s0, s1, t0, t1):  # rectangle in planter-aligned frame: s along planter (north), t away from it (west)
    pts = []
    for s, t in ((s0, t0), (s1, t0), (s1, t1), (s0, t1)):
        pts.append((p0[0] + D_N[0] * s + N_W[0] * t, p0[1] + D_N[1] * s + N_W[1] * t))
    return Polygon(pts)
def circ(cx, cy, r): return Point(cx, cy).buffer(r, 32)
def table4(cx, cy, tw=1200, td=800, layer='SMK-L-FURN'):
    add('table', layer, R(cx - tw / 2, cy - td / 2, cx + tw / 2, cy + td / 2), seats=4)
    for sx in (-tw / 4, tw / 4):
        for sy in (-1, 1):
            y0 = cy + sy * (td / 2 + 50); y1 = y0 + sy * 450
            add('chair', layer, R(cx + sx - 225, y0, cx + sx + 225, y1))
    return R(cx - tw / 2, cy - td / 2 - 500, cx + tw / 2, cy + td / 2 + 500)

seats = {}
def count(k, n): seats[k] = seats.get(k, 0) + n

# ---------------- zones (areas) ----------------
zones = {}
KIDS = Polygon([V['Z5_pocketSW'], V['Z4_S'], V['Z7_bldgSE'], V['Z6_pocketNW']])
zones['Kids zone'] = KIDS
ALLEY = R(1300, 16300, 6300, 19700)
PLAZA = Polygon([(6300, 12800), (xi(12800), 12800), (xi(STAIR[0]), STAIR[0]), (xb(STAIR[0]), STAIR[0]), (xb(STAIR[1]), STAIR[1]), (xi(STAIR[1]), STAIR[1]), (xi(19700), 19700), (6300, 19700)]).intersection(U)
zones['East entrance plaza'] = PLAZA
zones['Alley'] = ALLEY

# ---------------- BAR on the facade (under the F2 balcony) ----------------
BAR_Y0, BAR_Y1 = 8600, 15200
add('backbar', 'SMK-L-BAR', R(0, BAR_Y0, 550, BAR_Y1), label='Back bar: tea / samovar, coffee,\nsinks, ice, u/c fridges · h 900 + display')
add('barcounter', 'SMK-L-BAR', R(1500, BAR_Y0, 2100, BAR_Y1))
add('bartop', 'SMK-L-BAR', R(2100, BAR_Y0, 2400, BAR_Y1))
add('pickup', 'SMK-L-BAR', R(1500, BAR_Y0 - 700, 2400, BAR_Y0), label='Waiter pick-up')
n_st = 0; y = BAR_Y0 + 450
while y + 225 <= BAR_Y1 - 150:
    add('stool', 'SMK-L-FURN', circ(2750, y, 200)); n_st += 1; y += 620
count('Bar counter', n_st)
zones['Bar (incl. stools)'] = R(0, BAR_Y0 - 700, 3000, BAR_Y1)

# ---------------- BBQ / outdoor kitchen, SE corner, along the planter ----------------
P0 = (xi(3600), 3600)
BBQ = obl(P0, 0, 5900, 0, 2550)
zones['BBQ / outdoor kitchen'] = BBQ
add('hotline', 'SMK-L-BBQ', obl(P0, 0, 5200, 0, 750))
add('equip', 'SMK-L-BBQ', obl(P0, 1500, 3900, 80, 700), label='Mangal 2.4 m')
tp = obl(P0, 300, 1100, 40, 800).centroid; add('equip', 'SMK-L-BBQ', circ(tp.x, tp.y, 400), label='Tandoor Ø800')
kp = obl(P0, 4350, 5110, 40, 800).centroid; add('equip', 'SMK-L-BBQ', circ(kp.x, kp.y, 380), label='Kazan (plov)')
add('prep', 'SMK-L-BBQ', obl(P0, 5200, 5900, 750, 2550), label='Prep · sink · fridges')
add('pass', 'SMK-L-BBQ', obl(P0, 1000, 5900, 1850, 2550), label='Show counter / pass')
add('hood', 'SMK-L-ROOF', obl(P0, -100, 5300, -100, 1050))
VIEW = obl(P0, 0, 5900, 2550, 3550)
zones['BBQ viewing / queue'] = VIEW

# ---------------- PHOTO ZONE on the south edge ----------------
ang_s = math.atan2(Z3[1], Z3[0] - V['Z4_S'][0])
def on_south(x, off):  # point on south edge at x, offset north (perpendicular)
    y = ys(x); return (x - math.sin(ang_s) * off, y + math.cos(ang_s) * off)
a, b = on_south(1300, 250), on_south(5700, 250)
c_, d_ = on_south(5700, 650), on_south(1300, 650)
add('backdrop', 'SMK-L-PHOTO', Polygon([a, b, c_, d_]), label='Pishtaq backdrop 4.4 × h 3.2 m\n(majolica frame, lit arch)')
mid = on_south(3500, 2700)
add('rosette', 'SMK-L-PHOTO', circ(mid[0], mid[1], 1000), label='Floor rosette Ø2.0')
PHOTO = Polygon([on_south(1100, 0), on_south(6200, 0), (6200 - 200, 5000), (1100, 5000)]).intersection(FLOOR)
zones['Photo zone'] = PHOTO

# ---------------- KIDS ----------------
add('fence', 'SMK-L-KIDS', Polygon([(-80, 40), (0, 40), (0, 1500), (-80, 1500)]))
add('fence', 'SMK-L-KIDS', Polygon([(-80, 2500), (0, 2500), (0, 4060), (-80, 4060)]))
add('play', 'SMK-L-KIDS', R(-6900, 300, -3900, 1900), label='Soft play / climbing')
add('play', 'SMK-L-KIDS', R(-3500, 2700, -800, 3800), label='Low table + chalk wall')

# ---------------- DINING ----------------
fp_tables = []
# south block (between bar and BBQ)
for yy in (6300, 8800, 11300, 13800):
    for xx in (5000, 7200):
        fp_tables.append(table4(xx, yy)); count('South dining 4-tops', 4)
# north-west block (west of the main aisle)
for yy in (21600, 24100, 26600, 29100):
    for xx in (3150, 5350):
        fp_tables.append(table4(xx, yy)); count('North dining 4-tops', 4)
# tapchan (hybrid, seat 450 / table 700) under the entrance canopy
for (x0, x1) in ((2600, 4300), (4450, 6150)):
    for (y0, y1) in ((31300, 33300), (34100, 36100)):
        add('tapchan', 'SMK-L-FURN', R(x0, y0, x1, y1))
        add('tapchan_table', 'SMK-L-FURN', R(x0 + 450, y0 + 500, x1 - 450, y1 - 500))
        count('Tapchans (hybrid, 6 pax)', 6)
add('screen', 'SMK-L-FURN', R(4300, 31300, 4450, 36100), label='Panjara screen')
# east banquette along the planter, 2-tops
BQ_Y0, BQ_Y1 = 20300, 31000
pb = (xi(BQ_Y0), BQ_Y0); slen = (BQ_Y1 - BQ_Y0) / math.cos(TH)
add('banquette', 'SMK-L-FURN', obl(pb, 0, slen, 0, 550), label='Banquette, ikat upholstery')
s = 300
while s + 700 <= slen - 200:
    add('table', 'SMK-L-FURN', obl(pb, s, s + 700, 600, 1300), seats=2)
    add('chair', 'SMK-L-FURN', obl(pb, s + 125, s + 575, 1350, 1800))
    count('Banquette 2-tops', 2); s += 1500

# ---------------- service points ----------------
add('station', 'SMK-L-SERV', R(0, 21400, 700, 22400), label='W1 waiter station\n(POS, cutlery, water)')
add('station', 'SMK-L-SERV', obl((xi(32300), 32300), 0, 1100, 0, 600), label='W2 station')
add('host', 'SMK-L-SERV', R(8700, 18900, 9400, 19400), label='Host')
add('bench', 'SMK-L-SERV', obl((xi(18700), 18700), 0, 1100, 0, 450), label='Waiting bench')

# ---------------- roof structure ----------------
cols = []
MID_X = 6300
for yy in (4100, 9850, 15600, 21350, 27100, 32100, 36300):
    cols.append((MID_X, yy))
for yy in (3700, 9850, 13000, 18600, 22850, 27100, 32100, 36000):
    cols.append((xb(yy) - 750, yy))
cols += [(-7050, 200), (-350, 250), (1700, 36700)]
for c in cols:
    add('column', 'SMK-L-ROOF', R(c[0] - 125, c[1] - 125, c[0] + 125, c[1] + 125))
ROOF = U.buffer(-150, join_style=2)
add('roof', 'SMK-L-ROOF', ROOF)

# ---------------- checks ----------------
keepout = {
    'wheelchair ramp': R(0, 26200, 2450, 36950),
    'entrance steps C-D': R(0, 16550, 1300, 21250),
    'door swing D-E': R(0, 22545, 1500, 25905),
    'planter': planter,
}
problems = []
col_polys = [R(c[0] - 125, c[1] - 125, c[0] + 125, c[1] + 125) for c in cols]
for it in items:
    if it['kind'] in ('roof', 'hood', 'column', 'fence'): continue
    p = Polygon(it['poly'])
    if not FLOOR.buffer(5).contains(p):
        problems.append(f"{it['kind']} outside usable floor @ {p.centroid.x:.0f},{p.centroid.y:.0f}")
    for k, kp_ in keepout.items():
        if it['kind'] not in ('station',) and p.intersection(kp_).area > 1000:
            problems.append(f"{it['kind']} hits {k} @ {p.centroid.x:.0f},{p.centroid.y:.0f}")
    for cp in col_polys:
        if p.intersects(cp) and it['kind'] not in ('hotline', 'pass', 'prep', 'equip', 'banquette'):
            problems.append(f"{it['kind']} hits column @ {p.centroid.x:.0f},{p.centroid.y:.0f}")
# clear widths
clear = {
    'Main N–S aisle (x 6300–7500)': 1200,
    'Behind bar stools to south dining': round(4400 - 2950),
    'Bartender aisle': 950,
    'BBQ staff aisle': 1100,
    'Alley': 3400,
    'Gap between table blocks (chairs back-to-back)': 2500 - 1900,
    'Door D–E clear zone to first table': 2550,
}
zone_areas = {k: round(v.area / 1e6, 1) for k, v in zones.items()}
total = sum(seats.values())
res = dict(seats=seats, total_seats=total, zone_areas=zone_areas, usable_area=round(U.area / 1e6, 1), floor_area=round(FLOOR.area / 1e6, 1),
           planter_area=round(planter.area / 1e6, 1), clear_widths=clear, problems=problems, columns=cols)
json.dump(dict(res, items=items), open(f'{OUT}/samarkand-terrace-layout-R1.json', 'w'), ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))

# ================= drawing =================
SCALE = 200; PAPER = (297, 420)
WX0, WX1 = -16200, 25200; WY0, WY1 = -8200, 47600
fig = plt.figure(figsize=(PAPER[0] / 25.4, PAPER[1] / 25.4), dpi=100)
ax = fig.add_axes([12 / PAPER[0], 72 / PAPER[1], (WX1 - WX0) / SCALE / PAPER[0], (WY1 - WY0) / SCALE / PAPER[1]])
ax.set_xlim(WX0, WX1); ax.set_ylim(WY0, WY1); ax.set_aspect('equal'); ax.axis('off')
pt = lambda mm: mm * 72 / 25.4
TXT = dict(family='DejaVu Sans')
def poly(p, fc='none', ec='#222', lw=.25, ls='-', z=4, alpha=1):
    if hasattr(p, 'geoms'):
        for g in p.geoms: poly(g, fc, ec, lw, ls, z, alpha)
        return
    if isinstance(p, Polygon) and p.is_empty: return
    ax.add_patch(MPoly(list(p.exterior.coords) if isinstance(p, Polygon) else p, closed=True, fc=fc, ec=ec, lw=pt(lw), ls=ls, zorder=z, alpha=alpha))
def txt(x, y, s, fs=5, c='#222', ha='center', w='normal', rot=0, z=12, box_=False):
    kw = dict(fontsize=fs, color=c, ha=ha, va='center', weight=w, rotation=rot, zorder=z, **TXT)
    if box_: kw['bbox'] = dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=.85)
    ax.text(x, y, s, **kw)

# base context (light)
ax.add_patch(MPoly([(WX0, 4100), (0, 4100), (0, 37100), (WX0, 37100)], closed=True, fc='#ebe8e3', ec='none', zorder=0))
txt(-7200, 20600, 'EXISTING BUILDING · MAIN HALL ±0.000', fs=6.5, c='#7a7a7a', rot=90)
lot = L['LOT'][0]; ax.plot(*zip(*lot), color='#d23c2c', lw=pt(.45), ls=(0, (10, 3, 2, 3)), zorder=3)
for lay, col, lw in (('BLDG', '#555', .35), ('GLAZ', '#7d9cc4', .2), ('DOOR', '#777', .2), ('STEPS', '#8b6b4a', .3), ('CONTEXT', '#b5b5b5', .3)):
    for p in L[lay]: ax.plot(*zip(*p), color=col, lw=pt(lw), zorder=2)
for p in L['EXIST']:  # keep only the ramp + planters visually (others are removed in the redesign)
    xs_ = [q[0] for q in p]
    if max(xs_) < 2600 or min(xs_) > 8000 and len(p) < 10: ax.plot(*zip(*p), color='#8b6b4a', lw=pt(.3), zorder=2)
for p in L['ABOVE']: ax.plot(*zip(*p), color='#2f5fb3', lw=pt(.4), ls=(0, (5, 3)), zorder=6)
for n, (o, v) in Z['grid'].items():
    if o == 'h':
        ax.plot([-14100, 15500], [v, v], color='#a0a0a0', lw=pt(.15), ls=(0, (12, 3, 2, 3)), zorder=1)
        ax.add_patch(Circle((-14800, v), 650, fc='white', ec='#999', lw=pt(.25), zorder=3)); txt(-14800, v, n, fs=6.2, c='#333')
    else:
        ax.plot([v, v], [-5600, 44200], color='#a0a0a0', lw=pt(.15), ls=(0, (12, 3, 2, 3)), zorder=1)
        ax.add_patch(Circle((v, -6300), 650, fc='white', ec='#999', lw=pt(.25), zorder=3)); txt(v, -6300, n, fs=6.2, c='#333')

# floor zones
poly(FLOOR, fc='#f6efe2', ec='none', z=1)
poly(planter, fc='#cfe3c0', ec='#6f8f55', lw=.3, z=2)
ZC = {'Kids zone': '#ffe08a', 'Photo zone': '#f4c6d6', 'BBQ / outdoor kitchen': '#f2b48a', 'BBQ viewing / queue': '#fbe2cf',
      'Bar (incl. stools)': '#e9cfa6', 'Alley': '#d9cfbf', 'East entrance plaza': '#e6dccd'}
for k, p in zones.items(): poly(p, fc=ZC[k], ec='none', z=2, alpha=.9)
# alley paving pattern (girih band)
for xx in range(1700, 6200, 900):
    ax.add_patch(MPoly([(xx, 18000), (xx + 350, 18350), (xx, 18700), (xx - 350, 18350)], closed=True, fc='none', ec='#a08a6a', lw=pt(.2), zorder=3))
    ax.add_patch(MPoly([(xx, 17300), (xx + 350, 17650), (xx, 18000), (xx - 350, 17650)], closed=True, fc='none', ec='#a08a6a', lw=pt(.2), zorder=3))
# roof
poly(ROOF, fc='none', ec='#5a3a22', lw=.35, ls=(0, (2, 2)), z=5)
STY = {'SMK-L-FURN': ('#ffffff', '#3b2a1e', .3), 'SMK-L-BAR': ('#c9a27e', '#3b2a1e', .35), 'SMK-L-BBQ': ('#e9e2d6', '#3b2a1e', .35),
       'SMK-L-PHOTO': ('#1f3f8a', '#1f3f8a', .3), 'SMK-L-KIDS': ('#ffffff', '#b08a1e', .3), 'SMK-L-SERV': ('#2a9da8', '#1d6f77', .3), 'SMK-L-ROOF': ('#5a3a22', '#5a3a22', .3)}
for it in items:
    k = it['kind']; fc, ec, lw = STY[it['layer']]
    if k == 'roof': continue
    if k == 'hood': poly(it['poly'], fc='none', ec='#8E1F24', lw=.35, ls=(0, (4, 2)), z=7); continue
    if k == 'tapchan': fc = '#e7c79a'
    if k == 'tapchan_table': fc = '#8a5a36'
    if k == 'banquette': fc = '#8E1F24'
    if k == 'rosette': fc = '#f6efe2'
    if k in ('play',): fc = '#fff4c8'
    if k == 'equip': fc = '#555' if 'Mangal' in it.get('label', '') else '#A4482B'
    if k == 'hotline': fc = '#9a9a9a'
    if k == 'screen': fc = '#5a3a22'
    poly(it['poly'], fc=fc, ec=ec, lw=lw, z=8 if k != 'column' else 9)

# flows
def flow(pts, c, ls):
    xs_, ys_ = zip(*pts)
    ax.plot(xs_, ys_, color=c, lw=pt(.6), ls=ls, zorder=10, solid_capstyle='round')
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ax.annotate('', xy=(x2, y2), xytext=(x1 + (x2 - x1) * .8, y1 + (y2 - y1) * .8), arrowprops=dict(arrowstyle='-|>', color=c, lw=pt(.6), mutation_scale=7), zorder=10)
G_C, S_C = '#2e9e44', '#e07a16'
flow([(xb(15800) + 1200, 15800), (xi(15800) - 300, 15900), (6600, 17500), (1500, 18000)], G_C, '-')
flow([(4000, 37300), (6900, 36200), (6900, 20200)], G_C, '-')
flow([(-300, 24200), (900, 23500), (900, 22000), (3500, 20100), (6800, 15200), (8200, 11000), (8500, 7400)], S_C, (0, (3, 2)))
flow([(-300, 18900), (900, 16000), (1100, 15500)], S_C, (0, (3, 2)))

# labels
txt(-3600, 2100, 'KIDS ZONE', fs=6.2, w='bold', c='#7a5a00'); txt(-3600, 1350, f"{zone_areas['Kids zone']} m² · fenced · soft floor", fs=4.6, c='#7a5a00')
txt(3600, 4400, 'PHOTO ZONE', fs=6.2, w='bold', c='#8a2a55')
txt(9500, 10500, 'BBQ / OUTDOOR KITCHEN', fs=5.2, w='bold', c='#8a3a10', box_=True)
txt(1050, 12000, 'BAR', fs=7, w='bold', c='#3b2a1e', rot=90)
txt(3700, 18000, 'ALLEY', fs=6.5, w='bold', c='#5a4a3a', box_=True)
txt(8200, 14200, 'EAST ENTRANCE\n(street, main)', fs=5.2, w='bold', c=G_C, box_=True)
txt(4200, 38100, 'NORTH ENTRANCE (parking, step-free via ramp)', fs=5, w='bold', c=G_C, box_=True)
txt(4375, 30600, 'TAPCHAN AIVAN', fs=5.2, w='bold', c='#5a3a22', box_=True)
txt(4250, 25400, 'DINING NORTH', fs=5.2, w='bold', c='#5a3a22', box_=True)
txt(6100, 10050, 'DINING SOUTH', fs=5.2, w='bold', c='#5a3a22', box_=True)
txt(8900, 27000, 'BANQUETTE', fs=4.8, w='bold', c='#8E1F24', rot=84.4, box_=True)
for it in items:
    if it.get('label') and it['kind'] in ('station', 'host', 'pickup'):
        p = Polygon(it['poly']).centroid; txt(p.x + 450, p.y, it['label'], fs=4.2, c='#1d6f77', ha='left', box_=True)
for it in items:
    if it['kind'] == 'equip':
        p = Polygon(it['poly']).centroid; txt(xb(p.y) + 500, p.y, it['label'], fs=4.2, c='#8a3a10', ha='left', box_=True)
txt(13800, -2000, 'ROOF (dashed): steel frame, timber slat ceiling,\nfans + lanterns · columns 250×250 (■)', fs=4.4, c='#5a3a22', ha='left', box_=True)
txt(21800, 22000, 'ĐƯỜNG VÕ NGUYÊN GIÁP 15M', fs=7.5, c='#555', w='bold', rot=-84.4)
# dimensions (key ergonomic ones)
def dimh(x1, x2, y, s, fs=4.4):
    ax.plot([x1, x2], [y, y], color='#111', lw=pt(.15), zorder=11)
    for xx in (x1, x2): ax.plot([xx - 120, xx + 120], [y - 120, y + 120], color='#111', lw=pt(.3), zorder=11)
    txt((x1 + x2) / 2, y + 260, s, fs=fs, c='#111')
def dimv(x, y1, y2, s, fs=4.4):
    ax.plot([x, x], [y1, y2], color='#111', lw=pt(.15), zorder=11)
    for yy in (y1, y2): ax.plot([x - 120, x + 120], [yy - 120, yy + 120], color='#111', lw=pt(.3), zorder=11)
    txt(x - 260, (y1 + y2) / 2, s, fs=fs, c='#111', rot=90)
dimh(6300, 7500, 23000, '1200')
dimh(0, 550, 7400, '550'); dimh(550, 1500, 7400, '950'); dimh(1500, 2400, 7400, '900')
dimv(-700, 16300, 19700, '3400')
dimv(3000, BAR_Y0, BAR_Y1, f'{BAR_Y1 - BAR_Y0}')
dimh(2950, 4400, 12550, '1450')
dimv(7700, 21600 + 950, 24100 - 950, '600');

# north arrow + title
ax.add_patch(MPoly([(21500, 45300), (20900, 42700), (21500, 43250), (22100, 42700)], closed=True, fc='#222', ec='none', zorder=12)); txt(21500, 46100, 'N', fs=8, w='bold')
tb = fig.add_axes([12 / PAPER[0], 8 / PAPER[1], (PAPER[0] - 24) / PAPER[0], 50 / PAPER[1]]); tb.set_xlim(0, PAPER[0] - 24); tb.set_ylim(0, 50); tb.axis('off')
tb.add_patch(plt.Rectangle((0, 0), PAPER[0] - 24, 50, fill=False, ec='#222', lw=.8)); tb.plot([150, 150], [0, 50], color='#222', lw=.5); tb.plot([0, 150], [30, 30], color='#222', lw=.5)
tb.text(4, 43, 'SAMARKAND', fontsize=15, weight='bold', **TXT)
tb.text(4, 35.5, 'Covered terrace — layout R1 (zoning, furniture, flows)', fontsize=8.5, **TXT)
tb.text(4, 24, '254 Võ Nguyên Giáp, Đà Nẵng · base: as-built DWG 10-07-2024', fontsize=6.2, **TXT)
tb.text(4, 17, 'Assumptions: terrace floor stays −0.470 · car ramp kept · planters on boundary kept ·', fontsize=5.4, color='#444', **TXT)
tb.text(4, 12.5, 'old pergola and round elements removed · new roof over the whole zone.', fontsize=5.4, color='#444', **TXT)
tb.text(4, 6, "Origin (0,0) = axis 6 × axis A'. Units mm. Scale 1:200 @ A3. 2026-10-22 · R1", fontsize=5.4, color='#444', **TXT)
rows = [(k, v) for k, v in seats.items()] + [('TOTAL SEATS', total)]
for i, (k, v) in enumerate(rows):
    tb.text(154, 45 - i * 5.6, k, fontsize=5.4, color='#555' if k != 'TOTAL SEATS' else '#111', weight='bold' if k == 'TOTAL SEATS' else 'normal', **TXT)
    tb.text(262, 45 - i * 5.6, str(v), fontsize=5.8, weight='bold', ha='right', **TXT)
# zone table + legend top
nt = fig.add_axes([12 / PAPER[0], 352 / PAPER[1], 273 / PAPER[0], 60 / PAPER[1]]); nt.axis('off'); nt.set_xlim(0, 273); nt.set_ylim(0, 60)
nt.text(0, 57, 'ZONES', fontsize=6.5, weight='bold', **TXT)
zl = list(zone_areas.items()) + [('Dining + circulation (rest)', round(FLOOR.area / 1e6 - sum(zone_areas.values()), 1)), ('Planters (kept)', round(planter.area / 1e6, 1)), ('Usable total (car ramp kept)', round(U.area / 1e6, 1))]
for i, (k, v) in enumerate(zl):
    col = ZC.get(k, '#f6efe2' if 'Dining' in k else '#cfe3c0' if 'Planter' in k else '#ffffff')
    nt.add_patch(plt.Rectangle((0, 49.5 - i * 5.2), 5, 3.4, fc=col, ec='#999', lw=.3))
    nt.text(7, 51.2 - i * 5.2, k, fontsize=5.4, va='center', **TXT); nt.text(80, 51.2 - i * 5.2, f'{v} m²', fontsize=5.6, weight='bold', va='center', ha='right', **TXT)
nt.text(100, 57, 'WHY THIS WORKS', fontsize=6.5, weight='bold', **TXT)
why = ['• Two entrances, one spine: street stair → plaza → alley → hall doors; parking → north aisle.',
       '• Bar on the façade under the balcony: closest to the hall, waiter pick-up faces the dining.',
       '• BBQ on the street side: smoke goes out over the planter, the show faces the alley and plaza.',
       '• Kids + photo at the quiet south end, 9 m from the fire, visible from the dining.',
       '• Staff (orange) use doors D–E / C–D, stations W1/W2, never cross the kids zone.',
       '• Tapchans under the existing canopy: shade, privacy, family tables next to parking.',
       '• Aisles ≥ 1200, alley 3400, 600 between chair backs, 2550 clear at the hall doors.',
       '• Roof columns sit on the building grid, inside planters or in aisle gaps.']
for i, t in enumerate(why): nt.text(100, 50.5 - i * 5.3, t, fontsize=5.2, color='#333', **TXT)
lg = fig.add_axes([12 / PAPER[0], 63 / PAPER[1], 273 / PAPER[0], 5 / PAPER[1]]); lg.axis('off'); lg.set_xlim(0, 273); lg.set_ylim(0, 5)
for x, c, ls, s in ((0, G_C, '-', 'Guest flow'), (50, S_C, (0, (3, 2)), 'Staff flow'), (100, '#5a3a22', (0, (2, 2)), 'New roof edge'), (150, '#2f5fb3', (0, (5, 3)), 'Existing canopy / balcony above'), (225, '#8E1F24', (0, (4, 2)), 'Exhaust hood')):
    lg.plot([x, x + 8], [2.5, 2.5], color=c, ls=ls, lw=1.6); lg.text(x + 10, 2.5, s, fontsize=5.4, va='center', **TXT)
fig.savefig(f'{OUT}/samarkand-terrace-layout-R1.pdf'); fig.savefig(f'{OUT}/samarkand-terrace-layout-R1.png', dpi=220); plt.close(fig)

# ================= DXF =================
doc = ezdxf.readfile(BASE_DXF); msp = doc.modelspace()
for lay, col in (('SMK-L-FURN', 7), ('SMK-L-BAR', 40), ('SMK-L-BBQ', 30), ('SMK-L-PHOTO', 5), ('SMK-L-KIDS', 2), ('SMK-L-SERV', 4), ('SMK-L-ROOF', 34), ('SMK-L-ZONES', 8), ('SMK-L-TEXT', 7)):
    if lay not in doc.layers: doc.layers.add(lay, color=col)
for it in items:
    msp.add_lwpolyline(it['poly'][:-1], close=True, dxfattribs={'layer': it['layer']})
for k, p in zones.items():
    msp.add_lwpolyline(list(p.exterior.coords)[:-1], close=True, dxfattribs={'layer': 'SMK-L-ZONES'})
    c = p.representative_point(); msp.add_text(k.upper(), height=300, dxfattribs={'layer': 'SMK-L-TEXT'}).set_placement((c.x, c.y), align=TextEntityAlignment.MIDDLE_CENTER)
doc.saveas(f'{OUT}/samarkand-terrace-layout-R1.dxf')
print('saved')
