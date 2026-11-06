"""Render the design-zone base plan: A3 portrait sheet at 1:200 (PDF + PNG) and a layered DXF (mm, 1:1)."""
import sys, json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyArrow
import ezdxf
from ezdxf.enums import TextEntityAlignment

Z = json.load(open(sys.argv[1]))
OUTDIR = sys.argv[2]
L = Z['layers']; M = Z['measurements']; V = Z['zone_vertices']; G = Z['grid']
SCALE = 200
PAPER = (297, 420)  # A3 portrait, mm
# drawing window in model mm (local coords)
WX0, WX1 = -16200, 25200
WY0, WY1 = -8200, 47600

STYLE = {
    'BLDG': dict(color='#222', lw=.45), 'GLAZ': dict(color='#3a6ea5', lw=.3), 'DOOR': dict(color='#444', lw=.25),
    'ABOVE': dict(color='#2f5fb3', lw=.6, ls=(0, (6, 3))), 'EXIST': dict(color='#7a4a1e', lw=.45),
    'STEPS': dict(color='#7a4a1e', lw=.35), 'CONTEXT': dict(color='#9a9a9a', lw=.35),
}
ZONE_C = '#2e9e44'; LOT_C = '#d23c2c'; DIM_C = '#1d1d1d'; GRID_C = '#8a8a8a'

fig = plt.figure(figsize=(PAPER[0] / 25.4, PAPER[1] / 25.4), dpi=100)
# drawing area: left 12mm, bottom 62mm (title block), width/height derived from scale
dw = (WX1 - WX0) / SCALE; dh = (WY1 - WY0) / SCALE
ax = fig.add_axes([12 / PAPER[0], 72 / PAPER[1], dw / PAPER[0], dh / PAPER[1]])
ax.set_xlim(WX0, WX1); ax.set_ylim(WY0, WY1); ax.set_aspect('equal'); ax.axis('off')
pt = lambda mm: mm * 72 / 25.4  # paper mm -> points
TXT = dict(family='DejaVu Sans')

# building context (hall west of facade + bay 5-6 north of A)
ax.add_patch(Polygon([(WX0, 4100), (0, 4100), (0, 37100), (WX0, 37100)], closed=True, fc='#e9e6e1', ec='none', zorder=0))
ax.text(-6700, 20600, 'EXISTING BUILDING\nMAIN HALL  ±0.000', ha='center', va='center', fontsize=7, color='#6b6b6b', rotation=90, **TXT)

# zone
zone = Z['zone']
ax.add_patch(Polygon(zone, closed=True, fc=ZONE_C, alpha=.10, ec='none', zorder=1))
ax.add_patch(Polygon(zone, closed=True, fill=False, ec=ZONE_C, lw=pt(.7), zorder=6))
for k, (x, y) in V.items():
    ax.add_patch(Circle((x, y), 160, fc='white', ec=ZONE_C, lw=pt(.3), zorder=7))
    lab = k.split('_')[0]
    off = {'Z1': (-250, 300), 'Z2': (250, 250), 'Z3': (300, 0), 'Z4': (150, -650), 'Z5': (-250, -650), 'Z6': (-250, 250), 'Z7': (250, 250)}[lab]
    ax.text(x + off[0], y + off[1], lab, fontsize=6, color=ZONE_C, weight='bold', ha='left' if off[0] > 0 else 'right', **TXT, zorder=8)

# lot
lot = L['LOT'][0]
xs, ys = zip(*lot)
ax.plot(xs, ys, color=LOT_C, lw=pt(.5), ls=(0, (10, 3, 2, 3)), zorder=5)

