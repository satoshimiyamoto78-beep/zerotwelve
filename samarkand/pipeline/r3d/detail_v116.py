"""rev. 11.6 (owner):
  * tables: no pattern anywhere — every table top plain walnut (hall carved tables, tent octagonal tables, trestles)
  * aivan floor: no timber deck — terracotta brick pavers 300 x 150 laid in a pinwheel around 150 glazed inserts (owner refs:
    warm peach / tan pavers, green, cobalt, white-green chequer and star inserts), 3 mm joints
  * aivan wall: the hall doors behind the wall carpets (and their handles) removed; the 'Samarkand' ad screen on the aivan removed
  * booths: plain walnut podium riser, partitions run to the aisle so no settee back sticks out (detail_v101);
    ceiling coffers mixed (detail_v109)"""
# ---- plain wood tables
WDp = XW['wd']; ntp = 0
for mmn in ('zfield_t', 'octa_inlay_uv'):
    for o_ in bpy.data.objects:
        if o_.type == 'MESH':
            for i_, m_ in enumerate(o_.data.materials):
                if m_ and m_.name == mmn: o_.data.materials[i_] = WDp; ntp += 1
# ---- remove the doors behind the aivan carpets + the ad screen
_rm('Hall_door_cd_n', 'Hall_door_de_s', 'Hall_door_de_n')
for o_ in bpy.data.objects:
    if o_.type == 'MESH' and o_.name.startswith('Aivan_screen'):
        me_ = o_.data
        if any(m_ and m_.name == 'ad_screen_uv' for m_ in me_.materials):
            bm_ = _bm12.new(); bm_.from_mesh(me_)
            idx_ = {i for i, m_ in enumerate(me_.materials) if m_ and m_.name == 'ad_screen_uv'}
            for f in bm_.faces:
                if f.material_index in idx_: f.material_index = list(me_.materials).index(WDp) if WDp in list(me_.materials) else f.material_index
            bm_.to_mesh(me_); bm_.free()
            for i, m_ in enumerate(me_.materials):
                if m_ and m_.name == 'ad_screen_uv': me_.materials[i] = WDp
# ---- aivan floor: brick pinwheel with glazed inserts
PAV = [mat(f'paver_{k}', c, rough=0.85, bump=0.25, noise_var=0.05) for k, c in enumerate(((0.80, 0.55, 0.42), (0.76, 0.5, 0.38), (0.83, 0.6, 0.47), (0.72, 0.48, 0.34)))]
INS = [mat('ins_green', (0.02, 0.22, 0.14), rough=0.15, coat=0.8), TILE[0], TILE[2], mat('ins_white', (0.9, 0.88, 0.82), rough=0.15, coat=0.8)]
L_, W_, J_ = 0.30, 0.15, 0.003; S_ = L_ - W_
rnd16 = _rnd.Random(16)
def pinwheel(u0, v0, u1, v1):
    v1_, v2_ = (L_, W_), (-W_, L_)
    det = L_ * L_ + W_ * W_
    def ij(x, y): return ((x * L_ + y * W_) / det, (-x * W_ + y * L_) / det)
    cs = [ij(u0, v0), ij(u1, v0), ij(u1, v1), ij(u0, v1)]
    for i in range(math.floor(min(c[0] for c in cs)) - 2, math.ceil(max(c[0] for c in cs)) + 2):
        for j in range(math.floor(min(c[1] for c in cs)) - 2, math.ceil(max(c[1] for c in cs)) + 2):
            ox, oy = i * v1_[0] + j * v2_[0], j * v2_[1] + i * v1_[1]
            sq = _box(ox + J_, oy + J_, ox + S_ - J_, oy + S_ - J_)
            k = (i * 3 + j * 7) % 6
            if k == 5:                                                               # chequer insert (white / green)
                h = S_ / 2
                for a_ in range(2):
                    for b_ in range(2):
                        yield _box(ox + a_ * h + J_, oy + b_ * h + J_, ox + (a_ + 1) * h - J_, oy + (b_ + 1) * h - J_), INS[3] if (a_ + b_) % 2 else INS[0]
            elif k == 4:                                                             # cobalt square with a white diamond (star insert)
                c_ = (ox + S_ / 2, oy + S_ / 2); r_ = S_ * 0.3
                dia = _P([(c_[0] - r_, c_[1]), (c_[0], c_[1] - r_), (c_[0] + r_, c_[1]), (c_[0], c_[1] + r_)])
                yield sq.difference(dia.buffer(J_, join_style=2)), INS[1]; yield dia, INS[3]
            else: yield sq, INS[k % 3]
            yield _box(ox + S_ + J_, oy + J_, ox + S_ + W_ - J_, oy + L_ - J_), PAV[rnd16.randrange(4)]           # A (vertical)
            yield _box(ox - W_ + J_, oy + S_ + J_, ox + S_ - J_, oy + S_ + W_ - J_), PAV[rnd16.randrange(4)]     # B (horizontal)
o_ = bpy.data.objects.get('aivan_deck')
nav = 0
if o_:
    for i_, m_ in enumerate(o_.data.materials):
        if m_ and m_.name == 'deck2': o_.data.materials[i_] = mat('aivan_paver_bed', (0.8, 0.55, 0.42))
    PAT.clear(); PAT['aivan_paver_bed'] = (MORTAR, 0.002, pinwheel, PAV[0], 0.2)
    HORIZ.clear(); HORIZ.add('aivan_paver_bed'); SIDES.clear(); UVS = 0.6; CULL_MINZ = 0.0 + 0.001
    HMINZ = -0.2; realize_all(skip=('Booth',)); CULL_MINZ = None; HMINZ = -99.0; nav = nobj
print('rev 11.6 plain tables', ntp, 'aivan floor pavers', nav)
