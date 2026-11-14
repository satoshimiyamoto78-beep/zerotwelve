"""new sheets for the contractor-format set: setting-out, zone plans 1:75, build-ups, lighting / power plans, furniture 2, extra developments, quantities"""
import re, collections
from lib import *
from sheets_plans import D, YAX, XAX, streetx, grids
import build2 as B2
INV = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'audit', 'inv.json')))
INV = [o for o in INV if not o[0].endswith(('_real', 'realc'))]
def objs(pat): return [o for o in INV if re.search(pat, o[0])]
def ctr(o): return (o[2][0] + o[3][0]) / 2, (o[2][1] + o[3][1]) / 2

def _bbox(name, plan=False):                                   # vector replacement for the raster bbox helper
    J = hload(name); V = np.asarray(J['vis'], float).reshape(-1, 5)
    h0, h1 = min(V[:, 0].min(), V[:, 2].min()), max(V[:, 0].max(), V[:, 2].max()); v0, v1 = min(V[:, 1].min(), V[:, 3].min()), max(V[:, 1].max(), V[:, 3].max())
    return (h0 - 0.03, h1 + 0.03, v0 - 0.03, v1 + 0.03), None
B2._bbox = _bbox

# ------------------------------------------------------------------ plan helpers
def ydim(v, x, y0, y1, off=3, side=1, **kw): dim(v, v.P(x, y0, 0), v.P(x, y1, 0), off, side=side, **kw)
def xdim(v, y, x0, x1, off=3, side=1, **kw): dim(v, v.P(x0, y, 0), v.P(x1, y, 0), off, side=side, **kw)
def ychain(v, x, ys, off=3, side=1, **kw): chain(v, [v.P(x, y, 0) for y in ys], off, side=side, **kw)
def xchain(v, y, xs, off=3, side=1, **kw): chain(v, [v.P(x, y, 0) for x in xs], off, side=side, **kw)
def in_y(o, y0, y1): return y0 <= (o[1][1] + o[2][1]) / 2 <= y1

def furniture_dims(v, y0, y1, fs=4.2):
    """automatic setting-out dimensions of everything that is placed on the floor inside the y-window"""
    T = [o for o in D['table'] if in_y(o, y0, y1)]
    groups = collections.defaultdict(list)
    for o in T: groups[round((o[1][0] + o[2][0]) / 2 / 0.5)].append(o)
    for g in groups.values():
        g.sort(key=lambda o: o[1][1]); x = min(o[1][0] for o in g) - 0.62
        ys = []
        for o in g: ys += [o[1][1], o[2][1]]
        if len(g) > 1: ychain(v, x, ys, 0, side=1, fs=fs, ext=False)
    for o in T:
        bx, by = v.P(o[1][0], o[2][1], 0); k = 1 / v.mpu
        v.ax.text(bx + 0.6 * k, by + 0.9 * k, f'x{o[1][0] * 1000:.0f} y{o[1][1] * 1000:.0f}', fontsize=3.5, color=BLUE, ha='left', va='bottom', zorder=9, bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none', alpha=0.9))
    B = sorted([o for o in D['booth'] if in_y(o, y0, y1)], key=lambda o: o[1][1])
    if B:
        ys = []
        for o in B: ys += [o[1][1], o[2][1]]
        for o in B: xdim(v, o[2][1] - 0.25, o[1][0], o[2][0], 0, fs=fs, ext=False)
        for o in B: ydim(v, o[1][0] + 0.2, o[1][1], o[2][1], 0, fs=fs, ext=False)
        for o in B:
            bx, by = v.P(o[1][0], o[1][1], 0); k = 1 / v.mpu
            v.ax.text(bx + 1.0 * k, by + 1.0 * k, f'x{o[1][0] * 1000:.0f} y{o[1][1] * 1000:.0f}', fontsize=3.5, color=BLUE, ha='left', va='bottom', zorder=9, bbox=dict(boxstyle='square,pad=0.05', fc='white', ec='none', alpha=0.9))
    A = sorted([o for o in D['aivan_table'] if in_y(o, y0, y1)], key=lambda o: o[1][1])
    S = sorted([o for o in D['aivan_settee'] if in_y(o, y0, y1)], key=lambda o: o[1][1])
    if S:
        ys = []
        for o in S: ys += [o[1][1], o[2][1]]
        ychain(v, 2.2, ys, 0, fs=fs, ext=False)
    for key in ('tent', 'tapchan', 'hauz', 'bar', 'planter'):
        for o in D[key]:
            if not in_y(o, y0, y1): continue
            ydim(v, o[2][0] + 0.12, o[1][1], o[2][1], 0, side=-1, fs=fs, ext=False); xdim(v, o[1][1] - 0.12, o[1][0], o[2][0], 0, side=1, fs=fs, ext=False)

def base_plan(pg, view, crop, scale, x0=17, y0=40, **kw):
    v = View(pg, view, x0, y0, scale, crop=crop, **kw); return v

# ------------------------------------------------------------------ KT-03a setting-out
def sheet_setout(pdf, num, tot):
    pg = Page('Mặt bằng định vị kết cấu, bục, tường', 'Setting-out plan — columns, platforms, walls', 'KT-03A', num, tot)
    v = View(pg, 'floorplan', 17, 40, 100, crop=(-19.3, 19.3, -11.2, 10.4), col='#b4b4b4', cutcol='#000000', lw=0.13)
    grids(v)
    ys = [0.0] + [y for _, y in YAX] + [37.1]
    ychain(v, -0.6, ys, 9); ydim(v, -0.6, 0.0, 37.1, 16, text='37.100')
    def xy(o, dx=1.2, dy=1.2, corner=True):
        lo, hi = (o[1], o[2]) if len(o) == 3 else (o[2], o[3])
        x_, y_ = (lo[0], lo[1]) if corner else ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2)
        bx, by = v.P(x_, y_, 0); k = 1 / v.mpu
        v.ax.add_patch(Circle((bx, by), 0.45 * k, color=BLUE, zorder=9, clip_on=False))
        v.ax.text(bx + dx * k, by + dy * k, f'x{x_ * 1000:.0f} y{y_ * 1000:.0f}', fontsize=4.0, color=BLUE, ha='left', va='bottom', zorder=9, bbox=dict(boxstyle='square,pad=0.06', fc='white', ec='none', alpha=0.92))
    for o in D['steel_col'] + D['dome_col']: xy(o, corner=False)
    kc = sorted(D['khiva_col'], key=lambda o: o[1][1]); ychain(v, 3.75, [(o[1][1] + o[2][1]) / 2 for o in kc], 0, side=-1, fs=4.2, ext=False)
    o = D['aivan_deck'][0]; ydim(v, 1.6, o[1][1], o[2][1], 0, text=f'{(o[2][1] - o[1][1]) * 1000:,.0f} sàn aivan +0.450'.replace(',', '.'), fs=4.6, ext=False); xdim(v, 24.2, 0.0, 3.3, 0, fs=4.6, ext=False)
    B = sorted(D['booth'], key=lambda o: o[1][1])
    for b in B: xy(b); xdim(v, b[2][1] - 0.3, b[1][0], b[2][0], 0, fs=4.2, ext=False); ydim(v, b[2][0] - 0.3, b[1][1], b[2][1], 0, fs=4.2, ext=False)
    o = D['bar'][0]; xy(o); ydim(v, o[2][0] + 0.3, o[1][1], o[2][1], 0, side=-1, fs=4.4, ext=False); xdim(v, o[1][1] - 0.3, o[1][0], o[2][0], 0, fs=4.4, ext=False)
    o = D['corridor'][0]; xy(o); ydim(v, 8.9, o[1][1], o[2][1], 0, fs=4.4, ext=False); xdim(v, o[1][1] - 0.3, o[1][0], o[2][0], 0, fs=4.4, ext=False)
    ydim(v, 11.35, 15.55, 18.05, 0, text='2.500 cổng / portal', fs=4.4, ext=False)
    for key in ('tent', 'tapchan', 'hauz', 'planter'):
        for o in D[key]:
            xy(o); ydim(v, o[2][0] + 0.15, o[1][1], o[2][1], 0, side=-1, fs=4.2, ext=False); xdim(v, o[1][1] - 0.15, o[1][0], o[2][0], 0, fs=4.2, ext=False)
    mw = objs(r'^Mangal_west_wall$')[0]; xy(mw); ydim(v, mw[2][0] - 0.5, mw[2][1], mw[3][1], 0, fs=4.4, ext=False)
    for t, x, y in [('±0.000', 6.0, 26.5), ('+0.450', 1.2, 26.5), ('+0.150', 9.2, 26.5), ('±0.000', 6.0, 8.0), ('−0.720 vỉa hè / pavement', 12.6, 23.5)]: level(v, *v.P(x, y, 0), t, fs=4.6)
    title(pg, 17, 33, 1, 'Mặt bằng định vị', 'Setting-out plan (furniture removed) — offsets from the building wall (axis A) and grid lines 1–9', 'TL / Scale 1:100', w=185)
    north(pg, 222, 30, ang=180)
    text_block(pg, 240, 37, ['Số xanh x…/y… = toạ độ (mm) của điểm đánh dấu • (tâm cột hoặc góc cấu kiện).', 'Gốc: mặt tường toà nhà (trục A, x = 0) × mép nam sân hiên (y = 0).',
                             'Blue x…/y… = coordinates (mm) of the marked point • (column centre or element corner).', 'Origin: building wall face (axis A) × south terrace edge. Verify on site.'], fs=4.8, lh=3.2)
    pg.save(pdf)

