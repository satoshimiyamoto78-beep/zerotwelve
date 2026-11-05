"""rev. 8.5 — AIVAN fabrication-grade detailing (owner: "the arch looks crooked, the rails are rectangles with a picture, the
tiles are fake"). Everything here is real geometry that a joiner / tiler can build from:
  * columns: plinth + pedestal with raised fielded panels and star rosettes, turned base, 16-flute shaft, turned rings, capital, abacus
  * arch heads: opening drawn from true circular arcs (Uzbek multifoil with a cusped spring hook), spandrel board = rectangle minus
    the opening, raised moulded frame = clean 50 mm offset of the opening, 8-point star rosettes in the spandrels
  * frieze: honey timber with real star rosettes and bead mouldings, scalloped drop edge, stepped cornice
  * bays: jali bays = frame + raised lower panel + real pierced star jali; planter bays = panelled timber planter + glazed pots + shrubs
  * aivan edge rails: handrail + turned balusters (ramp: posts + sloped handrail)
  * sedir booths: timber carcass with fielded front panels, kurpacha seat, carved back rail, bolsters; tables with turned fluted legs,
    arched aprons and a REAL tile field (100 mm glazed tiles, 3 mm grout) ; booth screens rebuilt in the same joinery
  * ceiling: timber beams @ 0.6 m + boards (vassa-style) over the aivan, wall plate on the facade; lanterns hang from the boards
Units m; aivan deck ±0.000; arcade axis XA."""
import shapely
from shapely.geometry import Polygon as SPoly, Point as SPt, box as SBox
from shapely.ops import unary_union as SUnion, polylabel
XA = 3.18; ZB = 3.02; ZC = ZB - 0.24
COLY = [15.45, 18.17] + [18.17 + (24.18 - 18.17) * k / 5 for k in range(1, 5)] + [24.18, 25.92, 27.13, 28.34]
OPEN = ((15.45, 18.17), (24.18, 25.92))
HZ = bl2.wood('aivan_honey_z', (0.70, 0.46, 0.24), (0.44, 0.26, 0.12), rough=0.5, scale=1.3, along='Z')
HY = bl2.wood('aivan_honey_y', (0.70, 0.46, 0.24), (0.44, 0.26, 0.12), rough=0.5, scale=1.3, along='Y')
HX = bl2.wood('aivan_honey_x', (0.70, 0.46, 0.24), (0.44, 0.26, 0.12), rough=0.5, scale=1.3, along='X')
HD = bl2.wood('aivan_dark_y', (0.40, 0.24, 0.12), (0.22, 0.12, 0.06), rough=0.45, scale=1.3, along='Y')
GL = dict(cob=mat('glaze_cobalt', (0.035, 0.09, 0.42), rough=0.12), wht=mat('glaze_white', (0.90, 0.88, 0.80), rough=0.12),
          trq=mat('glaze_turq', (0.06, 0.48, 0.52), rough=0.12), och=mat('glaze_ochre', (0.72, 0.46, 0.12), rough=0.15),
          iron=mat('wrought_iron', (0.025, 0.025, 0.025), rough=0.45, metal=0.7),
          grt=mat('tile_grout', (0.62, 0.58, 0.52), rough=0.9), clay=mat('pot_clay', (0.55, 0.28, 0.15), rough=0.8))
_rm('Khiva_column', 'Khiva_arcade_head', 'Khiva_arcade_beam', 'Khiva_arcade_bay', 'Aivan_fascia', 'aivan_rail_jali', 'Aivan_shrub_foliage',
    'Aivan_screen', 'Aivan_banquette', 'Aivan_table_', 'Aivan_lantern')
for o_ in [o for o in bpy.data.objects if o.name.startswith('Rod') and 0.0 < o.location.x < 3.3 and 15.0 < o.location.y < 29.0]: bpy.data.objects.remove(o_)
for o_ in [o for o in bpy.data.objects if o.name.startswith('Ceiling_carpet')]:
    lo_, hi_ = _bb(o_)
    if hi_[0] < 3.4 and lo_[1] > 15.0 and hi_[1] < 29.5: bpy.data.objects.remove(o_)

def star8(cx, cy, r, rot=0.0):
    """8-point star (two squares) as a shapely polygon"""
    pts = []
    for k in range(16):
        a = rot + math.pi * k / 8; rr = r if k % 2 == 0 else r * 0.62
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return SPoly(pts)
def lattice(u0, v0, u1, v1, pitch, bar):
    """owner: keep patterns simple to make — plain diagonal lattice of slats at +-45 deg (a joiner's halving-joint grid)"""
    r = SBox(u0, v0, u1, v1); W, H = u1 - u0, v1 - v0; ls = []
    k = -int(H / pitch) - 2
    while k * pitch < W + H:
        a0 = u0 + k * pitch
        ls.append(shapely.geometry.LineString([(a0, v0), (a0 + H, v1)])); ls.append(shapely.geometry.LineString([(a0 + H, v0), (a0, v1)]))
        k += 1
    return SUnion([l.buffer(bar / 2, cap_style=2) for l in ls]).intersection(r)
