"""rev. 11.3 (owner):
  * aivan stairs: handrails removed; terracotta jugs (tall + medium) on both sides of each flight, on the floor by the bottom step
  * aivan + booth tables rebuilt as trestle tables (owner ref): 50 mm walnut top with the tile field, two solid supports centred
    under the short ends on sledge feet, a low stretcher (z 0.18) with wedged through-tenons — nothing at the corners, so the knees
    are free when you sit down; aivan table 40 mm narrower -> ~80 mm from each settee front to the table edge
  * lamps: the dome's cascade chandelier (pierced brass / copper globes on beaded chains under a pierced canopy) in a small
    version replaces the pierced lanterns on the aivan (one at the centre of each of the 7 ceiling coffers — symmetric to the
    ceiling), in the tents and the pendant clusters in the pergola zone
  * aivan frieze: the printed zigzag zardevor band with tassels -> carved walnut frieze board with a real chip-carved star band,
    moulded cap and bead"""
# ---------------------------------------------------------------- stairs: rails out, jugs in
_rm('stepsA_handrail', 'stepsB_handrail')
JUG = {h: a_jar91(h) for h in (0.8, 0.55, 0.38)}
def _free(me, loc, skip=()):
    o_ = inst(me, '_probe', loc, 0, 'Aivan'); bpy.context.view_layer.update(); lo_, hi_ = _bb(o_)
    t1 = _tree10(o_.data, o_.matrix_world); ok = True
    for o2 in bpy.data.objects:
        if o2 is o_ or o2.type != 'MESH' or 'foliage' in o2.data.name or o2.name.startswith(skip): continue
        l2, h2 = _bb(o2)
        if any(h2[i] < lo_[i] - 0.03 or l2[i] > hi_[i] + 0.03 for i in range(3)): continue
        if o2.name.startswith(('terrace_floor', 'Court_', 'zellige')) and l2[2] < TER + 0.01 and h2[2] < TER + 0.03: continue
        if t1.overlap(_tree10(o2.data, o2.matrix_world)): ok = False; break
    bpy.data.objects.remove(o_); return ok
njug = 0
for nm_, (x0, x1, y0, y1) in (('A', (3.3, 4.2, 15.55, 18.05)), ('B', (3.3, 4.2, 24.3, 25.8))):
    for side, yy in (('S', y0 - 0.26), ('N', y1 + 0.26)):
        sg = -1 if side == 'S' else 1
        for h, dx, dy in ((0.8, 3.95, 0.0), (0.55, 3.55, 0.02), (0.38, 4.35, 0.05)):
            for tr in range(6):                                                     # nudge outwards until clear
                loc = (dx, yy + sg * (dy + 0.05 * tr), TER)
                if _free(JUG[h], loc): inst(JUG[h], f'Stair{nm_}_jug_{side}_{int(h * 100)}', loc, 0.4 * tr, 'Aivan'); njug += 1; break
# ---------------------------------------------------------------- trestle tables
@cached
def a_trestle(L, Dp):
    b = MB(); Wd = XW['wd']
    b.box(-L / 2, -Dp / 2, 0.70, L / 2, Dp / 2, 0.75, Wd, 0.008)                               # 50 mm top
    b.box(-L / 2 + 0.06, -Dp / 2 + 0.06, 0.75, L / 2 - 0.06, Dp / 2 - 0.06, 0.752, MORTAR)
    n, mrows = int((L - 0.12) / 0.103), int((Dp - 0.12) / 0.103)
    for i in range(n):
        for j in range(mrows):
            x0 = -n * 0.103 / 2 + i * 0.103; y0 = -mrows * 0.103 / 2 + j * 0.103
            pat = ((i % 4) in (1, 2)) == ((j % 4) in (1, 2))
            b.box(x0, y0, 0.75, x0 + 0.1, y0 + 0.1, 0.758, TILE[0] if pat else (TILE[2] if (i + j) % 2 else TILE[1]), 0.002)
    xs = L / 2 - min(0.16, L * 0.2)
    for sx in (-1, 1):
        x = sx * xs
        b.box(x - 0.045, -Dp / 2 + 0.07, 0.64, x + 0.045, Dp / 2 - 0.07, 0.70, Wd, 0.008)          # cross bearer under the top
        b.box(x - 0.045, -0.06, 0.1, x + 0.045, 0.06, 0.64, Wd, 0.006)                          # solid support, centred
        b.box(x - 0.05, -Dp / 2 + 0.08, 0.0, x + 0.05, Dp / 2 - 0.08, 0.1, Wd, 0.03)              # sledge foot
        for sy in (-1, 1): b.box(x - 0.05, sy * (Dp / 2 - 0.08) - 0.012, 0.0, x + 0.05, sy * (Dp / 2 - 0.08) + 0.012, 0.012, m['brass'], 0.002)
    b.box(-xs + 0.045, -0.03, 0.18, xs - 0.045, 0.03, 0.26, Wd, 0.006)                        # stretcher
    for sx in (-1, 1):
        b.box(sx * (xs + 0.045), -0.022, 0.19, sx * (xs + 0.095), 0.022, 0.25, Wd, 0.004)        # through-tenon
        b.box(sx * (xs + 0.06) - 0.012, -0.03, 0.17, sx * (xs + 0.06) + 0.012, 0.03, 0.28, Wd, 0.003)  # wedge
    return b.mesh(f'Trestle_{int(L * 100)}x{int(Dp * 100)}')
