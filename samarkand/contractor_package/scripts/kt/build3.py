"""v2 sheets: entrance portal, wall developments (aivan, bar, booths, photo zone), bar plan / front / waiter station, north zone + tent"""
from lib import *
from build1 import img_box, REND
from build2 import detail
def L(z): return z - TER
def ex_img(name, cap):
    def f(pg, v):
        p = os.path.join(REND, name)
        if os.path.exists(p):
            lx = 410 - 3 - 100; img_box(pg, p, lx, 24, 100, 62, None); pg.ax.text(lx, 22.5, cap, fontsize=4.6, color=MUTED, va='top')
    return f
E0, E1 = 15.55, 18.05

def sheet_portal(pdf, num, tot):
    pg = Page('Chi tiết cổng vào (pishtaq) — bản đơn giản dễ thi công', 'Entrance portal — plain buildable version', 'CT-12', num, tot)
    v = View(pg, 'det_pishtaq', 14, 150, 40, crop=(-2.4, 2.4, -2.65, 2.0), dmax=29.4)
    title(pg, 14, 144, 1, 'Mặt đứng phía phố', 'Street elevation', 'TL 1:40', w=110)
    for z, t in ((-1.17, '−0.720 vỉa hè'), (TER, '±0.000'), (TER + 2.62, '+2.620 đáy lanh-tô'), (3.09, '+3.540 đỉnh')): level(v, *v.P(12, 18.95, z), t, side=-1, fs=4.8)
    dim(v, v.P(12, E0, -1.3), v.P(12, E1, -1.3), 3, side=-1, text='2.500 thông thuỷ')
    dim(v, v.P(12, E0 - 0.7, -1.3), v.P(12, E0, -1.3), 3, side=-1, text='700'); dim(v, v.P(12, E1, -1.3), v.P(12, E1 + 0.7, -1.3), 3, side=-1, text='700')
    dim(v, v.P(12, E0 - 0.7, -1.3), v.P(12, E1 + 0.7, -1.3), 8, side=-1, text='3.900')
    dim(v, v.P(12, 14.75, -1.17), v.P(12, 14.75, -0.62), 3, side=1, text='550'); dim(v, v.P(12, 14.75, -0.62), v.P(12, 14.75, TER + 2.62), 3, side=1, text='3.240'); dim(v, v.P(12, 14.75, TER + 2.62), v.P(12, 14.75, 3.09), 3, side=1, text='920')
    for n, (p, d) in enumerate([((12, 15.2, 1.0), (-9, 6)), ((12, 15.2, -0.9), (-9, -3)), ((12, 16.8, 2.05), (0, -9)), ((12, 16.2, 1.95), (-6, -12)), ((12, 16.8, 2.6), (10, 10)), ((12, 17.6, 2.6), (12, 6)), ((12, 16.8, 3.05), (12, 9))], 1):
        tag(v, v.P(*p), '', dxy=d, num=n)
    v2 = View(pg, 'det_pishtaq_sec', 150, 150, 40, crop=(-2.4, 2.4, -2.65, 2.0), dmax=48.9)
    title(pg, 150, 144, 2, 'Mặt cắt dọc lối vào', 'Section along the entrance', 'TL 1:40', w=110)
    dim(v2, v2.P(10.75, 16.8, -1.3), v2.P(11.95, 16.8, -1.3), 3, side=-1, text='1.200')
    for z, t in ((TER, '±0.000'), (TER + 2.62, '+2.620')): level(v2, *v2.P(9.3, 16.8, z), t, side=1, fs=4.8)
    for n, (p, d) in ((8, ((11.3, 16.8, 1.0), (-10, 8))), (9, ((11.3, 16.8, 2.55), (-12, 6))), (10, ((11.6, 16.8, -0.8), (10, -6)))): tag(v2, v2.P(*p), '', dxy=d, num=n)
    v3 = View(pg, 'det_pishtaq_plan', 14, 36, 40, crop=(-2.4, 2.4, -1.5, 1.5))
    title(pg, 14, 30, 3, 'Mặt bằng (cắt +1.35)', 'Plan', 'TL 1:40', w=110)
    dim(v3, v3.P(10.75, E0 - 0.7, 0), v3.P(11.95, E0 - 0.7, 0), 3, side=1, text='1.200'); dim(v3, v3.P(11.95, E0 - 0.7, 0), v3.P(11.95, E0, 0), 3, side=-1, text='700')
    lx = 290; panel(pg, lx, 150, 410 - lx, 124, 'CHÚ THÍCH CẤU TẠO / CONSTRUCTION KEY')
    key = ['Trụ 700×1200: gạch men 150×150 ba màu (lam / ngọc / trắng) xếp chéo, viền cobalt 75 | 150 glazed tiles, diagonal 3-colour pattern, 75 cobalt border',
           'Chân đế đá trắng cao 550 (từ vỉa hè) | White stone plinth 550',
           'Vòm nhọn PHẲNG: tấm xi măng / GRC dày 60 sơn trắng, cắt theo dưỡng | Flat pointed-arch panel 60 thick',
           'Viền vòm gạch men ngọc lam rộng 90 | Turquoise edge band 90',
           'Lanh-tô: gạch ốp vàng 230×65 mạch 10, xây so le | Buff facing-brick lintel, running bond',
           'Chữ đồng «Samarkand» cao 300, nổi 16 | Brass letters h 300',
           'Mũ đá trắng dày 80, nhô 40 | White stone coping 80',
           'Mặt trong lối đi ốp cùng loại gạch 150 | Passage faces: same 150 tiles',
           'Trần lối đi PHẲNG (tấm xi măng sơn trắng) — không vòm muqarnas | Flat soffit, no vault',
           'Bậc đá 4 bậc × 180 (hiện trạng thiết kế) | 4 stone steps']
    yy = 266
    for i, t in enumerate(key, 1):
        a, b_ = t.split(' | ')
        pg.ax.add_patch(Circle((lx + 4, yy - 1.2), 2.1, fc='white', ec=BLUE, lw=0.6, zorder=5)); pg.ax.text(lx + 4, yy - 1.2, str(i), fontsize=5.2, ha='center', va='center', color=BLUE, fontweight='bold', zorder=6)
        pg.ax.text(lx + 8, yy, a, fontsize=4.7, va='top', zorder=5); pg.ax.text(lx + 8, yy - 3.4, b_, fontsize=4.2, va='top', color=MUTED, zorder=5); yy -= 8.6 if len(a) < 62 else 11.6
    panel(pg, 150, 20, 258, 118, 'TRÌNH TỰ THI CÔNG / BUILD SEQUENCE')
    text_block(pg, 153, 130, ['1. Hai cột thép SHS 150 của khung mái đứng trong hai trụ (xem KT-06); dầm mái y 15.3 / 18.3 đi qua khối lanh-tô.',
        '2. Khung phụ thép hộp 50×50 quanh mỗi trụ + lanh-tô; xây chèn gạch block 100 hoặc ốp tấm xi măng 12 hai lớp.',
        '3. Trát phẳng, chống thấm chân trụ 300; ốp đá chân đế 550.',
        '4. Ốp gạch men 150×150 bằng keo C2TE, mạch 3 mm ron epoxy trắng; viền cobalt 75 cắt từ gạch 150.',
        '5. Lắp tấm vòm phẳng (cắt CNC / dưỡng gỗ) vào mặt trước, bắt vít vào khung; dán viền men ngọc.',
        '6. Ốp gạch thẻ lanh-tô, lắp mũ đá, chữ đồng (chốt ren M6 + keo).',
        '',
        'Build: steel roof columns inside the pylons → 50×50 sub-frame + block / cement-board infill → render, plinth stone →',
        '150 tiles on C2TE, 3 mm joints → flat arch panel screwed to the frame → brick-slip lintel, coping, brass letters.',
        'Mặt bằng VUÔNG GÓC với trục lối vào (không xiên theo vỉa hè) — mọi mặt phẳng, mọi viên gạch vuông.',
        'The plan is square to the entrance axis: every face is flat, every tile is a full square.'], fs=5.0, lh=4.6)
    img_box(pg, os.path.join(REND, 'i_port.jpg'), 290, 26, 116, 0.001) if False else None
    pg.save(pdf)

