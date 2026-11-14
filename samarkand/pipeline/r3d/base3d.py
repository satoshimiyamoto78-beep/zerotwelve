"""Samarkand terrace — 3D BASE MODEL (LOD 200) of the whole site, built from the R9 plan data.
Levels (m): hall / aivan ±0, terrace −0.45, sidewalk −1.17. Roof skin top +3.75 at the façade, 5% fall to the street.
Usage: bvenv/bin/python base3d.py DATA.json OUTDIR [render: 1|0] [W H SAMPLES]
Writes OUTDIR/samarkand-base3d-R9.blend, .glb, .fbx, .obj and (optionally) 4 overview renders.
"""
import sys, os, math, json, random
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh
from mathutils import Vector
import bl
from bl import mat
import bl2

DATA, OUTD = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
DO_RENDER = (args[0] == '1') if args else False
W, H, S = (int(args[1]), int(args[2]), int(args[3])) if len(args) >= 4 else (1600, 1000, 64)
D = json.load(open(DATA))
REV = D['rev']

sc = bl2.reset(sky=True, sun_elev=38, sky_strength=0.35, exposure=-0.9)
for o in list(bpy.data.objects):                     # drop the helper far-ground plane, we model our own ground
    bpy.data.objects.remove(o)
m = bl2.M2()
m.update(
    concrete=mat('concrete', (0.58, 0.48, 0.38), rough=0.85, bump=0.1, noise_var=0.04),
    bronze=mat('bronze', (0.12, 0.10, 0.08), rough=0.45, metal=0.7),
    roofwood=bl2.wood('roofwood', (0.62, 0.43, 0.26), (0.40, 0.26, 0.14), rough=0.6, along='Y'),
    velvet=mat('velvet', (0.42, 0.14, 0.05), rough=0.75),
    rubber=mat('rubber', (0.95, 0.72, 0.30), rough=0.9),
    asphalt=mat('asphalt', (0.07, 0.07, 0.075), rough=0.75),
    sidewalk=mat('sidewalk', (0.42, 0.38, 0.33), rough=0.85, noise_var=0.03),
    ground=mat('ground', (0.16, 0.15, 0.13), rough=0.95),
    soil=mat('soil', (0.22, 0.15, 0.10), rough=1.0),
    slate=mat('slate', (0.18, 0.18, 0.19), rough=0.6),
    white=mat('white', (0.92, 0.90, 0.86), rough=0.35),
    fire=mat('fire', (1, .5, .1), emit=(1.0, 0.45, 0.12), strength=30.0),
    pomfruit=mat('pomfruit', (0.6, 0.05, 0.06), rough=0.4),
    bloom=mat('bloom', (0.98, 0.95, 0.85), rough=0.5),
    magenta=mat('magenta', (0.75, 0.05, 0.35), rough=0.6),
    bark=mat('bark', (0.30, 0.24, 0.18), rough=0.9, bump=0.3),
    play_g=mat('play_g', (0.55, 0.82, 0.45), rough=0.6), play_y=mat('play_y', (0.95, 0.82, 0.35), rough=0.6),
    play_o=mat('play_o', (0.95, 0.58, 0.32), rough=0.6), play_b=mat('play_b', (0.45, 0.76, 0.85), rough=0.6),
)

# ---------------- collections ----------------
COLS = {}
def coll(name):
    if name not in COLS:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); COLS[name] = c
    return COLS[name]
def link(o, cname):
    for c in o.users_collection: c.objects.unlink(o)
    coll(cname).objects.link(o); return o

# ---------------- mesh helpers (one object per call, no modifiers -> clean export) ----------------
def new_obj(name, bm, mats, cname):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for mm in mats: me.materials.append(mm)
    o = bpy.data.objects.new(name, me); coll(cname).objects.link(o); return o
def _prism(bm, pts, z0, z1, mi=0, top_mi=None):
    if len(pts) < 3: return
    if pts[0] == pts[-1]: pts = pts[:-1]
    a = [bm.verts.new((x, y, z0)) for x, y in pts]; b = [bm.verts.new((x, y, z1)) for x, y in pts]
    try:
        f = bm.faces.new(list(reversed(a))); f.material_index = mi
        f = bm.faces.new(b); f.material_index = mi if top_mi is None else top_mi
    except ValueError: pass
    n = len(pts)
    for i in range(n):
        try: f = bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i])); f.material_index = mi
        except ValueError: pass
