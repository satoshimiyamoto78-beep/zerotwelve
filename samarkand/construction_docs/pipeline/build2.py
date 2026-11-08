"""sheets: elevations, sections, construction details, furniture, schedules, perspectives"""
from lib import *
from sheets_plans import D, YAX, streetx
from build1 import img_box, REND
def L(z): return z - TER                                    # model z -> level above FFL
def lv(z): return f'{L(z):+.3f}'.replace('+0.000', '±0.000')

def sheet_elev(pdf, num, tot):
    pg = Page('Mặt đứng kiến trúc', 'Elevations', 'KT-07', num, tot)
    v = View(pg, 'el_east', 15, 158, 100, crop=(-19.5, 19.5, -5.6, 3.8), tone=True)
    for t, y in YAX: gridline(v, v.P(13, y, -1.3), v.P(13, y, 3.6), t, ends=(True, False))
    for z, t in [(TER, '±0.000 sàn sân hiên / FFL'), (2.82, '+3.27 đáy dầm phố / beam soffit'), (3.35, '+3.80 máng xối / gutter'), (5.49, '+5.94 đỉnh mái vòm'), (7.4, '+7.85 đỉnh alem')]:
        level(v, *v.P(13, 37.0, z), t, side=-1, fs=4.8)
    dim(v, v.P(13, 0, -1.3), v.P(13, 37.1, -1.3), 4, side=-1, text='37.100')
    for n, (y, z, t) in enumerate([(16.8, 1.5, 'Cổng pishtaq — gạch men sao, vòm nhọn'), (13.5, 0.4, 'Sebil — vòi nước đồng'), (25.6, 1.4, 'Cột Samarkand bọc gạch'),
                                   (27.3, 2.95, 'Diềm gỗ + băng gạch men + diềm chạm'), (6.0, 1.2, 'Mangal — tường gạch hazarbaf'), (19.9, 4.6, 'Mái vòm ốp men xanh'), (31.0, 0.0, 'Ghế đá phố + bồn cây')], 1):
        tag(v, v.P(13, y, z), '', dxy=(6, 9 if n % 2 else -9), num=n)
    title(pg, 15, 151, 1, 'Mặt đứng hướng phố (Đông)', 'Street elevation (East)', 'TL 1:100', w=110)
    v2 = View(pg, 'el_south', 15, 32, 100, crop=(-7.2, 10.3, -5.3, 3.8), tone=True)
    for z, t in [(TER, '±0.000'), (3.35, '+3.80'), (5.49, '+5.94')]: level(v2, *v2.P(13.2, -1, z), t, side=-1, fs=4.8)
    title(pg, 15, 26, 2, 'Mặt đứng hướng Nam', 'South elevation', 'TL 1:100', w=90)
    v3 = View(pg, 'el_north', 205, 32, 100, crop=(-10.3, 7.2, -5.3, 3.8), tone=True)
    tag(v3, v3.P(6.4, 40, 1.5), 'Cổng Khiva (gỗ chạm)', dxy=(-8, 12))
    title(pg, 205, 26, 3, 'Mặt đứng hướng Bắc', 'North elevation', 'TL 1:100', w=90)
    table(pg, 300, 146, ['#', 'Chú thích / Key'], [[str(i), t] for i, t in enumerate(['Cổng pishtaq — gạch men sao 8 cánh, vòm nhọn, muqarnas', 'Sebil — đài nước, vòi đồng', 'Cột Samarkand: lõi thép SHS150, bọc gạch cong + men',
        'Diềm mái gỗ óc chó + 2 hàng gạch men 100 + diềm chạm nhọn', 'Mangal — tường gạch hazarbaf + men lam', 'Mái vòm: tráng men lam ngọc, đèn lồng, alem đồng', 'Ghế xây trát vữa vôi + đệm, bồn cây'], 1)], [6, 100], fs=4.4, rh=3.0)
    pg.save(pdf)

def sheet_sections(pdf, num, tot):
    pg = Page('Mặt cắt kiến trúc', 'Architectural sections', 'KT-08', num, tot)
    v = View(pg, 'sec_A', 15, 162, 100, crop=(-19.5, 19.5, -3.9, 4.5), tone=True)
    for t, y in YAX: gridline(v, v.P(6, y, -0.9), v.P(6, y, 4.7), t, ends=(True, False))
    for z, t in [(TER, '±0.000'), (0.0, '+0.450 aivan'), (3.02, '+3.47 trần aivan'), (5.49, '+5.94 mái vòm')]: level(v, *v.P(6, 36.9, z), t, side=-1, fs=4.8)
    title(pg, 15, 155, 1, 'Mặt cắt A-A (dọc, qua mái vòm & cây)', 'Section A-A (longitudinal, looking to the hall)', 'TL 1:100', w=140)
    v2 = View(pg, 'sec_B', 15, 40, 100, crop=(-7.6, 7.8, -3.9, 4.5), tone=True)
    for z, t in [(TER, '±0.000'), (2.9, '+3.35 dầm vòng'), (3.9, '+4.35 cổ vòm'), (5.49, '+5.94 đỉnh vòm')]: level(v2, *v2.P(13.0, 19.9, z), t, side=-1, fs=4.6)
    dim(v2, v2.P(3.46, 19.9, 2.6), v2.P(8.54, 19.9, 2.6), 3, text='5.070 vòng mái vòm')
    title(pg, 15, 33, 2, 'Mặt cắt B-B (ngang qua mái vòm)', 'Section B-B (transverse, dome)', 'TL 1:100', w=110)
    v3 = View(pg, 'sec_C', 200, 40, 100, crop=(-7.6, 7.8, -3.9, 4.5), tone=True)
    for z, t in [(TER, '±0.000'), (0.0, '+0.450 aivan'), (TER + 0.15, '+0.150 cabin')]: level(v3, *v3.P(-1.9 + 0.1, 29.7, z), t, side=1, fs=4.6)
    title(pg, 200, 33, 3, 'Mặt cắt C-C (ngang qua aivan, sảnh, cabin)', 'Section C-C (aivan · hall · booth)', 'TL 1:100', w=120)
    pg.ax.text(372, 30, 'Vị trí cắt: xem KT-03\nSection marks on KT-03', fontsize=5.5, va='top', color=MUTED)
    pg.save(pdf)

