import json, re, math, collections
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
C = json.load(open('cad/cad_data.json')); Q = json.load(open('cad/quant_plan.json')); D = json.load(open('r12/samarkand-3d-data-R12.json'))
INV = C['inv']; TER = -0.45
def objs(pat): return [r for r in INV if re.search(pat, r[0])]
def n(pat): return len(objs(pat))
def dx(r): return r[3][0] - r[2][0]
def dy(r): return r[3][1] - r[2][1]
def dz(r): return r[3][2] - r[2][2]
A = Q['areas']; WFa = collections.defaultdict(float)
for c, nm, a in Q['wall']: WFa[c] += a
beams = objs(r'^roof_beam_y'); long_b = [b for b in beams if dx(b) > 8]; short_b = [b for b in beams if dx(b) <= 8]
purl = objs(r'^purlin(\.\d+)?$'); cols = objs(r'^column_steel|^column_portal'); dcols = objs(r'^Dome_column(\.\d+)?$')
t2 = [t for t in objs(r'^Table_') if max(dx(t), dy(t)) < 1.0]; t4 = [t for t in objs(r'^Table_') if max(dx(t), dy(t)) >= 1.0]
cc = objs(r'^Ceiling_coffers$')[0]; ceil_gross = dx(cc) * dy(cc); sky = D.get('skylight'); dome_open = 5.07 ** 2
sky_a = 9.0
fascia = objs(r'^Facade_fascia$')[0]; fl = math.hypot(dx(fascia), dy(fascia))
bal = objs(r'^Aivan_balustrade_'); bal_len = sum(max(dx(b), dy(b)) for b in bal)
SHEETS = collections.OrderedDict()
SHEETS['1 Sàn - Floors'] = [
 ('F1', 'Đá marble trắng 500×500×20 lát chéo 45°, viền gạch men cobalt 90, khảm kim cương; keo C2TE, vữa lót 40', 'White marble 500×500×20 on the diagonal, 90 mm cobalt glazed band with inlaid diamonds; C2TE on a 40 mm bed', 'm²', A['F1'][1], 'Diện tích tịnh: trừ aivan, bục cabin, hồ sao, bồn cây / net of aivan deck, booth podiums, star pool, tree ring'),
 ('F1a', 'Viền gạch men cobalt 90 trong sàn F1 (ước lượng theo mô-đun 590)', 'Cobalt band 90 mm inside F1 (per 590 mm module)', 'm', round(A['F1'][1] * 2 / 0.59, 0), '2 dải / mô-đun 0,59 m → ≈3,39 m / m²'),
 ('F2', 'Gạch zellige sao 8 cánh trên nền men trắng — hành lang vào', 'Zellige 8-point star tiles on white glazed field — entrance corridor', 'm²', A['F2'][1], ''),
 ('F3', 'Gạch nung 300×150 xếp chong chóng + gạch men 150×150 — sàn aivan +0.450', 'Terracotta 300×150 pinwheel + 150 glazed inserts — aivan deck +0.450', 'm²', A['F3'][1], 'Gồm chiếu nghỉ phía bắc / incl. north landing'),
 ('F3s', 'Kết cấu sàn nâng aivan: khung thép hộp 100×50 + tấm xi măng 20', 'Raised aivan deck: 100×50 steel frame + 20 cement board', 'm²', A['F3'][1], 'Cao 450 mm'),
 ('F3f', 'Mặt dựng sàn aivan ốp gỗ óc chó cao 450', 'Walnut-clad deck face h 450', 'm', round(13.2 + 0.9 + 2.4, 1), 'Cạnh dọc sảnh + chiếu nghỉ'),
 ('F4', 'Bục cabin +0.150: khung gỗ, ván, thảm; mặt dựng óc chó + nẹp đồng', 'Booth podium +0.150: timber frame, boards, carpet; walnut riser + brass strip', 'm²', A['F4'][1], '7 cabin'),
 ('F5', 'Cao su EPDM 500×500 — khu trẻ em', 'EPDM rubber tiles 500×500 — kids zone', 'm²', A['F5'][1], ''),
 ('F6', 'Đá slate chống trơn — khu mangal', 'Anti-slip slate — mangal', 'm²', A['F6'][1], ''),
 ('F7', 'Hồ sao 8 cánh 1.400: thành xây ốp men lam, đáy chống thấm', 'Star pool 1.40 m: glazed-tile wall, waterproofed basin', 'm²', A['F7'][1], 'Chu vi 4,4 m'),
 ('F8', 'Bậc cấp đá: cổng vào 4 bậc × 2.500 + bậc aivan (3 vị trí × 3 bậc)', 'Stone steps: entrance 4 × 2.50 m + aivan stairs (3 flights × 3 risers)', 'm', round(4 * 2.5 + 3 * 3 * 1.2, 1), 'Chiều dài mũi bậc / nosing length'),
 ('F9', 'Nẹp đồng 3×20 chuyển tiếp vật liệu', 'Brass transition strip 3×20', 'm', round(A['F2'][2] + A['F3'][2] * 0.4 + A['F5'][2] * 0.3 + A['F6'][2] * 0.5, 0), 'Ước lượng theo chu vi vùng / from zone perimeters')]