# grid
for n, (o, v) in G.items():
    if o == 'h':
        ax.plot([-14100, 15500], [v, v], color=GRID_C, lw=pt(.18), ls=(0, (12, 3, 2, 3)), zorder=2)
        ax.add_patch(Circle((-14800, v), 650, fc='white', ec=GRID_C, lw=pt(.25), zorder=3))
        ax.text(-14800, v, n, ha='center', va='center', fontsize=6.5, color='#333', **TXT, zorder=4)
    else:
        ax.plot([v, v], [-5600, 44200], color=GRID_C, lw=pt(.18), ls=(0, (12, 3, 2, 3)), zorder=2)
        ax.add_patch(Circle((v, -6300), 650, fc='white', ec=GRID_C, lw=pt(.25), zorder=3))
        ax.text(v, -6300, n, ha='center', va='center', fontsize=6.5, color='#333', **TXT, zorder=4)

for lay, st in STYLE.items():
    for p in L[lay]:
        xs, ys = zip(*p)
        ax.plot(xs, ys, color=st['color'], lw=pt(st['lw']) * 1.0, ls=st.get('ls', '-'), zorder=4 if lay != 'ABOVE' else 5, solid_capstyle='butt')

# ---------- dimensions ----------
def dim(p1, p2, off, text=None, fs=5.6, side=1):
    (x1, y1), (x2, y2) = p1, p2
    ang = math.atan2(y2 - y1, x2 - x1)
    nx, ny = -math.sin(ang) * off, math.cos(ang) * off
    a = (x1 + nx, y1 + ny); b = (x2 + nx, y2 + ny)
    ext = 250 if off > 0 else -250
    ex, ey = -math.sin(ang), math.cos(ang)
    for (px, py), (qx, qy) in (((x1, y1), a), ((x2, y2), b)):
        ax.plot([px + ex * 200 * (1 if off > 0 else -1), qx + ex * ext], [py + ey * 200 * (1 if off > 0 else -1), qy + ey * ext], color=DIM_C, lw=pt(.13), zorder=9)
    ax.plot([a[0], b[0]], [a[1], b[1]], color=DIM_C, lw=pt(.18), zorder=9)
    for q in (a, b):  # architectural ticks
        t = 180
        ax.plot([q[0] - t * math.cos(ang + math.pi / 4), q[0] + t * math.cos(ang + math.pi / 4)], [q[1] - t * math.sin(ang + math.pi / 4), q[1] + t * math.sin(ang + math.pi / 4)], color=DIM_C, lw=pt(.35), zorder=9)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    rot = math.degrees(ang)
    if rot > 90.5 or rot < -89.5: rot += 180
    d = math.dist(p1, p2)
    s = text or f'{d:.0f}'
    nn = 230 if off >= 0 else -230
    ax.text(mx + ex * nn * side, my + ey * nn * side, s, rotation=rot, rotation_mode='anchor', ha='center', va='bottom' if off * side >= 0 else 'top', fontsize=fs, color=DIM_C, **TXT, zorder=10)

gy = {n: v for n, (o, v) in G.items() if o == 'h'}
# facade chain (left of building) A'..G..Z1
chain = [("A'", gy["A'"]), ('A', gy['A']), ('B', gy['B']), ('C', gy['C']), ('D', gy['D']), ('E', gy['E']), ('F', gy['F']), ('G', gy['G']), ('Z1', V['Z1_NW'][1])]
X_CH = -10600
for (n1, y1), (n2, y2) in zip(chain, chain[1:]):
    dim((X_CH, y2), (X_CH, y1), 0, side=1)
dim((X_CH - 1300, V['Z1_NW'][1]), (X_CH - 1300, 0), 0, f"{V['Z1_NW'][1]:.0f}", side=1)
# depth facade -> boundary along axes
for n in ('G', 'D', 'A'):
    y = gy[n]
    xb = M[f'facade_to_boundary_at_{n}']
    dim((0, y), (xb, y), 1300 if n == 'G' else 520, f'{xb}')
