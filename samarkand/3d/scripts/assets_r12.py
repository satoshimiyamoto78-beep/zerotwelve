"""Samarkand asset library R12 (uses kit.py MB). Each function returns a cached mesh datablock built in LOCAL coords:
furniture origin = centre of the footprint at floor level; booth / tent origin = their plan corner (see each docstring).
Joinery rule: parts touch on shared planes (z of one part's top == z of the next part's bottom, side faces flush),
never overlap; small chamfers (2-4 mm) on wood, softer bevels on cushions."""
import math

def cached(fn):
    def w(*a):
        key = fn.__name__ + repr(a)
        if key not in ASSETS: ASSETS[key] = fn(*a)
        return ASSETS[key]
    return w

# ---------------------------------------------------------------- CHAIR
@cached
def a_chair():
    """carved Samarkand chair 440 x 440, seat +0.49, back +1.02; back on the -Y side, the sitter faces +Y"""
    b = MB(); L = 0.035; H = 0.22; W = m['walnut']
    for sx in (-1, 1):
        b.box(sx * H - (L if sx > 0 else 0), H - L, 0, sx * H + (0 if sx > 0 else L), H, 0.42, W, 0.003)            # front legs
        b.box(sx * H - (L if sx > 0 else 0), -H, 0, sx * H + (0 if sx > 0 else L), -H + L, 0.98, W, 0.003)          # rear legs
        b.lathe(sx * (H - L / 2), -H + L / 2, 0.98, [(0.0175, 0), (0.02, 0.012), (0.012, 0.03), (0.0, 0.04)], m['brass'], 10)
    r = 0.022
    b.box(-H + L, H - r, 0.34, H - L, H, 0.42, W, 0.002); b.box(-H + L, -H, 0.34, H - L, -H + r, 0.42, W, 0.002)      # aprons
    for sx in (-1, 1): b.box(sx * H - (r if sx > 0 else 0), -H + L, 0.34, sx * H + (0 if sx > 0 else r), H - L, 0.42, W, 0.002)
    seat = [(-H, -H + L), (-H + L, -H + L), (-H + L, -H), (H - L, -H), (H - L, -H + L), (H, -H + L), (H, H), (-H, H)]
    b.extrude(seat, 0.42, 0.44, W, 'xy', 0.002)
    b.box(-0.2, -H + L + 0.005, 0.44, 0.2, 0.2, 0.495, m['ikat'], 0.012)                                               # seat cushion
    b.box(-H + L, -H, 0.55, H - L, -H + r, 0.59, W, 0.002); b.box(-H + L, -H, 0.88, H - L, -H + r, 0.94, W, 0.002)       # back rails
    b.box(-H + L, -H + 0.006, 0.59, H - L, -H + 0.016, 0.88, X['carved'])                                             # carved panel
    b.extrude([(-H + L, 0.94), (H - L, 0.94), (H - L, 0.965), (0.0, 1.02), (-H + L, 0.965)], -H, -H + r, W, 'xz', 0.002)  # crest
    return b.mesh('Chair_carved')

# ---------------------------------------------------------------- TABLE + TABLEWARE
@cached
def a_table(n):
    """module table n x 700 (along X) x 800, top +0.72..0.76, one pedestal per module; origin = centre at floor"""
    b = MB(); Lx = 0.7 * n
    b.box(-Lx / 2, -0.4, 0.72, Lx / 2, 0.4, 0.76, m['oak'], 0.004)
    for j in range(n):
        cx = -Lx / 2 + 0.35 + 0.7 * j
        b.box(cx - 0.21, -0.21, 0, cx + 0.21, 0.21, 0.025, m['bronze'], 0.003)
        b.box(cx - 0.04, -0.04, 0.025, cx + 0.04, 0.04, 0.72, m['bronze'], 0.002)
    return b.mesh(f'Table_{2 * n}p')

def _plate(b, x, y, z):
    b.lathe(x, y, z, [(0.0, 0), (0.07, 0), (0.12, 0.012), (0.13, 0.022), (0.125, 0.024), (0.07, 0.012), (0.0, 0.012)], m['ceramic'], 24)
def _piala(b, x, y, z):
    b.lathe(x, y, z, [(0.0, 0), (0.022, 0), (0.045, 0.045), (0.041, 0.046), (0.019, 0.008), (0.0, 0.008)], m['turq'], 16)