def dev_sheet(pdf, num, tot, code, vi, en, view, scale, crop, dmax, x0, y0, marks, levels, chains, notes, img=None, flipx=False):
    pg = Page(vi, en, code, num, tot)
    v = View(pg, view, x0, y0, scale, crop=crop, dmax=dmax, tone=True)
    for p, t in levels: level(v, *v.P(*p), t, side=1, fs=4.8)
    for pts, off, sd, txts in chains:
        for (a, b_), t in zip(zip(pts[:-1], pts[1:]), txts): dim(v, v.P(*a), v.P(*b_), off, side=sd, text=t)
    for n, (p, d) in enumerate(marks, 1): tag(v, v.P(*p[0]), '', dxy=d, num=n)
    title(pg, x0, y0 - 20, 1, vi, en, f'TL / Scale 1:{scale}', w=150)
    return pg, v

def keylist(pg, lx, ytop, w, items, head='CHÚ THÍCH / KEY', h=None):
    h = h or (len(items) * 8.4 + 12); panel(pg, lx, ytop - h, w, h, head); yy = ytop - 9
    for i, t in enumerate(items, 1):
        a, b_ = (t.split(' | ') + [''])[:2]
        pg.ax.add_patch(Circle((lx + 4, yy - 1.2), 2.1, fc='white', ec=BLUE, lw=0.6, zorder=5)); pg.ax.text(lx + 4, yy - 1.2, str(i), fontsize=5.2, ha='center', va='center', color=BLUE, fontweight='bold', zorder=6)
        pg.ax.text(lx + 8, yy, a, fontsize=4.7, va='top', zorder=5); pg.ax.text(lx + 8, yy - 3.4, b_, fontsize=4.2, va='top', color=MUTED, zorder=5); yy -= 8.4

