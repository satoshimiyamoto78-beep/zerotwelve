"""Samarkand terrace R7 — preliminary cost estimate (VND/USD) as .xlsx with live formulas.
Quantities come from layout_r8.py / roof_r7.py geometry. Args: zone.json base.dxf outdir
"""
import sys, json, runpy
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

argv = sys.argv[:]
sys.argv = ['layout_r8.py'] + argv[1:4]
G = runpy.run_path(__file__.replace('estimate_r8.py', 'layout_r8.py'))
sys.argv = argv
OUT = argv[3]
RQ = json.load(open(f"{OUT}/samarkand-roof-{G['REV']}.json"))
items, zm = G['items'], G['zone_m2']
def cnt(k): return sum(1 for it in items if it['kind'] == k)
def length(k): return sum(it['geom'].length for it in items if it['kind'] == k) / 2 / 1000
area_floor = round((G['FLOOR'].area - G['PLAT'].area - G['ALLEY'].area - G['KIDS'].area) / 1e6 - zm['bbq'] - zm['court_s'] * 0, 1)
n_chairs, n_mod = cnt('chair'), G['n_mod']
bq_len = round(sum(b - a for a, b in G['BQ']) / 1000, 1)
sbench = round(length('sbench'), 1)
steel_t = round((RQ['beams_m'] * 42 + RQ['purlins_m'] * 7.5 + 11 * 3.6 * 28 + RQ['ledger_m'] * 22 + 30 * 20) / 1000, 1)
RATE = 26000
M = 1_000_000