def detail(pdf, num, tot, code, vi, en, view, scale, crop, calls, levels=(), dims=(), notes=(), x0=14, y0=36, extra=None, tone=False, legend_x=None, dmax=None):
    pg = Page(vi, en, code, num, tot)
    v = View(pg, view, x0, y0, scale, crop=crop, tone=tone, dmax=dmax)
    for i, (p, side) in enumerate(calls, 1):
        tag(v, v.P(*p[0]), '', dxy=side, num=i)
    for p, t, *s in levels: level(v, *v.P(*p), t, side=(s[0] if s else 1), fs=5.0)
    for a, b, off, sd, t in dims: dim(v, v.P(*a), v.P(*b), off, side=sd, text=t)
    w = v.box[2]; lx = legend_x or min(x0 + w + 8, 290)
    title(pg, x0, y0 - 7, 1, vi, en, f'TL / Scale 1:{scale}', w=min(w, 150))
    panel(pg, lx, 150, 410 - lx, 124, 'CHÚ THÍCH CẤU TẠO / CONSTRUCTION KEY')
    yy = 266
    for i, (p, side) in enumerate(calls, 1):
        txt = p[1]; parts = txt.split(' | ')
        pg.ax.add_patch(Circle((lx + 4, yy - 1.2), 2.1, fc='white', ec=BLUE, lw=0.6, zorder=5)); pg.ax.text(lx + 4, yy - 1.2, str(i), fontsize=5.2, ha='center', va='center', color=BLUE, fontweight='bold', zorder=6)
        pg.ax.text(lx + 8, yy, parts[0], fontsize=5.1, va='top', zorder=5, wrap=True)
        if len(parts) > 1: pg.ax.text(lx + 8, yy - 3.1, parts[1], fontsize=4.5, va='top', color=MUTED, zorder=5)
        yy -= 7.6 if len(parts) > 1 else 4.6
    panel(pg, lx, 20, 410 - lx, 124, 'GHI CHÚ / NOTES')
    text_block(pg, lx + 3, 136, list(notes), fs=5.0, lh=4.0)
    if extra: extra(pg, v)
    pg.save(pdf)

def sheet_column(pdf, num, tot):
    z0 = TER
    calls = [(((10.9, 25.6, -0.42), 'Bệ đá ashlar bát giác r=270, cao 60 | Octagonal ashlar plinth r 270 × 60'), (-14, 0)),
             (((10.9, 25.6, -0.2), 'Thân bệ ốp gạch men sao girih (bát giác r=230), cao 340 | Girih star-tile die, h 340'), (-14, 4)),
             (((10.9, 25.6, 0.04), 'Gờ đá + băng kufic gạch men 30×30 (Ø350) | Stone ring + square-kufic glazed band'), (-14, 0)),
             (((10.9, 25.6, 1.1), 'Thân cột: gạch cong 120×50 mạch 8, men lam xếp lưới thoi (Ø330) | Curved brick courses, glazed diamond lattice'), (-14, 0)),
             (((10.9, 25.6, 2.18), 'Băng kufic trên + gờ đá | Upper kufic band + stone ring'), (-14, 0)),
             (((10.9, 25.6, 2.5), 'Đầu cột muqarnas 4 tầng gạch men lam/ngọc, mỗi tầng 100 | 4-tier glazed muqarnas capital'), (-14, 6)),
             (((10.9, 25.6, 2.79), 'Đế đỡ đá + bản mã liên kết dầm I300 | Stone abacus + beam seat plate'), (-14, 6)),
             (((10.52, 25.6, 1.4), 'Lõi thép SHS 150×150×6 (kết cấu) — gạch neo bằng ty inox 316 @300 | Steel core, SS316 ties @300'), (14, 0))]
    lev = [((10.9, 24.5, TER), '±0.000'), ((10.9, 24.5, 2.817), '+3.267 đáy dầm')]
    dims = [((10.9, 25.43, 0.5), (10.9, 25.77, 0.5), 3, -1, 'Ø330'), ((10.9, 25.33, -0.47), (10.9, 25.87, -0.47), 4, -1, '540'),
            ((10.9, 26.0, TER), (10.9, 26.0, 0.01), 4, 1, '460'), ((10.9, 26.0, 0.01), (10.9, 26.0, 2.317), 4, 1, '2.307'), ((10.9, 26.0, 2.317), (10.9, 26.0, 2.817), 4, 1, '500')]
    notes = ['• Gạch thân cột là gạch cong đặt hàng (bán kính 165) — không dùng gạch phẳng cắt.', '• Mạch vữa vôi-xi măng 8 mm, lõm 3 mm; men: cobalt RAL 5002 / ngọc lam.',
             '• Bọc lõi thép bằng lưới thép + vữa 20 trước khi ốp; chừa khe co giãn 10 ở đỉnh.', '• Đầu cột muqarnas đúc GRC sẵn theo 4 tầng, ốp gạch men, lắp bu lông.',
             '• Custom curved brick (r 165), 8 mm recessed joints; GRC muqarnas precast in 4 tiers.', '• SL / Qty: 7 cột phố + cổng.']
    def ex(pg, v):
        v2 = View(pg, 'det_pishtaq', 150, 36, 50, crop=(-2.5, 2.5, -2.7, 2.7))
        title(pg, 150, 29, 2, 'Mặt đứng cổng pishtaq', 'Pishtaq portal elevation', 'TL 1:50', w=90)
        dim(v2, v2.P(12, 15.55, -0.3), v2.P(12, 18.05, -0.3), 4, side=-1, text='2.500 lối vào')
        level(v2, *v2.P(12, 18.4, 1.868), '+2.318 thông thuỷ vòm', fs=4.8)
    detail(pdf, num, tot, 'CT-01', 'Chi tiết cột Samarkand & cổng pishtaq', 'Samarkand column & pishtaq', 'det_column', 20, (-1.1, 1.1, -1.95, 2.0), calls, lev, dims, notes, extra=ex, legend_x=262, dmax=29.9)