def sheet_dev_aivan(pdf, num, tot):
    ys = [14.34, 15.30, 16.66, 18.60, 20.40, 22.22, 24.04, 25.98, 27.80, 28.28]
    tx = ['960 lưới', '1.360 lưới', '1.940 cửa', '1.800 thảm 1', '1.820 thảm 2', '1.820 thảm 3', '1.940 lưới', '1.820 thảm 4', '480']
    marks = [(((3, 15.9, 1.6),), (0, 14)), (((3, 19.5, 1.9),), (0, 14)), (((3, 17.6, 1.3),), (0, 16)), (((3, 21.3, 2.72),), (10, 8)), (((3, 25.0, 1.5),), (0, 14)), (((3, 19.2, 0.5),), (6, -14)), (((3, 21.9, 0.3),), (8, -14)), (((3, 23.2, 2.3),), (10, 10))]
    pg, v = dev_sheet(pdf, num, tot, 'DV-01', 'Khai triển tường aivan', 'Aivan wall development (looking at the building wall)', 'dev_aivan', 50, (-7.45, 7.3, -2.2, 1.9), 30.3, 14, 150,
                      marks, [((3, 28.6, TER), '±0.000'), ((3, 28.6, 0.0), '+0.450 sàn aivan'), ((3, 28.6, 2.79), '+3.240 trần aivan')],
                      [([(3, y, TER - 0.25) for y in ys], 3, -1, tx), ([(3, 14.34, TER - 0.25), (3, 28.28, TER - 0.25)], 9, -1, ['13.940'])], [])
    for ya, yb, t_ in ((14.34, 15.30, 'LƯỚI'), (15.32, 16.66, 'LƯỚI'), (16.69, 18.58, 'CỬA'), (18.60, 20.39, 'THẢM 1'), (20.41, 22.21, 'THẢM 2'), (22.23, 24.03, 'THẢM 3'), (24.06, 25.96, 'LƯỚI'), (25.99, 27.79, 'THẢM 4')):
        h_, v_ = v.P(3, (ya + yb) / 2, 2.45); v.ax.text(h_, v_, t_, fontsize=5.6, ha='center', va='center', color=BLUE, fontweight='bold', zorder=9, bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=BLUE, lw=0.5))
    keylist(pg, 14, 116, 190, ['Vách lưới sao gỗ óc chó dày 30, ô 160, nan 14, khung 60; tấm nền MDF than 5; LED hắt chân | Walnut star lattice 30 on a charcoal backing, LED at the foot',
        'Thảm treo từ sàn aivan (+0.48) tới trần (+3.20): 1.76 × 2.72 m, thanh đồng Ø24 + nẹp gỗ chân | Wall carpet deck-to-ceiling on a brass rod',
        'Cửa sảnh toà nhà (hiện trạng) — giữ nguyên | Existing hall door',
        'Trần ô hộp aivan +3.240 (xem CT-02) | Aivan coffered ceiling',
        'Ô cầu thang giữa: lưới sao (không treo thảm) | Stair bay: lattice',
        'Sofa 3 chỗ + bàn chân chữ T (CT-11) | Settees + trestle tables',
        'Ổ cắm tường +0.300 trên sàn aivan, cạnh sofa (4 vị trí) | Wall sockets +0.30',
        'Đèn chùm nhỏ kiểu mái vòm, tâm mỗi ô trần (7 bộ) | Cascade chandeliers'], h=82)
    panel(pg, 212, 34, 196, 82, 'GHI CHÚ / NOTES')
    text_block(pg, 215, 108, ['• Thứ tự từ bar tới cuối aivan: LƯỚI (bar → cửa) · CỬA · THẢM · THẢM · THẢM · LƯỚI · THẢM · lưới hẹp.',
        '• Diềm gỗ chạm phía trên thảm ĐÃ BỎ — thảm chạy hết chiều cao.',
        '• Lưới: cùng file CNC với vách hành lang (CT-07) → một mẫu cho cả hai nơi.',
        '• Thảm: thảm thật của chủ đầu tư, kích thước cắt / chọn ≈1.76 × 2.72 m; treo cách tường 15 mm.',
        '• Order from the bar: LATTICE · DOOR · CARPET ×3 · LATTICE · CARPET · narrow lattice. The carved frieze is removed.',
        '• The lattice uses the same CNC file as the corridor screens.'], fs=5.0, lh=4.8)
    pg.save(pdf)

