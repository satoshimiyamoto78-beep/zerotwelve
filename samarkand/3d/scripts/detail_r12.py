"""Samarkand R12 — DETAIL PASS v2 (clean modelling). Executed inside base3d_r12.py's namespace after the base items.
Uses kit.py (closed-shell mesh builder) and assets_r12.py (asset library). Every furniture piece / fixture is its own
object (linked instance of a shared mesh), named, with its origin at its base; parts meet flush; nothing penetrates.
Zone-unique pieces (corridor ceiling, firewood wall, hood, portal arch...) are built with the same closed primitives."""
import os, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
TEX2 = os.path.join(HERE, 'tex2')
for f_ in ('kit.py', 'assets_r12.py'): exec(open(os.path.join(HERE, f_)).read())
RD = random.Random(42)

# ---------------- materials ----------------
def tex2(name, file, size, rough=0.6, bump=0.25, coat=0.0):
    return bl2.tile(name, os.path.join(TEX2, file), size, rough=rough, bump=bump, coat=coat)
def uvmat(name, file, rough=0.8, sheen=0.5):
    if name in bl._mats: return bl._mats[name]
    mm = bpy.data.materials.new(name); N = mm.node_tree.nodes; Lk = mm.node_tree.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = rough; b.inputs['Sheen Weight'].default_value = sheen
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(TEX2, file), check_existing=True)
    uv = N.new('ShaderNodeUVMap'); uv.uv_map = 'UVMap'; Lk.new(uv.outputs['UV'], it.inputs['Vector']); Lk.new(it.outputs['Color'], b.inputs['Base Color'])
    bl._mats[name] = mm; return mm
X = dict(
    carved=tex2('carved_t', 'carved.png', 0.9, rough=0.55, bump=0.5),
    kilim=bl2.fabric('kilim_f', os.path.join(TEX2, 'kilim.png'), 0.6),
    velvet=bl2.fabric('velvet_f', os.path.join(TEX2, 'velvet.png'), 0.8),
    tent=bl2.fabric('tent_f', os.path.join(TEX2, 'tentstripe.png'), 1.2),
    copper=tex2('copper_t', 'copper.png', 0.5, rough=0.3, bump=0.4),
    gajbrick=tex2('gajbrick_t', 'gajbrick.png', 1.4, rough=0.85, bump=0.6),
    dometile=tex2('dometile_t', 'dometile.png', 0.7, rough=0.55, bump=0.5),
    lotus=mat('lotus', (0.16, 0.42, 0.14), rough=0.5), pinkfl=mat('pinkfl', (0.95, 0.55, 0.65), rough=0.5),
    meat=mat('meat', (0.42, 0.16, 0.08), rough=0.6), ember=mat('ember', (1, .3, .05), emit=(1.0, 0.28, 0.04), strength=6.0),
    lampglow=mat('lampglow', (1, .75, .45), emit=(1.0, 0.62, 0.30), strength=8.0),
)
for k in ('carpet1', 'carpet2', 'carpet3', 'carpet4'): X[k] = uvmat(k + '_uv', k + '.png')
for th in ('sogd', 'sasan', 'saman', 'khorezm', 'timur', 'shahr', 'margil', 'pamir'): X['ep_' + th] = uvmat('ep_' + th + '_uv', 'ep_' + th + '.png', rough=0.5, sheen=0.1)
for mm, sz in ((m['ikat'], 0.5), (m['suzani'], 0.6), (m['jali'], 0.5), (m['majolica'], 0.6), (m['band'], 1.2), (m['girih'], 0.6), (m['floor'], 1.2),
               (X['carved'], 0.9), (X['kilim'], 0.6), (X['velvet'], 0.8), (X['tent'], 1.2), (X['copper'], 0.5), (X['gajbrick'], 1.4), (X['dometile'], 0.7)):
    register_uv_size(mm, sz)