def sheet_aivan(pdf, num, tot):
    calls = [(((1.0, 23.4, 0.0), 'Sàn gạch nung 300×150 xếp chong chóng + gạch men 150 (F3) | Terracotta pinwheel + glazed inserts'), (6, 14)),
             (((1.8, 23.4, -0.25), 'Kết cấu sàn: khung thép hộp 100×50, tấm xi măng 20, vữa 30, keo C2TE | Steel frame + 20 cement board + bed'), (6, -10)),
             (((3.31, 23.4, -0.2), 'Mặt dựng sàn aivan ốp gỗ óc chó | Walnut-clad deck face'), (10, -6)),
             (((3.18, 23.4, 1.4), 'Cột Khiva gỗ chạm 180×180, chân đế đồng | Carved Khiva column 180×180'), (10, 4)),
             (((3.18, 23.4, 2.3), 'Đầu vòm chạm (arcade) + dầm gỗ | Carved arcade head + beam'), (10, 6)),
             (((1.6, 23.4, 3.0), 'Trần ô hộp aivan +3.47: khung gỗ, thảm, LED hắt | Coffered aivan ceiling'), (8, 6)),
             (((1.72, 23.4, 2.4), 'Đèn chùm kiểu mái vòm (7 bộ, tâm mỗi ô trần) | Cascade chandelier at coffer centre'), (8, 2)),
             (((0.9, 23.45, 0.5), 'Sofa 3 chỗ 1660, đệm thảm có viền | 3-seat carved settee'), (-6, 8)),
             (((0.17, 23.4, 1.4), 'Thảm treo tường trong khung, thanh đồng | Wall carpets on brass rods'), (8, -4)),
             (((0.19, 23.4, 2.45), 'Diềm gỗ chạm sao thay zardevor | Carved walnut frieze'), (8, 4))]
    lev = [((3.6, 23.4, TER), '±0.000'), ((3.6, 23.4, 0.0), '+0.450 aivan'), ((3.6, 23.4, 3.02), '+3.470 trần')]
    dims = [((0.0, 23.4, TER - 0.05), (3.3, 23.4, TER - 0.05), 4, -1, '3.300'), ((3.5, 23.4, TER), (3.5, 23.4, 0.0), 4, 1, '450')]
    notes = ['• Mẫu chong chóng: gạch 300×150 quay quanh ô vuông 150 (gạch men); lưới', '  lặp (300,150)/(−150,300). Mạch 3 mm vữa xám. Viền giữ bằng nẹp đồng.',
             '• Pinwheel: 300×150 pavers round a 150 glazed insert; 3 mm grey joints.', '• Lan can bậc thang đã bỏ: đặt bình gốm 3 cỡ (800 / 550 / 380) hai bên.',
             '• Bậc: 3 bậc cao 150, mặt đá dày 30 mũi 20, cổ bậc gạch men 100.', '• Bàn aivan: chân chữ T đặt giữa (xem CT-11).']
    def ex(pg, v):
        ax = pg.ax; x0, y0, s = 150, 40, 6.0                          # pinwheel module diagram 1:10
        L_, W_ = 0.30, 0.15; S_ = L_ - W_
        for i in range(-1, 3):
            for j in range(-1, 3):
                ox, oy = i * L_ - j * W_, i * W_ + j * L_
                for (a, b, c, d), col in (((ox, oy, ox + S_, oy + S_), '#1f5f4a' if (i + j) % 2 else '#1f3f8a'), ((ox + S_, oy, ox + S_ + W_, oy + L_), '#d9a07f'), ((ox - W_, oy + S_, ox + S_, oy + S_ + W_), '#cf9472')):
                    X0, Y0 = x0 + 30 + a * 100 / s * 2, y0 + 30 + b * 100 / s * 2; X1, Y1 = x0 + 30 + c * 100 / s * 2, y0 + 30 + d * 100 / s * 2
                    if 0 < X0 - x0 < 70 and 0 < Y0 - y0 < 70: ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fc=col, ec='white', lw=0.6, zorder=4))
        ax.text(x0, y0 - 4, 'Module lát chong chóng / pinwheel module (TL 1:10)', fontsize=5.5, fontweight='bold')
    detail(pdf, num, tot, 'CT-02', 'Chi tiết aivan', 'Aivan — section & finishes', 'det_aivan', 20, (-2.3, 2.5, -2.35, 2.2), calls, lev, dims, notes, extra=None, legend_x=262, dmax=55.0)

def sheet_booth(pdf, num, tot):
    calls = [(((8.3, 25.2, TER + 0.08), 'Bục cabin +0.150: khung gỗ, mặt ván, thảm Ba Tư; mặt dựng óc chó + nẹp đồng | Podium, walnut riser, brass strip'), (-8, -8)),
             (((9.0, 25.2, 0.25), 'Sofa 2 chỗ 1400 (700/người), đệm thảm có viền ống | Wide 2-seat settee, piped rug cushions'), (-12, 4)),
             (((9.0, 25.2, 0.35), 'Bàn chân chữ T 1200×850, mặt gỗ dày 50 | Trestle table 1200×850'), (12, -2)),
             (((8.3, 25.2, 1.2), 'Vách lưới gỗ óc chó 40 hai mặt + lõi MDF 18 sơn than | Walnut lattice both faces, 18 charcoal MDF core'), (-12, 6)),
             (((8.1, 25.2, 1.0), 'Rèm nhung, thanh đồng Ø24 dưới biển tên, vòng vén đồng + tua | Velvet curtains, brass rod, tie-back'), (-12, -6)),
             (((8.9, 25.2, 1.95), 'Trần lưới gỗ +2.40 trên tấm than | Lattice ceiling +2.40'), (8, 8)),
             (((8.9, 25.2, 1.6), 'Đèn chùm kiểu mái vòm trên bàn | Cascade chandelier over the table'), (10, 4)),
             (((9.85, 25.2, 0.33), 'Lan can phía phố cao 780, mũ đá trắng | Street parapet h 780, stone cap'), (10, -4)),
             (((10.5, 25.6, 1.0), 'Cột Samarkand (CT-01) | Samarkand column'), (10, 0)),
             (((11.35, 25.2, 2.85), 'Diềm mái phố (CT-08) | Street eave'), (6, 6))]
    lev = [((7.0, 25.2, TER), '±0.000'), ((7.0, 25.2, TER + 0.15), '+0.150 bục'), ((7.0, 25.2, TER + 0.65), '+0.650 mặt ghế'), ((7.0, 25.2, TER + 0.90), '+0.900 mặt bàn'), ((7.0, 25.2, TER + 2.40), '+2.400 trần cabin')]
    dims = [((8.045, 25.2, TER - 0.05), (9.995, 25.2, TER - 0.05), 4, -1, '1.950 cabin')]
    notes = ['• Cabin 2.400 × 1.950; sofa 1400 sâu 546; bàn 1200 × 850; mép ghế — mép bàn ≈190.', '• Booth 2.400 × 1.950; settee 1400 × 546; table 1200 × 850.',
             '• Sofa đặt sâu sát lan can; lối vào phía hành lang thông thoáng ≥ 270.', '• Ổ cắm 2S2U trên lan can +0.600 (2 / cabin).',
             '• Rèm: nhung chống cháy, 2 tấm / cabin, màu theo cabin (vang / ngọc / lá / mật ong).', '• 7 cabin: Samarkand, Bukhara, Khiva, Khujand, Penjikent, Tashkent, Margilan.']
    def ex(pg, v):
        v2 = View(pg, 'det_booth_plan', 150, 36, 25, crop=(-2.6, 2.6, -1.5, 1.5))
        title(pg, 150, 29, 2, 'Mặt bằng cabin', 'Booth plan', 'TL 1:25', w=90)
    detail(pdf, num, tot, 'CT-03', 'Chi tiết cabin VIP', 'VIP booth — section & plan', 'det_booth', 20, (-2.5, 2.3, -2.35, 2.2), calls, lev, dims, notes, extra=None, legend_x=262, dmax=56.6)

