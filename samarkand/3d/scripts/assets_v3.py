"""Samarkand asset library v3 (client renders): open themed booths with niche walls, theme objects, vases, rattan
pendant, velvet swag, Rishtan tableware with food, stylised people. Same joinery rules as assets_r12.py (closed shells,
flush contact). Needs kit.py + assets_r12.py + the X / m material dicts in the namespace."""
import math, random

def lathe_pic(b, x, y, z, prof, mm, D, n=28):
    """lathe whose upward faces carry a top-view picture of diameter D (plates, bread)"""
    fs = b.lathe(x, y, z, prof, mm, n)
    for f in fs:
        if f.normal.z > 0.3:
            for lp in f.loops: lp[b.uv].uv = (0.5 + (lp.vert.co.x - x) / D, 0.5 + (lp.vert.co.y - y) / D)
            b.fixed.add(f)
    return fs
def scale_verts(b, fs, origin, s):
    vs = {v for f in fs for v in f.verts}
    for v in vs: v.co = Vector((origin[0] + (v.co.x - origin[0]) * s[0], origin[1] + (v.co.y - origin[1]) * s[1], origin[2] + (v.co.z - origin[2]) * s[2]))
    for f in fs: f.normal_update()

TH = 0.16                              # booth partition thickness (niche wall)
CUSH = {'sogd': 'kilim2', 'sasan': 'suzani2', 'saman': 'kilim', 'khorezm': 'ikat', 'timur': 'suzani2', 'shahr': 'kilim2', 'margil': 'ikat', 'pamir': 'kilim'}

# ---------------------------------------------------------------- NICHE WALL between booths
@cached
def a_nichewall(L, th_s, th_n):
    """plaster niche wall h 2.2 between two booths: carved end posts, plaster body with a majolica band, a through
    pointed-arch niche (sill +1.00) near the street end, carved frieze, framed epoch art on each face.
    Local x 0..L (portal side at 0), y 0..TH (south face y=0, north face y=TH)."""
    b = MB(); W = m['walnut']; P = X['plaster']; H = 2.2
    b.box(0, 0, 0, 0.08, TH, H, W, 0.004); b.box(L - 0.08, 0, 0, L, TH, H, W, 0.004)
    xn, nw, nb, zs, za, zt = L - 0.08 - 0.32, 0.42, 1.0, 1.42, 1.66, 2.06
    b.box(0.08, 0, 0, L - 0.08, TH, 0.86, P); b.box(0.08, 0, 0.86, L - 0.08, TH, nb, m['majolica'])
    b.box(0.08, 0, nb, xn - nw / 2, TH, zt, P); b.box(xn + nw / 2, 0, nb, L - 0.08, TH, zt, P)
    for poly in spandrel_polys(xn, nw, zs, za, zt): b.extrude(poly, 0, TH, P, 'xz')
    b.box(0.08, 0, zt, L - 0.08, TH, H, X['carved'])
    for th, y0, y1, face in ((th_s, -0.025, 0.0, '-y'), (th_n, TH, TH + 0.025, '+y')):
        if not th: continue
        a0, a1, z0, z1 = (0.32, 0.76, 1.08, 1.86) if face == '-y' else (0.14, 0.60, 1.08, 1.86)   # south face: clear of the stepped neighbour's curtain
        b.box(a0, y0, z0, a0 + 0.04, y1, z1, m['brass'], 0.003); b.box(a1 - 0.04, y0, z0, a1, y1, z1, m['brass'], 0.003)
        b.box(a0 + 0.04, y0, z0, a1 - 0.04, y1, z0 + 0.04, m['brass'], 0.003); b.box(a0 + 0.04, y0, z1 - 0.04, a1 - 0.04, y1, z1, m['brass'], 0.003)
        yb0, yb1 = (y1 - 0.008, y1) if face == '-y' else (y0, y0 + 0.008)
        b.picture_box(a0 + 0.04, yb0, z0 + 0.04, a1 - 0.04, yb1, z1 - 0.04, X['ep_' + th], face)
    return b.mesh(f'Nichewall_{int(L * 1000)}_{th_s}_{th_n}')