def sheet_dev_bar(pdf, num, tot):
    marks = [(((1.4, 8.92, 0.0),), (-8, -12)), (((1.4, 9.52, 0.05),), (0, -14)), (((1.4, 11.3, 0.05),), (0, -14)), (((1.4, 13.86, 0.6),), (10, 6)), (((1.4, 10.92, 0.65),), (0, 12)),
             (((1.4, 11.66, 0.62),), (6, 14)), (((1.4, 9.57, 0.62),), (-6, 14)), (((1.4, 12.68, 0.62),), (4, 14)), (((1.4, 9.5, 1.47),), (-14, 6)), (((1.4, 12.6, 2.6),), (10, 8)), (((1.4, 11.0, 2.98),), (12, 6))]
    pg, v = dev_sheet(pdf, num, tot, 'DV-02', 'Khai triển tường bar & quầy sau', 'Bar back wall & back-bar elevation', 'dev_bar', 25, (-3.0, 3.1, -2.2, 1.65), 30.2, 14, 110,
                      marks, [((1.4, 14.4, TER), '±0.000'), ((1.4, 14.4, TER + 0.90), '+0.900 mặt bàn'), ((1.4, 14.4, TER + 1.50), '+1.500 kệ 1'), ((1.4, 14.4, TER + 1.90), '+1.900 kệ 2'), ((1.4, 14.4, TER + 2.30), '+2.300 kệ 3'), ((1.4, 14.4, 3.10), '+3.550')],
                      [([(1.4, y, TER - 0.2) for y in (8.62, 9.22, 9.82, 10.42, 12.22, 12.82, 13.42, 14.28)], 3, -1, ['600', '600', '600', '1.800', '600', '600', '860']),
                       ([(1.4, 8.62, TER - 0.2), (1.4, 14.28, TER - 0.2)], 9, -1, ['5.660'])], [])
    keylist(pg, 262, 274, 146, ['Máy làm đá dưới quầy 600 | Under-counter ice maker', 'Tủ mát cửa kính dưới quầy 600 (4 cái) | Glass-door fridges ×4', 'Tủ gỗ óc chó 3 cánh | Walnut door cabinet',
        'Tủ mát đứng cửa kính 860 × 2.050 | Tall bottle cooler', 'Máy pha espresso 2 group 750 | 2-group espresso machine', 'Máy xay cà phê ×2 + hộp gõ bã | Grinders ×2 + knock box',
        'Máy xay sinh tố ×2 | Blenders ×2', 'Bình nước trái cây kính có vòi ×2 | Glass dispensers ×2', 'Kệ gỗ óc chó dày 40 sâu 285, ke đồng, lan can đồng, LED dưới kệ | Walnut shelves on brass brackets',
        'Tường gạch ốp vàng 230×65 mạch 10 + gạch men đầu lam / ngọc xếp lưới thoi | Buff brick + glazed headers', 'Phào gỗ + nẹp đồng +3.35 | Walnut cornice'], h=106)
    panel(pg, 262, 20, 146, 142, 'GHI CHÚ / NOTES')
    text_block(pg, 265, 154, ['• Bar KHÔNG CỒN: cà phê, đồ lạnh, mocktail.', '• Mặt bàn quầy sau +0.900, sâu 550, gỗ óc chó 40.', '• Lối nhân viên giữa hai quầy: 920.',
        '• Cấp / thoát nước: máy đá, máy pha, chậu rửa', '  (quầy trước) — ống chờ theo M&E.', '• Điện: mỗi thiết bị 1 ổ riêng IP44 trên tường', '  +1.050; tủ mát ổ dưới quầy.',
        '• Kệ: 3 tầng × 3 đoạn 1.52 m; tải 25 kg/m.', '', '• Non-alcoholic bar. Worktop +0.90, 550 deep.', '• Staff aisle 920. Water / drain for the ice',
        '  maker, espresso machine and sinks by M&E.'], fs=5.0, lh=4.6)
    img_box(pg, os.path.join(REND, 'i_bar.jpg'), 265, 24, 140, 66, None)
    pg.save(pdf)