# (section, item, unit, qty, unit price VND, note, economy option, economy unit price or None)
S = []
def L(sec, it, u, q, p, note='', eco='', pe=None): S.append((sec, it, u, q, p, note, eco, pe))
s = '1. Демонтаж и подготовка'
L(s, 'Демонтаж волны-ламелей под балконом', 'компл', 1, 25 * M, 'с вывозом')
L(s, 'Демонтаж старой перголы, круглых элементов, козырька E–G', 'компл', 1, 30 * M, '')
L(s, 'Снятие старого покрытия, стяжка-выравнивание террасы', 'м²', round(G['FLOOR'].area / 1e6, 1), 180_000, 'кроме клумб')
s = '2. Навес (кровля)'
L(s, 'Металлоконструкции: балки, прогоны, колонны, опорный швеллер, обвязка двориков', 'т', steel_t, 38_000 * 1000, '≈38 000 ₫/кг с изготовлением, оцинковкой, покраской и монтажом', 'Без горячей оцинковки, грунт + 2 слоя краски', 32_000 * 1000)
L(s, 'Сэндвич-панель PU 50 мм, низ «под дерево», с крепежом', 'м²', round(RQ['roof_m2'] * 1.05, 1), 420_000, 'нижний слой = готовый потолок', 'Панель PU 50 мм без «дерева» (белый низ)', 340_000)
L(s, 'Коробчатый желоб вдоль улицы и вокруг двориков', 'м', round(RQ['gutter_street_m'] + RQ['gutter_courts_m'], 1), 450_000, 'оцинк. сталь 0,6 мм')
L(s, 'Водостоки в колоннах + выпуск в дренаж', 'шт', 13, 1_800_000, '')
L(s, 'Примыкание к фасаду (фартук, герметик)', 'м', RQ['ledger_m'], 280_000, '')
L(s, 'Обшивка колонн деревом (акация, масло)', 'шт', 11, 2_800_000, '', 'Фиброцемент под дерево', 1_600_000)
L(s, 'Реечный потолок над баром и коридором (акцент)', 'м²', 40, 950_000, 'сосна/акация, огнезащита', 'Алюминиевые рейки под дерево', 750_000)
s = '3. Полы и платформа'
L(s, 'Керамогранит 600×600 «терракота» с вставками-кабошонами, укладка', 'м²', area_floor, 620_000, 'антискольжение R11', 'Керамогранит без вставок', 480_000)
L(s, 'Аллея: цементная плитка-гирих 200×200, укладка', 'м²', zm['alley'], 1_450_000, 'энкаустик ручной работы, производство во Вьетнаме')
L(s, 'Мангальная: противоскользящий пол + трап', 'м²', zm['bbq'], 750_000, '')
L(s, 'Айван ±0.000: стальной каркас + ДПК-доска', 'м²', zm['platform'], 2_100_000, 'на месте засыпанных ступеней', 'Бетонная плита + керамогранит', 1_500_000)
L(s, 'Перила айвана с решёткой-джали (ЧПУ, металл)', 'м', 22, 3_200_000, '', 'Простые деревянные перила', 1_800_000)
L(s, 'Пандус 1:12 + ступени (облицовка)', 'компл', 1, 45 * M, '')
s = '4. Уличный фасад'
L(s, 'Скамьи из литого бетона, спинка, майоликовый пояс', 'м', sbench, 3_600_000, '', 'Печатная плитка вместо майолики', 3_000_000)
L(s, 'Портал-пештак у входа (2 пилона) + ступени с тротуара', 'компл', 1, 65 * M, '')
L(s, 'Фонтан-себиль (майоликовая стена, латунный носик, чаша, насос)', 'компл', 1, 42 * M, '')
L(s, 'Уличная фото-арка с нишей и подсветкой', 'компл', 1, 32 * M, '')
L(s, 'Клумбы: грунт, дренаж, капельный полив, растения', 'м²', round(G['planter'].area / 1e6, 1), 650_000, '')
L(s, 'Гранат (анор) — деревья у входа + кадка у бара', 'шт', 3, 4_500_000, 'крупномер 1,8–2,2 м')
L(s, 'Плюмерия (франжипани) в уличной клумбе', 'шт', 5, 5_000_000, 'ствол 8–10 см')
L(s, 'Бугенвиллия по спинкам скамей и колоннам', 'шт', 24, 450_000, 'с опорами-шпалерами')
L(s, 'Пальмы: арека в фото-лаунже + у уличной арки', 'шт', 6, 3_200_000, 'в терракотовых кадках')
L(s, 'Банан, стрелиция Николая — зелёная стена за топчанами', 'шт', 6, 1_300_000, '')
L(s, 'Жасмин самбак, грядка трав у мангала (райхон, мята, базилик)', 'компл', 1, 6 * M, '')
s = '5. Зоны и встроенная мебель'
L(s, 'Бар: стойка 5,7 м (рифлёная плитка, терраццо-столешница), бэк-бар с нишами', 'компл', 1, 185 * M, '', 'Столешница из кварц-агломерата, бэк-бар без ниш', 145 * M)
L(s, 'Кабинки: 2 скамьи, стол, резная ширма, фонарь', 'шт', 9, 16 * M, '', 'Ширма — фанера ЧПУ под покраску', 12.5 * M)
L(s, 'Банкетка айвана (каркас, поролон, икат-ткань для улицы)', 'м', bq_len, 4_200_000, '')
L(s, 'Топчаны 2,0 × 2,2 м (резное дерево, курпачи, низкий стол)', 'шт', 2, 24 * M, '')
L(s, 'Шатёр-маджлис (каркас, ткань с огнезащитой, П-диван, ковёр, 2 стола, фонари)', 'компл', 1, 78 * M, '', 'Готовый арабский шатёр + стандартный диван', 58 * M)
L(s, 'Фото-лаунж «Очаг» (портал с драпировкой, ковры, LED-огонь, хумы, 3 столика, 12 пуфов)', 'компл', 1, 61 * M, '')
L(s, 'Коридор-драпировка (бархат с огнезащитой, каркас, дорожка, хумы, фонари)', 'компл', 1, 46 * M, '')
L(s, 'Фонтан-хауз Ø1,2 м: борт-скамья из майолики, мозаика-звезда Ø2,6 м в полу, насос, лотосы, 8 светильников', 'компл', 1, 58 * M, '', 'Без мозаики в полу, борт из бетона с плиткой', 42 * M)
L(s, 'Скамьи вокруг чинаров (юг — кольцо, север — полукольцо)', 'компл', 1, 52 * M, 'тик/акация на бетонном основании')
L(s, 'Станция персонала (стеллажи, стойка, мойка) + стойка хостес', 'компл', 1, 38 * M, '')
L(s, 'Детская зона: резиновое покрытие, ограждение, игровые элементы', 'компл', 1, 75 * M, '')
s = '6. Отдельная мебель'
L(s, 'Столы-модули 700 × 800 (массив акации, стальная база, стяжки)', 'шт', n_mod, 2_900_000, 'для улицы, масло-воск', 'Столешница HPL под дерево', 2_100_000)
L(s, 'Стулья для улицы (ротанг / дерево)', 'шт', n_chairs, 1_650_000, '', 'Синтетический ротанг (массовая серия)', 1_150_000)
L(s, 'Барные стулья', 'шт', 9, 2_600_000, '')
s = '7. Мангальная (см. лист «Мангальная»)'
s = '8. Свет, электрика, вентиляция'
L(s, 'Электрика, щит, розетки, кабель в лотках по балкам', 'м²', RQ['roof_m2'], 280_000, '')
L(s, 'Светильники: фонари, подвесы, ленты в нишах, подсветка деревьев', 'компл', 1, 165 * M, 'тёплые 2200–2700 K, IP65 у края', 'Меньше подвесов, больше лент', 120 * M)
L(s, 'Потолочные вентиляторы для улицы', 'шт', 12, 4_800_000, 'влажность/жара Дананга')
L(s, 'Звук (фоновая музыка, 8 колонок)', 'компл', 1, 38 * M, '')
L(s, 'Водопровод и канализация (бар, мангал, фонтаны, мойки)', 'компл', 1, 55 * M, '')

