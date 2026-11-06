"""Samarkand terrace — roof concept R7: plan 1:150 + two sections 1:100 (A3 portrait, RU/EN) + roof quantities JSON.
Runs layout_r12.py for the geometry. Args: zone.json base.dxf outdir
"""
import sys, json, math, runpy
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union

argv = sys.argv[:]
sys.argv = ['layout_r12.py'] + argv[1:4]
G = runpy.run_path(__file__.replace('roof_r12.py', 'layout_r12.py'))
sys.argv = argv
OUT = argv[3]
U, xb, xi, R, C = G['U'], G['xb'], G['xi'], G['R'], G['C']
COURT_S, COURT_N, BEAMS = G['COURT_S'], G['COURT_N'], G['TRUSS_Y']
TREE_N, TREE_S = G['TREE_N'], G['TREE_S']
DOMES, ZR = G['DOMES'], G['DOME_RING']
REV, DATE = G['REV'], G['DATE']

# ---------------- roof geometry (mm, local) ----------------
SOFFIT = 3850                 # F2 balcony slab soffit
TOP0 = 3750                   # top of roof skin at the façade (100 below the soffit)
FALL = 0.05                   # 5% to the street
PANEL, PURLIN, BEAM = 50, 200, 300
EAVE_OUT = 300                # overhang past the lot line? no: gutter sits inside -> roof edge = lot line
roof_all = U.buffer(0)
FOOT = unary_union([C(*d['c'], d['r'], 96) for d in DOMES])          # roof panel stops at the dome rings
roof = roof_all.difference(FOOT)
cols = [(xb(y) - 750, y) for y in BEAMS] + [(-7050, 200), (-350, 250)]
def top(x): return TOP0 - FALL * x
def dz(d, rho):                             # dome surface: ellipsoid of revolution, springing at ZR
    return ZR + d['rise'] * math.sqrt(max(0.0, 1 - (rho / d['r']) ** 2))
def dome_area(d):                           # numeric surface area of the shell between the oculus/lantern and the ring
    r0 = d['oc'] or d.get('lantern', 0); n = 200; A = 0
    for i in range(n):
        a, b = r0 + (d['r'] - r0) * i / n, r0 + (d['r'] - r0) * (i + 1) / n
        A += math.pi * (a + b) * math.hypot(b - a, dz(d, b) - dz(d, a))
    return A
def drum_area(d):                           # drum between the sloping roof skin and the level ring
    return sum((ZR - top(d['c'][0] + d['r'] * math.cos(2 * math.pi * k / 72))) * 2 * math.pi * d['r'] / 72 for k in range(72))
q = dict(roof_m2=round(roof.area / 1e6, 1), courts_m2=round((COURT_S.area + COURT_N.area) / 1e6, 1),
         beams_m=round(sum(xb(y) for y in BEAMS) / 1000, 1), n_cols=len(cols),
         gutter_street_m=round(LineString([(xb(0), 0), (xb(37000), 37000)]).length / 1000, 1),
         gutter_courts_m=round((COURT_S.length + COURT_N.length) / 1000, 1),
         domes=[dict(key=d['key'], d_m=2 * d['r'] / 1000, oculus_m=2 * d['oc'] / 1000, top=round(dz(d, d['oc'] or 0) + (600 if not d['oc'] else 0)),
                     shell_m2=round(dome_area(d) / 1e6, 1), drum_m2=round(drum_area(d) / 1e6, 1), ribs_m=round(12 * math.hypot(d['r'] - (d['oc'] or d.get('lantern', 0)), d['rise']) * 1.08 / 1000, 1),
                     ring_m=round(2 * math.pi * (d['r'] + d['oc']) / 1000, 1)) for d in DOMES],
         ledger_m=37.1, eave_top=round(top(xb(20000))), eave_clear=round(top(xb(20000) - 750) - PANEL - PURLIN - BEAM + 450))
# purlins @1200 parallel to the façade
purl = []
for k in range(1, 14):
    x = k * 1000 - 200
    ln_ = LineString([(x, -2000), (x, 40000)]).intersection(roof)
    for g in getattr(ln_, 'geoms', [ln_]):
        if g.length > 0: purl.append(g)