def prism(name, rings, z0, z1, mm, cname, top=None):
    bm = bmesh.new()
    for r in rings: _prism(bm, r, z0, z1, 0, 1 if top else None)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, [mm] + ([top] if top else []), cname)
def boxes(name, bl_, mm, cname):
    """bl_: list of (x0,y0,z0,x1,y1,z1[,mi]); mm: material or list"""
    bm = bmesh.new()
    for b in bl_:
        x0, y0, z0, x1, y1, z1 = b[:6]; mi = b[6] if len(b) > 6 else 0
        _prism(bm, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mi)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, mm if isinstance(mm, list) else [mm], cname)
def cylinder(name, x, y, z0, z1, r, mm, cname, n=24, r2=None):
    bm = bmesh.new(); r2 = r if r2 is None else r2
    a = [bm.verts.new((x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n), z0)) for i in range(n)]
    b = [bm.verts.new((x + r2 * math.cos(2 * math.pi * i / n), y + r2 * math.sin(2 * math.pi * i / n), z1)) for i in range(n)]
    bm.faces.new(list(reversed(a))); bm.faces.new(b)
    for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    o = new_obj(name, bm, [mm], cname)
    for p in o.data.polygons: p.use_smooth = len(p.vertices) == 4
    return o
def blob(name, pts, mm, cname, subdiv=2):
    """cluster of icospheres (x,y,z,r) in one mesh — low-poly foliage"""
    bm = bmesh.new()
    for x, y, z, r in pts:
        ret = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=r)
        bmesh.ops.translate(bm, verts=ret['verts'], vec=(x, y, z))
    o = new_obj(name, bm, [mm], cname)
    for p in o.data.polygons: p.use_smooth = True
    return o
def sloped_box(name, x0, x1, y0, y1, ztop_fn, depth, mm, cname, top_mi_mat=None):
    """box whose top follows ztop_fn(x) (linear) — for beams / roof strips"""
    bm = bmesh.new()
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    a = [bm.verts.new((x, y, ztop_fn(x) - depth)) for x, y in pts]; b = [bm.verts.new((x, y, ztop_fn(x))) for x, y in pts]
    bm.faces.new(list(reversed(a))); f = bm.faces.new(b)
    if top_mi_mat: f.material_index = 1
    for i in range(4): bm.faces.new((a[i], a[(i + 1) % 4], b[(i + 1) % 4], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, [mm] + ([top_mi_mat] if top_mi_mat else []), cname)

TER, SID = -0.45, -1.17
def top(x): return 3.75 - 0.05 * x                     # roof skin top
def on_plat(r):
    xs = [p[0] for p in r]; ys = [p[1] for p in r]; cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    return (cx < 3.3 and 15.3 < cy < 28.5) or (cx < 2.4 and 28.5 <= cy < 30.9)
def cen(r): return sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r)
def bbox(r): xs = [p[0] for p in r]; ys = [p[1] for p in r]; return min(xs), min(ys), max(xs), max(ys)
xb0, xb1 = D['lot'][0][0], D['lot'][1][0]; yb0, yb1 = D['lot'][0][1], D['lot'][1][1]
def xb(y): return xb0 + (xb1 - xb0) * (y - yb0) / (yb1 - yb0)

# ======================= CONTEXT =======================
boxes('ground', [(-45, -25, -1.6, 60, 75, -1.45)], m['ground'], 'Context')
boxes('road', [(14.9, -25, -1.32, 32, 75, -1.30)], m['asphalt'], 'Context')
boxes('road_marks', [(23.3, y, -1.30, 23.45, y + 3, -1.295) for y in range(-24, 74, 6)], m['white'], 'Context')
sw = [[(xb(-25), -25), (14.9, -25), (14.9, 75), (xb(75), 75)]]
prism('sidewalk', sw, -1.45, SID, m['sidewalk'], 'Context')
prism('driveway', D['drive'], -1.45, TER - 0.02, m['concrete'], 'Context')
# ======================= BUILDING =======================
bx = [(-30.4, 4.1, -1.45, 0.0, 37.1, 11.7)]
boxes('building_hall', bx, m['plaster_l'], 'Building')
boxes('parapet', [(-30.4, 4.1, 11.7, 0.25, 37.1, 12.0)], m['bronze'], 'Building')
# F1 glazing with door frames, F2 / F3 glass bands
gl = []
for zf, zt in ((0.0, 3.25), (4.55, 7.3), (8.15, 10.9)):
    gl.append((0.0, 4.2, zf, 0.06, 37.0, zt))
