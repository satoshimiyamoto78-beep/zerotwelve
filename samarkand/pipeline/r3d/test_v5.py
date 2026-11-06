"""perspective test scene for v5 architecture: pishtaq (street face to camera), Samarkand column, frieze"""
import sys
src = open('r3d/test_v4.py').read().split("B = [(")[0].replace("argv = sys.argv[1:]; OUT = argv[0]", "argv = sys.argv[1:]; OUT = argv[0]")
exec(src)
from mathutils import Vector
VIEW = argv[4] if len(argv) > 4 else 'front'
me = a_pishtaq(2.5, 3.9, 1.5); o = bpy.data.objects.new('P', me); sc.collection.objects.link(o)
mc = a_sam_column(3.0)
for i, y in enumerate((-3.2, 3.2)): oc = bpy.data.objects.new('C', mc); sc.collection.objects.link(oc); oc.location = (2.2, y, 0)
mf = a_frieze(3.2); of = bpy.data.objects.new('F', mf); sc.collection.objects.link(of); of.location = (-1.5, -4.8, 2.6)
bpy.ops.mesh.primitive_plane_add(size=40); g = bpy.context.active_object; g.data.materials.append(X['brickpave'])
w = sc.world; w.node_tree.nodes['Background'].inputs[0].default_value = (0.75, 0.82, 0.95, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 1.0
ld = bpy.data.lights.new('sun', 'SUN'); ld.energy = 4.0; ld.angle = math.radians(3); so = bpy.data.objects.new('sun', ld); so.rotation_euler = (math.radians(50), 0, math.radians(70)); sc.collection.objects.link(so)
cd = bpy.data.cameras.new('cam'); cd.lens = 24; co = bpy.data.objects.new('cam', cd); sc.collection.objects.link(co)
loc, tgt = {'front': ((7.5, -2.6, 1.6), (0, 0, 2.2)), 'under': ((2.2, -0.4, 1.4), (-0.6, 0.0, 3.0)), 'col': ((4.3, -1.6, 1.5), (2.2, -3.2, 1.6))}[VIEW]
co.location = loc; co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
sc.view_settings.exposure = 0.0; sc.cycles.samples = S; sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