def put(b, g, a0, a1, mm, plane):
    """extrude any shapely (multi)polygon, holes allowed"""
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty or p.area < 1e-6: continue
        p = p.buffer(0)
        for q in getattr(p, 'geoms', [p]):
            if q.area > 1e-6: ext_holes(b, shapely.geometry.polygon.orient(q), a0, a1, mm, plane)
def fielded(b, u0, v0, u1, v1, w0, w1, mm, plane, star=True):
    """raised fielded panel on a face: flat field (w0..w1) + 2-step raised centre + optional star rosette"""
    put(b, SBox(u0, v0, u1, v1), w0, w1, mm, plane)
    d = (w1 - w0)
    sg = 1 if w1 > w0 else -1
    put(b, SBox(u0 + 0.025, v0 + 0.025, u1 - 0.025, v1 - 0.025), w1, w1 + sg * 0.008, mm, plane)
    put(b, SBox(u0 + 0.045, v0 + 0.045, u1 - 0.045, v1 - 0.045), w1 + sg * 0.008, w1 + sg * 0.014, mm, plane)
    if star and min(u1 - u0, v1 - v0) > 0.12:
        r = 0.32 * min(u1 - u0, v1 - v0); c = ((u0 + u1) / 2, (v0 + v1) / 2)
        put(b, star8(c[0], c[1], r, math.pi / 8), w1 + sg * 0.014, w1 + sg * 0.022, GL['och'] if False else mm, plane)

# ---------------------------------------------------------------- COLUMN
@cached
def a_col85(H):
    b = MB()
    b.box(-0.118, -0.118, 0.0, 0.118, 0.118, 0.06, HZ, 0.006)
    b.box(-0.095, -0.095, 0.06, 0.095, 0.095, 0.56, HZ)                                      # core
    for sg, pl in ((1, 'x'), (-1, 'x'), (1, 'y'), (-1, 'y')):                                 # fielded panel on each face
        if pl == 'x': fielded(b, -0.095, 0.08, 0.095, 0.54, sg * 0.095, sg * 0.105, HZ, 'yz')
        else: fielded(b, -0.095, 0.08, 0.095, 0.54, sg * 0.095, sg * 0.105, HZ, 'xz')
    b.box(-0.118, -0.118, 0.56, 0.118, 0.118, 0.595, HZ, 0.006); b.box(-0.11, -0.11, 0.595, 0.11, 0.11, 0.62, HZ, 0.004)
    b.lathe(0, 0, 0.62, [(0.0, 0.0), (0.105, 0.0), (0.105, 0.03), (0.092, 0.05), (0.1, 0.08), (0.088, 0.12), (0.085, 0.16), (0.0, 0.16)], HZ, 32)
    z0, z1 = 0.78, H - 0.42
    fl = [((0.08 - 0.009 * abs(math.sin(8 * a))) * math.cos(a), (0.08 - 0.009 * abs(math.sin(8 * a))) * math.sin(a)) for a in [2 * math.pi * k / 128 for k in range(128)]]
    b.extrude(fl, z0, z1, HZ, 'xy')
    for zr in (z0 + 0.04, z0 + (z1 - z0) * 0.62, z1 - 0.05):
        b.lathe(0, 0, zr - 0.03, [(0.0, 0.0), (0.082, 0.0), (0.095, 0.012), (0.098, 0.03), (0.095, 0.048), (0.082, 0.06), (0.0, 0.06)], HZ, 32)
    b.lathe(0, 0, z1, [(0.0, 0.0), (0.085, 0.0), (0.098, 0.03), (0.09, 0.07), (0.104, 0.12), (0.118, 0.19), (0.104, 0.245), (0.122, 0.27), (0.122, 0.3), (0.0, 0.3)], HZ, 32)
    b.box(-0.12, -0.12, H - 0.12, 0.12, 0.12, H - 0.06, HZ, 0.004); b.box(-0.15, -0.15, H - 0.06, 0.15, 0.15, H, HZ, 0.006)
    return b.mesh(f'Aivan85_column_{int(H * 100)}')

# ---------------------------------------------------------------- ARCH HEAD
def _arc(p, q, sag, n=10):
    """circular arc p->q bulging by `sag` to the LEFT of p->q (negative = right)"""
    (x0, y0), (x1, y1) = p, q; mx, my = (x0 + x1) / 2, (y0 + y1) / 2; dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    if abs(sag) < 1e-6: return [p, q]
    R = (L * L / 4 + sag * sag) / (2 * abs(sag)); cxx, cyy = mx - nx * (R - abs(sag)) * (1 if sag > 0 else -1), my - ny * (R - abs(sag)) * (1 if sag > 0 else -1)
    a0, a1 = math.atan2(y0 - cyy, x0 - cxx), math.atan2(y1 - cyy, x1 - cxx)
    da = a1 - a0
    while da > math.pi: da -= 2 * math.pi
    while da < -math.pi: da += 2 * math.pi
    return [(cxx + R * math.cos(a0 + da * k / n), cyy + R * math.sin(a0 + da * k / n)) for k in range(n + 1)]
