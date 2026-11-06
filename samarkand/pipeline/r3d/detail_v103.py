"""rev. 10.3 (owner: 'joints — where a rail meets a stair, a wall, a column — have to be worked out properly'):
stairs up to the aivan (south, middle) and the bar steps rebuilt as real flights: 3 risers of 150, stone treads 30 thick with a
20 mm bullnose overhang and a brass anti-slip inlay 30 mm behind the nosing, risers clad in glazed 100 mm tiles;
brass handrails d 42 on both sides at +0.90 over the nosing line, 300 mm level extensions top and bottom, bottom end returned into
a post with a ball finial, top end into a newel on the top tread, intermediate posts <= 1.0 m, base rosettes on every post."""
_rm('stepsA', 'stepsB', 'barsteps')
BRS = m['brass']; STN = STONE_
def flight(name, x0, x1, y0, y1, up, nrise=3):
    """steps over the box (x0..x1, y0..y1) from TER to TER + 0.45, rising towards `up` ('-x' or '+y'); returns the nosing line"""
    b = MB(); R = 0.45 / nrise
    along_x = up == '-x'
    run = ((x1 - x0) if along_x else (y1 - y0)) / nrise
    nos = []
    for k in range(nrise):
        zt = TER + R * (k + 1)
        if along_x:
            xr = x1 - run * k                                           # riser face of step k (bottom step k = 0)
            b.box(x0, y0, TER, xr - 0.0, y1, zt - 0.03, MORTAR)
            for ya_, yb_ in ((y0 - 0.02, y0), (y1, y1 + 0.02)): b.box(x0 + 0.045, ya_, TER, xr, yb_, zt - 0.03, STN, 0.003)    # stone cheeks
            b.box(x0, y0, zt - 0.03, xr + 0.02, y1, zt, STN, 0.006)
            b.box(xr - 0.05, y0 + 0.05, zt, xr - 0.03, y1 - 0.05, zt + 0.002, BRS)
            tile_band(b, 'x', xr, 1, y0 + 0.01, y1 - 0.01, zt - R + 0.01, zt - 0.03)
            nos.append((xr + 0.02, zt))
        else:
            yr = y0 + run * k
            b.box(x0, yr, TER, x1, y1, zt - 0.03, MORTAR)
            if x0 > 0.6: [b.box(xa_, yr, TER, xb_, y1, zt - 0.03, STN, 0.003) for xa_, xb_ in ((x0 - 0.02, x0), (x1, x1 + 0.02))]
            b.box(x0, yr - 0.02, zt - 0.03, x1, y1, zt, STN, 0.006)
            b.box(x0 + 0.05, yr + 0.03, zt, x1 - 0.05, yr + 0.05, zt + 0.002, BRS)
            tile_band(b, 'y', yr, -1, x0 + 0.01, x1 - 0.01, zt - R + 0.01, zt - 0.03)
            nos.append((yr - 0.02, zt))
    inst(b.mesh(name), name, (0, 0, 0), 0, 'Aivan')
    return nos, run
def handrail(name, pts):
    """pts: polyline (x, y, z) of the rail centre; posts drop from every vertex to the surface z given as the 4th value"""
    b = MB()
    for (xa, ya, za, _), (xb_, yb2, zb, _) in zip(pts[:-1], pts[1:]): b.rod((xa, ya, za), (xb_, yb2, zb), 0.021, BRS, 16)
    for x, y, z, zf in pts:
        b.cyl(x, y, zf, z - 0.021, 0.016, BRS, 16)
        b.cyl(x, y, zf, zf + 0.006, 0.04, BRS, 24)                                  # rosette on the tread / floor
    x, y, z, zf = pts[0]; b.lathe(x, y, z - 0.03, [(0.0, 0.0), (0.03, 0.03), (0.0, 0.06)], BRS, 16)   # ball finial on the bottom post
    inst(b.mesh(name), name, (0, 0, 0), 0, 'Aivan')
for nm, (x0, x1, y0, y1), up in (('stepsA', (3.3, 4.2, 15.55, 18.05), '-x'), ('stepsB', (3.3, 4.2, 24.3, 25.8), '-x'), ('barsteps', (0.55, 1.5, 14.33, 15.3), '+y')):
    nos, run = flight(f'{nm}_flight', x0, x1, y0, y1, up)
    if nm == 'barsteps': continue                                         # staff steps between the bar back wall and the counter: they are the rails
    for side, c in enumerate((y0 + 0.06, y1 - 0.06) if up == '-x' else (x0 + 0.06, x1 - 0.06)):
        if up == '-x':
            xb_, zb = nos[0]; xt, zt = nos[-1]
            pts = [(x1 + 0.3, c, zb + 0.9, TER), (xb_ - 0.05, c, zb + 0.9, zb), (xt - 0.05, c, zt + 0.9, zt), (x0 + 0.08, c, zt + 0.9, TER + 0.45)]
        else:
            yb_, zb = nos[0]; yt, zt = nos[-1]
            pts = [(c, y0 - 0.3, zb + 0.9, TER), (c, yb_ + 0.05, zb + 0.9, zb), (c, yt + 0.05, zt + 0.9, zt), (c, y1 - 0.08, zt + 0.9, TER + 0.45)]
        handrail(f'{nm}_handrail_{side}', pts)
print('rev 10.3 stairs + handrails ok')
