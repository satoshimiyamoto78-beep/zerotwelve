"""Samarkand covered terrace — Layout R4 (owner review 2026-10-22).
Clean orthogonal geometry on the building grid; local mm (origin axis 6 x axis A', x east, y north).
Outputs: JSON + DXF (base + SMK-R3-*) + SVG presentation sheets in Russian and English.
"""
import sys, json, math
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import split, unary_union
import ezdxf

Z = json.load(open(sys.argv[1])); BASE_DXF = sys.argv[2]; OUT = sys.argv[3]
L = Z['layers']; V = Z['zone_vertices']

# ---------------- site ----------------
Z2, Z3 = V['Z2_NE'], V['Z3_SE']
SLOPE = (Z3[0] - Z2[0]) / (Z2[1] - Z3[1])
def xb(y): return Z3[0] - (y - Z3[1]) * SLOPE          # east boundary
def xi(y): return xb(y) - 1500                          # planter inner face
def yr(x): return 37090.5 - 0.06542 * (x - 83.6)        # driveway edge
def ys(x): return Z3[1] * (x - V['Z4_S'][0]) / (Z3[0] - V['Z4_S'][0])
zone = Polygon(Z['zone'])
U = sorted(split(zone, LineString([(-20000, yr(-20000)), (30000, yr(30000))])).geoms, key=lambda g: g.centroid.y)[0]
def R(x0, y0, x1, y1): return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
def C(x, y, r, n=48): return Point(x, y).buffer(r, n)

items = []
def add(kind, geom, layer='SMK-R3-FURN', **kw):
    items.append(dict(kind=kind, geom=geom, layer=layer, **kw)); return geom
seats = {}
def seat(k, n): seats[k] = seats.get(k, 0) + n

# ---------------- fixed decisions ----------------
ENT = (15550, 18050)                       # street entrance narrowed to 2500
TREE_N, TREE_S = (5999, 27097), (5999, 12722)
DOORS = {'cd': (16795, 20155, True), 'de_s': (22545, 24225, False), 'de_n': (24225, 25905, True), 'ef': (28663, 30363, True)}

# planters: existing band along the boundary, entrance gap 2.5 m; booths/BBQ are orthogonal, the slant is absorbed by planting
band = Polygon([(xi(-500), -500), (xb(-500) + 10, -500), (xb(40000) + 10, 40000), (xi(40000), 40000)]).intersection(U)
gap = R(xi(ENT[0]) - 400, ENT[0], xb(ENT[0]) + 400, ENT[1])
planter = band.difference(gap)

# ======================= SOUTH =======================
KIDS = Polygon([V['Z5_pocketSW'], V['Z4_S'], V['Z7_bldgSE'], V['Z6_pocketNW']])
# photo zone: orthogonal pishtaq wall, planting behind it
PH_WALL = R(1300, 1650, 5300, 2000)
add('pishtaq', PH_WALL, 'SMK-R3-PHOTO')
add('pishtaq_niche', R(2650, 2000, 3950, 2180), 'SMK-R3-PHOTO')
add('medallion', C(3300, 3450, 850, 64), 'SMK-R3-PHOTO')
add('camera', C(3300, 5050, 160, 24), 'SMK-R3-PHOTO')
photo_plant = Polygon([(1000, ys(1000)), (5800, ys(5800)), (5800, 1650), (1000, 1650)])
# staff service station (owner's blue)
add('shelving', R(0, 4300, 600, 8350), 'SMK-R3-SERV')
add('counter', R(1400, 5300, 2000, 8100), 'SMK-R3-SERV')
add('screenwall', R(2000, 5300, 2080, 8400), 'SMK-R3-SERV')
# bar: counter 5.7 m, staff steps up to the platform at the north end
BAR = (8600, 14300)
add('backbar', R(0, BAR[0], 550, BAR[1]), 'SMK-R3-BAR')
add('barbody', R(1500, BAR[0], 2100, BAR[1]), 'SMK-R3-BAR')
add('bartop', R(2100, BAR[0] - 100, 2400, BAR[1]), 'SMK-R3-BAR')
add('barreturn', R(1500, BAR[0] - 600, 2400, BAR[0]), 'SMK-R3-BAR')
add('samovar', C(275, 9300, 210, 32), 'SMK-R3-BAR'); add('coffee', R(60, 10200, 500, 10900), 'SMK-R3-BAR')
add('sink', R(80, 12900, 480, 13400), 'SMK-R3-BAR')
add('barsteps', R(550, 14300, 1500, 15300), 'SMK-R3-STEPS')
y = BAR[0] + 400
while y + 200 <= BAR[1] - 100:
    add('stool', C(2780, y, 200, 28), 'SMK-R3-BAR'); seat('bar', 1); y += 620
# BBQ / mangal kitchen — orthogonal block 3.2 x 6.1
BX0, BX1, BY0, BY1 = 8100, 11300, 3700, 9800
add('bbqfloor', R(BX0, BY0, BX1, BY1), 'SMK-R3-BBQ')
add('firewall', R(11150, BY0, BX1, BY1), 'SMK-R3-BBQ')
add('tandoorblock', R(10200, 3900, 11150, 5000), 'SMK-R3-BBQ'); add('tandoor', C(10675, 4450, 430), 'SMK-R3-BBQ')
add('mangal', R(10550, 5200, 11150, 7600), 'SMK-R3-BBQ')
add('kazanblock', R(10200, 7800, 11150, 8800), 'SMK-R3-BBQ'); add('kazan', C(10675, 8300, 380), 'SMK-R3-BBQ')
add('sinkbins', R(10550, 8950, 11150, 9700), 'SMK-R3-BBQ')
add('prep', R(BX0, 4600, BX0 + 650, 7300), 'SMK-R3-BBQ'); add('pass', R(BX0, 7300, BX0 + 650, BY1), 'SMK-R3-BBQ')
add('glass', R(BX0 - 40, 7300, BX0, BY1), 'SMK-R3-BBQ')
add('hood', R(10100, 3800, 11250, 9750), 'SMK-R3-BBQ')
bbq_plant = Polygon([(BX1, BY0 - 300), (xb(BY0 - 300), BY0 - 300), (xb(BY1 + 300), BY1 + 300), (BX1, BY1 + 300)]).intersection(U)
# chairs/tables helpers
def table_ns(cx, cy, key, tl=1200, tw=800):
    add('table', R(cx - tl / 2, cy - tw / 2, cx + tl / 2, cy + tw / 2))
    for sy in (-1, 1):
        for sx in (-tl / 4, tl / 4):
            y0 = cy + sy * (tw / 2 + 40); add('chair', R(cx + sx - 225, y0, cx + sx + 225, y0 + sy * 450), back=('n' if sy > 0 else 's'))
    seat(key, 4)