boxes('facade_glass', gl, m['darkglass'], 'Building')
mull = []
for y in [4.1 + k * 1.15 for k in range(29)]:
    mull.append((0.06, y, 0.0, 0.12, y + 0.06, 3.25))
for a, b, op in D['doors']:
    mull += [(0.06, a, 0, 0.14, a + 0.1, 2.7), (0.06, b - 0.1, 0, 0.14, b, 2.7), (0.06, a, 2.6, 0.14, b, 2.7)]
boxes('facade_mullions', mull, m['bronze'], 'Building')
boxes('slab_F2_balcony', [(0.0, 4.1, 3.85, 1.5, 32.1, 4.2), (-0.3, 4.1, 7.45, 0.3, 37.1, 7.8)], m['plaster_l'], 'Building')
boxes('balcony_rail', [(1.45, 4.1, 4.2, 1.5, 32.1, 5.2), (1.4, 4.1, 5.15, 1.5, 32.1, 5.22)], m['bronze'], 'Building')
# ======================= TERRACE FLOORS =======================
prism('terrace_floor', D['floor'], -1.45, TER, m['floor'], 'Floors')
prism('alley_girih', D['alley'], TER, TER + 0.012, m['girih'], 'Floors')
prism('kids_rubber', D['kids'], -1.45, TER + 0.03, m['rubber'], 'Floors')
prism('aivan_deck', D['plat'], TER, 0.0, m['deck'], 'Floors')
# planter band: retaining wall to the sidewalk, soil top
prism('planter_band', D['planter'], -1.45, TER + 0.2, m['concrete'], 'Street_facade')
prism('planter_soil', D['planter'], TER + 0.2, TER + 0.22, m['soil'], 'Planting')
for nm in ('photo_plant', 'bbq_plant'):
    prism(nm, D[nm], TER, TER + 0.3, m['concrete'], 'Planting'); prism(nm + '_soil', D[nm], TER + 0.3, TER + 0.32, m['soil'], 'Planting')
# entrance steps from the sidewalk (4 risers) in the planter gap
e0, e1 = D['ent']; s0, s1 = D['street_steps']
st = []
for i in range(4):
    xa = s1 - (i + 1) * (s1 - s0) / 5
    st.append((xa, e0, SID, s1 if i == 0 else s1 - i * (s1 - s0) / 5, e1, SID + (i + 1) * 0.18))
st.append((s0, e0, SID, s0 + (s1 - s0) / 5, e1, TER))
boxes('street_steps', st, m['concrete'], 'Street_facade')

