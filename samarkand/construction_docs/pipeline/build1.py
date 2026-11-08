"""sheets 1..8: cover, general, zoning, furniture plan (sheets_plans), floor finishes, RCP + lighting, roof structure"""
from lib import *
from sheets_plans import D, YAX, XAX, streetx, grids, sheet_plan
from matplotlib.patches import Polygon as MP
REND = os.path.join(os.path.dirname(__file__), 'renders')

def img_box(pg, path, x, y, w, h, cap=None):
    if not os.path.exists(path): return
    im = Image.open(path).convert('RGB'); iw, ih = im.size; tr = w / h
    if iw / ih > tr: nw = int(ih * tr); im = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else: nh = int(iw / tr); im = im.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    ax = pg.fig.add_axes([x / 420, y / 297, w / 420, h / 297]); ax.imshow(np.asarray(im)); ax.axis('off')
    if cap: pg.ax.text(x, y - 3, cap, fontsize=6.2, color=MUTED, va='top')

def sheet_cover(pdf, num, tot):
    fig = plt.figure(figsize=(420 * MM, 297 * MM), dpi=300); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis('off')
    ax.add_patch(Rectangle((0, 0), 420, 297, color=PAPER))
    class P_: pass
    pg = P_(); pg.fig = fig; pg.ax = ax
    img_box(pg, os.path.join(REND, 'r_street.jpg'), 12, 64, 396, 150)
    ax.text(210, 262, 'SAMARKAND', fontfamily=SERIF, fontsize=40, fontweight='bold', color='#16264d', ha='center', va='center')
    ax.text(210, 245, 'NHÀ HÀNG ẨM THỰC TRUNG Á · CENTRAL ASIAN RESTAURANT', fontsize=12, color=GREEN_D, ha='center', va='center')
    ax.text(210, 234, 'HỒ SƠ THIẾT KẾ THI CÔNG NỘI THẤT & KIẾN TRÚC CẢNH QUAN SÂN HIÊN · CONSTRUCTION DRAWING SET', fontsize=9, ha='center', va='center')
    ax.text(210, 224, 'Sân hiên 446 m² · 152 chỗ trong nhà · Đà Nẵng, Việt Nam', fontsize=8, color=MUTED, ha='center', va='center')
    ax.plot([60, 360], [56, 56], color=INK, lw=1.2)
    ax.text(210, 47, 'Phiên bản / Revision R12-v11.7  ·  Tháng 11 / 2026  ·  Khổ A3 — tỷ lệ in đúng khi in 100 % / print at 100 % on A3', fontsize=7.5, ha='center')
    ax.text(210, 38, 'Tài liệu dùng cho đội thi công: mọi kích thước bằng mm (cao độ bằng m), kiểm tra tại hiện trường trước khi gia công.', fontsize=7, ha='center', color=MUTED)
    ax.text(210, 31, 'For the construction team: all dimensions in mm (levels in m) — verify on site before fabrication.', fontsize=7, ha='center', color=MUTED)
    pdf.savefig(fig, facecolor=PAPER); plt.close(fig)

INDEX = [('KT-00', 'Bìa / Cover'), ('KT-01', 'Thông tin chung, ghi chú, danh mục / General notes & index'), ('KT-02', 'Mặt bằng phân khu & diện tích / Zoning & areas'),
         ('KT-03', 'Mặt bằng bố trí nội thất & kích thước / Furniture & dimension plan'), ('KT-04', 'Mặt bằng hoàn thiện sàn / Floor finishes plan'),
         ('KT-05', 'Mặt bằng trần & chiếu sáng / Reflected ceiling & lighting'), ('KT-06', 'Mặt bằng kết cấu mái / Roof framing plan'),
         ('KT-07', 'Mặt đứng / Elevations'), ('KT-08', 'Mặt cắt A-A, B-B, C-C / Sections'),
         ('CT-01', 'Chi tiết cột Samarkand & cổng pishtaq / Column & pishtaq'), ('CT-02', 'Chi tiết aivan / Aivan'), ('CT-03', 'Chi tiết cabin VIP / Booths'),
         ('CT-04', 'Chi tiết trần ô hộp / Ceiling coffers'), ('CT-05', 'Chi tiết mái vòm / Dome'), ('CT-06', 'Chi tiết quầy bar / Bar'),
         ('CT-07', 'Chi tiết hành lang vòm / Arcade corridor'), ('CT-08', 'Chi tiết diềm mái mặt tiền / Street eave'), ('CT-09', 'Chi tiết khu mangal / Mangal'),
         ('CT-10', 'Chi tiết sàn đá & gạch / Floor details'), ('CT-11', 'Nội thất: ghế, sofa, bàn / Furniture'), ('BV-01', 'Bảng vật liệu hoàn thiện / Finishes schedule'),
         ('BV-02', 'Bảng chiếu sáng & điện / Lighting & power schedule'), ('PC-01', 'Phối cảnh / Perspectives 1'), ('PC-02', 'Phối cảnh / Perspectives 2')]