def _teapot(b, x, y, z):
    b.lathe(x, y, z, [(0.0, 0), (0.05, 0), (0.08, 0.05), (0.075, 0.1), (0.04, 0.125), (0.0, 0.125)], m['lapis'], 20)
    b.lathe(x, y, z + 0.125, [(0.0, 0), (0.04, 0), (0.035, 0.018), (0.012, 0.028), (0.016, 0.04), (0.0, 0.046)], m['lapis'], 16)
    b.rod((x + 0.077, y, z + 0.07), (x + 0.15, y, z + 0.13), 0.009, m['lapis'], 8)
@cached
def a_tableware(n):
    """plates + pialas for 2n seats, suzani runner, teapot; sits on a module table top (+0.76); origin = table centre"""
    b = MB(); Lx = 0.7 * n; z = 0.76
    b.picture_box(-Lx / 2 + 0.06, -0.15, z, Lx / 2 - 0.06, 0.15, z + 0.003, X['carpet2'], '+z')
    for j in range(n):
        cx = -Lx / 2 + 0.35 + 0.7 * j
        for sy in (-1, 1):
            _plate(b, cx, sy * 0.25, z + (0.003 if abs(sy * 0.25) < 0.15 else 0.0)); _piala(b, cx + 0.2, sy * 0.24, z)
    if n >= 2: _teapot(b, 0.0, 0.0, z + 0.003)
    return b.mesh(f'Tableware_{2 * n}p')

# ---------------------------------------------------------------- LANTERN
@cached
def a_lantern(s=1.0):
    """brass lantern; origin = glass centre. Top of the hook at +0.39*s"""
    b = MB(); h, r = 0.17 * s, 0.135 * s
    b.cyl(0, 0, -h, h, r, X['lampglow'], 20)
    b.lathe(0, 0, -h - 0.12 * s, [(0.0, 0), (0.03 * s, 0.02 * s), (0.1 * s, 0.07 * s), (0.152 * s, 0.12 * s), (0.0, 0.12 * s)], m['brass'], 20)
    b.lathe(0, 0, h, [(0.0, 0), (0.155 * s, 0), (0.11 * s, 0.08 * s), (0.04 * s, 0.15 * s), (0.015 * s, 0.2 * s), (0.0, 0.22 * s)], m['brass'], 20)
    for k in range(8):
        a = 2 * math.pi * k / 8; b.obox((r + 0.008 * s) * math.cos(a), (r + 0.008 * s) * math.sin(a), -h, h, 0.016 * s, 0.016 * s, a, m['brass'])
    return b.mesh(f'Lantern_{s:.2f}')
@cached
def a_rod():
    """unit brass rod (scaled in Z per instance), origin at its bottom"""
    b = MB(); b.cyl(0, 0, 0, 1.0, 0.006, m['brass'], 6); return b.mesh('Rod_unit')
def lantern_at(x, y, z, s, ceil_z, cname='Lights', name='Lantern'):
    inst(a_lantern(s), name, (x, y, z), 0, cname)
    top_ = z + 0.39 * s
    if ceil_z - top_ > 0.005: inst(a_rod(), 'Rod', (x, y, top_), 0, cname, scale=(1, 1, ceil_z - top_))

# ---------------------------------------------------------------- CUSHIONS
@cached
def a_cushion(w, d, h, mat_key):
    b = MB(); mm = X[mat_key] if mat_key in X else m[mat_key]
    b.box(-w / 2, -d / 2, 0, w / 2, d / 2, h, mm, min(0.03, h * 0.3)); return b.mesh(f'Cushion_{mat_key}_{int(w * 1000)}x{int(d * 1000)}x{int(h * 1000)}')
@cached
def a_bolster(L, r, mat_key):
    b = MB(); mm = X[mat_key] if mat_key in X else m[mat_key]
    b.rod((0, -L / 2, 0), (0, L / 2, 0), r, mm, 16)
    me = b.mesh(f'Bolster_{mat_key}_{int(L * 1000)}'); return me