def ceil_at(x, y):
    """underside of whatever is overhead: balcony slab (x < 1.5) or the roof sandwich panel"""
    return 3.85 if x < 1.5 else top(x) - 0.05

# =============== 1. THEMED BOOTHS: partitions (stepped), modules, lanterns ===============
BO = D['booths']
for k, (y0, y1, xw, xe, th) in enumerate(BO):
    L = (BO[k - 1][3] if k > 0 else xe) - xw                     # south partition reaches the back of the booth before it
    inst(a_partition(round(L, 3)), f'Booth{k + 1}_partition_S', (xw, y0, TER), 0, 'Booths')
    inst(a_booth(th), f'Booth{k + 1}_{th}', (xw, y0, TER), 0, 'Booths')
    lantern_at(xw + 0.65, (y0 + y1) / 2, TER + 1.75, 0.9, TER + 2.2, 'Booths', f'Booth{k + 1}_lantern')
y0, y1, xw, xe, th = BO[-1]
inst(a_partition(1.3), f'Booth{len(BO)}_partition_N', (xw, y1, TER), 0, 'Booths')

# =============== 2. CHAIRS / TABLES / TABLEWARE (one object per piece) ===============
ROT_BACK = {'s': 0.0, 'n': math.pi, 'e': math.pi / 2, 'w': -math.pi / 2}
nc = nt = 0
for it in D['items']:
    if it['kind'] == 'chair':
        for r in it['poly']:
            base = 0.0 if on_plat(r) else TER; x0, y0, x1, y1 = bbox(r)
            nc += 1; inst(a_chair(), f'Chair_{nc:03d}', ((x0 + x1) / 2, (y0 + y1) / 2, base), ROT_BACK[it.get('back', 'n')], 'Furniture')
    if it['kind'] == 'table':
        for r in it['poly']:
            base = 0.0 if on_plat(r) else TER; x0, y0, x1, y1 = bbox(r); n = it.get('mods', 1); rz = 0.0 if it.get('axis', 'x') == 'x' else math.pi / 2
            nt += 1; c_ = ((x0 + x1) / 2, (y0 + y1) / 2, base)
            inst(a_table(n), f'Table_{nt:03d}', c_, rz, 'Furniture'); inst(a_tableware(n), f'Tableware_{nt:03d}', c_, rz, 'Furniture')

# =============== 3. AIVAN SEDIR BOOTHS: back cushions, wall carpets, tableware, lanterns ===============
scr = [bbox(it['poly'][0]) for it in D['items'] if it['kind'] == 'ascreen']
ats = [bbox(it['poly'][0]) for it in D['items'] if it['kind'] == 'atable']
for i_, it in enumerate([it for it in D['items'] if it['kind'] == 'abench']):
    x0, y0, x1, y1 = bbox(it['poly'][0]); cy = (y0 + y1) / 2
    tb = min(ats, key=lambda b_: abs((b_[1] + b_[3]) / 2 - cy)); away = -1 if (tb[1] + tb[3]) / 2 > cy else 1
    yo = y0 if away < 0 else y1                                        # outer edge of the bench
    for sx0, sy0, sx1, sy1 in scr:                                     # a screen over the bench edge: start at its face
        if sx0 < x1 and sx1 > x0 and sy0 - 1e-6 <= yo <= sy1 + 1e-6: yo = sy1 if away < 0 else sy0
    yc = yo - away * 0.07; cx0, cx1 = x0 + 0.17, x1 - 0.05                 # clear of the wall carpet (x 0.14..0.152)
    inst(a_cushion(round(cx1 - cx0, 3), 0.14, 0.42, 'kilim'), f'Aivan_backcushion_{i_ + 1}', ((cx0 + cx1) / 2, yc, 0.45), 0, 'Aivan')
