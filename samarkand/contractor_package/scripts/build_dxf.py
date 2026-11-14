import json, math, collections, ezdxf
from ezdxf.enums import TextEntityAlignment as TA
from shapely.geometry import Polygon, LineString, MultiPolygon, box, Point
from shapely.ops import polygonize, unary_union
C = json.load(open('cad/cad_data.json')); D = json.load(open('r12/samarkand-3d-data-R12.json'))
TER = -0.45; K = 1000.0
def XY(x, y): return (y * K, -x * K)                       # model (x east, y north) -> CAD (X along the street, Y up = building side)
doc = ezdxf.new('R2010', setup=True); doc.units = 4; doc.header['$INSUNITS'] = 4; doc.header['$MEASUREMENT'] = 1; doc.header['$LTSCALE'] = 50
msp = doc.modelspace()
doc.styles.new('VN', dxfattribs={'font': 'arial.ttf'})
LAY = [('S-GRID', 8, 'CENTER'), ('A-WALL-CUT', 7, None), ('A-BLDG', 8, None), ('S-COLS', 1, None), ('S-BEAM', 1, 'DASHED'), ('S-PURL', 9, 'DASHED'), ('A-FURN', 3, None), ('A-FURN-BASE', 9, None),
       ('A-BOOTH', 30, None), ('A-AIVAN', 40, None), ('A-BAR', 5, None), ('A-MANGAL', 12, None), ('A-TENT', 60, None), ('A-FACADE', 150, None), ('A-CORR', 34, None), ('A-KIDS', 50, None), ('A-MISC', 9, None),
       ('A-FLOR-F1', 2, None), ('A-FLOR-F2', 4, None), ('A-FLOR-F3', 30, None), ('A-FLOR-F4', 6, None), ('A-FLOR-F5', 50, None), ('A-FLOR-F6', 8, None), ('A-FLOR-F7', 140, None), ('A-FLOR-TEXT', 7, None),
       ('A-CLNG', 150, None), ('A-ROOF', 9, None), ('E-LITE', 1, None), ('E-POWR', 5, None), ('A-PLNT', 92, None), ('A-DIMS', 1, None), ('A-TEXT', 7, None), ('A-SECT', 7, None), ('A-SECT-BEYOND', 9, None), ('A-WFIN', 6, None), ('A-FRAME', 7, None)]
for n, c, lt in LAY:
    l = doc.layers.add(n, color=c)
    if lt and lt in doc.linetypes: l.dxf.linetype = lt
def T(txt, p, h=150, lay='A-TEXT', al=TA.LEFT, rot=0): msp.add_text(txt, height=h, dxfattribs={'layer': lay, 'style': 'VN', 'rotation': rot}).set_placement(p, align=al)
def PL(pts, lay, closed=True, w=0): return msp.add_lwpolyline(pts, close=closed, dxfattribs={'layer': lay, 'const_width': w})
def polys(segs):
    ls = [LineString([(a, b), (c, d)]) for a, b, c, d in segs if (a - c) ** 2 + (b - d) ** 2 > 1e-10]
    if not ls: return [], []
    ps = list(polygonize(unary_union(ls)))
    if ps:
        u = unary_union(ps); gs = [u] if u.geom_type == 'Polygon' else list(getattr(u, 'geoms', []))
        return [g for g in gs if g.geom_type == 'Polygon' and g.area > 2e-5], []
    return [], ls
def draw_poly(g, lay, f):
    PL([f(x, y) for x, y in list(g.exterior.coords)[:-1]], lay)
    for r in g.interiors: PL([f(x, y) for x, y in list(r.coords)[:-1]], lay)
CL = {'Furniture': 'A-FURN', 'Booths': 'A-BOOTH', 'Booths.001': 'A-BOOTH', 'Aivan': 'A-AIVAN', 'Aivan.001': 'A-AIVAN', 'Bar': 'A-BAR', 'Bar.001': 'A-BAR', 'Mangal': 'A-MANGAL', 'Mangal.001': 'A-MANGAL',
      'Tapchans_tent': 'A-TENT', 'Tapchans_tent.001': 'A-TENT', 'Street_facade': 'A-FACADE', 'Street_facade.001': 'A-FACADE', 'Corridor': 'A-CORR', 'Corridor.001': 'A-CORR', 'Kids': 'A-KIDS', 'Building': 'A-BLDG',
      'Columns': 'S-COLS', 'Roof_structure': 'S-COLS', 'Photo_lounge': 'A-FURN', 'Service': 'A-BAR', 'Fountain': 'A-MISC', 'Trees': 'A-PLNT', 'Planting': 'A-PLNT', 'Planting.001': 'A-PLNT', 'Domes': 'S-COLS',
      'North_gate': 'A-FACADE', 'Lights': 'E-LITE', 'Lights.001': 'E-LITE', 'Bukhara_dome': 'E-LITE', 'Bukhara_dome.001': 'E-LITE', 'Pergola_existing': 'S-COLS'}