SHEETS['2 Tường - Walls'] = [
 ('W1', 'Cột phố Samarkand: lõi thép SHS150 bọc gạch cong + men, chân đá, đầu cột', 'Street column: SHS150 core, curved brick + glaze cladding, stone base, capital', 'cái/pcs', n(r'^Sam_column_\d+$'), 'Ø330 × h≈3,27 m; ốp ≈2,4 m²/cột'),
 ('W2', 'Cổng vào: gạch men 150×150 ba màu trên 2 trụ 700×1200', 'Entrance portal: 150×150 glazed tiles on two 700×1200 pylons', 'm²', 19.2, '4 mặt × 2 trụ (CT-12)'),
 ('W2a', 'Cổng vào: gạch thẻ ốp lanh-tô (2 mặt)', 'Portal lintel: brick slips (2 faces)', 'm²', round(2 * 3.9 * 0.84, 1), '3.900 × 840'),
 ('W2b', 'Cổng vào: đá chân đế cao 550 + mũ đá 80', 'Portal: stone plinth h 550 + coping 80', 'm²', round(2 * 3.96 * 0.55 + 3.98 * 1.28, 1), ''),
 ('W2c', 'Cổng vào: tấm vòm phẳng dày 60 + viền men ngọc', 'Portal: flat pointed-arch panel 60 thick + turquoise band', 'cái/pcs', 1, '2.500 × ≈1.200'),
 ('W3', 'Tường bar: gạch thẻ vàng 230×65 mạch 10 + gạch men đầu', 'Bar back wall: buff brick slips 230×65, 10 mm joints + glazed headers', 'm²', round(5.7 * 3.55, 1), '5.700 × 3.550'),
 ('W3a', 'Mặt trước quầy bar: cùng loại gạch', 'Bar counter front: same brick', 'm²', round(6.2 * 0.905 + 0.27 * 0.905, 1), '6.200 × 905 + hồi'),
 ('W4', 'Tường mangal: gạch hazarbaf + men lam (tường tây + hộp chụp hút)', 'Mangal walls: hazarbaf brick + glaze (west wall + hood breast)', 'm²', round(5.15 * 3.2 + 2 * (4.9 + 1.2) * 1.75, 1), 'Ước lượng / estimate'),
 ('W5', 'Tường ranh nam trát đất sét có hốc vòm', 'South boundary wall, clay plaster with arched niches', 'm²', round(12.4 * 2.7 + 10.2 * 1.45, 1), '≈12,4 m × 2,7 + phần trên'),
 ('W6', 'Vách cabin đúc sẵn 1.950×2.450: khung 45×70, lõi MDF 18, lưới sao óc chó 40 hai mặt', 'Prefab booth partition 1.950×2.450: 45×70 frame, 18 MDF core, walnut star lattice both faces', 'tấm/pcs', 8, '4,78 m² / tấm; lưới 9,56 m² / tấm'),
 ('W6a', 'Trần lưới cabin +2.400 (cùng mẫu lưới)', 'Booth lattice ceiling +2.40', 'm²', A['F4'][1], '7 cabin'),
 ('W6b', 'Rèm nhung cabin 2 tấm / cabin, thanh đồng Ø24', 'Booth velvet curtains, 2 per booth, brass rod', 'bộ/sets', 7, 'Cao 1.900'),
 ('W7', 'Vách lưới sao óc chó 30 trên nền MDF than — tường aivan', 'Walnut star lattice 30 on charcoal backing — aivan wall', 'm²', round(WFa['W7'], 1), '4 tấm (DV-01)'),
 ('W7a', 'Vách lưới sao — hành lang vào (2 bên × 3 ô)', 'Star lattice — entrance corridor (2 sides × 3 bays)', 'm²', round(2 * (0.69 + 0.69 + 0.64) * 2.5, 1), ''),
 ('W8', 'Thảm treo tường aivan 1.760 × 2.720 (thảm của chủ đầu tư) + thanh đồng', 'Aivan wall carpets 1.76 × 2.72 (owner supplied) + brass rod', 'tấm/pcs', 4, f"{WFa['W8']:.1f} m² tổng"),
 ('W9', 'Vòm gỗ óc chó hành lang 160×140 (4 vòm, thông thuỷ 2.000)', 'Corridor walnut pointed arches 160×140 (4 no., 2.00 m clear)', 'cái/pcs', 4, ''),
 ('W10', 'Vòm gỗ khu chụp ảnh 2.300 thông thuỷ + góc lưới', 'Photo-zone arch 2.30 m clear + lattice spandrels', 'cái/pcs', 1, 'Cao 2.790'),
 ('W11', 'Cột Khiva gỗ chạm 180×180 + đầu vòm chạm (aivan)', 'Carved Khiva columns 180×180 + arcade heads (aivan)', 'cái/pcs', n(r'^Khiva_column_\d+$'), f"{n(r'^Khiva_arcade_head')} đầu vòm"),
 ('W12', 'Lan can gỗ aivan cao 1.050 (đầu hồi + chiếu nghỉ)', 'Aivan timber balustrade h 1.05 (ends + landing)', 'm', round(bal_len, 1), f'{len(bal)} đoạn'),
 ('W13', 'Diềm mái phố: gỗ 40×300 + 2 hàng gạch men 100 + diềm chạm', 'Street eave: 40×300 walnut fascia + 2 rows of 100 tiles + carved fringe', 'm', round(fl, 1), ''),
 ('W14', 'Hộp gỗ bọc đầu dầm + nắp đồng', 'Walnut beam-end casing + brass cap', 'cái/pcs', len(long_b) + 3, ''),
 ('W15', 'Ghế xây trát vôi ngoài phố + đệm', 'Street plaster benches + pads', 'm', round(sum(max(dx(b), dy(b)) for b in objs(r'^Street_bench_plaster_\d$')), 1), f"{n(r'^Street_bench_plaster_')} đoạn"),
 ('W16', 'Bệ / bồn cây dọc phố trát vôi trắng (mặt đứng cao 720 + mặt trên)', 'Street plinth / planter, white lime render (720 high face + top)', 'm²', round(33.2 * 0.72 + 25 * 0.8, 1), 'Ước lượng: 33,2 m × 0,72 + mặt trên ≈ 20 m² / estimate'),
 ('W17', 'Bảng tên gỗ + chữ đồng «Samarkand» (vách phố 1, cổng 1)', 'Name boards with brass letters (street screen 1, portal 1)', 'bộ/sets', 2, '')]