# ---------------------------------------------------------------- THEMED BOOTH (module 1.30 deep x 2.00 wide)
@cached
def a_partition(L):
    """carved partition h 2.2 between booths, length L (booths step along the slanted lot line);
    local x 0..L (front / portal side at 0), y 0..0.06"""
    b = MB(); W = m['walnut']
    for x0 in (0.0, L - 0.06): b.box(x0, 0, 0, x0 + 0.06, 0.06, 2.2, W, 0.003)
    b.box(0.06, 0, 0, L - 0.06, 0.06, 0.10, W, 0.002); b.box(0.06, 0, 2.12, L - 0.06, 0.06, 2.2, W, 0.002)
    b.box(0.06, 0.015, 0.10, L - 0.06, 0.045, 2.12, X['carved'])
    return b.mesh(f'Booth_partition_{int(round(L * 1000))}')
@cached
def a_booth(theme):
    """themed booth interior + portal; local x 0..1.30 (x=0 is the portal line, x grows to the street), y 0..2.0, z 0 = floor.
    The partition at y 0..0.06 is a separate asset (a_partition); the next booth's partition closes y = 2.0."""
    b = MB(); W = m['walnut']; D_, Wd = 1.3, 2.0
    # back wall: kilim dado + brass-framed epoch panel
    b.box(1.24, 0.06, 0, D_, Wd, 0.6, X['kilim'])
    b.box(1.265, 0.06, 0.6, D_, Wd, 2.2, m['brass'])
    b.picture_box(1.255, 0.16, 0.66, 1.265, Wd - 0.1, 2.08, X['ep_' + theme], '-x')
    # ceiling cap resting on the partitions, brass fascia in front of the portal head
    b.box(-0.07, 0.0, 2.2, D_, Wd, 2.25, X['velvet'])
    b.box(-0.09, 0.0, 2.08, -0.07, Wd, 2.25, m['brass'])
    # portal: two posts + carved spandrels of a pointed arch (opening 1.56)
    b.box(-0.07, 0.0, 0, 0.0, 0.22, 2.2, W, 0.003); b.box(-0.07, Wd - 0.22, 0, 0.0, Wd, 2.2, W, 0.003)
    for poly in spandrel_polys(Wd / 2, Wd - 0.44, 1.8, 2.12, 2.2): b.extrude(poly, -0.07, 0.0, X['carved'], 'yz')
    b.box(-0.075, 0.04, 1.45, -0.07, 0.18, 1.62, m['brass'])                                            # plaque
    # curtain rod (partition face to partition face) + two tied-back velvet curtains
    b.rod((0.03, 0.06, 2.08), (0.03, Wd, 2.08), 0.012, m['brass'], 10)
    for side in (0, 1):
        ya = 0.07 if side == 0 else Wd - 0.01; sg = 1 if side == 0 else -1
        rows = []
        for zz, wdt, tie in ((2.066, 0.48, 0), (1.6, 0.26, 0), (1.05, 0.07, 1), (0.55, 0.16, 0), (0.01, 0.26, 0)):
            cols = []
            for c in range(9):
                t = c / 8; yy = ya + sg * (0.05 + wdt * t if tie else wdt * t)
                cols.append((0.035 + 0.025 * math.sin(t * math.pi * 3 + (0.6 if tie else 0)), yy, zz))
            rows.append(cols)
        rows.reverse(); b.sheet(rows, X['velvet'], 0.006, picture=False)
    # benches (walnut base + ikat seat pad + kilim back cushion), table with pedestal
    for y0, y1, yb0, yb1 in ((0.06, 0.58, 0.06, 0.2), (Wd - 0.58, Wd, Wd - 0.2, Wd)):
        b.box(0.08, y0, 0, 1.24, y1, 0.38, W, 0.003)
        b.box(0.1, y0 + 0.01, 0.38, 1.22, y1 - 0.01, 0.45, m['ikat'], 0.015)
        b.box(0.12, yb0 + (0.0 if yb0 < 1 else 0.0), 0.45, 1.2, yb1, 0.9, X['kilim'], 0.02)
    b.box(0.15, 0.65, 0.72, 1.15, 1.35, 0.76, m['oak'], 0.004)
    b.box(0.45, 0.8, 0, 0.85, 1.2, 0.025, m['bronze'], 0.003); b.box(0.61, 0.96, 0.025, 0.69, 1.04, 0.72, m['bronze'], 0.002)
    for px in (0.4, 0.9):
        for py in (0.82, 1.18): _plate(b, px, py, 0.76); _piala(b, px + 0.2, py, 0.76)
    _teapot(b, 0.65, 1.0, 0.76)
    return b.mesh(f'Booth_{theme}')