def opening85(c, w, zs, za):
    """Uzbek multifoil arch, left half drawn from arcs: spring hook (bulging into the opening) + 3 lobes on a pointed curve"""
    base = arch_left(c, w, zs + 0.12, za, 60); s = (c - w / 2, zs)
    k1 = (c - w / 2 + 0.05, zs + 0.12)
    pts = _arc(s, k1, -0.035, 8)                                               # hook: bulges into the opening
    cusps = [base[0], base[18], base[38], base[60]]
    cusps[0] = k1
    for a, q in zip(cusps[:-1], cusps[1:]):
        L = math.hypot(q[0] - a[0], q[1] - a[1]); pts += _arc(a, q, 0.17 * L, 12)[1:]
    left = pts; right = [(2 * c - u, z) for u, z in reversed(left)][1:]
    return SPoly([(c - w / 2, zs - 1.0)] + left + right + [(c + w / 2, zs - 1.0)]).buffer(0)
@cached
def a_head85(L, open_):
    b = MB(); y0, y1 = 0.15, L - 0.15; c = L / 2; w = L - 0.36
    zs = -(0.80 if not open_ else 0.78); za = -0.11
    rect = SBox(y0, zs, y1, 0.0); op = opening85(c, w, zs, za)
    span = rect.difference(op)
    put(b, span, -0.035, 0.035, HY, 'yz')
    frame = op.buffer(0.05, join_style=1).difference(op).intersection(rect)
    put(b, frame, -0.05, 0.05, HD, 'yz')
    bead = rect.exterior.buffer(0.012).intersection(rect.buffer(-0.001)).difference(op.buffer(0.05))
    put(b, bead, -0.042, 0.042, HD, 'yz')
    for part in getattr(span.difference(op.buffer(0.07)), 'geoms', [span.difference(op.buffer(0.07))]):
        if part.area < 0.004: continue
        pc = polylabel(part, 0.002); r = min(0.09, part.exterior.distance(pc) * 0.8)       # largest circle inside the spandrel
        if r < 0.025: continue
        ros = star8(pc.x, pc.y, r, math.pi / 8).union(SPt(pc.x, pc.y).buffer(r * 0.32, 16)).difference(SPt(pc.x, pc.y).buffer(r * 0.18, 16))
        put(b, ros, -0.047, 0.047, HD, 'yz')
    if not open_: _pierced(b, 0, c, za - 0.03, 0.7)
    return b.mesh(f'Aivan85_head_{int(L * 1000)}_{int(open_)}')

# ---------------------------------------------------------------- BAYS
@cached
def a_bay85(L, kind):
    """bay between column centres (local y 0..L; x -0.1..0.1). 'jali': frame + raised lower panel + pierced jali + lamp strip;
    'plant': panelled planter (h 0.55) with three glazed pots"""
    b = MB(); y0, y1 = 0.13, L - 0.13
    if kind == 'iron':                                   # owner ref: low panelled base + plain wrought-iron grille (bars + rings), h 1.0
        b.box(-0.07, y0, 0.0, 0.07, y1, 0.06, HY, 0.004)
        b.box(-0.055, y0, 0.06, 0.055, y1, 0.42, HY)
        for sg in (-1, 1): fielded(b, y0 + 0.02, 0.09, y1 - 0.02, 0.39, sg * 0.055, sg * 0.062, HY, 'yz', star=False)
        b.box(-0.07, y0, 0.42, 0.07, y1, 0.46, HY, 0.006)
        I = GL['iron']; zt = 1.0
        b.box(-0.01, y0 + 0.02, 0.46, 0.01, y0 + 0.05, zt, I); b.box(-0.01, y1 - 0.05, 0.46, 0.01, y1 - 0.02, zt, I)
        for za_ in (0.48, zt - 0.03): b.box(-0.012, y0 + 0.02, za_, 0.012, y1 - 0.02, za_ + 0.03, I)
        b.box(-0.02, y0 + 0.02, zt, 0.02, y1 - 0.02, zt + 0.03, HY, 0.006)                    # timber handrail on the grille
        nbar = max(2, int((y1 - y0 - 0.07) / 0.11))
        for k in range(nbar):
            yy = y0 + 0.05 + (k + 0.5) * (y1 - y0 - 0.1) / nbar
            b.rod((0, yy, 0.51), (0, yy, zt - 0.03), 0.007, I, 8)
            if k % 2 == 0: b.ring(0, yy, 0.73, [(0.045, -0.006), (0.055, -0.006), (0.055, 0.006), (0.045, 0.006)], I, 24) if False else None
        for k in range(0, nbar - 1, 2):                                                       # one ring between every other pair of bars
            yy = y0 + 0.05 + (k + 1.0) * (y1 - y0 - 0.1) / nbar; rr = 0.5 * (y1 - y0 - 0.1) / nbar
            ring = SPt(yy, 0.74).buffer(rr, 24).difference(SPt(yy, 0.74).buffer(rr - 0.01, 24))
            put(b, ring, -0.006, 0.006, I, 'yz')
    else:
        b.box(-0.12, y0, 0.0, 0.12, y1, 0.06, HY, 0.004)
        b.box(-0.105, y0, 0.06, 0.105, y1, 0.5, HY)
        n = max(1, round((y1 - y0) / 0.45))
        for sg in (-1, 1):
            for k in range(n):
                a_ = y0 + 0.03 + k * (y1 - y0 - 0.06) / n; b_ = a_ + (y1 - y0 - 0.06) / n
                fielded(b, a_ + 0.015, 0.09, b_ - 0.015, 0.47, sg * 0.105, sg * 0.112, HY, 'yz')
        b.box(-0.125, y0 - 0.0, 0.5, 0.125, y1, 0.545, HY, 0.006)
        npot = 3 if (y1 - y0) > 0.95 else 2
        for k in range(npot):
            cy = y0 + (k + 0.5) * (y1 - y0) / npot
            b.lathe(0, cy, 0.545, [(0.0, 0.0), (0.075, 0.0), (0.082, 0.02), (0.11, 0.09), (0.118, 0.15), (0.108, 0.22), (0.098, 0.25), (0.112, 0.265), (0.112, 0.285), (0.0, 0.285)], GL['cob'], 32)
            b.lathe(0, cy, 0.545 + 0.13, [(0.0, 0.0), (0.1185, 0.0), (0.1185, 0.04), (0.0, 0.04)], GL['wht'], 32)          # painted band
            b.lathe(0, cy, 0.545 + 0.27, [(0.0, 0.0), (0.098, 0.0), (0.098, 0.012), (0.0, 0.012)], m['soil'] if 'soil' in m else GL['clay'], 24)
    return b.mesh(f'Aivan85_bay_{int(L * 1000)}_{kind}')