# ======================= ITEMS =======================
HT = {  # kind: (z0, z1, material, collection)   heights above the item's own floor
    'rug': (0, 0.012, 'linen', 'Booths'), 'screen': (0, 1.8, 'jali', 'Booths'), 'bench': (0, 0.45, 'ikat', 'Booths'), 'btable': (0.72, 0.76, 'walnut', 'Booths'),
    'abench': (0, 0.45, 'ikat', 'Aivan'), 'atable': (0.72, 0.76, 'walnut', 'Aivan'), 'ascreen': (0, 1.2, 'jali', 'Aivan'),
    'tapchan': (0, 0.45, 'walnut', 'Tapchans_tent'), 'kurpacha': (0.45, 0.57, 'ikat', 'Tapchans_tent'), 'tapchanrug': (0.45, 0.47, 'suzani', 'Tapchans_tent'),
    'tapchantable': (0.45, 0.78, 'walnut', 'Tapchans_tent'), 'sofa': (0, 0.42, 'ikat', 'Tapchans_tent'), 'carpet': (0, 0.015, 'suzani', 'Tapchans_tent'),
    'otable': (0, 0.45, 'white', 'Tapchans_tent'), 'pole': (0, 2.3, 'walnut', 'Tapchans_tent'),
    'pit': (0, 0.08, 'soil', 'Trees'), 'ringbench': (0, 0.45, 'oak', 'Trees'), 'hauzborder': (0, 0.45, 'majolica', 'Fountain'), 'hauz': (0, 0.36, 'water', 'Fountain'),
    'medallion': (0, 0.008, 'majolica', 'Fountain'), 'plantbed': (0, 0.4, 'concrete', 'Planting'),
    'backbar': (0, 0.95, 'walnut', 'Bar'), 'barbody': (0, 1.05, 'lapis', 'Bar'), 'bartop': (1.03, 1.09, 'terrazzo', 'Bar'), 'barreturn': (0, 1.09, 'terrazzo', 'Bar'),
    'coffee': (0.95, 1.35, 'steel', 'Bar'), 'sink': (0.95, 0.97, 'steel', 'Bar'),
    'shelving': (0, 2.2, 'walnut', 'Service'), 'counter': (0, 0.95, 'steel', 'Service'), 'screenwall': (0, 1.6, 'jali', 'Service'),
    'station': (0, 1.0, 'turq', 'Service'), 'host': (0, 1.05, 'turq', 'Service'),
    'bbqfloor': (0, 0.012, 'slate', 'Mangal'), 'firewall': (0, 2.4, 'brick', 'Mangal'), 'tandoorblock': (0, 0.85, 'majolica', 'Mangal'),
    'mangal': (0, 0.85, 'black', 'Mangal'), 'ledge': (0, 0.9, 'steel', 'Mangal'), 'kazanblock': (0, 0.7, 'brick', 'Mangal'),
    'sinkbins': (0, 0.9, 'steel', 'Mangal'), 'prep': (0, 0.9, 'steel', 'Mangal'), 'pass': (0, 0.95, 'steel', 'Mangal'), 'glass': (0.95, 1.4, 'glass', 'Mangal'),
    'hood': (2.0, 2.45, 'steel', 'Mangal'), 'storage': (0, 2.2, 'walnut', 'Mangal'),
    'phdrape': (0, 2.8, 'velvet', 'Photo_lounge'), 'phrug': (0, 0.015, 'suzani', 'Photo_lounge'), 'firebowl': (0, 0.4, 'concrete', 'Photo_lounge'),
    'ltable': (0, 0.4, 'brass', 'Photo_lounge'), 'pouf': (0, 0.4, 'ikat', 'Photo_lounge'), 'jar': (0, 0.75, 'clay', 'Photo_lounge'),
    'flantern': (0, 0.6, 'brass', 'Photo_lounge'), 'runner': (0, 0.015, 'suzani', 'Corridor'),
    'sbench': ('S', 0.45, 'concrete', 'Street_facade'), 'sback': ('S', 1.0, 'majolica', 'Street_facade'), 'sebil': ('S', 2.6, 'majolica', 'Street_facade'),
    'sebilbasin': ('S', 0.55, 'water', 'Street_facade'), 'sarch': ('S', 2.9, 'jali', 'Street_facade'), 'portal': ('S', 3.4, 'brick', 'Street_facade'),
    'pot': (0, 0.6, 'clay', 'Planting'), 'spalm': ('S', 0.75, 'clay', 'Planting'),
}
counter = {}
for it in D['items']:
    k = it['kind']
    if k == 'table':                                       # modular table: top + pedestal(s)
        for r in it['poly']:
            base = 0.0 if on_plat(r) else TER; x0, y0, x1, y1 = bbox(r)
            n = it.get('mods', 1); ax = it.get('axis', 'x'); legs = []
            for j in range(n):
                cx = x0 + (j + .5) * (x1 - x0) / n if ax == 'x' else (x0 + x1) / 2
                cy = (y0 + y1) / 2 if ax == 'x' else y0 + (j + .5) * (y1 - y0) / n
                legs.append((cx - 0.04, cy - 0.04, base, cx + 0.04, cy + 0.04, base + 0.72)); legs.append((cx - 0.22, cy - 0.22, base, cx + 0.22, cy + 0.22, base + 0.03))
            boxes(f'table_{n * 2}p', [(x0, y0, base + 0.72, x1, y1, base + 0.76)], m['oak'], 'Furniture'); boxes('table_base', legs, m['bronze'], 'Furniture')
        continue
    if k == 'chair':
        for r in it['poly']:
            base = 0.0 if on_plat(r) else TER; x0, y0, x1, y1 = bbox(r); bk = it.get('back', 'n'); t_ = 0.05
            parts = [(x0 + .02, y0 + .02, base + 0.42, x1 - .02, y1 - .02, base + 0.47, 1)]
            for lx, ly in ((x0 + .04, y0 + .04), (x1 - .07, y0 + .04), (x0 + .04, y1 - .07), (x1 - .07, y1 - .07)): parts.append((lx, ly, base, lx + .03, ly + .03, base + 0.42))
            parts.append({'n': (x0, y1 - t_, base + 0.47, x1, y1, base + 0.86), 's': (x0, y0, base + 0.47, x1, y0 + t_, base + 0.86),
                          'e': (x1 - t_, y0, base + 0.47, x1, y1, base + 0.86), 'w': (x0, y0, base + 0.47, x0 + t_, y1, base + 0.86)}[bk])
            boxes('chair', parts, [m['walnut'], m['ikat']], 'Furniture')
        continue
    if k == 'stool':
        for r in it['poly']:
            cx, cy = cen(r); cylinder('bar_stool_seat', cx, cy, TER + 0.72, TER + 0.77, 0.2, m['ikat'], 'Bar'); cylinder('bar_stool_leg', cx, cy, TER, TER + 0.72, 0.03, m['bronze'], 'Bar', n=8)
        continue
    if k in ('samovar', 'tandoor', 'kazan'):
        for r in it['poly']:
            cx, cy = cen(r); rad = (bbox(r)[2] - bbox(r)[0]) / 2
            if k == 'samovar': cylinder('samovar', cx, cy, TER + 0.95, TER + 1.5, rad * .7, m['brass'], 'Bar', r2=rad * .45)
            elif k == 'tandoor': cylinder('tandoor', cx, cy, TER + 0.85, TER + 1.0, rad, m['clay'], 'Mangal', r2=rad * .6)
            else: cylinder('kazan', cx, cy, TER + 0.7, TER + 0.95, rad, m['black'], 'Mangal', r2=rad * .9)
        continue
    if k == 'lantern':
        for r in it['poly']:
            cx, cy = cen(r); base = 0.0 if on_plat(r) else TER
            cylinder('lantern', cx, cy, base + 1.9, base + 2.25, 0.13, m['glow_soft'], 'Lights', n=8); cylinder('lantern_rod', cx, cy, base + 2.25, top(cx) - 0.55, 0.008, m['bronze'], 'Lights', n=6)
        continue
    if k == 'flamp':
        for r in it['poly']:
            cx, cy = cen(r); cylinder('floor_lantern', cx, cy, TER, TER + 0.55, 0.08, m['glow_soft'], 'Corridor', n=8)
        continue
    if k == 'candle':
        for r in it['poly']:
            cx, cy = cen(r); cylinder('candle', cx, cy, TER, TER + 0.15, 0.04, m['candle'], 'Photo_lounge', n=8)
        continue
    if k == 'curtain':                                     # velvet walls of the draped corridor + swags overhead
        pts = it['poly'][0]; (xa, ya), (xb_, yb_) = pts[0], pts[-1]
        side = 1 if ya < (D['ent'][0] + D['ent'][1]) / 2 else -1
        boxes('corridor_curtain', [(xa, ya - 0.04, TER, xb_, ya + 0.04, TER + 2.6)], m['velvet'], 'Corridor')
        continue
    if k not in HT: continue
    z0, z1, mn, cn = HT[k]
    for r in it['poly']:
        if z0 == 'S': prism(k, [r], SID, SID + z1, m[mn], cn); continue
        base = 0.0 if on_plat(r) else TER
        if k in ('ascreen', 'abench', 'atable'): base = 0.0
        prism(k, [r], base + z0, base + z1, m[mn] if mn in m else mat(mn), cn)
        if k in ('btable', 'atable'):
            cx, cy = cen(r); boxes(k + '_leg', [(cx - .05, cy - .05, base, cx + .05, cy + .05, base + 0.72)], m['bronze'], cn)
        if k == 'tapchan':
            x0, y0, x1, y1 = bbox(r); boxes('tapchan_rail', [(x0, y0, base + 0.45, x1, y0 + 0.05, base + 0.75), (x0, y1 - 0.05, base + 0.45, x1, y1, base + 0.75), (x0, y0, base + 0.45, x0 + 0.05, y1, base + 0.75)], m['walnut'], cn)
        if k == 'firebowl':
            cx, cy = cen(r); cylinder('fire', cx, cy, base + 0.4, base + 0.75, 0.22, m['fire'], 'Lights', n=12, r2=0.02)
        if k == 'portal':
            x0, y0, x1, y1 = bbox(r); prism('portal_cap', [r], SID + 3.0, SID + 3.4, m['majolica'], cn)
        if k == 'hood':
            cx, cy = cen(r); boxes('mangal_stack', [(cx - 0.2, cy - 0.2, base + 2.45, cx + 0.2, cy + 0.2, 5.2)], m['steel'], 'Mangal')

