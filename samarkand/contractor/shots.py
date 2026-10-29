"""Product shots for the BOQ: each item alone on a light studio background, 3/4 view.
Usage: bvenv/bin/python boq/shots.py BLEND OUTDIR [names...]"""
import bpy, sys, math, os, re
from mathutils import Vector
BLEND, OUT = sys.argv[1], sys.argv[2]; ONLY = sys.argv[3:]
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene
SHOTS = [  # key, regex of objects to show, view azimuth (deg), elevation (deg), extra zoom
 ('chair', r'^Chair_001$', 55, 16, 1.0), ('table4', r'^(Table_003|Tableset_003)$', 210, 30, 1.0), ('table2', r'^(Table_001|Tableset_001)$', 210, 30, 1.0),
 ('booth', r'^Booth3_', 300, 16, 1.0), ('tapchan', r'^Tapchan_', 230, 26, 1.0), ('tent', r'^(Tent_1|Tent1_|Tent_octatable$|Tent_octatable\.001$|carpet$)', 250, 16, 1.0),
 ('octatable', r'^Tent_octatable$', 210, 30, 1.0), ('majlis', r'^Tent1_majlis_W$', 300, 20, 1.0),
 ('rotunda', r'^(Bukhara_|rotunda$)', 210, 14, 1.0), ('lantern', r'^Aivan_lantern_1$', 210, 10, 1.0), ('pendant', r'^Pendant_cluster$', 210, 10, 1.0),
 ('chandelier', r'^Chandelier_dome_C$', 210, 8, 1.0), ('drum_pendant', r'^Bar_drum_pendant_1$', 210, 10, 1.0), ('sconce', r'^Sconce_firewall_1$', 240, 10, 1.0),
 ('khiva_column', r'^Khiva_column_01$', 210, 10, 1.0), ('sam_column', r'^Sam_column_01$', 210, 10, 1.0), ('khiva_gate', r'^Khiva_gate$', 200, 10, 1.0),
 ('arcade', r'^(Khiva_arcade_bay_0[2-4]|Khiva_column_0[2-4]|Khiva_arcade_head_0[2-3])$', 120, 12, 1.0),
 ('pishtaq', r'^Street_pishtaq$', 250, 8, 1.0), ('sebil', r'^Street_sebil$', 250, 8, 1.0),
 ('door_main', r'^Hall_door_cd_s$', 20, 6, 1.0), ('door_glass', r'^Hall_door_cd_n$', 20, 6, 1.0), ('lift', r'^Lift_portal$', 20, 6, 1.0),
 ('aivan_screen_ad', r'^Aivan_screen_1$', 200, 10, 1.0), ('aivan_screen', r'^Aivan_screen_2$', 200, 10, 1.0),
 ('aivan_booth', r'^(Aivan_banquette_[12]|Aivan_table_1|Aivan_tableset_1|Aivan_screen_2|Aivan_wallcarpet_1|Aivan_lantern_1)$', 60, 22, 1.0),
 ('jali_cabinet', r'^Host_cabinet$', 230, 12, 1.0), ('station', r'^(Station_cabinet_[123]|Station_screen)$', 20, 12, 1.0),
 ('chinar', r'^(Chinar_|Tree_uplight)', 220, 12, 1.0), ('flycarpet', r'^Flying_carpet_01$', 200, 25, 1.0), ('ceiling_carpet', r'^Ceiling_carpet_01$', 200, 40, 1.0),
 ('corridor', r'^(Corridor_|corridor_curtain)', 270, 22, 1.0), ('bar', r'^(Bar_counter|Bar_backwall|Bar_cornice|Barstool|Bar_drum)', 60, 14, 1.0), ('barstool', r'^Barstool$', 210, 14, 1.0),
 ('hauz', r'^(hauz|Hauz_|medallion_mosaic)', 210, 30, 1.0), ('kids', r'^(Kids_|kids_rubber|play_)', 230, 30, 1.0), ('zardevor', r'^Zardevor_1$', 15, 6, 1.0),
 ('mangal_sign', r'^(Mangal_signboard|Logo_Samarkand_W|Logo_subtitle_W)$', 195, 4, 1.0), ('street_sign', r'^(Logo_Samarkand_E|Logo_subtitle_E)$', 15, 4, 1.0),
 ('mangal', r'^(Mangal_hood|mangal$|Tandoor_copper|Kazan|tandoorblock|kazanblock|pass$|Firewood_wall|Heat_lamp)', 300, 22, 1.0),
 ('skylight', r'^(Skylight_panjara)$', 210, 50, 1.0), ('dome', r'^(dome_.*_C)$', 220, 20, 1.0), ('urn', r'^(pot$|Pomegranate\.002$)', 210, 12, 1.0),
 ('street_bench', r'^(sbench$|sback$)', 230, 18, 1.0), ('photo_lounge', r'^(Photo_portal_drape|phrug|pouf|ltable|firebowl|fire$|jar$|flantern|candle)', 20, 22, 1.0),
 ('amphora', r'^Corridor_amphora_1$', 210, 10, 1.0), ('aivan_rail', r'^aivan_rail_jali$', 20, 25, 1.0),
]
for o in bpy.data.objects:
    if o.type == 'LIGHT': o.hide_render = True
world = sc.world; nt = world.node_tree
for n in list(nt.nodes):
    if n.type not in ('BACKGROUND', 'OUTPUT_WORLD'): nt.nodes.remove(n)
bg = nt.nodes['Background']; bg.inputs['Color'].default_value = (0.93, 0.92, 0.9, 1); bg.inputs['Strength'].default_value = 1.7
sc.view_settings.exposure = 0.0
ld = bpy.data.lights.new('key', 'SUN'); ld.energy = 3.0; ld.angle = math.radians(8); key = bpy.data.objects.new('key', ld); sc.collection.objects.link(key)
key.rotation_euler = (math.radians(50), 0, math.radians(35))
cam_d = bpy.data.cameras.new('shotcam'); cam = bpy.data.objects.new('shotcam', cam_d); sc.collection.objects.link(cam); sc.camera = cam; cam_d.lens = 50
sc.render.resolution_x, sc.render.resolution_y = 640, 480; sc.render.resolution_percentage = 100
sc.cycles.samples = 48; sc.cycles.use_denoising = True
try: sc.render.film_transparent = False
except Exception: pass
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for key_, pat, az, el, zm in SHOTS:
    if ONLY and key_ not in ONLY: continue
    rx = re.compile(pat); sel = [o for o in meshes if rx.search(o.name)]
    if not sel: print('MISS', key_); continue
    for o in meshes: o.hide_render = o not in sel
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in sel for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    c = (lo + hi) / 2; r = max((hi - lo).length / 2, 0.05)
    d = r / math.sin(cam_d.angle / 2 * 0.92) * 1.02 / zm
    a, e = math.radians(az), math.radians(el)
    cam.location = c + Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e))) * d
    cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam_d.clip_start = max(0.01, d - 3 * r); cam_d.clip_end = d + 3 * r
    sc.render.filepath = os.path.join(OUT, key_ + '.png'); bpy.ops.render.render(write_still=True); print('SHOT', key_, len(sel))
