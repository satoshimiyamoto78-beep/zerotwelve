import bpy, sys, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
for o in list(bpy.data.objects):
    if o.users_collection and o.users_collection[0].name == 'People': bpy.data.objects.remove(o)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = int(os.environ.get('SPP', 40)); sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1600, 1000, 100
sc.cycles.max_bounces = 4; sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 88
try: sc.view_settings.view_transform = 'AgX'
except Exception: sc.view_settings.view_transform = 'Filmic'
cd = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cd); sc.collection.objects.link(cam); sc.camera = cam
SH = {  # name: (loc, target, lens)
 'r_street': ((17.5, 30.5, 1.6), (9.5, 18.0, 1.8), 20),
 'r_hall':   ((7.6, 15.9, 1.15), (2.0, 22.5, 1.0), 22),
 'r_aivan':  ((6.2, 30.5, 1.2), (1.2, 24.0, 1.3), 22),
 'r_booth':  ((6.4, 22.4, 1.25), (9.4, 26.5, 0.9), 24),
 'r_dome':   ((6.0, 13.6, 1.0), (6.0, 19.9, 4.6), 18),
 'r_corr':   ((9.0, 13.2, 1.3), (9.0, 19.0, 1.4), 22),
 'r_bar':    ((5.6, 6.0, 1.4), (1.2, 11.2, 1.2), 22),
 'r_booths_ext': ((15.0, 20.5, 1.7), (9.5, 30.0, 1.3), 22),
 'r_hall2':  ((4.2, 7.6, 1.55), (6.6, 19.9, 2.3), 20),
}
for n in sys.argv[sys.argv.index('--') + 1:]:
    loc, tgt, lens = SH[n]; cd.lens = lens; cam.location = Vector(loc)
    cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.abspath(f'cd/renders/{n}.jpg'); bpy.ops.render.render(write_still=True); print('ok', n, flush=True)