def sheet_coffers(pdf, num, tot):
    pg = Page('Chi tiết trần ô hộp', 'Coffered ceiling — types C1–C4', 'CT-04', num, tot)
    ax = pg.ax; S = 10.0                                         # 1:10 diagrams, mm on paper = mm / 10
    def coffer(x, y, kind, ttl):
        k = 1 / S; W = 1200 * k; frame = 70 * k
        ax.add_patch(Rectangle((x - 20 * k, y + 140 * k), W + 40 * k, 30 * k, fc='#d7d2c8', ec=INK, lw=0.4, hatch='////'))  # beam/purlin zone
        for xx in (x, x + W - frame):                                       # grid beams 70×140
            ax.add_patch(Rectangle((xx, y), frame, 140 * k, fc='#8a5a3b', ec=INK, lw=0.5))
        if kind == 1:
            for xx in (x + frame, x + W - frame - 45 * k): ax.add_patch(Rectangle((xx, y + 40 * k), 45 * k, 100 * k, fc='#a8714b', ec=INK, lw=0.4))
            ax.add_patch(Rectangle((x + frame + 60 * k, y + 140 * k - 12 * k), W - 2 * frame - 120 * k, 12 * k, fc='#9b2b2b', ec=INK, lw=0.4))
            ax.add_patch(Rectangle((x + frame + 30 * k, y + 140 * k - 2 * k), W - 2 * frame - 60 * k, 2 * k, fc='#ffd27a', ec='none'))
            ax.text(x + W / 2, y + 100 * k, 'thảm / carpet + LED 2700K hắt', ha='center', fontsize=4.6)
        if kind == 2:
            ax.add_patch(Rectangle((x + frame, y - 150 * k), 45 * k, 290 * k, fc='#a8714b', ec=INK, lw=0.4)); ax.add_patch(Rectangle((x + W - frame - 45 * k, y - 150 * k), 45 * k, 290 * k, fc='#a8714b', ec=INK, lw=0.4))
            for i in range(12): ax.add_patch(Rectangle((x + frame + 60 * k + i * 75 * k, y - 130 * k), 32 * k, 110 * k, fc='#8a5a3b', ec=INK, lw=0.3))
            ax.add_patch(Rectangle((x + frame + 50 * k, y + 110 * k), W - 2 * frame - 100 * k, 4 * k, fc='#ffd27a'))
            ax.text(x + W / 2, y + 40 * k, 'nan gỗ 32 @75 / slats', ha='center', fontsize=4.6)
        if kind in (3, 4):
            drop = 100 if kind == 4 else 0
            for xx in (x + frame, x + W - frame - 45 * k): ax.add_patch(Rectangle((xx, y + 40 * k - drop * k), 45 * k, (100 + drop) * k, fc='#a8714b', ec=INK, lw=0.4))
            ax.add_patch(Rectangle((x + frame + 60 * k, y + 140 * k - 12 * k), W - 2 * frame - 120 * k, 12 * k, fc='#9b2b2b', ec=INK, lw=0.4))
            ax.add_patch(Rectangle((x + frame + 46 * k, y + 80 * k), W - 2 * frame - 92 * k, 44 * k, fc='#7a4a2c', ec=INK, lw=0.3, alpha=0.8))
            ax.text(x + W / 2, y + 60 * k - drop * k, 'sườn chéo 44×58 / diagonal ribs', ha='center', fontsize=4.6, color='white' if False else INK)
        ax.plot([x - 30 * k, x + W + 30 * k], [y, y], color=BLUE, lw=0.4, ls='--'); ax.text(x + W + 32 * k, y, 'đáy lưới / grid soffit', fontsize=4.4, color=BLUE, va='center')
        ax.text(x, y + 200 * k, ttl, fontsize=6.2, fontweight='bold'); ax.text(x, y - 230 * k, f'module 1200 · dầm lưới 70×140 · khung 45', fontsize=4.6, color=MUTED)
    coffer(20, 200, 1, 'C1 — Ô thảm Ba Tư + LED hắt / carpet coffer'); coffer(170, 200, 2, 'C2 — Hộp nan gỗ hạ 150 / dropped slat box')
    coffer(20, 110, 3, 'C3 — Ô thảm + sườn chéo / ribbed carpet'); coffer(170, 110, 4, 'C4 — Ô sâu (khung hạ 100) + sườn / deep coffer')
    panel(pg, 320, 40, 90, 234, 'THÔNG SỐ / SPECIFICATION')
    text_block(pg, 323, 266, ['Trần treo dưới dầm mái 130 (đi theo dốc 3,5 %).', 'Suspended 130 under the roof beams (3.5 % fall).', '',
                              'Lưới gỗ óc chó 70×140 module ≈1,2 m, liên kết', 'bằng ke thép ẩn + ty treo M8 @1200 vào xà gồ.', '',
                              'Khung ô: gỗ 45×100 (C4: 45×200).', 'Thảm: ảnh 19 thảm Ba Tư của chủ đầu tư,', 'dán lên ván MDF 9 chống cháy, khung nẹp.', '',
                              'LED dây 2700K, 9,6 W/m, IP20, driver 24 V', 'đặt trong khoang kỹ thuật, có cửa thăm.', '',
                              'Lỗ chờ: ống treo đèn chùm, đầu báo khói,', 'quạt / điều hoà (phối hợp M&E).', '',
                              'Mở: mái vòm (Ø5,07 vuông) và giếng trời', '3,0 × 3,0 m giữ trống.', '',
                              'Số lượng ô: 150 (xem KT-05).'], fs=5.0, lh=4.0)
    pg.ax.text(20, 34, 'Tất cả mặt cắt TL 1:10 (kích thước mm) / all sections 1:10', fontsize=5.5, color=MUTED)
    pg.save(pdf)