SHEETS['3 Trần - Ceilings'] = [
 ('C1-4', 'Trần ô hộp gỗ óc chó (lưới 70×140, mô-đun ≈1,2 m), thảm / nan gỗ, LED hắt', 'Walnut coffered ceiling (70×140 grid, ≈1.2 m module), carpet / slat infill, LED', 'm²', round(ceil_gross - dome_open - sky_a, 1), f'Gộp {ceil_gross:.1f} − mái vòm 25,7 − giếng trời 9,0'),
 ('C5', 'Trần ô hộp aivan +3.240', 'Aivan coffered ceiling +3.24', 'm²', round(2.89 * 13.19, 1), '2.890 × 13.190'),
 ('C6', 'Mái vòm Ø≈5,07 (vỏ GRC ốp men, mặt trong vẽ karbandi)', 'Dome Ø≈5.07 (GRC shell, glazed outside, painted karbandi inside)', 'cái/pcs', 1, 'Diện tích mặt trong ≈ 46 m²'),
 ('C7', 'LED dây 2700K 9,6 W/m trong ô trần', 'LED strip 2700K 9.6 W/m in the coffers', 'm', round((ceil_gross - dome_open - sky_a) / 1.44 * 4 * 1.0, 0), '≈ 4 × 1,0 m / ô 1,2×1,2'),
 ('C8', 'Dải nhung trang trí dưới trần (khu mangal)', 'Velvet swags under the ceiling (mangal side)', 'dải/pcs', n(r'^Velvet_swag_'), '0,7 × 4,65 m')]