ntt = 0
for o_ in [o for o in bpy.data.objects if o.type == 'MESH' and o.data.name.startswith('Teatable_')]:
    L_, D_ = [int(v) / 100 for v in o_.data.name.split('_')[1].split('.')[0].split('x')]
    if o_.name.startswith('Aivan'): D_ = round(D_ - 0.04, 2)
    o_.data = a_trestle(L_, D_); ntt += 1
# ---------------------------------------------------------------- small cascade chandeliers
def mini_cascade(name, cx, cy, ztop, zlow, coll_, Rc=0.2):
    b = MB()
    disc = SPt(cx, cy).buffer(Rc, 48)
    cut = [SPt(cx + 0.62 * Rc * math.cos(2 * math.pi * k / 8), cy + 0.62 * Rc * math.sin(2 * math.pi * k / 8)).buffer(0.12 * Rc, 16) for k in range(8)]
    put(b, disc.difference(SUnion(cut)), ztop - 0.012, ztop - 0.001, BRZ, 'xy')                  # pierced canopy plate
    put(b, SPt(cx, cy).buffer(Rc + 0.015, 48).difference(SPt(cx, cy).buffer(Rc - 0.02, 48)), ztop - 0.03, ztop - 0.001, BRZ, 'xy')
    span = ztop - 0.03 - zlow
    rings = [(0.0, 1, 0.1), (Rc * 0.75, 6, 0.07)]
    for ri, (rr, n, R) in enumerate(rings):
        for k in range(n):
            a = 2 * math.pi * k / n; x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            gt = zlow + 0.2 + 1.87 * R + (0.0 if ri == 0 else (0.12 if k % 2 else 0.24)) * span / 0.9
            gt = min(gt, ztop - 0.08)
            _chain(b, x, y, ztop - 0.03, gt); _globe(b, x, y, gt, R * (1.0 if k % 2 == 0 else 0.86), PERF[(k + ri) % 2])
    inst(b.mesh(name), name, (0, 0, 0), 0, coll_)
_rm('Aivan_lantern', 'Tent1_lantern', 'Tent2_lantern', 'Pendant_cluster')
for o_ in [o for o in bpy.data.objects if o.name.startswith('Rod') and o.users_collection and o.users_collection[0].name in ('Aivan', 'Tapchans_tent')]:
    bpy.data.objects.remove(o_)
NC_, CY0_, CY1_, CXc = 7, 15.3, 28.49, (0.34 + 3.11) / 2
nch = 0
for k in range(NC_):
    cy_ = CY0_ + (CY1_ - CY0_) * (k + 0.5) / NC_
    mini_cascade(f'Aivan_chandelier_{k + 1}', CXc, cy_, 3.02, 2.08, 'Aivan'); nch += 1
for nm_, (x, y, zt, zl) in {'Tent1_chandelier_1': (2.95, 31.9, 1.8, 1.2), 'Tent1_chandelier_2': (2.95, 32.8, 1.8, 1.2),
                            'Tent2_chandelier_1': (2.95, 34.75, 1.8, 1.2), 'Tent2_chandelier_2': (2.95, 35.75, 1.8, 1.2)}.items():
    b_ = MB(); b_.cyl(x, y, zt, zt + 0.1, 0.008, BRZ, 8); inst(b_.mesh(nm_ + '_rod'), nm_ + '_rod', (0, 0, 0), 0, 'Tapchans_tent')
    mini_cascade(nm_, x, y, zt, zl, 'Tapchans_tent', 0.15); nch += 1
for nm_, (x, y, zt, zl) in {'Pergola_chandelier_1': (2.01, 5.74, 3.4, 2.05), 'Pergola_chandelier_2': (6.93, 3.75, 3.0, 1.75), 'Pergola_chandelier_3': (6.48, 5.54, 3.0, 1.75)}.items():
    mini_cascade(nm_, x, y, zt, zl, 'Lights'); nch += 1
# ---------------------------------------------------------------- carved frieze instead of the printed zardevor
nfr = 0
for o_ in [o for o in bpy.data.objects if o.name.startswith('Zardevor_')]:
    lo_, hi_ = _bb(o_); bpy.data.objects.remove(o_)
    b = MB(); y0, y1 = lo_[1], hi_[1]
    b.box(0.16, y0, 2.28, 0.205, y1, 2.70, mat('carved_t2', (0.2, 0.12, 0.07), rough=0.5), 0.004)   # board (gets the real carving)
    b.box(0.16, y0 - 0.01, 2.70, 0.235, y1 + 0.01, 2.75, XW['wd'], 0.008)                           # moulded cap
    b.box(0.16, y0 - 0.005, 2.24, 0.222, y1 + 0.005, 2.28, XW['wd'], 0.006)                         # bead
    b.box(0.205, y0 + 0.02, 2.255, 0.225, y1 - 0.02, 2.265, m['brass'])                             # brass inlay line
    inst(b.mesh(f'Aivan_frieze_{nfr + 1}'), f'Aivan_frieze_{nfr + 1}', (0, 0, 0), 0, 'Aivan'); nfr += 1
PAT.clear(); PAT['carved_t2'] = (WDARK, 0.006, _stars_d(0.14, 0.055, XW['wd']), XW['wd'], 0.1); SIDES.clear(); SIDES.add('carved_t2')
HORIZ.clear(); realize_all(skip=('Booth',))
print('rev 11.3 jugs', njug, 'trestle tables', ntt, 'chandeliers', nch, 'friezes', nfr)
