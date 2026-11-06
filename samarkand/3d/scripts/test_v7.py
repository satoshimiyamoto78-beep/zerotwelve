"""Asset test sheet for assets_v4: builds the new assets standalone, prints mesh QA, renders material + clay/wire rows.
Usage: bvenv/bin/python r3d/test_v4.py OUT.png [W H S] [names,...]"""
import sys, os, math, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector
import bl, bl2
from bl import mat
HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[1:]; OUT = argv[0]; W, H, S = (int(argv[1]), int(argv[2]), int(argv[3])) if len(argv) > 3 else (1800, 900, 32)
ONLY = argv[4].split(',') if len(argv) > 4 else None
sc = bl2.reset(sky=False, exposure=0.3)
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
m = bl2.M2(); m.update(bronze=mat('bronze', (0.12, 0.10, 0.08), rough=0.45, metal=0.7), velvet=mat('velvet', (0.42, 0.14, 0.05), rough=0.75))
COLS = {}
def coll(name):
    if name not in COLS:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); COLS[name] = c
    return COLS[name]
src = open(os.path.join(HERE, 'detail_r12.py')).read(); __file__ = os.path.join(HERE, 'detail_r12.py')
exec(src[:src.index('def ceil_at')])
exec(open(os.path.join(HERE, 'assets_v4.py')).read()); exec(open(os.path.join(HERE, 'assets_v5.py')).read()); exec(open(os.path.join(HERE, 'assets_v6.py')).read()); exec(open(os.path.join(HERE, 'assets_v7.py')).read())
exec(open(os.path.join(HERE, 'qa.py')).read().split("meshes, objs = {}, []")[0].split("bpy.ops.wm.open_mainfile(filepath=BLEND)")[1])
B = [('cab1', lambda: a_jali_cabinet(0.6, 0.55, 1.05, 1)), ('cab2', lambda: a_jali_cabinet(1.4, 0.45, 0.9, 2)), ('chair', lambda: a_carvedchair('k1'))]
if ONLY: B = [b for b in B if b[0] in ONLY]
clay = bpy.data.materials.new('clay_wire'); N = clay.node_tree.nodes; L = clay.node_tree.links
b_ = N['Principled BSDF']; wf = N.new('ShaderNodeWireframe'); wf.use_pixel_size = True; wf.inputs['Size'].default_value = 0.7
mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs['A'].default_value = (0.78, 0.74, 0.68, 1); mix.inputs['B'].default_value = (0.12, 0.2, 0.45, 1)
L.new(wf.outputs['Fac'], mix.inputs['Factor']); L.new(mix.outputs['Result'], b_.inputs['Base Color'])
x = 0.0; rep = {}
for nm, fn in B:
    me = fn(); r = mesh_report(me); rep[nm] = {k: v for k, v in r.items() if v and k not in ('uv',)}
    vs = [v.co for v in me.vertices]; lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))); hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    sz = hi - lo
    for row, cl in ((0, False), (1, True)):
        me2 = me if not cl else me.copy()
        if cl: me2.materials.clear(); me2.materials.append(clay)
        o = bpy.data.objects.new(nm, me2); sc.collection.objects.link(o); o.rotation_euler = (0, 0, -0.5 + math.pi)
        o.location = (x + sz.x / 2 - (lo.x + sz.x / 2), row * -2.2 - (lo.y + sz.y / 2), -lo.z + (0 if hi.z < 0.01 else 0))
    x += max(sz.x, sz.y) * 1.2 + 0.25
print(json.dumps(rep, indent=0))
bpy.ops.mesh.primitive_plane_add(size=80, location=(x / 2, -1, 0)); g = bpy.context.active_object
gm = bpy.data.materials.new('gs'); gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.85, 0.82, 0.77, 1); g.data.materials.append(gm)
w = sc.world; w.node_tree.nodes['Background'].inputs[0].default_value = (0.9, 0.88, 0.84, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.8
ld = bpy.data.lights.new('sun', 'SUN'); ld.energy = 3.0; ld.angle = math.radians(8); so = bpy.data.objects.new('sun', ld); so.rotation_euler = (math.radians(50), 0, math.radians(30)); sc.collection.objects.link(so)
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = x * 1.02
co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co); co.location = (x / 2 - 0.15, -14.0, 7.5)
d = Vector((x / 2 - 0.15, -1.1, 0.9)) - co.location; co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
sc.view_settings.exposure = 0.2; sc.cycles.samples = S
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
