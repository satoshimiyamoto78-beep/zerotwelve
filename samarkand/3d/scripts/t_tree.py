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

from mathutils import Vector
for me in a_chinar_trained(): o = bpy.data.objects.new('T', me); sc.collection.objects.link(o)
bpy.ops.mesh.primitive_plane_add(size=20); g = bpy.context.active_object; g.data.materials.append(X['brickpave'])
mb = MB(); mb.ring(0, 0, 0, [(1.0, 0.0), (1.45, 0.0), (1.45, 0.40), (1.0, 0.40)], X['majcobalt'], 96); mb.ring(0, 0, 0.4, [(0.97, 0.0), (1.48, 0.0), (1.48, 0.045), (0.97, 0.045)], m['walnut'], 96)
ob = bpy.data.objects.new('B', mb.mesh('rb')); sc.collection.objects.link(ob)
w = sc.world; w.node_tree.nodes['Background'].inputs[0].default_value = (0.8, 0.85, 0.95, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.8
ld = bpy.data.lights.new('sun', 'SUN'); ld.energy = 3.5; ld.angle = math.radians(4); so = bpy.data.objects.new('sun', ld); so.rotation_euler = (math.radians(35), 0, math.radians(60)); sc.collection.objects.link(so)
cd = bpy.data.cameras.new('cam'); cd.lens = 24; co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co)
loc, tgt = (4.2, -3.6, 1.3), (0, 0, 1.9)
co.location = loc; co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
sc.view_settings.exposure = 0.0; sc.cycles.samples = S; sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
