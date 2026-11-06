"""Build the Samarkand design-zone base plan from the as-built DWG (parsed to db.json).

Sources (all 1:1 mm in model space):
  site plan  "TỔNG MẶT BẰNG TẦNG 1"  -> lot boundary, planters, stairs, pergola, levels
  plan F1    "MẶT BẰNG BỐ TRÍ TẦNG 1" -> facade walls/columns/glazing/doors, steps, ramp, canopy
  plan F2    "MẶT BẰNG BỐ TRÍ TẦNG 2" -> balcony slab outline above the zone
Sheets are aligned on the structural grid (axis 6 x axis G):
  F1 -> site: (+41530, +120147)   F2 -> site: (+41530, +183668)
Local origin of the output = intersection of axis 6 and axis A' (site 1006949, -259352).
"""
import sys, json, math
sys.path.insert(0, sys.argv[1])
from cad import CAD
import numpy as np

DB, OUT = sys.argv[2], sys.argv[3]
c = CAD(DB)

F1 = (41530.0, 120147.0)
F2 = (41530.0, 183668.0)
ORG = (1006949.0, -259352.0)
AX6_SITE = 1006949.0
AXES_Y_F1 = {"A'": -379499, 'A': -375399, 'B': -369649, 'C': -363899, 'D': -358149, 'E': -352399, 'F': -347399, 'G': -342399}
AXES_X_F1 = {'5': 958169, '6': 965419}

def loc(pts, off=(0, 0)):
    return [(round(x + off[0] - ORG[0], 1), round(y + off[1] - ORG[1], 1)) for x, y in pts]

def length(p): return sum(math.dist(p[i], p[i + 1]) for i in range(len(p) - 1))
def inside(pts, bb): return any(bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] for x, y in pts)
def allin(pts, bb): return all(bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] for x, y in pts)

layers = {k: [] for k in ['ZONE', 'LOT', 'GRID', 'BLDG', 'GLAZ', 'DOOR', 'ABOVE', 'EXIST', 'STEPS', 'CONTEXT', 'LEVEL']}
texts = []

# ---------------- lot boundary ----------------
lot = None
L_line = None
for kind, d, lay, e in c.explode():
    if kind == 'poly' and e.get('handle') == '3214':
        lot = d
    if kind == 'poly' and lay == '01- NET TUONG- 242' and len(d) in (4, 5) and abs(d[0][0] - 1005605) < 3 and abs(d[0][1] + 259645) < 3:
        L_line = (d[0], d[1])
assert lot and L_line
lot_l = loc(lot)
layers['LOT'].append(lot_l)

