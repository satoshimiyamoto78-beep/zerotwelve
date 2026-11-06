"""rev. 10.1 (owner booth refs: dark timber girih lattice on walls + ceiling, charcoal backing, upholstered settees, mosaic-glass
globe clusters, valance over the opening; 'booths step down like stairs — put the city names on them'):
every booth rebuilt — 150 mm podium (walnut fascia + a band of real glazed tiles in the booth colour, Persian rug on top),
lattice partitions (18 mm charcoal core, 40 mm walnut strip lattice both faces, posts), lattice ceiling at +2.40 over a charcoal
soffit, parapet to the street kept at +0.78 with a stone cap, pleated velvet valance over the view, 2 settees 1.10 (chair family)
facing across a 0.80 x 0.70 tile table, globe cluster, walnut name board with brass letters on the aisle side.
Ergonomics: seat +0.65 over the floor (+0.50 over the podium), seat depth 430, back 455, 550 per sitter, table +0.90 over the floor
(+0.75 over the podium), clear gap seat-front to table 30 mm, two steps of 150 mm read as a stair along the aisle."""
from shapely.geometry import LineString as _LS, box as _SB
from shapely.ops import unary_union as _UU
THEMES = [  # (name, tile colour, globe colour, lattice kind, cell)
    ('Самарканд', (0.03, 0.1, 0.42), (0.1, 0.25, 0.9), 'star', 0.30), ('Бухара', (0.06, 0.5, 0.52), (0.1, 0.75, 0.7), 'diamond', 0.26),
    ('Хива', (0.08, 0.38, 0.18), (0.2, 0.8, 0.3), 'hex', 0.32), ('Худжанд', (0.75, 0.52, 0.12), (1.0, 0.7, 0.2), 'star', 0.26),
    ('Пенджикент', (0.6, 0.15, 0.08), (1.0, 0.35, 0.15), 'diamond', 0.32), ('Ташкент', (0.05, 0.2, 0.5), (0.85, 0.85, 1.0), 'hex', 0.28),
    ('Маргилан', (0.5, 0.08, 0.32), (0.95, 0.25, 0.6), 'star', 0.34), ('Памир', (0.88, 0.86, 0.8), (0.95, 0.95, 0.85), 'diamond', 0.3)]
CHAR = mat('charcoal_mdf', (0.035, 0.032, 0.03), rough=0.75); WD = XW['wd']
STONE_ = bl._mats.get('cap_stone_white') or mat('cap_stone_white', (0.86, 0.84, 0.79), rough=0.35)
VELV = bl._mats.get('velvet_wine89') or X['velvet_wine']
def lattice_poly(u0, v0, u1, v1, kind, cell, w=0.022, frame=0.05):
    L = []; U, V = u1 - u0, v1 - v0; n = int(max(U, V) / cell) + 3
    for k in range(-n, 2 * n):
        c = k * cell
        if kind in ('star', 'square'):
            L.append(_LS([(u0 + c, v0 - 1), (u0 + c, v1 + 1)])); L.append(_LS([(u0 - 1, v0 + c), (u1 + 1, v0 + c)]))
        if kind in ('star', 'diamond'):
            L.append(_LS([(u0 + c - 5, v0 - 5), (u0 + c + 5, v0 + 5)])); L.append(_LS([(u0 + c - 5, v0 + 5), (u0 + c + 5, v0 - 5)]))
        if kind == 'hex':
            L.append(_LS([(u0 - 1, v0 + c * 0.866), (u1 + 1, v0 + c * 0.866)]))
            for s_ in (1, -1):
                L.append(_LS([(u0 + c - 6 * 0.577, v0 - s_ * 6), (u0 + c + 6 * 0.577, v0 + s_ * 6)]))
    inner = _SB(u0 + frame, v0 + frame, u1 - frame, v1 - frame)
    g = _UU([l.buffer(w / 2, cap_style=2) for l in L]).intersection(inner)
    g = _UU([g, _SB(u0, v0, u1, v1).difference(inner)])
    return [g] if g.geom_type == 'Polygon' else [q for q in g.geoms if q.geom_type == 'Polygon']