# ---------------------------------------------------------------- OPEN THEMED BOOTH
@cached
def a_booth_open(theme):
    """themed booth open to the street / sea: local x 0..1.30 (portal at x=0, street side at 1.30), y 0..2.0;
    the niche wall at y 0..TH is separate (a_nichewall), the next one closes y = 2.0"""
    b = MB(); W = m['walnut']; Wd = 2.0; P = X['plaster']; cm = X[CUSH[theme]] if CUSH[theme] in X else m[CUSH[theme]]
    # cap (velvet board resting on the walls) + quilted suzani panels under it + brass fascia
    b.box(-0.07, 0.0, 2.2, 1.3, Wd, 2.25, X['velvet'])
    nx, ny = 5, 5; x0q, x1q, y0q, y1q = 0.02, 1.2, TH + 0.02, Wd - 0.02
    for i in range(nx):
        for j in range(ny):
            ax, bx = x0q + (x1q - x0q) * i / nx, x0q + (x1q - x0q) * (i + 1) / nx; ay, by = y0q + (y1q - y0q) * j / ny, y0q + (y1q - y0q) * (j + 1) / ny
            b.box(ax + 0.004, ay + 0.004, 2.165, bx - 0.004, by - 0.004, 2.2, X['quilt'], 0.012)
    b.box(-0.09, 0.0, 2.08, -0.07, Wd, 2.25, m['brass'])
    # portal posts + carved pointed-arch head + plaque
    b.box(-0.07, 0.0, 0, 0.0, 0.22, 2.2, W, 0.003); b.box(-0.07, Wd - 0.22, 0, 0.0, Wd, 2.2, W, 0.003)
    for poly in spandrel_polys(Wd / 2, Wd - 0.44, 1.8, 2.12, 2.2): b.extrude(poly, -0.07, 0.0, X['carved'], 'yz')
    b.box(-0.075, 0.04, 1.45, -0.07, 0.18, 1.62, m['brass'])
    # velvet swag in front of the portal head + two tails at the posts
    rows = []
    for zz_t in (0.0, 1.0):
        rows.append([(-0.1, Wd * c / 12, 2.2 - zz_t * (0.07 + 0.2 * math.sin(math.pi * c / 12))) for c in range(13)])
    b.sheet(rows, X['velvet'], 0.006, picture=False)
    for yy0, yy1 in ((0.0, 0.22), (Wd - 0.22, Wd)):
        b.sheet([[(-0.1, yy0 + (yy1 - yy0) * c / 3, zz) for c in range(4)] for zz in (1.55, 2.12)], X['velvet'], 0.006, picture=False)
    # street side: plaster parapet with a majolica cap, carved arch framing the sea view
    b.box(1.14, TH, 0, 1.3, Wd, 0.72, P); b.box(1.12, TH, 0.72, 1.3, Wd, 0.78, m['majolica'], 0.003)
    for poly in spandrel_polys((TH + Wd) / 2, Wd - TH, 1.75, 2.1, 2.2): b.extrude(poly, 1.22, 1.3, X['carved'], 'yz')
    # curtain rod (wall face to wall face) + tied-back curtains
    b.rod((0.03, TH, 2.08), (0.03, Wd, 2.08), 0.012, m['brass'], 10)
    for side in (0, 1):
        ya = TH + 0.01 if side == 0 else Wd - 0.01; sg = 1 if side == 0 else -1; rows = []
        for zz, wdt, tie in ((2.066, 0.46, 0), (1.6, 0.24, 0), (1.05, 0.07, 1), (0.55, 0.15, 0), (0.01, 0.24, 0)):
            rows.append([(0.035 + 0.025 * math.sin(c / 8 * math.pi * 3 + (0.6 if tie else 0)), ya + sg * (0.05 + wdt * c / 8 if tie else wdt * c / 8), zz) for c in range(9)])
        rows.reverse(); b.sheet(rows, X['velvet'], 0.006, picture=False)
    # benches with seat pads + theme back cushions against the niche walls, table on a pedestal
    for y0, y1, yb0, yb1 in ((TH, TH + 0.5, TH, TH + 0.14), (Wd - 0.5, Wd, Wd - 0.14, Wd)):
        b.box(0.08, y0, 0, 1.14, y1, 0.38, W, 0.003)
        b.box(0.1, y0 + 0.01, 0.38, 1.12, y1 - 0.01, 0.45, cm, 0.015)
        b.box(0.12, yb0, 0.45, 1.1, yb1, 0.9, cm, 0.02)
    b.box(0.15, 0.73, 0.72, 1.05, 1.43, 0.76, m['oak'], 0.004)
    b.box(0.4, 0.88, 0, 0.8, 1.28, 0.025, m['bronze'], 0.003); b.box(0.56, 1.04, 0.025, 0.64, 1.12, 0.72, m['bronze'], 0.002)
    return b.mesh(f'Booth_open_{theme}')

