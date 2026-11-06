import sys, os, math, json, random
sys.path.insert(0, os.path.dirname(__file__))
from bl2 import *
import bmesh
sc = reset(sun_elev=14, sky_strength=0.6, exposure=-0.5); m = M2()
OUT, W, H, S = sys.argv[-4], int(sys.argv[-3]), int(sys.argv[-2]), int(sys.argv[-1])
D = json.load(open(os.path.join(os.path.dirname(__file__), 'aerial_data.json')))
def extrude(ring, z0, z1, mm, name='ex'):
    pts = ring[:-1] if ring[0] == ring[-1] else ring
    if len(pts) < 3: return None
    bm = bmesh.new(); a = [bm.verts.new((x, y, z0)) for x, y in pts]; b = [bm.verts.new((x, y, z1)) for x, y in pts]
    try:
        bm.faces.new(a); bm.faces.new(list(reversed(b)))
    except ValueError: pass
    n = len(pts)
    for i in range(n):
        try: bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
        except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); me.materials.append(mm); return o
def ex_all(rings, z0, z1, mm):
    for r in rings: extrude(r, z0, z1, mm)
sun(elev=16, rot=245, strength=3.2)
bpy.data.objects['Plane'].location.z = -1.3
# ground, street, driveway, lot
box(-40, -25, -0.25, 50, 70, -0.15, mat('ground', (0.32, 0.30, 0.27), rough=0.9))
xb0 = D['bound'][0][0]
box(xb0 + 0.2, -25, -0.9, xb0 + 3.5, 70, -0.7, mat('sidewalk', (0.62, 0.6, 0.56), rough=0.8))
box(xb0 + 3.5, -25, -1.2, xb0 + 19, 70, -1.0, mat('asphalt', (0.07, 0.07, 0.075), rough=0.7))
for y in range(-25, 70, 6): box(xb0 + 11.2, y, -0.999, xb0 + 11.4, y + 3, -0.995, mat('paint', (0.9, 0.9, 0.85), rough=0.6))
box(-2, 36.9, -0.15, xb0 - 0.2, 42.5, -0.05, mat('drive', (0.45, 0.44, 0.42), rough=0.85))
# building: three floors, plaster with glass bands, balcony
box(-34, 4.1, -0.15, 0, 37.1, 11.5, m['plaster_l'], bevel=0.02)
for zf in (0.3, 4.4, 8.0):
    box(0.0, 4.4, zf, 0.05, 36.8, zf + 3.0, m['glass'])
box(0, 9.85, 4.2, 1.5, 32.1, 4.45, m['plaster_l'])
box(-34, 4.1, 11.5, 0.6, 37.1, 11.9, m['walnut'])
# terrace floors (local origin = axis 6 x axis A'; terrace floor shown at 0)
ex_all(D['floor'], -0.15, 0.0, m['floor'])
ex_all(D['alley'], 0.0, 0.01, m['girih'])
ex_all(D['kids'], 0.0, 0.03, mat('rubber', (0.95, 0.72, 0.3), rough=0.9))
ex_all(D['plat'], 0.0, 0.47, m['deck'])
ex_all(D['planter'], 0.0, 0.5, m['brick'])
rr = random.Random(4)
for r in D['planter']:
    pts = r[:-1]; xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for k in range(400):
        x = rr.uniform(min(xs), max(xs)); y = rr.uniform(min(ys), max(ys))
        from mathutils import Vector
        inside = False; n = len(pts); j = n - 1
        for i in range(n):
            if (pts[i][1] > y) != (pts[j][1] > y) and x < (pts[j][0] - pts[i][0]) * (y - pts[i][1]) / (pts[j][1] - pts[i][1]) + pts[i][0]: inside = not inside
            j = i
        if inside and k % 3 == 0: leafy(m, x, y, 0.35, 0.45, n=160, seed=k)