for i_, (x0, y0, x1, y1) in enumerate(ats):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    mb = MB(); mb.picture_box(0.0, -0.85, 0.75, 0.012, 0.85, 2.25, X['carpet%d' % (1 + i_ % 4)], '+x'); mb.box(0.0, -0.9, 2.25, 0.03, 0.9, 2.29, m['brass'])
    inst(mb.mesh(f'Aivan_wallcarpet_{i_ + 1}'), f'Aivan_wallcarpet_{i_ + 1}', (0.14, cy, 0.0), 0, 'Aivan')
    inst(a_tableware(2), f'Aivan_tableware_{i_ + 1}', (cx, cy, 0.0), 0.0 if (x1 - x0) >= (y1 - y0) else math.pi / 2, 'Aivan')
    lantern_at(cx, cy, 1.95, 1.0, ceil_at(cx, cy), 'Aivan', f'Aivan_lantern_{i_ + 1}')

# =============== 4. FLYING CARPETS under the roof ===============
ZONES = [(2.6, 8.6, 5.3, 9.3), (8.0, 11.0, 10.4, 14.6), (3.6, 7.8, 22.9, 24.8), (4.4, 7.6, 30.2, 34.0), (1.7, 3.2, 15.6, 28.2)]
def clear_of_domes(x, y, pad): return all(math.hypot(x - d['c'][0], y - d['c'][1]) > d['r'] + pad for d in D['domes'])
nfc = 0
for zx0, zx1, zy0, zy1 in ZONES:
    y = zy0 + 1.0
    while y < zy1 - 0.9:
        x = zx0 + 0.7
        while x < zx1 - 0.6:
            if clear_of_domes(x, y, 1.0):
                rot = math.pi / 2 if (zx1 - zx0) > 2.5 and nfc % 2 else 0.0; z = top(x + 1.0) - 0.8 + RD.uniform(-0.06, 0.04)
                nfc += 1; inst(a_flycarpet(1 + nfc % 4), f'Flying_carpet_{nfc:02d}', (x, y, z), rot, 'Carpet_ceiling')
                c_, s_ = math.cos(rot), math.sin(rot)
                for u, v in ((-0.55, -0.85), (0.55, -0.85), (0.55, 0.85), (-0.55, 0.85)):
                    px, py = x + u * c_ - v * s_, y + u * s_ + v * c_; pz = z + 0.05 * math.sin(v / 1.9 * 2 * math.pi) + 0.013
                    inst(a_rod(), 'Rod_carpet', (px, py, pz), 0, 'Carpet_ceiling', scale=(0.7, 0.7, ceil_at(px, py) - pz))
            x += 1.6
        y += 2.3
print('flying carpets', nfc)

# =============== 5. MAJLIS TENTS ===============
for i_, (tx0, ty0, tx1, ty1) in enumerate(D.get('tents', [D['tent']])):
    w, d = round(tx1 - tx0, 3), round(ty1 - ty0, 3)
    inst(a_tent(w, d), f'Tent_{i_ + 1}', (tx0, ty0, TER), 0, 'Tapchans_tent')
    sofa_top = TER + 0.42
    inst(a_cushion(0.13, round(d - 0.02, 3), 0.42, 'kilim'), f'Tent{i_ + 1}_cushion_W', (tx0 + 0.065, ty0 + d / 2, sofa_top), 0, 'Tapchans_tent')
    for yy, nm in ((ty0 + 0.065, 'S'), (ty1 - 0.065, 'N')):
        inst(a_cushion(round(w - 0.25 - 0.65 - 0.02, 3), 0.13, 0.42, 'kilim'), f'Tent{i_ + 1}_cushion_{nm}', (tx0 + 0.65 + (w - 0.25 - 0.65) / 2, yy, sofa_top), 0, 'Tapchans_tent')
    for it in D['items']:
        if it['kind'] == 'otable':
            ox, oy = cen(it['poly'][0])
            if tx0 <= ox <= tx1 and ty0 <= oy <= ty1:
                if 'Tent_tray' not in ASSETS:
                    mb = MB(); mb.cyl(0, 0, 0, 0.02, 0.33, m['brass'], 32); _plate(mb, -0.12, 0.0, 0.02); _piala(mb, 0.15, 0.08, 0.02); _piala(mb, 0.15, -0.1, 0.02)
                    ASSETS['Tent_tray'] = mb.mesh('Tent_tray')
                inst(ASSETS['Tent_tray'], f'Tent{i_ + 1}_tray', (ox, oy, TER + 0.465), 0, 'Tapchans_tent')
    for yy in (ty0 + 0.9, ty1 - 0.9): lantern_at((tx0 + tx1) / 2 + 0.2, yy, TER + 1.8, 0.9, TER + 2.25, 'Tapchans_tent', f'Tent{i_ + 1}_lantern')