def sheet_general(pdf, num, tot):
    pg = Page('Thông tin chung & ghi chú kỹ thuật', 'General information, notes & drawing index', 'KT-01', num, tot)
    panel(pg, 12, 150, 130, 124, 'THÔNG TIN DỰ ÁN / PROJECT DATA')
    rows = [['Dự án / Project', 'SAMARKAND — nhà hàng Trung Á'], ['Địa điểm / Site', 'Sân hiên trệt, Đà Nẵng'], ['Hạng mục / Scope', 'Nội thất, mái che, cảnh quan sân hiên'],
            ['Diện tích / Area', '446 m² (gồm sân hiên)'], ['Chiều dài mặt tiền', '37,1 m dọc phố'], ['Sức chứa / Seats', '152 trong nhà + ~30 ghế phố'],
            ['Cao độ chuẩn / Datum', '±0.000 = sàn hoàn thiện sân hiên'], ['Aivan / Cabin', '+0.450 / +0.150'], ['Mái / Roof', 'Klip-Lok dốc 3,5 % ra phố'],
            ['Đỉnh mái vòm / Dome', '+5.94 (đỉnh alem +7.85)'], ['Mô hình 3D / Model', 'R12-v11.7 (viewer + Blender)']]
    table(pg, 15, 266, ['Mục / Item', 'Thông số / Data'], rows, [42, 82], fs=5.2, rh=4.5)
    panel(pg, 148, 150, 128, 124, 'GHI CHÚ CHUNG / GENERAL NOTES')
    notes = ['1. Kích thước bằng mm, cao độ bằng m. Không đo trên bản vẽ — dùng số ghi.', '   Dimensions in mm, levels in m. Do not scale — use written dimensions.',
             '2. Nhà thầu kiểm tra hiện trạng (cột, dầm, sàn, cửa toà nhà) trước khi gia công.', '   Verify existing building, slab and openings before fabrication.',
             '3. Kết cấu thép (cột 150×150, dầm I300×150, xà gồ) — kỹ sư kết cấu', '   duyệt tiết diện & liên kết trước khi thi công.',
             '4. Gỗ: óc chó / gỗ tự nhiên sấy ≤12 %, xử lý chống mối mọt, sơn PU mờ.', '   Walnut / kiln-dried hardwood ≤12 % MC, anti-termite, matt PU.',
             '5. Gạch men / gạch ốp: keo dán C2TE, ron epoxy 2–3 mm.', '   Glazed tiles & brick slips: C2TE adhesive, 2–3 mm epoxy grout.',
             '6. Vải bọc & rèm: chống cháy (BS 5867 / tương đương), giặt được.', '   Upholstery & curtains: flame-retardant, washable.',
             '7. Điện: TCVN / IEC; ổ cắm sàn IP44, đèn ngoài trời IP65, RCBO 30 mA.', '   Electrical to TCVN/IEC; floor boxes IP44, outdoor IP65.',
             '8. PCCC: lối thoát ≥1,0 m, không cản trở bởi rèm / chậu cây.', '   Escape routes ≥1.0 m clear of curtains & planters.',
             '9. Mọi mẫu vật liệu được chủ đầu tư duyệt trước khi đặt hàng.', '   All samples approved by the owner before ordering.']
    text_block(pg, 151, 265, notes, fs=5.0, lh=4.4)
    panel(pg, 282, 150, 126, 124, 'DANH MỤC BẢN VẼ / DRAWING INDEX')
    table(pg, 285, 266, ['Số / No.', 'Tên bản vẽ / Title'], [[c, t] for c, t in INDEX], [16, 104], fs=4.7, rh=4.35)
    panel(pg, 12, 20, 196, 124, 'KÝ HIỆU / SYMBOLS')
    ax = pg.ax; y = 128
    sy = [('grid', 'Trục định vị / Grid axis'), ('level', 'Cao độ hoàn thiện / Finished level'), ('dim', 'Đường kích thước (mm) / Dimension'), ('cut', 'Phần bị cắt / Cut element (poché)'),
          ('bub', 'Số hiệu khu / Zone or item tag'), ('sec', 'Vị trí mặt cắt / Section mark')]
    for k, t in sy:
        if k == 'grid':
            ax.plot([20, 45], [y, y], color='#8a8a8a', lw=0.5, ls=(0, (8, 2, 1, 2))); ax.add_patch(Circle((49, y), 3, fc='white', ec=INK, lw=0.6)); ax.text(49, y, '3', ha='center', va='center', fontsize=6, fontweight='bold')
        elif k == 'level':
            ax.add_patch(MP([[30, y - 1], [28.5, y + 1], [31.5, y + 1]], closed=True, fc=BLUE)); ax.plot([30, 48], [y + 1, y + 1], color=BLUE, lw=0.4); ax.text(32, y + 1.8, '+0.450', fontsize=5, color=BLUE)
        elif k == 'dim':
            ax.plot([20, 48], [y, y], color=RED, lw=0.45)
            for xx in (20, 48): ax.plot([xx - 1, xx + 1], [y - 1, y + 1], color=RED, lw=0.8)
            ax.text(34, y + 1.5, '2.400', color=RED, fontsize=5, ha='center')
        elif k == 'cut': ax.add_patch(Rectangle((22, y - 2), 24, 4, fc='#262626'))
        elif k == 'bub': ax.add_patch(Circle((34, y), 2.6, fc='white', ec=BLUE, lw=0.6)); ax.text(34, y, '4', ha='center', va='center', fontsize=6, color=BLUE, fontweight='bold')
        else:
            ax.plot([22, 46], [y, y], color=INK, lw=0.9, ls=(0, (6, 2))); ax.add_patch(MP([[46, y], [42, y + 2], [42, y - 2]], closed=True, fc=INK)); ax.text(48, y, 'A', fontsize=6, fontweight='bold', va='center')
        ax.text(58, y, t, fontsize=5.6, va='center'); y -= 9
    text_block(pg, 110, 128, ['VIẾT TẮT / ABBREVIATIONS', 'FFL — cao độ sàn hoàn thiện / finished floor level', 'SHS — thép hộp vuông / square hollow section',
                              'MDF — ván sợi mật độ trung bình', 'LED 2700K — đèn ánh sáng vàng ấm', 'IP44 / IP65 — cấp bảo vệ thiết bị điện', 'CT — chi tiết / detail',
                              'TL — tỷ lệ / scale', 'VL — vật liệu / material'], fs=5.2, lh=4.3, bold_first=True)
    panel(pg, 214, 20, 194, 124, 'NGUYÊN TẮC THIẾT KẾ / DESIGN INTENT')
    text_block(pg, 217, 128, ['«Con đường tơ lụa trên một bàn ăn» — gỗ chạm khắc, men lam, thảm dệt tay và ánh đồng ấm của Samarkand & Bukhara.',
                              'Mọi bề mặt hoa văn là VẬT LIỆU THẬT (gạch, gạch men, gỗ chạm), không dùng ảnh in / decal.',
                              'Every pattern is built from real material — brick, glazed tile, carved timber — never printed decals.', '',
                              'Ưu tiên công thái học: lối đi ≥ 930 mm, mép ghế — mép bàn 80–190 mm, chân bàn đặt giữa (bàn chân chữ T),',
                              'ghế sofa 700 mm / người trong cabin, chiều cao bàn 750 mm, ghế 450–500 mm.',
                              'Ergonomics: aisles ≥ 930, seat-to-table 80–190, centred trestle legs, 700 per sitter in booths.', '',
                              'Khí hậu biển Đà Nẵng: inox 316 cho phụ kiện ngoài trời, gỗ xử lý chống ẩm, vải ngoài trời giới hạn',
                              '(chỉ dải rèm buộc), mọi đèn ngoài trời IP65.', 'Coastal climate: SS316 outdoor fixings, sealed timber, minimal loose fabric, IP65 outdoors.'], fs=5.3, lh=4.4)
    pg.save(pdf)