q['purlins_m'] = round(sum(g.length for g in purl) / 1000, 1)
json.dump(q, open(f'{OUT}/samarkand-roof-{REV}.json', 'w'))
print(json.dumps(q))

T = {'ru': dict(t1='Навес · концепция кровли', sub='План кровли 1:200 · разрезы 1:100', A='РАЗРЕЗ 1–1 (по оси D, через центральный купол)', B='РАЗРЕЗ 2–2 (через южный купол с чинаром)',
                plan='ПЛАН КРОВЛИ', court='открыто к небу', dome='купол Ø{d:.1f} · окулус Ø{o:.1f}', dome_c='купол Ø{d:.1f} · фонарь', oc='окулус', fall='5%', gutter='желоб', hall='ЗАЛ', street='ТРОТУАР', ul='ул. Võ Nguyên Giáp',
                spec='РЕШЕНИЕ', S=['Балки: сталь, оцинковка + порошковая краска «тёмная бронза», по линиям колонн, шаг 3,0–5,75 м',
                                    'Опора у фасада: опорный уголок/швеллер на анкерах под плитой балкона (низ плиты +3.850)',
                                    'Опора у улицы: 9 колонн 150×150 в стенке клумбы, обшивка деревом; оголовок +2.9',
                                    'Прогоны С200 шаг 1,2 м; сэндвич-панель PU 50 мм с нижним слоем «под дерево»',
                                    'Уклон 5% к улице; коробчатый желоб вдоль улицы, водостоки внутри колонн → дренаж клумб',
                                    'Купола: над чинарами Ø6,0 и Ø4,4 с открытым окулусом Ø3,6 / Ø2,4 (крона выходит наружу, дождь — в приствольную яму), между ними глухой Ø5,6 с остеклённым фонарём',
                                    'Купол: 12 гнутых рёбер 100×50 на опорном кольце +3.900, барабан с джали-окнами (свет + вытяжка горячего воздуха), внутри ГРЦ-панели «кирпич-гирих», снаружи терракотовое покрытие по мембране',
                                    'Деревянная реечная подшивка — только над баром и коридором (акцент)',
                                    'Волна-ламели под балконом демонтируются; фасад 2-го этажа остаётся открытым',
                                    'Тайфун: ветровой район II, анкеровка на отрыв; расчёт — инженер-конструктор'],
                qt='ОБЪЁМЫ', Q=[('Площадь кровли', 'roof_m2', 'м²'), ('Окулусы (открыто)', 'courts_m2', 'м²'), ('Балки (пог. м)', 'beams_m', 'м'),
                                  ('Прогоны (пог. м)', 'purlins_m', 'м'), ('Колонны', 'n_cols', 'шт'), ('Желоб улица / дворики', None, 'м')],
                lv='отм.', clear='в свету', foot='Концепция · сечения и узлы подтверждает расчёт конструктора'),
     'en': dict(t1='Terrace roof · concept', sub='Roof plan 1:200 · sections 1:100', A='SECTION 1–1 (on axis D, through the central dome)', B='SECTION 2–2 (through the south chinar dome)',
                plan='ROOF PLAN', court='open to the sky', dome='dome Ø{d:.1f} · oculus Ø{o:.1f}', dome_c='dome Ø{d:.1f} · lantern', oc='oculus', fall='5%', gutter='gutter', hall='HALL', street='SIDEWALK', ul='Võ Nguyên Giáp',
                spec='SOLUTION', S=['Beams: galvanised steel, dark-bronze powder coat, on the column lines at 3.0–5.75 m',
                                    'Façade bearing: steel ledger on anchors under the balcony slab (soffit +3.850)',
                                    'Street bearing: 9 columns 150×150 in the planter wall, wood-clad; cap +2.9',
                                    'C200 purlins at 1.2 m; 50 mm PU sandwich panel with a wood-look underside',
                                    '5% fall to the street; box gutter along the street, downpipes inside the columns → planter drain',
                                    'Domes: over the chinars Ø6.0 and Ø4.4 with an open oculus Ø3.6 / Ø2.4 (the crown grows out, rain falls into the tree pit); a closed Ø5.6 dome with a glazed lantern between them',
                                    'Dome: 12 bent ribs 100×50 on a level ring at +3.900, drum with jali windows (light + hot-air exhaust), GRC girih brick-slip panels inside, terracotta skin on a membrane outside',
                                    'Timber slat ceiling only over the bar and the corridor (accent)',
                                    'Wave louvers under the balcony removed; the F2 façade stays open',
                                    'Typhoon: wind zone II, uplift anchorage; structural engineer to calculate'],
                qt='QUANTITIES', Q=[('Roof area', 'roof_m2', 'm²'), ('Oculi (open)', 'courts_m2', 'm²'), ('Beams (lin. m)', 'beams_m', 'm'),
                                    ('Purlins (lin. m)', 'purlins_m', 'm'), ('Columns', 'n_cols', 'pcs'), ('Gutter street / courts', None, 'm')],
                lv='lvl', clear='clear', foot='Concept · member sizes and connections per the structural engineer')}