# ---------------- PLAN: slices
P_by = collections.defaultdict(lambda: collections.defaultdict(list))
for h, lst in C['plan'].items():
    for name, coll, segs in lst: P_by[(name, coll)][h] += segs
FOOT = {}
for (name, coll), hs in P_by.items():
    lay = CL.get(coll, 'A-MISC')
    if coll in ('Lights', 'Lights.001', 'Roof_skin'): continue
    cutp, cutl = polys(hs.get('1.2', []))
    structural = coll in ('Building', 'Columns', 'Roof_structure', 'Domes', 'Pergola_existing') or name.startswith(('Booth_partition', 'Street_pishtaq', 'Mangal_west', 'firewall', 'Boundary_clay', 'Bar_brickwall', 'Khiva_column', 'sarch'))
    if structural:
        for g in cutp: draw_poly(g, 'A-WALL-CUT' if coll != 'Building' else 'A-BLDG', XY)
        for l in cutl: msp.add_line(XY(*l.coords[0]), XY(*l.coords[1]), dxfattribs={'layer': 'A-WALL-CUT'})
        continue
    allp = []
    for h in ('0.4', '0.55', '0.73', '0.88', '1.2', '1.65'):
        p_, _ = polys(hs.get(h, [])); allp += p_
    if allp:
        u = unary_union(allp); gs = [u] if u.geom_type == 'Polygon' else list(getattr(u, 'geoms', []))
        for g in gs:
            if g.geom_type == 'Polygon' and g.area > 4e-4: draw_poly(g.simplify(0.002), lay, XY)
        FOOT[name] = u
    bp, _ = polys(hs.get('0.1', []))
    for g in bp:
        if g.area > 4e-4: draw_poly(g.simplify(0.002), 'A-FURN-BASE', XY)
    if name not in FOOT and bp: FOOT[name] = unary_union(bp)
# ---------------- grid
YAX = [('1', 4.1), ('2', 9.85), ('3', 15.3), ('4', 18.3), ('5', 21.35), ('6', 25.6), ('7', 29.1), ('8', 32.1), ('9', 36.3)]
def streetx(y): return 12.639 + (9.465 - 12.639) * (y - 4.1) / (36.3 - 4.1)
XAX = [('A', lambda y: 0.0), ('B', lambda y: 4.13), ('C', lambda y: 8.0), ('D', streetx)]
for t, y in YAX:
    a, b = XY(-2.2, y), XY(14.6, y); msp.add_line(a, b, dxfattribs={'layer': 'S-GRID'})
    for p in (a, b): msp.add_circle((p[0], p[1] + (400 if p is a else -400)), 320, dxfattribs={'layer': 'S-GRID'}); T(t, (p[0], p[1] + (400 if p is a else -400)), 300, 'S-GRID', TA.MIDDLE_CENTER)
for t, f in XAX:
    a, b = XY(f(-1.6), -1.6), XY(f(38.6), 38.6); msp.add_line(a, b, dxfattribs={'layer': 'S-GRID'})
    for p, s in ((a, -1), (b, 1)): msp.add_circle((p[0] + s * 400, p[1]), 320, dxfattribs={'layer': 'S-GRID'}); T(t, (p[0] + s * 400, p[1]), 300, 'S-GRID', TA.MIDDLE_CENTER)
ds = doc.dimstyles.new('SMK', dxfattribs={'dimtxt': 180, 'dimasz': 120, 'dimexo': 80, 'dimexe': 120, 'dimtad': 1, 'dimdec': 0, 'dimgap': 60, 'dimtxsty': 'VN', 'dimclrd': 1, 'dimclre': 1, 'dimclrt': 7, 'dimblk': 'ARCHTICK'})
def DIM(p1, p2, base, ang=0):
    d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=ang, dimstyle='SMK', dxfattribs={'layer': 'A-DIMS'}); d.render()