ZONES = [('Bar', '#e9c48f', [(0.14, 7.7), (3.3, 7.7), (3.3, 15.3), (0.14, 15.3)]), ('Sảnh chính / Hall', '#f4e6c8', [(3.3, 8.6), (9.3, 8.6), (9.3, 15.6), (7.6, 15.6), (7.6, 30.9), (3.3, 30.9), (3.3, 15.3)]),
         ('Aivan', '#d7b98f', [(0, 15.3), (3.3, 15.3), (3.3, 30.9), (0, 30.9)]), ('Cabin VIP', '#c9a3a3', [(8.5, 18.9), (10.47, 18.9), (9.05, 35.62), (7.17, 35.62)]),
         ('Lều & tapchan', '#b9c9a5', [(1.4, 28.5), (4.6, 28.5), (4.6, 36.7), (1.4, 36.7)]), ('Majlis & pergola', '#cdb8d8', [(3.1, 1.0), (9.4, 1.0), (9.4, 8.3), (3.1, 8.3)]),
         ('Mangal', '#e3a58c', [(9.4, 3.2), (12.3, 3.2), (12.3, 9.0), (9.4, 9.0)]), ('Hành lang vòm / Corridor', '#a9c4d9', [(7.67, 15.64), (10.4, 15.64), (10.4, 17.96), (7.67, 17.96)]),
         ('Khu trẻ em / Kids', '#f2d36b', [(-7.1, 0.3), (-0.15, 0.3), (-0.15, 4.1), (-7.1, 4.1)]), ('Bukhara dome / lối ra', '#b7d3c3', [(4.9, 31.0), (7.6, 31.0), (7.6, 36.6), (4.9, 36.6)])]