# ---------------------------------------------------------------- MAJLIS TENT (2.60 x 2.75)
@cached
def a_tent(w, d):
    """majlis tent shell; local x 0..w (open east side at x = w), y 0..d, z 0 = floor"""
    b = MB(); W = m['walnut']; zw, ap = 2.25, 2.95; p = 0.06
    for x0, y0 in ((-p, -p), (w, -p), (-p, d), (w, d)): b.box(x0, y0, 0, x0 + p, y0 + p, zw, W, 0.003)     # square poles outside the footprint
    b.box(-0.03, 0.0, 0, 0.0, d, zw, X['tent'])                                                     # walls between the poles, flush
    b.box(0.0, -0.03, 0, w, 0.0, zw, X['tent']); b.box(0.0, d, 0, w, d + 0.03, zw, X['tent'])
    # pyramid roof as one closed solid resting on poles and walls; finial on the apex
    base = [(-p, -p), (w + p, -p), (w + p, d + p), (-p, d + p)]
    vb = [b.bm.verts.new((x, y, zw)) for x, y in base]; va = b.bm.verts.new((w / 2, d / 2, ap)); i = b.mi(X['tent'])
    fs = [b.bm.faces.new(list(reversed(vb)))] + [b.bm.faces.new((vb[k], vb[(k + 1) % 4], va)) for k in range(4)]
    for f in fs: f.material_index = i
    bmesh.ops.recalc_face_normals(b.bm, faces=fs)
    b.lathe(w / 2, d / 2, ap, [(0.0, 0), (0.035, 0.02), (0.05, 0.08), (0.02, 0.16), (0.0, 0.24)], m['brass'], 12)
    # scalloped valance hanging from the roof edge (closed thin band)
    for k in range(4):
        (x0, y0), (x1, y1) = base[k], base[(k + 1) % 4]; L = math.hypot(x1 - x0, y1 - y0); n = max(4, int(L / 0.3)); top_, bot = [], []
        nx_, ny_ = (y1 - y0) / L, -(x1 - x0) / L
        for j in range(2 * n + 1):
            t = j / (2 * n); xx, yy = x0 + (x1 - x0) * t + nx_ * 0.004, y0 + (y1 - y0) * t + ny_ * 0.004
            top_.append((xx, yy, zw - 0.001)); bot.append((xx, yy, zw - (0.24 if j % 2 else 0.12)))
        b.sheet([bot, top_], X['velvet'], 0.006, picture=False)
    # tied-back front curtains on the open side
    for yy0, sg in ((0.02, 1), (d - 0.02, -1)):
        rows = []
        for zz, wdt, tie in ((zw - 0.01, 0.5, 0), (1.5, 0.22, 0), (1.0, 0.06, 1), (0.01, 0.24, 0)):
            rows.append([(w + 0.02 + 0.02 * math.sin(c / 6 * math.pi * 2), yy0 + sg * (wdt * c / 6 + (0.03 if tie else 0)), zz) for c in range(7)])
        rows.reverse(); b.sheet(rows, X['tent'], 0.006, picture=False)
    return b.mesh(f'Tent_{int(w * 100)}x{int(d * 100)}')

# ---------------------------------------------------------------- TAPCHAN RAILING (on the 2.0 x 2.2 deck)
@cached
def a_tapchan_rail(w, d):
    """balustrade on 3 sides (N, S, W) of a tapchan deck; local x 0..w, y 0..d, z 0 = deck top"""
    b = MB(); W = m['walnut']; h = 0.3
    for x0, y0, x1, y1 in ((0, 0, w, 0.05), (0, d - 0.05, w, d), (0, 0.05, 0.05, d - 0.05)):
        b.box(x0, y0, h, x1, y1, h + 0.04, W, 0.003)                      # hand rail
    for px, py in ((0.025, 0.025), (w - 0.025, 0.025), (0.025, d - 0.025), (w - 0.025, d - 0.025)):
        b.box(px - 0.025, py - 0.025, 0, px + 0.025, py + 0.025, h, W, 0.003)
        b.lathe(px, py, h + 0.04, [(0.0, 0), (0.025, 0), (0.03, 0.03), (0.012, 0.07), (0.0, 0.09)], m['brass'], 10)
    for t in [k / 10 for k in range(1, 10)]:
        for py in (0.025, d - 0.025): b.lathe(w * t, py, 0, [(0.0, 0), (0.016, 0), (0.016, 0.06), (0.022, 0.12), (0.014, 0.2), (0.016, h), (0.0, h)], W, 8)
    for t in [k / 11 for k in range(1, 11)]: b.lathe(0.025, d * t, 0, [(0.0, 0), (0.016, 0), (0.016, 0.06), (0.022, 0.12), (0.014, 0.2), (0.016, h), (0.0, h)], W, 8)
    return b.mesh('Tapchan_railing')

