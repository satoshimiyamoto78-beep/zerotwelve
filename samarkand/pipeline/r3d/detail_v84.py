"""rev. 8.4 — AIVAN ARCADE per the owner's reference (Uzbek carved timber gallery): square carved pedestals, fluted shafts with turned
rings, turned capitals under a stepped abacus, multifoil (cusped) arches with a raised walnut frame, carved spandrels, a frieze with a
scalloped drop edge and a stepped cornice; carved fascia on the aivan deck edge. Replaces the rev. 7 Khiva columns / heads / beam."""
XA = 3.18; ZB = 3.02; ZC = ZB - 0.24
COLY = [15.45, 18.17] + [18.17 + (24.18 - 18.17) * k / 5 for k in range(1, 5)] + [24.18, 25.92, 27.13, 28.34]
OPEN = ((15.45, 18.17), (24.18, 25.92))
_rm('Khiva_column', 'Khiva_arcade_head', 'Khiva_arcade_beam')

@cached
def a_aivan_column(H):
    """carved pedestal 0.26 sq (0..0.62), turned base, 16-flute shaft with three turned rings, turned capital, stepped abacus to H"""
    b = MB(); W, C, WN = X['carved'], X['carved'], m['walnut']
    b.box(-0.118, -0.118, 0.0, 0.118, 0.118, 0.06, WN, 0.006)
    b.box(-0.105, -0.105, 0.06, 0.105, 0.105, 0.56, C, 0.004)
    b.box(-0.118, -0.118, 0.56, 0.118, 0.118, 0.6, WN, 0.006); b.box(-0.11, -0.11, 0.6, 0.11, 0.11, 0.62, WN, 0.004)
    b.lathe(0, 0, 0.62, [(0.0, 0.0), (0.105, 0.0), (0.105, 0.03), (0.092, 0.05), (0.1, 0.08), (0.088, 0.12), (0.085, 0.16), (0.0, 0.16)], WN, 24)
    z0, z1 = 0.78, H - 0.42
    fl = [((0.08 - 0.009 * abs(math.sin(8 * a))) * math.cos(a), (0.08 - 0.009 * abs(math.sin(8 * a))) * math.sin(a)) for a in [2 * math.pi * k / 96 for k in range(96)]]
    b.extrude(fl, z0, z1, W, 'xy')
    for zr in (z0 + 0.04, z0 + (z1 - z0) * 0.62, z1 - 0.05):
        b.lathe(0, 0, zr - 0.03, [(0.0, 0.0), (0.082, 0.0), (0.095, 0.015), (0.095, 0.045), (0.082, 0.06), (0.0, 0.06)], WN, 24)
    b.lathe(0, 0, z1, [(0.0, 0.0), (0.085, 0.0), (0.1, 0.04), (0.09, 0.08), (0.11, 0.13), (0.125, 0.2), (0.11, 0.25), (0.13, 0.28), (0.13, 0.3), (0.0, 0.3)], WN, 24)
    b.box(-0.12, -0.12, H - 0.12, 0.12, 0.12, H - 0.06, C, 0.004); b.box(-0.15, -0.15, H - 0.06, 0.15, 0.15, H, WN, 0.006)
    return b.mesh(f'Aivan_column_{int(H * 100)}')

def _cusped_left(c, w, zs, za, lobes=3, A=0.055, n=72):
    """left half of a multifoil pointed arch: the rev. 7 pointed curve with `lobes` scallops cut into the spandrel side"""
    base = arch_left(c, w, zs, za, n)
    out = []
    for k, (u, z) in enumerate(base):
        t = k / n; ka, kb = max(0, k - 1), min(n, k + 1)
        tu, tz = base[kb][0] - base[ka][0], base[kb][1] - base[ka][1]; L_ = math.hypot(tu, tz) or 1.0
        nu, nz = -tz / L_, tu / L_                                  # left normal = into the spandrel
        o = A * abs(math.sin(lobes * math.pi * t)) * (1.0 if t < 0.97 else (1 - t) / 0.03)
        out.append((u + nu * o, z + nz * o))
    return out

