"""rev. 9.7 (owner: 'plants are poor and generic' + supplied models): the owner's ficus (braided trunk, archibase 'Plant house 2', OBJ in dm)
replaces the generic plumerias, planter pomegranates and the photo-zone areca (planted in the soil, its pot dropped, pebble mulch kept)
and the potted pomegranate on the aivan corner (with its own white ceramic pot). Leaves decimated to ~30 % for the web viewer."""
import random as _rq
PD = os.path.join(HERE, 'plants')
def load_ficus():
    if 'Ficus_foliage_src' in bpy.data.meshes: return bpy.data.meshes['Ficus_foliage_src'], bpy.data.meshes['Ficus_foliage_nopot']
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=os.path.join(PD, 'Plant house 2 N261220.obj'))
    o = [x for x in bpy.data.objects if x not in before][0]
    me = o.data; me.name = 'Ficus_foliage_src'
    for v in me.vertices: v.co = o.matrix_world @ v.co
    o.matrix_world = Matrix.Identity(4)
    import bmesh as _bm
    bm = _bm.new(); bm.from_mesh(me)
    cx = sum(v.co.x for v in bm.verts if v.co.z < 3.6) / max(1, len([v for v in bm.verts if v.co.z < 3.6])); cy = sum(v.co.y for v in bm.verts if v.co.z < 3.6) / max(1, len([v for v in bm.verts if v.co.z < 3.6]))
    for v in bm.verts: v.co.x = (v.co.x - cx) * 0.1; v.co.y = (v.co.y - cy) * 0.1; v.co.z = (v.co.z - 0.076) * 0.1      # dm -> m, origin = pot base centre
    bm.to_mesh(me); bm.free()
    # materials: leaves textured, bark, white ceramic pot, pebble mulch
    leaf = bpy.data.materials.new('ficus_leaf'); leaf.use_nodes = True; N = leaf.node_tree.nodes; b = N['Principled BSDF']
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(PD, 'leaf-lin.jpg'), check_existing=True)
    leaf.node_tree.links.new(it.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.45
    b.inputs['Subsurface Weight'].default_value = 0.15 if 'Subsurface Weight' in b.inputs else 0
    MATS = {'green': leaf, 'broun': mat('ficus_bark', (0.16, 0.1, 0.06), rough=0.8, bump=0.6), 'st_tile': mat('pot_ceramic_white', (0.86, 0.84, 0.8), rough=0.3, coat=0.4),
            'st_yellow': mat('pebble_mulch', (0.42, 0.36, 0.3), rough=0.9, bump=0.8, noise_var=0.2)}
    for i, mm in enumerate(me.materials):
        k = next((k for k in MATS if mm and mm.name.startswith(k)), None)
        if k: me.materials[i] = MATS[k]
    # decimate the foliage only
    leaf_i = [i for i, mm in enumerate(me.materials) if mm is leaf]
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT')
    for i in leaf_i: o.active_material_index = i; bpy.ops.object.material_slot_select()
    bpy.ops.mesh.decimate(ratio=0.3); bpy.ops.object.mode_set(mode='OBJECT')
    # pot-less copy (planted in soil)
    me2 = me.copy(); me2.name = 'Ficus_foliage_nopot'
    bm = _bm.new(); bm.from_mesh(me2)
    pot_i = [i for i, mm in enumerate(me2.materials) if mm and mm.name.startswith('pot_ceramic')]
    _bm.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in pot_i], context='FACES')
    _bm.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    zb = min(v.co.z for v in bm.verts if True)
    for v in bm.verts: v.co.z -= zb                                                    # lowest point (trunk foot) on the soil
    bm.to_mesh(me2); bm.free()
    bpy.data.objects.remove(o)
    return me, me2
FIC, FIC_NP = load_ficus()
rq = _rq.Random(11); nrep = 0
from mathutils.bvhtree import BVHTree as _BVH
def _tree(o_):
    mw = o_.matrix_world; nm = mw.to_3x3().inverted_safe().transposed()
    vs = [mw @ v.co - (nm @ v.normal).normalized() * 0.002 for v in o_.data.vertices]
    return _BVH.FromPolygons(vs, [list(p.vertices) for p in o_.data.polygons])
def _clear(o_):
    bpy.context.view_layer.update(); lo, hi = _bb(o_); t = None
    for q in bpy.data.objects:
        if q is o_ or q.type != 'MESH' or not q.data.polygons or q.name.startswith(('Bougainvillea', 'Jasmine', 'Banana', 'Street_palm', 'Herbs', 'Planter_shrub', 'Olive', 'Croton', 'Ficus', 'roof_panel', 'terrace_floor', 'planter_soil', 'photo_plant_soil', 'ground', 'sidewalk')): continue
        ql, qh = _bb(q)
        if any(ql[k] > hi[k] or lo[k] > qh[k] for k in range(3)): continue
        if t is None: t = _tree(o_)
        if t.overlap(_tree(q)): _clear.last = q.name; return False
    return True
def place(me, name, x, y, z, s, cname):
    o_ = bpy.data.objects.new(name, me); o_.location = (x, y, z); coll(cname).objects.link(o_)
    for k in range(16):                                                    # largest scale / turn whose crown touches nothing
        sk = s * (1.0 - 0.08 * (k // 2)); o_.scale = (sk, sk, sk); o_.rotation_euler = (0, 0, rq.uniform(0, 6.28))
        if _clear(o_): return o_
    print('ficus dropped at', round(x, 2), round(y, 2), 'blocked by', getattr(_clear, 'last', '?')); bpy.data.objects.remove(o_); return None
for o_ in [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(('Plumeria', 'Pomegranate', 'Areca'))]:
    lo_, hi_ = _bb(o_); x, y, z = (lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2, lo_[2]; H = hi_[2] - lo_[2]; nm = o_.name
    pot_ = None
    if nm.startswith('Pomegranate'):
        for p_ in [p for p in bpy.data.objects if p.type == 'MESH' and p.name.split('.')[0] == 'pot']:
            pl, ph = _bb(p_)
            if pl[0] - 0.05 < x < ph[0] + 0.05 and pl[1] - 0.05 < y < ph[1] + 0.05 and abs(ph[2] - z) < 0.05: pot_ = p_
    bpy.data.objects.remove(o_)
    if pot_:
        pl, ph = _bb(pot_); bpy.data.objects.remove(pot_)
        place(FIC, f'Ficus_potted_{nrep}', (pl[0] + ph[0]) / 2, (pl[1] + ph[1]) / 2, pl[2], rq.uniform(1.05, 1.2), 'Planting')
    else:
        s = max(1.1, min(1.6, max(H, 1.4) / 1.3)) * rq.uniform(0.92, 1.08)
        place(FIC_NP, f'Ficus_planted_{nrep}', x, y, z, s, 'Planting')
    nrep += 1
print('rev 9.7 ficus placed', nrep)