def sheet_dome(pdf, num, tot):
    calls = [(((8.3, 19.9, 4.6), 'Vỏ mái vòm: sườn thép cong + tấm GRC, ốp gạch men lam (gân dưa) | Ribbed shell, glazed tiles'), (10, 6)),
             (((7.6, 19.9, 4.4), 'Mặt trong karbandi (sơn vẽ hoa văn) | Painted karbandi interior'), (-14, 8)),
             (((8.4, 19.9, 3.65), 'Cổ vòm có cửa sổ, gạch kufic | Drum with windows, kufic band'), (12, 0)),
             (((8.45, 19.9, 3.1), 'Dầm vòng thép hộp + ốp gỗ | Steel ring girder, timber clad'), (12, -4)),
             (((7.98, 19.9, 1.5), 'Cột đỡ vòm SHS150 bọc gỗ chạm (4 cột) | Dome column, carved casing'), (12, -2)),
             (((6.0, 19.9, 2.4), 'Đèn chùm thác cầu đồng đục lỗ (61 cầu) treo từ đỉnh | Cascade chandelier, crown hook'), (-14, -4)),
             (((6.0, 19.9, 5.75), 'Đèn lồng đỉnh vòm + mũ | Lantern + cap'), (10, 4)),
             (((6.0, 19.9, 6.8), 'Alem đồng thau | Brass finial'), (10, 2))]
    lev = [((9.6, 19.9, TER), '±0.000'), ((9.6, 19.9, 2.9), '+3.350'), ((9.6, 19.9, 3.9), '+4.350'), ((9.6, 19.9, 5.49), '+5.940'), ((9.6, 19.9, 7.4), '+7.850')]
    dims = [((3.46, 19.9, 2.6), (8.54, 19.9, 2.6), 4, -1, '5.070')]
    notes = ['• Kết cấu vòm & neo đèn chùm (≈180 kg) — kỹ sư kết cấu tính.', '• Móc treo inox 316 tại đỉnh, xích an toàn phụ.', '• Gạch men lam ngọc ốp ngoài bằng keo ngoài trời + ron epoxy.',
             '• Chống thấm: màng PU dưới lớp ốp, diềm thoát nước tại cổ vòm.', '• Mặt trong: thạch cao chịu ẩm, sơn vẽ tay theo mẫu karbandi.']
    detail(pdf, num, tot, 'CT-05', 'Chi tiết mái vòm', 'Dome — section', 'det_dome', 40, (-4.0, 4.0, -3.7, 4.4), calls, lev, dims, notes, legend_x=232, dmax=53.0)

def sheet_bar(pdf, num, tot):
    calls = [(((0.45, 11.6, 1.2), 'Tường bar: gạch bannai + hốc vòm, kệ gỗ | Bannai brick back wall with arched niches'), (10, 10)),
             (((0.55, 11.6, 3.0), 'Gờ phào gỗ chạm | Carved cornice'), (10, 4)),
             (((1.9, 11.6, 0.64), 'Mặt quầy gỗ óc chó dày 40 +1.090 | Walnut counter top'), (10, 8)),
             (((2.42, 11.6, 0.1), 'Mặt quầy: terracotta rãnh đứng + gạch men | Fluted terracotta front'), (10, -4)),
             (((2.78, 11.6, 0.1), 'Ghế bar gỗ (10 cái) | Timber bar stools'), (10, -8)),
             (((1.95, 11.6, 1.8), 'Đèn trống kết hạt (4 bộ) — ống treo xuyên trần | Beaded drum pendants'), (10, 0)),
             (((1.8, 11.6, 2.95), 'Trần ô hộp (C1–C4) | Coffered ceiling'), (10, 6))]
    lev = [((3.3, 11.6, TER), '±0.000'), ((3.3, 11.6, 0.64), '+1.090 quầy')]
    dims = [((1.45, 11.6, TER - 0.15), (2.42, 11.6, TER - 0.15), 4, -1, '970'), ((0.14, 11.6, TER - 0.15), (1.45, 11.6, TER - 0.15), 4, -1, '1.310 lối nhân viên')]
    notes = ['• Quầy dài 6.560; lối nhân viên 1.310; chân ghế cách quầy 150.', '• Kỹ thuật dưới quầy: cấp/thoát nước, ổ cắm IP44, rãnh kỹ thuật 200 (phối hợp M&E).',
             '• Tường hậu: lõi gạch + gạch bannai ốp, hốc vòm có LED 2700K, kệ gỗ.', '• Bar length 6.56 m, staff aisle 1.31 m; MEP under counter by others.']
    detail(pdf, num, tot, 'CT-06', 'Chi tiết quầy bar', 'Bar — section', 'det_bar', 20, (-2.3, 2.3, -2.3, 2.1), calls, lev, dims, notes, legend_x=262, dmax=42.8)