# ---------------------------------------------------------------- VASES + THEME OBJECTS
@cached
def a_vase(kind):
    b = MB()
    if kind == 0: b.lathe(0, 0, 0, [(0.0, 0), (0.035, 0), (0.06, 0.08), (0.055, 0.2), (0.025, 0.3), (0.022, 0.34), (0.035, 0.37), (0.0, 0.37)], m['lapis'], 24)
    elif kind == 1:                                                               # brass kumgan
        b.lathe(0, 0, 0, [(0.0, 0), (0.04, 0), (0.065, 0.1), (0.05, 0.19), (0.02, 0.24), (0.02, 0.3), (0.035, 0.31), (0.0, 0.33)], m['brass'], 24)
        b.rod((0.055, 0, 0.12), (0.11, 0, 0.26), 0.008, m['brass'], 6)
    elif kind == 2: b.lathe(0, 0, 0, [(0.0, 0), (0.04, 0), (0.065, 0.06), (0.06, 0.16), (0.03, 0.22), (0.04, 0.25), (0.0, 0.25)], m['clay'], 20)
    else: b.lathe(0, 0, 0, [(0.0, 0), (0.03, 0), (0.035, 0.03), (0.065, 0.06), (0.068, 0.1), (0.0, 0.08)], m['turq'], 24)
    return b.mesh(f'Vase_{kind}')
@cached
def a_monument(theme):
    """small museum object for the booth parapet (footprint <= 0.30 x 0.15); origin = bottom centre"""
    b = MB()
    b.box(-0.14, -0.07, 0, 0.14, 0.07, 0.04, m['walnut'], 0.003)                     # plinth
    z = 0.04
    if theme == 'sogd':                                                                # terracotta ossuary with gabled lid
        b.box(-0.1, -0.05, z, 0.1, 0.05, z + 0.12, m['clay'], 0.004)
        b.extrude([(-0.1, z + 0.12), (0.1, z + 0.12), (0.0, z + 0.2)], -0.05, 0.05, m['clay'], 'xz')
    elif theme == 'sasan':                                                             # silver plate on a stand
        b.box(-0.04, -0.03, z, 0.04, 0.03, z + 0.02, m['walnut']); b.rod((0, 0, z + 0.02), (0, 0, z + 0.14), 0.006, m['brass'], 6)
        b.rod((0, -0.01, z + 0.14), (0, 0.0, z + 0.142), 0.11, m['steel'], 32)
    elif theme == 'saman':                                                             # epigraphic bowl
        b.lathe(0, 0, z, [(0.0, 0), (0.04, 0), (0.05, 0.02), (0.12, 0.08), (0.11, 0.085), (0.0, 0.03)], m['ceramic'], 32)
    elif theme == 'khorezm':                                                           # majolica stele
        b.box(-0.08, -0.03, z, 0.08, 0.03, z + 0.24, m['majolica'], 0.004); b.box(-0.09, -0.035, z + 0.24, 0.09, 0.035, z + 0.26, m['brass'])
    elif theme == 'timur':                                                             # miniature ribbed dome on a cube
        b.box(-0.07, -0.06, z, 0.07, 0.06, z + 0.1, m['majolica'], 0.003)
        b.lathe(0, 0, z + 0.1, [(0.0, 0), (0.055, 0), (0.07, 0.06), (0.05, 0.11), (0.0, 0.14)], X['domeglaze'], 24)
        b.lathe(0, 0, z + 0.24, [(0.0, 0), (0.008, 0), (0.0, 0.05)], m['brass'], 8)
    elif theme == 'shahr':                                                             # pishtaq model
        b.extrude([(-0.11, z), (0.11, z), (0.11, z + 0.2), (-0.11, z + 0.2)], -0.04, 0.04, m['majolica'], 'xz')
        for sx in (-1, 1): b.cyl(sx * 0.095, 0, z + 0.2, z + 0.26, 0.015, m['band'], 10)
    elif theme == 'margil':                                                            # stack of ikat silk bolts
        for i, (yy, zz) in enumerate(((-0.03, 0.03), (0.03, 0.03), (0.0, 0.082))):
            b.rod((-0.12, yy, z + zz), (0.12, yy, z + zz), 0.03, m['ikat'], 16)
    else:                                                                              # pamir chirog lamp
        b.lathe(0, 0, z, [(0.0, 0), (0.05, 0), (0.05, 0.02), (0.02, 0.05), (0.02, 0.14), (0.06, 0.16), (0.0, 0.17)], m['clay'], 16)
        b.lathe(0, 0, z + 0.17, [(0.0, 0), (0.012, 0), (0.0, 0.03)], X['lampglow'], 8)
    return b.mesh(f'Theme_object_{theme}')