BBQ = [('Тандыр глиняный Ø900 в кирпичном коробе', 'шт', 1, 28 * M, 'местный мастер или Узбекистан'),
       ('Мангал из нерж. стали 2,0 м, решётка, шампурница', 'шт', 1, 19 * M, ''),
       ('Казан Ø800 чугун + газовая горелка высокого давления', 'компл', 1, 14 * M, ''),
       ('Вытяжной зонт из нерж. стали 4,5 м + вентилятор + труба выше кровли', 'компл', 1, 88 * M, 'обязательно (ветер с ЮВ)'),
       ('Холодильный стол 2-дверный 1,8 м', 'шт', 1, 29 * M, ''),
       ('Мойка 2-секционная + раковина для рук', 'компл', 1, 13 * M, ''),
       ('Раздача 2,8 м с подогревом и ИК-лампами', 'компл', 1, 32 * M, ''),
       ('Заготовочный стол из нержавейки + стеллажи', 'компл', 1, 14 * M, ''),
       ('Огнестойкая кирпичная стена, облицовка, отделка', 'компл', 1, 38 * M, ''),
       ('Газ: разводка, отсекатель, датчик утечки', 'компл', 1, 16 * M, ''),
       ('Трап, жироуловитель', 'компл', 1, 12 * M, ''),
       ('Склад угля и тары (стеллажи, металлические баки для золы)', 'компл', 1, 9 * M, ''),
       ('Огнетушители, кошма, аптечка', 'компл', 1, 4.5 * M, ''),
       ('Инвентарь: шампуры 200 шт, противни, решётки', 'компл', 1, 15 * M, '')]

wb = Workbook(); ws = wb.active; ws.title = 'Смета'
thin = Side(style='thin', color='C9B99A'); B = Border(bottom=thin)
HF = PatternFill('solid', fgColor='1F3F8A'); SF = PatternFill('solid', fgColor='EFE1C6'); TF = PatternFill('solid', fgColor='8E1F24')
ws['A1'] = 'SAMARKAND · крытая терраса R8 — предварительная смета'; ws['A1'].font = Font(size=14, bold=True, color='3B2A1E')
ws['A2'] = 'Ориентировочные цены по Дананг, 2026 (±20 %). Перед заказом взять 3 коммерческих предложения на каждый раздел. Курс:'; ws['A2'].font = Font(italic=True, color='6B5A48')
ws['H2'] = RATE; ws['I2'] = '₫ за 1 USD'; ws['H2'].font = Font(bold=True, color='8E1F24')
hdr = ['№', 'Раздел / позиция', 'Ед.', 'Кол-во', 'Цена, ₫', 'Сумма, ₫', 'Сумма, USD', 'Примечание', 'Эконом-вариант', 'Цена эконом, ₫', 'Сумма эконом, ₫', 'Эконом, USD']
for j, h in enumerate(hdr, 1):
    c = ws.cell(4, j, h); c.font = Font(bold=True, color='FFFFFF'); c.fill = HF; c.alignment = Alignment(wrap_text=True, vertical='center')