# zone edges
dim(V['Z1_NW'], V['Z2_NE'], 1500, f"{M['north_edge_Z1_Z2']}")
dim(V['Z2_NE'], V['Z3_SE'], 2600, f"{M['east_edge_Z2_Z3']}", side=1)
dim(V['Z4_S'], V['Z3_SE'], -1500, f"{M['south_edge_Z3_Z4']}")
dim(V['Z5_pocketSW'], (V['Z5_pocketSW'][0], 0) if False else V['Z6_pocketNW'], 1200, '4100')
dim((V['Z5_pocketSW'][0], -3400), (0, -3400), 0, '7250')

# canopy & balcony dims
can = L['ABOVE'][0]
cx0, cx1 = min(p[0] for p in can), max(p[0] for p in can); cy0, cy1 = min(p[1] for p in can), max(p[1] for p in can)
dim((cx0, cy1), (cx1, cy1), 420, f'{cx1 - cx0:.0f}', fs=5)
dim((cx1, cy1), (cx1, cy0), -420, f'{cy1 - cy0:.0f}', fs=5, side=1)
bal = L['ABOVE'][1]
bx1 = max(p[0] for p in bal)

# ---------- labels ----------
def label(x, y, s, fs=5.4, color='#333', ha='left', rot=0, weight='normal', zorder=11, box=False):
    kw = dict(fontsize=fs, color=color, ha=ha, va='center', rotation=rot, weight=weight, zorder=zorder, **TXT)
    if box: kw['bbox'] = dict(boxstyle='round,pad=0.25', fc='white', ec='none', alpha=.85)
    ax.text(x, y, s, **kw)

def leader(x0, y0, x1, y1, s, fs=5.2, color='#333', ha='left'):
    ax.plot([x0, x1], [y0, y1], color=color, lw=pt(.15), zorder=11)
    ax.add_patch(Circle((x0, y0), 70, fc=color, ec='none', zorder=11))
    label(x1 + (120 if ha == 'left' else -120), y1, s, fs=fs, color=color, ha=ha, box=True)

label(6300, 19500, 'DESIGN ZONE\nterrace / outdoor bar', fs=8.5, color=ZONE_C, ha='center', weight='bold')
label(6300, 17500, f"{M['zone_area_m2']} m² total · 446.5 m² without car ramp\n(incl. bay 5–6/A–A' {M['pocket_area_m2']} m²)", fs=5.6, color=ZONE_C, ha='center')
leader(1800, 33000, 7600, 34200, 'Entrance canopy above (F1 roof)', color='#2f5fb3')
leader(bx1 - 300, 9000, 3200, 8000, f'Floor-2 balcony above, ≤{bx1:.0f}', color='#2f5fb3')
leader(1100, 17800, 3700, 15800, 'Entrance steps ±0.000 → −0.470\n(3 risers, existing)', color='#7a4a1e')
leader(1200, 36100, 3600, 37900, 'Wheelchair ramp + rail (existing)', color='#7a4a1e')
leader(5999, 27097, 8400, 29600, 'Round element Ø2.0 (existing)', color='#7a4a1e')
leader(5999, 12722, 8400, 14000, 'Round element Ø2.0 (existing)', color='#7a4a1e')
leader(10500, 30000, 12600, 31500, 'Planter wall\non boundary (existing)', color='#7a4a1e')
leader(11400, 16000, 13200, 19800, 'Steps from sidewalk\n−1.170 → −0.470\nwidth 4940 (existing)', color='#7a4a1e')
leader(6500, 6300, 4300, 2100, 'Pergola 6.0 × 5.8, 6 posts 200×200\n(existing — keep or remove?)', color='#7a4a1e', ha='left')
leader(13600, -2400, 15000, -4200, 'Gate pillar', color='#7a4a1e')
label(4800, 40300, 'EXISTING CAR RAMP 8% → rear parking\n53.4 m² of the zone — keep vehicle access?', fs=5.2, color='#b0471e', ha='center', box=True)
label(4500, -4500, 'Existing paved area (outside zone)', fs=5, color='#8a8a8a', ha='center')
label(-3600, 2050, "Bay 5–6 / A–A'\nopen to sky", fs=5.4, color=ZONE_C, ha='center')
label(21800, 22000, 'ĐƯỜNG VÕ NGUYÊN GIÁP 15M', fs=7.5, color='#555', ha='center', rot=-84.4, weight='bold')
label(11500, 43200, 'LOT BOUNDARY', fs=5, color=LOT_C, ha='left')
for t in Z['texts']:
    (x, y), s = t['p'], t['s']
    if t['kind'] == 'level':
        lvl = s.replace('-', '−')
        ax.add_patch(Polygon([(x, y), (x - 220, y + 330), (x + 220, y + 330)], closed=True, fc='#333', ec='none', zorder=11))
        label(x + 300, y + 200, lvl, fs=5.6, color='#111', weight='bold', box=True)