# ---------------------------------------------------------------- BALUSTRADE
@cached
def a_balustrade(L):
    """straight balustrade along local +x, 0..L: bottom rail, turned balusters @ 120, moulded handrail, newel posts; h 0.95"""
    b = MB(); h = 0.95
    for xx in (0.0, L):
        x0 = min(max(xx - 0.03, 0.0), L - 0.06)
        b.box(x0, -0.03, 0.0, x0 + 0.06, 0.03, h + 0.04, HZ, 0.005)
        b.lathe(x0 + 0.03, 0.0, h + 0.04, [(0.0, 0.0), (0.026, 0.0), (0.03, 0.025), (0.015, 0.05), (0.0, 0.06)], HZ, 16)
    b.box(0.06, -0.025, 0.0, L - 0.06, 0.025, 0.07, HX, 0.004)
    b.box(0.06, -0.03, h - 0.05, L - 0.06, 0.03, h, HX, 0.008); b.box(0.06, -0.02, h, L - 0.06, 0.02, h + 0.02, HX, 0.006)
    n = max(1, int((L - 0.12) / 0.12))
    for k in range(n):
        x = 0.06 + (k + 0.5) * (L - 0.12) / n
        b.lathe(x, 0.0, 0.07, [(0.0, 0.0), (0.02, 0.0), (0.02, 0.03), (0.016, 0.06), (0.024, 0.2), (0.014, 0.4), (0.02, 0.5), (0.014, 0.62), (0.02, 0.78), (0.02, h - 0.12), (0.0, h - 0.12)], HZ, 12)
    return b.mesh(f'Balustrade_{int(L * 1000)}')

# ---------------------------------------------------------------- SEDIR + TABLE + SCREEN
@cached
def a_sedir(L, Dp, col):
    """Uzbek sedir banquette L (local x) x Dp (local y), back at y = 0, sitter faces +y (origin back-left floor corner):
    recessed plinth, front face of fielded panels, seat deck +0.38, kurpacha 100, carved back rail on posts, bolsters"""
    b = MB(); V = X['velvet_' + col]; zd = 0.38
    b.box(0.02, 0.02, 0.0, L - 0.02, Dp - 0.04, 0.06, HD)                                       # recessed plinth
    b.box(0.0, 0.0, 0.06, L, Dp, zd, HX)
    n = max(1, round(L / 0.5))
    for k in range(n):
        a_ = 0.03 + k * (L - 0.06) / n; b_ = a_ + (L - 0.06) / n
        fielded(b, a_ + 0.015, 0.09, b_ - 0.015, zd - 0.03, Dp, Dp + 0.008, HX, 'xz', star=True)
    b.box(0.0, 0.0, zd, L, Dp + 0.012, zd + 0.03, HX, 0.006)                         # seat deck with nosing
    b.box(0.03, 0.06, zd + 0.03, L - 0.03, Dp - 0.02, zd + 0.13, V, 0.03)                       # kurpacha
    for xx in (0.0, L - 0.06): b.box(xx, 0.0, zd + 0.03, xx + 0.06, 0.06, 0.98, HZ, 0.005)     # back posts
    b.box(0.0, 0.0, 0.9, L, 0.06, 0.98, HX, 0.006); b.box(0.0, 0.0, zd + 0.03, L, 0.03, 0.9, HX)
    nb = max(1, round((L - 0.12) / 0.32))
    for k in range(nb):                                                                       # carved back: arched cut-outs
        a_ = 0.06 + k * (L - 0.12) / nb; b_ = a_ + (L - 0.12) / nb; cc = (a_ + b_) / 2
        rect = SBox(a_, zd + 0.13, b_, 0.9); op = opening85(cc, (b_ - a_) - 0.06, zd + 0.30, 0.84)
        put(b, rect.difference(op), 0.03, 0.05, HX, 'xz')
    for k in range(nb):                                                                       # back cushions / bolster
        a_ = 0.06 + k * (L - 0.12) / nb; b_ = a_ + (L - 0.12) / nb
        b.box(a_ + 0.02, 0.05, zd + 0.13, b_ - 0.02, 0.17, zd + 0.48, X['kilim2'] if 'kilim2' in X else V, 0.04)
    return b.mesh(f'Sedir_{int(L * 1000)}x{int(Dp * 1000)}_{col}')