r = 5; sec_rows = []; cur = None; first = None; n = 0
def close_sec():
    global r
    if cur is None: return
    c = ws.cell(r, 2, f'Итого: {cur}'); c.font = Font(bold=True)
    ws.cell(r, 6, f'=SUM(F{first}:F{r - 1})'); ws.cell(r, 7, f'=F{r}/$H$2'); ws.cell(r, 11, f'=SUM(K{first}:K{r - 1})')
    for j in (6, 7, 11): ws.cell(r, j).font = Font(bold=True)
    for j in range(1, 12): ws.cell(r, j).fill = SF
    sec_rows.append((cur, r)); r += 2
rows = S[:]
for sec, it, u, q, p, note, eco, pe in rows + [('7. Мангальная (см. лист «Мангальная»)', None, None, None, None, None, None, None)]:
    if sec != cur:
        close_sec(); cur = sec
        ws.cell(r, 2, sec).font = Font(bold=True, color='8E1F24', size=12); r += 1; first = r
    if it is None:
        ws.cell(r, 2, 'Оборудование и отделка мангальной'); ws.cell(r, 3, 'компл'); ws.cell(r, 4, 1)
        ws.cell(r, 5, "='Мангальная'!E{}".format(len(BBQ) + 4)); ws.cell(r, 6, f'=D{r}*E{r}'); ws.cell(r, 7, f'=F{r}/$H$2'); ws.cell(r, 11, f'=F{r}')
        r += 1; continue
    n += 1
    ws.cell(r, 1, n); ws.cell(r, 2, it); ws.cell(r, 3, u); ws.cell(r, 4, q); ws.cell(r, 5, p)
    ws.cell(r, 6, f'=D{r}*E{r}'); ws.cell(r, 7, f'=F{r}/$H$2'); ws.cell(r, 8, note); ws.cell(r, 9, eco)
    if pe is not None: ws.cell(r, 10, pe); ws.cell(r, 11, f'=D{r}*J{r}')
    else: ws.cell(r, 11, f'=F{r}')
    for j in range(1, 12): ws.cell(r, j).border = B
    r += 1
close_sec()
tot = r
ws.cell(r, 2, 'ИТОГО строительство и оснащение').font = Font(bold=True, size=12)
ws.cell(r, 6, '=' + '+'.join(f'F{x}' for _, x in sec_rows)); ws.cell(r, 7, f'=F{r}/$H$2'); ws.cell(r, 11, '=' + '+'.join(f'K{x}' for _, x in sec_rows)); r += 1
ws.cell(r, 2, 'Непредвиденные расходы 10 %'); ws.cell(r, 6, f'=F{tot}*0.1'); ws.cell(r, 7, f'=F{r}/$H$2'); ws.cell(r, 11, f'=K{tot}*0.1'); r += 1
ws.cell(r, 2, 'Проект конструкций навеса + согласования'); ws.cell(r, 6, 45 * M); ws.cell(r, 7, f'=F{r}/$H$2'); ws.cell(r, 11, f'=F{r}'); r += 1
ws.cell(r, 2, 'ВСЕГО'); ws.cell(r, 6, f'=SUM(F{tot}:F{r - 1})'); ws.cell(r, 7, f'=F{r}/$H$2'); ws.cell(r, 11, f'=SUM(K{tot}:K{r - 1})'); ws.cell(r, 12, f'=K{r}/$H$2')
for j in range(1, 13): ws.cell(r, j).fill = TF; ws.cell(r, j).font = Font(bold=True, color='FFFFFF', size=12)
grand = r; r += 2
ws.cell(r, 2, 'Экономия при всех эконом-вариантах, ₫'); ws.cell(r, 6, f'=F{grand}-K{grand}'); ws.cell(r, 6).font = Font(bold=True, color='1D6F77'); r += 1
ws.cell(r, 2, 'Стоимость 1 м² террасы (446,5 м²), ₫'); ws.cell(r, 6, f'=F{grand}/446.5'); r += 1
ws.cell(r, 2, f'Стоимость 1 посадочного места ({G["total"]} мест), ₫'); ws.cell(r, 6, f'=F{grand}/{G["total"]}'); r += 2
notes = ['Количества посчитаны из геометрии плана R8 (DXF) и кровли; металл — по весу балок, прогонов, колонн.',
         'Не входят: кухонное оборудование основной кухни, посуда, униформа, вывески, IT/касса, лицензии.',
         'Самые большие статьи: навес, мебель, мангальная, бар. Экономить в первую очередь: оцинковка, «дерево» на панели, рейки, ротанг, HPL-столешницы.',
         'Не экономить: вытяжка мангальной, анкеровка навеса на тайфун, гидроизоляция примыканий, антискользящий пол.']