def table_ew(cx, cy, key, tl=1200, tw=800):
    add('table', R(cx - tw / 2, cy - tl / 2, cx + tw / 2, cy + tl / 2))
    for sx in (-1, 1):
        for sy in (-tl / 4, tl / 4):
            x0 = cx + sx * (tw / 2 + 40); add('chair', R(x0, cy + sy - 225, x0 + sx * 450, cy + sy + 225), back=('e' if sx > 0 else 'w'))
    seat(key, 4)
for cy in (6800, 9300):
    for cx in (5000, 7300):
        table_ns(cx, cy, 'south')
# chinar south: full round bench
def ring(c, r0, r1, a0=0, a1=360):
    an = C(c[0], c[1], r1, 96).difference(C(c[0], c[1], r0, 96))
    if a1 - a0 >= 360: return an
    return an.intersection(Polygon([c] + [(c[0] + 6000 * math.cos(math.radians(a)), c[1] + 6000 * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 5)]))
add('pit', C(*TREE_S, 1000), 'SMK-R3-TREE'); add('ringbench', ring(TREE_S, 1000, 1450), 'SMK-R3-TREE'); seat('chinar_s', 10)
# high tables facing the mangal + host + waiting bench
for cy in (11450, 13600):
    for cx in (8400, 10300):
        table_ns(cx, cy, 'plaza')
add('host', R(7550, 14650, 8150, 15200), 'SMK-R3-SERV')

# ======================= NORTH =======================
PLAT = R(0, 15300, 2400, 30900)
add('platform', PLAT, 'SMK-R3-STEPS')
add('stepsA', R(2400, ENT[0], 3300, ENT[1]), 'SMK-R3-STEPS')          # alley -> platform
add('stepsB', R(2400, 24300, 3300, 25800), 'SMK-R3-STEPS')            # staff, open D-E door
RAMP = R(0, 30900, 1300, 36540); add('ramp', RAMP, 'SMK-R3-STEPS')
RAIL = [((2400, ENT[1]), (2400, 24300)), ((2400, 25800), (2400, 30900)), ((1300, 30900), (2400, 30900)), ((1300, 30900), (1300, 36540)), ((2400, 15300), (2400, ENT[0])), ((1500, 15300), (2400, 15300))]
for cy in (21350, 23400, 26900):
    table_ew(1150, cy, 'platform')
add('station', R(1750, 30250, 2350, 30850), 'SMK-R3-SERV')
# booths: orthogonal, stepped with the boundary, 2.0 m module, depth 1.3
B_Y0, B_N, B_W, B_D = 18300, 9, 2000, 1300
booth_west = []
for k in range(B_N):
    y0, y1 = B_Y0 + k * B_W, B_Y0 + (k + 1) * B_W
    xe = xi(y1); xw = xe - B_D; booth_west.append((y0, y1, xw))
    add('rug', R(xw, y0 + 60, xe, y1))
    add('screen', R(xw, y0, xe, y0 + 60))
    add('bench', R(xw + 80, y0 + 100, xe - 60, y0 + 580))
    add('btable', R(xw + 150, y0 + 650, xe - 150, y1 - 650))
    add('bench', R(xw + 80, y1 - 580, xe - 60, y1 - 100))
    add('lantern', C((xw + xe) / 2, (y0 + y1) / 2, 150, 20))
    add('sliver', Polygon([(xe, y0), (xi(y0), y0), (xi(y1), y1), (xe, y1)]))
    seat('booths', 4)
add('screen', R(booth_west[-1][2], B_Y0 + B_N * B_W, xi(B_Y0 + B_N * B_W), B_Y0 + B_N * B_W + 60))
# north dining: two columns of 4-tops on a 2.5 m pitch
for cy, cols_ in ((19300, (4300, 6600)), (21600, (4300, 6600)), (23900, (4300, 6600))):
    for cx in cols_: table_ns(cx, cy, 'north')
table_ew(3400, 27150, 'north')
# chinar north: bench open to the path
add('pit', C(*TREE_N, 1000), 'SMK-R3-TREE'); add('ringbench', ring(TREE_N, 1000, 1450, 120, 290), 'SMK-R3-TREE'); seat('chinar_n', 6)
# tapchans along an aryk with a small hauz (Lyabi-Hauz motif)
for y0 in (28700, 30600, 32500, 34400):
    add('tapchan', R(2450, y0, 4450, y0 + 1800)); add('tapchanrug', R(2600, y0 + 150, 4300, y0 + 1650)); add('tapchantable', R(3000, y0 + 500, 3900, y0 + 1300))
    seat('tapchans', 6)
add('aryk', R(4780, 28900, 5080, 36100), 'SMK-R3-TREE')
hz = Polygon([(4930 + 650 * math.cos(math.radians(22.5 + 45 * i)), 32700 + 650 * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)])
add('hauzborder', hz.buffer(200, join_style=2), 'SMK-R3-TREE'); add('hauz', hz, 'SMK-R3-TREE')

# ======================= ROOF =======================
TRUSS_Y = [4100, 9850, 16800, 21350, 25600, 29100, 32100, 36300]
COL_E = [4100, 9850, 15300, 18300, 21350, 25600, 29100, 32100, 36300]
cols = [(xb(y) - 750, y) for y in COL_E] + [(-7050, 200), (-350, 250)]

# ======================= ZONES (for areas, labels) =======================
ALLEY = R(3300, ENT[0], xi(ENT[1]), ENT[1])
FLOOR = U.difference(planter)
zones = {'kids': KIDS, 'photo': R(1000, 2000, 5800, 4700), 'service': R(0, 4250, 2080, 8400), 'bar': R(0, 8000, 3000, 15300),
         'bbq': R(BX0, BY0, BX1, BY1), 'alley': ALLEY, 'platform': PLAT, 'booths': unary_union([R(w, a, xi(b), b) for a, b, w in booth_west]),
         'tapchan': R(2450, 28700, 5100, 36200)}
zone_m2 = {k: round(v.area / 1e6, 1) for k, v in zones.items()}

# ======================= CHECKS =======================
probs = []
FURN = ('table', 'chair', 'btable', 'bench', 'tapchan', 'stool', 'hightable', 'station', 'host', 'ringbench', 'shelving', 'counter')
solid = [it for it in items if it['kind'] in FURN]
okfloor = FLOOR.union(PLAT).buffer(5)
door_clear = [R(0, a, 1500, b) for a, b, op in DOORS.values() if op]
pits = [C(*TREE_N, 1000), C(*TREE_S, 1000)]
blocked = unary_union([RAMP, R(2400, ENT[0], 3300, ENT[1]), R(2400, 24300, 3300, 25800), R(550, 14300, 1500, 15300)])
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
        if a.intersection(b).area > 1500 and {solid[i]['kind'], solid[j]['kind']} not in ({'table', 'chair'}, {'btable', 'bench'}):
            probs.append(f"overlap {solid[i]['kind']}/{solid[j]['kind']} @ {a.centroid.x:.0f},{a.centroid.y:.0f}")
