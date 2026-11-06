"""rev. 11.7 (owner): 'all generated textures -> real; booth lamps replaced; booth settees for two but wide, set deeper; curtains in
every booth'.
  * booths: 2-seat settees 1.40 (700 per person) pushed to the parapet side (detail_v101), the cascade chandelier of the dome in a
    small size over each table instead of the glass-globe cluster, and a pair of velvet curtains at each booth opening: brass rod
    under the name board, gathered pleats tied back with a brass ring and tassel at +1.10, falling to the podium
  * every generated (procedural) image texture is replaced by a real material: canvas, velvet, glazes, porcelain, food, copper,
    rattan, slate are plain physical materials (the colour of the real thing, its roughness / sheen); the ikat pillows take the
    owner's carpet photos; the kids' rubber floor is laid as real 500 mm EPDM tiles. Kept: the owner's carpet photos, the plant /
    doner models' own textures, the wood and marble grain."""
def solid(name, rgb, rough=0.6, metal=0.0, sheen=0.0, coat=0.0, emit=None):
    mm = bpy.data.materials.get(name)
    if mm is None or not mm.use_nodes: return
    nt = mm.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bs.outputs[0], out.inputs[0])
    bs.inputs['Base Color'].default_value = (*rgb, 1); bs.inputs['Roughness'].default_value = rough; bs.inputs['Metallic'].default_value = metal
    for k_, v_ in (('Sheen Weight', sheen), ('Coat Weight', coat)):
        if k_ in bs.inputs: bs.inputs[k_].default_value = v_
    if emit:
        bs.inputs['Emission Color'].default_value = (*emit, 1); bs.inputs['Emission Strength'].default_value = 3.0
REAL = {  # material: (rgb, rough, metal, sheen, coat)
    'tent_f_t': ((0.86, 0.8, 0.68), 0.85, 0, 0.2, 0),              # ecru cotton canvas
    'velvet_f_t': ((0.35, 0.05, 0.07), 0.7, 0, 0.8, 0), 'velvet_f_t_cush': ((0.35, 0.05, 0.07), 0.7, 0, 0.8, 0),
    'velvet_wine_f_t': ((0.3, 0.04, 0.06), 0.7, 0, 0.8, 0), 'velvet_wine_f_t_cush': ((0.3, 0.04, 0.06), 0.7, 0, 0.8, 0),
    'rishtan_uv': ((0.1, 0.32, 0.62), 0.12, 0, 0, 0.9),             # Rishtan ishkor glaze (turquoise-cobalt)
    'pakhta_t': ((0.92, 0.93, 0.95), 0.1, 0, 0, 0.9),               # white porcelain
    'plov_t': ((0.8, 0.58, 0.3), 0.55, 0, 0, 0), 'bread_uv': ((0.62, 0.36, 0.16), 0.6, 0, 0, 0),
    'copper_t': ((0.85, 0.45, 0.28), 0.3, 1.0, 0, 0),
    'k_chalkboard': ((0.07, 0.09, 0.08), 0.85, 0, 0, 0),             # slate board
    'rattan_t': ((0.72, 0.56, 0.34), 0.6, 0, 0, 0),
    'beadikat_uv': ((0.7, 0.36, 0.14), 0.4, 0, 0, 0),               # amber glass beads
    'vase_turq_t': ((0.06, 0.48, 0.52), 0.12, 0, 0, 0.9), 'vase_cob_t': ((0.04, 0.12, 0.45), 0.12, 0, 0, 0.9), 'vase_isf_t': ((0.1, 0.3, 0.55), 0.12, 0, 0, 0.9),
    'pierced_brass': ((0.8, 0.6, 0.26), 0.3, 1.0, 0, 0), 'band2': ((0.6, 0.12, 0.1), 0.6, 0, 0, 0),
}
for nm_, (rgb, r_, mt_, sh_, ct_) in REAL.items(): solid(nm_, rgb, r_, mt_, sh_, ct_)
for nm_ in ('ikat2_t_cush', 'ikat2_t'):                                         # ikat pillows: the owner's carpet photo instead
    mm = bpy.data.materials.get(nm_)
    if mm and mm.use_nodes:
        for n_ in mm.node_tree.nodes:
            if n_.type == 'TEX_IMAGE': n_.image = bpy.data.images.load(os.path.join(TEX2, 'rug_p12.jpg'), check_existing=True)
