import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from bl import *
sc = reset(); m = M()
OUT, W, H, S = sys.argv[-4], int(sys.argv[-3]), int(sys.argv[-2]), int(sys.argv[-1])
box(-6, -4, -0.05, 6, 10, 0, m['floor'])
slat_ceiling(m, -6, 6, -4, 10, 3.6)
wl = box(-6, -4, 0, -3.2, 10, 3.6, m['plaster'])
for yc in (-1.2, 1.4, 5.6):
    o = prism_xz(arch_pts(yc, 1.3, 0.9, 2.3, 2.9), -0.2, 0.2, None, 'c'); o.rotation_euler[2] = math.pi / 2; o.location = (-3.2, 0, 0)
    bpy.context.view_layer.update(); cut(wl, o)
    b_ = prism_xz(arch_pts(yc, 1.3, 0.9, 2.3, 2.9), -0.01, 0.0, m['majolica'], 'b'); b_.rotation_euler[2] = math.pi / 2; b_.location = (-3.38, 0, 0)
    area(-3.0, yc, 2.6, 0.6, 15, rot=(0, math.radians(-70), 0))
# aryk (water channel) along y at x=0.3, hauz at y=3
box(0.15, -3, -0.02, 0.45, 9, 0.02, m['turq']); box(0.18, -3, 0.0, 0.42, 9, 0.015, m['water'])
for sx in (0.12, 0.45): box(sx, -3, 0, sx + 0.03, 9, 0.05, m['majolica'])
oct_ = [(0.3 + 0.75 * math.cos(math.radians(22.5 + 45 * i)), 3 + 0.75 * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
import bmesh
def octo(r, z0, z1, mm):
    pts = [(0.3 + r * math.cos(math.radians(22.5 + 45 * i)), 3 + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    bm = bmesh.new(); a = [bm.verts.new((x, y, z0)) for x, y in pts]; b = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    for i in range(8): bm.faces.new((a[i], a[(i + 1) % 8], b[(i + 1) % 8], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new('o'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('o', me); bpy.context.collection.objects.link(o); me.materials.append(mm); return o
octo(0.95, 0, 0.32, m['majolica']); octo(0.78, 0.0, 0.3, m['water'])
cyl(0.3, 3, 0.45, 0.07, 0.3, m['brass'], verts=24); cyl(0.3, 3, 0.75, 0.012, 0.45, m['water'], verts=12)
point(0.3, 3, 0.2, 8, color=(0.6, 0.9, 1.0))
# three tapchans west of the aryk
for k, y0 in enumerate((-2.2, 0.4, 3.0 + 1.6)):
    x0, x1 = -2.9, -0.9
    box(x0, y0, 0, x1, y0 + 2.0, 0.45, m['walnut'], bevel=0.01)
    for xx in (x0 + 0.05, x1 - 0.05):
        for yy in (y0 + 0.05, y0 + 1.95): cyl(xx, yy, 0.225, 0.05, 0.45, m['walnut'], verts=16)
    box(x0 + 0.05, y0 + 0.05, 0.45, x1 - 0.05, y0 + 1.95, 0.55, m['suzani'], bevel=0.03)        # kurpacha mattress
    # carved panjara rails on three sides (open to the aryk)
    for (a0, b0, a1, b1) in ((x0, y0, x0 + 0.06, y0 + 2.0), (x0, y0, x1, y0 + 0.06), (x0, y0 + 1.94, x1, y0 + 2.0)):
        box(a0, b0, 0.55, a1, b1, 0.95, m['jali'])
        box(a0 - 0.01, b0 - 0.01, 0.95, a1 + 0.01, b1 + 0.01, 0.99, m['walnut'])
    for yy in (y0 + 0.35, y0 + 1.0, y0 + 1.65):
        cyl(x0 + 0.25, yy, 0.68, 0.13, 0.55, m['ikat'], axis='Y')
    box(-2.3, y0 + 0.55, 0.55, -1.5, y0 + 1.45, 0.82, m['walnut'], bevel=0.01)                   # low table
    lathe(-1.9, y0 + 1.0, 0.82, [(0, 0), (0.06, 0), (0.09, 0.05), (0.08, 0.1), (0.04, 0.12), (0, 0.13)], m['turq'], steps=24)
    for dy in (-0.25, 0.25): lathe(-2.1, y0 + 1.0 + dy, 0.82, [(0, 0), (0.025, 0), (0.04, 0.05), (0, 0.05)], m['lapis'], steps=20)
    lathe(-1.7, y0 + 0.8, 0.82, [(0, 0), (0.15, 0), (0.17, 0.03), (0, 0.03)], m['clay'], steps=32)
    lantern(m, -1.9, y0 + 1.0, 2.0, s=1.0, rod_top=3.6, energy=40)
# greenery and the chinar trunk
cyl(2.6, -1.2, 2.0, 0.3, 4.0, mat('bark', (0.30, 0.24, 0.18), rough=0.9, bump=0.3), verts=24)
for y in range(-3, 9): bush(m, 2.2 + (y % 2) * 0.3, y, 0.0, 0.6, n=6, seed=y + 200)
area(0, 2, 3.4, 6, 150, rot=(0, 0, 0))
camera((2.4, -3.4, 1.7), (-1.6, 2.2, 0.75), lens=22)
render(OUT, W, H, S)
