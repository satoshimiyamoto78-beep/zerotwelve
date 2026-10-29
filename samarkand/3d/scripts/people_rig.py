"""Pose the owner's T-posed low-poly people: auto-rig (bone heat), pose (stand / sit), apply, smooth, dress by regions.
Usage: bvenv/bin/python r3d/people_rig.py FBX OUT.blend PREVIEW.png"""
import sys, math, bpy, bmesh
from mathutils import Vector, Matrix
FBX, OUT, PNG = sys.argv[1:4]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)
bpy.context.view_layer.update()
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for o in meshes: o.hide_viewport = False; o.hide_set(False)      # two of them import hidden (not evaluated by the depsgraph)
for o in meshes:                                   # bake transforms: metres, Z up, feet at z 0, centred
    o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
    if max(v.co.z for v in o.data.vertices) > 10:  # two of the six came without the cm->m / Y-up conversion
        o.data.transform(Matrix.Scale(0.01, 4) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
    vs = [v.co for v in o.data.vertices]; c = Vector(((min(v.x for v in vs) + max(v.x for v in vs)) / 2, (min(v.y for v in vs) + max(v.y for v in vs)) / 2, min(v.z for v in vs)))
    o.data.transform(Matrix.Translation(-c))
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)    # the exports are triangle soup: weld
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
def stats(o):
    vs = [v.co for v in o.data.vertices]; H = max(v.z for v in vs); W = max(v.x for v in vs)
    return H, W
def joints(o):
    """joint heights from the mesh: arm line = z of the widest vertices; hips / knees / ankles by proportion"""
    H, W = stats(o); vs = [v.co for v in o.data.vertices]
    arm = sorted(vs, key=lambda v: -abs(v.x))[:20]; za = sum(v.z for v in arm) / len(arm)
    legx = sum(abs(v.x) for v in vs if 0.3 * H < v.z < 0.4 * H) / max(1, len([v for v in vs if 0.3 * H < v.z < 0.4 * H]))
    return dict(H=H, W=W, arm=za, hip=0.53 * H, knee=0.285 * H, ankle=0.05 * H, legx=legx, sh=0.115 * H, neck=0.83 * H)
def build_rig(o, J):
    arm = bpy.data.armatures.new('rig'); ob = bpy.data.objects.new(o.name + '_rig', arm); bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.mode_set(mode='EDIT'); eb = arm.edit_bones
    def bone(n, h, t, parent=None):
        b = eb.new(n); b.head = h; b.tail = t
        if parent: b.parent = eb[parent]; b.use_connect = (Vector(eb[parent].tail) - Vector(h)).length < 1e-4
        return b
    H, za = J['H'], J['arm']
    bone('hips', (0, 0, J['hip']), (0, 0, J['hip'] + 0.12 * H)); bone('spine', (0, 0, J['hip'] + 0.12 * H), (0, 0, J['neck']), 'hips')
    bone('neck', (0, 0, J['neck']), (0, 0, 0.9 * H), 'spine'); bone('head', (0, 0, 0.9 * H), (0, 0, H), 'neck')
    for s, n in ((1, 'L'), (-1, 'R')):
        lx = s * J['legx']
        bone('thigh.' + n, (lx, 0, J['hip']), (lx, 0, J['knee']), 'hips'); bone('shin.' + n, (lx, 0, J['knee']), (lx, 0, J['ankle']), 'thigh.' + n)
        bone('foot.' + n, (lx, 0, J['ankle']), (lx, -0.12, 0.02), 'shin.' + n)
        bone('clav.' + n, (s * 0.03, 0, za), (s * J['sh'], 0, za), 'spine')
        ex = s * (J['sh'] + (J['W'] - J['sh']) * 0.42); wx = s * (J['sh'] + (J['W'] - J['sh']) * 0.83)
        bone('upper.' + n, (s * J['sh'], 0, za), (ex, 0, za), 'clav.' + n); bone('fore.' + n, (ex, 0, za), (wx, 0, za), 'upper.' + n)
        bone('hand.' + n, (wx, 0, za), (s * J['W'], 0, za), 'fore.' + n)
    bpy.ops.object.mode_set(mode='OBJECT')
    # geometric skinning: inverse-distance weights to the two nearest bone segments (side-locked for limbs)
    segs = [(b.name, Vector(b.head_local), Vector(b.tail_local)) for b in arm.bones]
    groups = {n: o.vertex_groups.new(name=n) for n, _, _ in segs}
    def dseg(p, a, b):
        ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(1e-9, ab.length_squared))); return (a + ab * t - p).length
    for v in o.data.vertices:
        p = v.co; side = 'L' if p.x > 0 else 'R'
        cand = [(dseg(p, a, b), n) for n, a, b in segs if not (n.endswith('.L') and side == 'R') and not (n.endswith('.R') and side == 'L')]
        if p.z < J['hip'] - 0.05 * J['H']: cand = [c for c in cand if c[1].split('.')[0] in ('thigh', 'shin', 'foot', 'hips')]
        cand.sort(); (d1, n1), (d2, n2) = cand[0], cand[1]
        w1, w2 = 1 / (d1 + 1e-3) ** 4, 1 / (d2 + 1e-3) ** 4; t_ = w1 + w2
        groups[n1].add([v.index], w1 / t_, 'REPLACE'); groups[n2].add([v.index], w2 / t_, 'ADD')
    md = o.modifiers.new('arm', 'ARMATURE'); md.object = ob
    return ob
