import sys
from matplotlib.backends.backend_pdf import PdfPages
from lib import *
import build1 as B1, build2 as B2, sheets_plans as SP
import build3 as B3
SHEETS = [B1.sheet_cover, B1.sheet_general, B1.sheet_zoning, SP.sheet_plan, B1.sheet_floor, B1.sheet_rcp, B1.sheet_roof, B2.sheet_elev, B2.sheet_sections,
          B3.sheet_dev_aivan, B3.sheet_dev_bar, B3.sheet_bar2, B3.sheet_dev_booths, B3.sheet_dev_photo, B3.sheet_north,
          B2.sheet_column, B2.sheet_aivan, B2.sheet_booth, B2.sheet_coffers, B2.sheet_dome, B2.sheet_bar, B2.sheet_corr, B2.sheet_eave, B2.sheet_mangal,
          B2.sheet_floor_details, B2.sheet_furniture, B3.sheet_portal, B2.sheet_finishes, B2.sheet_lighting,
          lambda p, n, t: B2.sheet_persp(p, n, t, 'PC-01', [('i_fac.jpg', 'Mặt tiền phố / street front'), ('i_port.jpg', 'Cổng vào / entrance portal'), ('i_hall.jpg', 'Sảnh / hall'), ('i_dome.jpg', 'Mái vòm & đèn chùm / dome & chandelier')], 'Phối cảnh mô hình 1'),
          lambda p, n, t: B2.sheet_persp(p, n, t, 'PC-02', [('i_aiv.jpg', 'Aivan'), ('i_booth.jpg', 'Cabin / booths'), ('i_bar.jpg', 'Quầy bar / bar'), ('i_north.jpg', 'Khu bắc / north zone')], 'Phối cảnh mô hình 2')]
only = [int(a) for a in sys.argv[1:]]
out = os.path.join(OUT, 'test.pdf' if only else 'Samarkand_KT_R12-v12.1.pdf')
with PdfPages(out) as pdf:
    for i, f in enumerate(SHEETS, 1):
        if only and i not in only: continue
        try: f(pdf, i, len(SHEETS)); print('ok', i, flush=True)
        except Exception as e:
            import traceback; traceback.print_exc(); print('FAIL', i, e)
print(out)