@cached
def a_globes(rgb):
    """mosaic-glass globe cluster: 5 globes on brass chains from a pierced canopy, origin = ceiling point"""
    gm = mat(f'globe_{int(rgb[0]*99)}{int(rgb[1]*99)}{int(rgb[2]*99)}', rgb, rough=0.2, emit=rgb, strength=3.0)
    b = MB(); b.lathe(0, 0, -0.06, [(0.0, 0.0), (0.12, 0.0), (0.1, 0.04), (0.03, 0.06), (0.0, 0.06)], m['brass'], 24)
    for k, (dx, dy, L) in enumerate(((0, 0, 0.75), (0.16, 0, 0.55), (-0.16, 0, 0.62), (0, 0.15, 0.48), (0, -0.15, 0.68))):
        b.rod((dx, dy, -0.06), (dx, dy, -L), 0.003, m['brass'], 6)
        b.lathe(dx, dy, -L - 0.17, [(0.0, 0.0), (0.04, 0.01), (0.075, 0.06), (0.08, 0.1), (0.06, 0.15), (0.02, 0.17), (0.0, 0.17)], gm, 16)
        b.lathe(dx, dy, -L - 0.005, [(0.0, 0.0), (0.02, 0.0), (0.02, 0.005), (0.0, 0.005)], m['brass'], 12)
    return b.mesh(f'Globes_{int(rgb[0]*99)}_{int(rgb[1]*99)}')
_rm(*[f'Booth{i}_{s}' for i in range(1, 9) for s in ('banquette', 'niche', 'pendant', 'table_', 'trim', 'wall')])
for i, (y0, y1, x0, x1, key) in enumerate(D['booths']):
    _rm(f'Booth{i + 1}_{key}')
    o_ = bpy.data.objects.get(f'Booth{i + 1}_table')
    if o_: bpy.data.objects.remove(o_)
B = D['booths']; ZP = TER + 0.15; ZC = TER + 2.40
# ---------------------------------------------------------------- partitions on every booth boundary
bounds = [B[0][0]] + [b_[1] for b_ in B]
for k, yb in enumerate(bounds):
    nb = [b_ for b_ in B if abs(b_[0] - yb) < 1e-3 or abs(b_[1] - yb) < 1e-3]
    xa, xe = max(b_[2] for b_ in nb), min(b_[3] for b_ in nb)
    kind, cell = THEMES[min(k, 7)][3], THEMES[min(k, 7)][4]
    mb = MB()
    mb.box(xa + 0.04, yb - 0.009, TER, xe - 0.18, yb + 0.009, ZC, CHAR)                                   # charcoal core
    for q in lattice_poly(xa + 0.04, TER, xe - 0.18, ZC, kind, cell):
        ext_holes(mb, q, yb + 0.009, yb + 0.04, WD, 'xz'); ext_holes(mb, q, yb - 0.04, yb - 0.009, WD, 'xz')
    mb.box(xa - 0.04, yb - 0.04, TER, xa + 0.04, yb + 0.04, ZC + 0.05, WD, 0.004)                        # aisle post
    mb.box(xe - 0.18, yb - 0.04, TER, xe, yb + 0.04, ZC + 0.05, WD, 0.004)                               # street post on the parapet line
    inst(mb.mesh(f'Booth_partition_{k}'), f'Booth_partition_{k}', (0, 0, 0), 0, 'Booths')
