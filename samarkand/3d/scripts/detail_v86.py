"""rev. 8.6 — AIVAN ARCADE SIMPLIFIED for cheap, fast building (owner ref.: straight timber posts + CNC-cut arch panels with fretwork):
  * posts: solid square timber, lower block 160 x 160 to +0.95 (plinth, two routed grooves, moulded cap), upper post 120 x 120 to the beam
  * beam: straight 140 x 240 timber on the posts
  * arch panels: one CNC-cut 25 mm board per bay = rectangle minus a plain two-centred pointed arch; the area above the arch is pierced
    with a simple 8-point-star fretwork (60 mm solid border round the arch and the board edges)
  * lower part of closed bays: sturdy timber grid (30 x 30 bars @ 100) in a frame, handrail +0.95
  * three bays carry a 250 shelf at +0.55 with terracotta vases (owner ref.: matt rough clay, simple organic forms, some ribbed)
Replaces the rev. 8.5 columns / arch heads / frieze / bays; keeps its balustrades, sedirs, tables, screens and coffered ceiling."""
XA = 3.18; ZB = 3.02; ZC = ZB - 0.24
COLY = [15.45, 18.17] + [18.17 + (24.18 - 18.17) * k / 5 for k in range(1, 5)] + [24.18, 25.92, 27.13, 28.34]
OPEN = ((15.45, 18.17), (24.18, 25.92))
_rm('Khiva_column', 'Khiva_arcade_head', 'Khiva_arcade_beam', 'Khiva_arcade_bay', 'Aivan_shrub_foliage')