# kids rubber floor -> real 500 mm EPDM tiles
PAT.clear(); KC = [mat(f'epdm_{k}', c, rough=0.9) for k, c in enumerate(((0.75, 0.42, 0.25), (0.35, 0.55, 0.45), (0.9, 0.75, 0.45), (0.45, 0.6, 0.75)))]
PAT['kidsfloor_t'] = (MORTAR, 0.002, _grid(lambda i, j: KC[(i * 3 + j) % 4], 0.497, 0.003), KC[0], 0.3)
HORIZ.clear(); HORIZ.add('kidsfloor_t'); SIDES.clear(); CULL_MINZ = TER + 0.05; HMINZ = -99.0
realize_all(skip=('Booth',)); CULL_MINZ = None
# ---------------------------------------------------------------- booths: chandeliers + curtains
_rm('Booth1_globes', 'Booth2_globes', 'Booth3_globes', 'Booth4_globes', 'Booth5_globes', 'Booth6_globes', 'Booth7_globes')
ZC7 = TER + 2.40
CURT = [mat(f'curtain_velvet_{k}', c, rough=0.7) for k, c in enumerate(((0.3, 0.04, 0.06), (0.05, 0.22, 0.24), (0.1, 0.18, 0.08), (0.42, 0.26, 0.06)))]
ncur = 0
for i, (y0, y1, x0, x1, key) in enumerate(D['booths']):
    t_ = bpy.data.objects.get(f'Booth{i + 1}_table')
    if t_:
        lo_, hi_ = _bb(t_); cx_, cy_ = (lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2
        mini_cascade(f'Booth{i + 1}_chandelier', cx_, cy_, ZC7 - 0.036, TER + 1.85, 'Booths', 0.16)
    # curtains at the opening (x = x0 + 0.08), one panel each side, gathered to a tie-back
    b = MB(); xr = x0 + 0.08; ya, yb_ = y0 + 0.06, y1 - 0.06; zr = ZC7 - 0.37; CM = CURT[i % 4]
    b.rod((xr, ya, zr), (xr, yb_, zr), 0.012, m['brass'], 12)
    for yy in (ya, yb_): b.lathe(xr, yy, zr - 0.015, [(0.0, 0.0), (0.022, 0.0), (0.025, 0.015), (0.0, 0.03)], m['brass'], 12)
    for side, (ye, s) in enumerate(((ya + 0.03, 1), (yb_ - 0.03, -1))):
        W_top = 0.52; ztie = TER + 1.10; ytie = ye + s * 0.07
        for k in range(9):
            yt = ye + s * W_top * k / 8; yb2 = ye + s * (0.06 + 0.3 * k / 8)
            dx = 0.03 * math.sin(k * 1.9)
            p0 = (xr + dx * 0.5, yt, zr - 0.02); p1 = (xr + 0.02 + dx, ytie + s * 0.012 * (k - 4) / 4, ztie); p2 = (xr + dx, yb2, ZP + 0.01)
            b.rod(p0, p1, 0.028, CM, 8); b.rod(p1, p2, 0.03, CM, 8)
        b.lathe(xr + 0.02, ytie, ztie - 0.03, [(0.0, 0.0), (0.06, 0.0), (0.065, 0.03), (0.06, 0.06), (0.0, 0.06)], m['brass'], 16)   # tie-back ring
        b.lathe(xr + 0.09, ytie, ztie - 0.25, [(0.0, 0.0), (0.03, 0.02), (0.035, 0.12), (0.012, 0.2), (0.0, 0.22)], CM, 10)      # tassel
        b.rod((xr + 0.09, ytie, ztie - 0.03), (xr + 0.03, ytie, ztie - 0.01), 0.004, m['brass'], 6)
    inst(b.mesh(f'Booth{i + 1}_curtains'), f'Booth{i + 1}_curtains', (0, 0, 0), 0, 'Booths'); ncur += 1
print('rev 11.7 real materials', len(REAL), 'booth curtains', ncur)