ys = [0.0] + [y for _, y in YAX] + [37.1]
for a, b in zip(ys[:-1], ys[1:]): DIM(XY(-1.0, a), XY(-1.0, b), (0, 1900))
DIM(XY(-1.0, 0.0), XY(-1.0, 37.1), (0, 2600))
for a, b in ((0.0, 4.13), (4.13, 8.0), (8.0, streetx(38.2))): DIM(XY(a, 38.2), XY(b, 38.2), (39300, 0), 90)
# ---------------- floor finish zones (closed polylines + areas)
def P(r): return Polygon(r).buffer(0)
fm = unary_union([P(r) for r in D['floor_main']] + [P(r) for r in D['inlays']['aryk']])
deck = Polygon([(0, 15.3), (3.3, 15.3), (3.3, 28.5), (2.4, 28.5), (2.4, 30.9), (0, 30.9)])          # aivan deck + north landing (L-shape)
_I = {r[0]: r for r in C['inv']}
booth = unary_union([box(_I[f'Booth{k}_shell'][2][0], _I[f'Booth{k}_shell'][2][1], _I[f'Booth{k}_shell'][3][0], _I[f'Booth{k}_shell'][3][1]) for k in range(1, 8)])
hauz = FOOT.get('Hauz_star_wall'); hauz = hauz.convex_hull if hauz is not None else Point(6.07, 29.65).buffer(0.7)
ring = FOOT.get('Tree_planter_ring_1'); ring = ring.convex_hull if ring is not None else Point(6.0, 12.72).buffer(0.93)
med = unary_union([P(r) for r in D['inlays']['medallion']])
def holes_free(g): return g
Z = collections.OrderedDict()
Z['F1'] = ('Đá marble trắng 500×500 lát chéo 45°, viền cobalt 90 / White marble 500×500 diagonal + cobalt band', fm.difference(unary_union([deck, booth, hauz, ring])).union(med.difference(hauz)))
Z['F2'] = ('Gạch zellige sao 8 cánh — hành lang / Zellige star tiles, corridor', unary_union([P(r) for r in D['inlays']['alley']]))
Z['F3'] = ('Gạch nung 300×150 chong chóng + gạch men 150 — aivan +0.450 / Terracotta pinwheel, aivan deck', deck)
Z['F4'] = ('Bục cabin +0.150: khung gỗ + thảm / Booth podium, timber + carpet', booth)
Z['F5'] = ('Cao su EPDM 500×500 — khu trẻ em / EPDM tiles, kids', unary_union([P(r) for r in D['inlays']['kids']]))
Z['F6'] = ('Đá slate chống trơn — mangal / Anti-slip slate, mangal', unary_union([P(r) for r in D['inlays']['bbq']]))
Z['F7'] = ('Hồ sao: men lam + đá / Star pool basin', hauz)
AREAS = {}
for k, (desc, g) in Z.items():
    gs = [g] if g.geom_type == 'Polygon' else list(g.geoms); AREAS[k] = (desc, round(g.area, 2), round(g.length, 2))
    for q in gs:
        if q.area < 0.01: continue
        draw_poly(q, f'A-FLOR-{k}', XY)
    c = max(gs, key=lambda q: q.area).representative_point(); T(f'{k}  {g.area:.1f} m²', XY(c.x, c.y), 260, 'A-FLOR-TEXT', TA.MIDDLE_CENTER)
