import bpy, math, sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 24; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3
sc.render.resolution_x, sc.render.resolution_y = 1000, 700; sc.render.image_settings.file_format = 'JPEG'
if not sc.world: sc.world = bpy.data.worlds.new('w')
sc.world.use_nodes = True; bg = sc.world.node_tree.nodes.get('Background'); bg.inputs[1].default_value = 1.2; bg.inputs[0].default_value = (0.9, 0.9, 0.95, 1)
for o in list(bpy.data.objects):
    pass
ld = bpy.data.lights.new('k', 'SUN'); ld.energy = 3.0; lo = bpy.data.objects.new('k', ld); sc.collection.objects.link(lo); lo.rotation_euler = (0.7, 0.2, 2.2)
cd = bpy.data.cameras.new('c'); cd.lens = 28; cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
def shot(nm, eye, tgt):
    cam.location = Vector(eye); d = Vector(tgt) - Vector(eye); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = '/tmp/claude-0/-home-user-zerotwelve/1b150d8a-25e8-5370-b86d-453a7d8bda62/scratchpad/closeups/' + nm + '.jpg'; bpy.ops.render.render(write_still=True)
def near(n, off, dz=0.6):
    o = bpy.data.objects[n]; c = o.matrix_world.translation; return (c.x + off[0], c.y + off[1], c.z + off[2]), (c.x, c.y, c.z + dz)
import json
for nm, obj, off, dz in json.loads(sys.argv[-1]):
    e, t = near(obj, off, dz); shot(nm, e, t)
