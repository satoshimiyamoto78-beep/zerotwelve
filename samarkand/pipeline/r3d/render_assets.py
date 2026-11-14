"""Asset sheet: each library asset twice — with its materials and as clay + wireframe (topology check).
Usage: bvenv/bin/python render_assets.py MODEL.blend OUT.png [W H S]"""
import sys, math, bpy
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
bpy.ops.wm.open_mainfile(filepath=argv[0]); OUT = argv[1]
W, H, S = (int(argv[2]), int(argv[3]), int(argv[4])) if len(argv) > 4 else (1800, 1100, 48)
NAMES = ['Chair_carved', 'Table_4p', 'Tableware_4p', 'Lantern_1.00', 'Vitrine', 'Tandoor_copper', 'Corridor_niche', 'Bukhara_rotunda', 'Booth_timur']
src = bpy.context.scene
sc = bpy.data.scenes.new('AssetSheet'); bpy.context.window.scene = sc if bpy.context.window else None
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = S; sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'AgX'; sc.view_settings.exposure = 0.3
w = bpy.data.worlds.new('sheetW'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.92, 0.89, 0.84, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.9
clay = bpy.data.materials.new('clay_wire'); N = clay.node_tree.nodes; L = clay.node_tree.links
b = N['Principled BSDF']; b.inputs['Base Color'].default_value = (0.78, 0.74, 0.68, 1); b.inputs['Roughness'].default_value = 0.7
wf = N.new('ShaderNodeWireframe'); wf.use_pixel_size = True; wf.inputs['Size'].default_value = 0.9
mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs['A'].default_value = (0.78, 0.74, 0.68, 1); mix.inputs['B'].default_value = (0.12, 0.2, 0.45, 1)
L.new(wf.outputs['Fac'], mix.inputs['Factor']); L.new(mix.outputs['Result'], b.inputs['Base Color'])
meshes = {me.name: me for me in bpy.data.meshes}
x = 0.0; placed = []
for nm in NAMES:
    me = meshes.get(nm)
    if me is None: print('missing', nm); continue
    vs = [v.co for v in me.vertices]; lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))); hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    size = hi - lo; sf = 1.0 if max(size) < 1.2 else 1.2 / max(size)
    for row, use_clay in ((0, False), (1, True)):
        me2 = me if not use_clay else me.copy()
        if use_clay:
            me2.materials.clear(); me2.materials.append(clay)
        o = bpy.data.objects.new(nm + ('_wire' if use_clay else ''), me2); sc.collection.objects.link(o)
        rz = {'Chair_carved': math.pi - 0.6, 'Booth_timur': math.pi / 2 - 0.5}.get(nm, -0.6)
        cx_, cy_ = (lo.x + size.x / 2) * sf, (lo.y + size.y / 2) * sf; c_, s_ = math.cos(rz), math.sin(rz)
        o.scale = (sf, sf, sf); o.rotation_euler = (0, 0, rz)
        o.location = (x - (cx_ * c_ - cy_ * s_), row * -2.6 - (cx_ * s_ + cy_ * c_), -lo.z * sf)
    placed.append((nm, x)); x += max(size.x, size.y) * sf + 0.35
bpy.ops.mesh.primitive_plane_add(size=60, location=(x / 2, -1, 0)); g = bpy.context.active_object
gm = bpy.data.materials.new('ground_sheet'); gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.9, 0.87, 0.82, 1); g.data.materials.append(gm)
if g.name not in sc.collection.objects: sc.collection.objects.link(g)
ld = bpy.data.lights.new('sun', 'SUN'); ld.energy = 3.0; ld.angle = math.radians(8); so = bpy.data.objects.new('sun', ld); so.rotation_euler = (math.radians(50), 0, math.radians(30)); sc.collection.objects.link(so)
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = x * 1.0
co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co); co.location = (x / 2 - 0.2, -14.0, 9.5)
d = Vector((x / 2 - 0.2, -1.3, 0.4)) - co.location; co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.filepath = OUT
bpy.ops.render.render(write_still=True, scene=sc.name)
print('sheet', placed)