# ------------------------------------------------------------------ zone plans 1:75
def sheet_zone(pdf, num, tot, code, vi, en, y0, y1, notes):
    pg = Page(vi, en, code, num, tot)
    h0, h1 = y0 - 18.4, y1 - 18.4
    v = View(pg, 'plan', 22, 36, 60, crop=(h0, h1, -10.1, 3.75), lw=0.22)
    k = 1 / v.mpu
    for t, y in YAX:
        if y0 + 0.3 < y < y1 - 0.3: gridline(v, v.P(-0.25, y, 0), v.P(13.1, y, 0), t, ends=(True, False))
    for t, f in XAX[:3]: gridline(v, v.P(f(0), y0 + 0.2, 0), v.P(f(0), y1 - 0.2, 0), t, ends=(True, False))
    ys = [y for y in [0.0] + [y for _, y in YAX] + [37.1] if y0 <= y <= y1]
    if y0 < min(ys) - 0.2: ys = [y0] + ys
    ychain(v, -0.1, ys, 0, fs=4.6, ext=False)
    furniture_dims(v, y0, y1)
    for txt, x, y in notes: tag(v, v.P(x, y, 0), txt, dxy=(5, 5), fs=4.4)
    title(pg, 14, 26, 1, vi, en + ' — furniture setting-out', 'TL / Scale 1:60', w=170)
    pg.ax.text(200, 27, 'Số đỏ = kích thước mm. Số xanh x…/y… = toạ độ góc bàn / cabin (mm) từ gốc: tường toà nhà (trục A) × mép nam sân hiên. Bàn 2 chỗ 700×800, bàn 4 chỗ 1400×800; ghế 584×555.', fontsize=5, color=MUTED, va='center')
    pg.ax.text(200, 23, 'Red = mm. Blue x…/y… = coordinates (mm) of the table / booth corner from the origin: building wall (axis A) × south terrace edge. 2-top 700×800, 4-top 1400×800; chair 584×555.', fontsize=5, color=MUTED, va='center')
    pg.save(pdf)