# aivan rails + steps (terrace -> aivan) + bar steps + ramp
rails = []
for (a, b) in D['rail']:
    (x0, y0), (x1, y1) = a, b
    rails.append((min(x0, x1) - 0.025, min(y0, y1) - 0.025, 0.0, max(x0, x1) + 0.025, max(y0, y1) + 0.025, 1.0))
boxes('aivan_rail_jali', rails, m['jali'], 'Aivan')
for it in D['items']:
    if it['kind'] in ('stepsA', 'stepsB', 'barsteps'):
        x0, y0, x1, y1 = bbox(it['poly'][0]); st = []
        for i in range(3):
            if it['kind'] == 'barsteps': st.append((x0, y0 + i * (y1 - y0) / 3, TER, x1, y1, TER + (i + 1) * 0.15))
            else: st.append((x1 - (i + 1) * (x1 - x0) / 3, y0, TER, x1 - i * (x1 - x0) / 3, y1, TER + (i + 1) * 0.15))
        boxes(it['kind'], st, m['oak'], 'Aivan')
    if it['kind'] == 'ramp':
        x0, y0, x1, y1 = bbox(it['poly'][0])
        bm = bmesh.new(); vs = [bm.verts.new(v) for v in ((x0, y0, 0), (x1, y0, 0), (x1, y1, TER), (x0, y1, TER), (x0, y0, TER - 0.1), (x1, y0, TER - 0.1), (x1, y1, TER - 0.1), (x0, y1, TER - 0.1))]
        for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj('ramp_1_12', bm, [m['concrete']], 'Aivan')