def terracotta(name, base, rough=0.85, bump=0.6, rib=0.0):
    """matt rough clay: base colour mottled by noise, fine grain bump; rib > 0 adds horizontal throwing rings"""
    if name in bl._mats: return bl._mats[name]
    mm = bpy.data.materials.new(name); mm.use_nodes = True; N = mm.node_tree.nodes; Lk = mm.node_tree.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    tc = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9.0; nz.inputs['Detail'].default_value = 6; Lk.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (*[c * 0.78 for c in base], 1); cr.color_ramp.elements[1].color = (*[min(1, c * 1.15) for c in base], 1)
    Lk.new(nz.outputs['Fac'], cr.inputs['Fac']); Lk.new(cr.outputs['Color'], b.inputs['Base Color'])
    gr = N.new('ShaderNodeTexNoise'); gr.inputs['Scale'].default_value = 420.0; Lk.new(tc.outputs['Object'], gr.inputs['Vector'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump * 0.25; bp.inputs['Distance'].default_value = 0.002
    if rib > 0:
        sp = N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Object'], sp.inputs['Vector'])
        sw = N.new('ShaderNodeMath'); sw.operation = 'SINE'; mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = rib
        Lk.new(sp.outputs['Z'], mul.inputs[0]); Lk.new(mul.outputs['Value'], sw.inputs[0])
        ad = N.new('ShaderNodeMath'); ad.operation = 'ADD'; Lk.new(sw.outputs['Value'], ad.inputs[0]); Lk.new(gr.outputs['Fac'], ad.inputs[1])
        bp.inputs['Strength'].default_value = bump * 0.5; Lk.new(ad.outputs['Value'], bp.inputs['Height'])
    else: Lk.new(gr.outputs['Fac'], bp.inputs['Height'])
    Lk.new(bp.outputs['Normal'], b.inputs['Normal'])
    bl._mats[name] = mm; return mm
TC = dict(red=terracotta('tc_red', (0.56, 0.24, 0.13)), orange=terracotta('tc_orange', (0.66, 0.33, 0.17)),
          sand=terracotta('tc_sand', (0.70, 0.45, 0.28), rib=900.0), rust=terracotta('tc_rust', (0.50, 0.25, 0.12), bump=1.0))

VASES = {   # (r, z) profiles in m, owner refs: bottle, tall slender, globe with a small neck, ribbed globe, rustic jar
    'bottle': ([(0.0, 0.0), (0.06, 0.0), (0.105, 0.05), (0.118, 0.14), (0.1, 0.24), (0.06, 0.31), (0.04, 0.36), (0.038, 0.46), (0.044, 0.475), (0.0, 0.475)], 'red'),
    'tall': ([(0.0, 0.0), (0.06, 0.0), (0.075, 0.1), (0.085, 0.3), (0.07, 0.48), (0.052, 0.6), (0.05, 0.66), (0.0, 0.66)], 'orange'),
    'globe': ([(0.0, 0.0), (0.05, 0.0), (0.12, 0.05), (0.14, 0.13), (0.12, 0.21), (0.06, 0.25), (0.035, 0.27), (0.035, 0.34), (0.04, 0.345), (0.0, 0.345)], 'red'),
    'ribbed': ([(0.0, 0.0), (0.06, 0.0), (0.13, 0.06), (0.15, 0.15), (0.13, 0.24), (0.075, 0.29), (0.07, 0.33), (0.08, 0.34), (0.0, 0.34)], 'sand'),
    'jar': ([(0.0, 0.0), (0.06, 0.0), (0.1, 0.06), (0.115, 0.15), (0.095, 0.22), (0.075, 0.24), (0.085, 0.255), (0.088, 0.27), (0.0, 0.27)], 'rust'),
}
@cached
def a_vase_tc(kind):
    prof, c = VASES[kind]; b = MB()
    b.lathe(0, 0, 0, prof, TC[c], 40)
    return b.mesh(f'Vase_tc_{kind}')

@cached
def a_post86(H):
    """square timber post: lower block 160 (plinth 180, two 4 mm routed grooves, moulded cap) to +0.95, upper post 120 to H"""
    b = MB()
    b.box(-0.09, -0.09, 0.0, 0.09, 0.09, 0.08, HZ, 0.008)
    for z0, z1, h in ((0.08, 0.3, 0.08), (0.3, 0.32, 0.076), (0.32, 0.6, 0.08), (0.6, 0.62, 0.076), (0.62, 0.88, 0.08)):
        b.box(-h, -h, z0, h, h, z1, HZ, 0.004 if h == 0.08 else 0.0)
    b.box(-0.09, -0.09, 0.88, 0.09, 0.09, 0.92, HZ, 0.008); b.box(-0.075, -0.075, 0.92, 0.075, 0.075, 0.95, HZ, 0.006)
    b.box(-0.06, -0.06, 0.95, 0.06, 0.06, H, HZ, 0.006)
    return b.mesh(f'Aivan86_post_{int(H * 100)}')

def pointed(c, w, zs, za, n=24):
    """plain two-centred pointed arch opening (legs run down to zs - 2)"""
    h = za - zs; R = (w * w / 4 + h * h) / w                    # both arcs pass the spring points and meet at the apex
    cL, cR = c - w / 2 + R, c + w / 2 - R
    left = [(cL - R * math.cos(t), zs + R * math.sin(t)) for t in [math.asin(h / R) * k / n for k in range(n + 1)]]
    right = [(2 * c - u, z) for u, z in reversed(left[:-1])]
    return SPoly([(c - w / 2, zs - 2.0)] + left + right + [(c + w / 2, zs - 2.0)]).buffer(0)
@cached
def a_archpanel86(L, open_):
    """CNC board 25 mm between the post faces (local y 0..L, beam underside at z 0): pointed arch, star fretwork above it"""
    b = MB(); y0, y1 = 0.06, L - 0.06; za = -0.16 if not open_ else -0.12; w = (y1 - y0) - 0.1
    zs = za - max(0.79, 0.53 * w)                                 # wide stair bays: spring lower so the two arcs still meet in a point
    rect = SBox(y0, zs, y1, 0.0); op = pointed((y0 + y1) / 2, w, zs, za)
    board = rect.difference(op)
    field = board.buffer(-0.06, join_style=2)
    stars = []
    cell = 0.13; nyc = int((y1 - y0) / cell) + 1; nzc = int(abs(zs) / cell) + 1      # stars r 52 @ 130: bars >= 25 mm for the router
    for i in range(nyc + 1):
        for j in range(nzc + 1):
            cy, cz = y0 + (i + 0.5) * cell, zs + (j + 0.5) * cell
            stars.append(star8(cy, cz, 0.40 * cell, math.pi / 8))
    pierce = field.intersection(SUnion(stars))
    put(b, board.difference(pierce), -0.0125, 0.0125, HY, 'yz')
    edge = op.buffer(0.012).difference(op).intersection(rect)                      # 12 mm bead on the arch edge, both faces
    put(b, edge, -0.02, 0.02, HY, 'yz')
    return b.mesh(f'Aivan86_arch_{int(L * 1000)}_{int(open_)}')
@cached
def a_rail86(L, shelf):
    """lower part of a closed bay between the post faces: frame + 30 x 30 timber grid @ 100 + handrail +0.95; shelf: 250 board at +0.55
    and a low solid board below it (vase display)"""
    b = MB(); y0, y1 = 0.09, L - 0.09
    b.box(-0.03, y0, 0.0, 0.03, y1, 0.14, HY, 0.004)                                           # sill on the deck
    if shelf:                                            # vase bays: solid board + 250 shelf, open above (the shelf is the rail)
        b.box(-0.015, y0, 0.14, 0.015, y1, 0.53, HY)
        b.box(-0.125, y0, 0.53, 0.125, y1, 0.555, HY, 0.006)
        return b.mesh(f'Aivan86_rail_{int(L * 1000)}_shelf')
    b.box(-0.045, y0, 0.9, 0.045, y1, 0.95, HY, 0.008)
    g = SBox(y0, 0.14, y1, 0.9); bars = []
    n = int((y1 - y0) / 0.1)
    for k in range(1, n + 1): yy = y0 + k * (y1 - y0) / (n + 1); bars.append(SBox(yy - 0.015, 0.14, yy + 0.015, 0.9))
    m_ = int((0.9 - 0.14) / 0.1)
    for k in range(1, m_ + 1): zz = 0.14 + k * (0.9 - 0.14) / (m_ + 1); bars.append(SBox(y0, zz - 0.015, y1, zz + 0.015))
    put(b, SUnion(bars).intersection(g), -0.015, 0.015, HY, 'yz')
    return b.mesh(f'Aivan86_rail_{int(L * 1000)}_grid')

for i_, y in enumerate(COLY): inst(a_post86(ZC), f'Khiva_column_{i_ + 1:02d}', (XA, y, 0.0), 0, 'Aivan')
nb_ = 0; SHELVES = []
for i_, (ya, yb) in enumerate(zip(COLY[:-1], COLY[1:])):
    L = round(yb - ya, 4); op_ = (ya, yb) in OPEN
    inst(a_archpanel86(L, op_), f'Khiva_arcade_head_{i_ + 1:02d}', (XA, ya, ZC), 0, 'Aivan')
    if not op_:
        nb_ += 1; sh_ = nb_ % 2 == 0
        inst(a_rail86(L, sh_), f'Khiva_arcade_bay_{i_ + 1:02d}', (XA, ya, 0.0), 0, 'Aivan')
        if sh_: SHELVES.append((ya, L))
mb = MB(); mb.box(XA - 0.07, COLY[0] - 0.12, ZC, XA + 0.07, COLY[-1] + 0.12, ZB, HY, 0.006)
inst(mb.mesh('Khiva_arcade_beam'), 'Khiva_arcade_beam', (0, 0, 0), 0, 'Aivan')
SETS = [('bottle', 'ribbed', 'tall'), ('globe', 'jar', 'bottle'), ('tall', 'globe', 'ribbed')]
nv_ = 0
RMAX = {k: max(r for r, z in v[0]) for k, v in VASES.items()}
for k_, (ya, L) in enumerate(SHELVES):                                  # pack by size between the shelf posts, 40 mm gaps
    kinds = SETS[k_ % len(SETS)]; lo, hi = ya + 0.09 + 0.03, ya + L - 0.09 - 0.03
    placed = []; y = lo
    for kd in kinds:
        r = RMAX[kd]
        if y + 2 * r > hi: break
        placed.append((kd, y + r)); y += 2 * r + 0.04
    sh = (hi - y + 0.04) / 2 if placed else 0
    for kd, yy in placed:
        nv_ += 1; inst(a_vase_tc(kd), f'Aivan_vase_{nv_}', (XA, yy + sh, 0.555), 0.4 * nv_, 'Aivan')
print('rev 8.6 aivan simplified: posts', len(COLY), 'shelves', len(SHELVES), 'vases', nv_)
