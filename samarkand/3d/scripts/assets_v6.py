"""Samarkand asset library v6 — the bar (owner references: sculpted clay niche wall, terracotta baguette front,
beaded ikat drum pendants, wooden stools, wall carpet, reed fringe), chinar trunk, sebil fountain.
Closed shells, flush joints; shapely is used for the niche wall (wall = panel minus rounded niche shapes)."""
import math
from shapely.geometry import box as sbox, LineString
from shapely.ops import unary_union, split as ssplit

def _pieces(poly):
    """hole-free pieces of a polygon (cuts along z through every hole's top and bottom)"""
    out = []
    for p in getattr(poly, 'geoms', [poly]):
        if p.is_empty: continue
        if not p.interiors: out.append(p); continue
        cuts = sorted({round(v, 6) for r in p.interiors for v in (r.bounds[1], r.bounds[3])})
        ps = [p]
        for c in cuts:
            nxt = []
            for q in ps:
                try: nxt.extend(ssplit(q, LineString([(-100, c), (100, c)])).geoms)
                except Exception: nxt.append(q)
            ps = nxt
        for q in ps: out.extend(_pieces(q) if q.interiors else [q])
    return [q for q in out if q.area > 1e-5]
def _rr(y0, z0, y1, z1, r):
    return sbox(y0, z0, y1, z1).buffer(-r, join_style=1).buffer(r, resolution=6, join_style=1)

BAR_NICHES = [  # Timurid pointed-arch niches: (y0, y1, sill, springing, apex) along the wall (local metres from the bar floor)
    (0.25, 1.15, 1.2, 2.3, 2.75), (1.45, 2.15, 1.2, 2.1, 2.45), (2.45, 3.55, 1.2, 2.35, 2.85), (3.85, 4.55, 1.2, 2.1, 2.45)]
@cached
def a_barwall(L, Hw):
    """back-bar in the Samarkand manner: tiled back counter (x 0..0.55, top +0.96), bannai glazed-brick wall (x 0..0.32) with
    pointed-arch niches in kufic frames, cobalt majolica niche backs, walnut shelves with warm LED, bottles / jars / samovar;
    local y 0..L along the building face, x = 0 at the wall line"""
    b = MB(); W = m['walnut']; BR = X['bannai']
    b.box(0.0, 0.0, 0.0, 0.55, L, 0.12, X['stone'], 0.004)
    b.box(0.0, 0.0, 0.12, 0.53, L, 0.92, X['girihstar'], 0.004); b.box(0.0, -0.01, 0.92, 0.57, L + 0.01, 0.96, W, 0.004)
    b.box(0.0, 0.0, 0.96, 0.10, L, Hw, X['majcobalt'])                                               # back skin = niche backs
    holes = []
    for y0, y1, zs, zsp, za in BAR_NICHES:
        c, w = (y0 + y1) / 2, y1 - y0; Lp = arch_left(c, w, zsp, za, 12); Rp = [(2 * c - u, z) for u, z in Lp]
        from shapely.geometry import Polygon as _Poly
        holes.append(_Poly([(y0, zs), (y1, zs)] + Rp + Lp[::-1][1:]))
    wall = sbox(0.0, 0.96, L, Hw).difference(unary_union(holes))
    for q in _pieces(wall): b.extrude(list(q.exterior.coords)[:-1], 0.10, 0.32, BR, 'yz')
    for h in holes:                                                                                     # kufic glazed-brick frame, 20 mm proud
        fr = h.buffer(0.075, join_style=2, mitre_limit=2.5).difference(h).intersection(sbox(0.0, 0.96, L, Hw))
        for q in _pieces(fr): b.extrude(list(q.exterior.coords)[:-1], 0.32, 0.34, X['kufic'], 'yz')
    rnd = random.Random(5)
    for h, (y0n, y1n, zs, zsp, za) in zip(holes, BAR_NICHES):
        levels = [zs] + [zs + k * 0.42 for k in range(1, 4) if zs + k * 0.42 < zsp - 0.05]
        for zl in levels:
            ya, yb = y0n + 0.004, y1n - 0.004
            if zl > zs:
                b.box(0.10, ya, zl, 0.30, yb, zl + 0.03, W, 0.003); b.box(0.27, ya + 0.02, zl - 0.008, 0.29, yb - 0.02, zl, X['lampglow'])
            zt = zl + (0.03 if zl > zs else 0.0); y = ya + 0.05
            while y < yb - 0.08:
                k = rnd.random()
                if k < 0.4: b.lathe(0.2, y, zt, [(0.0, 0.0), (0.032, 0.0), (0.032, 0.2), (0.012, 0.25), (0.011, 0.29), (0.0, 0.29)], m['glass'], 12); y += 0.075
                elif k < 0.75: b.lathe(0.2, y, zt, [(0.0, 0.0), (0.04, 0.0), (0.06, 0.05), (0.05, 0.12), (0.025, 0.16), (0.03, 0.18), (0.0, 0.18)], X['rishtan'] if 'rishtan' in X else m['clay'], 16); y += 0.12
                else: b.lathe(0.2, y, zt, [(0.0, 0.0), (0.05, 0.0), (0.06, 0.08), (0.04, 0.16), (0.045, 0.18), (0.0, 0.19)], m['clay'], 14); y += 0.12
        b.box(0.12, y0n + 0.06, zsp - 0.02, 0.14, y1n - 0.06, zsp, X['lampglow'])                     # warm glow at the springing line
    y0h, y1h = BAR_NICHES[2][0], BAR_NICHES[2][1]                                                       # samovar in the central niche
    b.lathe(0.2, (y0h + y1h) / 2, 1.2, [(0.0, 0.0), (0.06, 0.0), (0.05, 0.04), (0.1, 0.1), (0.11, 0.2), (0.08, 0.3), (0.04, 0.33), (0.05, 0.36), (0.0, 0.38)], m['brass'], 20)
    return b.mesh(f'Barwall_{int(L * 1000)}')