# ---------------- design zone polygon (site coords) ----------------
def inter(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

i_ne = min(range(len(lot)), key=lambda i: math.dist(lot[i], (1016605, -217387)))
NW_PREV, NE, SE = lot[i_ne - 1], lot[i_ne], lot[i_ne + 1]
yA, yA2 = AXES_Y_F1['A'] + F1[1], AXES_Y_F1["A'"] + F1[1]
x5 = AXES_X_F1['5'] + F1[0]
Z1 = inter(NW_PREV, NE, (AX6_SITE, 0), (AX6_SITE, 1))
Z2 = NE
Z3 = inter(NE, SE, L_line[0], L_line[1])
Z4 = inter(L_line[0], L_line[1], (0, yA2), (1, yA2))
Z5 = (x5, yA2)
Z6 = (x5, yA)
Z7 = (AX6_SITE, yA)
zone_site = [Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z1]
zone = loc(zone_site)
layers['ZONE'].append(zone)

def area(p):
    return abs(sum(p[i][0] * p[i + 1][1] - p[i + 1][0] * p[i][1] for i in range(len(p) - 1))) / 2

# ---------------- site-plan elements ----------------
SBB = (998000, -267600, 1023600, -213500)
for kind, d, lay, e in c.explode():
    if kind not in ('seg', 'poly') or not inside(d, SBB):
        continue
    xs = [p[0] for p in d]; ys = [p[1] for p in d]
    L = length(d)
    if lay == '01- NET TUONG- 242' and min(xs) > 1005000 and min(ys) > -267000 and not (max(xs) < 1007000):
        tgt = 'CONTEXT' if min(ys) < -262500 and max(ys) < -255800 and min(xs) < 1006000 else 'EXIST'
        layers[tgt].append(loc(d))
    elif lay == '8l NET TO':
        horiz_axis = kind == 'seg' and abs(ys[0] - ys[1]) < 1 and min(xs) < 990000
        if horiz_axis or L < 400:
            continue
        north_ramp = min(ys) > -223000 and max(ys) < -217000 and 1006500 < min(xs) and max(xs) < 1017300 and not (abs(ys[0] - ys[-1]) > 900 and abs(xs[0] - xs[-1]) > 9000)
        planter_inner = len(d) >= 4 and min(xs) > 1015500 and max(xs) < 1021000 and -258000 < min(ys) and max(ys) < -222000
        stair = 1017400 < min(xs) and max(xs) < 1019100 and -246100 < min(ys) and max(ys) < -240900 and 4800 < L < 5100
        pillar = min(xs) > 1019300 and max(xs) < 1021000 and min(ys) > -262300 and max(ys) < -260700
        round_el = False
        bottom = len(d) == 5 and min(ys) < -259000 and max(ys) > -260000 and min(xs) > 1005000 and min(ys) > -266000
        if north_ramp:
            layers['CONTEXT'].append(loc(d))
        elif planter_inner or pillar or round_el:
            layers['EXIST'].append(loc(d))
        elif stair:
            layers['STEPS'].append(loc(d))
        elif bottom:
            layers['CONTEXT'].append(loc(d))
    elif lay == 'A_Dim' and kind == 'seg' and 1017400 < min(xs) and max(xs) < 1019100 and -246100 < min(ys) and max(ys) < -240900 and 4800 < L < 5100:
        layers['STEPS'].append(loc(d))
    elif lay == '04-Net thay' and min(xs) > 1006500 and max(ys) < -217000 and min(ys) > -223500:
        layers['CONTEXT'].append(loc(d))
    elif lay == '0___TUONG XAY MOI' and len(d) > 4:
        layers['CONTEXT'].append(loc(d))
    elif kind == 'text':
        pass
for kind, d, lay, e in c.explode():
    if kind == 'poly' and len(d) > 40:
        xs = [p[0] for p in d]; ys = [p[1] for p in d]
        cx, cy, r = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (max(xs) - min(xs)) / 2
        if abs(cx - 1012948) < 60 and (abs(cy + 232255) < 60 or abs(cy + 246630) < 60) and 700 < r < 1100:
            layers['EXIST'].append(loc(d))
for kind, d, lay, e in c.explode():
    if kind == 'text':
        p, s, h = d
        if SBB[0] < p[0] < SBB[2] and SBB[1] < p[1] < SBB[3] and s.strip() in ('- 0.470', '- 1.170', 'ĐỘ DỐC 8%'):
            texts.append({'p': loc([p])[0], 's': s.replace(' ', '') if s.startswith('-') else 'RAMP 8%', 'kind': 'level' if s.startswith('-') else 'note'})

# ---------------- floor 1 (facade) elements ----------------
FBB = (956500, -379700, 970500, -341300)
keep_f1 = {'A-Wall': 'BLDG', 'A-GLAZ-CURT': 'GLAZ', '03- Net Cua- 153': 'GLAZ', '04-Net thay': 'BLDG', 'X-BT-MB-F1$0$SP-CỬA': 'DOOR',
           '01- NET TUONG- 242': 'BLDG', '0': 'BLDG', '05- Net Khuat - 250': 'ABOVE'}
for kind, d, lay, e in c.explode():
    if kind not in ('seg', 'poly') or not allin(d, FBB):
        continue
    xs = [p[0] for p in d]; ys = [p[1] for p in d]
    if lay in keep_f1:
        # inside the hall keep only the facade band and the A-A' bay
        if max(xs) < 964900 and not (min(ys) > -379700 and max(ys) < -375150):
            continue
        layers[keep_f1[lay]].append(loc(d, F1))
    elif lay == 'A_Dim' and e['type'] == 'LWPOLYLINE' and min(xs) > 965400 and max(xs) < 968500 and length(d) > 1000:
        tgt = 'STEPS' if (max(xs) - min(xs) < 5 and length(d) > 4000) else 'EXIST'
        layers[tgt].append(loc(d, F1))
    elif lay in ('01- NET TUONG- 242', 'A-Wall', 'TUONG', 'A-WALL-FNSH') and min(xs) > 956500 and min(ys) > -379700 and max(ys) < -375000:
        layers['BLDG'].append(loc(d, F1))

# ---------------- floor 2 balcony (above) ----------------
for kind, d, lay, e in c.explode():
    if kind == 'poly' and lay == '0' and len(d) > 30:
        xs = [p[0] for p in d]; ys = [p[1] for p in d]
        if abs(min(xs) - 965419) < 5 and 966500 < max(xs) < 967200 and -439500 < min(ys) < -438000:
            layers['ABOVE'].append(loc(d, F2))

# ---------------- grid ----------------
grid = {}
for n, y in AXES_Y_F1.items():
    grid[n] = ('h', round(y + F1[1] - ORG[1], 1))
for n, x in AXES_X_F1.items():
    grid[n] = ('v', round(x + F1[0] - ORG[0], 1))

# ---------------- measurements ----------------
def xb_at(y_site):  # east boundary x at a given site y
    return inter(NE, SE, (0, y_site), (1, y_site))[0]
meas = {}
for n, y in AXES_Y_F1.items():
    ys_ = y + F1[1]
    if ys_ >= Z3[1] - 1e-6 or n == 'A':
        meas[f'facade_to_boundary_at_{n}'] = round(xb_at(ys_) - AX6_SITE)
meas['north_edge_Z1_Z2'] = round(math.dist(Z1, Z2))
meas['east_edge_Z2_Z3'] = round(math.dist(Z2, Z3))
meas['south_edge_Z3_Z4'] = round(math.dist(Z3, Z4))
meas['facade_A_to_north_boundary'] = round(Z1[1] - yA)
meas['facade_A_to_G'] = 33000
meas['pocket_5_6_x_A_Aprime'] = [7250, 4100]
meas['zone_area_m2'] = round(area(zone) / 1e6, 1)
meas['pocket_area_m2'] = round(7.25 * 4.1, 1)
meas['east_boundary_bearing_deg_from_north'] = round(math.degrees(math.atan2(SE[0] - NE[0], NE[1] - SE[1])), 2)
meas['south_edge_angle_deg'] = round(math.degrees(math.atan2(Z3[1] - Z4[1], Z3[0] - Z4[0])), 2)

out = {
    'units': 'mm', 'origin': 'axis 6 x axis A\'', 'origin_site_coords': ORG,
    'offsets': {'F1_to_site': F1, 'F2_to_site': F2},
    'zone': zone, 'zone_vertices': dict(zip(['Z1_NW', 'Z2_NE', 'Z3_SE', 'Z4_S', 'Z5_pocketSW', 'Z6_pocketNW', 'Z7_bldgSE'], zone[:7])),
    'grid': grid, 'levels': {'building_floor': 0.0, 'forecourt': -0.470, 'sidewalk_VNG': -1.170},
    'measurements': meas, 'layers': layers, 'texts': texts,
}
json.dump(out, open(OUT, 'w'))
print(json.dumps(meas, indent=1, ensure_ascii=False))
print({k: len(v) for k, v in layers.items()}, len(texts))