# tent: fabric walls on W/N/S + pyramid canopy
tx0, ty0, tx1, ty1 = D['tent']; tz = TER + 2.3; apex = TER + 2.95
boxes('tent_walls', [(tx0 - 0.05, ty0 - 0.05, TER, tx0, ty1 + 0.05, tz), (tx0, ty0 - 0.05, TER, tx1 + 0.05, ty0, tz), (tx0, ty1, TER, tx1 + 0.05, ty1 + 0.05, tz)], m['suzani'], 'Tapchans_tent')
bm = bmesh.new(); c = [bm.verts.new(v) for v in ((tx0 - .05, ty0 - .05, tz), (tx1 + .05, ty0 - .05, tz), (tx1 + .05, ty1 + .05, tz), (tx0 - .05, ty1 + .05, tz))]
ap = bm.verts.new(((tx0 + tx1) / 2, (ty0 + ty1) / 2, apex))
for i in range(4): bm.faces.new((c[i], c[(i + 1) % 4], ap))
new_obj('tent_canopy', bm, [m['velvet']], 'Tapchans_tent')
# corridor swags overhead
e0, e1 = D['ent']; t0, t1 = D['tun']; sw_ = []
for x in [t0 + 0.3 + 0.7 * i for i in range(int((t1 - t0) / 0.7))]:
    for j in range(8):
        y = e0 + 0.1 + j * (e1 - e0 - 0.2) / 8; z = TER + 2.55 - 0.35 * math.sin(math.pi * (j + .5) / 8)
        sw_.append((x - 0.25, y, z - 0.03, x + 0.25, y + (e1 - e0 - 0.2) / 8, z))
boxes('corridor_swags', sw_, m['velvet'], 'Corridor')

# ======================= TREES + PLANTING =======================
rr = random.Random(7)
for i, (x, y) in enumerate(D['trees']):
    cylinder(f'chinar_trunk_{i}', x, y, TER, 5.2, 0.32, m['bark'], 'Trees', n=16, r2=0.2)
    pts = [(x + 2.0 * math.cos(a) * rr.uniform(.7, 1), y + 2.0 * math.sin(a) * rr.uniform(.7, 1), 5.2 + rr.uniform(-.4, .6), rr.uniform(1.1, 1.6)) for a in [k * 0.785 for k in range(8)]]
    pts.append((x, y, 6.2, 1.8)); blob(f'chinar_canopy_{i}', pts, m['leaf'], 'Trees')