# clear path in front of the booths
west = unary_union([it['geom'] for it in solid if it['geom'].centroid.y > ENT[1] and it['geom'].bounds[2] < 7800] + [C(*TREE_N, 1000)])
pmin = 1e9
for a, b, xw in booth_west:
    for yy in range(int(a) + 50, int(b), 100):
        hit = LineString([(xw - 4000, yy), (xw, yy)]).intersection(west)
        xe = max([p[0] for g in getattr(hit, 'geoms', [hit]) for p in getattr(g, 'coords', [])] or [xw - 4000])
        pmin = min(pmin, xw - xe)
total = sum(seats.values())
res = dict(seats=seats, total=total, zones_m2=zone_m2, path_min=round(pmin), problems=probs, entrance_width=ENT[1] - ENT[0])
print(json.dumps(res, indent=1, ensure_ascii=False))

def coords(g):
    return [[(round(x, 1), round(y, 1)) for x, y in p.exterior.coords] for p in getattr(g, 'geoms', [g]) if not p.is_empty]
json.dump(dict(res, columns=cols, truss_y=TRUSS_Y, items=[dict(kind=i['kind'], layer=i['layer'], poly=coords(i['geom'])) for i in items]), open(f'{OUT}/samarkand-terrace-layout-R4.json', 'w'), ensure_ascii=False)
doc = ezdxf.readfile(BASE_DXF); msp = doc.modelspace()
for lay, col in (('SMK-R3-FURN', 7), ('SMK-R3-BAR', 40), ('SMK-R3-BBQ', 30), ('SMK-R3-PHOTO', 5), ('SMK-R3-SERV', 4), ('SMK-R3-TREE', 3), ('SMK-R3-STEPS', 8), ('SMK-R3-ROOF', 34), ('SMK-R3-PLANT', 3)):
    if lay not in doc.layers: doc.layers.add(lay, color=col)
for it in items:
    for p in coords(it['geom']): msp.add_lwpolyline(p[:-1], close=True, dxfattribs={'layer': it['layer']})
for p in coords(planter): msp.add_lwpolyline(p[:-1], close=True, dxfattribs={'layer': 'SMK-R3-PLANT'})
for a, b in RAIL: msp.add_line(a, b, dxfattribs={'layer': 'SMK-R3-STEPS'})
for c in cols: msp.add_lwpolyline(list(R(c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150).exterior.coords)[:-1], close=True, dxfattribs={'layer': 'SMK-R3-ROOF'})
for yy in TRUSS_Y: msp.add_line((0, yy), (xb(yy) - 750, yy), dxfattribs={'layer': 'SMK-R3-ROOF'})
for c in (TREE_N, TREE_S): msp.add_circle(c, 1400, dxfattribs={'layer': 'SMK-R3-ROOF'})
doc.saveas(f'{OUT}/samarkand-terrace-layout-R4.dxf')

# ======================= SVG =======================
T = {
 'ru': dict(sub='Крытая терраса  ·  планировка R4', cuisine='Таджикская и узбекская кухня  ·  Võ Nguyên Giáp, 254, Дананг',
            hall='ОСНОВНОЙ ЗАЛ  ·  ±0.000', drive='ПОДЪЕЗД 8% → ПАРКОВКА', street='УЛ. ВÕ NGUYÊN GIÁP  ·  15 М  ·  → МОРЕ',
            zones='ЗОНЫ', seats='ПОСАДКА', total='Итого мест', key='ОБОЗНАЧЕНИЯ', bbq_t='МАНГАЛЬНАЯ  ·  1:100',
            L=[('Главный вход с улицы', 'проём 2,5 м, хостес'), ('Аллея', 'орнамент-гирих, 2,5 м, к дверям зала'),
               ('Айван-платформа ±0.000', 'бывшие ступени, 3 стола, перила'), ('Кабинки с видом на море', '9 кабинок, резные ширмы, фонари'),
               ('Чинар-дворик (север)', 'дерево сохранено, круглая скамья'), ('Топчаны у арыка и хауза', '4 топчана, вода, тень'),
               ('Северный вход + пандус 1:12', 'с парковки, без ступеней'), ('Бар', 'чай, самовар, кофе · 9 стульев'),
               ('Станция персонала', 'стеллажи, касса, вода, лёд, посуда'), ('Зал юг', '4 стола на 4'),
               ('Чинар-дворик (юг)', 'скамья вокруг дерева + 4 стола на 4'), ('Мангальная', 'тандыр · мангал · казан · заготовка · раздача'),
               ('Фотозона', 'пештак с майоликой, медальон, точка съёмки'), ('Детская зона', 'ограждение, мягкое покрытие'), ('Зал север', '7 столов на 4')],
            S={'platform': 'Айван-платформа', 'booths': 'Кабинки у моря', 'north': 'Зал север', 'chinar_n': 'Скамья у чинара (север)', 'tapchans': 'Топчаны',
               'bar': 'Барная стойка', 'south': 'Зал юг', 'chinar_s': 'Скамья у чинара (юг)', 'plaza': 'Столы у входа (под чинарой)'},
            K=['Колонна навеса (сталь, обшивка деревом)', 'Линия фермы навеса', 'Вход гостей', 'Маршрут персонала', 'Дверь зала открыта', 'Дверь зала закрыта', 'Вытяжной зонт'],
            bbqL=['Тандыр Ø900', 'Мангал 2,4 м, угли', 'Казан Ø800, газ', 'Мойка, уголь, зола', 'Заготовка, холодильники', 'Раздача, подогрев, лепёшки', 'Кирпичная огнестойкая стена'],
            bbqN=['Проход повара 1,45–1,65 м · зонт и труба выше кровли', 'Огнетушитель, отсекатель газа, трап, сланец'],
            notes=['Основа: исполнительный чертёж DWG (Long House, 10.07.2024) в масштабе 1:1. Отметки: терраса −0.470, платформа и зал ±0.000.',
                   'Навес: стальные фермы по сетке осей, колонны спрятаны в озеленении у улицы, у фасада опорная балка (проверка инженером).',
                   'Внутри обеденной зоны колонн нет. Деревья сохранены и проходят через проёмы в кровле Ø2,8 м.',
                   'Одна дверь D–E закрыта (перед ней стол). Северная дверь D–E и задняя дверь у лифта выходят на платформу.'],
            foot='Концепция для согласования с заказчиком · размеры уточнить на месте', ph='ФОТОЗОНА', barlbl='БАР', ent='ВХОД', scale='Масштаб 1:150 · A3',
            lv_t='терраса −0.470', lv_p='±0.000'),
 'en': dict(sub='Covered terrace  ·  Layout R4', cuisine='Tajik & Uzbek national cuisine  ·  254 Võ Nguyên Giáp, Đà Nẵng',
            hall='MAIN HALL  ·  ±0.000', drive='DRIVEWAY 8% → PARKING', street='VÕ NGUYÊN GIÁP  ·  15 M  ·  → SEA',
            zones='ZONES', seats='SEATS', total='Total seats', key='KEY', bbq_t='MANGAL KITCHEN  ·  1:100',
            L=[('Street entrance', '2.5 m opening, host'), ('Alley', 'girih paving, 2.5 m, to the hall doors'),
               ('Aivan platform ±0.000', 'former steps, 3 tables, rail'), ('Sea-view booths', '9 booths, carved screens, lanterns'),
               ('Chinar court north', 'tree kept, round bench'), ('Tapchans by the aryk & hauz', '4 tapchans, water, shade'),
               ('North entrance + ramp 1:12', 'from parking, step-free'), ('Bar', 'tea, samovar, coffee · 9 stools'),
               ('Staff station', 'shelving, POS, water, ice, dishes'), ('Dining south', '4 tables for 4'),
               ('Chinar court south', 'round bench + 4 tables for 4'), ('Mangal kitchen', 'tandoor · mangal · kazan · prep · pass'),
               ('Photo zone', 'majolica pishtaq, medallion, photo spot'), ('Kids zone', 'fenced, soft floor'), ('Dining north', '7 tables for 4')],
            S={'platform': 'Aivan platform', 'booths': 'Sea-view booths', 'north': 'Dining north', 'chinar_n': 'Chinar bench north', 'tapchans': 'Tapchans',
               'bar': 'Bar counter', 'south': 'Dining south', 'chinar_s': 'Chinar bench south', 'plaza': 'Tables at the entrance'},
            K=['Roof column (steel, wood-clad)', 'Roof truss line', 'Guest entrance', 'Staff route', 'Hall door, open', 'Hall door, closed', 'Exhaust hood'],
            bbqL=['Tandoor Ø900', 'Mangal 2.4 m, charcoal', 'Kazan Ø800, gas', 'Sink, charcoal, ash', 'Cold prep, fridges', 'Pass, heat lamps, bread', 'Brick fire wall'],
            bbqN=['Cook aisle 1.45–1.65 m · hood + stack above the roof', 'Extinguisher, gas shut-off, floor drain, slate'],
            notes=['Base: as-built DWG (Long House, 10-07-2024) at 1:1. Levels: terrace −0.470, platform and hall ±0.000.',
                   'Roof: steel trusses on the building grid, columns hidden in the street planters, ledger on the façade (engineer to confirm).',
                   'No columns inside the dining. Trees kept, growing through Ø2.8 m roof oculi.',
                   'One D–E door stays closed (table in front). The D–E north door and the back door by the lift open onto the platform.'],
            foot='Concept for client review · dimensions to verify on site', ph='PHOTO ZONE', barlbl='BAR', ent='ENTRANCE', scale='Scale 1:150 · A3',
            lv_t='terrace −0.470', lv_p='±0.000')}