def sheet_bar2(pdf, num, tot):
    pg = Page('Quầy bar: mặt bằng, mặt trước, trạm phục vụ', 'Bar plan, counter front, waiter station', 'DV-03', num, tot)
    v = View(pg, 'det_bar_plan', 14, 186, 40, crop=(-3.5, 3.6, -1.75, 1.75))
    title(pg, 14, 180, 1, 'Mặt bằng bar (cắt +1.07)', 'Bar plan', 'TL 1:40', w=110)
    dim(v, v.P(0.72, 14.6, 0), v.P(1.64, 14.6, 0), 3, side=-1, text='920 lối NV'); dim(v, v.P(1.64, 14.6, 0), v.P(2.44, 14.6, 0), 3, side=-1, text='800')
    dim(v, v.P(0.22, 14.6, 0), v.P(0.72, 14.6, 0), 3, side=-1, text='500'); dim(v, v.P(3.2, 8.10, 0), v.P(3.2, 14.30, 0), 4, side=-1, text='6.200 quầy trước')
    dim(v, v.P(2.44, 7.9, 0), v.P(3.0, 7.9, 0), 3, side=1, text='ghế')
    for n, (p, d) in enumerate([((1.8, 8.4, 0), (4, 12)), ((1.8, 9.7, 0), (4, 12)), ((1.8, 10.4, 0), (4, 12)), ((1.8, 11.2, 0), (4, 12)), ((1.8, 11.9, 0), (4, 12)), ((1.8, 12.7, 0), (4, 12)), ((0.45, 10.9, 0), (-4, -12)), ((1.2, 8.3, 0), (-10, -8))], 1):
        tag(v, v.P(*p), '', dxy=d, num=n)
    v2 = View(pg, 'dev_barfront', 14, 126, 40, crop=(-3.4, 3.5, -0.95, 1.0), dmax=27.95, tone=True)
    title(pg, 14, 120, 2, 'Mặt trước quầy (nhìn từ sảnh)', 'Counter front from the hall', 'TL 1:40', w=110)
    for z, t in ((TER, '±0.000'), (TER + 1.05, '+1.050 mặt quầy')): level(v2, *v2.P(3, 14.5, z), t, side=1, fs=4.8)
    v3 = View(pg, 'dev_station', 14, 30, 30, crop=(-2.2, 2.3, -1.4, 1.1), dmax=30.2, tone=True)
    title(pg, 14, 24, 3, 'Trạm phục vụ (nhìn từ sảnh)', 'Waiter station from the hall', 'TL 1:30', w=110)
    keylist(pg, 205, 274, 203, ['Thu ngân POS + ngăn kéo | POS + drawer', 'Thùng rác 2 ngăn | Bins', 'Khay đá + thanh siro (speed rail) | Ice well + syrup rail', 'Máy rửa ly dưới quầy 600 | Glass washer',
        'Chậu rửa đôi + chậu rửa tay | Double sink + hand sink', 'Tủ mát dưới quầy ×2 | Under-counter fridges ×2', 'Quầy sau: thiết bị pha chế (xem DV-02) | Back bar equipment', 'Lối vào nhân viên từ phía nam, rộng 740 | Staff entry from the south, 740 clear'], h=80)
    panel(pg, 205, 20, 203, 170, 'GHI CHÚ / NOTES')
    text_block(pg, 208, 182, ['QUẦY TRƯỚC / FRONT COUNTER', '• Dài 6.200, sâu 800; hai cao độ: mặt khách gỗ óc chó +1.050 (rộng 460), mặt làm việc inox +0.900 (rộng 360).',
        '• Mặt trước: gạch ốp vàng 230×65 mạch 10, gạch men đầu lam / ngọc xếp lưới thoi — cùng loại với tường bar.',
        '• Chân đế đen lùi 100, thanh gác chân đồng Ø48 cao +220, 10 ghế bar bước 620.', '',
        'TRẠM PHỤC VỤ / WAITER STATION', '• Quầy 2.800 × 600 × 940: thân gỗ óc chó, mặt trước nan gỗ / terracotta rãnh, mặt đá trắng 40.',
        '• Trên mặt: POS, 3 ống đựng dao nĩa đồng, chồng khay, 2 bình nước. Phía nhân viên: 4 cánh tủ.',
        '• Sau lưng: 3 tủ chạm sát tường (ly, đĩa, khăn) cao 2.150; vách lưới che phía sảnh cao 1.680.', '',
        '• Front counter 6.20 × 0.80, two levels (+1.05 guest top, +0.90 stainless work shelf); face in the same brick as the back wall.',
        '• Waiter station: walnut pass counter 2.80 × 0.60 × 0.94 with a white stone top; three carved wall cabinets behind it.'], fs=5.0, lh=4.8)
    pg.save(pdf)