@cached
def a_bar_cornice(L, ztop):
    """carved walnut frieze with a row of stepped muqarnas corbels under it (Khiva carving), hung on the wall face;
    local x 0..0.14 out from the wall face, y 0..L, top at ztop"""
    b = MB(); W = m['walnut']; C = X['carved']
    b.box(0.0, 0.0, ztop - 0.22, 0.06, L, ztop, C, 0.003)
    b.box(0.0, 0.0, ztop - 0.03, 0.14, L, ztop, W, 0.004)
    n = int(L / 0.16)
    for k in range(n):
        yc = (k + 0.5) * L / n
        for t, (d, hz) in enumerate(((0.025, 0.05), (0.05, 0.05), (0.08, 0.05))):
            z1 = ztop - 0.03 - t * 0.05; b.box(0.06 if t == 0 else 0.0, yc - 0.055 + 0.012 * t, z1 - hz, 0.06 + d, yc + 0.055 - 0.012 * t, z1, W if t % 2 else C, 0.003)
    return b.mesh(f'Bar_cornice_{int(L * 1000)}')

def _flutes(b, y0, y1, z0, z1, xf, axis_y=True, rows=3, sgn=1):
    """terracotta baguette cladding on the plane x = xf (or y = xf), growing towards +sgn: rows of vertical glazed sticks,
    deep and shallow alternating in a checker (as in the references)"""
    w, g = 0.046, 0.008; n = int((y1 - y0) / (w + g)); off = ((y1 - y0) - n * (w + g) + g) / 2
    hz = (z1 - z0) / rows
    for r in range(rows):
        for k in range(n):
            a = y0 + off + k * (w + g); d = 0.075 if (k // 2 + r) % 2 else 0.04
            za, zb = z0 + r * hz + 0.004, z0 + (r + 1) * hz - 0.004
            TC = X['glazeturq'] if d > 0.05 else X['glazecob']                                   # Shah-i-Zinda glazed bricks: deep turquoise / shallow cobalt
            if axis_y: b.box(xf, a, za, xf + sgn * d, a + w, zb, TC, 0.004)
            else: b.box(a, xf, za, a + w, xf + sgn * d, zb, TC, 0.004)
@cached
def a_barcounter(L, Lr):
    """front bar: plastered body x 0..0.62, y 0..L (+ return y -Lr..0 with x 0..0.9), terracotta baguette front on x = 0.62
    and on the return face y = -Lr, toe-kick LED, walnut top with a 0.26 overhang; origin at the body's back corner"""
    b = MB(); P = X['bannai']; W = m['walnut']; t = 0.1
    b.box(0.0, 0.0, 0.0, 0.62, L, 1.03, P, 0.004)
    b.box(0.0, -Lr, 0.0, 0.9, 0.0, 1.03, P, 0.004)
    b.box(0.62, 0.0, t - 0.012, 0.64, L, t, X['lampglow'])
    _flutes(b, 0.0, L, t, 1.0, 0.62, True, 3, 1)
    _flutes(b, 0.0, 0.9, t, 1.0, -Lr, False, 3, -1)
    b.box(0.0, -Lr, -0.012 + t, 0.9, -Lr - 0.02, t, X['lampglow'])
    b.box(-0.05, -Lr - 0.26, 1.03, 0.92, L, 1.09, W, 0.006)                                     # top: return + main run
    b.box(0.92, -Lr - 0.26, 1.03, 0.62 + 0.26, L, 1.09, W, 0.006)
    return b.mesh(f'Barcounter_{int(L * 1000)}')

@cached
def a_barstool():
    """wooden bar stool, seat +0.76 (leather pad), low back to +1.02; back on -Y, the sitter faces +Y"""
    b = MB(); W = m['walnut']; LE = X['leather']
    for sx in (-1, 1):
        b.rod((sx * 0.165, 0.15, 0.72), (sx * 0.2, 0.19, 0.014), 0.017, W, 10)
        b.rod((sx * 0.165, -0.15, 1.02), (sx * 0.2, -0.19, 0.014), 0.019, W, 10)
        for fy in (0.19, -0.19): b.cyl(sx * 0.2, fy, 0.0, 0.012, 0.024, m['black'], 12)                  # felt glides
    for z in (0.26, 0.5):
        b.rod((-0.188, 0.178, z * 0.97), (0.188, 0.178, z * 0.97), 0.011, W, 8) if z == 0.26 else b.rod((-0.185, -0.17, z), (0.185, -0.17, z), 0.011, W, 8)
        b.rod((-0.186, -0.165, z), (-0.186, 0.165, z), 0.011, W, 8); b.rod((0.186, -0.165, z), (0.186, 0.165, z), 0.011, W, 8)
    b.box(-0.2, -0.19, 0.72, 0.2, 0.19, 0.745, W, 0.004)
    b.box(-0.185, -0.17, 0.745, 0.185, 0.18, 0.775, LE, 0.012)
    b.box(-0.19, -0.2, 0.86, 0.19, -0.165, 1.02, W, 0.005)
    b.box(-0.17, -0.165, 0.88, 0.17, -0.15, 1.0, LE, 0.006)
    return b.mesh('Barstool')

@cached
def a_drum_pendant(drop):
    """beaded ikat drum pendant: rod `drop` from the ceiling (origin) to a brass crown, beaded drum r 0.22 h 0.30 with the
    pattern from the reference photo, bead tassels below, warm bulb inside"""
    b = MB(); R, Hd = 0.22, 0.3; zt = -drop; zb = zt - Hd; N = 48; T = 0.006
    b.cyl(0, 0, zt, 0.0, 0.007, m['brass'], 8)
    b.ring(0, 0, zt - 0.015, [(R - 0.012, 0.0), (R + 0.01, 0.0), (R + 0.01, 0.015), (R - 0.012, 0.015)], m['brass'], N)
    for k in range(4):
        a = k * math.pi / 2; b.rod((0, 0, zt), (R * math.cos(a), R * math.sin(a), zt - 0.008), 0.004, m['brass'], 6)
    # drum: closed tube with a cylindrical picture UV on the outer face
    i = b.mi(X['beadikat']); rows = []
    for rr, zz in ((R, zb), (R, zt - 0.015), (R - T, zt - 0.015), (R - T, zb)):
        rows.append([b.bm.verts.new((rr * math.cos(2 * math.pi * k / N), rr * math.sin(2 * math.pi * k / N), zz)) for k in range(N)])
    for si, (p_, q_) in enumerate(zip(rows, rows[1:] + rows[:1])):
        for k in range(N):
            f = b.bm.faces.new((p_[k], p_[(k + 1) % N], q_[(k + 1) % N], q_[k])); f.material_index = i
            if si == 0:
                for lp, uv in zip(f.loops, ((2 * k / N, 0.0), (2 * (k + 1) / N, 0.0), (2 * (k + 1) / N, 1.0), (2 * k / N, 1.0))): lp[b.uv].uv = uv
                b.fixed.add(f)
    b.ring(0, 0, zb - 0.012, [(R - 0.01, 0.0), (R + 0.008, 0.0), (R + 0.008, 0.012), (R - 0.01, 0.012)], m['brass'], N)
    for k in range(36):                                                                                    # bead tassels
        a = 2 * math.pi * k / 36; L_ = 0.05 + 0.04 * (k % 3); x, y = (R - 0.001) * math.cos(a), (R - 0.001) * math.sin(a)
        b.cyl(x, y, zb - 0.012 - L_, zb - 0.012, 0.0035, m['brass'], 6)
        b.lathe(x, y, zb - 0.012 - L_ - 0.018, [(0.0, 0.0), (0.008, 0.004), (0.009, 0.009), (0.008, 0.014), (0.0, 0.018)], X['domeglaze'] if k % 2 else m['ceramic'], 8)
    b.lathe(0, 0, zt - 0.2, [(0.0, 0.0), (0.04, 0.01), (0.05, 0.06), (0.03, 0.11), (0.012, 0.13), (0.012, 0.185), (0.0, 0.185)], X['lampglow'], 16)
    return b.mesh(f'Drum_pendant_{int(drop * 100)}')

@cached
def a_fringe(L, hmax):
    """reed fringe: walnut batten (local x 0..0.14, y 0..L, z -0.05..0) with dried-reed strands hanging up to hmax"""
    b = MB(); rnd = random.Random(11); RE = X['reed']
    b.box(0.0, 0.0, -0.05, 0.14, L, 0.0, m['walnut'], 0.004)
    y = 0.004
    while y < L - 0.01:
        for row, x in enumerate((0.03, 0.075, 0.11)):
            h = hmax * rnd.uniform(0.55, 1.0); w = rnd.uniform(0.006, 0.01)
            b.box(x - 0.003, y + row * 0.004, -0.05 - h, x + 0.003, y + row * 0.004 + w, -0.05, RE)
        y += 0.014
    return b.mesh(f'Reed_fringe_{int(L * 1000)}')

@cached
def a_chinar_trunk(H, r0, r1):
    """plane-tree trunk: root flare with 6 buttresses, bark ridges, tapering to r1 at H; origin at the floor"""
    b = MB(); N = 36; prof = [(0.0, r0 * 1.9), (0.08, r0 * 1.6), (0.25, r0 * 1.2), (0.5, r0 * 1.05), (1.2, r0), (2.5, r0 * 0.9), (4.0, (r0 + r1) / 2), (H, r1)]
    rings = []
    for z, r in prof:
        flare = max(0.0, 1 - z / 0.6)
        rings.append([b.bm.verts.new(((r * (1 + 0.28 * flare * max(0, math.cos(3 * a)) ** 3 + 0.035 * math.sin(11 * a + z * 1.7))) * math.cos(a),
                                      (r * (1 + 0.28 * flare * max(0, math.cos(3 * a)) ** 3 + 0.035 * math.sin(11 * a + z * 1.7))) * math.sin(a), z))
                      for a in [2 * math.pi * k / N for k in range(N)]])
    i = b.mi(X['bark2']); fs = []
    for p_, q_ in zip(rings[:-1], rings[1:]):
        for k in range(N): fs.append(b.bm.faces.new((p_[k], p_[(k + 1) % N], q_[(k + 1) % N], q_[k])))
    fs += [b.bm.faces.new(list(reversed(rings[0]))), b.bm.faces.new(rings[-1])]
    for f in fs: f.material_index = i
    bmesh.ops.recalc_face_normals(b.bm, faces=fs)
    return soften(b.mesh('Chinar_trunk'), 1)

@cached
def a_sebil(Wd, D, Db, zf=0.3):
    """street wall fountain (sebil): glazed-brick wall D deep with a pointed-arch niche (girih back, majolica tympanum,
    kufic frame and head band), bronze spout, stone basin Db deep in front; local y 0..Wd along the street,
    x 0..D (+x = street side), z from the sidewalk"""
    b = MB(); ST = X['stone']; H = 2.6; c = Wd / 2; w = Wd - 0.5; zs, za = 1.75, 2.15
    b.box(0.0, 0.0, 0.0, D, Wd, 0.3, ST, 0.008)
    b.box(0.0, 0.0, 0.3, D - 0.15, Wd, H - 0.25, X['hazarbaf'])                                   # back mass behind the niche
    b.box(D - 0.15, 0.25, 0.3, D - 0.135, Wd - 0.25, za, X['girihstar'])                          # niche back panel
    for ya, yb in ((0.0, 0.25), (Wd - 0.25, Wd)):
        b.box(D - 0.15, ya, 0.3, D, yb, H - 0.25, X['hazarbaf'])
        b.box(D, ya + 0.03, zf, D + 0.02, yb - 0.03, H - 0.25, X['kufic'])
    for poly in spandrel_polys(c, w, zs, za, H - 0.25): b.extrude(poly, D - 0.15, D, X['majcobalt'], 'yz')
    L_ = arch_left(c, w, zs, za, 10); R_ = [(2 * c - u, z) for u, z in L_][::-1]
    for (u0, z0), (u1, z1) in zip(L_ + R_[1:], (L_ + R_[1:])[1:]): b.rod((D + 0.004, u0, z0), (D + 0.004, u1, z1), 0.02, X['domeglaze'], 8)
    b.box(-0.0, -0.03, H - 0.25, D + 0.05, Wd + 0.03, H, X['kufic'], 0.006)
    b.box(-0.0, -0.05, H, D + 0.07, Wd + 0.05, H + 0.06, ST, 0.008)
    b.rod((D - 0.135, c, 0.95), (D + 0.12, c, 0.9), 0.014, m['bronze'], 10)
    b.lathe(D - 0.135, c, 0.92, [(0.0, 0.0), (0.05, 0.0), (0.05, 0.06), (0.0, 0.06)], m['bronze'], 16)
    b.box(D, 0.25, 0.0, D + Db, Wd - 0.25, 0.4, ST, 0.01)                                       # basin: solid base + rim walls, water inside
    for x0_, y0_, x1_, y1_ in ((D, 0.25, D + Db, 0.3), (D, Wd - 0.3, D + Db, Wd - 0.25), (D + Db - 0.05, 0.3, D + Db, Wd - 0.3)):
        b.box(x0_, y0_, 0.4, x1_, y1_, 0.55, ST, 0.005)
    b.box(D, 0.3, 0.4, D + Db - 0.05, Wd - 0.3, 0.5, m['water'])
    return b.mesh(f'Sebil_{int(Wd * 1000)}')