SHEETS['4 Kết cấu mái - Roof'] = [
 ('K1', 'Cột thép SHS 150×150×6, đế 300×300×16, 4 bu lông M16', 'Steel column SHS 150×150×6, base plate 300×300×16, 4 M16', 'cái/pcs', len(cols), f'Cao ≈ {sum(dz(c) for c in cols) / max(1, len(cols)):.2f} m; tổng {sum(dz(c) for c in cols):.1f} m ≈ {sum(dz(c) for c in cols) * 26.4:.0f} kg'),
 ('K1a', 'Cột đỡ mái vòm SHS 150 bọc gỗ', 'Dome columns SHS 150 with timber casing', 'cái/pcs', len(dcols), f'tổng {sum(dz(c) for c in dcols):.1f} m'),
 ('K2', 'Dầm chính HEB 300 (sơ bộ) nhịp 10–12,6 m', 'Main beams HEB 300 (preliminary), spans 10–12.6 m', 'm', round(sum(dx(b) for b in long_b), 1), f'{len(long_b)} dầm ≈ {sum(dx(b) for b in long_b) * 117:.0f} kg — kỹ sư kết cấu duyệt'),
 ('K2a', 'Dầm ngắn I 300×150', 'Short beams I 300×150', 'm', round(sum(dx(b) for b in short_b), 1), f'{len(short_b)} dầm ≈ {sum(dx(b) for b in short_b) * 42.2:.0f} kg'),
 ('K3', 'Xà gồ C200×80×2,5 @1000', 'Purlins C200×80×2.5 @1000', 'm', round(sum(dy(p) for p in purl), 1), f'{len(purl)} thanh'),
 ('K4', 'Dầm vòng mái vòm thép hộp 200×100', 'Dome ring girder SHS 200×100', 'm', round(4 * 5.07, 1), ''),
 ('K5', 'Tôn Klip-Lok 0,48 dốc 3,5 % + máng xối phố', 'Klip-Lok 0.48 roofing, 3.5 % fall + street gutter', 'm²', round(sum(Polygon_area for Polygon_area in [379.4]), 1), 'Diện tích mặt bằng mái'),
 ('K6', 'Móc treo / bản mã vào dầm biên toà nhà (khoan cấy hoá chất M12)', 'Ledger hangers to the building edge beam (M12 chemical anchors)', 'cái/pcs', n(r'^Ledger_hanger'), ''),
 ('K7', 'Máng xối + ống thoát nước mái', 'Gutter + downpipes', 'm', round(fl, 1), 'Dọc mép phố')]