def sheet_dev_booths(pdf, num, tot):
    YB = [18.86 + 2.4 * k for k in range(8)]; names = ['Samarkand', 'Bukhara', 'Khiva', 'Khujand', 'Penjikent', 'Tashkent', 'Margilan']
    pg, v = dev_sheet(pdf, num, tot, 'DV-04', 'Khai triển dãy cabin (nhìn từ sảnh)', 'Booth row development (from the hall aisle)', 'dev_booths', 50, (-8.9, 8.9, -1.85, 1.75), 40.8, 14, 160,
                      [(((7, 20.06, 1.75),), (0, 14)), (((7, 22.46, 0.9),), (0, 22)), (((7, 23.66, 1.0),), (0, 22)), (((7, 26.06, -0.37),), (0, -14)), (((7, 27.26, 1.6),), (6, 16)), (((7, 30.9, 1.95),), (8, 12))],
                      [((7, 18.5, TER), '±0.000'), ((7, 18.5, TER + 0.15), '+0.150 bục'), ((7, 18.5, 2.0), '+2.450 đỉnh cabin')],
                      [([(7, y, TER - 0.2) for y in YB], 3, 1, ['2.400'] * 7), ([(7, YB[0], TER - 0.2), (7, YB[-1], TER - 0.2)], 9, 1, ['16.800 = 7 × 2.400'])], [])
    for k, nm in enumerate(names):
        h, vv = v.P(7, YB[k] + 1.2, TER - 0.75); v.ax.text(h, vv, f'{k + 1} · {nm}', fontsize=5.4, ha='center', va='center', color=INK, fontweight='bold', zorder=8)
    keylist(pg, 14, 122, 190, ['Bảng tên gỗ óc chó chữ đồng trên lanh-tô | Name board on the lintel', 'Rèm nhung 2 tấm / cabin, thanh đồng Ø24, vòng vén đồng | Velvet curtains, brass rod, tie-backs',
        'Vách ngăn: tấm ĐÚC SẴN 1.950 × 2.450 — khung gỗ 45×70, lõi MDF than 18, lưới sao óc chó 40 hai mặt | Prefab partition panel, star lattice both faces',
        'Bục +0.150: khung gỗ, mặt dựng óc chó + nẹp đồng | Podium +0.150', 'Trụ 70×70 có đế đồng cao 100; mũ gỗ trên lanh-tô | Posts with brass shoes; cornice cap',
        'Trần lưới sao +2.400 (cùng mẫu vách) | Lattice ceiling +2.40'], h=66)
    panel(pg, 212, 56, 196, 66, 'GHI CHÚ / NOTES')
    text_block(pg, 215, 114, ['• 7 cabin GIỐNG HỆT NHAU: 2.400 × 1.950, cao 2.450. Một bộ bản vẽ gia công dùng cho cả 7.', '• Một mẫu lưới (sao, ô 300) cho vách và trần → một file CNC.',
        '• Cabin lùi dần theo đường phố (mỗi cabin lệch ≈ 237 mm) — xem KT-03.', '• Khác nhau giữa các cabin: màu rèm, màu gạch viền bục, bảng tên.',
        '• 7 identical modules 2.40 × 1.95 × 2.45; one lattice pattern for walls and ceilings; they step with the street line.'], fs=5.0, lh=4.8)
    img_box(pg, os.path.join(REND, 'i_booth.jpg'), 212, 20, 196, 0.001, None) if False else None
    pg.save(pdf)