def sheet_corr(pdf, num, tot):
    calls = [(((8.6, 15.72, 2.0), 'Vòm nhọn gỗ óc chó, bề mặt 160, dày 140 (4 vòm) | Pointed walnut arch 160 face × 140'), (-12, 6)),
             (((9.0, 15.66, 1.0), 'Vách lưới hoa văn sao cắt CNC gỗ óc chó dày 30, khung 60 | CNC star-lattice panel 30, frame 60'), (-12, -4)),
             (((9.0, 15.72, TER + 0.01), 'Dải LED hắt chân vách 2700K IP65 | Base uplight strip IP65'), (-12, -8)),
             (((9.0, 16.8, 2.2), 'Đèn chùm kiểu mái vòm giữa các vòm | Cascade chandelier between arches'), (10, 4)),
             (((8.6, 15.85, 1.5), 'Dải rèm nhung buộc, vòng đồng | Tied velvet sash, brass ring'), (-12, 2)),
             (((9.0, 16.0, 0.0), 'Bình gốm 3 cỡ | Terracotta jugs'), (-12, -2)),
             (((9.0, 16.8, TER), 'Lối gạch zellige sao (F2) | Zellige star runner'), (10, -6)),
             (((8.6, 17.88, TER + 0.06), 'Chân vòm bọc đồng cao 120 | Brass shoe h 120'), (10, -2))]
    lev = [((9.0, 18.2, TER), '±0.000'), ((9.0, 18.2, TER + 2.15), '+2.150 chân vòm'), ((9.0, 18.2, TER + 2.95), '+2.950 đỉnh vòm')]
    dims = [((9.0, 15.8, TER + 0.3), (9.0, 17.8, TER + 0.3), 4, 1, '2.000 thông thuỷ'), ((9.0, 15.64, TER - 0.1), (9.0, 17.96, TER - 0.1), 4, -1, '2.320')]
    notes = ['• Vòm gỗ ghép thanh cong (glulam óc chó), liên kết ke inox ẩn vào sàn & trần.', '• Lưới CNC: ván gỗ óc chó / MDF chống ẩm veneer óc chó dày 30.',
             '• Hạn chế vải (gió, mưa): chỉ dải rèm buộc cố định.', '• 4 arches at x = 7.75 / 8.60 / 9.45 / 10.25 m; panels between, uplights at the base.']
    detail(pdf, num, tot, 'CT-07', 'Chi tiết hành lang vòm', 'Arcade corridor — section', 'det_corr', 20, (-1.7, 1.7, -2.0, 2.0), calls, lev, dims, notes, legend_x=200, dmax=21.7)

def sheet_eave(pdf, num, tot):
    calls = [(((11.35, 27.3, 3.15), 'Máng xối phố (hiện trạng) | Street gutter'), (10, 6)),
             (((11.36, 27.3, 2.92), 'Diềm gỗ óc chó 40×300 + 2 hàng gạch men 100 (cobalt/trắng/ngọc) | Walnut fascia + glazed tile band'), (12, 2)),
             (((11.36, 27.3, 2.7), 'Diềm chạm nhọn gỗ 25, bước 250, lỗ tròn | Carved pointed-drop fringe'), (12, -4)),
             (((10.9, 25.6, 2.95), 'Ốp dầm gỗ chạm sao + công-xon bậc + nắp đồng | Carved beam casing, corbel, brass cap'), (-14, 6)),
             (((10.52, 25.6, 1.4), 'Cột Samarkand (CT-01)'), (-14, 0)),
             (((11.1, 27.3, TER + 0.45), 'Ghế xây trát vôi + đệm, bồn cây | Plaster bench + planter'), (10, -6))]
    lev = [((12.5, 27.3, TER), '±0.000'), ((12.5, 27.3, 3.07), '+3.520 đáy máng')]
    notes = ['• Diềm & ốp dầm: gỗ óc chó / teak xử lý ngoài trời, sơn dầu UV.', '• Gạch men dán keo ngoài trời C2TES1, ron epoxy; khe co giãn mỗi 3 m.',
             '• Liên kết vào máng / dầm: ke inox 316 + bu lông M10.', '• Diềm chạm cắt CNC, cạnh vê 3 mm, sơn chống thấm 2 lớp.']
    detail(pdf, num, tot, 'CT-08', 'Chi tiết diềm mái mặt tiền', 'Street eave — fascia, tiles, fringe, beam casing', 'det_eave', 20, (-2.3, 2.3, -2.3, 2.2), calls, lev, (), notes, legend_x=262, dmax=60.5)

def sheet_mangal(pdf, num, tot):
    calls = [(((9.37, 5.5, 1.2), 'Tường gạch hazarbaf (gạch vàng + men lam thoi) | Hazarbaf brick, glazed lattice'), (10, 8)),
             (((9.37, 4.3, 0.4), 'Cửa nhân viên | Staff door'), (10, -6)),
             (((9.37, 8.6, 0.5), 'Tủ trưng bày kính + đế gạch | Glass display on brick base'), (-10, 4)),
             (((9.37, 7.6, 1.0), 'Đống củi trang trí | Firewood stack'), (-10, -4))]
    notes = ['• Lõi tường xây gạch, ốp gạch thẻ hazarbaf 240×60 mạch lõm 12.', '• Bếp mangal / tandoor / kazan: thiết bị chuyên dụng — hút khói theo M&E.', '• Tường chịu nhiệt phía bếp: gạch chịu lửa + vữa chịu nhiệt.']
    detail(pdf, num, tot, 'CT-09', 'Chi tiết khu mangal', 'Mangal — wall elevation', 'det_mangal', 25, (-2.7, 2.7, -1.75, 2.1), calls, (), (), notes, legend_x=236, dmax=7.6)