TILE_PAT = ['cob', 'wht', 'trq', 'wht', 'cob', 'wht', 'och', 'wht']
@cached
def a_tiletable85(Lx, Ly):
    """table Lx x Ly x 0.76: frame 70, field of real glazed tiles 100 x 100 (3 mm grout), arched aprons, fluted turned legs, stretchers"""
    b = MB(); hx, hy, f = Lx / 2, Ly / 2, 0.07
    for x0, y0, x1, y1 in ((-hx, -hy, hx, -hy + f), (-hx, hy - f, hx, hy), (-hx, -hy + f, -hx + f, hy - f), (hx - f, -hy + f, hx, hy - f)):
        b.box(x0, y0, 0.715, x1, y1, 0.76, HX if abs(x1 - x0) > abs(y1 - y0) else HY, 0.006)
    b.box(-hx + f, -hy + f, 0.715, hx - f, hy - f, 0.751, GL['grt'])
    ix0, iy0, ix1, iy1 = -hx + f + 0.004, -hy + f + 0.004, hx - f - 0.004, hy - f - 0.004
    nx, ny = max(1, round((ix1 - ix0) / 0.1)), max(1, round((iy1 - iy0) / 0.1)); tx, ty = (ix1 - ix0) / nx, (iy1 - iy0) / ny
    for i in range(nx):
        for j in range(ny):
            k = (abs(i - nx // 2) + abs(j - ny // 2)) % len(TILE_PAT)
            b.box(ix0 + i * tx + 0.0015, iy0 + j * ty + 0.0015, 0.751, ix0 + (i + 1) * tx - 0.0015, iy0 + (j + 1) * ty - 0.0015, 0.76, GL[TILE_PAT[k]], 0.0015)
    a = 0.05
    for sy in (-1, 1):                                                                        # long aprons with arched cut-outs
        for p in arch_apron(-hx + a + 0.07, 0.6, hx - a - 0.07, 0.715, 0.66, 0.7): put(b, p, sy * (hy - a - 0.02), sy * (hy - a), HX, 'xz')
    for sx in (-1, 1):
        for p in arch_apron(-hy + a + 0.07, 0.6, hy - a - 0.07, 0.715, 0.66, 0.7): put(b, p, sx * (hx - a - 0.02), sx * (hx - a), HY, 'yz')
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (hx - a - 0.035), sy * (hy - a - 0.035)
            b.box(cx - 0.035, cy - 0.035, 0.6, cx + 0.035, cy + 0.035, 0.715, HZ)
            fl = [(cx + (0.03 - 0.004 * abs(math.sin(6 * t))) * math.cos(t), cy + (0.03 - 0.004 * abs(math.sin(6 * t))) * math.sin(t)) for t in [2 * math.pi * q / 72 for q in range(72)]]
            b.extrude(fl, 0.16, 0.6, HZ, 'xy')
            b.lathe(cx, cy, 0.0, [(0.0, 0.0), (0.03, 0.0), (0.036, 0.03), (0.026, 0.07), (0.04, 0.12), (0.036, 0.16), (0.0, 0.16)], HZ, 24)
    b.box(-hx + a + 0.035, -0.02, 0.12, hx - a - 0.035, 0.02, 0.16, HX, 0.004)                      # H-stretcher
    for sx in (-1, 1): b.box(sx * (hx - a - 0.035) - 0.02, -hy + a + 0.035, 0.12, sx * (hx - a - 0.035) + 0.02, hy - a - 0.035, 0.16, HY, 0.004)
    return b.mesh(f'Tiletable85_{int(Lx * 1000)}x{int(Ly * 1000)}')

@cached
def a_screen85(L, H, ad=False):
    """booth screen in the x-z plane (local x 0..L, y 0..0.06, z 0..H): stiles + rails, raised lower panel, pierced jali, brass cap"""
    b = MB(); F = 0.07
    b.box(0, 0, 0, F, 0.06, H, HZ, 0.004); b.box(L - F, 0, 0, L, 0.06, H, HZ, 0.004)
    for z0_, z1_ in ((0.0, 0.1), (0.42, 0.48), (H - 0.07, H)): b.box(F, 0, z0_, L - F, 0.06, z1_, HX, 0.004)
    for w0_, w1_ in ((0.016, 0.046), (0.044, 0.014)): fielded(b, F, 0.1, L - F, 0.42, w0_, w1_, HX, 'xz', star=False)     # raised fields stay inside the 60 frame
    if ad: b.box(F, 0.01, 0.48, L - F, 0.05, H - 0.07, HX)
    else:
        put(b, lattice(F, 0.48, L - F, H - 0.07, 0.14, 0.03), 0.018, 0.042, HX, 'xz')
        b.box(F, 0.018, 0.48, L - F, 0.042, H - 0.07, HX) if False else None
    b.box(-0.01, -0.01, H, L + 0.01, 0.07, H + 0.025, m['brass'], 0.003)
    if ad:
        cx, w, h, z0 = L / 2, 1.45, 0.82, 0.2
        b.box(cx - w / 2 - 0.012, -0.03, z0 - 0.012, cx + w / 2 + 0.012, 0.01, z0 + h + 0.012, X82['black'], 0.004)
        b.picture_box(cx - w / 2, -0.032, z0, cx + w / 2, -0.03, z0 + h, X82['screen'], '-y')
    return b.mesh(f'Aivan85_screen_{int(L * 1000)}{"_ad" if ad else ""}')

# ================================================================ PLACE
for i_, y in enumerate(COLY): inst(a_col85(ZC), f'Khiva_column_{i_ + 1:02d}', (XA, y, 0.0), 0, 'Aivan')
nb_ = 0; PLANT_BAYS = []
for i_, (ya, yb) in enumerate(zip(COLY[:-1], COLY[1:])):
    L = round(yb - ya, 4); op_ = (ya, yb) in OPEN
    inst(a_head85(L, op_), f'Khiva_arcade_head_{i_ + 1:02d}', (XA, ya, ZC), 0, 'Aivan')
    if not op_:
        nb_ += 1; kind = 'iron' if nb_ % 2 else 'plant'
        inst(a_bay85(L, kind), f'Khiva_arcade_bay_{i_ + 1:02d}', (XA, ya, 0.0), 0, 'Aivan')
        if kind == 'plant': PLANT_BAYS.append((ya, L))
ns_ = 0
for ya, L in PLANT_BAYS:                                                    # shrubs in the glazed pots
    y0, y1 = ya + 0.13, ya + L - 0.13; npot = 3 if (y1 - y0) > 0.95 else 2
    for k in range(npot):
        ns_ += 1; inst(a_shrub(60 + ns_, ('bou', 'jas', 'green')[ns_ % 3]), f'Aivan_shrub_foliage_{ns_}', (XA, y0 + (k + 0.5) * (y1 - y0) / npot, 0.545 + 0.27 + 0.012), 0.9 * ns_, 'Planting')

# frieze beam: honey core, real rosettes + bead mouldings both faces, scalloped drop edge, stepped cornice
mb = MB(); y0_, y1_ = COLY[0] - 0.15, COLY[-1] + 0.15
mb.box(XA - 0.13, y0_, ZC, XA + 0.13, y1_, ZB - 0.06, HY, 0.004)
for sx in (-1, 1):
    for zz in (ZC + 0.025, ZB - 0.095): mb.box(XA + sx * 0.13, y0_, zz, XA + sx * 0.142, y1_, zz + 0.018, HD, 0.003)
    yy = y0_ + 0.2
    while yy < y1_ - 0.15:
        put(mb, star8(yy, (ZC + ZB - 0.06) / 2, 0.05, math.pi / 8).union(SPt(yy, (ZC + ZB - 0.06) / 2).buffer(0.018, 12)), XA + sx * 0.13, XA + sx * 0.142, HD, 'yz')
        yy += 0.3
mb.box(XA - 0.17, y0_ - 0.04, ZB - 0.06, XA + 0.17, y1_ + 0.04, ZB - 0.03, HY, 0.004)
mb.box(XA - 0.21, y0_ - 0.08, ZB - 0.03, XA + 0.21, y1_ + 0.08, ZB, HY, 0.004)
yy = y0_ + 0.05
while yy + 0.04 < y1_:
    if not any(abs(yy - cy_) < 0.2 for cy_ in COLY):
        semi = [(yy + 0.035 * math.cos(math.pi * k / 12), ZC - 0.035 * math.sin(math.pi * k / 12)) for k in range(13)]
        for sx in (-1, 1): mb.extrude(semi, XA + sx * 0.13, XA + sx * 0.11, HD, 'yz')
    yy += 0.09
inst(mb.mesh('Khiva_arcade_beam'), 'Khiva_arcade_beam', (0, 0, 0), 0, 'Aivan')

# deck-edge fascia (terrace side) with fielded panels
mb = MB()
for a_, b_ in ((15.3, 15.55), (18.05, 24.3), (25.8, 28.5)):
    mb.box(3.30, a_, TER, 3.318, b_, -0.0, HY)
    n = max(1, round((b_ - a_) / 0.6))
    for k in range(n):
        u0 = a_ + k * (b_ - a_) / n; u1 = u0 + (b_ - a_) / n
        if u1 - u0 > 0.15: fielded(mb, u0 + 0.02, TER + 0.05, u1 - 0.02, -0.05, 3.318, 3.326, HY, 'yz', star=False)
inst(mb.mesh('Aivan_fascia'), 'Aivan_fascia', (0, 0, 0), 0, 'Aivan')

DONE_ENDS = set()
# aivan edge rails: balustrades on the deck edges (not the arcade line), ramp rail = posts + sloped handrail
for k_, ((x0, y0), (x1, y1)) in enumerate(D['rail']):
    if abs(x0 - 3.3) < 1e-3 and abs(x1 - 3.3) < 1e-3: continue
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 0.3: continue
    if abs(x0 - 1.3) < 1e-3 and abs(x1 - 1.3) < 1e-3 and min(y0, y1) > 30.0:              # ramp 1:12 down to the terrace
        mb = MB(); ya_, yb_ = min(y0, y1), max(y0, y1)
        from mathutils.bvhtree import BVHTree as _BVH
        _ro = bpy.data.objects.get('ramp_1_12'); _mw = _ro.matrix_world; _bv = _BVH.FromPolygons([_mw @ v.co for v in _ro.data.vertices], [list(p_.vertices) for p_ in _ro.data.polygons])
        def zr(x, y):                                     # ramp surface (it has a level landing at the lift)
            h_ = _bv.ray_cast(Vector((x, y, 2.0)), Vector((0, 0, -1)), 5.0); return h_[0].z if h_[0] is not None else -0.45
        def zpost(y): return max(zr(x0 - 0.075 + dx, y + dy) for dx in (0.0, 0.07) for dy in (-0.035, 0.035)) + 0.001
        zf = lambda y: zpost(ya_ + 0.04) + (zpost(yb_ - 0.04) - zpost(ya_ + 0.04)) * (y - ya_ - 0.04) / (yb_ - ya_ - 0.08)
        n = max(2, int((yb_ - ya_) / 1.2) + 1)
        for q in range(n):
            y = ya_ + q * (yb_ - ya_) / (n - 1); y = min(max(y, ya_ + 0.04), yb_ - 0.04)
            mb.box(x0 - 0.075, y - 0.035, zpost(y), x0 - 0.005, y + 0.035, zf(y) + 0.95, HZ, 0.004)
        rows = [[(x0 - 0.03, y, zf(y) + 0.95), (x0 + 0.03, y, zf(y) + 0.95)] for y in (ya_, yb_)]
        hb = bmesh.new(); vs = []
        for (yy_,) in ((ya_,), (yb_,)):
            for dx_, dz_ in ((-0.07, 0.95), (-0.01, 0.95), (-0.01, 1.0), (-0.07, 1.0)): vs.append(hb.verts.new((x0 + dx_, yy_, zf(yy_) + dz_)))
        a4, b4 = vs[:4], vs[4:]
        hb.faces.new(list(reversed(a4))); hb.faces.new(b4)
        for i in range(4): hb.faces.new((a4[i], a4[(i + 1) % 4], b4[(i + 1) % 4], b4[i]))
        bmesh.ops.recalc_face_normals(hb, faces=hb.faces)
        me_ = mb.mesh(f'Aivan_ramp_handrail_posts'); inst(me_, 'Aivan_ramp_handrail_posts', (0, 0, 0), 0, 'Aivan')
        hm = bpy.data.meshes.new('Aivan_ramp_handrail'); hb.to_mesh(hm); hb.free(); hm.materials.append(HY)
        ho = bpy.data.objects.new('Aivan_ramp_handrail', hm); coll('Aivan').objects.link(ho)
        continue
    ang = math.atan2(y1 - y0, x1 - x0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    for e_ in list(DONE_ENDS):
        if math.hypot(e_[0] - x0, e_[1] - y0) < 1e-3: x0, y0, L = x0 + ux * 0.065, y0 + uy * 0.065, L - 0.065
        elif math.hypot(e_[0] - x1, e_[1] - y1) < 1e-3: L -= 0.065
    DONE_ENDS.update({(round(x0 - ux * 0.0, 4), round(y0, 4)), (round(x1, 4), round(y1, 4))}); DONE_ENDS.update({(round(x1, 4), round(y1, 4))})
    inst(a_balustrade(round(L, 3)), f'Aivan_balustrade_{k_ + 1}', (x0, y0, 0.0), ang, 'Aivan')

# booth screens (same joinery), sedir banquettes, tile tables, lanterns from the new ceiling
asc_ = sorted([bbox(it['poly'][0]) for it in D['items'] if it['kind'] == 'ascreen'], key=lambda b_: b_[1])
for i_, (x0, y0, x1, y1) in enumerate(asc_): inst(a_screen85(round(x1 - x0, 3), 1.2, i_ == 0), f'Aivan_screen_{i_ + 1}', (x0, y0, 0.0), 0, 'Aivan')
scr = asc_; ats = [bbox(it['poly'][0]) for it in D['items'] if it['kind'] == 'atable']
for i_, it in enumerate([it for it in D['items'] if it['kind'] == 'abench']):
    x0, y0, x1, y1 = bbox(it['poly'][0]); cy = (y0 + y1) / 2
    tb = min(ats, key=lambda b_: abs((b_[1] + b_[3]) / 2 - cy)); away = -1 if (tb[1] + tb[3]) / 2 > cy else 1
    yo = y0 if away < 0 else y1
    for sx0, sy0, sx1, sy1 in scr:
        if sx0 < x1 and sx1 > x0 and sy0 - 1e-6 <= yo <= sy1 + 1e-6: yo = sy1 if away < 0 else sy0
    yf = y1 if away < 0 else y0; bx0 = 0.16; Lb = round(x1 - bx0, 3); Db = round(abs(yf - yo), 3)
    if away < 0: inst(a_sedir(Lb, Db, 'navy'), f'Aivan_banquette_{i_ + 1}', (bx0, yo, 0.0), 0.0, 'Aivan')
    else: inst(a_sedir(Lb, Db, 'navy'), f'Aivan_banquette_{i_ + 1}', (x1, yo, 0.0), math.pi, 'Aivan')
for i_, (x0, y0, x1, y1) in enumerate(ats):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    inst(a_tiletable85(round(x1 - x0, 3), round(y1 - y0, 3)), f'Aivan_table_{i_ + 1}', (cx, cy, 0.0), 0.0, 'Aivan')

# CEILING over the aivan — coffered timber ceiling after Cafe De Bobo (Dushanbe, owner ref.): primary beams on the booth
# rhythm, each coffer = timber frame + warm LED cove + kilim panel recessed 80 mm + diagonal X ribs; wall plate on the facade
CY0, CY1, CX0, CX1, ZT = 15.3, 28.49, 0.22, XA - 0.21, ZB          # stops at the cornice face; plate clear of the door heads
mb = MB(); KP = [X['kilim2'], X['kilim']]
mb.box(CX0, CY0, ZT - 0.22, CX0 + 0.12, CY1, ZT, HD, 0.004)                                   # wall plate (chem. anchors to the facade)
NC = 7; ys_ = [CY0 + (CY1 - CY0) * k / NC for k in range(NC + 1)]
for y in ys_: mb.box(CX0 + 0.12, max(CY0, y - 0.07), ZT - 0.2, CX1, min(CY1, y + 0.07), ZT, HD, 0.006)       # primary beams 140 x 200
for k in range(NC):
    ya_c, yb_c = ys_[k] + 0.07, ys_[k + 1] - 0.07; xa_c, xb_c = CX0 + 0.12, CX1
    for x0_, y0_, x1_, y1_ in ((xa_c, ya_c, xb_c, ya_c + 0.08), (xa_c, yb_c - 0.08, xb_c, yb_c), (xa_c, ya_c + 0.08, xa_c + 0.08, yb_c - 0.08), (xb_c - 0.08, ya_c + 0.08, xb_c, yb_c - 0.08)):
        mb.box(x0_, y0_, ZT - 0.1, x1_, y1_, ZT, HX, 0.004)                                   # coffer frame (2nd step)
    mb.box(xa_c + 0.08, ya_c + 0.08, ZT - 0.012, xb_c - 0.08, ya_c + 0.095, ZT - 0.002, X['lampglow'])
    mb.box(xa_c + 0.08, yb_c - 0.095, ZT - 0.012, xb_c - 0.08, yb_c - 0.08, ZT - 0.002, X['lampglow'])
    mb.picture_box(xa_c + 0.08, ya_c + 0.08, ZT + 0.06, xb_c - 0.08, yb_c - 0.08, ZT + 0.075, KP[k % 2], '-z')       # kilim panel
    for x0_, y0_, x1_, y1_ in ((xa_c + 0.08, ya_c + 0.08, xb_c - 0.08, ya_c + 0.1), (xa_c + 0.08, yb_c - 0.1, xb_c - 0.08, yb_c - 0.08), (xa_c + 0.08, ya_c + 0.1, xa_c + 0.1, yb_c - 0.1), (xb_c - 0.1, ya_c + 0.1, xb_c - 0.08, yb_c - 0.1)):
        mb.box(x0_, y0_, ZT, x1_, y1_, ZT + 0.06, HX)                                          # cove upstand to the panel
    cx_, cy_ = (xa_c + xb_c) / 2, (ya_c + yb_c) / 2; dl = math.hypot(xb_c - xa_c - 0.2, yb_c - ya_c - 0.2)
    for sg in (1, -1): mb.obox(cx_, cy_, ZT - 0.0, ZT + 0.06, dl, 0.05, sg * math.atan2(yb_c - ya_c - 0.2, xb_c - xa_c - 0.2), HD, 0.004)   # X ribs
inst(mb.mesh('Aivan_ceiling'), 'Aivan_ceiling', (0, 0, 0), 0, 'Aivan')
for i_, (x0, y0, x1, y1) in enumerate(ats):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lantern_at(cx, cy, 1.95, 1.0, ZT + 0.06, 'Aivan', f'Aivan_lantern_{i_ + 1}')
for o_ in [o for o in bpy.data.objects if o.name.startswith('Zardevor')]: o_.location.z = ZT - 0.2 - 0.574 - 0.002   # under the wall plate
print('rev 8.5 aivan detailing ok: columns', len(COLY), 'plant bays', len(PLANT_BAYS), 'coffers', NC)