S_ = 150.0; PX0, PY0 = 14.0, 62.0; XMIN, YMAX = -8600.0, 39400.0
def P(x, y): return (PX0 + (x - XMIN) / S_, PY0 + (YMAX - y) / S_)
OX, OY = P(0, 0)
def d_of(g):
    out = []
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty: continue
        out.append('M' + 'L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in p.exterior.coords) + 'Z')
        for r in p.interiors: out.append('M' + 'L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in r.coords) + 'Z')
    return ''.join(out)

def tile_pat(pid, size_mm, body, bg):
    s = size_mm / S_
    return f'<pattern id="{pid}" x="{OX % s:.3f}" y="{OY % s:.3f}" width="{s:.3f}" height="{s:.3f}" patternUnits="userSpaceOnUse"><rect width="{s:.3f}" height="{s:.3f}" fill="{bg}"/>{body(s)}</pattern>'
def terr(s):  # 600 tiles, grout + small terracotta cabochon at corners
    c = s * .16
    return (f'<path d="M0 0H{s:.3f}M0 0V{s:.3f}" stroke="#d5c09c" stroke-width=".14"/>'
            f'<path d="M0 {-c:.3f}L{c:.3f} 0L0 {c:.3f}L{-c:.3f} 0Z" fill="#b5653a"/><path d="M{s:.3f} {-c:.3f}L{s + c:.3f} 0L{s:.3f} {c:.3f}L{s - c:.3f} 0Z" fill="#b5653a"/>'
            f'<path d="M0 {s - c:.3f}L{c:.3f} {s:.3f}L0 {s + c:.3f}L{-c:.3f} {s:.3f}Z" fill="#b5653a"/><path d="M{s:.3f} {s - c:.3f}L{s + c:.3f} {s:.3f}L{s:.3f} {s + c:.3f}L{s - c:.3f} {s:.3f}Z" fill="#b5653a"/>')
def girih(s):
    h = s / 2; a = s * .26
    sq = f'<rect x="{h - a:.3f}" y="{h - a:.3f}" width="{2 * a:.3f}" height="{2 * a:.3f}" fill="#1F3F8A"/>'
    return (f'<path d="M0 0H{s:.3f}M0 0V{s:.3f}" stroke="#a4643c" stroke-width=".14"/>{sq}'
            f'<rect x="{h - a:.3f}" y="{h - a:.3f}" width="{2 * a:.3f}" height="{2 * a:.3f}" fill="#1F3F8A" transform="rotate(45 {h:.3f} {h:.3f})"/>'
            f'<circle cx="{h:.3f}" cy="{h:.3f}" r="{s * .11:.3f}" fill="#2A9DA8"/><circle cx="{h:.3f}" cy="{h:.3f}" r="{s * .05:.3f}" fill="#efe6d8"/>')
def slate(s): return f'<path d="M0 0H{s:.3f}M0 0V{s:.3f}" stroke="#5f5b56" stroke-width=".14"/>'
def rubber(s): h = s / 2; return f'<rect width="{h:.3f}" height="{h:.3f}" fill="#f6c25a"/><rect x="{h:.3f}" y="{h:.3f}" width="{h:.3f}" height="{h:.3f}" fill="#f6c25a"/><path d="M0 0H{s:.3f}M0 0V{s:.3f}" stroke="#e0a83e" stroke-width=".1"/>'
deck_s = 150 / S_
DEFS = ('<defs>' + tile_pat('terr', 600, terr, '#efe1c6') + tile_pat('alley', 600, girih, '#c98b62') + tile_pat('slate', 600, slate, '#7a756e') + tile_pat('rubber', 500, rubber, '#ffd978') +
        f'<pattern id="deck" x="{OX % (2400 / S_):.3f}" y="{OY % deck_s:.3f}" width="{deck_s:.3f}" height="{2400 / S_:.3f}" patternUnits="userSpaceOnUse"><rect width="{deck_s:.3f}" height="{2400 / S_:.3f}" fill="#c69c6d"/><path d="M{deck_s:.3f} 0V{2400 / S_:.3f}M0 {1200 / S_:.3f}H{deck_s / 2:.3f}" stroke="#9b7148" stroke-width=".1"/></pattern>'
        '<pattern id="ikat" width="2.4" height="2.4" patternUnits="userSpaceOnUse"><rect width="2.4" height="2.4" fill="#8E1F24"/><path d="M1.2 .25L1.95 1.2L1.2 2.15L.45 1.2Z" fill="#d9a23a"/><path d="M1.2 .8L1.5 1.2L1.2 1.6L.9 1.2Z" fill="#1F3F8A"/></pattern>'
        '<pattern id="suzani" width="3.2" height="3.2" patternUnits="userSpaceOnUse"><rect width="3.2" height="3.2" fill="#f1e5d0"/><circle cx="1.6" cy="1.6" r=".95" fill="#b8323a"/><circle cx="1.6" cy="1.6" r=".42" fill="#d9a23a"/><circle cx="0" cy="0" r=".4" fill="#2a6f4a"/><circle cx="3.2" cy="0" r=".4" fill="#2a6f4a"/><circle cx="0" cy="3.2" r=".4" fill="#2a6f4a"/><circle cx="3.2" cy="3.2" r=".4" fill="#2a6f4a"/></pattern>'
        '<pattern id="majolica" width="1.8" height="1.8" patternUnits="userSpaceOnUse"><rect width="1.8" height="1.8" fill="#1F3F8A"/><path d="M.9 .15L1.15 .65L1.65 .9L1.15 1.15L.9 1.65L.65 1.15L.15 .9L.65 .65Z" fill="#2A9DA8"/><circle cx=".9" cy=".9" r=".2" fill="#efe6d8"/></pattern>'
        '<pattern id="lattice" width=".9" height=".9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width=".9" height=".9" fill="#4a2f1c"/><rect x=".22" y=".22" width=".46" height=".46" fill="#9a6a40"/></pattern>'
        '<pattern id="hatch" width="2" height="2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="2" height="2" fill="#e6e0d6"/><path d="M0 0V2" stroke="#d4ccbf" stroke-width=".22"/></pattern>'
        '<pattern id="green" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#a7c38a"/><circle cx="1.5" cy="1.6" r="1.25" fill="#8cb06b"/><circle cx="4.4" cy="4.1" r="1.5" fill="#7aa35c"/><circle cx="1.9" cy="4.8" r=".8" fill="#93b874"/><circle cx="4.9" cy="1.1" r=".75" fill="#6e9752"/></pattern>'
        '<radialGradient id="water" cx="45%" cy="40%" r="65%"><stop offset="0" stop-color="#c9eef4"/><stop offset="1" stop-color="#3a98b2"/></radialGradient>'
        '<radialGradient id="leaf" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#9cc86c"/><stop offset=".7" stop-color="#5f9442"/><stop offset="1" stop-color="#3f6e2c"/></radialGradient>'
        '<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ffd27a" stop-opacity=".95"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="brass" cx="40%" cy="35%" r="65%"><stop offset="0" stop-color="#f0d184"/><stop offset="1" stop-color="#a87a2a"/></radialGradient>'
        '<filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx=".3" dy=".4" stdDeviation=".3" flood-color="#2b1d12" flood-opacity=".32"/></filter>'
        '<filter id="tsh" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="1.2" dy="1.4" stdDeviation="1" flood-color="#1f2d14" flood-opacity=".35"/></filter>'
        '<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="#2e7d3a"/></marker>'
        '<marker id="arrS" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="#d9731a"/></marker>'
        '</defs>')

def build(lang):
    t = T[lang]; out = []
    def sh(g, fill='none', stroke='none', sw=.12, extra=''):
        out.append(f'<path d="{d_of(g)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" fill-rule="evenodd" {extra}/>')
    def ln(a, b, stroke, sw, extra=''):
        (x1, y1), (x2, y2) = P(*a), P(*b); out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
    def tx(x, y, s, size=2.2, fill='#3b2a1e', anchor='middle', weight=400, family='Inter', extra='', page=False):
        if not page: x, y = P(x, y)
        out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>')
    def num(x, y, n, page=False):
        if not page: x, y = P(x, y)
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.2" fill="#1F3F8A" stroke="#fbf6ec" stroke-width=".45"/><text x="{x:.2f}" y="{y + 1:.2f}" font-family="Inter" font-size="2.5" font-weight="700" fill="#fff" text-anchor="middle">{n}</text>')
    W, H = 297, 420
    out.append(f'<rect width="{W}" height="{H}" fill="#f7f1e6"/><rect x="7" y="7" width="{W - 14}" height="{H - 14}" fill="none" stroke="#5A3A22" stroke-width=".6"/><rect x="8.4" y="8.4" width="{W - 16.8}" height="{H - 16.8}" fill="none" stroke="#b8893a" stroke-width=".25"/>')
    # context: hall, street, driveway, lot line
    sh(R(XMIN + 300, 4100, 0, 37100), 'url(#hatch)')
    hx, hy = P(-4300, 21000); tx(hx, hy, t['hall'], 3.0, '#8a7f70', weight=600, page=True, extra=f'transform="rotate(-90 {hx:.2f} {hy:.2f})" letter-spacing=".7"')
    sx0, sx1 = P(14900, 0)[0], P(18600, 0)[0]
    out.append(f'<rect x="{sx0:.2f}" y="{PY0:.2f}" width="{sx1 - sx0:.2f}" height="{P(0, -2600)[1] - PY0:.2f}" fill="#d3d9dd"/>')
    mx, my = P(16900, 20000); tx(mx, my, t['street'], 2.8, '#5d6a74', weight=700, page=True, extra=f'transform="rotate(-90 {mx:.2f} {my:.2f})" letter-spacing=".8"')
    sh(Polygon([(0, yr(0)), (xb(36500), yr(xb(36500))), tuple(Z2), (0, V['Z1_NW'][1])]), '#dcd7ce')
    tx(4800, 38050, t['drive'], 2.0, '#8a8178', weight=600, extra='letter-spacing=".4"')
    out.append('<path d="M' + 'L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in L['LOT'][0] if -8600 < x < 15000 and -3000 < y < 39500) + '" fill="none" stroke="#c0392b" stroke-width=".3" stroke-dasharray="3 1 .6 1"/>')
    # floors
    sh(FLOOR, 'url(#terr)')
    sh(ALLEY, 'url(#alley)', '#7a4a2c', .2)
    sh(PLAT, 'url(#deck)', '#6b4429', .3)
    sh(KIDS, 'url(#rubber)', '#c98a1c', .3)
    sh(R(BX0, BY0, BX1, BY1), 'url(#slate)', '#3b2a1e', .25)
    sh(planter.union(photo_plant).union(bbq_plant), 'url(#green)', '#5f8a44', .2)
    for it in items:
        if it['kind'] == 'sliver': sh(it['geom'], 'url(#green)', 'none')
    # steps / ramp / rails
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
    for a_, b_ in RAIL: ln(a_, b_, '#3b2a1e', .5)
    # street stair 2.5 m
    xs0, xs1 = xi(ENT[0]) - 200, xb(ENT[0]) + 300
    sh(R(xs0, ENT[0], xs1, ENT[1]), '#d8c9ae', '#6b4429', .2)
    for j in range(1, 5): ln((xs0 + j * (xs1 - xs0) / 5, ENT[0]), (xs0 + j * (xs1 - xs0) / 5, ENT[1]), '#6b4429', .15)
    # doors
    for (a_, b_, op) in DOORS.values(): ln((-70, a_), (-70, b_), '#2A9DA8' if op else '#9a9a9a', .9)
    # --- objects
    def chair(g, back):
        sh(g, '#efe2c8', '#5a3a22', .1, 'filter="url(#sh)"')
        x0, y0, x1, y1 = g.bounds; bw = 90
        bb = {'n': R(x0, y1 - bw, x1, y1), 's': R(x0, y0, x1, y0 + bw), 'e': R(x1 - bw, y0, x1, y1), 'w': R(x0, y0, x0 + bw, y1)}[back]
        sh(bb, '#8a5a36')
    for it in items:
        k, g = it['kind'], it['geom']
        if k == 'chair': chair(g, it['back'])
    STY = {'table': ('#a87444', '#5a3a22', 'sh'), 'btable': ('#a87444', '#5a3a22', 'sh'), 'rug': ('#f0dfc2', 'none', ''), 'bench': ('url(#ikat)', '#3b2a1e', 'sh'),
           'screen': ('url(#lattice)', '#2b1d12', 'sh'), 'tapchan': ('#b88a58', '#5a3a22', 'sh'), 'tapchanrug': ('url(#suzani)', 'none', ''), 'tapchantable': ('#6b4429', '#3b2a1e', 'sh'),
           'stool': ('#8a5a36', '#3b2a1e', 'sh'), 'hightable': ('#a87444', '#5a3a22', 'sh'), 'station': ('#2A9DA8', '#1d6f77', ''), 'host': ('#2A9DA8', '#1d6f77', 'sh'),
           'backbar': ('#4a2f1c', '#2b1d12', 'sh'), 'barbody': ('#A4482B', '#5a2a18', 'sh'), 'bartop': ('#efe6d8', '#8a7f70', ''), 'barreturn': ('#efe6d8', '#8a7f70', 'sh'),
           'samovar': ('url(#brass)', '#7a5a1a', ''), 'coffee': ('#2f2f2f', '#111', ''), 'sink': ('#c9ccd0', '#6b6f73', ''),
           'shelving': ('url(#lattice)', '#2b1d12', 'sh'), 'counter': ('#c9ccd0', '#6b6f73', 'sh'), 'screenwall': ('#4a2f1c', 'none', ''),
           'firewall': ('#A4482B', '#5a2a18', ''), 'tandoorblock': ('#c98b62', '#5a3a22', 'sh'), 'tandoor': ('#7a3d22', '#3b1d10', ''), 'mangal': ('#333', '#111', 'sh'),
           'kazanblock': ('#9a9590', '#55524e', 'sh'), 'kazan': ('#1d1d1d', '#b8893a', ''), 'sinkbins': ('#c9ccd0', '#6b6f73', ''), 'prep': ('#d7dadd', '#6b6f73', 'sh'), 'pass': ('#e9ebed', '#6b6f73', 'sh'), 'glass': ('#bfe0ea', 'none', ''),
           'pishtaq': ('url(#majolica)', '#13285a', 'sh'), 'pishtaq_niche': ('#2A9DA8', '#13285a', ''), 'medallion': ('url(#majolica)', '#b8893a', ''), 'camera': ('#3b2a1e', 'none', ''),
           'pit': ('#6b5a48', '#4a3b2c', ''), 'ringbench': ('#9a6a40', '#4a2f1c', 'sh'), 'aryk': ('url(#water)', '#1F3F8A', ''), 'hauzborder': ('url(#majolica)', '#13285a', 'sh'), 'hauz': ('url(#water)', 'none', ''),
           'bench': ('url(#ikat)', '#3b2a1e', 'sh'), 'lantern': ('url(#glow)', 'none', '')}
    ORDER = ['rug', 'tapchan', 'tapchanrug', 'aryk', 'hauzborder', 'hauz', 'medallion', 'pit', 'ringbench', 'table', 'btable', 'bench', 'screen', 'tapchantable', 'stool', 'hightable', 'station', 'host',
             'backbar', 'barbody', 'bartop', 'barreturn', 'samovar', 'coffee', 'sink', 'shelving', 'counter', 'screenwall', 'firewall', 'tandoorblock', 'tandoor', 'mangal', 'kazanblock', 'kazan',
             'sinkbins', 'prep', 'pass', 'glass', 'pishtaq', 'pishtaq_niche', 'camera', 'lantern']
    for k in ORDER:
        for it in items:
            if it['kind'] == k:
                f, s_, fx = STY[k]; sh(it['geom'], f, s_, .14, 'filter="url(#sh)"' if fx else '')
    # details: bottles on the back bar, embers, tandoor rim, hood, pishtaq arch, camera spot
    for yy in range(9800, 12800, 260):
        if not (10150 < yy < 10950): out.append(f'<circle cx="{P(380, yy)[0]:.2f}" cy="{P(380, yy)[1]:.2f}" r=".45" fill="#2A9DA8" opacity=".85"/>')
    for f_ in (.15, .38, .62, .85):
        ln((10600, 5200 + 2400 * f_ - 120), (11100, 5200 + 2400 * f_ + 120), '#ec5a2a', .55)
    for c_, r_ in (((10675, 4450), 2.0), ((10675, 8300), 1.9)):
        cx, cy = P(*c_); out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r_}" fill="none" stroke="#d9a23a" stroke-width=".35"/>')
    sh(R(10100, 3800, 11250, 9750), 'none', '#8E1F24', .3, 'stroke-dasharray="1.2 .8"')
    ax_, ay_ = P(2650, 2180); bx_, by_ = P(3950, 2180); mx_, my_ = P(3300, 2000)
    out.append(f'<path d="M{ax_:.2f} {ay_:.2f}Q{ax_:.2f} {my_ - 1.8:.2f} {mx_:.2f} {my_ - 2.6:.2f}Q{bx_:.2f} {my_ - 1.8:.2f} {bx_:.2f} {by_:.2f}" fill="none" stroke="#d9a23a" stroke-width=".35"/>')
    cx, cy = P(3300, 5050); out.append(f'<path d="M{cx:.2f} {cy:.2f}L{cx - 2.2:.2f} {cy - 6.2:.2f}M{cx:.2f} {cy:.2f}L{cx + 2.2:.2f} {cy - 6.2:.2f}" stroke="#3b2a1e" stroke-width=".18" stroke-dasharray=".6 .5"/>')
    # play elements
    for g, c in ((R(-6800, 400, -4200, 1700), '#f39a5c'), (R(-3400, 2600, -900, 3700), '#7fc3d4'), (C(-5400, 3000, 550), '#9bd27f'), (C(-2200, 1100, 450), '#f3d35c')):
        sh(g, c, '#7a5a1a', .15, 'filter="url(#sh)"')
    # roof
    for yy in TRUSS_Y: ln((0, yy), (xb(yy) - 750, yy), '#5A3A22', .12, 'stroke-dasharray="2 1.2" opacity=".45"')
    for c in cols: sh(R(c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150), '#2b1d12')
    # trees: lobed canopy with shadow, highlights, oculus ring
    for c, r in ((TREE_N, 3200), (TREE_S, 3000)):
        lobes = unary_union([C(c[0], c[1], r * .72, 64)] + [C(c[0] + r * .52 * math.cos(math.radians(a)), c[1] + r * .52 * math.sin(math.radians(a)), r * .44, 48) for a in range(0, 360, 36)])
        sh(lobes, 'url(#leaf)', '#355e25', .3, 'opacity=".5" filter="url(#tsh)"')
        for a in range(18, 360, 72):
            g = C(c[0] + r * .35 * math.cos(math.radians(a)), c[1] + r * .35 * math.sin(math.radians(a)), r * .2, 32); sh(g, '#b4d987', 'none', 0, 'opacity=".28"')
        for a in range(0, 360, 45):
            ln(c, (c[0] + r * .62 * math.cos(math.radians(a)), c[1] + r * .62 * math.sin(math.radians(a))), '#3d5f2a', .18, 'opacity=".35"')
        cx, cy = P(*c); out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{1400 / S_:.2f}" fill="none" stroke="#fbf6ec" stroke-width=".3" stroke-dasharray="1 .7" opacity=".9"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{320 / S_:.2f}" fill="#5a4636"/>')
    # flows
    def arrow(pts_, color, sw, marker, dash=''):
        out.append(f'<path d="M' + 'L'.join(f'{P(x, y)[0]:.2f},{P(x, y)[1]:.2f}' for x, y in pts_) + f'" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#{marker})" {dash}/>')
    arrow([(17600, 16800), (xi(16800) - 300, 16800), (3700, 16800)], '#2e7d3a', .7, 'arr')
    arrow([(6800, 39000), (6800, 36700), (7000, 33500)], '#2e7d3a', .7, 'arr')
    arrow([(-600, 25050), (2850, 25050), (6500, 25050)], '#d9731a', .4, 'arrS', 'stroke-dasharray="1 .8"')
    arrow([(1000, 14800), (1000, 4700), (1000, 5250), (7700, 5250), (8000, 4200)], '#d9731a', .4, 'arrS', 'stroke-dasharray="1 .8"')
    # labels on the plan
    bx_, by_ = P(1800, 11450); tx(bx_ + .9, by_, t['barlbl'], 2.6, '#fbf6ec', weight=700, page=True, extra=f'transform="rotate(-90 {bx_ + .9:.2f} {by_:.2f})" letter-spacing="1.2"')
    tx(3300, 4600, t['ph'], 2.1, '#1F3F8A', weight=700, extra='letter-spacing=".6"')
    tx(xb(16800) + 1500, 17800, t['ent'], 2.2, '#2e7d3a', weight=700)
    for (x, y), s in (((-1500, 27000), t['lv_p']), ((3500, 15200), t['lv_t'])):
        X, Y = P(x, y); out.append(f'<path d="M{X:.2f} {Y:.2f}l-1 -1.5h2z" fill="#3b2a1e"/>'); tx(X + 1.4, Y - .2, s, 1.9, '#3b2a1e', anchor='start', weight=600, page=True)
    NUM = [(1, (9600, 16000)), (2, (5600, 16800)), (3, (1200, 19000)), (4, (xi(28300) - 650, 27300)), (5, (3400, 28430)), (6, (5700, 34200)), (7, (3600, 37200)),
           (8, (3400, 12600)), (9, (1000, 4700)), (10, (6150, 8050)), (11, (6000, 14400)), (12, (9600, 6700)), (13, (5300, 3300)), (14, (-3600, 2200)), (15, (5450, 20750))]
    for n, (x, y) in NUM: num(x, y, n)
    # scale bar, north
    sx, sy = 14, 352
    for k in range(5):
        out.append(f'<rect x="{sx + k * 1000 / S_:.2f}" y="{sy}" width="{1000 / S_:.2f}" height="1.2" fill="{"#3b2a1e" if k % 2 == 0 else "#f7f1e6"}" stroke="#3b2a1e" stroke-width=".15"/>')
    tx(sx, sy + 4.2, '0', 2.0, page=True, anchor='start'); tx(sx + 5000 / S_, sy + 4.2, '5 m' if lang == 'en' else '5 м', 2.0, page=True)
    tx(sx + 5000 / S_ + 4, sy + 1.2, t['scale'], 2.0, '#6b5a48', anchor='start', page=True)
    nx, ny = 150, 352; out.append(f'<path d="M{nx} {ny - 6}L{nx - 2.4} {ny + 2}L{nx} {ny + .6}L{nx + 2.4} {ny + 2}Z" fill="#3b2a1e"/>'); tx(nx, ny - 7.5, 'N' if lang == 'en' else 'С', 2.8, page=True, weight=700)
    # title
    tx(14, 26, 'SAMARKAND', 15, '#3b2a1e', anchor='start', family='Bitstream Charter', weight=700, page=True, extra='letter-spacing="2.5"')
    tx(14, 34.5, t['sub'], 5.0, '#8E1F24', anchor='start', family='Bitstream Charter', page=True)
    tx(14, 41, t['cuisine'], 3.0, '#6b5a48', anchor='start', page=True)
    out.append(f'<rect x="14" y="45" width="{W - 28}" height="1.6" fill="url(#majolica)"/>')
    # legend
    lx, ly = 203, 62
    tx(lx, ly, t['zones'], 3.0, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".6"')
    for i, (t1, t2) in enumerate(t['L']):
        yy = ly + 6 + i * 6.9; num(lx + 2.2, yy - .9, i + 1, page=True)
        tx(lx + 5.8, yy - .5, t1, 2.4, '#3b2a1e', anchor='start', weight=600, page=True); tx(lx + 5.8, yy + 2.3, t2, 1.95, '#6b5a48', anchor='start', page=True)
    sy0 = ly + 6 + len(t['L']) * 6.9 + 3
    tx(lx, sy0, t['seats'], 3.0, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".6"')
    for i, (k, v) in enumerate(seats.items()):
        tx(lx, sy0 + 5 + i * 4.0, t['S'][k], 2.2, '#3b2a1e', anchor='start', page=True); tx(W - 14, sy0 + 5 + i * 4.0, str(v), 2.2, '#3b2a1e', anchor='end', weight=600, page=True)
    yt = sy0 + 5 + len(seats) * 4.0 + 1
    out.append(f'<line x1="{lx}" y1="{yt - 2.6}" x2="{W - 14}" y2="{yt - 2.6}" stroke="#3b2a1e" stroke-width=".2"/>')
    tx(lx, yt + .6, t['total'], 2.7, '#8E1F24', anchor='start', weight=700, page=True); tx(W - 14, yt + .6, str(total), 3.2, '#8E1F24', anchor='end', weight=700, page=True)
    ky = yt + 8
    tx(lx, ky, t['key'], 3.0, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".6"')
    kinds = ['sq', 'dash', 'arr', 'dot', 'door', 'door2', 'hood']
    for i, (kind, s) in enumerate(zip(kinds, t['K'])):
        yy = ky + 4.3 + i * 3.9
        if kind == 'sq': out.append(f'<rect x="{lx}" y="{yy - 2}" width="2" height="2" fill="#2b1d12"/>')
        elif kind == 'arr': out.append(f'<line x1="{lx}" y1="{yy - 1}" x2="{lx + 5}" y2="{yy - 1}" stroke="#2e7d3a" stroke-width=".7" marker-end="url(#arr)"/>')
        elif kind in ('door', 'door2'): out.append(f'<line x1="{lx}" y1="{yy - 1}" x2="{lx + 5}" y2="{yy - 1}" stroke="{"#2A9DA8" if kind == "door" else "#9a9a9a"}" stroke-width=".9"/>')
        else: out.append(f'<line x1="{lx}" y1="{yy - 1}" x2="{lx + 5}" y2="{yy - 1}" stroke="{ {"dash": "#5A3A22", "dot": "#d9731a", "hood": "#8E1F24"}[kind]}" stroke-width=".4" stroke-dasharray="{"1 .8" if kind == "dot" else "1.6 .9"}"/>')
        tx(lx + 7, yy - .2, s, 2.1, '#3b2a1e', anchor='start', page=True)
    # mangal inset
    iy0 = ky + 4.3 + len(kinds) * 3.9 + 6; IS = 100.0
    tx(lx, iy0, t['bbq_t'], 3.0, '#3b2a1e', anchor='start', weight=700, page=True, extra='letter-spacing=".5"')
    def Pi(x, y): return (lx + (x - BX0) / IS, iy0 + 3 + (BY1 - y) / IS)
    def ish(g, f, s_='#3b2a1e', sw=.15, extra=''):
        for p in getattr(g, 'geoms', [g]):
            out.append(f'<path d="M' + 'L'.join(f'{Pi(x, y)[0]:.2f},{Pi(x, y)[1]:.2f}' for x, y in p.exterior.coords) + f'Z" fill="{f}" stroke="{s_}" stroke-width="{sw}" {extra}/>')
    ish(R(BX0, BY0, BX1, BY1), '#7a756e', '#3b2a1e', .25)
    for k in ('firewall', 'tandoorblock', 'tandoor', 'mangal', 'kazanblock', 'kazan', 'sinkbins', 'prep', 'pass', 'glass'):
        g = [i for i in items if i['kind'] == k][0]['geom']; f, s_, _ = STY[k]; ish(g, f, s_)
    ish(R(10100, 3800, 11250, 9750), 'none', '#8E1F24', .3, 'stroke-dasharray="1.2 .8"')
    labs = [('tandoor', 0), ('mangal', 1), ('kazan', 2), ('sinkbins', 3), ('prep', 4), ('pass', 5), ('firewall', 6)]
    ex = lx + (BX1 - BX0) / IS + 4
    for j, (k, li) in enumerate(sorted(labs, key=lambda q: -[i for i in items if i['kind'] == q[0]][0]['geom'].centroid.y)):
        g = [i for i in items if i['kind'] == k][0]['geom']; c = g.centroid; cx, cy = Pi(c.x, c.y); tyy = iy0 + 5 + j * 8.4
        out.append(f'<path d="M{cx:.2f} {cy:.2f}L{ex - 1:.2f} {tyy - .7:.2f}" stroke="#8a7f70" stroke-width=".15" fill="none"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r=".45" fill="#8E1F24"/>')
        tx(ex, tyy, t['bbqL'][li], 2.0, '#3b2a1e', anchor='start', page=True)
    for j, s in enumerate(t['bbqN']): tx(lx, iy0 + 3 + (BY1 - BY0) / IS + 5 + j * 3.4, s, 1.9, '#6b5a48', anchor='start', page=True)
    # notes + footer
    for i, s in enumerate(t['notes']): tx(14, 370 + i * 4.3, s, 2.1, '#4b3a2e', anchor='start', page=True)
    out.append(f'<rect x="14" y="{H - 22}" width="{W - 28}" height="1.2" fill="url(#majolica)"/>')
    tx(14, H - 14.5, 'SAMARKAND  ·  R4  ·  2026-10-22', 2.3, '#3b2a1e', anchor='start', weight=600, page=True)
    tx(W / 2, H - 14.5, t['foot'], 2.1, '#6b5a48', page=True)
    tx(W - 14, H - 14.5, 'designed by Nomad Group', 1.9, '#8a7f70', anchor='end', page=True, extra='font-style="italic" letter-spacing=".3"')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">{DEFS}{"".join(out)}</svg>'

for lang in ('ru', 'en'):
    open(f'{OUT}/samarkand-terrace-layout-R4-{lang}.svg', 'w').write(build(lang))
print('svg ok')