label(-1600, 26500, '±0.000', fs=5.6, color='#111', weight='bold', ha='right', box=True)

# north arrow
nx, ny = 21500, 43600
ax.add_patch(Polygon([(nx, ny + 1700), (nx - 600, ny - 900), (nx, ny - 350), (nx + 600, ny - 900)], closed=True, fc='#222', ec='none', zorder=12))
label(nx, ny + 2500, 'N', fs=8, color='#222', ha='center', weight='bold')

# ---------- key plan + site checks ----------
kp = fig.add_axes([12 / PAPER[0], 352 / PAPER[1], 110 / PAPER[0], 60 / PAPER[1]])
kp.set_aspect('equal'); kp.axis('off')
lx, ly = zip(*lot)
kp.fill(lx, ly, fc='#f3efe9', ec=LOT_C, lw=.7)
kp.add_patch(Polygon(zone, closed=True, fc=ZONE_C, alpha=.55, ec=ZONE_C, lw=.6))
kp.text(min(lx), max(ly) + 2500, 'KEY PLAN — whole lot, design zone in green', fontsize=6, weight='bold', **TXT)
kp.text(max(lx) + 1500, (min(ly) + max(ly)) / 2, 'VÕ NGUYÊN GIÁP', rotation=-84.4, fontsize=5, color='#555', va='center', **TXT)
kp.text(min(lx) - 1500, (min(ly) + max(ly)) / 2, 'LÂM HOÀNH', rotation=90, fontsize=5, color='#555', va='center', ha='right', **TXT)
nt = fig.add_axes([140 / PAPER[0], 352 / PAPER[1], 145 / PAPER[0], 60 / PAPER[1]]); nt.axis('off'); nt.set_xlim(0, 145); nt.set_ylim(0, 60)
nt.text(0, 57, 'VERIFY ON SITE BEFORE DESIGN FREEZE', fontsize=6.2, weight='bold', color='#b0471e', **TXT)
checks = ['1. Entrance canopy: F1 plan 4404 × 7638, site plan shows 5000 × 9200 — measure.',
          '2. Floor-2 balcony edge (≤1502 from façade) — confirm soffit height.',
          '3. Two round elements Ø2.0 — what are they (planter / fountain / tree)?',
          '4. Pergola 6.0 × 5.8: west side open in DWG — keep, rebuild or remove?',
          "5. Bay 5–6 / A–A': open to sky in F2 plan; F3 / roof not checked.",
          '6. Levels from DWG: ±0.000 hall, −0.470 forecourt, −1.170 sidewalk.',
          '7. Drainage, power, water points in the zone are not in the DWG.',
          '8. North strip Z1–Z2 is the 8% car ramp to parking: keep, or relocate access?']
for i, t in enumerate(checks):
    nt.text(0, 49 - i * 6.6, t, fontsize=5.4, color='#333', **TXT)

