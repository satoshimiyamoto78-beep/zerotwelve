from lib import *
D = json.load(open(os.path.join(os.path.dirname(__file__), 'model_data.json')))
YAX = [('1', 4.1), ('2', 9.85), ('3', 15.3), ('4', 18.3), ('5', 21.35), ('6', 25.6), ('7', 29.1), ('8', 32.1), ('9', 36.3)]
def streetx(y):                                     # street column line D
    return 12.639 + (9.465 - 12.639) * (y - 4.1) / (36.3 - 4.1)
XAX = [('A', lambda y: 0.0), ('B', lambda y: 4.13), ('C', lambda y: 8.0), ('D', streetx)]
def c(o): lo, hi = o[1], o[2]; return (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
def grids(v, y0=-1.2, y1=38.2, x0=-1.6, x1=14.2, both=True):
    for t, y in YAX: gridline(v, v.P(x0, y, 0), v.P(x1 if y > 3 else 14.0, y, 0), t, ends=(True, both))
    for t, f in XAX: gridline(v, v.P(f(y0 + 1), y0, 0), v.P(f(y1 - 1), y1, 0), t, ends=(True, both))

def sheet_plan(pdf, num, tot):
    pg = Page('Mặt bằng bố trí nội thất & kích thước', 'Furniture layout & dimension plan', 'KT-03', num, tot)
    v = View(pg, 'plan', 17, 40, 100, crop=(-19.3, 19.3, -11.2, 10.4), thick=1)
    grids(v)
    # overall + grid chain dimensions (top = hall side, x = -1.0)
    ys = [0.0] + [y for _, y in YAX] + [37.1]
    chain(v, [v.P(-0.6, y, 0) for y in ys], 9, side=1)
    dim(v, v.P(-0.6, 0.0, 0), v.P(-0.6, 37.1, 0), 16, side=1, text='37.100  (dài sân hiên / terrace length)')
    # depth at the entrance + aivan + booth aisle
    dim(v, v.P(0.0, 15.0, 0), v.P(3.3, 15.0, 0), 4, side=-1, text='3.300 aivan')
    dim(v, v.P(0.0, 38.0, 0), v.P(9.46, 38.0, 0), 4, side=1)
    dim(v, v.P(6.64, 29.7, 0), v.P(7.57, 29.7, 0), 3, side=1, text='≥930 lối đi / aisle')
    b = [o for o in D['booth'] if o[0] == 'Booth4_shell'][0]; lo, hi = b[1], b[2]
    dim(v, v.P(lo[0], lo[1], 0), v.P(lo[0], hi[1], 0), 5, side=-1, text='2.400 cabin')
    dim(v, v.P(lo[0], hi[1], 0), v.P(hi[0], hi[1], 0), 5, side=1, text='1.950')
    dim(v, v.P(7.66, 15.64, 0), v.P(7.66, 17.96, 0), 6, side=1, text='2.320 hành lang')
    dim(v, v.P(1.45, 7.74, 0), v.P(1.45, 14.3, 0), 6, side=1, text='6.560 quầy bar')
    # zone labels (number bubbles) + levels
    Z = [(1, 1.9, 11.2, 'Quầy bar'), (2, 6.0, 9.6, 'Sảnh ăn chính'), (3, 6.0, 19.9, 'Mái vòm'), (4, 9.0, 27.5, 'Cabin VIP'),
         (5, 1.4, 23.0, 'Aivan +0.450'), (6, 2.7, 33.5, 'Lều / Tents'), (7, 3.6, 29.7, 'Tapchan'), (8, 1.5, 4.5, 'Majlis'),
         (9, -3.6, 2.9, 'Khu trẻ em'), (10, 10.8, 6.0, 'Mangal'), (11, 9.0, 16.8, 'Hành lang vòm'), (12, 11.5, 16.8, 'Cổng Pishtaq'), (13, 6.0, 12.7, 'Cây ô liu'), (14, 11.6, 27.5, 'Ghế đường phố')]
    for n, x, y, t in Z: bubble(v, *v.P(x, y, 0), str(n), r=2.6, col=BLUE, fs=6)
    level(v, *v.P(5.0, 33.0, 0), '±0.000 FFL sân hiên (= +0.45 trên nền cát hoàn thiện)')
    level(v, *v.P(1.0, 29.5, 0), '+0.450 aivan')
    level(v, *v.P(8.4, 34.8, 0), '+0.150 cabin', side=-1)
    title(pg, 17, 33, 1, 'Mặt bằng bố trí nội thất', 'Furniture & dimension plan, cut at +1.20', 'TL / Scale 1:100', w=150)
    scalebar(pg, 172, 31, 100, 5); north(pg, 200, 31, ang=180)
    # legend + seat schedule
    leg = [f'{n}  {t}' for n, _, _, t in Z]
    text_block(pg, 214, 36.5, ['CHÚ THÍCH KHU / ZONES'] + [' · '.join(leg[i:i + 5]) for i in range(0, len(leg), 5)], fs=5.0, lh=3.1, bold_first=True)
    table(pg, 330, 37, ['Khu / Zone', 'Chỗ / Seats'], [['Sảnh 19 bàn / Hall', '58'], ['Cabin 7 / Booths', '28'], ['Aivan 4 vịnh / bays', '24'],
          ['Bar / Lều / Majlis / Tapchan', '10 / 16 / 10 / 6'], ['TỔNG TRONG NHÀ / TOTAL INSIDE', '152']], [52, 26], fs=4.6, rh=3.3)
    pg.save(pdf)
if __name__ == '__main__':
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(os.path.join(OUT, 'test_plan.pdf')) as pdf: sheet_plan(pdf, 3, 25)
