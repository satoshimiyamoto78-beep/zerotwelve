import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from bl2 import *
import bmesh
sc = reset(); m = M2()
OUT, W, H, S = sys.argv[-4], int(sys.argv[-3]), int(sys.argv[-2]), int(sys.argv[-1])
# R5: ramp + water channel on the west, four tapchans open to the east (path), fountain at the north entrance
box(-7, -3, -0.05, 6, 11, 0, m['floor'])
slat_ceiling(m, -7, 6, -3, 11, 3.6)
for yb in (0.5, 4.2, 7.9): box(-7, yb - 0.1, 3.4, 6, yb + 0.1, 3.6, m['walnut'])
# building facade (glass + walnut) behind the ramp, with the ramp and its rail
box(-5.9, -3, 0, -5.85, 11, 3.4, m['glass'])
box(-9.5, -3, 0, -8.0, 11, 3.6, m['plaster'])
for y in (0.0, 4.0, 8.0): lantern(m, -7.0, y, 2.5, s=1.2, rod_top=3.6, energy=18)
for y in range(-3, 12, 2): box(-5.92, y - 0.05, 0, -5.82, y + 0.05, 3.4, m['walnut'])
ramp = box(-5.8, -3, 0, -4.5, 9.5, 0.05, m['deck'])
for y in [-3 + k * 0.6 for k in range(22)]: box(-4.52, y - 0.025, 0.05, -4.47, y + 0.025, 0.95, m['brass'])
box(-4.55, -3, 0.95, -4.42, 9.5, 0.99, m['walnut'])
# aryk: tiled channel with water, small octagonal fountain at the north end
box(-4.2, -2.5, -0.02, -3.85, 8.2, 0.03, m['majolica']); box(-4.15, -2.5, 0.0, -3.9, 8.2, 0.025, m['water'])
def octo(cx, cy, r, z0, z1, mm):
    pts = [(cx + r * math.cos(math.radians(22.5 + 45 * i)), cy + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    bm = bmesh.new(); a = [bm.verts.new((x, y, z0)) for x, y in pts]; b = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    for i in range(8): bm.faces.new((a[i], a[(i + 1) % 8], b[(i + 1) % 8], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new('o'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('o', me); bpy.context.collection.objects.link(o); me.materials.append(mm); return o
octo(-4.02, 8.7, 0.62, 0, 0.42, m['majolica']); octo(-4.02, 8.7, 0.5, 0.0, 0.4, m['water'])
lathe(-4.02, 8.7, 0.4, [(0, 0), (0.12, 0), (0.1, 0.2), (0.22, 0.28), (0.2, 0.32), (0.05, 0.3), (0.04, 0.5), (0, 0.5)], m['brass'])
point(-4.02, 8.7, 0.35, 10, color=(0.6, 0.9, 1.0))
# tapchans 2.0 x 1.8, rails west/north/south, open to the east
for k, y0 in enumerate((-1.9, 0.0, 1.9, 3.8)):
    x0, x1 = -3.6, -1.6
    box(x0, y0, 0, x1, y0 + 1.8, 0.45, m['walnut'], bevel=0.01)
    for xx in (x0 + 0.06, x1 - 0.06):
        for yy in (y0 + 0.06, y0 + 1.74): cyl(xx, yy, 0.225, 0.05, 0.45, m['walnut'], verts=16)
    cushion(m, x0 + 0.05, y0 + 0.05, 0.45, x1 - 0.05, y0 + 1.75, 0.55, m['suzani'])
    for (a0, b0, a1, b1) in ((x0, y0, x0 + 0.06, y0 + 1.8), (x0, y0, x1, y0 + 0.06), (x0, y0 + 1.74, x1, y0 + 1.8)):
        box(a0, b0, 0.55, a1, b1, 1.0, m['jali'])
        box(a0 - 0.012, b0 - 0.012, 1.0, a1 + 0.012, b1 + 0.012, 1.04, m['walnut'])
    for yy in (y0 + 0.35, y0 + 0.9, y0 + 1.45):
        o = cyl(x0 + 0.24, yy, 0.69, 0.13, 0.5, m['ikat'], axis='Y')
    for yy in (y0 + 0.25, y0 + 1.55): cushion(m, x0 + 0.5, yy - 0.18, 0.55, x0 + 1.1, yy + 0.18, 0.65, m['ikat'])
    box(x0 + 0.55, y0 + 0.5, 0.55, x0 + 1.45, y0 + 1.3, 0.82, m['walnut'], bevel=0.01)
    teapot(m, x0 + 1.0, y0 + 0.9, 0.82, s=1.1)
    for dx, dy in ((-0.25, -0.22), (0.25, -0.22), (-0.25, 0.22), (0.25, 0.22)): piala(m, x0 + 1.0 + dx, y0 + 0.9 + dy, 0.82)
    lathe(x0 + 0.75, y0 + 0.65, 0.82, [(0, 0), (0.16, 0), (0.18, 0.03), (0, 0.03)], m['majolica'], steps=36)
    candle(m, x0 + 1.25, y0 + 1.1, 0.82)
    lantern(m, x0 + 1.0, y0 + 0.9, 2.15, s=1.0, rod_top=3.4, energy=38)
# path on the east and the sea-view booths beyond
for y0 in (-2.0, 0.0, 2.0, 4.0, 6.0):
    o = prism_xz(arch_pts(0, 1.3, 0, 1.75, 2.2), -0.03, 0.03, m['jali'], 'scr'); o.rotation_euler[2] = math.pi / 2; o.location = (3.6, y0, 0)
    box(2.95, y0 + 0.15, 0, 4.25, y0 + 0.6, 0.45, m['ikat'])
for y in range(-3, 11): bush(m, 5.0, y, 0.3, 0.7, seed=300 + y)
# chinar trunk to the south
cyl(-0.5, -4.3, 2.0, 0.3, 4.0, mat('bark', (0.30, 0.24, 0.18), rough=0.9, bump=0.3), verts=24)
area(-1, 3, 3.4, 6, 110, rot=(0, 0, 0))
camera((2.2, -3.2, 1.65), (-2.4, 3.2, 0.8), lens=22, fstop=5.6, focus=5.5)
render(OUT, W, H, S)