# ---------- title block ----------
tb = fig.add_axes([12 / PAPER[0], 8 / PAPER[1], (PAPER[0] - 24) / PAPER[0], 50 / PAPER[1]])
tb.set_xlim(0, PAPER[0] - 24); tb.set_ylim(0, 50); tb.axis('off')
tb.add_patch(plt.Rectangle((0, 0), PAPER[0] - 24, 50, fill=False, ec='#222', lw=.8))
tb.plot([150, 150], [0, 50], color='#222', lw=.5); tb.plot([0, 150], [30, 30], color='#222', lw=.5)
tb.text(4, 43, 'SAMARKAND', fontsize=15, weight='bold', **TXT)
tb.text(4, 35.5, 'Design zone — base plan (existing conditions)', fontsize=8.5, **TXT)
tb.text(4, 24, '254 Võ Nguyên Giáp, P. Phước Mỹ, Q. Sơn Trà, Đà Nẵng', fontsize=6.5, **TXT)
tb.text(4, 18, 'Source: BV hoàn công 10-07-2024 (Long House) — DWG, sheets "Tổng mặt bằng tầng 1",', fontsize=5.6, color='#444', **TXT)
tb.text(4, 13.5, '"Mặt bằng bố trí tầng 1/2". Sheets aligned on grid 6×G; geometry taken 1:1 in mm.', fontsize=5.6, color='#444', **TXT)
tb.text(4, 7, "Origin (0,0) = axis 6 × axis A'.  Units: mm.  Levels: building ±0.000.", fontsize=5.6, color='#444', **TXT)
rows = [('Scale', '1:200 @ A3'), ('Zone area', f"{M['zone_area_m2']} m² (446.5 w/o ramp)"), ('Façade A–G', '33 000'),
        ('Depth at G / D / A', f"{M['facade_to_boundary_at_G']} / {M['facade_to_boundary_at_D']} / {M['facade_to_boundary_at_A']}"),
        ('East boundary', f"{M['east_edge_Z2_Z3']}, {M['east_boundary_bearing_deg_from_north']}° off N"),
        ('Date / rev', '2026-10-22 / R0')]
for i, (k, v) in enumerate(rows):
    tb.text(154, 44 - i * 7.2, k, fontsize=5.6, color='#555', **TXT)
    tb.text(196, 44 - i * 7.2, v, fontsize=6, weight='bold', **TXT)
# legend strip above title block
lg = fig.add_axes([12 / PAPER[0], 58.5 / PAPER[1], (PAPER[0] - 24) / PAPER[0], 5 / PAPER[1]]); lg.axis('off'); lg.set_xlim(0, 273); lg.set_ylim(0, 5)
items = [(ZONE_C, '-', 'Design zone'), (LOT_C, (0, (6, 2, 1, 2)), 'Lot boundary'), ('#2f5fb3', (0, (4, 2)), 'Above (canopy / balcony)'), ('#7a4a1e', '-', 'Existing site elements'), ('#9a9a9a', '-', 'Context')]
x = 0
for col, ls, s in items:
    lg.plot([x, x + 8], [2.5, 2.5], color=col, ls=ls, lw=1.6); lg.text(x + 10, 2.5, s, fontsize=5.6, va='center', **TXT); x += 55

fig.savefig(f'{OUTDIR}/samarkand-zone-base-plan.pdf')
fig.savefig(f'{OUTDIR}/samarkand-zone-base-plan.png', dpi=220)
plt.close(fig)

# ---------- DXF ----------
doc = ezdxf.new('R2018', setup=True)
doc.header['$INSUNITS'] = 4  # mm
doc.header['$MEASUREMENT'] = 1
lt = {'ZONE': (3, 'CONTINUOUS'), 'LOT': (1, 'DASHDOT'), 'GRID': (8, 'CENTER'), 'BLDG': (7, 'CONTINUOUS'), 'GLAZ': (5, 'CONTINUOUS'),
      'DOOR': (7, 'CONTINUOUS'), 'ABOVE': (5, 'DASHED'), 'EXIST': (30, 'CONTINUOUS'), 'STEPS': (30, 'CONTINUOUS'), 'CONTEXT': (8, 'CONTINUOUS'),
      'LEVEL': (7, 'CONTINUOUS'), 'DIMS': (7, 'CONTINUOUS'), 'TEXT': (7, 'CONTINUOUS')}