def sheet_dev_photo(pdf, num, tot):
    XC = 6.86
    marks = [(((XC, 5.9, 2.15),), (10, 10)), (((XC + 0.9, 5.9, 1.8),), (14, 6)), (((XC, 5.9, 0.9),), (16, 0)), (((XC + 1.6, 5.9, 0.9),), (10, -4)), (((XC, 5.9, 0.1),), (-16, -6)), (((XC, 5.9, 1.75),), (-16, 8)), (((XC - 1.0, 5.9, -0.3),), (-10, -8)), (((XC, 5.9, -0.25),), (10, -10))]
    pg, v = dev_sheet(pdf, num, tot, 'DV-05', 'Khu chụp ảnh (majlis): khai triển tường nam', 'Photo zone (majlis): south wall elevation', 'dev_photo', 25, (-3.1, 3.1, -2.0, 1.9), 29.2, 14, 110,
                      marks, [((XC + 2.95, 5.9, TER), '±0.000'), ((XC + 2.95, 5.9, TER + 1.55), '+1.550 chân vòm'), ((XC + 2.95, 5.9, TER + 2.50), '+2.500 đỉnh vòm'), ((XC + 2.95, 5.9, TER + 2.79), '+2.790 phào')],
                      [([(XC - 1.31, 5.9, TER - 0.15), (XC - 1.15, 5.9, TER - 0.15), (XC + 1.15, 5.9, TER - 0.15), (XC + 1.31, 5.9, TER - 0.15)], 3, -1, ['160', '2.300 thông thuỷ', '160'])], [])
    keylist(pg, 262, 274, 146, ['Vòm nhọn gỗ óc chó: bản 130, dày 120 | Pointed walnut arch 130 × 120', 'Góc vòm: lưới sao óc chó 40 (ô 140) | Star-lattice spandrels',
        'Thảm treo giữa vòm (thảm của chủ đầu tư) | Hanging carpet on the axis', 'Rèm nhung đỏ rượu xếp ly hai bên | Wine velvet drape',
        'Sofa chạm 3 chỗ 1.660 (cùng mẫu aivan) | Carved 3-seat settee', 'Đèn chùm kiểu mái vòm Ø600, đúng trục | Cascade chandelier Ø600 on the axis',
        'Đệm ngồi sàn 800×800 ×4, đôn ×4 | Floor cushions ×4, poufs ×4', 'Bàn thấp 870×870 trên thảm | Low table'], h=82)
    panel(pg, 262, 20, 146, 166, 'GHI CHÚ / NOTES')
    text_block(pg, 265, 178, ['• Mọi thứ đối xứng qua một trục: vòm — thảm —', '  sofa — đèn chùm — bàn thấp.', '• Vòm đứng độc lập trước rèm, chân bọc đồng', '  cao 120, neo sàn 2 bu lông M10 / chân.',
        '• Phào gỗ 70 trên đỉnh vòm +2.790.', '• Lưới góc vòm: cùng mẫu sao (CNC).', '', '• Everything sits on one axis: arch — carpet —', '  settee — chandelier — low table.',
        '• Free-standing arch in front of the drape,', '  brass shoes, 2 × M10 anchors per foot.'], fs=5.0, lh=4.6)
    img_box(pg, os.path.join(REND, 'i_photo.jpg'), 265, 24, 140, 74, None)
    pg.save(pdf)

