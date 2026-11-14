import bpy, math, sys
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 8; sc.cycles.use_denoising = True
X0, X1, Y0, Y1 = [float(v) for v in sys.argv[sys.argv.index('--') + 1:][:4]]; out = sys.argv[-1]
sc.render.resolution_x = 900; sc.render.resolution_y = int(900 * (Y1 - Y0) / (X1 - X0)); sc.render.image_settings.file_format = 'JPEG'
for o in bpy.data.objects:
    w = o.matrix_world.translation
    if o.type in ('MESH',) and (o.bound_box and max((o.matrix_world @ __import__('mathutils').Vector(v)).z for v in o.bound_box) > 1.3): o.hide_render = True
if not sc.world: sc.world = bpy.data.worlds.new('w')
sc.world.use_nodes = True; bg = sc.world.node_tree.nodes['Background']; bg.inputs[1].default_value = 2.0
ld = bpy.data.lights.new('k', 'SUN'); ld.energy = 3.0; lo = bpy.data.objects.new('k', ld); sc.collection.objects.link(lo)
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'; cd.ortho_scale = max(X1 - X0, Y1 - Y0)
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = ((X0 + X1) / 2, (Y0 + Y1) / 2, 20); cam.rotation_euler = (0, 0, 0)
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