@cached
def a_aivan_head(L, open_):
    """arch head of one bay (local y 0..L, beam underside at z 0): carved spandrels between the abacus edges (y 0.15..L-0.15),
    raised walnut frame 45 wide following the cusped outline, a small pierced lantern at the apex of closed bays"""
    b = MB(); w = L - 0.40; c = L / 2; zs = -(0.80 if not open_ else 0.78); za = -0.1          # closed bays: springs just above the jali frame (+1.96)
    pts = _cusped_left(c, w, zs, za)
    left = pts + [(c, 0.0), (c - w / 2, 0.0)]; right = [(2 * c - u, z) for u, z in pts] + [(c, 0.0), (c + w / 2, 0.0)]
    for poly in (left, right): b.extrude(poly, -0.05, 0.05, X['carved'], 'yz')
    def off(ps, d):
        o = []
        for k, (u, z) in enumerate(ps):
            ka, kb = max(0, k - 1), min(len(ps) - 1, k + 1); tu, tz = ps[kb][0] - ps[ka][0], ps[kb][1] - ps[ka][1]; L_ = math.hypot(tu, tz) or 1.0
            o.append((u - tz / L_ * d, z + tu / L_ * d))
        return o
    for side in (pts, [(2 * c - u, z) for u, z in pts]):
        sd = side if side is pts else list(reversed(side))
        inner = sd; outer = off(sd, 0.038 if side is pts else -0.038)
        for k in range(len(inner) - 1):                              # frame as short quads (robust on the cusps)
            q = [inner[k], inner[k + 1], outer[k + 1], outer[k]]
            if abs(sum(q[i][0] * q[(i + 1) % 4][1] - q[(i + 1) % 4][0] * q[i][1] for i in range(4))) > 1e-7: b.extrude(q, -0.065, 0.065, m['walnut'], 'yz')
    if not open_: _pierced(b, 0, c, za - 0.02, 0.7)
    return b.mesh(f'Aivan_head_{int(L * 1000)}_{int(open_)}')

for i_, y in enumerate(COLY): inst(a_aivan_column(ZC), f'Khiva_column_{i_ + 1:02d}', (XA, y, 0.0), 0, 'Aivan')
for i_, (ya, yb) in enumerate(zip(COLY[:-1], COLY[1:])):
    L = round(yb - ya, 4); inst(a_aivan_head(L, (ya, yb) in OPEN), f'Khiva_arcade_head_{i_ + 1:02d}', (XA, ya, ZC), 0, 'Aivan')

# frieze beam: walnut core, carved panels on both faces, scalloped drop edge, stepped cornice (all inside the 240 under the roof beams)
mb = MB(); y0_, y1_ = COLY[0] - 0.15, COLY[-1] + 0.15
mb.box(XA - 0.13, y0_, ZC, XA + 0.13, y1_, ZB - 0.06, m['walnut'], 0.004)
for sx in (-1, 1):
    mb.box(XA + sx * 0.13, y0_, ZC + 0.04, XA + sx * 0.145, y1_, ZB - 0.1, X['carved'])
    mb.box(XA + sx * 0.145, y0_, ZC + 0.02, XA + sx * 0.152, y1_, ZC + 0.035, m['brass'])
mb.box(XA - 0.17, y0_ - 0.04, ZB - 0.06, XA + 0.17, y1_ + 0.04, ZB - 0.03, m['walnut'], 0.004)
mb.box(XA - 0.21, y0_ - 0.08, ZB - 0.03, XA + 0.21, y1_ + 0.08, ZB, m['walnut'], 0.004)
yy = y0_ + 0.05
while yy + 0.04 < y1_:                                            # scalloped drop edge (half discs r 35 every 90) on both faces
    if any(abs(yy - cy_) < 0.2 for cy_ in COLY): yy += 0.09; continue
    semi = [(yy + 0.035 * math.cos(math.pi * k / 10), ZC - 0.035 * math.sin(math.pi * k / 10)) for k in range(11)]
    for sx in (-1, 1): mb.extrude(semi, XA + sx * 0.13, XA + sx * 0.11, m['walnut'], 'yz')
    yy += 0.09
inst(mb.mesh('Khiva_arcade_beam'), 'Khiva_arcade_beam', (0, 0, 0), 0, 'Aivan')

# carved fascia on the aivan deck edge (terrace side, x 3.30), interrupted at the two stairs; zig-zag top band
mb = MB()
for a_, b_ in ((15.3, 15.55), (18.05, 24.3), (25.8, 28.5)):
    mb.box(3.30, a_, TER, 3.325, b_, -0.06, X['carved'])
    mb.box(3.30, a_, -0.06, 3.335, b_, -0.0, m['walnut'], 0.003)
inst(mb.mesh('Aivan_fascia'), 'Aivan_fascia', (0, 0, 0), 0, 'Aivan')
print('rev 8.4 aivan arcade ok', len(COLY), 'columns')