def sheet_zone_s(pdf, num, tot):
    sheet_zone(pdf, num, tot, 'MB-01', 'Mặt bằng khu nam 1:60 — majlis, mangal, bar, sảnh', 'South half: photo zone, mangal, bar, hall, entrance', -0.6, 19.4,
               [('Trạm phục vụ / waiter station', 1.0, 6.3), ('Khu chụp ảnh / photo zone', 6.4, 3.4), ('Mangal', 10.6, 5.6), ('Quầy bar', 2.0, 11.2), ('Cây ô liu + giếng trời / tree under skylight', 6.0, 12.7), ('Cổng vào / portal', 11.35, 16.8), ('Quầy lễ tân / host', 5.9, 15.1)])
def sheet_zone_n(pdf, num, tot):
    sheet_zone(pdf, num, tot, 'MB-02', 'Mặt bằng khu bắc 1:60 — aivan, mái vòm, cabin, lều', 'North half: aivan, dome, booths, tents, tapchan', 17.8, 37.8,
               [('Aivan +0.450', 1.0, 24.0), ('Mái vòm / dome Ø5.2', 6.0, 19.9), ('Cabin VIP +0.150', 9.3, 27.5), ('Tapchan', 3.4, 29.6), ('Hồ sao / star pool', 6.07, 29.65), ('Lều / tent', 2.75, 32.3), ('Lều / tent', 2.75, 35.3)])

