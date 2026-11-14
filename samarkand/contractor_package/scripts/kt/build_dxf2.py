"""All hidden-line views as true vector geometry, 1:1 in mm, one DXF (R12 for maximum compatibility)."""
import json, os, numpy as np
from ezdxf.addons.r12writer import r12writer
H = 'hlr/out'
ROWS = [('PLANS', [('plan', 'FURNITURE PLAN (cut +1.20)'), ('floorplan', 'FLOOR FINISH PLAN (furniture removed)'), ('rcp', 'REFLECTED CEILING PLAN'), ('roof', 'ROOF FRAMING PLAN')]),
        ('ELEVATIONS / SECTIONS', [('el_east', 'STREET ELEVATION'), ('el_south', 'SOUTH ELEVATION'), ('el_north', 'NORTH ELEVATION'), ('sec_A', 'SECTION A-A'), ('sec_B', 'SECTION B-B'), ('sec_C', 'SECTION C-C')]),
        ('WALL DEVELOPMENTS', [('dev_aivan', 'AIVAN WALL'), ('dev_bar', 'BAR BACK WALL'), ('dev_barfront', 'BAR COUNTER FRONT'), ('dev_station', 'WAITER STATION'), ('dev_booths', 'BOOTH ROW'), ('dev_hall_e', 'HALL LOOKING TO STREET'), ('dev_photo', 'PHOTO ZONE'), ('dev_kids', 'KIDS ZONE'), ('det_mangal', 'MANGAL WALL')]),
        ('DETAILS', [('det_column', 'STREET COLUMN'), ('det_aivan', 'AIVAN SECTION'), ('det_booth', 'BOOTH SECTION'), ('det_booth_plan', 'BOOTH PLAN'), ('det_dome', 'DOME SECTION'), ('det_bar', 'BAR SECTION'), ('det_bar_plan', 'BAR PLAN'), ('det_corr', 'CORRIDOR SECTION'),
                     ('det_eave', 'STREET EAVE'), ('det_pishtaq', 'PORTAL ELEVATION'), ('det_pishtaq_sec', 'PORTAL SECTION'), ('det_pishtaq_plan', 'PORTAL PLAN'), ('det_tent', 'TENT SECTION'), ('det_north', 'NORTH ZONE PLAN')]),
        ('FURNITURE', [(f'f_{k}_{v}', f'{t} - {v.upper()}') for k, t in [('chair', 'CHAIR'), ('settee', 'BOOTH SETTEE'), ('aivset', 'AIVAN SETTEE'), ('table', 'TRESTLE TABLE'), ('t4', 'HALL TABLE 4'), ('t2', 'HALL TABLE 2'), ('stool', 'BAR STOOL'), ('host', 'HOST STAND'), ('stcab', 'STATION CABINET'), ('tapchan', 'TAPCHAN'), ('tent', 'TENT')] for v in ('front', 'side', 'plan')])]
out = 'kt/out/Samarkand_R12-v12.1_drawings.dxf'; n = 0
with r12writer(out) as dxf:
    y0 = 0.0
    for rname, views in ROWS:
        x0 = 0.0; hmax = 0.0
        dxf.add_text(rname, (x0, y0 + 1500), height=700, layer='A-TITLE', color=3)
        for name, title in views:
            J = json.load(open(f'{H}/{name}.json')); V = np.asarray(J['vis'], float).reshape(-1, 5)[:, :4] * 1000
            cs = [np.asarray(ss, float).reshape(-1, 4) * 1000 for _, ss in J['cut']]; C = np.concatenate(cs) if cs else np.zeros((0, 4))
            if name == 'rcp': V[:, [1, 3]] *= -1; C[:, [1, 3]] *= -1
            A = np.concatenate([V, C]); h0 = min(A[:, 0].min(), A[:, 2].min()); h1 = max(A[:, 0].max(), A[:, 2].max()); v0 = min(A[:, 1].min(), A[:, 3].min()); v1 = max(A[:, 1].max(), A[:, 3].max())
            # clip very distant background (window of the camera): keep
            V = V[np.hypot(V[:, 2] - V[:, 0], V[:, 3] - V[:, 1]) > 2.0]
            ox, oy = x0 - h0, y0 - v1
            for a in np.round(V, 1): dxf.add_line((a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy), layer='A-VIEW', color=7)
            for a in np.round(C, 1): dxf.add_line((a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy), layer='A-CUT', color=2)
            n += len(V) + len(C)
            th = 250 if (h1 - h0) > 6000 else 90
            dxf.add_text(f'{title}   1:1 mm', (x0, y0 - (v1 - v0) - th * 2.2), height=th, layer='A-TITLE', color=3)
            x0 += (h1 - h0) + max(1500, 0.08 * (h1 - h0)); hmax = max(hmax, v1 - v0)
        y0 -= hmax + 6000
print(n, os.path.getsize(out) / 1e6)