for k, (col, ltype) in lt.items():
    doc.layers.add(f'SMK-{k}', color=col, linetype=ltype)
msp = doc.modelspace()
for k in ['ZONE', 'LOT', 'BLDG', 'GLAZ', 'DOOR', 'ABOVE', 'EXIST', 'STEPS', 'CONTEXT']:
    for p in L[k]:
        closed = len(p) > 2 and math.dist(p[0], p[-1]) < 1
        msp.add_lwpolyline(p[:-1] if closed else p, close=closed, dxfattribs={'layer': f'SMK-{k}', 'ltscale': 50 if k in ('LOT', 'ABOVE') else 1})
for n, (o, v) in G.items():
    if o == 'h':
        msp.add_line((-14100, v), (15500, v), dxfattribs={'layer': 'SMK-GRID', 'ltscale': 60}); c = (-14800, v)
    else:
        msp.add_line((v, -5600), (v, 44200), dxfattribs={'layer': 'SMK-GRID', 'ltscale': 60}); c = (v, -6300)
    msp.add_circle(c, 650, dxfattribs={'layer': 'SMK-GRID'})
    msp.add_text(n, height=500, dxfattribs={'layer': 'SMK-GRID'}).set_placement(c, align=TextEntityAlignment.MIDDLE_CENTER)
ds = doc.dimstyles.new('SMK200')
ds.dxf.dimtxt = 450; ds.dxf.dimasz = 300; ds.dxf.dimexe = 200; ds.dxf.dimexo = 200; ds.dxf.dimtsz = 250; ds.dxf.dimdec = 0; ds.dxf.dimgap = 100
def ddim(p1, p2, dist):
    msp.add_aligned_dim(p1=p1, p2=p2, distance=dist, dimstyle='SMK200', dxfattribs={'layer': 'SMK-DIMS'}).render()
for (n1, y1), (n2, y2) in zip(chain, chain[1:]):
    ddim((0, y1), (0, y2), 10600)
ddim((0, 0), (0, V['Z1_NW'][1]), 11900)
for n in ('G', 'D', 'A'):
    ddim((0, gy[n]), (M[f'facade_to_boundary_at_{n}'], gy[n]), 1300 if n == 'G' else 520)
ddim(V['Z1_NW'], V['Z2_NE'], 1500)
ddim(V['Z2_NE'], V['Z3_SE'], 2600)
ddim(V['Z4_S'], V['Z3_SE'], -1500)
ddim(V['Z5_pocketSW'], (0, 0), -3400)
ddim(V['Z5_pocketSW'], V['Z6_pocketNW'], 1200)
ddim((cx0, cy1), (cx1, cy1), 420); ddim((cx1, cy1), (cx1, cy0), -420)
for t in Z['texts']:
    if t['kind'] == 'level':
        msp.add_text(t['s'], height=350, dxfattribs={'layer': 'SMK-LEVEL'}).set_placement((t['p'][0] + 300, t['p'][1] + 100))
msp.add_text('±0.000', height=350, dxfattribs={'layer': 'SMK-LEVEL'}).set_placement((-2600, 26400))
for x, y, s in [(5200, 20800, 'DESIGN ZONE'), (21800, 22000, 'DUONG VO NGUYEN GIAP 15M'), (-3600, 2050, "BAY 5-6 / A-A'")]:
    msp.add_text(s, height=500, dxfattribs={'layer': 'SMK-TEXT'}).set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)
doc.saveas(f'{OUTDIR}/samarkand-zone-base.dxf')
json.dump({k: v for k, v in Z.items() if k != 'layers'}, open(f'{OUTDIR}/samarkand-zone-data.json', 'w'), ensure_ascii=False, indent=1)
print('ok')
