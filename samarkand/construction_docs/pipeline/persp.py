import bpy, sys, os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
for o in list(bpy.data.objects):
    if o.users_collection and o.users_collection[0].name == 'People': bpy.data.objects.remove(o)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = int(os.environ.get('SPP', 40)); sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1600, 1000, int(os.environ.get('PCT', 100))
sc.cycles.max_bounces = 4; sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 88
try: sc.view_settings.view_transform = 'AgX'
except Exception: sc.view_settings.view_transform = 'Filmic'
sc.view_settings.exposure = float(os.environ.get('EXPO', 0)); sc.render.image_settings.quality = 92
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
 'r_bk':     ((7.6, 29.6, 1.35), (6.0, 35.2, 2.0), 22),
 'r_bk2':    ((6.3, 30.0, 1.45), (5.9, 35.2, 2.1), 24),
 'r_bar2':   ((3.6, 12.9, 1.5), (0.6, 10.6, 1.15), 22),
 'r_bar4':   ((1.35, 12.4, 1.5), (0.3, 10.9, 1.2), 20),
 'r_bar3':   ((1.2, 7.2, 1.6), (1.0, 13.0, 1.0), 26),
 'r_tabs':   ((4.6, 29.2, 1.75), (5.8, 33.4, 0.9), 20),
 'r_tabs2':  ((6.3, 37.6, 1.7), (5.6, 33.0, 0.9), 22),
 'r_logo':   ((14.6, 24.2, 1.55), (10.6, 26.95, 1.45), 30),
 'q_aivwall': ((6.5, 22.0, 1.5), (0.2, 22.0, 1.6), 16),
 'q_aivS':    ((5.2, 17.6, 1.5), (0.2, 15.8, 1.5), 18),
 'q_fac1':    ((16.0, 26.0, 1.6), (10.5, 23.5, 1.4), 20),
 'q_fac2':    ((15.5, 12.0, 1.6), (11.5, 16.8, 1.8), 20),
 'q_majlis':  ((5.2, 6.4, 1.5), (1.0, 3.6, 1.2), 18),
 'q_mangal':  ((6.0, 8.6, 1.6), (11.0, 5.6, 2.2), 18),
 'q_station': ((3.9, 9.2, 1.6), (1.2, 6.4, 0.8), 22),
 'q_kids':    ((2.5, 2.0, 1.5), (-3.5, 2.8, 1.2), 16),
 'q_hallN':   ((6.0, 21.8, 1.6), (5.6, 30.0, 1.6), 16),
 'q_hallS':   ((7.6, 15.0, 1.6), (5.0, 8.0, 1.6), 16),
 'q_top1':    ((13.8, 29.5, 2.6), (10.3, 29.3, -0.6), 22),
 'q_fac3':    ((14.5, 33.5, 1.3), (10.2, 30.5, 0.4), 24),
 'q_cap1':    ((12.9, 27.2, 1.9), (10.6, 25.6, 2.75), 30),
 'q_cap2':    ((8.3, 27.0, 1.6), (10.5, 25.6, 2.8), 30),
 'q_booth1':  ((5.6, 23.2, 1.5), (9.0, 25.0, 1.2), 22),
 'q_photo':   ((6.86, 7.9, 1.5), (6.86, 2.0, 1.25), 20),
 'q_port1':   ((16.2, 18.6, 1.3), (11.6, 16.8, 1.0), 22),
 'q_port2':   ((7.2, 16.8, 1.2), (11.5, 16.8, 1.3), 22),
 'i_port':   ((16.0, 19.2, 1.4), (11.6, 16.8, 1.1), 24),
 'i_fac':    ((17.0, 30.0, 1.6), (9.8, 20.0, 1.6), 20),
 'i_bar':    ((3.7, 12.9, 1.5), (0.6, 10.6, 1.15), 22),
 'i_aiv':    ((6.3, 21.4, 1.5), (0.2, 21.4, 1.5), 18),
 'i_booth':  ((5.6, 23.2, 1.5), (9.0, 25.0, 1.2), 22),
 'i_dome':   ((6.0, 14.2, 1.0), (6.0, 19.9, 4.4), 18),
 'i_corr':   ((7.0, 16.8, 1.3), (11.5, 16.8, 1.3), 22),
 'i_hall':   ((6.2, 22.0, 1.6), (5.6, 30.0, 1.5), 16),
 'i_north':  ((4.6, 29.2, 1.75), (5.8, 33.4, 0.9), 20),
 'i_photo':  ((6.86, 7.6, 1.5), (6.86, 2.0, 1.25), 22),
 'i_mangal': ((6.3, 9.6, 1.6), (11.0, 5.6, 1.7), 20),
 'i_tent':   ((6.4, 33.0, 1.4), (2.7, 32.4, 1.1), 22),
 'r_hall2':  ((4.2, 7.6, 1.55), (6.6, 19.9, 2.3), 20),
}
for n in sys.argv[sys.argv.index('--') + 1:]:
    loc, tgt, lens = SH[n]; cd.lens = lens; cam.location = Vector(loc)
    cam.rotation_euler = (Vector(tgt) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.abspath(f'cd/renders/{n}.jpg'); bpy.ops.render.render(write_still=True); print('ok', n, flush=True)
