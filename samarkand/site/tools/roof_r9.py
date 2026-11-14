"""Samarkand terrace — roof concept R7: plan 1:150 + two sections 1:100 (A3 portrait, RU/EN) + roof quantities JSON.
Runs layout_r9.py for the geometry. Args: zone.json base.dxf outdir
"""
import sys, json, math, runpy
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union

argv = sys.argv[:]
sys.argv = ['layout_r9.py'] + argv[1:4]
G = runpy.run_path(__file__.replace('roof_r9.py', 'layout_r9.py'))
sys.argv = argv
OUT = argv[3]
U, xb, xi, R, C = G['U'], G['xb'], G['xi'], G['R'], G['C']
COURT_S, COURT_N, BEAMS = G['COURT_S'], G['COURT_N'], G['TRUSS_Y']
TREE_N, TREE_S = G['TREE_N'], G['TREE_S']
REV, DATE = G['REV'], G['DATE']

# ---------------- roof geometry (mm, local) ----------------
SOFFIT = 3850                 # F2 balcony slab soffit
TOP0 = 3750                   # top of roof skin at the façade (100 below the soffit)
FALL = 0.05                   # 5% to the street
PANEL, PURLIN, BEAM = 50, 200, 300
EAVE_OUT = 300                # overhang past the lot line? no: gutter sits inside -> roof edge = lot line
roof_all = U.buffer(0)
roof = roof_all.difference(COURT_S).difference(COURT_N)
cols = [(xb(y) - 750, y) for y in BEAMS] + [(-7050, 200), (-350, 250)]
def top(x): return TOP0 - FALL * x
q = dict(roof_m2=round(roof.area / 1e6, 1), courts_m2=round((COURT_S.area + COURT_N.area) / 1e6, 1),
         beams_m=round(sum(xb(y) for y in BEAMS) / 1000, 1), n_cols=len(cols),
         gutter_street_m=round(LineString([(xb(0), 0), (xb(37000), 37000)]).length / 1000, 1),
         gutter_courts_m=round((COURT_S.length + COURT_N.length) / 1000, 1),
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

T = {'ru': dict(t1='Навес · концепция кровли', sub='План кровли 1:200 · разрезы 1:100', A='РАЗРЕЗ 1–1 (по оси D)', B='РАЗРЕЗ 2–2 (через южный чинар-дворик)',
                plan='ПЛАН КРОВЛИ', court='открыто к небу', fall='5%', gutter='желоб', hall='ЗАЛ', street='ТРОТУАР', ul='ул. Võ Nguyên Giáp',
                spec='РЕШЕНИЕ', S=['Балки: сталь, оцинковка + порошковая краска «тёмная бронза», по линиям колонн, шаг 3,0–5,75 м',
                                    'Опора у фасада: опорный уголок/швеллер на анкерах под плитой балкона (низ плиты +3.850)',
                                    'Опора у улицы: 9 колонн 150×150 в стенке клумбы, обшивка деревом; оголовок +2.9',
                                    'Прогоны С200 шаг 1,2 м; сэндвич-панель PU 50 мм с нижним слоем «под дерево»',
                                    'Уклон 5% к улице; коробчатый желоб вдоль улицы, водостоки внутри колонн → дренаж клумб',
                                    'Дворики у чинаров: проём с обвязкой и желобом по периметру, водосток в приствольную яму',
                                    'Деревянная реечная подшивка — только над баром и коридором (акцент)',
                                    'Волна-ламели под балконом демонтируются; фасад 2-го этажа остаётся открытым',
                                    'Тайфун: ветровой район II, анкеровка на отрыв; расчёт — инженер-конструктор'],
                qt='ОБЪЁМЫ', Q=[('Площадь кровли', 'roof_m2', 'м²'), ('Открытые дворики', 'courts_m2', 'м²'), ('Балки (пог. м)', 'beams_m', 'м'),
                                  ('Прогоны (пог. м)', 'purlins_m', 'м'), ('Колонны', 'n_cols', 'шт'), ('Желоб улица / дворики', None, 'м')],
                lv='отм.', clear='в свету', foot='Концепция · сечения и узлы подтверждает расчёт конструктора'),
     'en': dict(t1='Terrace roof · concept', sub='Roof plan 1:200 · sections 1:100', A='SECTION 1–1 (on axis D)', B='SECTION 2–2 (through the south chinar court)',
                plan='ROOF PLAN', court='open to the sky', fall='5%', gutter='gutter', hall='HALL', street='SIDEWALK', ul='Võ Nguyên Giáp',
                spec='SOLUTION', S=['Beams: galvanised steel, dark-bronze powder coat, on the column lines at 3.0–5.75 m',
                                    'Façade bearing: steel ledger on anchors under the balcony slab (soffit +3.850)',
                                    'Street bearing: 9 columns 150×150 in the planter wall, wood-clad; cap +2.9',
                                    'C200 purlins at 1.2 m; 50 mm PU sandwich panel with a wood-look underside',
                                    '5% fall to the street; box gutter along the street, downpipes inside the columns → planter drain',
                                    'Chinar courts: trimmed opening with a perimeter gutter, downpipe into the tree pit',
                                    'Timber slat ceiling only over the bar and the corridor (accent)',
                                    'Wave louvers under the balcony removed; the F2 façade stays open',
                                    'Typhoon: wind zone II, uplift anchorage; structural engineer to calculate'],
                qt='QUANTITIES', Q=[('Roof area', 'roof_m2', 'm²'), ('Open courts', 'courts_m2', 'm²'), ('Beams (lin. m)', 'beams_m', 'm'),
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
    for cg in (COURT_S, COURT_N):
        path(cg, '#f7f1e6', '#2A9DA8', .5, 'stroke-dasharray="1.6 .8"')
        x0, y0, x1, y1 = cg.bounds; c = ((x0 + x1) / 2, (y0 + y1) / 2)
        cx, cy = P(*c); o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{3000 / S1:.2f}" fill="#7aa35c" opacity=".45"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r="1.2" fill="#5a4636"/>')
        tx(cx, P(*c)[1] + 7.2, t['court'], 1.7, '#1d6f77', 'middle', 700)
        tx(cx, P(*c)[1] + 9.4, f'{(x1 - x0) / 1000:.1f} × {(y1 - y0) / 1000:.1f} м'.replace('м', 'm' if lang == 'en' else 'м').replace('.', ',' if lang == 'ru' else '.'), 1.7, '#1d6f77', 'middle')
    for y in BEAMS:
        seg = LineString([(0, y), (xb(y), y)]).difference(COURT_S.union(COURT_N))
        for g in getattr(seg, 'geoms', [seg]): ln(g.coords[0], g.coords[-1], '#3b2a1e', .55)
    ln((0, 0), (0, 37100), '#3b2a1e', .7)                                                  # façade ledger
    ln((xb(0) - 200, 0), (xb(37000) - 200, 37000), '#1F3F8A', .6)                         # street gutter
    for c in cols:
        if c[0] > -2800: path(R(c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150), '#2b1d12')
    for y in (7000, 19800, 33500):                                                          # fall arrows
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
        def M(x, z): return (112 + (x + 1500) / S2, oy + (5600 - z) / S2)
        tx(112, oy - 3, title + '  ·  1:100', 2.6, weight=700, extra='letter-spacing=".4"')
        path(R(-1500, -900, 0, 4600), 'url(#hs)', '#3b2a1e', .2, M=M)                             # building
        path(R(-1500, 3850, 1500, 4200), '#cfc6b8', '#3b2a1e', .2, M=M)                           # balcony slab
        ln((1450, 4200), (1450, 5200), '#3b2a1e', .3, M=M); ln((1450, 5200), (1300, 5200), '#3b2a1e', .3, M=M)
        path(R(0, -900, x_st + 1500, -450), 'url(#hs)', '#3b2a1e', .15, M=M)                    # terrace slab
        path(R(x_st, -1300, x_st + 1500, -1170), '#d8d0c4', '#3b2a1e', .15, M=M)                  # sidewalk
        if ycut > 15000: path(R(0, -450, 3300, 0), '#c69c6d', '#3b2a1e', .2, M=M)                # aivan deck
        path(R(x_st - 1500, -450, x_st - 1350, -170), '#d8c8b2', '#3b2a1e', .15, M=M); path(R(x_st - 700, -1170, x_st - 550, -170), '#d8c8b2', '#3b2a1e', .15, M=M)
        path(R(x_st - 550, -1170, x_st, -720), '#d8c8b2', '#3b2a1e', .15, M=M)
        cx = x_st - 750
        bot_c = top(cx) - PANEL - PURLIN - BEAM
        path(R(cx - 75, -170, cx + 75, bot_c), '#3b2a1e', 'none', M=M); path(R(cx - 150, -170, cx + 150, 1800), '#a87444', '#3b2a1e', .15, M=M)
        # roof: beam, purlins, panel
        x_end = x_st
        segs = [(0, x_end)]
        if court is not None:
            c0, c1 = court.bounds[0], court.bounds[2]; segs = [(0, c0), (c1, x_end)]
        for a, b in segs:
            path(Polygon([(a, top(a)), (b, top(b)), (b, top(b) - PANEL), (a, top(a) - PANEL)]), '#8a6a4a', '#3b2a1e', .15, M=M)
            path(Polygon([(a, top(a) - PANEL - PURLIN), (b, top(b) - PANEL - PURLIN), (b, top(b) - PANEL - PURLIN - BEAM), (a, top(a) - PANEL - PURLIN - BEAM)]), '#4a4038', 'none', M=M)
            for x in range(int(a) + 400, int(b), 1200): path(R(x, top(x) - PANEL - PURLIN, x + 70, top(x) - PANEL), '#4a4038', 'none', M=M)
        if court is not None:
            for x in (c0, c1): path(R(x - 150 if x == c1 else x, top(x) - PANEL - 250, x + 150 if x == c0 else x, top(x) - PANEL), '#1F3F8A', 'none', M=M)
            # tree through the court
            tcx = (c0 + c1) / 2
            path(R(tcx - 160, -450, tcx + 160, 4300), '#6b4f35', 'none', M=M)
            X, Z = M(tcx, 4900); o.append(f'<ellipse cx="{X:.2f}" cy="{Z:.2f}" rx="{3000 / S2:.2f}" ry="{700 / S2:.2f}" fill="#7aa35c" opacity=".75"/>')
            tx(X, M(0, 2600)[1], t['court'], 1.7, '#1d6f77', 'middle', 700, 'paint-order="stroke" stroke="#f7f1e6" stroke-width=".6"')
        path(R(x_end - 250, top(x_end) - 260, x_end, top(x_end) - PANEL), '#1F3F8A', 'none', M=M)            # street gutter
        path(R(-120, top(0) - PANEL - PURLIN - BEAM - 60, 0, top(0) - PANEL + 20), '#3b2a1e', 'none', M=M)     # ledger
        # furniture silhouettes
        for x0, x1, h in ((600, 1400, 750), (x_st - 2800, x_st - 1500, 750)) if ycut > 15000 else ((1500, 2400, 1050), (8000, 9300, 750)):
            path(R(x0, (0 if (ycut > 15000 and x0 < 3300) else -450) + h - 40, x1, (0 if (ycut > 15000 and x0 < 3300) else -450) + h), '#a87444', 'none', M=M)
        # person scale
        px_ = 5000 if court is None else 9000
        X, Z = M(px_, -450); o.append(f'<path d="M{X:.2f} {Z:.2f}l.6 -8.2l.6 8.2M{X + .6:.2f} {Z - 8.2:.2f}v-5.5" stroke="#8a7f70" stroke-width=".5" fill="none"/><circle cx="{X + .6:.2f}" cy="{Z - 14.6:.2f}" r="1.2" fill="#8a7f70"/>')
        # levels
        def lev(x, z, s_):
            X, Z = M(x, z); o.append(f'<path d="M{X:.2f} {Z:.2f}l-.9 -1.3h1.8z" fill="#3b2a1e"/>'); tx(X + 1.2, Z - .3, s_, 1.6, weight=600)
        lev(-1300, 3850, '+3.850'); lev(-1300, 4200, '+4.200'); lev(-1300, 0, '±0.000')
        lev(200, top(0), f'+{top(0) / 1000:.3f}'.replace('+-', '-')); lev(x_end - 900, top(x_end) + 150, f'+{top(x_end) / 1000:.3f}')
        lev(x_st + 200, -1170, '−1.170'); lev(4400 if ycut > 15000 else 2600, -450, '−0.450')
        # clear heights
        for x in ((2200, x_st - 1100) if court is None else (2000, x_st - 1100)):
            z0 = 0 if (ycut > 15000 and x < 3300) else -450; z1 = top(x) - PANEL - PURLIN - BEAM
            a, b = M(x, z0), M(x, z1)
            o.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="#1d6f77" stroke-width=".18"/>')
            tx(a[0] - .6, (a[1] + b[1]) / 2, f'{round(z1 - z0)}', 1.6, '#1d6f77', 'middle', 700, f'transform="rotate(-90 {a[0] - .6:.2f} {(a[1] + b[1]) / 2:.2f})"')
        X, Z = M(x_st * .55, top(x_st * .55) + 350); tx(X, Z, f'i = {t["fall"]} →', 1.8, '#8E1F24', 'middle', 700)
        tx(M(-750, 0)[0], M(0, 1500)[1], t['hall'], 2, '#6b5a48', 'middle', 700)
        tx(M(x_st + 750, 0)[0], M(0, -1600)[1] + 2.4, t['street'], 1.6, '#6b5a48', 'middle', 700)
    section(62, 21350, t['A'])
    section(148, TREE_S[1], t['B'], COURT_S)
    # ---------- spec + quantities
    sy = 232; tx(112, sy, t['spec'], 2.8, weight=700, extra='letter-spacing=".5"'); o.append(f'<line x1="112" y1="{sy + 1.2}" x2="{W - 14}" y2="{sy + 1.2}" stroke="#b8893a" stroke-width=".2"/>')
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
    o.append(f'<rect x="14" y="{H - 20}" width="{W - 28}" height="1" fill="#1F3F8A"/>')
    tx(14, H - 13, f'SAMARKAND  ·  ROOF {REV}  ·  {DATE}', 2.2, weight=600); tx(W / 2, H - 13, t['foot'], 2.0, '#6b5a48', 'middle')
    tx(W - 14, H - 13, 'designed by Nomad Group', 1.9, '#8a7f70', 'end', extra='font-style="italic"')
    defs = ('<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10z" fill="#8E1F24"/></marker>'
            '<pattern id="hs" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1.2" height="1.2" fill="#ece6dc"/><path d="M0 0V1.2" stroke="#9a8f80" stroke-width=".15"/></pattern></defs>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">{defs}{"".join(o)}</svg>'

for lang in ('ru', 'en'):
    open(f'{OUT}/samarkand-roof-{REV}-{lang}.svg', 'w').write(build(lang))
print('roof svg ok')