SHEETS['5 Nội thất - Furniture'] = [
 ('N1', 'Ghế gỗ chạm (đệm thảm có viền)', 'Carved armchair with piped rug cushion', 'cái/pcs', n(r'^Chair_'), '671×638×1.111'),
 ('N2', 'Bàn chân chữ T 2 chỗ 700×800', 'Trestle table, 2-top 700×800', 'cái/pcs', len(t2), ''),
 ('N3', 'Bàn chân chữ T 4 chỗ 1.400×800', 'Trestle table, 4-top 1.400×800', 'cái/pcs', len(t4), ''),
 ('N4', 'Sofa cabin 2 chỗ 1.400', 'Booth settee, 2-seat 1.400', 'cái/pcs', n(r'^Booth\d_settee_'), ''),
 ('N5', 'Bàn cabin 1.200×850', 'Booth table 1.200×850', 'cái/pcs', n(r'^Booth\d_table$'), ''),
 ('N6', 'Sofa aivan 3 chỗ 1.660 (+1 khu chụp ảnh)', 'Aivan settee, 3-seat 1.660 (+1 photo zone)', 'cái/pcs', n(r'^Aivan_settee_') + n(r'^Photo_settee$'), ''),
 ('N7', 'Bàn aivan 1.200×560', 'Aivan table 1.200×560', 'cái/pcs', n(r'^Aivan_table_\d$'), ''),
 ('N8', 'Ghế bar gỗ', 'Timber bar stool', 'cái/pcs', n(r'^Barstool'), ''),
 ('N9', 'Lều majlis 2.720×2.800 (khung gỗ + bạt + rèm), đệm ngồi, bàn thấp', 'Majlis tent 2.72×2.80 (timber frame, canvas, curtains), cushions, low tables', 'bộ/sets', n(r'^Tent_\d$'), '8 chỗ / lều'),
 ('N10', 'Tapchan 2.000×2.200 + đệm + bàn thấp', 'Tapchan 2.00×2.20 with mattress and low table', 'bộ/sets', n(r'^Tapchan_v82$'), ''),
 ('N11', 'Đệm ngồi sàn 800×800 / đôn (majlis)', 'Floor cushions 800×800 / poufs (majlis)', 'cái/pcs', n(r'^Majlis_cushion_') + n(r'^Majlis_pouf_'), ''),
 ('N12', 'Tủ phục vụ chạm sát tường 1.330×520×2.150', 'Carved service cabinet 1.330×520×2.150', 'cái/pcs', n(r'^Station_cabinet_\d$'), ''),
 ('N13', 'Quầy trạm phục vụ 2.800×600×940 (óc chó + đá trắng)', 'Waiter pass counter 2.80×0.60×0.94 (walnut + white stone)', 'cái/pcs', 1, ''),
 ('N14', 'Quầy bar trước 6.200×800 (2 cao độ) + quầy sau 4.800×550 + tủ mát đứng', 'Front bar counter 6.20×0.80 (2 levels) + back bar 4.80×0.55 + tall cooler', 'bộ/sets', 1, 'DV-02, DV-03, CT-06'),
 ('N15', 'Kệ gỗ óc chó bar dày 40 sâu 285, ke đồng', 'Bar walnut shelves 40 thick, 285 deep, brass brackets', 'm', round(3 * (1.52 * 3), 1), '3 tầng × 3 đoạn'),
 ('N16', 'Thiết bị bar: máy espresso 2 group, 2 máy xay, 2 máy xay sinh tố, máy ép, máy đá, 6 tủ mát dưới quầy, máy rửa ly', 'Bar equipment: 2-group espresso, 2 grinders, 2 blenders, citrus press, ice maker, 6 under-counter fridges, glass washer', 'bộ/sets', 1, 'Chủ đầu tư cấp / owner supplied?'),
 ('N17', 'Bình gốm trang trí (hành lang, bậc aivan)', 'Decorative terracotta jugs (corridor, aivan steps)', 'cái/pcs', n(r'jug|Jug'), ''),
 ('N18', 'Cây trồng: ficus 8, cây cắt tỉa 7, cọ 3, ô liu 2, lưỡi hổ 2, chinar 1, chậu hoa 2', 'Plants: ficus 8, topiary 7, palms 3, olive 2, sansevieria 2, chinar 1, flower pots 2', 'cây/pcs', 25, 'Theo mô hình / per the model'),
 ('N19', 'Đồ chơi & nội thất khu trẻ em', 'Kids zone furniture & play items', 'bộ/sets', 1, f"{n(r'^Kids_')} hạng mục")]