W, H = 297, 420
S1 = 200.0; X0, Y1 = -3600.0, 38400.0; PX, PY = 16.0, 66.0
def P(x, y): return (PX + (x - X0) / S1, PY + (Y1 - y) / S1)

def build(lang):
    t = T[lang]; o = []
    def path(g, fill, st='none', sw=.15, extra='', M=P):
        for p in getattr(g, 'geoms', [g]):
            if p.is_empty: continue
            o.append('<path d="M' + 'L'.join(f'{M(x, y)[0]:.2f},{M(x, y)[1]:.2f}' for x, y in p.exterior.coords) + 'Z' +
                     ''.join('M' + 'L'.join(f'{M(x, y)[0]:.2f},{M(x, y)[1]:.2f}' for x, y in r.coords) + 'Z' for r in p.interiors) +
                     f'" fill="{fill}" stroke="{st}" stroke-width="{sw}" fill-rule="evenodd" {extra}/>')
    def ln(a, b, st, sw, extra='', M=P):
        (x1, y1), (x2, y2) = M(*a), M(*b); o.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{st}" stroke-width="{sw}" {extra}/>')
    def tx(x, y, s, size=2.2, fill='#3b2a1e', anchor='start', weight=400, extra='', family='Inter'):
        o.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>')
    o.append(f'<rect width="{W}" height="{H}" fill="#f7f1e6"/><rect x="7" y="7" width="{W - 14}" height="{H - 14}" fill="none" stroke="#5A3A22" stroke-width=".6"/>')
    tx(14, 24, 'SAMARKAND', 12, weight=700, family='Bitstream Charter', extra='letter-spacing="2"')
    tx(14, 32, t['t1'], 4.6, '#8E1F24', family='Bitstream Charter'); tx(14, 38, t['sub'], 2.6, '#6b5a48')
    tx(W - 14, 24, REV, 10, '#d9c9ad', 'end', 700, family='Bitstream Charter'); tx(W - 14, 32, DATE, 2.6, '#6b5a48', 'end')
    o.append(f'<rect x="14" y="42" width="{W - 28}" height="1.2" fill="#1F3F8A"/>')
    # ---------- plan
    tx(14, 52, t['plan'] + '  ·  1:200', 2.8, weight=700, extra='letter-spacing=".5"')
    path(R(-2800, 4100, 0, 37100), '#e6e0d6', '#9a8f80', .15)
    roof_v = roof.intersection(R(-2800, -3000, 20000, 40000))
    tx(P(-1400, 22000)[0], P(-1400, 22000)[1], t['hall'], 2.6, '#9a8f80', 'middle', 700, f'transform="rotate(-90 {P(-1400, 22000)[0]:.2f} {P(-1400, 22000)[1]:.2f})" letter-spacing="1"')
    path(roof_v, '#c9a77c', '#5a3a22', .3)
    for g in purl: ln(g.coords[0], g.coords[-1], '#a8865c', .12)
    for d in DOMES:
        c = d['c']; cx, cy = P(*c)
        o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{d["r"] / S1:.2f}" fill="#d08a5e" stroke="#7a3518" stroke-width=".35"/>')
        o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{(d["r"] + 120) / S1:.2f}" fill="none" stroke="#1F3F8A" stroke-width=".35"/>')   # ring gutter
        r0 = d['oc'] or d['lantern']
        for k in range(12):
            a = 2 * math.pi * k / 12; ln((c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a)), (c[0] + d['r'] * math.cos(a), c[1] + d['r'] * math.sin(a)), '#7a3518', .2)
        if d['oc']:
            o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{d["oc"] / S1:.2f}" fill="#f7f1e6" stroke="#2A9DA8" stroke-width=".4"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{(d["oc"] + 600) / S1:.2f}" fill="#7aa35c" opacity=".5"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r="1.1" fill="#5a4636"/>')
            lab = t['dome'].format(d=2 * d['r'] / 1000, o=2 * d['oc'] / 1000)
        else:
            o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{d["lantern"] / S1:.2f}" fill="#bfe3ea" stroke="#2A9DA8" stroke-width=".3"/>')
            lab = t['dome_c'].format(d=2 * d['r'] / 1000)
        if lang == 'ru': lab = lab.replace('.', ',')
        tx(cx, cy + d['r'] / S1 + 3.0, lab, 1.6, '#7a3518', 'middle', 700, 'paint-order="stroke" stroke="#f7f1e6" stroke-width=".5"')
    for y in BEAMS:
        seg = LineString([(0, y), (xb(y), y)]).difference(FOOT)
        for g in getattr(seg, 'geoms', [seg]): ln(g.coords[0], g.coords[-1], '#3b2a1e', .55)
    ln((0, 0), (0, 37100), '#3b2a1e', .7)                                                  # façade ledger
    ln((xb(0) - 200, 0), (xb(37000) - 200, 37000), '#1F3F8A', .6)                         # street gutter
    for c in cols:
        if c[0] > -2800: path(R(c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150), '#2b1d12')
    for y in (7000, 23700, 33500):                                                          # fall arrows
        a, b = P(1500, y), P(xb(y) - 1800, y)
        o.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#8E1F24" stroke-width=".35" marker-end="url(#ar)"/>')
        tx((a[0] + b[0]) / 2, a[1] - 1, f'i = {t["fall"]}', 1.9, '#8E1F24', 'middle', 700)
    tx(P(xb(30000) - 300, 30000)[0] + 1.5, P(0, 30000)[1], t['gutter'], 1.7, '#1F3F8A', extra=f'transform="rotate(-84 {P(xb(30000), 30000)[0] + 1.5:.2f} {P(0, 30000)[1]:.2f})"')
    for nm, yy in (("A'", 0), ('A', 4100), ('B', 9850), ('C', 15600), ('D', 21350), ('E', 27100), ('F', 32100), ('G', 37100)):
        ln((-3300, yy), (-2800, yy), '#8a7f70', .15); X, Y = P(-3400, yy)
        o.append(f'<circle cx="{X - 1:.2f}" cy="{Y:.2f}" r="1.9" fill="#f7f1e6" stroke="#5a4a3a" stroke-width=".2"/>'); tx(X - 1, Y + .7, nm, 1.8, anchor='middle', weight=600)
    for nm, yy in (('1', 21350), ('2', TREE_S[1])):                                          # section marks
        a, b = P(-700, yy), P(xb(yy) + 1200, yy)
        o.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#8E1F24" stroke-width=".25" stroke-dasharray="3 .8 .6 .8"/>')
        for X in (a[0], b[0]): o.append(f'<circle cx="{X:.2f}" cy="{a[1]:.2f}" r="1.8" fill="#8E1F24"/>'); tx(X, a[1] + .7, nm, 1.9, '#fff', 'middle', 700)
    nx, ny = 90, 300; o.append(f'<path d="M{nx} {ny - 5}L{nx - 2} {ny + 1.6}L{nx} {ny + .5}L{nx + 2} {ny + 1.6}Z" fill="#3b2a1e"/>'); tx(nx, ny - 6.4, 'N' if lang == 'en' else 'С', 2.4, anchor='middle', weight=700)
    # ---------- sections (1:100), x = distance from the façade, z = level
    S2 = 100.0
    def section(oy, ycut, title, court=None):
        x_st = xb(ycut)
        def M(x, z): return (112 + (x + 1500) / S2, oy + (7000 - z) / S2)
        tx(112, oy - 3, title + '  ·  1:100', 2.6, weight=700, extra='letter-spacing=".4"')
        path(R(-1500, -900, 0, 4600), 'url(#hs)', '#3b2a1e', .2, M=M)                             # building
        path(R(-1500, 3850, 1500, 4200), '#cfc6b8', '#3b2a1e', .2, M=M)                           # balcony slab
        ln((1450, 4200), (1450, 5200), '#3b2a1e', .3, M=M); ln((1450, 5200), (1300, 5200), '#3b2a1e', .3, M=M)
        path(R(0, -900, x_st + 1500, -450), 'url(#hs)', '#3b2a1e', .15, M=M)                    # terrace slab
        path(R(x_st, -1300, x_st + 1500, -1170), '#d8d0c4', '#3b2a1e', .15, M=M)                  # sidewalk
        if ycut > 15000: path(R(0, -450, 3300, 0), '#c69c6d', '#3b2a1e', .2, M=M)                # aivan deck
        path(R(x_st - 1500, -450, x_st - 1350, -170), '#d8c8b2', '#3b2a1e', .15, M=M); path(R(x_st - 700, -1170, x_st - 550, -170), '#d8c8b2', '#3b2a1e', .15, M=M)
        path(R(x_st - 550, -1170, x_st, -720), '#d8c8b2', '#3b2a1e', .15, M=M)
        def lev(x, z, s_):
            X, Z = M(x, z); o.append(f'<path d="M{X:.2f} {Z:.2f}l-.9 -1.3h1.8z" fill="#3b2a1e"/>'); tx(X + 1.2, Z - .3, s_, 1.6, weight=600)
        cx = x_st - 750
        bot_c = top(cx) - PANEL - PURLIN - BEAM
        path(R(cx - 75, -170, cx + 75, bot_c), '#3b2a1e', 'none', M=M); path(R(cx - 150, -170, cx + 150, 1800), '#a87444', '#3b2a1e', .15, M=M)
        # roof: beam, purlins, panel
        x_end = x_st
        segs = [(0, x_end)]
        cut = [d for d in DOMES if abs(d['c'][1] - ycut) < d['r']]
        for d in cut:
            dy = abs(d['c'][1] - ycut); a_ = math.sqrt(d['r'] ** 2 - dy ** 2); c0, c1 = d['c'][0] - a_, d['c'][0] + a_
            segs = [(p, min(q_, c0)) for p, q_ in segs if p < c0] + [(max(p, c1), q_) for p, q_ in segs if q_ > c1]
            # drum (jali windows) from the roof skin to the ring, then the shell profile along the cut
            for x_ in (c0, c1):
                path(R(x_ - 120, top(x_) - PANEL, x_ + 120, ZR), '#c98b62', '#3b2a1e', .15, M=M)
                path(R(x_ - 60, top(x_) + 80, x_ + 60, ZR - 120), '#f2e3c7', 'none', M=M)                       # jali window
            r_in = d['oc'] or 0
            pts_o, pts_i = [], []
            for k in range(81):
                x_ = c0 + (c1 - c0) * k / 80; rho = math.hypot(x_ - d['c'][0], dy)
                pts_o.append((x_, dz(d, rho) + 120 if rho >= r_in else None)); pts_i.append((x_, dz(d, rho) if rho >= r_in else None))
            run_o, run_i = [], []
            for (xo, zo), (xi_, zi) in zip(pts_o, pts_i):
                if zo is None:
                    if run_o: path(Polygon(run_o + run_i[::-1]), '#d08a5e', '#3b2a1e', .2, M=M); run_o, run_i = [], []
                    continue
                run_o.append((xo, zo)); run_i.append((xi_, zi))
            if len(run_o) > 1: path(Polygon(run_o + run_i[::-1]), '#d08a5e', '#3b2a1e', .2, M=M)
            if not d['oc']:
                lz = dz(d, 0); path(R(d['c'][0] - d['lantern'], lz - 100, d['c'][0] + d['lantern'], lz + 500), '#bfe3ea', '#3b2a1e', .2, M=M)
            else:
                X, Z = M(d['c'][0] + d['oc'] + 500, dz(d, d['oc']) + 250); tx(X, Z, t['oc'] + f' Ø{2 * d["oc"] / 1000:.1f}'.replace('.', ',' if lang == 'ru' else '.'), 1.6, '#1d6f77', 'start', 700)
            lev(d['c'][0] + a_ * .55, ZR, f'+{ZR / 1000:.3f}'); top_z = dz(d, r_in) + 120 + (600 if not d['oc'] else 0)
            lev(d['c'][0] - d['oc'] - 1300 if d['oc'] else d['c'][0] + d['lantern'] + 200, top_z, f'+{top_z / 1000:.3f}')
        for a, b in segs:
            path(Polygon([(a, top(a)), (b, top(b)), (b, top(b) - PANEL), (a, top(a) - PANEL)]), '#8a6a4a', '#3b2a1e', .15, M=M)
            path(Polygon([(a, top(a) - PANEL - PURLIN), (b, top(b) - PANEL - PURLIN), (b, top(b) - PANEL - PURLIN - BEAM), (a, top(a) - PANEL - PURLIN - BEAM)]), '#4a4038', 'none', M=M)
            for x in range(int(a) + 400, int(b), 1200): path(R(x, top(x) - PANEL - PURLIN, x + 70, top(x) - PANEL), '#4a4038', 'none', M=M)
        if court is not None:
            # tree grows out through the oculus
            tcx = TREE_S[0]
            path(R(tcx - 160, -450, tcx + 160, 5600), '#6b4f35', 'none', M=M)
            for dx_, dz_ in ((-700, 5000), (650, 5200)): ln((tcx, 4400), (tcx + dx_, dz_), '#6b4f35', .5, M=M)
            X, Z = M(tcx, 6100); o.append(f'<ellipse cx="{X:.2f}" cy="{Z:.2f}" rx="{3300 / S2:.2f}" ry="{600 / S2:.2f}" fill="#7aa35c" opacity=".75"/>')
        path(R(x_end - 250, top(x_end) - 260, x_end, top(x_end) - PANEL), '#1F3F8A', 'none', M=M)            # street gutter
        path(R(-120, top(0) - PANEL - PURLIN - BEAM - 60, 0, top(0) - PANEL + 20), '#3b2a1e', 'none', M=M)     # ledger
        # furniture silhouettes
        for x0, x1, h in ((600, 1400, 750), (x_st - 2800, x_st - 1500, 750)) if ycut > 15000 else ((1500, 2400, 1050), (8000, 9300, 750)):
            path(R(x0, (0 if (ycut > 15000 and x0 < 3300) else -450) + h - 40, x1, (0 if (ycut > 15000 and x0 < 3300) else -450) + h), '#a87444', 'none', M=M)
        # person scale
        px_ = 5000 if court is None else 9000
        X, Z = M(px_, -450); o.append(f'<path d="M{X:.2f} {Z:.2f}l.6 -8.2l.6 8.2M{X + .6:.2f} {Z - 8.2:.2f}v-5.5" stroke="#8a7f70" stroke-width=".5" fill="none"/><circle cx="{X + .6:.2f}" cy="{Z - 14.6:.2f}" r="1.2" fill="#8a7f70"/>')
        # levels
        lev(-1300, 3850, '+3.850'); lev(-1300, 4200, '+4.200'); lev(-1300, 0, '±0.000')
        lev(200, top(0), f'+{top(0) / 1000:.3f}'.replace('+-', '-')); lev(x_end - 900, top(x_end) + 150, f'+{top(x_end) / 1000:.3f}')
        lev(x_st + 200, -1170, '−1.170'); lev(4400 if ycut > 15000 else 2600, -450, '−0.450')
        # clear heights
        for x in ((2200, x_st - 1100) if court is None else (2000, x_st - 1100)):
            z0 = 0 if (ycut > 15000 and x < 3300) else -450; z1 = top(x) - PANEL - PURLIN - BEAM
            a, b = M(x, z0), M(x, z1)
            o.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#1d6f77" stroke-width=".18"/>')
            tx(a[0] - .6, (a[1] + b[1]) / 2, f'{round(z1 - z0)}', 1.6, '#1d6f77', 'middle', 700, f'transform="rotate(-90 {a[0] - .6:.2f} {(a[1] + b[1]) / 2:.2f})"')
        X, Z = M(x_st * .8, top(x_st * .8) + 450); tx(X, Z, f'i = {t["fall"]} →', 1.8, '#8E1F24', 'middle', 700)
        tx(M(-750, 0)[0], M(0, 1500)[1], t['hall'], 2, '#6b5a48', 'middle', 700)
        tx(M(x_st + 750, 0)[0], M(0, -1600)[1] + 2.4, t['street'], 1.6, '#6b5a48', 'middle', 700)
    section(58, 21350, t['A'])
    section(152, TREE_S[1], t['B'], COURT_S)
    # ---------- spec + quantities
    sy = 244; tx(112, sy, t['spec'], 2.8, weight=700, extra='letter-spacing=".5"'); o.append(f'<line x1="112" y1="{sy + 1.2}" x2="{W - 14}" y2="{sy + 1.2}" stroke="#b8893a" stroke-width=".2"/>')
    yy = sy + 6
    for s_ in t['S']:
        words, lines, cur = s_.split(' '), [], ''
        for w_ in words:
            if len(cur) + len(w_) > 92: lines.append(cur); cur = w_
            else: cur = (cur + ' ' + w_).strip()
        lines.append(cur)
        for j, l_ in enumerate(lines): tx(112 + (0 if j == 0 else 2), yy, ('· ' if j == 0 else '') + l_, 1.9, '#3b2a1e'); yy += 3
        yy += .5
    yy += 3; tx(112, yy, t['qt'], 2.8, weight=700, extra='letter-spacing=".5"'); o.append(f'<line x1="112" y1="{yy + 1.2}" x2="{W - 14}" y2="{yy + 1.2}" stroke="#b8893a" stroke-width=".2"/>'); yy += 6
    for nm, k, u in t['Q']:
        v = f"{q['gutter_street_m']} / {q['gutter_courts_m']}" if k is None else q[k]
        tx(112, yy, nm, 2.0); tx(W - 14, yy, f'{v} {u}', 2.0, anchor='end', weight=700); yy += 3.6
    for dq in q['domes']:
        nm = (t['dome'] if dq['oculus_m'] else t['dome_c']).format(d=dq['d_m'], o=dq['oculus_m'])
        v = f"{dq['shell_m2']} + {dq['drum_m2']} m² · {dq['ribs_m']} m".replace('m', 'м' if lang == 'ru' else 'm')
        tx(112, yy, nm.capitalize(), 2.0); tx(W - 14, yy, v, 2.0, anchor='end', weight=700); yy += 3.6
    o.append(f'<rect x="14" y="{H - 20}" width="{W - 28}" height="1" fill="#1F3F8A"/>')
    tx(14, H - 13, f'SAMARKAND  ·  ROOF {REV}  ·  {DATE}', 2.2, weight=600); tx(W / 2, H - 13, t['foot'], 2.0, '#6b5a48', 'middle')
    tx(W - 14, H - 13, 'designed by Nomad Group', 1.9, '#8a7f70', 'end', extra='font-style="italic"')
    defs = ('<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="#8E1F24"/></marker>'
            '<pattern id="hs" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1.2" height="1.2" fill="#ece6dc"/><path d="M0 0V1.2" stroke="#9a8f80" stroke-width=".15"/></pattern></defs>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">{defs}{"".join(o)}</svg>'

for lang in ('ru', 'en'):
    open(f'{OUT}/samarkand-roof-{REV}-{lang}.svg', 'w').write(build(lang))
print('roof svg ok')
