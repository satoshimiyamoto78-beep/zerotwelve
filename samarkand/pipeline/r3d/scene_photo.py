import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from bl import *
sc = reset(); m = M()
OUT, W, H, S = sys.argv[-4], int(sys.argv[-3]), int(sys.argv[-2]), int(sys.argv[-1])
box(-6, -3, -0.05, 6, 8, 0, m['floor'])
slat_ceiling(m, -6, 6, -3, 8, 3.9, axis='Y')
# greenery behind
for x in range(-5, 6): bush(m, x * 1.0, -1.6, 0.0, 0.9, n=10, seed=x + 40)
# pishtaq portal 4.2 x 3.9 x 0.45, arch opening 1.9 / spring 2.35 / apex 3.15
pw, ph, d = 4.2, 3.9, 0.45
fr = box(-pw / 2, -0.45, 0, pw / 2, 0, ph, m['plaster_l'], name='portal')
cut(fr, prism_xz(arch_pts(0, 1.9, -0.1, 2.35, 3.15), -0.3, 0.2, None, 'c'))
box(-pw / 2 + 0.02, 0.0, 0.0, pw / 2 - 0.02, 0.03, ph - 0.02, m['majolica'])                 # tiled face (cut below)
face = [o for o in bpy.data.objects if o.name.startswith('box')][-1]
cut(face, prism_xz(arch_pts(0, 2.3, -0.1, 2.35, 3.45), -0.2, 0.2, None, 'c2'))
pointed_frame(m['lapis'], 0, 0.0, 0.06, 1.9, 2.35, 3.15, t=0.2, z0=0.0)
pointed_frame(m['brass'], 0, 0.06, 0.075, 2.3, 2.35, 3.45, t=0.03, z0=0.0)
box(-pw / 2, 0.0, ph - 0.42, pw / 2, 0.08, ph, m['band'])                                    # inscription band
box(-pw / 2, 0.0, ph - 0.46, pw / 2, 0.09, ph - 0.42, m['brass'])
for xs in (-pw / 2, pw / 2 - 0.22):                                                          # corner guldasta shafts
    box(xs, -0.02, 0, xs + 0.22, 0.1, ph - 0.46, m['turq'], bevel=0.01)
# recess: turquoise mosaic back, stepped muqarnas rings, backlight
gm = bpy.data.materials.new('girih_glow'); gm.use_nodes = True; N = gm.node_tree.nodes; Lk = gm.node_tree.links
bs = N['Principled BSDF']; it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(TEX, 'girih.png')); it.projection = 'BOX'
tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (2.2, 2.2, 2.2)
Lk.new(tc.outputs['Object'], mp.inputs['Vector']); Lk.new(mp.outputs['Vector'], it.inputs['Vector'])
Lk.new(it.outputs['Color'], bs.inputs['Base Color']); Lk.new(it.outputs['Color'], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = 1.6
for yb in (-0.30, -0.22, -0.12, -0.02):
    o = prism_xz(arch_pts(0, 1.88, 0.0, 2.35, 3.14), yb - 0.01, yb, gm if yb == -0.30 else None, 'back')
    if yb != -0.30: bpy.data.objects.remove(o, do_unlink=True)
for k, (w_, zs_, za_) in enumerate(((1.7, 2.45, 3.05), (1.45, 2.55, 2.95), (1.15, 2.62, 2.86))):
    pointed_frame((m['turq'], m['lapis'], m['brass'])[k], 0, -0.3 + 0.07 * k, -0.24 + 0.07 * k, w_, zs_, za_, t=0.09, z0=zs_ - 0.05)
area(0, 0.6, 1.7, 1.6, 70, rot=(math.radians(-90), 0, 0))
point(0, -0.12, 2.6, 25, radius=0.2)
box(-0.9, -0.29, 0.05, 0.9, -0.27, 0.08, m['glow'])
# floor medallion + photo spot
o = cyl(0, 1.6, 0.003, 1.0, 0.006, m['girih'], verts=64)
torus(0, 1.6, 0.006, 1.0, 0.025, m['brass'])
cyl(0, 4.2, 0.004, 0.18, 0.008, m['brass'], verts=32)
# sandyk chest bench with cushions in the arch
box(-0.75, -0.25, 0, 0.75, 0.3, 0.42, m['red'], bevel=0.01)
box(-0.7, 0.29, 0.06, 0.7, 0.31, 0.36, m['suzani'])
box(-0.7, -0.22, 0.42, 0.7, 0.27, 0.5, m['ikat'], bevel=0.03)
cyl(-0.5, 0.0, 0.62, 0.11, 0.42, m['suzani'], axis='X'); cyl(0.5, 0.0, 0.62, 0.11, 0.42, m['suzani'], axis='X')
# flanking: brass floor lanterns + potted trees + jugs
for sx in (-1, 1):
    lantern(m, sx * 1.55, 0.8, 0.45, s=1.6, energy=35)
    potted_tree(m, sx * 2.8, 0.7, s=1.15, seed=10 + sx)
    lathe(sx * 1.25, 0.55, 0, [(0, 0), (0.1, 0), (0.17, 0.15), (0.16, 0.32), (0.07, 0.45), (0.05, 0.55), (0.08, 0.58), (0, 0.58)], m['clay'])
lantern(m, 0, 1.6, 3.2, s=1.2, rod_top=3.9, energy=40)
area(0, 6, 2.6, 4, 90, rot=(math.radians(70), 0, math.radians(180)))
camera((0.4, 6.3, 1.55), (0, 0, 1.75), lens=28)
render(OUT, W, H, S)