# ------------------------------------------------------------------ build-ups
HATCH = {'stone': '', 'tile': '', 'mortar': '....', 'conc': 'oo', 'wood': '////', 'steel': 'xxxx', 'ins': '\\\\\\\\', 'board': '--', 'fabric': '++', 'air': None}
BUILD = [
 ('F1', 'Sàn sảnh — đá marble', 'Hall floor — marble', 'sàn / floor', [(20, 'Đá marble trắng 500×500×20 lát chéo 45° + viền men cobalt 90 / marble + cobalt band', 'stone'), (5, 'Keo dán C2TE / adhesive', 'mortar'), (40, 'Vữa lót M75 có lưới thép D4@200 / screed with mesh', 'mortar'), (2, 'Màng chống thấm PU 1,5 mm / PU membrane', 'ins'), (120, 'Sàn bê tông hiện trạng (dốc 1 % ra phố) / existing slab', 'conc')]),
 ('F2', 'Sàn hành lang — zellige', 'Corridor floor — zellige', 'sàn / floor', [(12, 'Gạch zellige sao 8 cánh 200×200×12, ron epoxy 2 / zellige star tiles', 'tile'), (5, 'Keo C2TE', 'mortar'), (48, 'Vữa lót M75 / screed', 'mortar'), (2, 'Chống thấm PU', 'ins'), (120, 'Sàn bê tông hiện trạng / existing slab', 'conc')]),
 ('F3', 'Sàn aivan +0.450', 'Aivan raised deck +0.450', 'sàn / floor', [(15, 'Gạch nung 300×150×15 chong chóng + gạch men 150 / terracotta pinwheel', 'tile'), (5, 'Keo C2TE', 'mortar'), (20, 'Tấm xi măng Cemboard 20 (2 lớp so le) / cement board', 'board'), (100, 'Khung thép hộp mạ 100×50×2 @400 / steel frame', 'steel'), (310, 'Chân đỡ thép 50×50 @800, bắt bu lông nở / legs — khoảng rỗng đi ống / void for services', 'air'), (120, 'Sàn bê tông hiện trạng', 'conc')]),
 ('F4', 'Bục cabin +0.150', 'Booth podium +0.150', 'sàn / floor', [(10, 'Thảm dệt dán / carpet', 'fabric'), (18, 'Ván plywood chống ẩm 18 / plywood', 'board'), (100, 'Khung gỗ 50×100 @400, xử lý mối / timber frame', 'wood'), (22, 'Đệm cao su + chêm / pads', 'air'), (120, 'Sàn hoàn thiện F1 / on finished floor', 'conc')]),
 ('F5', 'Sàn trẻ em — EPDM', 'Kids floor — EPDM', 'sàn / floor', [(25, 'Gạch cao su EPDM 500×500×25 / EPDM tiles', 'fabric'), (3, 'Keo PU', 'mortar'), (40, 'Vữa lót phẳng / screed', 'mortar'), (120, 'Sàn bê tông hiện trạng', 'conc')]),
 ('F6', 'Sàn mangal — slate', 'Mangal floor — slate', 'sàn / floor', [(15, 'Đá slate chống trơn R11 300×600 / anti-slip slate', 'stone'), (5, 'Keo C2TE', 'mortar'), (40, 'Vữa lót dốc 1,5 % về phễu thu / screed to drain', 'mortar'), (2, 'Chống thấm PU', 'ins'), (120, 'Sàn bê tông hiện trạng', 'conc')]),
 ('T1', 'Tường bar — gạch ốp', 'Bar wall — brick slips', 'tường / wall', [(20, 'Gạch thẻ vàng 230×65×20 mạch 10 + gạch men đầu / buff brick slips + glazed headers', 'tile'), (5, 'Keo C2TE', 'mortar'), (12, 'Tấm xi măng 12 / cement board', 'board'), (50, 'Khung thép hộp 50×50 @400 / steel studs', 'steel'), (200, 'Tường toà nhà hiện trạng / existing wall', 'conc')]),
 ('T2', 'Tường aivan — lưới gỗ + thảm', 'Aivan wall — lattice & carpets', 'tường / wall', [(30, 'Lưới sao óc chó CNC 30 / walnut star lattice', 'wood'), (20, 'Khe hở + LED / gap + LED', 'air'), (18, 'Tấm MDF chống ẩm sơn than 18 / painted MDF', 'board'), (40, 'Khung gỗ 40×60 @600 / battens', 'wood'), (200, 'Tường / kính toà nhà hiện trạng', 'conc')]),
 ('T3', 'Vách cabin', 'Booth partition', 'tường / wall', [(40, 'Lưới gỗ óc chó 40 / walnut lattice', 'wood'), (18, 'Lõi MDF than 18 / charcoal MDF core', 'board'), (40, 'Lưới gỗ óc chó 40 / walnut lattice', 'wood')]),
 ('T4', 'Tường mangal — hazarbaf', 'Mangal wall — hazarbaf brick', 'tường / wall', [(60, 'Gạch hazarbaf vàng 200×60 + men lam, mạch 12 / patterned brick', 'tile'), (15, 'Vữa xây M75 / mortar', 'mortar'), (200, 'Tường gạch block 200 mới, giằng BTCT / new block wall', 'conc')]),
 ('M1', 'Trần ô hộp C1–C4', 'Coffered ceiling C1–C4', 'trần / ceiling', [(300, 'Dầm thép mái HEB 300 (sơ bộ) + xà gồ / roof steel (preliminary)', 'steel'), (130, 'Ty treo M8 @1200 — khoảng kỹ thuật / hangers, service void', 'air'), (45, 'Khung gỗ 45×100 / timber carrier', 'wood'), (9, 'MDF chống cháy 9 + thảm Ba Tư dán / FR MDF + carpet', 'fabric'), (140, 'Dầm lưới óc chó 70×140 mô-đun 1.200 + LED hắt 2700K / walnut grid', 'wood')]),
 ('M2', 'Mái tôn', 'Roof sheeting', 'mái / roof', [(41, 'Tôn Klip-Lok 0,48 mạ màu, dốc 3,5 % / Klip-Lok sheet', 'steel'), (50, 'Bông khoáng cách nhiệt 50 + màng bạc / insulation', 'ins'), (200, 'Xà gồ C200×80×2,5 @1000 / purlins', 'steel'), (300, 'Dầm HEB 300 (sơ bộ — kỹ sư tính) / beams', 'steel')]),
]
def sheet_buildup(pdf, num, tot):
    pg = Page('Ghi chú cấu tạo vật liệu hoàn thiện', 'Material build-ups — floors F, walls T, ceilings / roof M', 'GC-01', num, tot)
    cw, ch = 99.5, 81.5
    for i, (code, vi, en, kind, layers) in enumerate(BUILD):
        cx = 11 + (i % 4) * (cw + 0.8); cy = 277 - (i // 4 + 1) * (ch + 1.6)
        ax = pg.ax; ax.add_patch(Rectangle((cx, cy), cw, ch, fc='none', ec=INK, lw=0.35, zorder=2))
        ax.add_patch(Rectangle((cx, cy + ch - 9), 14, 9, fc='#e8e8e8', ec=INK, lw=0.35, zorder=3)); ax.text(cx + 7, cy + ch - 4.5, code, fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)
        ax.text(cx + 16, cy + ch - 3, vi.upper(), fontsize=6, fontweight='bold', va='center'); ax.text(cx + 16, cy + ch - 6.6, en, fontsize=4.6, color=MUTED, va='center')
        tot_ = sum(t for t, _, _ in layers); hs = [max(4.2, min(16, t * 0.09 + 3.2)) for t, _, _ in layers]; sc_ = min(1.0, (ch - 16) / sum(hs)); y = cy + ch - 12
        for (t, txt, hk), h in zip(layers, hs):
            h *= sc_; hatch = HATCH[hk]
            if hatch is None: ax.add_patch(Rectangle((cx + 3, y - h), 16, h, fc='white', ec=INK, lw=0.3, ls='--', zorder=3))
            else: ax.add_patch(Rectangle((cx + 3, y - h), 16, h, fc='#f4f4f4' if hk in ('stone', 'tile') else 'white', ec=INK, lw=0.4, hatch=hatch, zorder=3))
            ax.text(cx + 20.5, y - h / 2, f'{t}', fontsize=5.2, fontweight='bold', va='center', color=RED)
            parts = txt.split(' / '); ax.text(cx + 27, y - h / 2 + (0.9 if len(parts) > 1 else 0), parts[0], fontsize=3.9, va='center')
            if len(parts) > 1: ax.text(cx + 27, y - h / 2 - 1.3, parts[1], fontsize=3.4, va='center', color=MUTED)
            y -= h
        ax.text(cx + 3, cy + 1.6, f'Σ ≈ {tot_} mm  ·  {kind}', fontsize=4.4, color=MUTED, va='bottom')
    pg.ax.text(13, 21.5, 'Chiều dày lớp bằng mm (số đỏ). Sơ đồ không theo tỷ lệ. Kết cấu thép là sơ bộ — kỹ sư kết cấu tính và duyệt.  /  Layer thickness in mm (red). Diagrams not to scale. Steel is preliminary — to be designed by the structural engineer.', fontsize=5, color=MUTED)
    pg.save(pdf)

# ------------------------------------------------------------------ lighting & power plans
def _sym(v, x, y, kind, z=0):
    ax = v.ax; k = 1 / v.mpu; bx, by = v.P(x, y, z); c = RED; kw = dict(zorder=8, clip_on=False)
    if kind == 'L1': ax.add_patch(Circle((bx, by), 3.0 * k, fc='none', ec=c, lw=0.9, **kw)); ax.add_patch(Circle((bx, by), 1.6 * k, fc=c, ec=c, **kw))
    elif kind == 'L2': ax.add_patch(Circle((bx, by), 1.6 * k, fc='none', ec=c, lw=0.8, **kw)); ax.plot([bx - 1.6 * k, bx + 1.6 * k], [by, by], color=c, lw=0.5, **kw); ax.plot([bx, bx], [by - 1.6 * k, by + 1.6 * k], color=c, lw=0.5, **kw)
    elif kind == 'L5': ax.add_patch(Circle((bx, by), 2.0 * k, fc='none', ec=c, lw=0.8, **kw)); ax.add_patch(Circle((bx, by), 1.0 * k, fc='none', ec=c, lw=0.5, **kw))
    elif kind == 'L6': ax.add_patch(Rectangle((bx - 1.6 * k, by - 0.8 * k), 3.2 * k, 1.6 * k, fc=c, ec=c, **kw))
    elif kind == 'L7': ax.add_patch(MPoly([[bx - 1.5 * k, by - 1.3 * k], [bx + 1.5 * k, by - 1.3 * k], [bx, by + 1.5 * k]], closed=True, fc=c, ec=c, **kw))
    elif kind == 'L8': ax.add_patch(Circle((bx, by), 1.3 * k, fc='white', ec=c, lw=0.8, **kw)); ax.add_patch(Circle((bx, by), 0.45 * k, fc=c, ec=c, **kw))
    elif kind == 'P1': ax.add_patch(Rectangle((bx - 1.3 * k, by - 1.3 * k), 2.6 * k, 2.6 * k, fc='white', ec=BLUE, lw=0.8, **kw)); ax.plot([bx - 1.3 * k, bx + 1.3 * k], [by - 1.3 * k, by + 1.3 * k], color=BLUE, lw=0.5, **kw)
    elif kind == 'P2': ax.add_patch(MPoly([[bx - 1.4 * k, by], [bx, by + 1.4 * k], [bx + 1.4 * k, by], [bx, by - 1.4 * k]], closed=True, fc=BLUE, ec=BLUE, **kw))
    elif kind == 'P3': ax.add_patch(Rectangle((bx - 1.6 * k, by - 1.6 * k), 3.2 * k, 3.2 * k, fc=BLUE, ec=BLUE, **kw)); ax.text(bx, by, 'E', color='white', fontsize=4.5, fontweight='bold', ha='center', va='center', zorder=9)
    elif kind == 'W': ax.add_patch(Circle((bx, by), 1.7 * k, fc='#0a7d55', ec='#0a7d55', **kw)); ax.text(bx, by, 'N', color='white', fontsize=4.5, fontweight='bold', ha='center', va='center', zorder=9)
    elif kind == 'DB': ax.add_patch(Rectangle((bx - 2.6 * k, by - 1.4 * k), 5.2 * k, 2.8 * k, fc='white', ec=BLUE, lw=1.0, **kw)); ax.text(bx, by, 'TĐ', color=BLUE, fontsize=4.5, fontweight='bold', ha='center', va='center', zorder=9)
def _legend(pg, x, y, rows, w=(9, 118, 14)):
    ax = pg.ax
    class _V: pass
    for kind, txt, n in rows:
        vv = _V(); vv.ax = ax; vv.mpu = 1.0; vv.P = lambda a, b, c, _x=x + 3.5, _y=y: (_x, _y); _sym(vv, 0, 0, kind)
        ax.text(x + w[0], y, txt, fontsize=4.9, va='center'); ax.text(x + w[0] + w[1], y, str(n), fontsize=5.4, fontweight='bold', va='center'); y -= 4.6
    return y
def light_groups():
    G = collections.defaultdict(list); seen = set()
    for o in objs(r'chandelier|lantern_hang|Chandelier|Bar_drum_pendant|^Sconce_|^Aivan_uplight|^Tree_uplight|^Heat_lamp'):
        n = o[0]
        if 'rod' in n or 'band' in n or n in seen: continue
        seen.add(n); t = (n, o[2], o[3])
        if n.startswith('Chandelier_dome'): G['L1'].append(t)
        elif n.startswith('North_chandelier'): G['L4'].append(t)
        elif n.startswith('Bar_drum'): G['L3'].append(t)
        elif n.startswith('Sconce'): G['L5'].append(t)
        elif 'uplight' in n: G['L6'].append(t)
        elif n.startswith('Heat_lamp'): G['L7'].append(t)
        else: G['L2'].append(t)
    return G
def sheet_me_light(pdf, num, tot):
    pg = Page('Mặt bằng bố trí chiếu sáng', 'Lighting layout plan', 'ME-01', num, tot)
    v = View(pg, 'plan', 17, 62, 100, crop=(-19.3, 19.3, -11.2, 5.2), col='#8c8c8c', lw=0.16, poche='#e4e4e4')
    grids(v, both=False)
    G = light_groups()
    ST = {'L1': 'L1', 'L2': 'L2', 'L3': 'L5', 'L4': 'L5', 'L5': 'L7', 'L6': 'L8', 'L7': 'L6'}
    for kind, L in G.items():
        for o in L: _sym(v, (o[1][0] + o[2][0]) / 2, (o[1][1] + o[2][1]) / 2, ST[kind])
    title(pg, 17, 55, 1, 'Mặt bằng bố trí chiếu sáng', 'Lighting layout (symbols at true positions; mounting heights in the table)', 'TL / Scale 1:100', w=170)
    rows = [('L1', 'L1  Đèn chùm thác mái vòm (61 cầu đồng đục lỗ) ~600 W LED 2700K — treo đỉnh vòm / dome cascade chandelier', len(G['L1'])),
            ('L2', 'L2  Đèn chùm nhỏ kiểu mái vòm (7 cầu) ~60 W LED 2700K — đáy đèn +2.20 / small cascade chandelier', len(G['L2'])),
            ('L5', 'L3  Đèn trống kết hạt bar Ø450, E27 LED 12 W — đáy đèn +1.90 / beaded drum pendant (bar)', len(G['L3'])),
            ('L5', 'L4  Đèn trống đồng đục lỗ Ø900 — khu bắc / pierced brass drum Ø900 (north zone)', len(G['L4']))]
    y = _legend(pg, 17, 48, rows, w=(9, 160, 14))
    rows = [('L7', 'L5  Đèn bra đồng đục lỗ, tâm +1.95; IP44 trong, IP65 mặt phố / pierced brass wall sconce', len(G['L5'])),
            ('L8', 'L6  Đèn âm sàn hắt lên 7 W IP67 2700K — chân cây, cột aivan / in-ground uplight', len(G['L6'])),
            ('L6', 'L7  Đèn sưởi hồng ngoại mangal 2 kW — mạch riêng / infrared heat lamp, own circuit', len(G['L7']))]
    _legend(pg, 215, 48, rows, w=(9, 150, 14))
    pg.ax.text(224, 33.5, 'C7 · L8 · L9  LED dây 9,6 W/m 24 V 2700K: ô trần (≈150 ô), chân vách lưới, dưới kệ bar — xem KT-05, CT-04, BV-02 / LED strip: coffers, lattice base, bar shelves', fontsize=4.6, va='center')
    pg.ax.text(17, 22, 'Điều khiển: 4 kịch bản (ngày / chiều / tối / dọn dẹp), dimmer DALI hoặc 0–10 V. Tuyến dây, tiết diện, tủ điện: nhà thầu M&E thiết kế và tính toán.  /  4 scenes, DALI or 0–10 V. Cable routes, sizes and panel: by the M&E contractor.', fontsize=5, color=MUTED)
    pg.save(pdf)
def sheet_me_power(pdf, num, tot):
    pg = Page('Mặt bằng ổ cắm, cấp điện thiết bị & điểm cấp thoát nước', 'Power outlets, equipment supply & water / drain points', 'ME-02', num, tot)
    v = View(pg, 'plan', 17, 62, 100, crop=(-19.3, 19.3, -11.2, 5.2), col='#8c8c8c', lw=0.16, poche='#e4e4e4')
    grids(v, both=False)
    fs_ = objs(r'^Floor_socket'); bs = objs(r'^Booth\d_socket'); ws = objs(r'^Aivan_wallsocket')
    for o in fs_: _sym(v, *ctr(o), 'P1')
    for o in bs + ws: _sym(v, *ctr(o), 'P2')
    EQ = [(0.4, 8.7, 'Máy làm đá 0,6 kW'), (0.4, 10.0, 'Tủ mát ×4 — 4 × 0,35 kW'), (0.4, 11.4, 'Máy pha cà phê 2 group 3,5 kW (mạch riêng)'), (0.4, 12.4, 'Máy xay ×2 + máy xay sinh tố ×2 — 2,0 kW'), (0.4, 13.8, 'Tủ mát đứng 0,5 kW'),
          (2.0, 9.2, 'POS + máy in'), (11.4, 5.0, 'Quạt hút khói mangal 1,5 kW 3P'), (10.0, 8.7, 'Tủ trưng bày lạnh mangal 0,8 kW'), (5.9, 15.1, 'POS lễ tân / host'), (0.4, 6.3, 'POS trạm phục vụ ×2'), (6.07, 29.65, 'Bơm hồ sao 60 W IP68')]
    for i, (x, y, t) in enumerate(EQ, 1):
        _sym(v, x, y, 'P3'); bx, by = v.P(x, y, 0); v.ax.text(bx + 2.2 / v.mpu, by + 2.2 / v.mpu, str(i), fontsize=5, color=BLUE, fontweight='bold', zorder=9)
    WP = [(0.4, 8.7, 'Máy làm đá'), (0.4, 11.4, 'Máy pha cà phê'), (1.9, 10.6, 'Chậu rửa quầy trước ×2'), (6.07, 29.65, 'Hồ sao: cấp bù + xả đáy'), (5.99, 12.72, 'Tưới cây (vòi)')]
    sk = objs(r'^sinkbins$')
    if sk: WP.append((*ctr(sk[0]), 'Chậu rửa mangal'))
    for x, y, t in WP: _sym(v, x + 0.45, y, 'W')
    _sym(v, 9.45, 3.5, 'DB')
    title(pg, 17, 55, 1, 'Mặt bằng ổ cắm & điểm cấp thoát nước', 'Power outlets, equipment supply, water & drain points', 'TL / Scale 1:100', w=170)
    y = _legend(pg, 17, 48, [('P1', 'Hộp ổ cắm sàn bật nắp 180×180, 2 ổ 16 A + 2 USB, IP44 — đầu bàn / pop-up floor box', len(fs_)),
                             ('P2', 'Ổ cắm tường đôi 16 A: cabin +0.600 (trên bục), tường aivan +0.300 / twin wall socket', f'{len(bs)} + {len(ws)}'),
                             ('P3', 'Điểm cấp điện thiết bị (số = bảng bên phải), ổ IP44 +1.050 / equipment supply point', len(EQ)),
                             ('W', 'Điểm cấp nước lạnh Ø21 + thoát nước Ø60 (vị trí sơ bộ) / cold water + drain point (preliminary)', len(WP)),
                             ('DB', 'Tủ điện phụ (kho nhân viên mangal), RCBO 30 mA từng mạch / sub-panel', 1)])
    pg.ax.text(215, 50, 'P3 — THIẾT BỊ / EQUIPMENT', fontsize=5.2, fontweight='bold')
    for i, (x, y, t) in enumerate(EQ, 1):
        pg.ax.text(215 + ((i - 1) // 6) * 95, 46 - ((i - 1) % 6) * 3.7, f'{i}  {t}', fontsize=4.7, va='center')
    pg.ax.text(17, 21, 'Vị trí cấp thoát nước và công suất là SƠ BỘ theo bố trí thiết bị; nhà thầu M&E tính toán tuyến ống, tiết diện dây, tủ điện. Điều hoà: sân hiên mở — không thiết kế; quạt trần / phun sương theo yêu cầu chủ đầu tư.', fontsize=4.9, color=MUTED)
    pg.ax.text(17, 18, 'Water / drain points and loads are PRELIMINARY; pipe routes, cable sizes and the panel are by the M&E contractor. HVAC: open terrace — not designed; ceiling fans / misting on the owner\'s request.', fontsize=4.9, color=MUTED)
    pg.save(pdf)

# ------------------------------------------------------------------ furniture 2
def sheet_furn(pdf, num, tot, code, vi, en, rows, sc=25):
    pg = Page(vi, en, code, num, tot); ytop = 270
    for tagn, tvi, ten, spec, sc_ in rows:
        s_ = sc_ or sc; x = 16; cr = {}
        for kind in ('front', 'side', 'plan'): cr[kind] = _bbox(f'f_{tagn}_{kind}')[0]
        hmax = max((c[3] - c[2]) * 1000 / s_ for c in cr.values()); y = ytop - hmax; size = []
        for kind in ('front', 'side', 'plan'):
            c = cr[kind]; nm = f'f_{tagn}_{kind}'; w = (c[1] - c[0]) * 1000 / s_
            v = View(pg, nm, x, y, s_, crop=c, lw=0.25)
            dim(v, (c[0] + 0.03, c[2] + 0.03), (c[1] - 0.03, c[2] + 0.03), 3, side=-1, fs=4.4)
            dim(v, (c[1] - 0.03, c[2] + 0.03), (c[1] - 0.03, c[3] - 0.03), 3, side=-1, fs=4.4)
            size.append((c[1] - c[0] - 0.06, c[3] - c[2] - 0.06))
            pg.ax.text(x, y - 7.5, {'front': 'Mặt trước / front', 'side': 'Mặt bên / side', 'plan': 'Mặt bằng / plan'}[kind], fontsize=4.8, color=MUTED, va='top')
            x += w + 16
        tx = max(x + 4, 250)
        pg.ax.text(tx, ytop, tvi.upper(), fontsize=6.6, fontweight='bold', va='top'); pg.ax.text(tx, ytop - 4.6, ten, fontsize=5.2, color=MUTED, va='top')
        wdh = f'{size[0][0] * 1000:.0f} × {size[1][0] * 1000:.0f} × {size[0][1] * 1000:.0f} mm (R × S × C / W × D × H) · TL 1:{s_}'
        text_block(pg, tx, ytop - 9.5, [wdh] + spec, fs=5.0, lh=3.9)
        ytop = y - 15
    pg.save(pdf)
def sheet_furn1(pdf, num, tot):
    sheet_furn(pdf, num, tot, 'NT-01', 'Nội thất 1: ghế, sofa cabin, sofa aivan, bàn chữ T', 'Furniture 1 — carved chair, booth settee, aivan settee, trestle table',
        [('chair', 'Ghế gỗ chạm (62 cái)', 'Carved armchair — 62 pcs', ['Gỗ óc chó, PU mờ; lưng lưới sao CNC', 'Mặt ngồi +468, đệm thảm có viền; chân bọc đồng', 'Walnut, matt PU; CNC star-lattice back; brass feet'], None),
         ('settee', 'Sofa cabin 2 chỗ (14 cái)', 'Booth settee, 2-seat — 14 pcs', ['Khung óc chó, vòm chạm dưới mặt ngồi', 'Đệm mút D40 bọc thảm Ba Tư, viền ống', 'Walnut frame, carved arches; foam + Persian-carpet cover'], None),
         ('aivset', 'Sofa aivan 3 chỗ (8 cái)', 'Aivan settee, 3-seat — 8 pcs', ['Cùng mẫu sofa cabin, dài 1.684', 'Same design as the booth settee'], None),
         ('table', 'Bàn chân chữ T (cabin 7 / aivan 4)', 'Trestle table — booth 7 / aivan 4', ['Mặt gỗ óc chó dày 50, chân giữa + giằng', 'Cabin 1200×850 · aivan 1200×560', 'Walnut top 50, trestle legs + stretcher'], None)])
def sheet_furn2(pdf, num, tot):
    sheet_furn(pdf, num, tot, 'NT-02', 'Nội thất 2: bàn sảnh, ghế bar, quầy lễ tân', 'Furniture 2 — hall tables, bar stool, host stand',
        [('t4', 'Bàn sảnh 4 chỗ 1400×800', 'Hall table, 4-top', ['Mặt óc chó 40, khung chân chạm, cao 760', 'Walnut top 40, carved apron, h 760'], None),
         ('t2', 'Bàn sảnh 2 chỗ 700×800', 'Hall table, 2-top', ['Cùng mẫu bàn 4 chỗ / same design'], None),
         ('stool', 'Ghế bar (10 cái)', 'Bar stool — 10 pcs', ['Khung óc chó, gác chân đồng +300, mặt ngồi +750 (quầy +1.050)', 'Walnut, brass footrest, seat +750'], None),
         ('host', 'Quầy lễ tân', 'Host stand', ['Tủ óc chó cửa lưới chạm, mặt đá', 'Walnut cabinet, carved jali doors, stone top'], None)])
def sheet_furn3(pdf, num, tot):
    sheet_furn(pdf, num, tot, 'NT-03', 'Nội thất 3: tủ trạm, tapchan, lều majlis', 'Furniture 3 — station cabinet, tapchan, majlis tent',
        [('stcab', 'Tủ trạm phục vụ (3 cái)', 'Waiter-station cabinet — 3 pcs', ['Tủ óc chó 2 tầng, cửa lưới chạm, kệ hở giữa', 'Walnut two-tier cabinet, carved doors, open shelf'], 30),
         ('tapchan', 'Tapchan 2000×2200', 'Tapchan daybed', ['Sàn gỗ óc chó trên khung 100×50, lan can chạm 3 phía', 'Nệm kurpacha + gối ôm, bàn thấp 1000×660', 'Walnut platform, carved rails on 3 sides, kurpacha mats, low table'], 40),
         ('tent', 'Lều majlis 2720×2820 (2 cái)', 'Majlis tent — 2 pcs', ['4 trụ gỗ 60×60 cao 2.250, vì kèo 60×40, đỉnh +2.740', 'Mái + 3 vách canvas kem, viền tua; nệm majlis chữ U, 2 mâm đồng', 'Timber posts 60×60, canvas roof + 3 walls, U-shaped majlis seating'], 50)], sc=40)

# ------------------------------------------------------------------ extra developments
def sheet_dev_extra(pdf, num, tot):
    pg = Page('Khai triển: mặt sảnh nhìn về dãy cabin & khu trẻ em', 'Developments — hall looking at the booth row; kids zone', 'DV-07', num, tot)
    v = View(pg, 'dev_hall_e', 14, 168, 100, crop=(-16.0, 16.0, -1.9, 2.6))
    for t, y in YAX:
        if 6 < y < 37: gridline(v, (-(y - 21.5), -1.9), (-(y - 21.5), 2.6), t, ends=(True, False))
    for z, t in [(TER, '±0.000'), (TER + 0.15, '+0.150 bục cabin'), (TER + 2.4, '+2.400 trần cabin'), (TER + 3.2, '+3.200 đáy trần ô hộp')]: level(v, 15.2, z - 1.3, t, fs=4.6)
    title(pg, 14, 152, 1, 'Mặt sảnh nhìn về phía phố (dãy cabin, hành lang, mangal)', 'Hall elevation looking towards the street — cut on x = 6.2', 'TL / Scale 1:100', w=190)
    v2 = View(pg, 'dev_kids', 14, 58, 40, crop=(-4.4, 4.4, -1.4, 1.4))
    J = v2.J; c0 = J['cam']
    for z, t in [(TER, '±0.000'), (TER + 0.98, '+0.980 hàng rào chạm / carved fence'), (TER + 2.3, '+2.300 bảng phấn / chalkboard')]: level(v2, 3.4, z - c0[2], t, fs=4.6)
    dim(v2, (-7.26 - c0[0], TER - c0[2] - 0.05), (-0.12 - c0[0], TER - c0[2] - 0.05), 5, side=-1, text='7.140 khu trẻ em / kids zone')
    title(pg, 14, 50, 2, 'Khu trẻ em — mặt đứng nhìn về phía bắc', 'Kids zone — elevation looking north', 'TL / Scale 1:40', w=150)
    panel(pg, 250, 30, 158, 110, 'GHI CHÚ / NOTES')
    text_block(pg, 253, 130, ['• Hàng rào khu trẻ em: gỗ óc chó chạm, cao 980, cửa tự đóng.', '  Kids fence: carved walnut h 980, self-closing gate.', '• Sàn EPDM 25 mm (F5) — độ rơi tới hạn ≥ 1,0 m.', '  EPDM floor 25 mm, critical fall height ≥ 1.0 m.',
                               '• Tường khu trẻ em: vữa đất sét mịn + bảng phấn 1.880 × 2.300.', '  Walls: fine clay render + chalkboard.', '• Mọi góc cạnh bo R ≥ 10; sơn gốc nước an toàn cho trẻ.', '  All edges rounded R ≥ 10; water-based child-safe paint.',
                               '• Dãy cabin: 7 mô-đun giống nhau 2.400 × 1.950 (xem DV-04, CT-03).', '  Booth row: 7 identical modules (see DV-04, CT-03).'], fs=5.2, lh=4.2)
    pg.save(pdf)

# ------------------------------------------------------------------ quantities
def boq_rows():
    import openpyxl
    wb = openpyxl.load_workbook(os.path.join(os.path.dirname(__file__), '..', 'cad', 'Samarkand_BOQ_R12-v12.1.xlsx'), data_only=True); out = []
    for name in wb.sheetnames[1:]:
        ws = wb[name]; hdr = True; rows = []
        for r in ws.iter_rows(min_row=5, values_only=True):
            if r and r[1] and r[2] and r[5] is not None: rows.append((r[1], r[2], r[3], r[4], r[5]))
        out.append((name, hdr, rows))
    return out
def sheet_qty(pdf, num, tot, part):
    BQ = boq_rows(); pg = Page('Bảng thống kê khối lượng' + (' (tiếp)' if part else ''), 'Bill of quantities — net quantities from the model (prices: see the XLSX)', f'KL-0{part + 1}', num, tot)
    ax = pg.ax; x = 12; W = 396; sel = [BQ[i] for i in ((0, 1, 2), (3, 4, 5))[part] if i < len(BQ)]
    nrow = sum(len(r) for _, _, r in sel); rh = min(5.0, (250 - 9 * len(sel)) / max(nrow, 1)); y = 274
    for name, hdr, rows in sel:
        ax.add_patch(Rectangle((x, y - 5), W, 5, fc='#e8e8e8', ec=INK, lw=0.3, zorder=3)); ax.text(x + 1.5, y - 2.5, name.upper(), fontsize=5.8, fontweight='bold', va='center', zorder=4)
        ax.text(x + 352, y - 2.5, 'ĐVT / Unit', fontsize=4.6, va='center', zorder=4); ax.text(x + W - 2, y - 2.5, 'KL / Qty', fontsize=4.6, va='center', ha='right', zorder=4); y -= 5
        for r in rows:
            code, vi, en, unit, qty = r
            try: qty = float(qty)
            except Exception: pass
            q = (f'{qty:,.1f}'.replace(',', ' ') if qty != int(qty) else f'{int(qty)}') if isinstance(qty, float) else str(qty or '')
            ax.text(x + 1.5, y - rh / 2, str(code), fontsize=4.8, fontweight='bold', va='center')
            ax.text(x + 14, y - rh / 2, str(vi)[:125], fontsize=4.0, va='center'); ax.text(x + 186, y - rh / 2, str(en)[:122], fontsize=3.7, va='center', color=MUTED)
            ax.text(x + 352, y - rh / 2, str(unit or ''), fontsize=4.5, va='center'); ax.text(x + W - 2, y - rh / 2, q, fontsize=5.0, fontweight='bold', va='center', ha='right')
            ax.plot([x, x + W], [y - rh, y - rh], color='#aaaaaa', lw=0.2); y -= rh
        y -= 4
    pg.ax.text(12, 19.5, 'Khối lượng tịnh đo từ mô hình R12-v12.1; hao hụt và đơn giá trong file Samarkand_BOQ_R12-v12.1.xlsx. Diện tích sàn đo trên đa tuyến kín của file DXF.  /  Net quantities from the model; waste and prices in the XLSX. Floor areas are closed polylines in the DXF.', fontsize=4.8, color=MUTED)
    pg.save(pdf)