def sheet_floor_details(pdf, num, tot):
    pg = Page('Chi tiết sàn đá & gạch', 'Floor details — marble module, bands, joints', 'CT-10', num, tot)
    ax = pg.ax; s = 5.0                                           # 1:5 -> 1 m = 200 mm ... use mm/5
    x0, y0 = 30, 150; k = 1 / s
    A, W = 500, 90; P = A + W; CS = 0.16 * W
    def R(x, y, w, h, col, ang=45, cx=0, cy=0):
        import math
        pts = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], float)
        c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        pts = np.array([[cx + (px - cx) * c - (py - cy) * s_, cy + (px - cx) * s_ + (py - cy) * c] for px, py in pts])
        ax.add_patch(MPoly(x0 + pts * k / 1.0, closed=True, fc=col, ec='#555', lw=0.25, zorder=4))
    for i in range(-1, 2):
        for j in range(-1, 2):
            sx, sy = i * P, j * P
            R(sx, sy, A, A, '#f3f0ea'); R(sx + A, sy, W, A, '#ffffff'); R(sx, sy + A, A, W, '#ffffff')
            R(sx + A, sy, CS, A, '#1f3f8a'); R(sx + A + W - CS, sy, CS, A, '#1f3f8a'); R(sx, sy + A, A, CS, '#1f3f8a'); R(sx, sy + A + W - CS, A, CS, '#1f3f8a'); R(sx + A, sy + A, W, W, '#1f3f8a')
    ax.text(30, 260, 'F1 — Module đá marble 500×500 lát chéo 45° + viền 90 (TL 1:5)', fontsize=6.5, fontweight='bold')
    rows = [['Đá / Slab', 'Marble trắng Carrara (hoặc tương đương) 500×500×20, đánh bóng mờ'], ['Viền / Band', 'Cobalt 14 + trắng 62 + cobalt 14 (gạch men 20 dày)'],
            ['Khảm / Inlay', 'Kim cương men: đen / mật ong / lá / nâu xen kẽ'], ['Giao / Crossing', 'Ô cobalt 90×90 + kim cương mật ong'], ['Ron / Joint', '1,5 – 3 mm epoxy xám nhạt'],
            ['Lớp lót / Bed', 'Vữa xi măng cát 40 + keo C2TE; khe co giãn @6 m'], ['Dung sai / Tol.', 'Độ phẳng ≤ 2 mm / 2 m; chống trơn R10']]
    table(pg, 200, 262, ['Hạng mục', 'Quy cách / Specification'], rows, [28, 150], fs=5.0, rh=4.6)
    text_block(pg, 200, 214, ['Cấu tạo sàn F1 / Floor build-up:', '  1. Đá marble 20 + keo C2TE 5', '  2. Vữa lót 40 (có lưới thép D4 @200 ở sân hiên ngoài trời)', '  3. Màng chống thấm PU 1,5 mm (khu ngoài trời)',
                              '  4. Sàn bê tông hiện trạng — kiểm tra cao độ, tạo dốc 1 % ra phố', '', 'Chuyển tiếp: nẹp đồng 3×20 giữa F1 / F2 / F3 / F5', 'Transitions: 3×20 brass strip between finishes'], fs=5.2, lh=4.2)
    pg.ax.text(30, 40, 'Tham chiếu mặt bằng KT-04', fontsize=5.5, color=MUTED)
    pg.save(pdf)

def _bbox(name, pad=0.03, plan=False):
    J = json.load(open(f'{OUT}/{name}.json')); s = J['scale']; W, H = J['W'], J['H']; Hm = s * H / W
    d = np.asarray(Image.open(f'{OUT}/{name}_d.png')).astype(np.float32) / 65535 * 120
    m = (d < 119.5) & (d > 1.0); dm = None
    if m.mean() > 0.6:                                 # floor plane under the piece: drop the farthest layer
        far = d[m].max(); m &= d < far - 0.03; dm = (far - 0.03 + 1.3) / 0.5875
    ys, xs = np.where(m)
    h0, h1 = xs.min() / W * s - s / 2, (xs.max() + 1) / W * s - s / 2
    v1, v0 = Hm / 2 - ys.min() / H * Hm, Hm / 2 - (ys.max() + 1) / H * Hm
    return (h0 - pad, h1 + pad, v0 - pad, v1 + pad), dm

def sheet_furniture(pdf, num, tot):
    pg = Page('Chi tiết nội thất: ghế, sofa, bàn', 'Furniture — carved chair, settees, trestle table', 'CT-11', num, tot)
    rows = [('chair', 'Ghế gỗ chạm (58 cái)', 'Carved armchair', ['Mặt ngồi +468, đệm thảm có viền', 'Lưng lưới sao chạm, chân đồng']),
            ('settee', 'Sofa cabin 2 chỗ (14 cái)', 'Booth settee 2-seat', ['Mặt ngồi +500 trên bục +0.150', 'Đệm thảm Ba Tư có viền ống']),
            ('aivset', 'Sofa aivan 3 chỗ (8 cái)', 'Aivan settee 3-seat', ['Cùng mẫu với sofa cabin', 'Đệm thảm có viền']),
            ('table', 'Bàn chân chữ T (cabin 7 / aivan 4)', 'Trestle table', ['Mặt gỗ dày 50, chân giữa + thanh giằng', 'Cabin 1200 × 850 · aivan 1200 × 560'])]
    sc = 25; ytop = 268
    for tagn, vi, en, spec in rows:
        x = 16; hmax = 0; cr = {}
        for kind in ('front', 'side', 'plan'): cr[kind] = _bbox(f'f_{tagn}_{kind}', plan=kind == 'plan')
        hmax = max((c[3] - c[2]) * 1000 / sc for c, _ in cr.values())
        y = ytop - hmax; size = []
        for kind in ('front', 'side', 'plan'):
            c, dm = cr[kind]; nm = f'f_{tagn}_{kind}'
            w = (c[1] - c[0]) * 1000 / sc
            v = View(pg, nm, x, y, sc, crop=c, thick=1, dmax=dm)
            if kind != 'plan':
                dim(v, (c[0] + 0.03, c[2] + 0.03), (c[1] - 0.03, c[2] + 0.03), 3, side=-1, fs=4.4)
                dim(v, (c[1] - 0.03, c[2] + 0.03), (c[1] - 0.03, c[3] - 0.03), 3, side=-1, fs=4.4)
                size.append(c[1] - c[0] - 0.06); size.append(c[3] - c[2] - 0.06)
            pg.ax.text(x, y - 6.5, {'front': 'Mặt trước / front', 'side': 'Mặt bên / side', 'plan': 'Mặt bằng / plan'}[kind], fontsize=4.8, color=MUTED, va='top')
            x += w + 14
        tx = 262
        pg.ax.text(tx, ytop, vi.upper(), fontsize=7, fontweight='bold', fontfamily=SERIF, va='top'); pg.ax.text(tx, ytop - 5, en, fontsize=5.5, color=MUTED, va='top')
        wdh = f'{size[0] * 1000:.0f} × {size[2] * 1000:.0f} × {size[1] * 1000:.0f} mm (R × S × C / W × D × H)'
        text_block(pg, tx, ytop - 10, [wdh] + spec, fs=5.4, lh=4.2)
        ytop = y - 14
    pg.ax.text(262, 30, 'TL / Scale 1:25 · gỗ óc chó / walnut, PU mờ / matt PU', fontsize=5.6, color=MUTED)
    pg.save(pdf)