# ---------------------------------------------------------------- per booth
for i, (y0, y1, x0, x1, key) in enumerate(B):
    nm, tcol, gcol, kind, cell = THEMES[i]
    tmat = mat(f'booth_tile_{i}', tcol, rough=0.12, coat=0.9)
    ya, yb_ = y0 + 0.04, y1 - 0.04; xp = x1 - 0.18
    mb = MB()
    mb.box(x0, ya, TER, xp, yb_, ZP - 0.01, WD, 0.004)                                                    # podium carcass
    n = int((yb_ - ya - 0.04) / 0.103)
    for j in range(n):                                                                                    # tile band on the riser
        yy = ya + 0.02 + (yb_ - ya - 0.04 - n * 0.103) / 2 + j * 0.103
        mb.box(x0 - 0.012, yy, TER + 0.025, x0, yy + 0.1, TER + 0.125, tmat if j % 2 == 0 else TILE[1], 0.002)
    mb.box(xp, y0 + 0.04, TER, x1, y1 - 0.04, TER + 0.75, WD, 0.004)                                     # parapet to the street
    mb.box(xp, y0 + 0.04, TER + 0.75, x1 + 0.02, y1 - 0.04, TER + 0.78, STONE_, 0.004)             # stone cap (vases stand on it)
    mb.box(x0, ya, ZC, xp, yb_, ZC + 0.04, CHAR)                                                          # charcoal soffit
    for q in lattice_poly(x0, ya, xp, yb_, kind, cell * 0.9): ext_holes(mb, q, ZC - 0.035, ZC, WD, 'xy')    # lattice ceiling
    mb.box(x0 - 0.03, ya, ZC - 0.34, x0, yb_, ZC + 0.04, WD, 0.004)                                       # name board
    inst(mb.mesh(f'Booth{i + 1}_shell'), f'Booth{i + 1}_shell', (0, 0, 0), 0, 'Booths')
    # rug on the podium
    mb = MB(); fs = mb.picture_box(x0 + 0.03, ya + 0.02, ZP - 0.01, xp - 0.02, yb_ - 0.02, ZP, rugmat((i * 3 + 4) % NRUG + 1, False), '+z')
    inst(mb.mesh(f'Booth{i + 1}_rug'), f'Booth{i + 1}_rug', (0, 0, 0), 0, 'Booths')
    # valance over the street view (pleated velvet on a brass rod under the soffit)
    mb = MB(); pts = []; NN = 60
    for j in range(NN + 1):
        yy = ya + 0.01 + (yb_ - ya - 0.02) * j / NN; pts.append((xp - 0.02 - 0.02 * (1 + math.sin(2 * math.pi * j / 6)) / 2, yy))
    poly = [(xp - 0.005, ya + 0.01), (xp - 0.005, yb_ - 0.01)] + pts[::-1]
    mb.extrude(poly, ZC - 0.3, ZC - 0.035, VELV)
    inst(mb.mesh(f'Booth{i + 1}_valance'), f'Booth{i + 1}_valance', (0, 0, 0), 0, 'Booths')
    # settees + table (+ the tea set moves onto it)
    xc = (x0 + xp) / 2
    SL = 1.66 if xp - x0 >= 1.70 else 1.08                                                # rev 11.4: the aivan's 3-seat settee
    inst(a_settee(SL, 3 if SL > 1.5 else 2), f'Booth{i + 1}_settee_S', (xc, ya + 0.27, ZP), 0.0, 'Booths')
    inst(a_settee(SL, 3 if SL > 1.5 else 2), f'Booth{i + 1}_settee_N', (xc, yb_ - 0.27, ZP), math.pi, 'Booths')
    inst(a_teatable(1.4 if SL > 1.5 else 0.8, 0.85 if SL > 1.5 else 0.7), f'Booth{i + 1}_table', (xc, (y0 + y1) / 2, ZP), 0.0, 'Booths')
    ts = bpy.data.objects.get(f'Booth{i + 1}_tableset')
    if ts:
        lo_, hi_ = _bb(ts); ts.location.x += xc - (lo_[0] + hi_[0]) / 2; ts.location.y += (y0 + y1) / 2 - (lo_[1] + hi_[1]) / 2
        ts.location.z += ZP + 0.758 - lo_[2]; ts.scale.x = min(1.0, 0.7 / max(0.01, hi_[0] - lo_[0])); ts.scale.y = min(1.0, 0.6 / max(0.01, hi_[1] - lo_[1]))
    for o_ in [o for o in bpy.data.objects if o.name.startswith((f'Booth{i + 1}_parapet_vase', f'Booth{i + 1}_object'))]:
        lo_, hi_ = _bb(o_); o_.location.z += TER + 0.78 - lo_[2]
        if lo_[0] < xp - 0.02: o_.location.x += xp - 0.02 - lo_[0]
    inst(a_globes(gcol), f'Booth{i + 1}_globes', (xc, (y0 + y1) / 2, ZC - 0.035), 0.0, 'Booths')
    channel_text(nm, 0.13, 0.012, m['brass'], (x0 - 0.03, (y0 + y1) / 2, ZC - 0.24), (0, -1, 0), f'Booth{i + 1}_name')
print('rev 10.1 booths rebuilt', len(B))