# =============== 6. TAPCHAN ===============
for y0 in D['tap']:
    inst(a_tapchan_rail(2.0, 2.2), 'Tapchan_railing', (2.55, y0, TER + 0.45), 0, 'Tapchans_tent')
    inst(a_bolster(1.9, 0.09, 'ikat'), 'Tapchan_bolster', (2.55 + 0.18, y0 + 1.1, TER + 0.57 + 0.09), 0, 'Tapchans_tent')
    mb = MB(); mb.picture_box(-0.55, -0.45, 0, 0.55, 0.45, 0.003, X['carpet3'], '+z')
    for px, py in ((-0.3, -0.25), (-0.3, 0.25), (0.3, -0.25), (0.3, 0.25)): _plate(mb, px, py, 0.003)
    mb.lathe(0, 0, 0.003, [(0.0, 0), (0.12, 0), (0.17, 0.03), (0.18, 0.05), (0.0, 0.035)], m['majolica'], 32)
    inst(mb.mesh('Dastarkhan_set'), 'Tapchan_dastarkhan', (3.8, y0 + 1.1, TER + 0.78), 0, 'Tapchans_tent')

# =============== 7. CORRIDOR: arches, sagging velvet ceiling, museum niches, khum jars ===============
e0, e1 = D['ent']; t0, t1 = D['tun']; ya, yb = e0 + 0.08, e1 - 0.08; Wc = round(yb - ya, 3)     # curtain inner faces
xs = [t0 + 0.2 + 0.9 * i for i in range(int((t1 - t0 - 0.3) / 0.9) + 1)]
for i_, x in enumerate(xs): inst(a_corr_arch(Wc), f'Corridor_arch_{i_ + 1}', (x, ya, TER), 0, 'Corridor')
mb = MB()
for xa, xb2 in zip(xs[:-1], xs[1:]):
    rows = []
    for j in range(9):
        y = ya + Wc * j / 8; zrow = []
        for c in range(5):
            xx = xa + 0.09 + (xb2 - xa - 0.1) * c / 4
            zrow.append((xx, y, TER + 2.74 - 0.26 * math.sin(math.pi * j / 8) - 0.1 * math.sin(math.pi * c / 4)))
        rows.append(zrow)
    mb.sheet(rows, X['velvet'], 0.006, picture=False)
inst(mb.mesh('Corridor_velvet_ceiling'), 'Corridor_velvet_ceiling', (0, 0, 0), 0, 'Corridor')
nn = 0
for xa, xb2 in zip(xs[:-1], xs[1:]):
    xm = (xa + 0.08 + xb2) / 2
    for yw, rz in ((ya, 0.0), (yb, math.pi)):
        nn += 1; inst(a_niche(), f'Corridor_niche_{nn}', (xm, yw, TER + 0.9), rz, 'Corridor')
        sg = 1 if rz == 0 else -1
        inst(a_jar(0), f'Corridor_niche_{nn}_jar', (xm - 0.12, yw + sg * 0.13, TER + 0.95), 0, 'Corridor')
        inst(a_jar(1), f'Corridor_niche_{nn}_jar2', (xm + 0.12, yw + sg * 0.13, TER + 1.315), 0, 'Corridor')
