"""Ortho drawing passes from the Samarkand model. Usage: passes2.py -- spec.json name
spec[name] = {cam:[x,y,z], rot:[rx,ry,rz] deg (or tgt:[x,y,z]), scale: metres across W, W, H,
              hide_prefix:[...], hide_coll:[...], cut:[axis, value, keep('-'|'+')]}
Writes cd/out/<name>_{n,d,o,c}.png (normal, depth, object id, cut-cap mask) + <name>.json (camera for the overlay)."""
import bpy, sys, json, bmesh, math
from mathutils import Vector, Euler
a = sys.argv[sys.argv.index('--') + 1:]
S = json.load(open(a[0]))[a[1]]; name = a[1]
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
sc = bpy.context.scene
HC = set(S.get('hide_coll', [])) | {'People', 'Context', 'Cameras'}
for o in list(bpy.data.objects):
    c = o.users_collection[0].name if o.users_collection else ''
    if c in HC or o.type in ('LIGHT', 'CAMERA') or any(o.name.startswith(h) for h in S.get('hide_prefix', [])) or any(o.name.endswith(h) or o.data and getattr(o.data,'name','').endswith(h) for h in S.get('hide_suffix', [])): bpy.data.objects.remove(o)
ONLY = S.get('only')
if ONLY:
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and o.name not in ONLY: bpy.data.objects.remove(o)
cut = S.get('cut')
if cut:
    ax = 'xyz'.index(cut[0]); val = float(cut[1]); keep = cut[2]
    no = Vector((0, 0, 0)); no[ax] = 1.0
    for o in list(bpy.data.objects):
        if o.type != 'MESH': continue
        mw = o.matrix_world; P = [mw @ Vector(v) for v in o.bound_box]; lo = min(p[ax] for p in P); hi = max(p[ax] for p in P)
        if (keep == '-' and lo > val) or (keep == '+' and hi < val): bpy.data.objects.remove(o); continue
        if lo < val < hi:
            me = o.data.copy(); o.data = me; bm = bmesh.new(); bm.from_mesh(me); bm.transform(mw)
            r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=no * val, plane_no=no,
                                       clear_outer=(keep == '-'), clear_inner=(keep == '+'))
            cut_e = [e for e in r['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
            caps = []
            if cut_e:
                try: caps = bmesh.ops.holes_fill(bm, edges=cut_e, sides=0)['faces']
                except Exception: caps = []
            lay = bm.faces.layers.float.get('cap') or bm.faces.layers.float.new('cap')
            for f in bm.faces: f[lay] = 0.0
            for f in caps:
                if f.is_valid: f[lay] = 1.0
            bm.transform(mw.inverted()); bm.to_mesh(me); bm.free()
sc.render.engine = 'CYCLES'; sc.cycles.samples = 1; sc.cycles.use_denoising = False; sc.cycles.max_bounces = 0
sc.cycles.pixel_filter_type = 'BOX'; sc.cycles.filter_width = 0.01; sc.render.dither_intensity = 0.0
sc.render.resolution_x, sc.render.resolution_y = int(S['W']), int(S['H']); sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Raw'
w = sc.world or bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0, 0, 0, 1)
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'; cd.ortho_scale = S['scale']; cd.clip_end = 400; cd.clip_start = 0.01
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = Vector(S['cam'])
if 'rot' in S: cam.rotation_euler = Euler([math.radians(v) for v in S['rot']])
else: cam.rotation_euler = (Vector(S['tgt']) - cam.location).to_track_quat('-Z', 'Y').to_euler()
def emit_mat(kind):
    m = bpy.data.materials.new('pass_' + kind); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission'); nt.links.new(em.outputs[0], out.inputs[0])
    if kind == 'n':
        g = nt.nodes.new('ShaderNodeNewGeometry'); mp = nt.nodes.new('ShaderNodeVectorMath'); mp.operation = 'MULTIPLY_ADD'
        mp.inputs[1].default_value = (0.5, 0.5, 0.5); mp.inputs[2].default_value = (0.5, 0.5, 0.5)
        nt.links.new(g.outputs['Normal'], mp.inputs[0]); nt.links.new(mp.outputs[0], em.inputs[0])
    elif kind == 'd':
        cdat = nt.nodes.new('ShaderNodeCameraData'); mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 120.0
        nt.links.new(cdat.outputs['View Z Depth'], mr.inputs['Value']); nt.links.new(mr.outputs[0], em.inputs[0])
    elif kind == 'o':
        oi = nt.nodes.new('ShaderNodeObjectInfo'); h = nt.nodes.new('ShaderNodeCombineColor'); h.mode = 'HSV'
        nt.links.new(oi.outputs['Random'], h.inputs[0]); h.inputs[1].default_value = 1.0; h.inputs[2].default_value = 1.0
        nt.links.new(h.outputs[0], em.inputs[0])
    else:
        at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'cap'; nt.links.new(at.outputs['Fac'], em.inputs[0])
    return m
for kind in ('n', 'd', 'o', 'c'):
    sc.view_layers[0].material_override = emit_mat(kind)
    st = sc.render.image_settings; st.color_mode = 'BW' if kind in ('d', 'c') else 'RGB'; st.color_depth = '16' if kind == 'd' else '8'
    sc.render.filepath = f'cd/out/{name}_{kind}.png'; bpy.ops.render.render(write_still=True)
mw = cam.matrix_world
json.dump({'cam': list(cam.location), 'right': list(mw.col[0].xyz), 'up': list(mw.col[1].xyz), 'scale': S['scale'], 'W': S['W'], 'H': S['H']}, open(f'cd/out/{name}.json', 'w'))
print('ok', name)