def sheet_finishes(pdf, num, tot):
    pg = Page('Bảng vật liệu hoàn thiện', 'Finishes & materials schedule', 'BV-01', num, tot)
    rows = [['F1', 'Sàn sảnh', 'Marble trắng 500×500 chéo 45°, viền cobalt 90, khảm kim cương', 'KT-04, CT-10'], ['F2', 'Sàn hành lang', 'Gạch zellige sao 8 cánh trên nền men trắng', 'CT-07'],
            ['F3', 'Sàn aivan', 'Gạch nung 300×150 chong chóng + gạch men 150', 'CT-02'], ['F4', 'Bục cabin', 'Gỗ óc chó + thảm Ba Tư, nẹp đồng', 'CT-03'], ['F5', 'Sàn trẻ em', 'Cao su EPDM 500×500, 4 màu', 'KT-04'],
            ['W1', 'Cột phố', 'Gạch cong + men lam, kufic, muqarnas, bệ đá', 'CT-01'], ['W2', 'Pishtaq / sebil', 'Gạch men sao girih, kufic gạch, vòm nhọn', 'CT-01'],
            ['W3', 'Tường bar', 'Gạch bannai + hốc vòm, kệ gỗ', 'CT-06'], ['W4', 'Tường mangal', 'Gạch hazarbaf vàng + men lam', 'CT-09'], ['W5', 'Tường đất (ranh nam)', 'Vữa đất sét, hốc vòm nổi, thảm khung đèn hắt', 'KT-07'],
            ['W6', 'Vách cabin', 'Lưới gỗ óc chó 40 hai mặt + lõi MDF than 18', 'CT-03'], ['C1–C4', 'Trần', 'Ô hộp gỗ óc chó, thảm Ba Tư, nan gỗ, LED 2700K', 'CT-04'],
            ['C5', 'Trần aivan', 'Ô hộp gỗ, thảm kilim, sườn chéo', 'CT-02'], ['C6', 'Mái vòm', 'Vỏ GRC ốp men lam ngọc, karbandi vẽ tay', 'CT-05'],
            ['T1', 'Gỗ nội thất', 'Óc chó (walnut) vân thẳng, PU mờ; chạm khắc sao & kim cương', 'CT-11'], ['T2', 'Kim loại', 'Đồng thau (bóng mờ), inox 316 ngoài trời', '—'],
            ['T3', 'Vải bọc', 'Thảm Ba Tư (ảnh chủ đầu tư) cho đệm; nhung chống cháy cho rèm', 'CT-03'], ['T4', 'Gạch men', 'Cobalt RAL 5002, ngọc lam, trắng, mật ong — men bóng', '—']]
    table(pg, 14, 270, ['Mã', 'Vị trí / Location', 'Vật liệu & quy cách / Material & spec', 'Chi tiết'], rows, [16, 46, 210, 30], fs=5.4, rh=5.6)
    text_block(pg, 14, 160, ['Ghi chú: mọi vật liệu cần mẫu thật được chủ đầu tư duyệt; gỗ có chứng chỉ độ ẩm; gạch men ngoài trời có hệ số hút nước ≤ 3 %.',
                             'Notes: real samples approved by the owner; timber with moisture certificate; outdoor tiles water absorption ≤ 3 %.'], fs=5.6, lh=4.5)
    pg.save(pdf)

def sheet_lighting(pdf, num, tot):
    pg = Page('Bảng chiếu sáng & điện', 'Lighting & power schedule', 'BV-02', num, tot)
    rows = [['L1', 'Đèn chùm thác mái vòm (61 cầu đồng đục lỗ)', '1', '2700K · ~600 W LED · treo đỉnh vòm'], ['L2', 'Đèn chùm nhỏ kiểu mái vòm (7 cầu)', '7+3+3+4+7', 'Aivan · hành lang · pergola · lều · cabin'],
            ['L3', 'Dải LED hắt ô trần', '150 ô', '2700K · 9,6 W/m · 24 V · IP20'], ['L4', 'Dải LED chân vách hành lang', '6', '2700K · IP65'], ['L5', 'Đèn trống kết hạt (bar)', '4', '2700K · E27 LED 8 W'],
            ['L6', 'Đèn sưởi mangal', '4', 'Hồng ngoại 2 kW — ổ riêng'], ['L7', 'Bra đồng tường lửa', '1', 'IP65'], ['L8', 'Đèn hắt cây', '3', 'IP67 · 2700K'], ['L9', 'Đèn LED sau thảm khung', '2', '2700K · IP44'],
            ['P1', 'Hộp ổ cắm sàn 2S2U', '22', 'IP44 · cạnh bàn / sofa'], ['P2', 'Ổ cắm lan can cabin', '14', '2 / cabin · +0.600'], ['P3', 'Cấp nguồn bar / mangal', '—', 'Theo M&E — RCBO 30 mA']]
    table(pg, 14, 270, ['Mã', 'Thiết bị / Fitting', 'SL / Qty', 'Thông số / Data'], rows, [16, 120, 40, 140], fs=5.6, rh=6.0)
    text_block(pg, 14, 180, ['Điều khiển: 4 kịch bản (ngày / chiều / tối / dọn dẹp), dimmer DALI hoặc 0–10 V cho L1–L3.', 'Controls: 4 scenes, DALI / 0-10 V dimming for L1–L3.',
                             'Mạch riêng cho mangal, bar, chiếu sáng trần, ổ cắm sàn; tủ điện phụ đặt trong kho nhân viên.', 'Tất cả thiết bị ngoài trời IP65, dây đi ống luồn chống cháy.'], fs=5.6, lh=4.6)
    pg.save(pdf)

def sheet_persp(pdf, num, tot, code, imgs, title_vi):
    pg = Page(title_vi, 'Perspectives (3D model R12-v11.7)', code, num, tot)
    pos = [(14, 150, 194, 122), (214, 150, 194, 122), (14, 22, 194, 118), (214, 22, 194, 118)]
    for (f, cap), (x, y, w, h) in zip(imgs, pos): img_box(pg, os.path.join(REND, f), x, y + 4, w, h - 4, cap)
    pg.save(pdf)