# ---------------------------------------------------------------- CERAMICS
@cached
def a_khum():
    b = MB(); b.lathe(0, 0, 0, [(0.0, 0), (0.12, 0), (0.24, 0.3), (0.22, 0.6), (0.1, 0.78), (0.13, 0.84), (0.0, 0.84)], m['clay'], 20); return b.mesh('Khum_jar')
@cached
def a_jar(kind):
    b = MB()
    if kind == 0: b.lathe(0, 0, 0, [(0.0, 0), (0.05, 0), (0.09, 0.12), (0.06, 0.26), (0.03, 0.3), (0.045, 0.34), (0.0, 0.34)], m['clay'], 16)
    else: b.lathe(0, 0, 0, [(0.0, 0), (0.04, 0), (0.07, 0.08), (0.05, 0.2), (0.025, 0.24), (0.0, 0.25)], m['turq'], 16)
    return b.mesh(f'Jar_{kind}')

# ---------------------------------------------------------------- CORRIDOR PARTS
@cached
def a_corr_arch(W_):
    """pointed velvet arch over the corridor (width W_ along Y), 80 mm thick; local y 0..W_, x 0..0.08"""
    b = MB()
    b.box(0, 0, 0, 0.08, 0.15, 2.75, m['walnut'], 0.003); b.box(0, W_ - 0.15, 0, 0.08, W_, 2.75, m['walnut'], 0.003)
    for poly in spandrel_polys(W_ / 2, W_ - 0.3, 2.0, 2.62, 2.75): b.extrude(poly, 0, 0.08, X['velvet'], 'yz')
    return b.mesh('Corridor_arch')
@cached
def a_niche():
    """museum niche cabinet 600 x 260 x 900, hung on the wall: local y 0 = wall face, grows to +y; origin = bottom centre"""
    b = MB(); W = m['walnut']
    b.box(-0.3, 0, 0, 0.3, 0.26, 0.05, W, 0.002); b.box(-0.3, 0, 0.85, 0.3, 0.26, 0.9, W, 0.002)
    b.box(-0.3, 0, 0.05, -0.26, 0.26, 0.85, W, 0.002); b.box(0.26, 0, 0.05, 0.3, 0.26, 0.85, W, 0.002)
    b.box(-0.26, 0, 0.05, 0.26, 0.02, 0.85, X['velvet']); b.box(-0.26, 0.02, 0.84, 0.26, 0.26, 0.85, X['lampglow'])
    b.box(-0.26, 0.02, 0.4, 0.26, 0.24, 0.415, m['glass'])
    b.box(-0.1, 0.26, 0.0, 0.1, 0.265, 0.06, m['brass'])
    return b.mesh('Corridor_niche')

# ---------------------------------------------------------------- BUKHARA DOME ROTUNDA (on the podium top, origin = centre)
@cached
def a_rotunda():
    """lattice drum r 0.45 on the podium (z 0 = podium top), 2 glass shelves with ceramics, copper cap, 4 posts + ring canopy
    (posts stand on the floor at z = -0.15)"""
    b = MB(); W = m['walnut']; H = 2.15
    for k in range(20):
        a = 2 * math.pi * k / 20; b.obox(0.45 * math.cos(a), 0.45 * math.sin(a), 0, H, 0.04, 0.03, a + math.pi / 2, W)
    for zz in (0.0, 0.75, 1.45, H - 0.06):
        b.ring(0, 0, zz, [(0.465, 0), (0.5, 0), (0.5, 0.05), (0.465, 0.05)], m['brass'], 40)
    for zz in (0.75, 1.45):
        b.cyl(0, 0, zz, zz + 0.015, 0.435, m['glass'], 32)
        for k in range(8):
            a = 2 * math.pi * k / 8 + 0.3; px, py = 0.3 * math.cos(a), 0.3 * math.sin(a)
            [_jar_k0, _jar_k1][k % 2](b, px, py, zz + 0.015)
    b.cyl(0, 0, H - 0.03, H, 0.43, X['lampglow'], 32)
    b.lathe(0, 0, H, [(0.0, 0), (0.55, 0), (0.52, 0.12), (0.4, 0.3), (0.2, 0.42), (0.05, 0.47), (0.05, 0.6), (0.0, 0.62)], X['copper'], 32)
    for k in range(4):                                                    # posts between the vitrines, outside the podium
        a = k * math.pi / 2; b.cyl(0.96 * math.cos(a), 0.96 * math.sin(a), -0.15, 2.2, 0.03, m['bronze'], 10)
    b.ring(0, 0, 2.2, [(0.85, 0), (1.05, 0), (1.05, 0.12), (0.85, 0.12)], m['brass'], 64)
    return b.mesh('Bukhara_rotunda')
