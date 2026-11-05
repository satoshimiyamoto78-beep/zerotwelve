"""rev. 9.9 (owner: 'aivan tables are in the way; sofas like our chairs — two chairs joined, a bit longer, wooden, with cushions'):
  * a_settee(L): the carved-chair family stretched to a 2-seat settee (brass bun feet, arched aprons, pierced arms + back,
    moulded rails, a middle leg pair, two seat + two back cushions in the Persian rug upholstery). Seat +0.50, depth 546.
  * aivan bays (1.74 between the screens): two settees 1.30 long face each other at the wall, table 1.10 x 0.60 (walnut + real
    100 mm glazed tile inlay) set back to the wall, so the last 0.40 by the aisle is free to step into the bay."""
@cached
def a_settee(L):
    b = MB(); W = XW['wd']; BR = m['brass']; hx = L / 2
    py0, py1 = 0.21, 0.26
    for xs in ((-hx, -hx + 0.05), (hx - 0.05, hx), (-0.025, 0.025)):
        for sy in (-1, 1):
            x0, x1 = xs; y0, y1 = sorted((sy * py0, sy * py1)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            mid = abs(cx) < 0.1
            b.lathe(cx, cy, 0.0, [(0.0, 0.0), (0.012, 0.0), (0.022, 0.012), (0.021, 0.026), (0.016, 0.035), (0.0, 0.035)], BR, 16)
            top_ = (0.43 if sy > 0 else 0.875) if mid else (0.62 if sy > 0 else 0.955)
            b.box(x0, y0, 0.035, x1, y1, top_, W, 0.004)
            if sy < 0 and not mid: b.lathe(cx, cy, 0.955, [(0.0, 0.0), (0.03, 0.0), (0.03, 0.012), (0.018, 0.022), (0.008, 0.034), (0.0, 0.036)], W, 12)
            elif not mid: b.box(x0 - 0.004, y0 - 0.004, 0.33, x1 + 0.004, y1 + 0.004, 0.345, W, 0.002)
    ix = hx - 0.05
    b.box(-ix, 0.22, 0.36, ix, 0.25, 0.43, W, 0.003); b.box(-ix, -0.25, 0.36, ix, -0.22, 0.43, W, 0.003)
    for sx in (-1, 1): b.box(sx * (hx - 0.045), -py0, 0.36, sx * (hx - 0.012), py0, 0.43, W, 0.003)
    b.box(-ix + 0.005, -0.22, 0.40, ix - 0.005, 0.22, 0.42, W)
    for a0, a1 in ((-ix, -0.025), (0.025, ix)):                                                      # arched aprons, two bays
        for q in arch_apron(a0, 0.13, a1, 0.36, 0.25, 0.33): b.extrude(list(q.exterior.coords)[:-1], 0.226, 0.244, W, 'xz')
        for q in arch_apron(a0, 0.13, a1, 0.36, 0.25, 0.33): b.extrude(list(q.exterior.coords)[:-1], -0.244, -0.226, W, 'xz')
    for sx in (-1, 1):
        for q in arch_apron(-py0, 0.13, py0, 0.36, 0.25, 0.33): b.extrude(list(q.exterior.coords)[:-1], sx * (hx - 0.033), sx * (hx - 0.017), W, 'yz')
        b.box(sx * (hx - 0.045), -py0, 0.43, sx * (hx - 0.012), py0, 0.455, W, 0.002)
        for q in jali(-py0, 0.455, py0, 0.615, 0.053, 0.012): ext_holes(b, q, sx * (hx - 0.033), sx * (hx - 0.019), W, 'yz')
        x0, x1 = sorted((sx * (hx - 0.054), sx * (hx + 0.012)))
        b.box(x0, -py0, 0.62, x1, 0.29, 0.645, W, 0.006); b.box(x0 + 0.006, -py0, 0.645, x1 - 0.006, 0.282, 0.66, W, 0.004)
    b.box(-ix, -0.25, 0.43, ix, -0.222, 0.55, W, 0.003)
    for a0, a1 in ((-ix, -0.025), (0.025, ix)):
        for q in jali(a0, 0.55, a1, 0.875, 0.058, 0.014): ext_holes(b, q, -0.244, -0.228, W, 'xz')
    b.box(-ix, -0.252, 0.875, ix, -0.218, 0.94, W, 0.004); b.box(-ix, -0.256, 0.94, ix, -0.214, 0.955, W, 0.004)
    hard = b.mesh(f'Settee_frame_{int(L * 100)}')
    s = MB(); hw = (ix - 0.012) / 2
    for k, cx in enumerate((-(hw + 0.006), hw + 0.006)):
        s.box(cx - hw, -0.21, 0.42, cx + hw, 0.215, 0.515, XW['k1' if k else 'k2'], 0.03)
        s.box(cx - hw + 0.02, -0.219, 0.515, cx + hw - 0.02, -0.15, 0.71, XW['k2' if k else 'k1'], 0.03)
    return merge(f'Settee_{int(L * 100)}', [hard, soften(s.mesh(f'Settee_cushions_{int(L * 100)}'), 2)])
@cached
def a_teatable(L, Dp):
    """walnut table L x Dp, top +0.75 with a flush field of 100 mm glazed tiles, four turned legs"""
    b = MB(); W = XW['wd']
    b.box(-L / 2, -Dp / 2, 0.72, L / 2, Dp / 2, 0.75, W, 0.006)
    b.box(-L / 2 + 0.06, -Dp / 2 + 0.06, 0.75, L / 2 - 0.06, Dp / 2 - 0.06, 0.752, MORTAR)
    n, mrows = int((L - 0.12) / 0.103), int((Dp - 0.12) / 0.103)
    for i in range(n):
        for j in range(mrows):
            x0 = -n * 0.103 / 2 + i * 0.103; y0 = -mrows * 0.103 / 2 + j * 0.103
            pat = ((i % 4) in (1, 2)) == ((j % 4) in (1, 2))
            b.box(x0, y0, 0.75, x0 + 0.1, y0 + 0.1, 0.758, TILE[0] if pat else (TILE[2] if (i + j) % 2 else TILE[1]), 0.002)
    b.box(-L / 2 + 0.04, -Dp / 2 + 0.04, 0.62, L / 2 - 0.04, Dp / 2 - 0.04, 0.72, W, 0.004)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.lathe(sx * (L / 2 - 0.08), sy * (Dp / 2 - 0.08), 0.0, [(0.0, 0.0), (0.03, 0.0), (0.032, 0.05), (0.022, 0.09), (0.026, 0.3), (0.02, 0.5), (0.026, 0.6), (0.03, 0.62), (0.0, 0.62)], W, 16)
    return b.mesh(f'Teatable_{int(L * 100)}x{int(Dp * 100)}')

OLDB = [(_bb(o)[0][1] + _bb(o)[1][1]) / 2 for o in bpy.data.objects if o.name.startswith('Aivan_banquette')]   # bays that had seating
_rm('Aivan_banquette', 'Aivan_table_', 'Sedir')
scr = sorted([_bb(o) for o in bpy.data.objects if o.name.startswith('Aivan_screen')], key=lambda b_: b_[0][1])
sets = sorted([o for o in bpy.data.objects if o.name.startswith('Aivan_tableset')], key=lambda o: _bb(o)[0][1])
nb = 0
for (lo1, hi1), (lo2, hi2) in zip(scr[:-1], scr[1:]):
    y0, y1 = hi1[1], lo2[1]
    if not (1.6 < y1 - y0 < 1.9): continue
    if not any(y0 < yb < y1 for yb in OLDB): continue                     # the door bay stays a free passage
    nb += 1; XC = 0.2 + 0.65
    inst(a_settee(1.3), f'Aivan_settee_{nb}a', (XC, y0 + 0.259, 0.0), 0.0, 'Aivan')
    inst(a_settee(1.3), f'Aivan_settee_{nb}b', (XC, y1 - 0.259, 0.0), math.pi, 'Aivan')
    inst(a_teatable(1.1, 0.6), f'Aivan_table_{nb}', (0.8, (y0 + y1) / 2, 0.0), 0.0, 'Aivan')
    for o_ in sets:                                                       # tea set moves onto the new table, a little tighter
        lo_, hi_ = _bb(o_)
        if y0 < (lo_[1] + hi_[1]) / 2 < y1:
            cx_ = (lo_[0] + hi_[0]) / 2; o_.location.x += 0.8 - cx_; o_.scale.x = 0.82; o_.location.z += 0.758 - lo_[2]
            bpy.context.view_layer.update(); l2, h2 = _bb(o_); o_.location.x += 0.8 - (l2[0] + h2[0]) / 2
print('rev 9.9 aivan bays rebuilt', nb)
