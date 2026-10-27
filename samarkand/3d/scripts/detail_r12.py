"""Samarkand R12 — DETAIL PASS v2 (clean modelling). Executed inside base3d_r12.py's namespace after the base items.
Uses kit.py (closed-shell mesh builder) and assets_r12.py (asset library). Every furniture piece / fixture is its own
object (linked instance of a shared mesh), named, with its origin at its base; parts meet flush; nothing penetrates.
Zone-unique pieces (corridor ceiling, firewood wall, hood, portal arch...) are built with the same closed primitives."""
import os, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
TEX2 = os.path.join(HERE, 'tex2')
for f_ in ('kit.py', 'assets_r12.py', 'assets_v3.py', 'assets_v4.py', 'assets_v5.py', 'assets_v6.py'): exec(open(os.path.join(HERE, f_)).read())
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
for k, fn in (('carpet1', 'rug_oldpersian'), ('carpet2', 'rug_bukhara'), ('carpet3', 'suzani2'), ('carpet4', 'carpet1')): X[k] = uvmat(k + '_uv', fn + ('.jpg' if fn == 'rug_oldpersian' else '.png'))
X.update(kilim2=bl2.fabric('kilim2_f', os.path.join(TEX2, 'kilim2.png'), 0.6), suzani2=bl2.fabric('suzani2_f', os.path.join(TEX2, 'suzani2.png'), 0.9),
         quilt=bl2.fabric('quilt_f', os.path.join(TEX2, 'quilt.png'), 0.5), plaster=tex2('plaster_t', 'plaster.png', 1.5, rough=0.85, bump=0.15),
         rattan=tex2('rattan_t', 'rattan.png', 0.25, rough=0.7, bump=0.5), domeglaze=tex2('domeglaze_t', 'domeglaze.png', 0.9, rough=0.15, bump=0.2, coat=0.6),
         rishtan=uvmat('rishtan_uv', 'rishtan.png', rough=0.12, sheen=0.0), plov=tex2('plov_t', 'plov.png', 0.12, rough=0.6), bread=uvmat('bread_uv', 'bread.png', rough=0.7, sheen=0.0))
for th in ('sogd', 'sasan', 'saman', 'khorezm', 'timur', 'shahr', 'margil', 'pamir'): X['ep_' + th] = uvmat('ep_' + th + '_uv', 'ep_' + th + '.png', rough=0.5, sheen=0.1)
def pierced_mat(name):
    """pierced brass: metallic brass from pierced.png, the holes glow warm (pierced_mask -> emission)"""
    if name in bl._mats: return bl._mats[name]
    mm = tex2(name, 'pierced.png', 0.22, rough=0.3, bump=0.4); N = mm.node_tree.nodes; Lk = mm.node_tree.links; b = N['Principled BSDF']
    b.inputs['Metallic'].default_value = 0.9
    src_c = [l for l in Lk if l.to_socket == b.inputs['Base Color']][0].from_socket                 # deeper antique brass
    mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    mul.inputs['B'].default_value = (0.62, 0.42, 0.18, 1); Lk.new(src_c, mul.inputs['A']); Lk.new(mul.outputs['Result'], b.inputs['Base Color'])
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(TEX2, 'pierced_mask.png'), check_existing=True); it.projection = 'BOX'; it.projection_blend = 0.15
    src = [l.from_socket for l in Lk if l.to_node.type == 'TEX_IMAGE' and l.to_socket.name == 'Vector'][0]; Lk.new(src, it.inputs['Vector'])
    b.inputs['Emission Color'].default_value = (1.0, 0.6, 0.28, 1)
    mth = N.new('ShaderNodeMath'); mth.operation = 'MULTIPLY'; mth.inputs[1].default_value = 14.0
    Lk.new(it.outputs['Color'], mth.inputs[0]); Lk.new(mth.outputs[0], b.inputs['Emission Strength'])
    return mm