# ---------------- roof framing + ceiling outline + lights + sockets
INV = {r[0]: r for r in C['inv']}; cnt = collections.Counter()
for n, r in INV.items():
    lo, hi = r[2], r[3]; cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    def rect(lay): PL([XY(lo[0], lo[1]), XY(hi[0], lo[1]), XY(hi[0], hi[1]), XY(lo[0], hi[1])], lay)
    if n.startswith('roof_beam_y'): rect('S-BEAM'); T(('HEB 300' if hi[0] - lo[0] > 8 else 'I 300×150') + f'  L={hi[0] - lo[0]:.2f} m', XY(lo[0] + 0.6, cy + 0.12), 120, 'S-BEAM', rot=-90)
    elif n.startswith('purlin') and 'cleat' not in n: rect('S-PURL')
    elif n.startswith(('Ceiling_coffers',)): rect('A-CLNG')
    elif 'chandelier' in n.lower() and 'rod' not in n or 'lantern_hang' in n or 'drum_pendant' in n or n == 'North_chandelier':
        msp.add_circle(XY(cx, cy), 180, dxfattribs={'layer': 'E-LITE'}); msp.add_line(XY(cx - 0.18, cy), XY(cx + 0.18, cy), dxfattribs={'layer': 'E-LITE'}); msp.add_line(XY(cx, cy - 0.18), XY(cx, cy + 0.18), dxfattribs={'layer': 'E-LITE'}); cnt['L-chandelier'] += 1
    elif n.startswith('Sconce'): msp.add_circle(XY(cx, cy), 90, dxfattribs={'layer': 'E-LITE'}); T('B', XY(cx, cy), 100, 'E-LITE', TA.MIDDLE_CENTER); cnt['L-sconce'] += 1
    elif 'uplight' in n.lower(): msp.add_circle(XY(cx, cy), 60, dxfattribs={'layer': 'E-LITE'}); cnt['L-uplight'] += 1
    elif n.startswith('Floor_socket'): PL([XY(cx - 0.09, cy - 0.09), XY(cx + 0.09, cy - 0.09), XY(cx + 0.09, cy + 0.09), XY(cx - 0.09, cy + 0.09)], 'E-POWR'); msp.add_line(XY(cx - 0.09, cy - 0.09), XY(cx + 0.09, cy + 0.09), dxfattribs={'layer': 'E-POWR'}); cnt['P-floorbox'] += 1
    elif 'socket' in n.lower(): msp.add_circle(XY(cx, cy), 70, dxfattribs={'layer': 'E-POWR'}); cnt['P-wallsocket'] += 1
# plants as circles
for n, r in INV.items():
    pass
# ---------------- title + area table in the drawing
bx0, by0 = -1500, -15800
T('SAMARKAND — MẶT BẰNG TỔNG THỂ / GENERAL PLAN   TL 1:100   (đơn vị mm / units mm)   R12-v12.1', (bx0, by0 + 600), 320)
T('BẢNG DIỆN TÍCH SÀN / FLOOR AREA SCHEDULE', (bx0, by0), 250)
yy = by0 - 450
for k, (desc, a, per) in AREAS.items():
    T(f'{k}', (bx0, yy), 180); T(f'{a:8.1f} m²', (bx0 + 800, yy), 180); T(f'chu vi / perimeter {per:7.1f} m', (bx0 + 2600, yy), 180); T(desc, (bx0 + 6600, yy), 180); yy -= 330
T(f'Tổng / Total {sum(v[1] for v in AREAS.values()):.1f} m²', (bx0, yy), 200)
# ---------------- SECTIONS (cut contours) placed below
SEC = [('A', 'x', 6.0, 'MẶT CẮT A-A (dọc, x = 6.0) / SECTION A-A'), ('B', 'y', 19.9, 'MẶT CẮT B-B (qua mái vòm) / SECTION B-B'), ('C', 'y', 29.7, 'MẶT CẮT C-C (aivan · sảnh · cabin) / SECTION C-C'),
       ('bar', 'y', 11.6, 'CẮT QUẦY BAR / BAR SECTION'), ('booth', 'y', 25.2, 'CẮT CABIN / BOOTH SECTION'), ('portal', 'y', 16.8, 'CẮT CỔNG VÀO / PORTAL SECTION'), ('portalx', 'x', 11.35, 'CẮT NGANG CỔNG / PORTAL CROSS SECTION'),
       ('aivan', 'x', 1.0, 'CẮT DỌC AIVAN (x = 1.0) / AIVAN LONG SECTION'), ('north', 'y', 33.0, 'CẮT KHU BẮC (lều · bàn · cabin) / NORTH ZONE SECTION'), ('photo', 'x', 6.86, 'CẮT KHU CHỤP ẢNH / PHOTO ZONE SECTION')]