for i_, (xx, yy) in enumerate(((t1 - 0.35, ya + 0.3), (t1 - 0.35, yb - 0.3))): inst(a_khum(), f'Corridor_khum_{i_ + 1}', (xx, yy, TER), 0, 'Corridor')

# =============== 8. MANGAL ===============
BX0, BX1, BY0, BY1 = D['bbq']
for it in D['items']:
    k = it['kind']
    if k == 'tandoorblock':
        x0, y0, x1, y1 = bbox(it['poly'][0]); mb = MB()
        mb.lathe(0, 0, 0, [(0.0, 0), (0.44, 0), (0.46, 0.1), (0.43, 0.45), (0.3, 0.62), (0.24, 0.66), (0.0, 0.66)], X['copper'], 32)
        mb.ring(0, 0, 0.66, [(0.17, 0), (0.24, 0), (0.24, 0.03), (0.17, 0.03)], m['brass'], 32)
        inst(mb.mesh('Tandoor_copper'), 'Tandoor_copper', ((x0 + x1) / 2, (y0 + y1) / 2, TER + 0.85), 0, 'Mangal')
    if k == 'kazanblock':
        x0, y0, x1, y1 = bbox(it['poly'][0]); mb = MB()
        mb.lathe(0, 0, 0, [(0.0, 0), (0.15, 0), (0.36, 0.18), (0.4, 0.3), (0.42, 0.32), (0.0, 0.32)], m['black'], 32)
        inst(mb.mesh('Kazan'), 'Kazan', ((x0 + x1) / 2, (y0 + y1) / 2, TER + 0.7), 0, 'Mangal')
    if k == 'mangal':
        x0, y0, x1, y1 = bbox(it['poly'][0]); mb = MB()
        mb.box(x0 + 0.05, y0 + 0.05, TER + 0.85, x1 - 0.05, y1 - 0.05, TER + 0.87, X['ember'])
        for j in range(12):
            yy = y0 + 0.12 + j * (y1 - y0 - 0.24) / 11
            mb.rod((x0 + 0.02, yy, TER + 0.904), (x1 + 0.08, yy, TER + 0.904), 0.004, m['steel'], 6)
            for kk in range(4): mb.box(x0 + 0.08 + kk * 0.1, yy - 0.02, TER + 0.908, x0 + 0.14 + kk * 0.1, yy + 0.02, TER + 0.95, X['meat'])
        inst(mb.mesh('Mangal_skewers'), 'Mangal_skewers', (0, 0, 0), 0, 'Mangal')
    if k == 'woodstack':
        x0, y0, x1, y1 = bbox(it['poly'][0]); mb = MB(); WD = m['walnut']; r = 0.0625
        mb.box(x0, y0, TER, x1, y1, TER + 0.08, WD, 0.003); mb.box(x0, y0, TER + 2.0, x1, y1, TER + 2.08, WD, 0.003)
        mb.box(x0, y0, TER + 0.08, x1, y0 + 0.06, TER + 2.0, WD, 0.003); mb.box(x0, y1 - 0.06, TER + 0.08, x1, y1, TER + 2.0, WD, 0.003)
        row = 0; zz = TER + 0.08 + r
        while zz + r <= TER + 2.0 + 1e-6:
            yy = y0 + 0.06 + r + (r if row % 2 else 0)
            while yy + r <= y1 - 0.06 + 1e-6: mb.rod((x0 + 0.01, yy, zz), (x1 - 0.01, yy, zz), r - 0.001, m['oak'], 8); yy += 2 * r
            zz += r * math.sqrt(3); row += 1
        inst(mb.mesh('Firewood_wall'), 'Firewood_wall', (0, 0, 0), 0, 'Mangal')
    if k == 'hood':
        x0, y0, x1, y1 = bbox(it['poly'][0]); x1 = min(x1, BX1 - 0.15); hx, hy = (x0 + x1) / 2, (y0 + y1) / 2; zb = TER + 2.0; mb = MB()   # stop at the fire wall
        mb.box(x0, y0, zb - 0.12, x1, y1, zb, m['steel'], 0.003)
        vb = [mb.bm.verts.new(p) for p in ((x0, y0, zb), (x1, y0, zb), (x1, y1, zb), (x0, y1, zb))]
        vt = [mb.bm.verts.new(p) for p in ((hx - 0.2, hy - 0.2, TER + 2.45), (hx + 0.2, hy - 0.2, TER + 2.45), (hx + 0.2, hy + 0.2, TER + 2.45), (hx - 0.2, hy + 0.2, TER + 2.45))]
        fs = [mb.bm.faces.new(list(reversed(vb))), mb.bm.faces.new(vt)] + [mb.bm.faces.new((vb[i], vb[(i + 1) % 4], vt[(i + 1) % 4], vt[i])) for i in range(4)]
        ii = mb.mi(m['black'])
        for f in fs: f.material_index = ii
        bmesh.ops.recalc_face_normals(mb.bm, faces=fs)
        mb.box(x0, y0 - 0.02, zb - 0.32, x1, y0, zb - 0.12, m['majolica'])
        inst(mb.mesh('Mangal_hood'), 'Mangal_hood', (0, 0, 0), 0, 'Mangal')
    if k == 'pass':
        x0, y0, x1, y1 = bbox(it['poly'][0])
        if 'Heat_lamp' not in ASSETS:
            mb = MB(); mb.lathe(0, 0, 0, [(0.07, 0), (0.1, 0.0), (0.06, 0.12), (0.0, 0.14)], m['black'], 16)
            ASSETS['Heat_lamp'] = mb.mesh('Heat_lamp')
        for i_, xx in enumerate([x0 + 0.4 + 0.6 * i for i in range(int((x1 - x0) / 0.6))]):
            yy = (y0 + y1) / 2; inst(ASSETS['Heat_lamp'], f'Heat_lamp_{i_ + 1}', (xx, yy, TER + 1.75), 0, 'Mangal')
            inst(a_rod(), 'Rod_lamp', (xx, yy, TER + 1.89), 0, 'Mangal', scale=(1, 1, ceil_at(xx, yy) - TER - 1.89))