for c_ in ('terra', 'navy', 'emerald', 'wine'): X['velvet_' + c_] = bl2.fabric('velvet_%s_f' % c_, os.path.join(TEX2, 'velvet_%s.png' % c_), 0.5)
for c_ in ('linen', 'denim', 'silk_ikat', 'white', 'olive', 'black', 'rose', 'sand', 'terra'): X['cloth_' + c_] = bl2.fabric('cloth_%s_f' % c_, os.path.join(TEX2, 'cloth_%s.png' % c_), 0.35)
def mosaic_mat(name):
    """mosaic-glass lamp: Voronoi tesserae, random cobalt / turquoise / amber / ruby / milk-white per cell, glowing from inside,
    thin brass grout between the tiles (shader-built, no painted texture)"""
    if name in bl._mats: return bl._mats[name]
    mm = bpy.data.materials.new(name); N = mm.node_tree.nodes; Lk = mm.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 26.0
    Lk.new(tc.outputs['Object'], vo.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'CONSTANT'; cr = ramp.color_ramp
    pal = [(0.01, 0.03, 0.4), (0.0, 0.3, 0.38), (0.75, 0.28, 0.01), (0.01, 0.03, 0.4), (0.45, 0.01, 0.03), (0.0, 0.3, 0.38), (0.01, 0.03, 0.4), (0.75, 0.28, 0.01)]
    cr.elements[0].color = (*pal[0], 1); cr.elements[1].position = 1.0 / len(pal); cr.elements[1].color = (*pal[1], 1)
    for k, c in enumerate(pal[2:], 2): e = cr.elements.new(k / len(pal)); e.color = (*c, 1)
    sep = N.new('ShaderNodeSeparateColor'); Lk.new(vo.outputs['Color'], sep.inputs['Color']); Lk.new(sep.outputs['Red'], ramp.inputs['Fac'])
    ed = N.new('ShaderNodeTexVoronoi'); ed.feature = 'DISTANCE_TO_EDGE'; ed.inputs['Scale'].default_value = 26.0; Lk.new(tc.outputs['Object'], ed.inputs['Vector'])
    gr = N.new('ShaderNodeMath'); gr.operation = 'GREATER_THAN'; gr.inputs[1].default_value = 0.05; Lk.new(ed.outputs['Distance'], gr.inputs[0])   # 1 = glass, 0 = grout
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs['A'].default_value = (0.75, 0.55, 0.22, 1)
    Lk.new(gr.outputs[0], mix.inputs['Factor']); Lk.new(ramp.outputs['Color'], mix.inputs['B']); Lk.new(mix.outputs['Result'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.12; b.inputs['Coat Weight'].default_value = 0.8
    Lk.new(ramp.outputs['Color'], b.inputs['Emission Color'])
    em = N.new('ShaderNodeMath'); em.operation = 'MULTIPLY'; em.inputs[1].default_value = 2.2; Lk.new(gr.outputs[0], em.inputs[0]); Lk.new(em.outputs[0], b.inputs['Emission Strength'])
    met = N.new('ShaderNodeMath'); met.operation = 'SUBTRACT'; met.inputs[0].default_value = 1.0; Lk.new(gr.outputs[0], met.inputs[1]); Lk.new(met.outputs[0], b.inputs['Metallic'])
    bl._mats[name] = mm; return mm
X.update(zellige=tex2('zellige_t', 'zellige.png', 0.32, rough=0.12, bump=0.35, coat=0.6), pierced=mosaic_mat('mosaic_glass'))
X.update(bannai=tex2('bannai_t', 'bannai.png', 1.0, rough=0.7, bump=0.45, coat=0.15), bannai2=tex2('bannai2_t', 'bannai2.png', 1.4, rough=0.7, bump=0.45, coat=0.15),
         hazarbaf=tex2('hazarbaf_t', 'hazarbaf.png', 1.5, rough=0.6, bump=0.4, coat=0.25), kufic=tex2('kufic_t', 'kufic.png', 1.2, rough=0.25, bump=0.35, coat=0.5),
         majcobalt=tex2('majcobalt_t', 'majcobalt.png', 0.6, rough=0.15, bump=0.25, coat=0.7), majisfahan=tex2('majisfahan_t', 'majisfahan.png', 0.9, rough=0.15, bump=0.25, coat=0.7),
         girihstar=tex2('girihstar_t', 'girihstar.png', 0.8, rough=0.25, bump=0.35, coat=0.5),
         brickpave=tex2('brickpave_t', 'brickpave.png', 2.5, rough=0.8, bump=0.5), stone=tex2('stone_t', 'stone.png', 1.0, rough=0.6, bump=0.2),
         epigraph_uv=uvmat('epigraph_uv', 'epigraph.png', rough=0.15, sheen=0.0), runner_uv=uvmat('runner_uv', 'runner_malayer.jpg'), oldrug_uv=uvmat('oldrug_uv', 'rug_oldpersian.jpg'))
X.update(glazeturq=mat('glaze_turq', (0.03, 0.42, 0.46), rough=0.18, coat=0.8, noise_var=0.05), glazecob=mat('glaze_cob', (0.02, 0.06, 0.38), rough=0.18, coat=0.8, noise_var=0.04))
X.update(terracotta=mat('terracotta_glaze', (0.32, 0.085, 0.04), rough=0.3, coat=0.4, noise_var=0.06), clayplaster=mat('clay_plaster', (0.56, 0.43, 0.33), rough=0.85, bump=0.35, noise_var=0.03), leather=mat('leather_tan', (0.38, 0.19, 0.1), rough=0.45, bump=0.15),
         reed=mat('reed_dry', (0.5, 0.38, 0.22), rough=0.75, noise_var=0.06), bark2=mat('bark_plane', (0.3, 0.27, 0.2), rough=0.9, bump=1.2, noise_var=0.13),
         beadikat=uvmat('beadikat_uv', 'beadikat.jpg', rough=0.3, sheen=0.2))
for k_, sz in (('bannai', 1.0), ('bannai2', 1.4), ('hazarbaf', 1.5), ('kufic', 1.2), ('majcobalt', 0.6), ('majisfahan', 0.9), ('girihstar', 0.8), ('brickpave', 2.5), ('stone', 1.0)): register_uv_size(X[k_], sz)
for mm, sz in ((m['ikat'], 0.5), (m['suzani'], 0.6), (m['jali'], 0.5), (m['majolica'], 0.6), (m['band'], 1.2), (m['girih'], 0.6), (m['floor'], 1.2),
               (X['carved'], 0.9), (X['kilim'], 0.6), (X['kilim2'], 0.6), (X['suzani2'], 0.9), (X['quilt'], 0.5), (X['plaster'], 1.5), (X['rattan'], 0.25), (X['domeglaze'], 0.9), (X['plov'], 0.12), (X['velvet'], 0.8), (X['tent'], 1.2), (X['copper'], 0.5), (X['gajbrick'], 1.4), (X['dometile'], 0.7)):
    register_uv_size(mm, sz)
def ceil_at(x, y):
    """underside of whatever is overhead: balcony slab (x < 1.5), a roof beam (IPE 300 bottom flange), a purlin (C200 bottom)
    or the roof sandwich panel between them"""
    if x < 1.5: return 3.85
    if any(abs(y - yb_) < 0.085 for yb_, _ in D['beams']): return top(x) - 0.55
    if any(abs(x - px_) < 0.06 and py0 - 0.05 < y < py1 + 0.05 for px_, py0, py1 in D['purlins']): return top(x) - 0.25
    return top(x) - 0.05

# =============== 1. OPEN THEMED BOOTHS (sea view), niche walls with vases + framed epoch art, theme objects ===============
BO = D['booths']; PEOPLE = []
for k, (y0, y1, xw, xe, th) in enumerate(BO):
    L = round((BO[k - 1][3] if k > 0 else xe) - xw, 3)                   # wall reaches the back of the booth before it
    th_s = BO[k - 1][4] if k > 0 else None
    inst(a_nichewall(L, th_s, th), f'Booth{k + 1}_wall_S', (xw, y0, TER), 0, 'Booths')
    inst(a_vase(k % 4), f'Booth{k + 1}_niche_vase', (xw + L - 0.4, y0 + TH / 2, TER + 1.0), 0, 'Booths')
    inst(a_booth_open(th), f'Booth{k + 1}_{th}', (xw, y0, TER), 0, 'Booths')
    inst(a_monument(th), f'Booth{k + 1}_object_{th}', (xw + 1.21, y0 + (TH + 2.0) / 2, TER + 0.78), math.pi / 2, 'Booths')
    for i_, yy in enumerate((y0 + TH + 0.12, y0 + 2.0 - 0.12)): inst(a_vase((k + 2 * i_ + 1) % 4), f'Booth{k + 1}_parapet_vase_{i_ + 1}', (xw + 1.21, yy, TER + 0.78), 0, 'Booths')
    pil = CUSH[th]
    inst(a_banquette(1.03, 0.5, 'emerald', pil), f'Booth{k + 1}_banquette_S', (xw + 0.08, y0 + TH, TER), 0.0, 'Booths')
    inst(a_banquette(1.03, 0.5, 'emerald', pil), f'Booth{k + 1}_banquette_N', (xw + 1.11, y0 + 2.0, TER), math.pi, 'Booths')
    inst(a_tiletable(1.3), f'Booth{k + 1}_table', (xw + 0.6, y0 + 1.08, TER), 0.0, 'Booths')
    inst(a_boothset(), f'Booth{k + 1}_tableset', (xw, y0, TER), 0, 'Booths')
    inst(a_pendant_cluster(3, (0.1, 0.2, 0.15)), f'Booth{k + 1}_pendant', (xw + 0.6, y0 + 1.08, TER + 2.165), 0, 'Booths')
    if k == 2:                                                                  # one couple in a booth
        PEOPLE.append(('chair', (xw + 0.46, y0 + TH + 0.40, TER - 0.08), 0.0, ('silk_ikat', 'sand', 2, 1, True, 'short')))       # clear of the pillows,
        PEOPLE.append(('chair', (xw + 0.76, y0 + 2.0 - 0.40, TER - 0.08), math.pi, ('linen', 'denim', 0, 0, False, 'long')))    # legs interleave under the table
y0, y1, xw, xe, th = BO[-1]
inst(a_nichewall(1.3, th, None), f'Booth{len(BO)}_wall_N', (xw, y1, TER), 0, 'Booths')
inst(a_vase(1), f'Booth{len(BO)}_niche_vase_N', (xw + 1.3 - 0.4, y1 + TH / 2, TER + 1.0), 0, 'Booths')

# =============== 2. CHAIRS / TABLES / TABLEWARE (one object per piece) ===============
ROT_BACK = {'s': 0.0, 'n': math.pi, 'e': math.pi / 2, 'w': -math.pi / 2}
nc = nt = 0; CHAIRS = []
for it in D['items']:
    if it['kind'] == 'chair':
        for r in it['poly']:
            base = 0.0 if on_plat(r) else TER; x0, y0, x1, y1 = bbox(r)
            nc += 1; inst(a_tubchair('terra' if (y0 < 15.3 or nc % 5) else 'navy'), f'Chair_{nc:03d}', ((x0 + x1) / 2, (y0 + y1) / 2, base), ROT_BACK[it.get('back', 'n')], 'Furniture')
            CHAIRS.append(((x0 + x1) / 2, (y0 + y1) / 2, base, ROT_BACK[it.get('back', 'n')]))
    if it['kind'] == 'table':
        for r in it['poly']:
            base = 0.0 if on_plat(r) else TER; x0, y0, x1, y1 = bbox(r); n = it.get('mods', 1); rz = 0.0 if it.get('axis', 'x') == 'x' else math.pi / 2
            nt += 1; c_ = ((x0 + x1) / 2, (y0 + y1) / 2, base)
            inst(a_tiletable(n), f'Table_{nt:03d}', c_, rz, 'Furniture'); inst(a_tableset(n), f'Tableset_{nt:03d}', c_, rz, 'Furniture')

# =============== 3. AIVAN SEDIR BOOTHS: back cushions, wall carpets, tableware, lanterns ===============
scr = [bbox(it['poly'][0]) for it in D['items'] if it['kind'] == 'ascreen']; AIV = []
ats = [bbox(it['poly'][0]) for it in D['items'] if it['kind'] == 'atable']
for i_, it in enumerate([it for it in D['items'] if it['kind'] == 'abench']):
    x0, y0, x1, y1 = bbox(it['poly'][0]); cy = (y0 + y1) / 2
    tb = min(ats, key=lambda b_: abs((b_[1] + b_[3]) / 2 - cy)); away = -1 if (tb[1] + tb[3]) / 2 > cy else 1
    yo = y0 if away < 0 else y1                                        # outer edge of the bench
    for sx0, sy0, sx1, sy1 in scr:                                     # a screen over the bench edge: start at its face
        if sx0 < x1 and sx1 > x0 and sy0 - 1e-6 <= yo <= sy1 + 1e-6: yo = sy1 if away < 0 else sy0
    yf = y1 if away < 0 else y0; bx0 = 0.16; Lb = round(x1 - bx0, 3); Db = round(abs(yf - yo), 3)       # clear of the wall carpet (x 0.14..0.152)
    if away < 0: inst(a_banquette(Lb, Db, 'navy', 'kilim2'), f'Aivan_banquette_{i_ + 1}', (bx0, yo, 0.0), 0.0, 'Aivan')
    else: inst(a_banquette(Lb, Db, 'navy', 'kilim2'), f'Aivan_banquette_{i_ + 1}', (x1, yo, 0.0), math.pi, 'Aivan')
    AIV.append((bx0, x1, yo, away))
for i_, (x0, y0, x1, y1) in enumerate(ats):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    mb = MB(); mb.picture_box(0.0, -0.85, 0.75, 0.012, 0.85, 2.25, X['carpet%d' % (1 + i_ % 4)], '+x'); mb.box(0.0, -0.9, 2.25, 0.03, 0.9, 2.29, m['brass'])
    inst(mb.mesh(f'Aivan_wallcarpet_{i_ + 1}'), f'Aivan_wallcarpet_{i_ + 1}', (0.14, cy, 0.0), 0, 'Aivan')
    inst(a_tiletable(round((x1 - x0) / 0.7, 4)), f'Aivan_table_{i_ + 1}', (cx, cy, 0.0), 0.0, 'Aivan')
    inst(a_tableset(2), f'Aivan_tableset_{i_ + 1}', (cx, cy, 0.0), 0.0 if (x1 - x0) >= (y1 - y0) else math.pi / 2, 'Aivan')
    lantern_at(cx, cy, 1.95, 1.0, ceil_at(cx, cy), 'Aivan', f'Aivan_lantern_{i_ + 1}')

# =============== 4. FLYING CARPETS under the roof ===============
ZONES = [(3.6, 7.8, 22.9, 24.8), (4.4, 7.6, 30.2, 34.0)]
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
                    px, py = x + u * c_ - v * s_, y + u * s_ + v * c_
                    j_ = min(7, int((v + 0.95) / (1.9 / 8))); va = -0.95 + 1.9 * j_ / 8; vb = va + 1.9 / 8; t_ = (v - va) / (vb - va)
                    pz = z + 0.05 * ((1 - t_) * math.sin(va / 1.9 * 2 * math.pi) + t_ * math.sin(vb / 1.9 * 2 * math.pi)) + 0.0005   # exact top of the faceted carpet
                    inst(a_rod(), 'Rod_carpet', (px, py, pz), 0, 'Carpet_ceiling', scale=(0.7, 0.7, ceil_at(px, py) - pz))
            x += 1.6
        y += 2.3
print('flying carpets', nfc)

# =============== 5. MAJLIS TENTS ===============
for i_, (tx0, ty0, tx1, ty1) in enumerate(D.get('tents', [D['tent']])):
    w, d = round(tx1 - tx0, 3), round(ty1 - ty0, 3)
    inst(a_tent(w, d), f'Tent_{i_ + 1}', (tx0, ty0, TER), 0, 'Tapchans_tent')
    for j_, it in enumerate([it for it in D['items'] if it['kind'] == 'sofa']):
        sx0, sy0, sx1, sy1 = bbox(it['poly'][0])
        if not (tx0 - 0.05 <= sx0 and sx1 <= tx1 + 0.05 and ty0 - 0.05 <= sy0 and sy1 <= ty1 + 0.05): continue
        dW, dS, dN = sx0 - tx0, sy0 - ty0, ty1 - sy1
        if dW < 0.05 and (sy1 - sy0) > (sx1 - sx0): inst(a_banquette(round(sy1 - sy0, 3), round(sx1 - sx0, 3), 'wine', 'kilim2'), f'Tent{i_ + 1}_banquette_W', (sx0, sy1, TER), -math.pi / 2, 'Tapchans_tent')
        elif dS < dN: inst(a_banquette(round(sx1 - sx0, 3), round(sy1 - sy0, 3), 'wine', 'kilim2'), f'Tent{i_ + 1}_banquette_S', (sx0, sy0, TER), 0.0, 'Tapchans_tent')
        else: inst(a_banquette(round(sx1 - sx0, 3), round(sy1 - sy0, 3), 'wine', 'kilim2'), f'Tent{i_ + 1}_banquette_N', (sx1, sy1, TER), math.pi, 'Tapchans_tent')
    for it in D['items']:
        if it['kind'] == 'otable':
            ox, oy = cen(it['poly'][0])
            if tx0 <= ox <= tx1 and ty0 <= oy <= ty1:
                if 'Tent_tray' not in ASSETS:
                    mb = MB(); mb.cyl(0, 0, 0, 0.02, 0.33, m['brass'], 32); _plate_r(mb, -0.12, 0.0, 0.02, 0.11); _glass(mb, 0.15, 0.08, 0.02); _glass(mb, 0.15, -0.1, 0.02)
                    ASSETS['Tent_tray'] = mb.mesh('Tent_tray')
                inst(ASSETS['Tent_tray'], f'Tent{i_ + 1}_tray', (ox, oy, TER + 0.465), 0, 'Tapchans_tent')
    for yy in (ty0 + 0.9, ty1 - 0.9): lantern_at((tx0 + tx1) / 2 + 0.2, yy, TER + 1.8, 0.9, TER + 2.25, 'Tapchans_tent', f'Tent{i_ + 1}_lantern')

# =============== 6. TAPCHAN ===============
for y0 in D['tap']:
    inst(a_tapchan_rail(2.0, 2.2), 'Tapchan_railing', (2.55, y0, TER + 0.45), 0, 'Tapchans_tent')
    inst(a_bolster(1.9, 0.09, 'ikat'), 'Tapchan_bolster', (2.55 + 0.18, y0 + 1.1, TER + 0.57 + 0.09), 0, 'Tapchans_tent')
    mb = MB(); mb.picture_box(-0.55, -0.45, 0, 0.55, 0.45, 0.003, X['carpet3'], '+z')
    for px, py in ((-0.35, -0.25), (-0.35, 0.25), (0.35, -0.25), (0.35, 0.25)): _plate_r(mb, px, py, 0.003, 0.1)
    _lagan_plov(mb, 0.0, 0.0, 0.003); _bread(mb, 0.0, 0.33, 0.003, 0.07)
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
    a = k * 0.9 + 0.3; r_ = 0.15 + 0.045 * (k % 3); px, py = r_ * math.cos(a), r_ * math.sin(a)
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
e0, e1 = D['ent']
mb = MB(); mb.cyl(0, 0, 0, 0.05, 0.07, m['steel'], 16); mb.cyl(0, 0, 0.05, 0.055, 0.06, X['lampglow'], 16); up = mb.mesh('Uplight')
for x, y in D['trees']:
    for a in (0.5, 2.6, 4.7): inst(up, 'Tree_uplight', (x + 0.75 * math.cos(a), y + 0.75 * math.sin(a), TER + 0.08), 0, 'Lights')
for i_, ((x0, y0), mm) in enumerate((((-6.6, 1.8), m['majolica']), ((-5.6, 1.8), X['carved']), ((-1.0, 1.75), m['turq']))):
    mb = MB(); mb.box(0, 0, 0, 0.7, 0.45, 0.45, mm, 0.004); mb.box(-0.02, -0.02, 0.45, 0.72, 0.47, 0.5, m['brass'], 0.004)
    inst(mb.mesh(f'Kids_chest_{i_ + 1}'), f'Kids_chest_{i_ + 1}', (x0, y0, TER), 0, 'Kids')

# =============== 13a. CEILING CARPETS between the beams (aivan + dining south) with rattan pendant clusters ===============
TY = sorted(y for y, _ in D['beams']); ncc = 0
def ceiling_carpet(x0, x1, ya, yb, k):
    global ncc
    rows = []
    for j in range(7):
        y = ya + (yb - ya) * j / 6
        rows.append([(x0 + (x1 - x0) * c / 6, y, top(x0 + (x1 - x0) * c / 6) - 0.25) for c in range(7)])        # top face on the purlins; 12 mm solid hangs below
    mb = MB(); mb.sheet(rows, X['carpet%d' % (1 + k % 4)], 0.012, picture=True)
    ncc += 1; inst(mb.mesh(f'Ceiling_carpet_{ncc:02d}'), f'Ceiling_carpet_{ncc:02d}', (0, 0, 0), 0, 'Carpet_ceiling')
for ya, yb in zip(TY[:-1], TY[1:]):
    if 15.0 < ya < 29.0: ceiling_carpet(1.6, 3.0, ya + 0.1, yb - 0.1, int(ya))                       # aivan (outside the balcony slab)
for ya, yb in ((4.1, 9.85),):
    for x0, x1 in ((1.0, 3.4), (3.6, 6.0), (6.2, 8.6)):
        ceiling_carpet(x0, x1, ya + 0.1, yb - (0.1 if x1 < 3.5 else 0.42), int(x0))      # clear of the south dome ring girder
        for dx, dy in (((0.0, -1.2), (0.0, 1.2)) if x0 > 1.0 else ((0.0, -1.2),)):                                                        # pierced-brass pendant clusters
            cx, cy = (x0 + x1) / 2 + dx, (ya + yb) / 2 + dy
            rows_x = [x0 + (x1 - x0) * c / 6 for c in range(7)]; c_ = max(i for i, xx in enumerate(rows_x) if xx <= cx)
            xa_, xb_ = rows_x[c_], rows_x[min(6, c_ + 1)]; t_ = (cx - xa_) / max(1e-6, xb_ - xa_)
            zt = (1 - t_) * (top(xa_) - 0.25) + t_ * (top(xb_) - 0.25) - 0.012                         # exact underside of the faceted carpet
            inst(a_pendant_cluster(3), 'Pendant_cluster', (cx, cy, zt - 0.013), 0, 'Lights')          # canopy r 0.24 under a 5 % slope
print('ceiling carpets', ncc)

# =============== 13b. VELVET SWAGS over the plaza (beam to beam), CARPET FRIEZE over the aivan ===============
for i_, xc in enumerate((9.6, 10.35, 11.1)):
    ya, yb = 9.85 + 0.1, 14.6; rows = []                                   # stop clear of the street portal
    for c in (0, 1):
        xx = xc - 0.35 + 0.7 * c
        rows.append([(xx, ya + (yb - ya) * j / 14, top(xx) - 0.55 - 0.65 * math.sin(math.pi * j / 14)) for j in range(15)])
    mb = MB(); mb.sheet(rows, X['velvet'], 0.008, picture=False)
    inst(mb.mesh(f'Velvet_swag_{i_ + 1}'), f'Velvet_swag_{i_ + 1}', (0, 0, 0), 0, 'Carpet_ceiling')
for i_, (ya, yb) in enumerate(((15.62, 21.9), (21.9, 28.4))):
    n = int((yb - ya) / 0.4); top_row = [(0.152, ya + (yb - ya) * j / n, 3.14) for j in range(n + 1)]
    bot_row = [(0.152, ya + (yb - ya) * j / n, 2.45 + (0.12 if j % 2 else 0.0)) for j in range(n + 1)]
    mb = MB(); mb.sheet([bot_row, top_row], X['carpet3'], 0.008, picture=True)
    inst(mb.mesh(f'Carpet_frieze_{i_ + 1}'), f'Carpet_frieze_{i_ + 1}', (0, 0, 0), 0, 'Aivan')

# =============== 13c. PEOPLE — a few well-built figures, placed on real seats ===============
def chair_near(px, py, side):
    """the chair nearest to (px, py) whose sitter faces +Y (side 's') or -Y (side 'n')"""
    want = 0.0 if side == 's' else math.pi
    return min([c for c in CHAIRS if abs(c[3] - want) < 1e-6], key=lambda c: math.hypot(c[0] - px, c[1] - py))
for (px, py), side, look in (((3.0, 6.8), 's', ('white', 'olive', 1, 0, False, 'short')), ((3.0, 6.8), 'n', ('rose', 'black', 2, 1, True, 'long')),
                             ((7.0, 22.5), 's', ('terra', 'sand', 0, 2, True, 'long')), ((7.0, 22.5), 'n', ('black', 'linen', 3, 0, False, 'short'))):
    x, y, z, rz = chair_near(px, py, side); PEOPLE.append(('chair', (x, y, z), rz, look))
if AIV:
    bx0, bx1, yo, away = AIV[1]
    PEOPLE.append(('chair', ((bx0 + bx1) / 2 + 0.15, yo - away * 0.38, -0.08), 0.0 if away < 0 else math.pi, ('olive', 'denim', 1, 0, False, 'long')))
if 'rot' in D:
    rx, ry, _ = D['rot']; PEOPLE.append(('stand', (rx + 0.9, ry - 1.45, TER), math.pi * 0.72, ('linen', 'denim', 2, 2, False, 'long')))
PEOPLE.append(('stand', (D['hzc'][0] + 0.95, D['hzc'][1] - 1.55, TER), math.pi * 0.85, ('silk_ikat', 'sand', 0, 1, True, 'short')))
# scanned-base figures from the owner's pack, rigged and posed by people_rig.py (people_lib.blend): 1-2 trousers, 3-6 dresses
LIBP = os.path.join(HERE, 'people_lib.blend')
with bpy.data.libraries.load(LIBP) as (src, dst): dst.meshes = [n for n in src.meshes if n.startswith('Human_')]
HAIR = [(0.03, 0.025, 0.02), (0.16, 0.09, 0.05), (0.38, 0.33, 0.3)]
def human_lib(pose, look, idx):
    top_, bot, skin, hair, female, sleeve = look
    fig = (2 if female else 1) if pose != 'stand' else ((3 + idx % 4) if female else 1)
    me = bpy.data.meshes[f'Human_{fig}_{pose}'].copy(); me.name = f'Human_{idx + 1:02d}'
    mats = [mat(f'h_skin_{skin}', SKINC[skin], rough=0.45), mat(f'h_hair_{hair}', HAIR[hair], rough=0.4), X[CLOTHES[top_]], X[CLOTHES[bot]], mat('h_shoe', (0.12, 0.07, 0.045), rough=0.35)]
    for k, mm in enumerate(mats): me.materials[k] = mm
    return me
for i_, (pose, (x, y, z), rz, look) in enumerate(PEOPLE):
    if pose == 'stand': fl = z; lp = 'stand'
    else:
        fl = TER if z < TER - 0.05 else (0.0 if abs(z + 0.08) < 1e-6 else z)
        lp = 'sitc' if fl == z else 'sitb'                             # tub chair (seat 0.48) / banquette (seat 0.44) pose
    me_ = human_lib(lp, look, i_)
    zs_ = fl - me_['feet'] + 0.0005 if lp != 'stand' else z; off = 0.0   # feet on the floor; the seat takes the pelvis
    inst(me_, f'Person_{i_ + 1:02d}', (x - off * math.sin(rz), y + off * math.cos(rz), zs_), rz, 'People')
print('people', len(PEOPLE))

# =============== 14. KHIVA ARCADE: the aivan / hall divider (carved columns, tiled parapets, jali + myrtle bays, arched heads) ===============
XA = 3.18; ZB = 3.02; ZC = ZB - 0.24                                  # arcade axis on the aivan edge, beam top under the roof beams, capital top
COLY = [15.45, 18.17] + [18.17 + (24.18 - 18.17) * k / 5 for k in range(1, 5)] + [24.18, 25.92, 27.13, 28.34]
for i_, y in enumerate(COLY): inst(a_khiva_column(ZC), f'Khiva_column_{i_ + 1:02d}', (XA, y, 0.0), 0, 'Aivan')
nb_ = 0
for i_, (ya, yb) in enumerate(zip(COLY[:-1], COLY[1:])):
    L = round(yb - ya, 4); opening = (ya, yb) in ((15.45, 18.17), (24.18, 25.92))
    inst(a_arcade_head(L, 0.0, opening), f'Khiva_arcade_head_{i_ + 1:02d}', (XA, ya, ZC), 0, 'Aivan')
    if not opening:
        nb_ += 1; inst(a_arcade_bay(L, 'jali' if nb_ % 2 else 'plant'), f'Khiva_arcade_bay_{i_ + 1:02d}', (XA, ya, 0.0), 0, 'Aivan')
mb = MB(); mb.box(XA - 0.13, COLY[0] - 0.15, ZC, XA + 0.13, COLY[-1] + 0.15, ZB, m['walnut'], 0.006)
mb.box(XA + 0.13, COLY[0] - 0.15, ZC + 0.04, XA + 0.15, COLY[-1] + 0.15, ZB - 0.04, X['carved'])                    # carved frieze, hall face
for zz in (ZC + 0.02, ZB - 0.04): mb.box(XA + 0.15, COLY[0] - 0.15, zz, XA + 0.16, COLY[-1] + 0.15, zz + 0.02, m['brass'])
inst(mb.mesh('Khiva_arcade_beam'), 'Khiva_arcade_beam', (0, 0, 0), 0, 'Aivan')

# =============== 15. DOME CHANDELIER under the central dome's lantern ===============
for d in D['domes']:
    if not d['lantern']: continue
    th0 = math.asin(min(0.999, d['lantern'] / d['r'])); lz = ZR + (d['rise'] + T_) * math.cos(th0) + 0.5      # underside of the lantern cap
    inst(a_chandelier(round(lz - (TER + 3.65), 3), 0.95, 12), f'Chandelier_dome_{d["key"]}', (d['c'][0], d['c'][1], lz), 0, 'Lights')

# =============== 16. SAMARKAND COMMON AREAS (Shah-i-Zinda / Gur-e-Amir) ===============
# 16a. majolica columns cladding the steel columns, muqarnas capitals under the roof beams
e0, e1 = D['ent']
for i_, (x, y) in enumerate(D['cols']):
    if y < 0.6 and x < 0: continue
    if any(a <= y <= b for a, b in ((e0 - 0.7, e0), (e1, e1 + 0.7))): continue
    zt = top(x + 0.36) - 0.55 - 0.002; inst(a_sam_column(round(zt - TER, 4)), f'Sam_column_{i_ + 1:02d}', (x, y, TER), 0, 'Columns')      # capital clears the 5 % sloped beam flange
# 16b. Gur-e-Amir pishtaq at the street entrance, aligned with the street line
e0, e1 = D['ent']; yc_ = (e0 + e1) / 2; dx_, dy_ = xb1 - xb0, yb1 - yb0
Hp_ = round(min(top(xb(y_) - t_) - 0.55 for y_ in (e0 - 0.7, e1 + 0.7) for t_ in (0.0, 1.5)) - SID, 3)   # pylons carry the roof beams: top = beam underside
pm = a_pishtaq(round(e1 - e0, 3), Hp_, 1.5, round(TER - SID, 3)).copy(); pm.name = 'Pishtaq_sheared'
for v in pm.vertices: v.co.x += dx_ / dy_ * v.co.y                      # shear the plan to the street line: pylons = the plan's parallelograms
inst(pm, 'Street_pishtaq', (xb(yc_) - 0.75, yc_, SID), 0, 'Street_facade')
SKIPCOL = [(e0 - 0.7, e0), (e1, e1 + 0.7)]                               # columns inside the pylons are encased by them
# 16c. epigraphic frieze on the facade ledger (room face x = 0.18)
ybs = sorted(y_ for y_, _ in D['beams']); edges = [4.2] + [v for y_ in ybs if 4.2 < y_ < 37.0 for v in (y_ - 0.08, y_ + 0.08)] + [37.0]
for k_, (ya_, yb_) in enumerate(zip(edges[::2], edges[1::2])):                  # frieze panels between the beam ends
    if yb_ - ya_ > 0.3: inst(a_frieze(round(yb_ - ya_, 3), 0.435), f'Facade_frieze_{k_ + 1:02d}', (0.18, ya_, 3.25), 0, 'Building')
# 16d. corridor runner: the Malayer carpet
for it in D['items']:
    if it['kind'] == 'runner':
        x0, y0, x1, y1 = bbox(it['poly'][0]); mb = MB(); mb.picture_box(x0, y0, TER, x1, y1, TER + 0.012, X['runner_uv'], '+z')
        inst(mb.mesh('Corridor_runner_malayer'), 'Corridor_runner_malayer', (0, 0, 0), 0, 'Corridor')
# 16e. karbandi dome interior in the central dome (imported mesh, closed 20 mm shell), chandelier from its crown
for d in D['domes']:
    if not d['lantern']: continue
    gb = gonbad(d['c'][0], d['c'][1], ZR, d['r'] - 0.04, os.path.join(HERE, 'gonbad.obj'))
    o_ = bpy.data.objects.get(f'dome_ribs_{d["key"]}')
    if o_: bpy.data.objects.remove(o_)
    bpy.context.view_layer.update()
    hit = gb.ray_cast(Vector((d['c'][0], d['c'][1], ZR + 0.2)), Vector((0, 0, 1)))
    zc_ = hit[1].z if hit[0] else ZR + 1.5
    ch = bpy.data.objects.get(f'Chandelier_dome_{d["key"]}')
    if ch: bpy.data.objects.remove(ch)
    inst(a_chandelier(round(zc_ - (TER + 3.65), 3), 0.95, 12), f'Chandelier_dome_{d["key"]}', (d['c'][0], d['c'][1], zc_), 0, 'Lights')
    print('karbandi crown z', round(zc_, 3))
# 16f. common-area surfaces: Samarkand brick, majolica and girih instead of plain concrete / plaster
SWAP = {'planter_band': X['hazarbaf'], 'firewall': X['bannai'], 'barbody': X['majcobalt'], 'barreturn': X['girihstar'], 'terrace_floor': X['brickpave'],
        'alley_girih': X['girihstar'], 'sebil': X['majcobalt'], 'sback': X['kufic'], 'sbench': X['stone'], 'street_steps': X['stone'], 'host': X['majcobalt'],
        'photo_plant': X['hazarbaf'], 'bbq_plant': X['hazarbaf'], 'kazanblock': X['bannai2'], 'tandoorblock': X['majcobalt'], 'stepsA': X['stone'], 'stepsB': X['stone']}
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    k_ = next((k for k in SWAP if o.name == k or o.name.startswith(k + '.') or o.name.startswith(k + '_')), None)
    if k_ and not o.name.startswith(('photo_plant_soil', 'bbq_plant_soil')):
        for i_ in range(len(o.data.materials)): o.data.materials[i_] = SWAP[k_]
for d in D['domes']:                                                     # oculus domes: Samarkand brick inside, kufic drums
    o_ = bpy.data.objects.get(f'dome_drum_{d["key"]}')
    if o_: o_.data.materials[0] = X['kufic']

# =============== 17. THE BAR (owner references): sculpted niche wall, terracotta baguette counter, stools, beaded drums, fringe ===============
BAR_Y0, BAR_Y1 = 8.6, 14.3; LB = round(BAR_Y1 - BAR_Y0, 3); HW = round(3.10 - TER, 3)
BX_ = 0.14                                                               # clear of the glazing mullions
inst(a_barwall(LB, HW), 'Bar_backwall', (BX_, BAR_Y0, TER), 0, 'Bar')
mb = MB(); mb.picture_box(0.32, 4.75, 1.2, 0.335, 5.55, 2.95, X['oldrug_uv'], '+x'); mb.rod((0.345, 4.7, 2.98), (0.345, 5.6, 2.98), 0.01, m['brass'], 10)
mb.box(0.32, 4.68, 2.975, 0.335, 4.69, 2.985, m['brass']); mb.box(0.32, 5.61, 2.975, 0.335, 5.62, 2.985, m['brass'])
inst(mb.mesh('Bar_wallcarpet'), 'Bar_wallcarpet', (BX_, BAR_Y0, TER), 0, 'Bar')
mb = MB(); mb.box(0.35, 1.55, 0.96, 0.55, 2.25, 1.38, m['steel'], 0.01); mb.box(0.35, 1.6, 1.38, 0.52, 2.2, 1.4, m['brass'], 0.004)
for yy in (1.72, 1.9, 2.08): mb.rod((0.55, yy, 1.2), (0.62, yy, 1.17), 0.012, m['black'], 8)
inst(mb.mesh('Bar_espresso'), 'Bar_espresso', (BX_, BAR_Y0, TER), 0, 'Bar')
inst(a_barcounter(LB, 0.6), 'Bar_counter', (1.5, BAR_Y0, TER), 0, 'Bar')
inst(a_bar_cornice(LB, round(HW, 3)), 'Bar_cornice', (BX_ + 0.34, BAR_Y0, TER), 0, 'Bar')        # carved frieze + muqarnas corbels
for it in D['items']:
    if it['kind'] == 'stool':
        cx, cy = cen(it['poly'][0]); inst(a_barstool(), 'Barstool', (cx, cy, TER), math.pi / 2, 'Bar')
for i_, yy in enumerate((9.2, 10.6, 12.0, 13.4)):
    xx = 1.95; rows_x = [1.0 + 0.4 * c for c in range(7)]; c_ = max(i for i, x_ in enumerate(rows_x) if x_ <= xx); t_ = (xx - rows_x[c_]) / 0.4
    zt = (1 - t_) * (top(rows_x[c_]) - 0.25) + t_ * (top(rows_x[c_ + 1]) - 0.25) - 0.012
    inst(a_drum_pendant(round(zt - (TER + 2.35), 3)), f'Bar_drum_pendant_{i_ + 1}', (xx, yy, zt - 0.004), 0, 'Lights')
# =============== 18. STREET SEBIL, CHINAR TRUNKS ===============
y0s = 12.7; pm = a_sebil(1.6, 0.4, 0.55, round(TER - SID + 0.03, 3)).copy(); pm.name = 'Sebil_sheared'
for v in pm.vertices: v.co.x += dx_ / dy_ * v.co.y
inst(pm, 'Street_sebil', (xb(y0s) - 0.95, y0s, SID), 0, 'Street_facade')
for i_, (x, y) in enumerate(D['trees']):
    o_ = bpy.data.objects.get(f'chinar_trunk_{i_}')
    if o_: bpy.data.objects.remove(o_)
    inst(a_chinar_trunk(round(6.4 - TER, 3), 0.32, 0.2), f'Chinar_trunk_{i_ + 1}', (x, y, TER), 0, 'Trees')

# =============== 19. HAUZ COPING, STREET BENCH SEATS AND COPINGS ===============
from shapely.geometry import Polygon as SPoly
from shapely.ops import unary_union as sunion
ring = sunion([SPoly(r) for r in D['hauz_ring']])
mb = MB()
for z0_, z1_, off in ((TER + 0.38, TER + 0.42, 0.025), (TER + 0.42, TER + 0.45, 0.04)):           # two-step profiled stone coping
    g = ring.buffer(off, join_style=2, mitre_limit=3.0)
    for q in _pieces(g): mb.extrude(list(q.exterior.coords)[:-1], z0_, z1_, X['stone'], 'xy', 0.0)        # annulus -> hole-free pieces
bmesh.ops.triangulate(mb.bm, faces=[f for f in mb.bm.faces if len(f.verts) > 4])          # concave C-shaped caps: real triangulation
inst(mb.mesh('Hauz_coping'), 'Hauz_coping', (0, 0, 0), 0, 'Fountain')
o_ = bpy.data.objects.get('hauz_rim')
if o_: o_.data.materials[0] = X['kufic']
mb = MB()
for it in D['items']:
    if it['kind'] != 'sbench': continue
    pts = it['poly'][0]; ys = [p_[1] for p_ in pts]; a_, b_ = min(ys), max(ys)
    if b_ - a_ < 0.5: continue
    mb.extrude([(xb(a_) - 0.55, a_), (xb(a_) + 0.03, a_), (xb(b_) + 0.03, b_), (xb(b_) - 0.55, b_)], SID + 0.45, SID + 0.5, X['stone'], 'xy', 0.006)
for it in D['items']:
    if it['kind'] != 'sback': continue
    ys = [p_[1] for p_ in it['poly'][0]]; a_, b_ = min(ys), max(ys)
    mb.extrude([(xb(a_) - 0.72, a_), (xb(a_) - 0.53, a_), (xb(b_) - 0.53, b_), (xb(b_) - 0.72, b_)], SID + 1.0, SID + 1.05, X['stone'], 'xy', 0.006)
inst(mb.mesh('Street_bench_stone'), 'Street_bench_stone', (0, 0, 0), 0, 'Street_facade')

# =============== 13. DOME FINISHES ===============
for o in bpy.data.objects:
    if o.type != 'MESH' or not o.name.startswith('dome_'): continue
    for i_, ms in enumerate(o.data.materials):
        if ms == m.get('gaj'): o.data.materials[i_] = X['bannai']
        if ms == m.get('dometile'): o.data.materials[i_] = X['domeglaze']
print('detail v2 ok: chairs', nc, 'tables', nt, 'lanterns', nl, 'assets', len(ASSETS))