oy = -34000; SECPOS = {}
for key, ax, val, ttl in SEC:
    lst = C['sec'].get(key, []); us = [v for _, _, s in lst for a, b, c, d in s for v in (a, c)]
    if not us: continue
    u0, u1 = min(us), max(us); ox = -u0 * K
    def F(u, w, ox=ox, oy=oy): return (u * K + ox, (w - TER) * K + oy)
    for name, coll, segs in lst:
        pp, ll = polys(segs); clipb = box(u0 - 1, TER - 1.3, u1 + 1, TER + 8.6)
        pp = [h for g in pp for h in ([g.intersection(clipb)] if g.intersection(clipb).geom_type == 'Polygon' else list(getattr(g.intersection(clipb), 'geoms', []))) if h.geom_type == 'Polygon' and h.area > 1e-5]
        for g in pp: draw_poly(g, 'A-SECT' if coll != 'Building' else 'A-BLDG', F)
        for l in ll: msp.add_line(F(*l.coords[0]), F(*l.coords[1]), dxfattribs={'layer': 'A-SECT'})
    msp.add_line(F(u0 - 0.5, TER), F(u1 + 0.5, TER), dxfattribs={'layer': 'S-GRID'}); T('±0.000', F(u1 + 0.6, TER), 160, 'A-DIMS')
    for z, t in ((0.0, '+0.450'), (2.79, '+3.240'), (3.09, '+3.540')): T(t, F(u1 + 0.6, z), 120, 'A-DIMS')
    T(ttl + '   TL 1:50', (0, oy - 1900), 260); SECPOS[key] = (ox, oy, u0, u1); oy -= 13000
# ---------------- wall finish developments (analytic panels with areas)
oy -= 1000; T('KHAI TRIỂN TƯỜNG AIVAN (nhìn vào tường nhà) / AIVAN WALL DEVELOPMENT   TL 1:50', (0, oy + 4300), 260)
WF = []
def panel(y0, y1, z0, z1, code, name, lay='A-WFIN'):
    PL([(y0 * K, z0 * K + oy), (y1 * K, z0 * K + oy), (y1 * K, z1 * K + oy), (y0 * K, z1 * K + oy)], lay)
    a = (y1 - y0) * (z1 - z0); T(code, ((y0 + y1) / 2 * K, (z0 + z1) / 2 * K + oy + 120), 170, 'A-WFIN', TA.MIDDLE_CENTER); T(f'{a:.2f} m²', ((y0 + y1) / 2 * K, (z0 + z1) / 2 * K + oy - 160), 130, 'A-WFIN', TA.MIDDLE_CENTER)
    WF.append((code, name, round(a, 2)))
for y0, y1, z0 in ((14.34, 15.28, 0.02), (15.32, 16.66, 0.47), (24.06, 25.96, 0.47), (27.82, 28.28, 0.47)): panel(y0, y1, z0, 3.24, 'W7', 'Vách lưới sao óc chó 30 / walnut star lattice (aivan wall)')
for y0, y1 in ((18.60, 20.39), (20.41, 22.21), (22.23, 24.03), (25.99, 27.79)): panel(y0 + 0.02, y1 - 0.02, 0.48, 3.20, 'W8', 'Thảm treo sàn–trần / wall carpet deck-to-ceiling')
panel(16.69, 18.58, 0.45, 3.0, 'D1', 'Cửa sảnh hiện trạng / existing hall door')
msp.add_line((14000, oy), (29000, oy), dxfattribs={'layer': 'S-GRID'}); msp.add_line((15300, 450 + oy), (28500, 450 + oy), dxfattribs={'layer': 'A-SECT'}); msp.add_line((14000, 3240 + oy), (28500, 3240 + oy), dxfattribs={'layer': 'A-SECT'})
oy -= 7000; T('KHAI TRIỂN TƯỜNG BAR / BAR BACK WALL   TL 1:50', (0, oy + 4300), 260)
panel(8.60, 14.30, 0.0, 3.55, 'W3', 'Gạch ốp vàng 230×65 + gạch men đầu / buff brick + glazed headers (bar wall)')
oy -= 6000; T('MẶT TRƯỚC QUẦY BAR / BAR COUNTER FRONT   TL 1:50', (0, oy + 2000), 260)
panel(8.10, 14.30, 0.10, 1.01, 'W3', 'Gạch ốp vàng — mặt trước quầy / buff brick, counter front')
oy -= 5000; T('KHAI TRIỂN DÃY CABIN (vách ngăn 8 tấm, hai mặt) / BOOTH PARTITIONS   TL 1:50', (0, oy + 3300), 260)
for k in range(8): panel(k * 2.3, k * 2.3 + 1.95, 0.0, 2.45, 'W6', 'Vách cabin đúc sẵn 1.950×2.450, lưới hai mặt / prefab booth partition (per face ×2)')
json.dump({'areas': AREAS, 'wall': WF, 'cnt': dict(cnt)}, open('cad/quant_plan.json', 'w'), ensure_ascii=False)
doc.saveas('cad/Samarkand_R12-v12.1.dxf')
print('entities', len(msp)); print({k: v[1] for k, v in AREAS.items()}); print(dict(cnt))