# =============== 9. HAUZ: lotus + jet; ARYK majolica edges ===============
hx, hy = D['hzc']; mb = MB()
for k in range(7):
    a = k * 0.9 + 0.3; r_ = 0.18 + 0.05 * (k % 3); px, py = r_ * math.cos(a), r_ * math.sin(a)
    mb.cyl(px, py, 0, 0.01, 0.06 + 0.012 * (k % 2), X['lotus'], 16)
    if k % 3 == 0: mb.lathe(px, py, 0.01, [(0.0, 0), (0.035, 0.0), (0.045, 0.035), (0.0, 0.045)], X['pinkfl'], 10)
mb.lathe(0, 0, 0, [(0.0, 0), (0.05, 0), (0.015, 0.45), (0.0, 0.5)], m['glass'], 12)
inst(mb.mesh('Hauz_lotus_jet'), 'Hauz_lotus_jet', (hx, hy, TER + 0.36), 0, 'Fountain')
for it in D['items']:
    if it['kind'] == 'aryk':
        x0, y0, x1, y1 = bbox(it['poly'][0]); y0 = max(y0, D.get('hauz_rim_y1', y0)); mb = MB()
        mb.box(x0 - 0.08, y0, TER, x0, y1, TER + 0.06, m['majolica'], 0.003); mb.box(x1, y0, TER, x1 + 0.08, y1, TER + 0.06, m['majolica'], 0.003)
        inst(mb.mesh('Aryk_edges'), 'Aryk_edges', (0, 0, 0), 0, 'Fountain')