res = []
for o in meshes:
    J = joints(o); rig = build_rig(o, J)
    ok = sum(1 for v in o.data.vertices if len(v.groups) > 0)
    print(o.name, 'H %.2f W %.2f arm %.2f' % (J['H'], J['W'], J['arm']), 'weighted verts', ok, '/', len(o.data.vertices))
    res.append((o, rig, J))
from mathutils import Quaternion
# deltas in ARMATURE space (axis, degrees), relative to the parent: the figure faces -Y
POSES = {'stand': {'upper.L': ((0, 1, 0), 80), 'upper.R': ((0, 1, 0), -80), 'fore.L': ((1, 0, 0), -14), 'fore.R': ((1, 0, 0), -10)},
         'sit': {'upper.L': ((0, 1, 0), 78), 'upper.R': ((0, 1, 0), -78), 'fore.L': ((1, 0, 0), -70), 'fore.R': ((1, 0, 0), -70),
                 'thigh.L': ((1, 0, 0), -88), 'thigh.R': ((1, 0, 0), -88), 'shin.L': ((1, 0, 0), 88), 'shin.R': ((1, 0, 0), 88), 'foot.L': ((1, 0, 0), 0), 'foot.R': ((1, 0, 0), 0)},
         'sitc': {'upper.L': [((0, 1, 0), 82), ((1, 0, 0), -12)], 'upper.R': [((0, 1, 0), -82), ((1, 0, 0), -12)],      # chair: elbows forward over the armrests,
                  'fore.L': ((1, 0, 0), -58), 'fore.R': ((1, 0, 0), -58),                                                   # hands resting in the lap, under the table edge
                  'thigh.L': ((1, 0, 0), -70), 'thigh.R': ((1, 0, 0), -70), 'shin.L': ((1, 0, 0), 70), 'shin.R': ((1, 0, 0), 70)},
         'sitb': {'upper.L': [((0, 1, 0), 82), ((1, 0, 0), -12)], 'upper.R': [((0, 1, 0), -82), ((1, 0, 0), -12)],      # banquette (seat 0.44)
                  'fore.L': ((1, 0, 0), -58), 'fore.R': ((1, 0, 0), -58),
                  'thigh.L': ((1, 0, 0), -77), 'thigh.R': ((1, 0, 0), -77), 'shin.L': ((1, 0, 0), 77), 'shin.R': ((1, 0, 0), 77)}}
def pose(rig, name):
    for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = (1, 0, 0, 0)
    for n, spec in POSES[name].items():
        pb = rig.pose.bones[n]; R = pb.bone.matrix_local.to_quaternion(); Q = Quaternion()
        for ax, deg in (spec if isinstance(spec, list) else [spec]): Q = Quaternion(Vector(ax), math.radians(deg)) @ Q
        pb.rotation_quaternion = R.inverted() @ Q @ R
bpy.context.view_layer.update()
LIB = sys.argv[4] if len(sys.argv) > 4 else None
SLOTS = ('skin', 'hair', 'top', 'bottom', 'shoes')
DRESS = {3, 4, 5, 6}                                                 # figure numbers wearing dresses (checked on the preview)
def dress(o, me, J, idx):
    """material slot per face from the dominant bone + region rules (vertex groups are carried by new_from_object)"""
    H = J['H']; vs = o.data.vertices
    skirt = idx in DRESS
    gname = {vg.index: vg.name for vg in o.vertex_groups}
    hc = sum((v.co for v in vs if v.co.z > 0.9 * H), Vector()) / max(1, sum(1 for v in vs if v.co.z > 0.9 * H))
    def slot(v):
        b = gname[max(v.groups, key=lambda e: e.weight).group].split('.')[0] if v.groups else 'spine'
        z = v.co.z
        if b in ('head', 'neck'):
            if b == 'head' and (z > 0.935 * H or v.co.y > hc.y + 0.035): return 1
            return 0
        if b == 'hand': return 0
        if b == 'foot': return 4
        if skirt:
            if z < 0.33 * H: return 0 if z > 0.07 * H else 4
            return 2
        if b in ('thigh', 'shin', 'hips', 'spine') and z < 0.55 * H: return 3 if z > 0.065 * H else 4     # trousers up to a straight waist line
        return 2
    vslot = [slot(v) for v in vs]
    me.materials.clear()
    for nm in SLOTS: me.materials.append(bpy.data.materials.get('h_' + nm) or bpy.data.materials.new('h_' + nm))
    for p_ in me.polygons:
        c = [vslot[i] for i in p_.vertices]; p_.material_index = max(set(c), key=c.count)
    return skirt