for s_ in notes: ws.cell(r, 2, '· ' + s_).font = Font(italic=True, color='6B5A48'); r += 1
for j, w in enumerate([5, 62, 7, 9, 14, 16, 12, 34, 38, 14, 16, 12], 1): ws.column_dimensions[get_column_letter(j)].width = w
for row in ws.iter_rows(min_row=5, max_row=grand + 4):
    for c in row:
        if c.column in (5, 6, 10, 11): c.number_format = '#,##0'
        if c.column in (7, 12): c.number_format = '#,##0'
        if c.column == 4: c.number_format = '#,##0.0'
        if c.column in (2, 8, 9): c.alignment = Alignment(wrap_text=True, vertical='top')
ws.freeze_panes = 'C5'
# mangal sheet
wm = wb.create_sheet('Мангальная')
wm['A1'] = 'Мангальная 4,2 × 4,8 м — оборудование и отделка'; wm['A1'].font = Font(size=13, bold=True)
for j, h in enumerate(['Позиция', 'Ед.', 'Кол-во', 'Цена, ₫', 'Сумма, ₫', 'Примечание'], 1):
    c = wm.cell(3, j, h); c.font = Font(bold=True, color='FFFFFF'); c.fill = HF
for i, (it, u, q, p, note) in enumerate(BBQ):
    rr = 4 + i; wm.cell(rr, 1, it); wm.cell(rr, 2, u); wm.cell(rr, 3, q); wm.cell(rr, 4, p); wm.cell(rr, 5, f'=C{rr}*D{rr}'); wm.cell(rr, 6, note)
    for j in (4, 5): wm.cell(rr, j).number_format = '#,##0'
rr = 4 + len(BBQ); wm.cell(rr, 1, 'Итого мангальная').font = Font(bold=True); wm.cell(rr, 5, f'=SUM(E4:E{rr - 1})').font = Font(bold=True); wm.cell(rr, 5).number_format = '#,##0'
for j, w in enumerate([62, 7, 8, 14, 16, 30], 1): wm.column_dimensions[get_column_letter(j)].width = w
# quantities sheet
wq = wb.create_sheet('Объёмы')
Q = [('Площадь зоны (без подъезда)', 446.5, 'м²'), ('Площадь кровли', RQ['roof_m2'], 'м²'), ('Открытые дворики', RQ['courts_m2'], 'м²'), ('Металл навеса', steel_t, 'т'),
     ('Пол керамогранит', area_floor, 'м²'), ('Айван', zm['platform'], 'м²'), ('Аллея', zm['alley'], 'м²'), ('Мангальная', zm['bbq'], 'м²'),
     ('Столы-модули', n_mod, 'шт'), ('Стулья', n_chairs, 'шт'), ('Посадочных мест', G['total'], ''), ('Уличные скамьи', sbench, 'м')]
for i, (a, b, c) in enumerate(Q): wq.cell(i + 1, 1, a); wq.cell(i + 1, 2, b); wq.cell(i + 1, 3, c)
wq.column_dimensions['A'].width = 34
# python-side totals for reporting
base = sum(q * p for _, _, _, q, p, *_ in S) + sum(q * p for _, _, q, p, _ in BBQ)
eco = sum(q * (pe if pe is not None else p) for _, _, _, q, p, _, _, pe in S) + sum(q * p for _, _, q, p, _ in BBQ)
secs = {}
for sec, _, _, q, p, *_ in S: secs[sec] = secs.get(sec, 0) + q * p
secs['7. Мангальная'] = sum(q * p for _, _, q, p, _ in BBQ)
print(json.dumps({k: round(v / 1e6) for k, v in secs.items()}, ensure_ascii=False))
print('base M', round(base / 1e6), 'eco M', round(eco / 1e6), 'grand M', round((base * 1.1 + 45e6) / 1e6), 'grand eco M', round((eco * 1.1 + 45e6) / 1e6))
path = f"{OUT}/samarkand-estimate-{G['REV']}.xlsx"; wb.save(path); print('saved', path, 'steel_t', steel_t, 'floor', area_floor, 'chairs', n_chairs)