def poly_area(P): x = np.array([p[0] for p in P]); y = np.array([p[1] for p in P]); return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
def sheet_zoning(pdf, num, tot):
    pg = Page('Mặt bằng phân khu chức năng & diện tích', 'Zoning, circulation & area schedule', 'KT-02', num, tot)
    v = View(pg, 'plan', 17, 40, 100, crop=(-19.3, 19.3, -11.2, 10.4))
    for i, (n, col, P) in enumerate(ZONES):
        v.ax.add_patch(MP([v.P(x, y, 0) for x, y in P], closed=True, fc=col, ec=col, alpha=0.42, lw=0.6, zorder=2))
        cx = np.mean([p[0] for p in P]); cy = np.mean([p[1] for p in P]); bubble(v, *v.P(cx, cy, 0), str(i + 1), r=3, col=GREEN_D, fs=6.5)
    # circulation: main path street -> pishtaq -> corridor -> dome -> aivan
    path = [(13.0, 16.8), (10.4, 16.8), (7.6, 16.8), (6.0, 18.2), (4.3, 20.0), (3.6, 21.6)]
    pts = [v.P(x, y, 0) for x, y in path]
    v.ax.plot([p[0] for p in pts], [p[1] for p in pts], color=RED, lw=1.4, ls=(0, (6, 3)), zorder=6)
    v.ax.annotate('', xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle='-|>', color=RED, lw=1.2), zorder=6)
    tag(v, v.P(12.6, 16.8, 0), 'LỐI VÀO CHÍNH / MAIN ENTRANCE', dxy=(10, -14), col=RED, fs=5.5)
    grids(v)
    title(pg, 17, 33, 1, 'Mặt bằng phân khu', 'Zoning & circulation plan', 'TL / Scale 1:100', w=120); north(pg, 145, 31, ang=180); scalebar(pg, 160, 31, 100, 5)
    rows = [[f'{i + 1}', n, f'{poly_area(P):.1f}'] for i, (n, c, P) in enumerate(ZONES)]
    table(pg, 210, 37, ['#', 'Khu / Zone', 'm²'], rows[:5], [6, 50, 14], fs=4.6, rh=3.3); table(pg, 290, 37, ['#', 'Khu / Zone', 'm²'], rows[5:], [6, 50, 14], fs=4.6, rh=3.3)
    pg.ax.text(372, 34, 'Tổng sân hiên / Terrace total\n≈ 446 m²', fontsize=6, fontweight='bold', va='top')
    pg.save(pdf)