bpy.context.view_layer.update()
from mathutils.bvhtree import BVHTree
def watertight(me, vox):
    """voxel remesh -> closed manifold shell; material index of each new face from the nearest source face"""
    src = me.copy(); tmp = bpy.data.objects.new('_wt', me); bpy.context.scene.collection.objects.link(tmp)
    md = tmp.modifiers.new('rm', 'REMESH'); md.mode = 'VOXEL'; md.voxel_size = vox; md.use_smooth_shade = True
    dg = bpy.context.evaluated_depsgraph_get(); out = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.context.scene.collection.objects.unlink(tmp); bpy.data.objects.remove(tmp)
    bm = bmesh.new(); bm.from_mesh(out); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-4); bmesh.ops.holes_fill(bm, edges=bm.edges, sides=12); bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context='EDGES'); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_edges], context='VERTS'); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(out); bm.free()
    tree = BVHTree.FromPolygons([v.co for v in src.vertices], [list(p.vertices) for p in src.polygons])
    out.materials.clear()
    for mm in src.materials: out.materials.append(mm)
    for p in out.polygons:
        hit = tree.find_nearest(p.center)
        p.material_index = src.polygons[hit[2]].material_index if hit[2] is not None else 2
    for k_ in ('skirt',):
        if k_ in src: out[k_] = src[k_]
    nm_ = me.name; bpy.data.meshes.remove(src); bpy.data.meshes.remove(me); out.name = nm_
    return out
x = 0.0; lib = []
for k_, (o, rig, J) in enumerate(res):
    for k, nm in enumerate(('stand', 'sit', 'sitc', 'sitb')):
        pose(rig, nm); bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        me.name = f'Human_{k_ + 1}_{nm}'
        skirt = dress(o, me, J, k_ + 1)                                     # same vertex order as the rest mesh: classify first, then weld
        me = watertight(me, 0.015)
        # face +Y like the rest of the asset library; origin: floor (stand) or the seat contact (sit) under the pelvis
        me.transform(Matrix.Rotation(math.pi, 4, 'Z'))
        if nm in ('sit', 'sitc', 'sitb'):
            z0_ = min(v.co.z for v in me.vertices)
            th = [v.co.z for v in me.vertices if v.co.y < 0.12]                                     # seat contact: the buttocks (behind the knees' drop)
            me.transform(Matrix.Translation((0, 0, -min(th)))); me['feet'] = round(z0_ - min(th), 3)
        else: me.transform(Matrix.Translation((0, 0, -min(v.co.z for v in me.vertices))))
        me['kit'] = 1; me['skirt'] = int(skirt)
        for p_ in me.polygons: p_.use_smooth = True
        ob2 = bpy.data.objects.new(me.name, me); bpy.context.scene.collection.objects.link(ob2); ob2.location = (x, k * 1.5, 0)
        ob2.modifiers.new('ss', 'SUBSURF').levels = 1; lib.append(me)
    x += 1.0
    o.hide_render = True; rig.hide_render = True
cols = {'h_skin': (0.75, 0.55, 0.42), 'h_hair': (0.08, 0.05, 0.04), 'h_top': (0.85, 0.82, 0.76), 'h_bottom': (0.15, 0.2, 0.32), 'h_shoes': (0.1, 0.07, 0.05)}
for n_, c_ in cols.items():
    mm = bpy.data.materials[n_]; mm.node_tree.nodes['Principled BSDF'].inputs[0].default_value = (*c_, 1)
if LIB:
    for me in lib: me.use_fake_user = True
    bpy.data.libraries.write(LIB, set(lib), fake_user=True)
    print('library', LIB, [(me.name, len(me.polygons), me['skirt'], me.get('feet')) for me in lib])
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 16; sc.render.resolution_x, sc.render.resolution_y = 1800, 700
w = bpy.data.worlds.new('w'); sc.world = w; w.node_tree.nodes['Background'].inputs[1].default_value = 1.0
ld = bpy.data.lights.new('s', 'SUN'); ld.energy = 3; so = bpy.data.objects.new('s', ld); so.rotation_euler = (0.9, 0, 0.6); sc.collection.objects.link(so)
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'; cd.ortho_scale = 6.6; co = bpy.data.objects.new('c', cd); sc.collection.objects.link(co)
co.location = (2.6, 8, 1.6); co.rotation_euler = (math.radians(85), 0, math.radians(180 + 12)); sc.camera = co
sc.render.filepath = PNG; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
