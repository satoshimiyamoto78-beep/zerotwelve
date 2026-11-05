"""rev. 10.0 (owner's plant + equipment models, archibase; .3ds converted with tools/max3ds2obj.py):
  date palm in a terracotta pot -> the four street palms; kentia palm in a wicker basket -> both sides of the corridor's dining end;
  round topiary (pot dropped) -> the low planter shrubs; sansevieria in a red vase -> both sides of the street entrance;
  bonsai in a stone tray -> host stand; doner machine -> mangal prep counter. Leaves decimated for the web viewer."""
LEAFG = mat('palm_leaf', (0.13, 0.3, 0.09), rough=0.5, coat=0.2); BARK = bl._mats.get('ficus_bark') or mat('ficus_bark', (0.16, 0.1, 0.06), rough=0.8)
MULCH = bl._mats.get('pebble_mulch') or mat('pebble_mulch', (0.42, 0.36, 0.3), rough=0.9)
def load_model(key, scale, rules=None, drop=(), leaf_ratio=0.35, ground=True):
    """import plants/<key>/m.obj, scale to metres, origin = footprint centre at the lowest point; rules(objname, lo, hi, H) -> material or
    None (keep the OBJ material); objects whose rule returns 'drop' are removed; leaf faces (material name contains 'leaf') decimated"""
    nm = f'Model_{key}'
    if nm in bpy.data.meshes: return bpy.data.meshes[nm]
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=os.path.join(PD, key, 'm.obj'))
    new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    for o in new:
        for v in o.data.vertices: v.co = (o.matrix_world @ v.co) * scale
        o.matrix_world = Matrix.Identity(4)
    zs = [v.co.z for o in new for v in o.data.vertices]; H = max(zs) - min(zs)
    keep = []
    for o in new:
        lo = [min(v.co[i] for v in o.data.vertices) for i in range(3)]; hi = [max(v.co[i] for v in o.data.vertices) for i in range(3)]
        r = rules(o.name, lo, hi, H, min(zs)) if rules else None
        if r == 'drop': bpy.data.objects.remove(o); continue
        if r is not None:
            o.data.materials.clear(); o.data.materials.append(r)
        keep.append(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in keep: o.select_set(True)
    bpy.context.view_layer.objects.active = keep[0]
    if len(keep) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active; me = o.data; me.name = nm
    leaf_i = [i for i, mm in enumerate(me.materials) if mm and ('leaf' in mm.name.lower() or mm.name.startswith(('green', 'leaves')))]
    if leaf_i and leaf_ratio < 1:
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT')
        for i in leaf_i: o.active_material_index = i; bpy.ops.object.material_slot_select()
        bpy.ops.mesh.decimate(ratio=leaf_ratio); bpy.ops.object.mode_set(mode='OBJECT')
    if len(me.polygons) > 8000:                                    # the rest (pots, baskets, trunks) at half density
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT')
        for i in [i for i in range(len(me.materials)) if i not in leaf_i]: o.active_material_index = i; bpy.ops.object.material_slot_select()
        bpy.ops.mesh.decimate(ratio=0.5); bpy.ops.object.mode_set(mode='OBJECT')
    vs = me.vertices; cx = sum(v.co.x for v in vs) / len(vs); cy = sum(v.co.y for v in vs) / len(vs); z0 = min(v.co.z for v in vs)
    lowv = [v for v in vs if v.co.z < z0 + 0.05 * H]
    if lowv: cx = sum(v.co.x for v in lowv) / len(lowv); cy = sum(v.co.y for v in lowv) / len(lowv)
    for v in vs: v.co.x -= cx; v.co.y -= cy; v.co.z -= z0
    bpy.data.objects.remove(o)
    me.name = nm + '_foliage' if leaf_i else nm                    # 'foliage' in the mesh name: leaves may brush other leaves (QA)
    return me
def rule_palm(pot_mat):
    def r(n, lo, hi, H, z0):
        if n.startswith('sub') or n.startswith('ArchInte10'): return LEAFG
        if hi[2] - lo[2] > 0.3 * H: return BARK
        if hi[2] - z0 < 0.25 * H and (hi[0] - lo[0]) > 0.15 * H: return pot_mat
        return MULCH
    return r
def rule_topiary(n, lo, hi, H, z0):
    if n.startswith('sub'): return LEAFG
    if n.startswith('archmodel1'): return BARK
    return 'drop'                                                  # pot + soil: planted straight into the planter
MODELS = {}
def M_(key, *a, **k):
    if key not in MODELS: MODELS[key] = load_model(key, *a, **k)
    return MODELS[key]
placed = []
def place_fixed(me, name, x, y, z, s, rz, cname):
    o_ = bpy.data.objects.new(name, me); o_.location = (x, y, z); o_.scale = (s, s, s); o_.rotation_euler = (0, 0, rz); coll(cname).objects.link(o_)
    if _clear(o_): placed.append(name); return o_
    bpy.data.objects.remove(o_); print('model not placed (blocked by', getattr(_clear, 'last', '?'), ')', name); return None
# ---------------------------------------------------------------- street palms -> date palm in terracotta pot
DP = M_('palm_date', 0.0254, rule_palm(TC['orange']), leaf_ratio=0.1)
for o_ in [o for o in bpy.data.objects if o.name.startswith('Street_palm')]:
    lo_, hi_ = _bb(o_); x, y = (lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2
    zs_ = max(lo_[2], -0.45); bpy.data.objects.remove(o_)
    r_ = place(DP, f'Palm_date_{len(placed)}', x, y, zs_, 1.0, 'Planting')
    if r_: placed.append(r_.name)
# ---------------------------------------------------------------- planter shrubs -> topiary
TP = M_('topiary', 0.0254, rule_topiary, leaf_ratio=0.12)
for o_ in [o for o in bpy.data.objects if o.name.startswith('Planter_shrub')]:
    lo_, hi_ = _bb(o_); x, y, z = (lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2, lo_[2]; bpy.data.objects.remove(o_)
    r_ = place(TP, f'Topiary_{len(placed)}', x, y, z, rq.uniform(0.72, 0.85), 'Planting')
    if r_: placed.append(r_.name)
# ---------------------------------------------------------------- kentia palms at the corridor's dining end
KP = M_('palm_kentia', 0.0254, rule_palm(X.get('rattan', TC['sand'])), leaf_ratio=0.15)
e0, e1 = D['ent']; t0, t1 = D['tun']
for k_, y in enumerate((e0 + 0.35, e1 - 0.35)):
    r_ = place(KP, f'Palm_kentia_{k_}', t0 - 0.38, y, TER, 0.95, 'Planting')
    if r_: placed.append(r_.name)
# ---------------------------------------------------------------- sansevieria vases either side of the street entrance (on the sidewalk)
SV = M_('sansevieria', 0.001, None, leaf_ratio=0.3)
for k_, y in enumerate((e0 - 0.45, e1 + 0.45)):
    place_fixed(SV, f'Sansevieria_{k_}', 12.9, y, -1.17, 0.85, rq.uniform(0, 6.28), 'Planting')
# ---------------------------------------------------------------- bonsai on the host stand, doner on the mangal prep counter
BN = M_('bonsai', 0.1, None, leaf_ratio=0.2)
hs = next((o for o in bpy.data.objects if o.name.startswith('Host_cabinet')), None)
if hs:
    lo_, hi_ = _bb(hs); place_fixed(BN, 'Bonsai_host', (lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2, hi_[2], 0.7, 0.3, 'Furniture')
DN = M_('doner', 0.001, None, leaf_ratio=1.0)
pr = next((o for o in bpy.data.objects if o.name.split('.')[0] == 'prep'), None)
if pr:
    lo_, hi_ = _bb(pr); dx_ = max(v.co.x for v in DN.vertices) - min(v.co.x for v in DN.vertices); dy_ = max(v.co.y for v in DN.vertices) - min(v.co.y for v in DN.vertices)
    rz_ = 0.0 if dy_ >= dx_ else math.pi / 2; dmin = min(dx_, dy_)
    sc_ = min(0.8, (hi_[0] - lo_[0] - 0.02) / dmin)
    bx = (max(v.co.x for v in DN.vertices) + min(v.co.x for v in DN.vertices)) / 2; by = (max(v.co.y for v in DN.vertices) + min(v.co.y for v in DN.vertices)) / 2
    c_, s_ = math.cos(rz_), math.sin(rz_); ox, oy = (bx * c_ - by * s_) * sc_, (bx * s_ + by * c_) * sc_
    sc_ = min(0.8, (hi_[0] - lo_[0] - 0.04) / dmin)
    ox, oy = (bx * c_ - by * s_) * sc_, (bx * s_ + by * c_) * sc_
    place_fixed(DN, 'Doner_machine', (lo_[0] + hi_[0]) / 2 - ox, lo_[1] + 0.6 - oy, hi_[2], sc_, rz_, 'Mangal')
print('rev 10.0 models placed', placed)