@cached
def a_rattan():
    """rattan drum pendant d 0.4, h 0.26; origin = centre of the bottom; hook top at +0.30"""
    b = MB(); b.lathe(0, 0, 0, [(0.0, 0), (0.17, 0), (0.2, 0.04), (0.2, 0.22), (0.17, 0.26), (0.0, 0.26)], X['rattan'], 32)
    b.cyl(0, 0, -0.012, 0.0, 0.12, X['lampglow'], 24); b.cyl(0, 0, 0.26, 0.3, 0.02, m['brass'], 8)
    return b.mesh('Rattan_pendant')

# ---------------------------------------------------------------- TABLEWARE + FOOD
def _plate_r(b, x, y, z, r=0.12):
    lathe_pic(b, x, y, z, [(0.0, 0), (r * 0.55, 0), (r * 0.92, 0.012), (r, 0.022), (r * 0.96, 0.024), (r * 0.55, 0.012), (0.0, 0.012)], X['rishtan'], 2 * r, 28)
def _lagan_plov(b, x, y, z):
    lathe_pic(b, x, y, z, [(0.0, 0), (0.09, 0), (0.15, 0.02), (0.165, 0.032), (0.0, 0.016)], X['rishtan'], 0.33, 32)
    b.lathe(x, y, z + 0.016, [(0.0, 0), (0.12, 0), (0.1, 0.035), (0.05, 0.065), (0.0, 0.075)], X['plov'], 24)
    for k in range(6):
        a = 2 * math.pi * k / 6; b.obox(x + 0.045 * math.cos(a), y + 0.045 * math.sin(a), z + 0.07, z + 0.1, 0.035, 0.03, a, X['meat'])
def _bread(b, x, y, z, r=0.09):
    lathe_pic(b, x, y, z, [(0.0, 0), (r * 0.9, 0), (r, 0.012), (r * 0.95, 0.028), (r * 0.5, 0.02), (0.0, 0.016)], X['bread'], 2 * r, 24)
def _teapot2(b, x, y, z):
    b.lathe(x, y, z, [(0.0, 0), (0.05, 0), (0.08, 0.05), (0.075, 0.1), (0.04, 0.125), (0.0, 0.125)], m['lapis'], 24)
    b.lathe(x, y, z + 0.125, [(0.0, 0), (0.04, 0), (0.035, 0.018), (0.012, 0.028), (0.016, 0.04), (0.0, 0.046)], m['lapis'], 16)
    b.rod((x + 0.077, y, z + 0.07), (x + 0.15, y, z + 0.13), 0.009, m['lapis'], 8)
    b.ring(x - 0.09, y, z + 0.075, [(0.0, -0.035), (0.014, -0.035), (0.014, 0.035), (0.0, 0.035)], m['lapis'], 4) if False else None
def _glass(b, x, y, z):
    b.lathe(x, y, z, [(0.0, 0), (0.025, 0), (0.03, 0.03), (0.022, 0.055), (0.03, 0.09), (0.0, 0.09)], m['glass'], 16)
@cached
def a_tableset(n):
    """Rishtan plates for 2n seats + plov, bread, teapot, tea glasses on a module table (top +0.76); origin = table centre"""
    b = MB(); Lx = 0.7 * n; z = 0.76
    b.picture_box(-Lx / 2 + 0.06, -0.13, z, Lx / 2 - 0.06, 0.13, z + 0.003, X['kilim2'], '+z')
    for j in range(n):
        cx = -Lx / 2 + 0.35 + 0.7 * j
        for sy in (-1, 1): _plate_r(b, cx, sy * 0.265, z); _glass(b, cx + 0.2, sy * 0.27, z)
    if n >= 2:
        _lagan_plov(b, -0.2, 0.0, z + 0.003); _bread(b, 0.15, 0.0, z + 0.003); _teapot2(b, 0.42, 0.0, z + 0.003)
    else:
        _bread(b, -0.12, 0.0, z + 0.003); _teapot2(b, 0.12, 0.0, z + 0.003)
    return b.mesh(f'Tableset_{2 * n}p')
@cached
def a_boothset():
    """set for the booth table (x 0.15..1.05, y 0.73..1.43, top +0.76) in booth-local coordinates"""
    b = MB(); z = 0.76
    for px, py in ((0.33, 0.88), (0.87, 0.88), (0.33, 1.28), (0.87, 1.28)): _plate_r(b, px, py, z, 0.115)
    _lagan_plov(b, 0.6, 1.08, z); _teapot2(b, 0.28, 1.08, z); _bread(b, 0.9, 1.08, z, 0.08)
    return b.mesh('Boothset')