def sheet_north(pdf, num, tot):
    pg = Page('Khu bắc: bàn, lều, tapchan, hồ sao — mặt bằng & cắt lều', 'North zone: tables, tents, tapchan, star pool — plan & tent section', 'DV-06', num, tot)
    v = View(pg, 'det_north', 14, 122, 40, crop=(-3.7, 3.8, -2.7, 2.7))                       # h = y - 33.3, v = -(x - 5.3)
    title(pg, 14, 116, 1, 'Mặt bằng khu bắc', 'North zone plan', 'TL 1:40', w=120)
    dim(v, v.P(4.11, 33.1, 0), v.P(4.90, 33.1, 0), 3, side=1, text='790'); dim(v, v.P(6.30, 33.1, 0), v.P(7.12, 33.1, 0), 3, side=1, text='≈820')
    dim(v, v.P(6.6, 32.60, 0), v.P(6.6, 33.60, 0), 3, side=1, text='1.000'); dim(v, v.P(4.6, 29.2, 0), v.P(5.37, 29.2, 0), 3, side=-1, text='≥800'); dim(v, v.P(6.77, 29.2, 0), v.P(7.6, 29.2, 0), 3, side=-1, text='≥800')
    dim(v, v.P(5.37, 30.5, 0), v.P(6.77, 30.5, 0), 3, side=1, text='1.400 hồ sao')
    for n, (p, d) in enumerate([((5.6, 31.67, 0), (0, -14)), ((5.6, 33.1, 0), (-10, 10)), ((2.75, 32.3, 0), (0, 12)), ((3.5, 29.6, 0), (-4, 12)), ((6.07, 29.65, 0), (10, -10)), ((4.32, 36.0, 0), (-8, 8)), ((8.2, 34.4, 0), (8, 8))], 1):
        tag(v, v.P(*p), '', dxy=d, num=n)
    v2 = View(pg, 'det_tent', 240, 150, 30, crop=(-2.0, 2.0, -1.85, 2.05), dmax=65.3)
    title(pg, 240, 144, 2, 'Mặt cắt lều', 'Tent section', 'TL 1:30', w=110)
    for z, t in ((TER, '±0.000'), (TER + 2.25, '+2.250 vành'), (TER + 2.95, '+2.950 đỉnh')): level(v2, *v2.P(4.5, 32.3, z), t, side=1, fs=4.8)
    dim(v2, v2.P(1.39, 32.3, TER - 0.15), v2.P(4.11, 32.3, TER - 0.15), 3, side=-1, text='2.720')
    keylist(pg, 14, 106, 216, ['Bàn 4 chỗ 1.400 × 800 (2 bàn = 8 chỗ), cách nhau 1.000 | Two 4-top tables, 1.00 m apart', 'Đèn trống đồng đục lỗ Ø900 × 380, 3 ty treo, đáy +2.300 | Pierced brass drum Ø900',
        'Lều majlis 2.720 × 2.800 (2 lều × 8 chỗ ngồi đệm) | Majlis tents', 'Tapchan 2.000 × 2.200, sát lan can chiếu nghỉ aivan | Tapchan',
        'Hồ sao 8 cánh thu nhỏ còn 1.400 (trước 1.900) → lối hai bên ≥ 800 | Star pool reduced to 1.40 m', 'Chậu cây đất nung cạnh cổng bắc (ngoài luồng đi) | Pots by the north gate', 'Cabin 6–7 | Booths 6–7'], h=84)
    panel(pg, 240, 20, 168, 118, 'KHUNG LỀU / TENT FRAME')
    text_block(pg, 243, 130, ['• 4 trụ gỗ 60×60 cao 2.250 (hoặc thép hộp 50 bọc gỗ), đế đồng.', '• Vành trên 60×40 nối 4 trụ; 4 thanh kèo 40×40 lên khối đỉnh 100×100.',
        '• Mái bạt canvas kem may sẵn, luồn dây vào kèo; diềm nhung răng cưa.', '• 3 mặt vách bạt căng giữa trụ; mặt đông mở, rèm buộc hai bên.',
        '• Sàn: thảm + đệm ngồi; bàn bát giác thấp; 2 đèn chùm nhỏ / lều.', '', '• 4 posts 60×60, top ring 60×40, 4 hip rafters 40×40 to an apex block;',
        '  sewn canvas canopy laced to the rafters; three canvas walls, open east side.', '',
        'KÊNH NƯỚC ĐÃ BỎ — sàn đá liền; lối đi tối thiểu trong khu: 800 mm.', 'The water channel is removed; minimum aisle in this zone 800 mm.'], fs=5.0, lh=4.8)
    pg.save(pdf)