FLOORS = [('F1', 'Đá marble trắng 500×500 lát chéo 45°, viền men cobalt 90 + kim cương khảm', 'White marble 500×500 on 45°, 90 cobalt band, inlaid diamonds', '#f2efe8'),
          ('F2', 'Gạch zellige sao 8 cánh (lối hành lang) 160 / 200 module', 'Zellige 8-point star runner (corridor path)', '#9fc0de'),
          ('F3', 'Gạch nung 300×150 xếp «chong chóng» + gạch men 150', 'Terracotta 300×150 pinwheel + 150 glazed inserts (aivan)', '#d9a07f'),
          ('F4', 'Bục cabin: gỗ óc chó + thảm Ba Tư', 'Booth podium: walnut riser + Persian rug', '#a97b5a'),
          ('F5', 'Sàn cao su EPDM 500×500 (khu trẻ em)', 'EPDM rubber tiles 500×500 (kids)', '#f2d36b'),
          ('F6', 'Đá slate chống trơn (khu mangal)', 'Anti-slip slate (mangal)', '#8c8c8c'),
          ('F7', 'Gạch terracotta & zellige (sân phố, hauz)', 'Terracotta & zellige (street court, hauz)', '#cf8f6a')]
def sheet_floor(pdf, num, tot):
    pg = Page('Mặt bằng hoàn thiện sàn', 'Floor finishes plan', 'KT-04', num, tot)
    v = View(pg, 'floorplan', 17, 40, 100, crop=(-19.3, 19.3, -11.2, 10.4))
    for code, x, y in [('F1', 6.0, 10.0), ('F1', 5.8, 26.0), ('F2', 9.0, 16.8), ('F3', 1.5, 22.0), ('F4', 8.6, 31.5), ('F5', -3.6, 2.5), ('F6', 10.8, 5.5), ('F7', 11.4, 33.0), ('F1', 2.0, 33.5)]:
        bx, by = v.P(x, y, 0); k = 1 / v.mpu
        v.ax.add_patch(FancyBboxPatch((bx - 4 * k, by - 2.2 * k), 8 * k, 4.4 * k, boxstyle='round,pad=0', fc='white', ec=GREEN_D, lw=0.7, zorder=8))
        v.ax.text(bx, by, code, fontsize=6.5, fontweight='bold', ha='center', va='center', color=GREEN_D, zorder=9)
    grids(v)
    title(pg, 17, 33, 1, 'Mặt bằng hoàn thiện sàn', 'Floor finishes plan', 'TL / Scale 1:100', w=120); north(pg, 145, 31, ang=180)
    y = 37
    for code, vi, en, col in FLOORS:
        pg.ax.add_patch(Rectangle((160, y - 3), 6, 3, fc=col, ec=INK, lw=0.3)); pg.ax.text(168, y - 1.5, f'{code}  {vi}  —  {en}', fontsize=4.9, va='center'); y -= 3.6
    pg.save(pdf)