def _jar_k0(b, x, y, z): b.lathe(x, y, z, [(0.0, 0), (0.04, 0), (0.065, 0.1), (0.04, 0.2), (0.025, 0.24), (0.0, 0.24)], m['clay'], 12)
def _jar_k1(b, x, y, z): b.lathe(x, y, z, [(0.0, 0), (0.035, 0), (0.06, 0.07), (0.045, 0.17), (0.02, 0.2), (0.0, 0.21)], m['turq'], 12)
@cached
def a_vitrine():
    """lit glass vitrine 300 x 300 on a walnut base; origin = bottom centre (on the podium top)"""
    b = MB(); h = 0.15
    b.box(-h, -h, 0, h, h, 0.4, m['walnut'], 0.003)
    b.box(-h + 0.025, -h + 0.025, 0.4, h - 0.025, h - 0.025, 0.9, m['glass'])
    for sx in (-1, 1):
        for sy in (-1, 1): b.box(sx * h - (0.025 if sx > 0 else 0), sy * h - (0.025 if sy > 0 else 0), 0.4, sx * h + (0 if sx > 0 else 0.025), sy * h + (0 if sy > 0 else 0.025), 0.9, m['brass'])
    b.box(-h, -h, 0.9, h, h, 0.93, m['brass'])
    b.box(-0.1, -0.1, 0.4, 0.1, 0.1, 0.41, X['lampglow'])
    b.lathe(0, 0, 0.41, [(0.0, 0), (0.06, 0), (0.1, 0.12), (0.06, 0.24), (0.02, 0.3), (0.0, 0.3)], m['majolica'], 16)
    return b.mesh('Vitrine')
@cached
def a_gate(L):
    """Khiva gate: 2 carved posts 250 x 250 (inner faces L apart), beam, jali panel under the beam, brass capitals, 7 bells;
    local x 0..L+0.5 (post 0..0.25, opening 0.25..L+0.25, post L+0.25..L+0.5), y -0.125..0.125, z 0 = floor"""
    b = MB(); W = m['walnut']
    for x0 in (0.0, L + 0.25):
        b.box(x0, -0.125, 0, x0 + 0.25, 0.125, 2.55, X['carved'], 0.004)
        b.lathe(x0 + 0.125, 0, 2.55, [(0.0, 0), (0.16, 0), (0.2, 0.15), (0.2, 0.3), (0.0, 0.3)], m['brass'], 16)
    b.box(-0.25, -0.075, 2.85, L + 0.75, 0.075, 3.25, W, 0.004)
    b.box(0.25, -0.045, 2.55, L + 0.25, 0.045, 2.85, m['jali'])
    for k in range(7):
        gx = 0.25 + L * (k + 1) / 8
        b.cyl(gx, 0, 2.43, 2.55, 0.004, m['brass'], 6)
        b.lathe(gx, 0, 2.28, [(0.0, 0), (0.06, 0), (0.05, 0.08), (0.02, 0.15), (0.0, 0.15)], m['brass'], 12)
    return b.mesh(f'Khiva_gate_{int(L * 100)}')
@cached
def a_flycarpet(k):
    """flying carpet 1.25 x 1.90 with a gentle wave, 12 mm thick; origin = centre"""
    b = MB(); w, l = 1.25, 1.9; rows = []
    for j in range(9):
        v = -l / 2 + l * j / 8
        rows.append([(-w / 2 + w * c / 4, v, 0.05 * math.sin(v / l * 2 * math.pi)) for c in range(5)])
    b.sheet(rows, X['carpet%d' % k], 0.012, picture=True)
    return b.mesh(f'Flying_carpet_{k}')