for sp, x, y, r in D['plants']:
    zb = TER + (0.22 if sp in ('pom', 'plum', 'jas', 'herb') and x > 8 else 0.0)
    if sp == 'pom':
        cylinder('pomegranate_trunk', x, y, zb, zb + 1.1, 0.06, m['bark'], 'Planting', n=8)
        blob('pomegranate_crown', [(x + rr.uniform(-.2, .2), y + rr.uniform(-.2, .2), zb + 1.5 + rr.uniform(-.2, .2), r * .55) for _ in range(4)], m['leaf2'], 'Planting', 1)
        blob('pomegranate_fruit', [(x + r * .5 * math.cos(a), y + r * .5 * math.sin(a), zb + 1.35, 0.06) for a in range(0, 6)], m['pomfruit'], 'Planting', 1)
    elif sp == 'plum':
        cylinder('plumeria_trunk', x, y, zb, zb + 1.6, 0.08, m['bark'], 'Planting', n=8)
        blob('plumeria_crown', [(x + r * .5 * math.cos(a), y + r * .5 * math.sin(a), zb + 2.0, r * .45) for a in range(0, 6)], m['leaf2'], 'Planting', 1)
        blob('plumeria_flowers', [(x + r * .6 * math.cos(a * 1.1), y + r * .6 * math.sin(a * 1.1), zb + 2.25, 0.07) for a in range(9)], m['bloom'], 'Planting', 1)
    elif sp in ('areca', 'banana'):
        for j in range(5 if sp == 'areca' else 4):
            a = j * 2 * math.pi / (5 if sp == 'areca' else 4)
            boxes(f'{sp}_leaf', [(x + .1 * math.cos(a) - .06, y + .1 * math.sin(a) - .06, zb + .5, x + r * .7 * math.cos(a) + .06, y + r * .7 * math.sin(a) + .06, zb + (2.0 if sp == 'areca' else 1.7))], m['leaf'], 'Planting')
    elif sp == 'herb': blob('herbs', [(x, y, zb + 0.15, r * .7)], m['leaf2'], 'Planting', 1)
    elif sp == 'jas': blob('jasmine', [(x, y, zb + 0.4, r)], m['leaf2'], 'Planting', 1)
# planter shrubs along the street band (low-poly) + bougainvillea on the bench backs
shr = []
for y in [0.6 * k for k in range(1, 64)]:
    if D['ent'][0] - 0.8 < y < D['ent'][1] + 0.8: continue
    shr.append((xb(y) - 1.15 + rr.uniform(-.15, .15), y, TER + 0.45, rr.uniform(0.28, 0.42)))
blob('planter_shrubs', shr, m['leaf'], 'Planting', 1)
bou = []
for it in D['items']:
    if it['kind'] == 'sback':
        _, y0, _, y1 = bbox(it['poly'][0]); y = y0 + 0.3
        while y < y1: bou.append((xb(y) - 0.62, y, SID + 1.05, 0.16)); y += 0.45
blob('bougainvillea', bou, m['magenta'], 'Planting', 1)
# kids play elements
boxes('play_block', [(-6.8, 0.4, TER, -4.2, 1.7, TER + 0.7)], m['play_o'], 'Kids'); boxes('play_sand', [(-3.4, 2.6, TER, -0.9, 3.7, TER + 0.35)], m['play_b'], 'Kids')
cylinder('play_drum', -5.4, 3.0, TER, TER + 0.6, 0.55, m['play_g'], 'Kids'); cylinder('play_seat', -2.2, 1.1, TER, TER + 0.45, 0.45, m['play_y'], 'Kids')

# ======================= ROOF =======================
for i, r in enumerate(D['roof']):
    bm = bmesh.new(); pts = r
    a = [bm.verts.new((x, y, top(x) - 0.05)) for x, y in pts]; b = [bm.verts.new((x, y, top(x))) for x, y in pts]
    f = bm.faces.new(list(reversed(a))); f.material_index = 1
    f = bm.faces.new(b); f.material_index = 0
    n = len(pts)
    for j in range(n): bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj(f'roof_panel_{i}', bm, [m['bronze'], m['roofwood']], 'Roof_skin')
for y, xe in D['beams']:
    sloped_box(f'roof_beam_y{y:.1f}', 0.0, xe, y - 0.1, y + 0.1, lambda x: top(x) - 0.25, 0.3, m['bronze'], 'Roof_structure')
for x, y0, y1 in D['purlins']:
    sloped_box('purlin', x - 0.04, x + 0.04, y0, y1, lambda xx: top(xx) - 0.05, 0.2, m['bronze'], 'Roof_structure')
