"""rev. 9.5 (owner ref: street benches): the six street-side benches become built-in lime-plaster benches
  * body + 50 mm seat slab with a 40 mm overhang, warm LED strip hidden under the lip; back wall in the same textured plaster
    with a relief frieze (alternating triangles + a row of dots), rounded coping
  * kilim seat pads folded over the front edge (real fold), one per 620 mm seat
  * round walnut tables d 520 at +0.72 on 40 mm black steel J-stems fixed into the bench face (no legs on the sidewalk)
  * terrazzo bell pendants over the tables where the roof eave covers the bench"""
from shapely.geometry import Point as _Pt
from shapely.ops import unary_union as _un
_rm('Street_bench_stone', 'sback', 'sbench')
LIME = mat('lime_render', (0.86, 0.83, 0.77), rough=0.95, bump=0.9, noise_var=0.035)
TERZ = mat('terrazzo_shade', (0.88, 0.85, 0.8), rough=0.4, bump=0.2, noise_var=0.12)
LEDW = mat('led_warm_strip', (1, 0.85, 0.6), emit=(1.0, 0.75, 0.45), strength=5.0)
BLK = mat('steel_black_satin', (0.03, 0.03, 0.03), rough=0.35, metal=0.7)
KIL = [X.get('kilim', m['white']), X.get('kilim2', m['white'])]
ZS = -1.17                                                     # sidewalk top
ROOF_ = _un([SPoly(p) for p in D['roof']]).buffer(0)
backs = [bbox(it['poly'][0]) for it in D['items'] if it['kind'] == 'sback']
nseg = 0
for it in D['items']:
    if it['kind'] != 'sbench': continue
    p = it['poly'][0]; (a0, b0), (a1, b1) = p[0], p[3]                   # west (back) edge: p0 -> p3
    L = math.hypot(a1 - a0, b1 - b0); ang = math.atan2(b1 - b0, a1 - a0)
    W = abs((p[1][0] - p[0][0]) * math.sin(ang) - (p[1][1] - p[0][1]) * math.cos(ang))    # depth perpendicular to the back
    hasback = any(abs(bx1 - min(a0, a1)) < 0.25 or abs(bx1 - a0) < 0.05 for bx0, by0, bx1, by1 in backs)
    U0 = 0.15 if abs(b0 - 18.75) < 0.05 else 0.07; U1 = L - 0.07          # ends kept clear of the planter band (its edges are not square to the bench)
    mb = MB()
    mb.box(U0, -W + 0.04, 0.0, U1, 0.0, 0.40, LIME, 0.01)                                          # body
    mb.box(U0, -W, 0.40, U1, 0.0, 0.45, LIME, 0.012)                                                # seat slab, 40 mm lip
    mb.box(U0 + 0.02, -W + 0.03, 0.385, U1 - 0.02, -W + 0.045, 0.40, LEDW)                                # LED under the lip
    if hasback:
        mb.box(U0, 0.005, 0.0, U1, 0.145, 0.932, LIME, 0.008)
        mb.rod((U0, 0.075, 0.932), (U1, 0.075, 0.932), 0.068, LIME, 16)                             # rounded coping, top at +1.0 (planting on it)
        n = int(L / 0.12)
        for k in range(n):                                                                         # relief frieze, 12 mm proud
            x = (L - n * 0.12) / 2 + k * 0.12
            if k % 2 == 0: tri = [(x, 0.72), (x + 0.12, 0.72), (x + 0.06, 0.82)]
            else: tri = [(x, 0.82), (x + 0.12, 0.82), (x + 0.06, 0.72)]
            mb.extrude(tri, -0.012, 0.0, LIME, 'xz')
        for k in range(int(L / 0.06)):
            x = 0.03 + k * 0.06
            mb.box(x - 0.01, -0.01, 0.86, x + 0.01, 0.0, 0.88, LIME, 0.003)                         # row of dots
    inst(mb.mesh(f'Street_bench_plaster_{nseg}'), f'Street_bench_plaster_{nseg}', (a0, b0, ZS), ang, 'Street_facade')
    # kilim pads + tables + pendants
    mb = MB(); ns = max(1, int((L - 0.1) / 0.62)); x0 = (L - ns * 0.62) / 2
    for k in range(ns):
        xa, xb_ = x0 + k * 0.62 + 0.05, x0 + (k + 1) * 0.62 - 0.05; mm = KIL[k % 2]
        mb.box(xa, -W + 0.005, 0.45, xb_, -0.05, 0.51, mm, 0.02)                                    # pad on the seat
        mb.box(xa, -W - 0.045, 0.22, xb_, -W - 0.005, 0.47, mm, 0.012)                              # flap folded over the edge
        mb.rod((xa, -W - 0.02, 0.48), (xb_, -W - 0.02, 0.48), 0.03, mm, 12)                         # the fold
    inst(mb.mesh(f'Street_bench_pads_{nseg}'), f'Street_bench_pads_{nseg}', (a0, b0, ZS), ang, 'Street_facade')
    mb = MB(); tabs = [x0 + k * 0.62 for k in range(1, ns, 2)] or [L / 2]
    c_, s_ = math.cos(ang), math.sin(ang)
    for xt in tabs:
        yT = -W - 0.33
        _curve(mb, [(xt, yT, 0.70), (xt, yT, 0.22), (xt, yT + 0.04, 0.12), (xt, yT + 0.16, 0.09), (xt, -W + 0.03, 0.09)], 0.02, 0.02, BLK, 8)
        mb.box(xt - 0.06, -W + 0.03, 0.05, xt + 0.06, -W + 0.04, 0.13, BLK)                         # wall plate in the bench face
        mb.cyl(xt, yT, 0.70, 0.72, 0.05, BLK, 16)
        mb.cyl(xt, yT, 0.72, 0.75, 0.26, XW['wd'], 40); mb.ring(xt, yT, 0.72, [(0.255, 0.0), (0.265, 0.0), (0.265, 0.03), (0.255, 0.03)], BLK, 40)
        wx, wy = a0 + xt * c_ - yT * s_, b0 + xt * s_ + yT * c_
        if ROOF_.contains(_Pt(wx, wy)):                                                               # terrazzo pendant over the table
            zr = top(wx) - 0.05 - ZS
            mb.lathe(xt, yT, 1.95, [(0.0, 0.0), (0.085, 0.0), (0.085, 0.13), (0.06, 0.17), (0.02, 0.19), (0.0, 0.19)], TERZ, 24)
            mb.cyl(xt, yT, 1.95, 1.952, 0.08, LEDW, 24)
            mb.rod((xt, yT, 2.14), (xt, yT, zr), 0.003, BLK, 6)
    inst(mb.mesh(f'Street_bench_tables_{nseg}'), f'Street_bench_tables_{nseg}', (a0, b0, ZS), ang, 'Street_facade')
    nseg += 1
print('rev 9.5 street benches ok', nseg)
# a vine that stood on a now-trimmed wall end is dropped
WALLS_ = []
for it in D['items']:
    if it['kind'] == 'sback':
        q_ = SPoly(it['poly'][0]); x0q, y0q, x1q, y1q = q_.bounds
        WALLS_.append(q_.intersection(SB_(x0q - 1, y0q + 0.16, x1q + 1, y1q - 0.16)).buffer(0.03))
bpy.context.view_layer.update()
for o_ in [o for o in bpy.data.objects if o.name.startswith(('Jasmine', 'Bougainvillea'))]:
    vs_ = [o_.matrix_world @ v.co for v in o_.data.vertices]; zmin = min(v.z for v in vs_)
    if abs(zmin - (ZS + 1.0)) > 0.01: continue
    base = [v for v in vs_ if v.z < zmin + 0.01]
    if not any(any(w.contains(_Pt(v.x, v.y)) for w in WALLS_) for v in base): bpy.data.objects.remove(o_)        # its wall end is gone