def sheet_rcp(pdf, num, tot):
    pg = Page('Mặt bằng trần & bố trí chiếu sáng', 'Reflected ceiling & lighting plan', 'KT-05', num, tot)
    v = View(pg, 'rcp', 17, 40, 100, crop=(-19.3, 19.3, -10.4, 11.2), flip=True)
    k = 1 / v.mpu
    for n, x, y, lab in [('C1', 6.0, 26.0, 'C1'), ('C2', 5.0, 9.2, 'C2'), ('C3', 6.0, 31.5, 'C3'), ('C4', 2.0, 12.0, 'C4')]:
        bx, by = v.P(x, y, 3); v.ax.add_patch(Circle((bx, by), 3 * k, fc='white', ec=GREEN_D, lw=0.7, zorder=8)); v.ax.text(bx, by, lab, fontsize=5.5, ha='center', va='center', color=GREEN_D, fontweight='bold', zorder=9)
    for o in D['chandelier']:
        cx, cy = (o[1][0] + o[2][0]) / 2, (o[1][1] + o[2][1]) / 2
        bx, by = v.P(cx, cy, 3); v.ax.add_patch(Circle((bx, by), 1.6 * k, fc='none', ec=RED, lw=0.8, zorder=8)); v.ax.plot([bx - 1.6 * k, bx + 1.6 * k], [by, by], color=RED, lw=0.5, zorder=8); v.ax.plot([bx, bx], [by - 1.6 * k, by + 1.6 * k], color=RED, lw=0.5, zorder=8)
    for txt, x, y in [('+3.36 … +3.12  đáy trần ô hộp (theo dốc mái)', 6.0, 23.0), ('+3.47  trần aivan', 1.6, 17.0), ('+2.40  trần cabin (lam gỗ)', 8.6, 22.0), ('Mái vòm Ø5.2 — đỉnh +5.94', 6.0, 19.9)]:
        level(v, *v.P(x, y, 3), txt, fs=4.8)
    grids(v)
    title(pg, 17, 33, 1, 'Mặt bằng trần (nhìn xuống)', 'Reflected ceiling plan (looking down)', 'TL / Scale 1:100', w=120); north(pg, 145, 31, ang=180)
    leg = [['C1', 'Ô hộp gỗ 1,2 × 1,2 m, thảm Ba Tư, LED hắt 2700K', 'Walnut coffer + carpet + hidden LED'], ['C2', 'Hộp nan gỗ hạ 150, LED phía sau', 'Dropped timber slat box, back-lit'],
           ['C3', 'Ô thảm + sườn chéo gỗ', 'Carpet coffer with diagonal ribs'], ['C4', 'Ô sâu (khung hạ 100) + sườn chéo', 'Deep coffer + ribs'], ['⊕', 'Đèn chùm kiểu mái vòm (cầu đồng đục lỗ)', 'Dome-style cascade chandelier']]
    table(pg, 160, 38, ['Mã', 'Mô tả / Description (VI)', 'EN'], leg, [8, 80, 62], fs=4.6, rh=3.4)
    pg.save(pdf)

def sheet_roof(pdf, num, tot):
    pg = Page('Mặt bằng kết cấu mái & lưới trục', 'Roof framing plan & structural grid', 'KT-06', num, tot)
    v = View(pg, 'roof', 17, 40, 100, crop=(-19.3, 19.3, -11.2, 10.4))
    grids(v)
    for o in D['steel_col'] + D['dome_col']:
        cx, cy = (o[1][0] + o[2][0]) / 2, (o[1][1] + o[2][1]) / 2; tag(v, v.P(cx, cy, 3), '', dxy=(3, 3))
    tag(v, v.P(6.0, 25.6, 3.2), 'Dầm thép I300×150 (dốc 3,5 %) / steel beam', dxy=(10, -10))
    tag(v, v.P(6.76, 30.0, 3.3), 'Xà gồ thép C200×80 @1000 / purlins', dxy=(14, 8))
    tag(v, v.P(6.0, 17.4, 3.1), 'Dầm vòng mái vòm (thép hộp) / dome ring girder', dxy=(-10, 10))
    tag(v, v.P(6.0, 11.2, 3.5), 'Khung giếng trời 3,0 × 3,0 / skylight frame', dxy=(-14, -9))
    tag(v, v.P(0.1, 26.0, 3.3), 'Dầm biên + móc treo vào sàn tầng 2 toà nhà / ledger + hangers', dxy=(10, 6))
    tag(v, v.P(streetx(29.1), 29.1, 2.8), 'Cột thép SHS150×150 bọc gạch (cột Samarkand)', dxy=(8, -10))
    tag(v, v.P(4.13, 18.3, 3.0), 'Cột mái vòm SHS150 bọc gỗ', dxy=(-12, 8))
    title(pg, 17, 33, 1, 'Mặt bằng kết cấu mái', 'Roof framing plan (roof sheeting removed)', 'TL / Scale 1:100', w=120); north(pg, 145, 31, ang=180)
    rows = [['K1', 'Cột thép SHS 150×150×6, đế 300×300×16, 4 bu lông M16', '7+4'], ['K2', 'Dầm I300×150×6.5×9, liên kết bản mã 10', '12'], ['K3', 'Xà gồ C200×80×2.5 @1000', '20'],
            ['K4', 'Dầm vòng mái vòm SHS 200×100, 4 cột đỡ', '1'], ['K5', 'Tôn Klip-Lok 0.48, dốc 3,5 %, máng xối phố', '—'], ['K6', 'Dầm biên + móc treo M12 vào sàn L2 (khoan cấy hoá chất)', '28']]
    table(pg, 160, 38, ['Mã', 'Cấu kiện / Member (kỹ sư kết cấu duyệt)', 'SL'], rows, [8, 120, 10], fs=4.6, rh=3.4)
    pg.save(pdf)