boxes('facade_ledger', [(0.0, 0.0, top(0) - 0.6, 0.18, 37.1, top(0) - 0.05)], m['bronze'], 'Roof_structure')
for x, y in D['cols']:
    if y < 0.6 and x < 0: continue
    zt = top(x) - 0.55
    boxes('column_steel', [(x - 0.075, y - 0.075, TER, x + 0.075, y + 0.075, zt)], m['bronze'], 'Roof_structure')
    boxes('column_wood_clad', [(x - 0.15, y - 0.15, TER + 0.2, x + 0.15, y + 0.15, TER + 2.4)], m['oak'], 'Roof_structure')
gut = [(xb(y) - 0.3, y, top(xb(y)) - 0.28, xb(y), y + 0.6, top(xb(y)) - 0.02) for y in [0.6 * k for k in range(-2, 63)]]
boxes('gutter_street', gut, m['bronze'], 'Roof_structure')
for r in D['courts']:
    x0, y0, x1, y1 = bbox(r)
    boxes('court_gutter', [(x0 - .15, y0 - .15, top(x1) - .3, x1 + .15, y0, top(x0)), (x0 - .15, y1, top(x1) - .3, x1 + .15, y1 + .15, top(x0)),
                           (x0 - .15, y0, top(x0) - .3, x0, y1, top(x0)), (x1, y0, top(x1) - .3, x1 + .15, y1, top(x1))], m['bronze'], 'Roof_structure')

def flatten_materials():
    """glTF/FBX/OBJ cannot carry procedural shaders: bake each material to one representative flat colour"""
    for mm in bpy.data.materials:
        if not mm.use_nodes: continue
        b = mm.node_tree.nodes.get('Principled BSDF')
        if not b or not b.inputs['Base Color'].is_linked: continue
        src = b.inputs['Base Color'].links[0].from_node; col = None
        if src.type == 'TEX_IMAGE' and src.image:
            px = list(src.image.pixels[:]); n = len(px) // 4
            col = [sum(px[i::4][:n]) / n for i in range(3)]
        elif src.type == 'VALTORGB':
            e = src.color_ramp.elements; col = [(e[0].color[i] + 2 * e[-1].color[i]) / 3 for i in range(3)]
        elif src.type == 'MIX':
            A, B_ = src.inputs['A'].default_value, src.inputs['B'].default_value; col = [(A[i] + B_[i]) / 2 for i in range(3)]
        for l in list(b.inputs['Base Color'].links): mm.node_tree.links.remove(l)
        if b.inputs['Normal'].is_linked:
            for l in list(b.inputs['Normal'].links): mm.node_tree.links.remove(l)
        for key, c in (('ikat', (0.40, 0.05, 0.06)), ('suzani', (0.55, 0.16, 0.10)), ('floor', (0.80, 0.62, 0.45))):
            if key in mm.name: col = c
        if col: b.inputs['Base Color'].default_value = (*col, 1)

# ======================= SAVE / EXPORT =======================
for o in bpy.data.objects: o.select_set(False)
base = os.path.join(OUTD, f'samarkand-base3d-{REV}')
bpy.ops.wm.save_as_mainfile(filepath=base + '.blend')
# ======================= RENDERS =======================
if DO_RENDER:
    bl2.sun(elev=40, rot=235, strength=2.2, color=(1, 0.9, 0.78))
    VIEWS = [('aerial', (30, -7, 21), (6, 17.5, 0), 28, [], -1.3),
             ('aerial_cutaway', (28, -5, 19), (5.5, 18, 0), 28, ['Roof_skin'], -1.3),
             ('street', (17.5, 9.0, 0.4), (6.0, 18.5, 0.9), 22, [], -1.3),
             ('alley_north', (7.3, 17.0, 1.15), (5.0, 30.0, 0.9), 20, [], 0.4)]
    only = os.environ.get('VIEWS')
    for name, loc, tgt, lens, hide, ev in VIEWS:
        sc.view_settings.exposure = ev
        if only and name not in only.split(','): continue
        for cn, c in COLS.items(): c.hide_render = cn in hide
        bl2.camera(loc, tgt, lens=lens)
        bl.render(os.path.join(OUTD, f'samarkand-base3d-{REV}-{name}.png'), W, H, S)

# ======================= EXPORT (flat colours) =======================
flatten_materials()
bpy.ops.export_scene.gltf(filepath=base + '.glb', export_format='GLB', export_apply=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=base + '.fbx', apply_unit_scale=True, axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')
bpy.ops.wm.obj_export(filepath=base + '.obj', forward_axis='NEGATIVE_Z', up_axis='Y', export_materials=True)
print('saved', base, len(bpy.data.objects), 'objects')