HT = {'rug': (0.0, 0.012, 'linen'), 'screen': (0, 2.1, 'jali'), 'bench': (0, 0.45, 'ikat'), 'btable': (0, 0.75, 'walnut'), 'table': (0, 0.75, 'walnut'),
     'chair': (0, 0.47, 'ikat'), 'stool': (0, 0.75, 'walnut'), 'tapchan': (0, 0.45, 'walnut'), 'tapchanrug': (0.45, 0.56, 'suzani'), 'tapchantable': (0.56, 0.85, 'walnut'),
     'pit': (0, 0.08, 'clay'), 'ringbench': (0, 0.45, 'walnut'), 'aryk': (0, 0.03, 'water'), 'hauzborder': (0, 0.4, 'majolica'), 'hauz': (0, 0.39, 'water'),
     'backbar': (0, 0.95, 'walnut'), 'barbody': (0, 1.05, 'lapis'), 'bartop': (1.03, 1.09, 'terrazzo'), 'barreturn': (0, 1.09, 'terrazzo'),
     'shelving': (0, 2.2, 'walnut'), 'counter': (0, 0.95, 'steel'), 'screenwall': (0, 1.6, 'jali'), 'bbqfloor': (0, 0.01, 'black'), 'firewall': (0, 1.8, 'brick'),
     'tandoorblock': (0, 0.85, 'majolica'), 'tandoor': (0.85, 1.25, 'clay'), 'mangal': (0, 0.86, 'black'), 'kazanblock': (0, 0.7, 'brick'), 'kazan': (0.7, 1.0, 'black'),
     'sinkbins': (0, 0.9, 'steel'), 'prep': (0, 0.95, 'steel'), 'pass': (0, 0.95, 'steel'), 'glass': (0.95, 1.35, 'glass'), 'hood': (2.35, 2.75, 'black'), 'storage': (0, 2.1, 'walnut'),
     'pishtaq': (0, 3.9, 'majolica'), 'pishtaq_niche': (0, 3.1, 'turq'), 'medallion': (0, 0.012, 'girih'), 'station': (0, 1.0, 'turq'), 'host': (0, 1.05, 'turq'),
     'stepsA': (0, 0.3, 'oak'), 'stepsB': (0, 0.3, 'oak'), 'barsteps': (0, 0.3, 'oak'), 'ramp': (0, 0.25, 'deck'), 'sliver': (0, 0.5, 'brick'), 'samovar': (0.95, 1.5, 'brass'),
     'coffee': (0.95, 1.35, 'steel'), 'sink': (0.95, 0.96, 'steel'), 'lantern': (0, 0, None), 'camera': (0, 0, None), 'platform': (0, 0, None)}
on_deck = lambda r: any(0 <= x <= 3.3 and 15.3 <= y <= 30.9 for x, y in r)
for it in D['items']:
    k = it['kind']
    if k not in HT or HT[k][2] is None: continue
    z0, z1, mn = HT[k]
    for r in it['poly']:
        dz = 0.47 if (on_deck(r) and k in ('table', 'chair', 'station')) else 0.0
        extrude(r, z0 + dz, z1 + dz, m[mn] if mn in m else mat(mn, (0.5, 0.5, 0.5)))
# play elements in the kids zone
for (x, y, r, c) in ((-5.4, 3.0, 0.55, (0.6, 0.85, 0.5)), (-2.2, 1.1, 0.45, (0.95, 0.83, 0.35))):
    cyl(x, y, 0.3, r, 0.6, mat('play%d' % int(r * 100), c, rough=0.6))
box(-6.8, 0.4, 0.0, -4.2, 1.7, 0.7, mat('playA', (0.95, 0.6, 0.36), rough=0.6), bevel=0.08)
# trees: trunk + leafy canopy through the roof oculi
for (x, y) in D['trees']:
    cyl(x, y, 2.6, 0.3, 5.2, mat('bark', (0.30, 0.24, 0.18), rough=0.9, bump=0.3), verts=24)
    for k in range(7): leafy(m, x + 1.7 * math.cos(k * 0.9), y + 1.7 * math.sin(k * 0.9), 4.0 + (k % 2) * 0.5, 1.4, seed=500 + k)
    leafy(m, x, y, 4.6, 1.6, seed=520)
# roof structure shown as a cutaway: columns + trusses, no deck
for (x, y) in D['cols']:
    if y > 0.6: box(x - 0.15, y - 0.15, 0.0, x + 0.15, y + 0.15, 3.6, m['walnut'])
for (y, xe) in D['truss']:
    box(0.0, y - 0.1, 3.45, xe, y + 0.1, 3.75, m['walnut'])
box(D['bound'][0][0] - 0.75 - 0.1, -0.5, 3.45, D['bound'][0][0] - 0.75 + 0.1, 37.0, 3.75, m['walnut']) if False else None
camera((25, -5, 19), (4.0, 17.5, 0), lens=24, fstop=0)
render(OUT, W, H, S)