# =============== 10. BUKHARA DOME + KHIVA GATE ===============
if 'rot' in D:
    rx, ry, rr_ = D['rot']
    inst(a_rotunda(), 'Bukhara_rotunda', (rx, ry, TER + 0.15), 0, 'Bukhara_dome')
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; inst(a_vitrine(), f'Bukhara_vitrine_{k + 1}', (rx + 0.7 * math.cos(a), ry + 0.7 * math.sin(a), TER + 0.15), a, 'Bukhara_dome')
    g0, g1 = D['gate']
    inst(a_gate(round(g1 - g0, 3)), 'Khiva_gate', (g0 - 0.25, 36.425, TER), 0, 'North_gate')

# =============== 11. LANTERNS from the plan (gate etc.; booths, aivan and tents have their own) ===============
nl = 0
for it in D['items']:
    if it['kind'] != 'lantern': continue
    for r in it['poly']:
        cx, cy = cen(r); base = 0.0 if on_plat(r) else TER
        if any(y0 <= cy <= y1 and xw - 0.1 <= cx <= xe for y0, y1, xw, xe, _ in BO): continue
        if any(abs(cy - (a0[1] + a0[3]) / 2) < 0.6 and a0[0] - 0.3 < cx < a0[2] + 0.3 for a0 in ats): continue
        if cy > 36.2: continue                                         # the Khiva gate carries bells instead
        nl += 1
        ceil = ceil_at(cx, cy)
        lantern_at(cx, cy, min(base + 2.0, ceil - 0.5), 1.0, ceil, 'Lights', f'Lantern_{nl:02d}')

# =============== 12. STREET PISHTAQ ARCH, tree uplights, kids chests ===============
e0, e1 = D['ent']; xs_ = xb((e0 + e1) / 2) - 0.75; mb = MB()
for poly in spandrel_polys((e0 + e1) / 2, e1 - e0, SID + 2.55, SID + 3.2, SID + 3.4): mb.extrude(poly, xs_ - 0.15, xs_ + 0.15, m['majolica'], 'yz')
mb.box(xs_ - 0.17, e0 - 0.7, SID + 3.4, xs_ + 0.17, e1 + 0.7, SID + 3.62, m['band'], 0.004)
inst(mb.mesh('Street_pishtaq_arch'), 'Street_pishtaq_arch', (0, 0, 0), 0, 'Street_facade')
mb = MB(); mb.cyl(0, 0, 0, 0.05, 0.07, m['steel'], 16); mb.cyl(0, 0, 0.05, 0.055, 0.06, X['lampglow'], 16); up = mb.mesh('Uplight')
for x, y in D['trees']:
    for a in (0.5, 2.6, 4.7): inst(up, 'Tree_uplight', (x + 0.75 * math.cos(a), y + 0.75 * math.sin(a), TER + 0.08), 0, 'Lights')
for i_, ((x0, y0), mm) in enumerate((((-6.6, 1.8), m['majolica']), ((-5.6, 1.8), X['carved']), ((-1.0, 1.75), m['turq']))):
    mb = MB(); mb.box(0, 0, 0, 0.7, 0.45, 0.45, mm, 0.004); mb.box(-0.02, -0.02, 0.45, 0.72, 0.47, 0.5, m['brass'], 0.004)
    inst(mb.mesh(f'Kids_chest_{i_ + 1}'), f'Kids_chest_{i_ + 1}', (x0, y0, TER), 0, 'Kids')

# =============== 13. DOME FINISHES ===============
for o in bpy.data.objects:
    if o.type != 'MESH' or not o.name.startswith('dome_'): continue
    for i_, ms in enumerate(o.data.materials):
        if ms == m.get('gaj'): o.data.materials[i_] = X['gajbrick']
        if ms == m.get('dometile'): o.data.materials[i_] = X['dometile']
print('detail v2 ok: chairs', nc, 'tables', nt, 'lanterns', nl, 'assets', len(ASSETS))