ch = [r for r in INV if ('chandelier' in r[0].lower() and 'rod' not in r[0]) or 'lantern_hang' in r[0]]
SHEETS['6 Điện - Lighting & power'] = [
 ('L1', 'Đèn chùm thác mái vòm (61 cầu đồng đục lỗ)', 'Dome cascade chandelier (61 pierced brass globes)', 'bộ/sets', 1, 'Treo đỉnh vòm, ≈180 kg'),
 ('L2', 'Đèn chùm nhỏ kiểu mái vòm (7 cầu)', 'Small cascade chandelier (7 globes)', 'bộ/sets', len(ch), 'Aivan 7 · hành lang 3 · sảnh 9 · cabin 7 · lều 4 · majlis · khác'),
 ('L3', 'Đèn trống kết hạt (bar)', 'Beaded drum pendant (bar)', 'bộ/sets', n(r'^Bar_drum_pendant_'), ''),
 ('L4', 'Đèn trống đồng đục lỗ Ø900 (khu bắc)', 'Pierced brass drum Ø900 (north zone)', 'bộ/sets', n(r'^North_chandelier$'), ''),
 ('L5', 'Đèn bra đồng lồng đục lỗ', 'Brass lantern wall sconce', 'bộ/sets', n(r'^Sconce_'), 'Cột vòm 4 · cột phố 6 · mangal 1'),
 ('L6', 'Đèn âm sàn hắt lên Ø100 IP67', 'Recessed floor uplight Ø100 IP67', 'bộ/sets', n(r'[Uu]plight'), ''),
 ('L7', 'Đèn sưởi / đèn quầy mangal', 'Mangal heat / counter lamps', 'bộ/sets', n(r'^Heat_lamp_'), ''),
 ('L8', 'LED hắt chân vách lưới (hành lang 6, aivan 4)', 'LED uplight strip at lattice panels (corridor 6, aivan 4)', 'm', round(6 * 0.6 + 0.9 + 1.3 + 1.8 + 0.4, 1), 'IP65'),
 ('L9', 'LED dưới kệ bar + trong tủ mát', 'LED under the bar shelves + in coolers', 'm', round(3 * 4.56 + 6, 1), ''),
 ('P1', 'Hộp ổ cắm sàn bật nắp 180×180 (2 ổ + 2 USB) IP44', 'Pop-up floor box 180×180 (2 sockets + 2 USB) IP44', 'cái/pcs', n(r'^Floor_socket_'), 'Đầu mỗi bàn'),
 ('P2', 'Ổ cắm tường đôi (cabin 14, tường aivan 4)', 'Double wall socket (booths 14, aivan wall 4)', 'cái/pcs', 18, ''),
 ('P3', 'Ổ cắm thiết bị bar IP44 + cấp nguồn mangal', 'Bar equipment sockets IP44 + mangal supply', 'cái/pcs', 16, 'Theo M&E'),
 ('P4', 'Tủ điện phụ + điều khiển 4 kịch bản (DALI / 0–10 V)', 'Sub-board + 4-scene control (DALI / 0–10 V)', 'bộ/sets', 1, 'Theo M&E')]
wb = Workbook(); wb.remove(wb.active)
thin = Side(style='thin', color='999999'); B = Border(left=thin, right=thin, top=thin, bottom=thin)
HF = PatternFill('solid', fgColor='2F5D23'); IN = PatternFill('solid', fgColor='FFFF00')
def head(ws, title):
    ws['A1'] = 'SAMARKAND — BẢNG KHỐI LƯỢNG / BILL OF QUANTITIES — ' + title; ws['A1'].font = Font(name='Arial', size=13, bold=True)
    ws['A2'] = 'Nguồn: mô hình 3D R12-v12.1 + bản vẽ AutoCAD Samarkand_R12-v12.1.dxf · Khối lượng tịnh, chưa gồm hao hụt · Source: 3D model R12-v12.1; net quantities, no waste allowance'; ws['A2'].font = Font(name='Arial', size=9, italic=True)
    for i, h in enumerate(['STT\nNo.', 'Mã\nCode', 'Hạng mục (Tiếng Việt)', 'Item (English)', 'ĐVT\nUnit', 'Khối lượng\nQty', 'Hao hụt %\nWaste %', 'KL đặt hàng\nOrder qty', 'Đơn giá (VND)\nUnit price', 'Thành tiền (VND)\nAmount', 'Cơ sở tính / Basis'], 1):
        c = ws.cell(row=4, column=i, value=h); c.font = Font(name='Arial', size=9, bold=True, color='FFFFFF'); c.fill = HF; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); c.border = B
    ws.row_dimensions[4].height = 34
    for col, w in zip('ABCDEFGHIJK', (5, 7, 58, 58, 9, 11, 9, 11, 14, 16, 50)): ws.column_dimensions[col].width = w
    ws.freeze_panes = 'A5'
tot_refs = []
for name, rows in SHEETS.items():
    ws = wb.create_sheet(name[:31]); head(ws, name)
    for k, (code, vi, en, unit, qty, basis) in enumerate(rows):
        r = 5 + k
        vals = [k + 1, code, vi, en, unit, qty, 5 if unit in ('m²', 'm') else 0, f'=ROUND(F{r}*(1+G{r}/100),1)', None, f'=H{r}*I{r}', basis]
        for i, v in enumerate(vals, 1):
            c = ws.cell(row=r, column=i, value=v); c.font = Font(name='Arial', size=9, color='0000FF' if i in (6, 7) else '000000'); c.border = B
            c.alignment = Alignment(vertical='top', wrap_text=i in (3, 4, 11), horizontal='center' if i in (1, 2, 5) else None)
            if i == 9: c.fill = IN
            if i in (6, 8): c.number_format = '#,##0.0'
            if i in (9, 10): c.number_format = '#,##0;(#,##0);-'
    r = 5 + len(rows)
    ws.cell(row=r, column=3, value='CỘNG / SUBTOTAL').font = Font(name='Arial', size=9, bold=True)
    c = ws.cell(row=r, column=10, value=f'=SUM(J5:J{r - 1})'); c.font = Font(name='Arial', size=9, bold=True); c.number_format = '#,##0;(#,##0);-'; c.border = B
    tot_refs.append((name, f"='{name[:31]}'!J{r}"))
