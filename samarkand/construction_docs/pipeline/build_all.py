import sys
from matplotlib.backends.backend_pdf import PdfPages
from lib import *
import build1 as B1, build2 as B2, sheets_plans as SP
SHEETS = [B1.sheet_cover, B1.sheet_general, B1.sheet_zoning, SP.sheet_plan, B1.sheet_floor, B1.sheet_rcp, B1.sheet_roof,
          B2.sheet_elev, B2.sheet_sections, B2.sheet_column, B2.sheet_aivan, B2.sheet_booth, B2.sheet_coffers, B2.sheet_dome, B2.sheet_bar,
          B2.sheet_corr, B2.sheet_eave, B2.sheet_mangal, B2.sheet_floor_details, B2.sheet_furniture, B2.sheet_finishes, B2.sheet_lighting,
          lambda p, n, t: B2.sheet_persp(p, n, t, 'PC-01', [('r_street.jpg', 'Mặt tiền phố / street front'), ('r_booths_ext.jpg', 'Cabin VIP nhìn từ phố / booths from the street'), ('r_hall2.jpg', 'Sảnh nhìn về mái vòm / hall to the dome'), ('r_dome.jpg', 'Mái vòm & đèn chùm / dome & chandelier')], 'Phối cảnh 1'),
          lambda p, n, t: B2.sheet_persp(p, n, t, 'PC-02', [('r_aivan.jpg', 'Aivan'), ('r_booth.jpg', 'Bên trong cabin / inside a booth'), ('r_corr.jpg', 'Hành lang vòm / arcade corridor'), ('r_bar.jpg', 'Quầy bar / bar')], 'Phối cảnh 2')]
only = [int(a) for a in sys.argv[1:]]
out = os.path.join(OUT, 'test.pdf' if only else 'Samarkand_KT_R12-v11.7.pdf')
with PdfPages(out) as pdf:
    for i, f in enumerate(SHEETS, 1):
        if only and i not in only: continue
        try: f(pdf, i, len(SHEETS)); print('ok', i, flush=True)
        except Exception as e:
            import traceback; traceback.print_exc(); print('FAIL', i, e)
print(out)