# ---------------------------------------------------------------- PEOPLE (stylised architectural figures)
SKIN = [(0.80, 0.62, 0.48), (0.66, 0.47, 0.34), (0.55, 0.38, 0.28), (0.86, 0.70, 0.58)]
CLOTH = [(0.85, 0.82, 0.76), (0.12, 0.16, 0.28), (0.55, 0.12, 0.12), (0.20, 0.35, 0.30), (0.75, 0.55, 0.25), (0.92, 0.92, 0.9), (0.30, 0.30, 0.32), (0.45, 0.30, 0.55)]
def pmat(kind, i):
    c = (SKIN if kind == 'skin' else CLOTH)[i % (4 if kind == 'skin' else 8)]
    return mat(f'p_{kind}_{i}', c, rough=0.75 if kind != 'skin' else 0.5)
@cached
def a_person(pose, sk, top_, bot, hair, female):
    """stylised person, faces +Y, origin at the floor under the pelvis. pose: 'stand' | 'sit' (chair seat +0.495) | 'bench' (+0.45)"""
    b = MB(); S, T, B_, Hm = pmat('skin', sk), pmat('cloth', top_), pmat('cloth', bot), mat(f'p_hair_{hair}', [(0.08, 0.06, 0.05), (0.25, 0.16, 0.08), (0.5, 0.45, 0.42)][hair], rough=0.6)
    shoe = mat('p_shoe', (0.1, 0.08, 0.07), rough=0.5)
    if pose == 'stand':
        hip = 0.92
        for sx in (-1, 1):
            b.box(sx * 0.1 - 0.05, -0.06, 0, sx * 0.1 + 0.05, 0.16, 0.07, shoe, 0.01)
            b.rod((sx * 0.1, 0.0, 0.07), (sx * 0.1, 0.0, hip), 0.065, B_, 10)
        if female: b.lathe(0, 0, 0.5, [(0.0, 0), (0.24, 0), (0.17, 0.45), (0.0, 0.47)], B_, 20)
    else:
        hip = 0.495 if pose == 'sit' else 0.45
        for sx in (-1, 1):
            b.box(sx * 0.1 - 0.05, 0.42, 0, sx * 0.1 + 0.05, 0.62, 0.07, shoe, 0.01)
            b.rod((sx * 0.1, 0.48, 0.07), (sx * 0.1, 0.48, hip + 0.06), 0.055, B_, 10)
            b.rod((sx * 0.1, -0.02, hip + 0.065), (sx * 0.1, 0.48, hip + 0.065), 0.065, B_, 10)
    z0 = hip
    fs = b.lathe(0, 0, z0, [(0.0, 0), (0.17, 0), (0.18, 0.08), (0.14, 0.24), (0.19, 0.42), (0.17, 0.52), (0.07, 0.56), (0.0, 0.56)], T, 20)
    scale_verts(b, fs, (0, 0, z0), (1.0, 0.62, 1.0))
    b.cyl(0, 0, z0 + 0.56, z0 + 0.62, 0.05, S, 12)
    fh = b.lathe(0, 0.0, z0 + 0.62, [(0.0, 0), (0.07, 0.02), (0.095, 0.09), (0.085, 0.17), (0.05, 0.22), (0.0, 0.235)], S, 20)
    b.lathe(0, -0.01, z0 + 0.72, [(0.0, 0), (0.1, 0.0), (0.1, 0.06), (0.06, 0.13), (0.0, 0.145)], Hm, 20)
    sh = z0 + 0.5
    for sx in (-1, 1):
        if pose == 'stand':
            el, wr = (sx * 0.25, 0.02, sh - 0.28), (sx * 0.27, 0.06, sh - 0.55)
        else:
            el, wr = (sx * 0.24, 0.12, sh - 0.27), (sx * 0.17, 0.42, 0.79)
        b.rod((sx * 0.2, 0, sh), el, 0.045, T, 8); b.rod(el, wr, 0.038, S if pose != 'stand' else T, 8)
        b.lathe(wr[0], wr[1], wr[2] - 0.04, [(0.0, 0), (0.035, 0.01), (0.04, 0.05), (0.0, 0.08)], S, 10)
    return b.mesh(f'Person_{pose}_{sk}{top_}{bot}{hair}{int(female)}')