ws = wb.create_sheet('0 Tổng hợp - Summary', 0)
ws['A1'] = 'SAMARKAND — TỔNG HỢP KHỐI LƯỢNG & GIÁ / SUMMARY'; ws['A1'].font = Font(name='Arial', size=14, bold=True)
ws['A2'] = 'Nhà hàng Samarkand · Đà Nẵng · Mô hình R12-v12.1 · 11/2026'; ws['A2'].font = Font(name='Arial', size=10)
notes = ['Ô VÀNG = đơn giá do nhà thầu điền; cột Thành tiền và Tổng tự tính. / YELLOW cells = unit prices to be filled by the contractor; amounts and totals calculate.',
         'Chữ XANH = số liệu nhập (khối lượng tịnh từ mô hình, % hao hụt có thể sửa). / BLUE = inputs (net quantities from the model; waste % editable).',
         'Diện tích sàn đo trên đa tuyến kín trong file DXF (lớp A-FLOR-F1…F7). / Floor areas are measured on the closed polylines in the DXF (layers A-FLOR-F1…F7).',
         'Kết cấu thép là SƠ BỘ — kỹ sư kết cấu tính và duyệt. / Steel sizes are PRELIMINARY — to be designed by the structural engineer.',
         'Chưa gồm: M&E chi tiết (cấp thoát nước, điều hoà, PCCC), thiết bị bếp mangal. / Not included: detailed MEP, mangal kitchen equipment.']
for i, t in enumerate(notes): ws.cell(row=4 + i, column=1, value=t).font = Font(name='Arial', size=9)
for i, h in enumerate(['Phần / Section', 'Thành tiền (VND) / Amount'], 1):
    c = ws.cell(row=11, column=i, value=h); c.font = Font(name='Arial', size=10, bold=True, color='FFFFFF'); c.fill = HF; c.border = B
for k, (nm, ref) in enumerate(tot_refs):
    ws.cell(row=12 + k, column=1, value=nm).font = Font(name='Arial', size=10); c = ws.cell(row=12 + k, column=2, value=ref); c.font = Font(name='Arial', size=10, color='008000'); c.number_format = '#,##0;(#,##0);-'; c.border = B
r = 12 + len(tot_refs)
ws.cell(row=r, column=1, value='TỔNG CỘNG / GRAND TOTAL').font = Font(name='Arial', size=11, bold=True); c = ws.cell(row=r, column=2, value=f'=SUM(B12:B{r - 1})'); c.font = Font(name='Arial', size=11, bold=True); c.number_format = '#,##0;(#,##0);-'; c.border = B
ws.cell(row=r + 2, column=1, value='BẢNG DIỆN TÍCH SÀN / FLOOR AREAS (m²)').font = Font(name='Arial', size=10, bold=True)
for k, (code, (desc, a, per)) in enumerate(A.items()):
    ws.cell(row=r + 3 + k, column=1, value=f'{code} — {desc}').font = Font(name='Arial', size=9); c = ws.cell(row=r + 3 + k, column=2, value=a); c.font = Font(name='Arial', size=9, color='0000FF'); c.number_format = '#,##0.0'
e = r + 3 + len(A); ws.cell(row=e, column=1, value='Tổng diện tích sàn / Total floor area').font = Font(name='Arial', size=9, bold=True); c = ws.cell(row=e, column=2, value=f'=SUM(B{r + 3}:B{e - 1})'); c.number_format = '#,##0.0'; c.font = Font(name='Arial', size=9, bold=True)
ws.column_dimensions['A'].width = 110; ws.column_dimensions['B'].width = 26
wb.save('cad/Samarkand_BOQ_R12-v12.1.xlsx'); print('rows', {k: len(v) for k, v in SHEETS.items()})
