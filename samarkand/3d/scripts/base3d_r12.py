"""Samarkand terrace — 3D BASE MODEL (LOD 200) of the whole site, built from the plan data (R12: roof domes, Bukhara dome).
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
    dometile=mat('dometile', (0.60, 0.30, 0.17), rough=0.7, bump=0.15, noise_var=0.05),
    gaj=mat('gaj', (0.80, 0.64, 0.44), rough=0.8, bump=0.2, noise_var=0.06),
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
    q = []
    for p in pts:
        if not q or abs(p[0] - q[-1][0]) + abs(p[1] - q[-1][1]) > 1e-5: q.append(p)
    pts = q
    if len(pts) > 1 and abs(pts[0][0] - pts[-1][0]) + abs(pts[0][1] - pts[-1][1]) < 1e-5: pts = pts[:-1]
    if len(pts) < 3: return
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
boxes('ground', [(-45, -25, -1.6, 32.0, 75, -1.45)], m['ground'], 'Context')
boxes('road', [(14.9, -25, -1.32, 32, 75, -1.30)], m['asphalt'], 'Context')
boxes('beach_promenade', [(32.0, -25, -1.45, 36.0, 75, -1.17)], m['sidewalk'], 'Context')
boxes('beach_sand', [(36.0, -60, -1.9, 95.0, 110, -1.5)], mat('sand', (0.72, 0.63, 0.48), rough=0.95, noise_var=0.04), 'Context')
boxes('sea', [(95.0, -400, -2.2, 900.0, 500, -1.6)], mat('sea', (0.02, 0.24, 0.32), rough=0.12, coat=0.3), 'Context')
for yy in range(-20, 74, 9):
    cylinder('beach_palm_trunk', 34.0, yy, -1.17, 5.5, 0.16, m['bark'], 'Context', n=10, r2=0.11)
    for a_ in range(6): blob('beach_palm_leaf', [(34.0 + 1.2 * math.cos(a_) * t_, yy + 1.2 * math.sin(a_) * t_, 5.5 - 0.5 * t_ * t_, 0.28 - 0.08 * t_) for t_ in (0.3, 0.7, 1.0)], m['leaf'], 'Context', 1)
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
if 'inlays' in D:                                       # inlays sit flush in the slab (the main floor has them cut out)
    IN = D['inlays']
    prism('terrace_floor', D['floor_main'], -1.45, TER, m['floor'], 'Floors')
    prism('alley_girih', IN['alley'], -1.45, TER, m['girih'], 'Floors'); prism('kids_rubber', IN['kids'], -1.45, TER, m['rubber'], 'Floors')
    prism('bbq_floor_slate', IN['bbq'], -1.45, TER, m['slate'], 'Floors'); prism('medallion_mosaic', IN['medallion'], -1.45, TER, m['majolica'], 'Floors')
    prism('aryk_channel', IN['aryk'], -1.45, TER - 0.08, m['majolica'], 'Fountain'); prism('aryk_water', IN['aryk'], TER - 0.08, TER - 0.03, m['water'], 'Fountain')
    prism('hauz_rim', D['hauz_ring'], TER, TER + (0.38 if os.environ.get('DETAIL', '1') == '1' else 0.45), m['majolica'], 'Fountain')     # detail pass adds the stone coping
else:
    prism('terrace_floor', D['floor'], -1.45, TER, m['floor'], 'Floors')
    prism('alley_girih', D['alley'], TER, TER + 0.012, m['girih'], 'Floors')
    prism('kids_rubber', D['kids'], -1.45, TER + 0.03, m['rubber'], 'Floors')
prism('aivan_deck', D['plat'], TER, 0.0, m['deck'], 'Floors')
# planter band: retaining wall to the sidewalk, soil top
prism('planter_band', D['planter'], -1.45, TER - 0.03, m['concrete'], 'Street_facade')     # flush with the terrace: posts / walls stand on it
prism('planter_soil', D['planter'], TER - 0.03, TER, m['soil'], 'Planting')
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
    'woodstack': (0, 1.9, 'walnut', 'Mangal'), 'aryk': (0, 0.01, 'water', 'Fountain'), 'bridge': (0, 0.14, 'concrete', 'Fountain'),
    'gatepost': (0, 3.1, 'walnut', 'North_gate'), 'bportal': (0, 2.2, 'walnut', 'Booths'),
    'rotunda': (0, 0.15, 'oak', 'Bukhara_dome'), 'drum': (0.15, 2.3, 'jali', 'Bukhara_dome'), 'rbox': (0.15, 1.05, 'glass', 'Bukhara_dome'),
}
counter = {}
DETAIL = os.environ.get('DETAIL', '1') == '1'
SKIP = {'chair', 'lantern', 'screen', 'bportal', 'drum', 'rbox', 'woodstack', 'tandoor', 'kazan', 'table', 'bench', 'btable', 'rug', 'pole', 'gatepost',
        'flamp', 'medallion', 'bbqfloor', 'aryk', 'hauzborder', 'abench', 'sofa', 'atable', 'portal', 'runner', 'backbar', 'barbody', 'bartop', 'barreturn', 'stool', 'coffee', 'sink', 'samovar', 'sebil', 'sebilbasin'} if DETAIL else set()
if DETAIL:                                              # things that rest on something else start on its top
    HT_FIX = {'otable': (0.015, 0.465), 'tapchantable': (0.47, 0.78), 'bridge': (0.06, 0.2)}
else: HT_FIX = {}
for it in D['items']:
    k = it['kind']
    if k in SKIP: continue
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
    if k in HT_FIX: z0, z1 = HT_FIX[k]
    for r in it['poly']:
        if z0 == 'S': prism(k, [r], SID, SID + z1, m[mn], cn); continue
        base = 0.0 if on_plat(r) else TER
        if k in ('ascreen', 'abench', 'atable'): base = 0.0
        if not (DETAIL and k == 'hood'): prism(k, [r], base + z0, base + z1, m[mn] if mn in m else mat(mn), cn)
        if k in ('btable', 'atable'):
            cx, cy = cen(r); boxes(k + '_leg', [(cx - .05, cy - .05, base, cx + .05, cy + .05, base + 0.72)], m['bronze'], cn)
        if k == 'tapchan' and not DETAIL:
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
    if DETAIL and abs(x0 - 3.3) < 1e-3 and abs(x1 - 3.3) < 1e-3: continue          # replaced by the Khiva arcade (detail pass)
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
        bm = bmesh.new(); vs = [bm.verts.new(v) for v in ((x0, y0, 0), (x1, y0, 0), (x1, y1, TER + 0.005), (x0, y1, TER + 0.005), (x0, y0, TER), (x1, y0, TER), (x1, y1, TER), (x0, y1, TER))]   # wedge resting on the slab
        for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj('ramp_1_12', bm, [m['concrete']], 'Aivan')

# tent: fabric walls on W/N/S + pyramid canopy
for tx0, ty0, tx1, ty1 in D.get('tents', [D['tent']]):
  tz = TER + 2.3; apex = TER + 2.95
  if DETAIL: continue
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
if not DETAIL: boxes('corridor_swags', sw_, m['velvet'], 'Corridor')

# ======================= TREES + PLANTING =======================
rr = random.Random(7)
for i, (x, y) in enumerate(D['trees']):
    cylinder(f'chinar_trunk_{i}', x, y, TER, 6.4, 0.32, m['bark'], 'Trees', n=16, r2=0.2)
    for a in [k * 1.257 for k in range(5)]: cylinder(f'chinar_branch_{i}', x + 0.5 * math.cos(a), y + 0.5 * math.sin(a), 5.6, 6.6, 0.1, m['bark'], 'Trees', n=6, r2=0.06)
    rc, zc, r0_, r1_ = ((2.0, 7.2, 1.1, 1.5) if i == 0 else (1.6, 6.6, 0.95, 1.25))
    pts = [(x + rc * math.cos(a) * rr.uniform(.85, 1), y + rc * math.sin(a) * rr.uniform(.85, 1), zc + rr.uniform(0.0, .3), rr.uniform(r0_, r1_)) for a in [k * 0.785 for k in range(8)]]
    pts.append((x, y, zc + 0.9, r1_ + 0.3)); blob(f'chinar_canopy_{i}', pts, m['leaf'], 'Trees')
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
    sx_, sr_ = xb(y) - 1.15 + rr.uniform(-.15, .15), rr.uniform(0.28, 0.42)
    if DETAIL:                                                     # shrubs only where the planter soil is, clear of walls / benches / columns
        from shapely.geometry import Point as _P, Polygon as _Poly
        if '_PL' not in globals(): globals()['_PL'] = [_Poly(r_) for r_ in D['planter']]
        if not any(q_.contains(_P(sx_, y).buffer(sr_ * 0.9)) for q_ in _PL): continue
        if any(math.hypot(sx_ - cx_, y - cy_) < sr_ + 0.3 for cx_, cy_ in D['cols']): continue
    shr.append((sx_, y, TER + 0.45, sr_))
blob('planter_shrubs', shr, m['leaf'], 'Planting', 1)
bou = []
for it in D['items']:
    if it['kind'] == 'sback':
        _, y0, _, y1 = bbox(it['poly'][0]); y = y0 + 0.3
        while y < y1: bou.append((xb(y) - 0.62, y, SID + 1.05, 0.16)); y += 0.45
blob('bougainvillea', bou, m['magenta'], 'Planting', 1)
# kids play elements
boxes('play_block', [(-6.8, 0.45, TER, -4.9, 1.5, TER + 0.7)], m['play_o'], 'Kids'); boxes('play_sand', [(-3.0, 0.45, TER, -0.9, 1.45, TER + 0.35)], m['play_b'], 'Kids')
cylinder('play_drum', -4.0, 1.3, TER, TER + 0.6, 0.55, m['play_g'], 'Kids'); cylinder('play_seat', -2.3, 2.0, TER, TER + 0.45, 0.38, m['play_y'], 'Kids')
boxes('kids_fence', [(-7.25, 2.6, TER, -4.3, 2.65, TER + 0.9), (-3.4, 2.6, TER, -0.15, 2.65, TER + 0.9), (-0.2, 0.15, TER, -0.15, 2.65, TER + 0.9)], m['oak'], 'Kids')

# ======================= ROOF =======================
for i, r in enumerate(D['roof']):
    bm = bmesh.new(); pts = r
    a = [bm.verts.new((x, y, top(x) - 0.05)) for x, y in pts]; b = [bm.verts.new((x, y, top(x))) for x, y in pts]
    f = bm.faces.new(list(reversed(a))); f.material_index = 1
    f = bm.faces.new(b); f.material_index = 0
    n = len(pts)
    for j in range(n): bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj(f'roof_panel_{i}', bm, [m['bronze'], m['roofwood']], 'Roof_skin')
STEEL_DETAIL = os.environ.get('DETAIL', '1') == '1'
def sloped_parts(name, parts, mm, cname):
    """one closed object from several boxes whose tops follow linear z(x): parts = [(x0, x1, y0, y1, ztop_fn, depth)]"""
    bm = bmesh.new()
    for x0, x1, y0, y1, fn, dep in parts:
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        a = [bm.verts.new((x, y, fn(x) - dep)) for x, y in pts]; b = [bm.verts.new((x, y, fn(x))) for x, y in pts]
        bm.faces.new(list(reversed(a))); bm.faces.new(b)
        for i in range(4): bm.faces.new((a[i], a[(i + 1) % 4], b[(i + 1) % 4], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, [mm], cname)
def I_parts(x0, x1, yc, fn, D=0.3, B=0.15, tf=0.0107, tw=0.0071):
    """IPE-type section along x (IPE 300: 300 x 150, tf 10.7, tw 7.1), top following fn"""
    return [(x0, x1, yc - B / 2, yc + B / 2, fn, tf), (x0, x1, yc - tw / 2, yc + tw / 2, lambda x: fn(x) - tf, D - 2 * tf),
            (x0, x1, yc - B / 2, yc + B / 2, lambda x: fn(x) - D + tf, tf)]
RING_R = lambda d: d['r'] + 0.06                         # dome ring girder centre line (under the drum)
for y, xe in D['beams']:
    segs = [(0.18 if STEEL_DETAIL else 0.0, xe)]       # beams bear on the facade ledger face (x = 0.18)
    for d in D.get('domes', []):                      # beams frame into the dome ring girders (the beam's inner corner stops at the girder's outer flange edge)
        dy = abs(y - d['c'][1]); rt = (RING_R(d) + 0.075) if STEEL_DETAIL else (d['r'] + 0.2)
        dye = max(0.0, dy - 0.075) if STEEL_DETAIL else dy
        if dye < rt:
            h = math.sqrt(rt ** 2 - dye ** 2); c0, c1 = d['c'][0] - h, d['c'][0] + h
            segs = [(p, min(q, c0)) for p, q in segs if p < c0] + [(max(p, c1), q) for p, q in segs if q > c1]
    for p, q in segs:
        if STEEL_DETAIL: sloped_parts(f'roof_beam_y{y:.1f}', I_parts(p, q, y, lambda x: top(x) - 0.25), m['bronze'], 'Roof_structure')
        else: sloped_box(f'roof_beam_y{y:.1f}', p, q, y - 0.1, y + 0.1, lambda x: top(x) - 0.25, 0.3, m['bronze'], 'Roof_structure')
def trim_to_domes(x, y0, y1, extra):
    """purlin segment minus every dome curb disc (radius r + extra, widened by the purlin's half width): list of (y0, y1)"""
    segs = [(y0, y1)]
    for d in D.get('domes', []):
        cx, cy = d['c']; R = d['r'] + extra; dx = max(0.0, abs(x - cx) - 0.04)
        if dx >= R: continue
        h = math.sqrt(R ** 2 - dx ** 2); a, b = cy - h, cy + h
        segs = [(p, min(q, a)) for p, q in segs if p < a] + [(max(p, b), q) for p, q in segs if q > b]
    return [(p, q) for p, q in segs if q - p > 0.1]
cleats = []
for x, y0, y1 in D['purlins']:
    if STEEL_DETAIL:
        fn = lambda xx: top(xx) - 0.05                    # C200 purlin: web on the high side, flanges towards the street
        for y0, y1 in trim_to_domes(x, y0, y1, 0.125):
            sloped_parts('purlin', [(x - 0.04, x + 0.035, y0, y1, fn, 0.008), (x - 0.04, x - 0.034, y0, y1, lambda xx: fn(xx) - 0.008, 0.184),
                                    (x - 0.04, x + 0.035, y0, y1, lambda xx: fn(xx) - 0.192, 0.008)], m['bronze'], 'Roof_structure')
            for yb_, _ in D['beams']:
                if y0 + 0.05 < yb_ < y1 - 0.05: cleats.append((x - 0.05, x - 0.04, yb_ - 0.04, yb_ + 0.04, lambda xx: top(xx) - 0.13, 0.12))
    else: sloped_box('purlin', x - 0.04, x + 0.04, y0, y1, lambda xx: top(xx) - 0.05, 0.2, m['bronze'], 'Roof_structure')
cleats = list({(round(c[0], 4), round(c[1], 4)): c for c in cleats}.values())          # one cleat per crossing
if cleats: sloped_parts('purlin_cleats', cleats, m['steel'], 'Roof_structure')
boxes('facade_ledger', [(0.0, 0.0, 3.25, 0.18, 37.1, top(0) - 0.05)], m['bronze'], 'Roof_structure')        # ledger channel above the F1 glazing
for x, y in D['cols']:
    if y < 0.6 and x < 0: continue
    if DETAIL and any(a <= y <= b for a, b in ((D['ent'][0] - 0.7, D['ent'][0]), (D['ent'][1], D['ent'][1] + 0.7))): continue   # carried by the portal pylons
    zt = top(x) - 0.55
    boxes('column_steel', [(x - 0.075, y - 0.075, TER, x + 0.075, y + 0.075, zt)], m['bronze'], 'Roof_structure')
    if DETAIL: continue                                 # detail pass clads the column (Samarkand majolica column)
    z0c, z1c = TER + 0.2, TER + 2.4                     # wood sleeve: 4 boards around the steel column, flush, no overlap
    boxes('column_wood_clad', [(x - 0.15, y - 0.15, z0c, x + 0.15, y - 0.075, z1c), (x - 0.15, y + 0.075, z0c, x + 0.15, y + 0.15, z1c),
                               (x - 0.15, y - 0.075, z0c, x - 0.075, y + 0.075, z1c), (x + 0.075, y - 0.075, z0c, x + 0.15, y + 0.075, z1c)], m['oak'], 'Roof_structure')
gut = [(xb(y), y, top(xb(y)) - 0.2, xb(y) + 0.25, y + 0.6, top(xb(y)) - 0.04) for y in [0.6 * k for k in range(-2, 63)]]   # box gutter hung on the street edge
boxes('gutter_street', gut, m['bronze'], 'Roof_structure')
# ======================= ROOF DOMES (R12) =======================
ZR = D.get('dome_ring', 3.9); SEG = 48
T_ = 0.12
def dome_solid(d):
    """closed shell between the inner ellipsoid (r, rise) and the outer one (r+T, rise+T); flat annulus at the springing
    level ZR (the drum's top), conical lip at the oculus / lantern ring"""
    cx, cy = d['c']; r, h = d['r'], d['rise']; r0 = d['oc'] or d['lantern']
    th0 = math.asin(min(0.999, r0 / r)); N = 18
    ths = [th0 + (math.pi / 2 - th0) * k / N for k in range(N + 1)]
    bm = bmesh.new(); SEG = 96                         # local: finer rings for the ribbed shell
    def ringv(rad, z, rib=0.0): return [bm.verts.new((cx + rad * (1 + rib * math.cos(24 * 2 * math.pi * j / SEG)) * math.cos(2 * math.pi * j / SEG), cy + rad * (1 + rib * math.cos(24 * 2 * math.pi * j / SEG)) * math.sin(2 * math.pi * j / SEG), z)) for j in range(SEG)]
    O = [ringv((r + T_) * math.sin(t), ZR + (h + T_) * math.cos(t), 0.035 * math.sin(t) ** 0.5) for t in ths]; I = [ringv(r * math.sin(t), ZR + h * math.cos(t)) for t in ths]
    fo, fi, fl = [], [], []
    for a, b in zip(O[:-1], O[1:]):
        for j in range(SEG): fo.append(bm.faces.new((a[j], a[(j + 1) % SEG], b[(j + 1) % SEG], b[j])))
    for a, b in zip(I[:-1], I[1:]):
        for j in range(SEG): fi.append(bm.faces.new((b[j], b[(j + 1) % SEG], a[(j + 1) % SEG], a[j])))
    for a, b in ((I[0], O[0]), (O[-1], I[-1])):
        for j in range(SEG): fl.append(bm.faces.new((a[j], a[(j + 1) % SEG], b[(j + 1) % SEG], b[j])))
    for f in fi: f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces: f.smooth = True
    o = new_obj(f'dome_shell_{d["key"]}', bm, [m['dometile'], m['gaj']], 'Domes')
    return o, ths
for d in D.get('domes', []):
    cx, cy = d['c']; r0 = d['oc'] or d['lantern']
    o, ths = dome_solid(d)
    # drum: closed annulus r .. r+T from the sloping roof skin up to ZR (the shell's flat base)
    bm = bmesh.new(); rows = []
    for rad in (d['r'], d['r'] + T_):
        rows.append(([bm.verts.new((cx + rad * math.cos(2 * math.pi * j / SEG), cy + rad * math.sin(2 * math.pi * j / SEG), top(cx + rad * math.cos(2 * math.pi * j / SEG)))) for j in range(SEG)],
                     [bm.verts.new((cx + rad * math.cos(2 * math.pi * j / SEG), cy + rad * math.sin(2 * math.pi * j / SEG), ZR)) for j in range(SEG)]))
    (il, ih), (ol, oh) = rows
    for j in range(SEG):
        k = (j + 1) % SEG
        bm.faces.new((ol[j], ol[k], oh[k], oh[j])); bm.faces.new((ih[j], ih[k], il[k], il[j]))
        bm.faces.new((oh[j], oh[k], ih[k], ih[j])); bm.faces.new((il[j], il[k], ol[k], ol[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj(f'dome_drum_{d["key"]}', bm, [m['band']], 'Domes')
    if STEEL_DETAIL:                                  # ring girder (rolled IPE 300 in the roof plane) + drum curb (C200 ring) on it
        bm = bmesh.new(); Rg = RING_R(d); NS = 96
        def zt_(a, rr): return top(cx + rr * math.cos(a)) - 0.25
        for loop in ([(Rg - 0.075, 0.0), (Rg + 0.075, 0.0), (Rg + 0.075, -0.0107), (Rg - 0.075, -0.0107)],
                     [(Rg - 0.0036, -0.0107), (Rg + 0.0036, -0.0107), (Rg + 0.0036, -0.2893), (Rg - 0.0036, -0.2893)],
                     [(Rg - 0.075, -0.2893), (Rg + 0.075, -0.2893), (Rg + 0.075, -0.3), (Rg - 0.075, -0.3)]):
            rings_ = [[bm.verts.new((cx + rr * math.cos(2 * math.pi * j / NS), cy + rr * math.sin(2 * math.pi * j / NS), zt_(2 * math.pi * j / NS, rr) + hh)) for j in range(NS)] for rr, hh in loop]
            for a_, b_ in zip(rings_, rings_[1:] + rings_[:1]):
                for j in range(NS): bm.faces.new((a_[j], a_[(j + 1) % NS], b_[(j + 1) % NS], b_[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj(f'dome_ring_girder_{d["key"]}', bm, [m['bronze']], 'Roof_structure')
        bm = bmesh.new()
        loop = [(d['r'], 0.0), (d['r'] + 0.12, 0.0), (d['r'] + 0.12, 0.2), (d['r'], 0.2)]
        rings_ = [[bm.verts.new((cx + rr * math.cos(2 * math.pi * j / NS), cy + rr * math.sin(2 * math.pi * j / NS), zt_(2 * math.pi * j / NS, rr) + hh)) for j in range(NS)] for rr, hh in loop]
        for a_, b_ in zip(rings_, rings_[1:] + rings_[:1]):
            for j in range(NS): bm.faces.new((a_[j], a_[(j + 1) % NS], b_[(j + 1) % NS], b_[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj(f'dome_curb_{d["key"]}', bm, [m['steel']], 'Roof_structure')
    # ring beam inside the drum, under the springing line
    bm = bmesh.new(); prof = [(d['r'] - 0.15, ZR - 0.25), (d['r'], ZR - 0.25), (d['r'], ZR), (d['r'] - 0.15, ZR)]
    rg = [[bm.verts.new((cx + rr_ * math.cos(2 * math.pi * j / SEG), cy + rr_ * math.sin(2 * math.pi * j / SEG), zz)) for j in range(SEG)] for rr_, zz in prof]
    for si, (a, b) in enumerate(zip(rg, rg[1:] + rg[:1])):
        for j in range(SEG):
            f = bm.faces.new((a[j], a[(j + 1) % SEG], b[(j + 1) % SEG], b[j])); f.material_index = 1 if si == 3 else 0     # LED cove on the inner face
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj(f'dome_ring_{d["key"]}', bm, [m['bronze'], mat('coveglow', (1, .8, .55), emit=(1.0, 0.72, 0.42), strength=18.0)], 'Domes')
    # 12 ribs: closed 100 x 120 bars following the inner surface, stopping above the ring beam
    bm = bmesh.new(); r, h = d['r'], d['rise']
    for k in range(12):
        a = 2 * math.pi * k / 12; ca, sa = math.cos(a), math.sin(a); tx_, ty_ = -sa * 0.05, ca * 0.05; st_ = []
        for t in ths:
            if ZR + h * math.cos(t) < ZR + 0.14: break
            rho, z = r * math.sin(t), ZR + h * math.cos(t)
            nr = Vector((math.sin(t) / r, 0, math.cos(t) / h)).normalized()          # outward normal in the (rho, z) plane
            ri, zi = rho - nr.x * 0.12, z - nr.z * 0.12
            st_.append([bm.verts.new((cx + rho * ca + tx_, cy + rho * sa + ty_, z)), bm.verts.new((cx + rho * ca - tx_, cy + rho * sa - ty_, z)),
                        bm.verts.new((cx + ri * ca - tx_, cy + ri * sa - ty_, zi)), bm.verts.new((cx + ri * ca + tx_, cy + ri * sa + ty_, zi))])
        if len(st_) < 2: continue
        for p_, q_ in zip(st_[:-1], st_[1:]):
            for i in range(4): bm.faces.new((p_[i], p_[(i + 1) % 4], q_[(i + 1) % 4], q_[i]))
        bm.faces.new(list(reversed(st_[0]))); bm.faces.new(st_[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj(f'dome_ribs_{d["key"]}', bm, [m['gaj']], 'Domes')
    if d['lantern']:
        ro = (d['r'] + T_) * math.sin(ths[0]); lz = ZR + (d['rise'] + T_) * math.cos(ths[0])
        cylinder(f'dome_lantern_{d["key"]}', cx, cy, lz, lz + 0.5, ro, m['glass'], 'Domes', n=SEG)
        cylinder(f'dome_lantern_cap_{d["key"]}', cx, cy, lz + 0.5, lz + 0.85, ro + 0.1, m['dometile'], 'Domes', n=SEG, r2=0.05)
        cylinder(f'dome_finial_{d["key"]}', cx, cy, lz + 0.85, lz + 0.98, 0.05, m['brass'], 'Domes', n=12, r2=0.03)          # finial: neck, two balls, spike — stacked, touching
        cylinder(f'dome_finial_neck_{d["key"]}', cx, cy, lz + 1.12, lz + 1.2, 0.025, m['brass'], 'Domes', n=12, r2=0.02)
        cylinder(f'dome_finial_spike_{d["key"]}', cx, cy, lz + 1.3, lz + 1.45, 0.02, m['brass'], 'Domes', n=12, r2=0.004)
        blob(f'dome_finial_ball_{d["key"]}', [(cx, cy, lz + 1.05, 0.07), (cx, cy, lz + 1.25, 0.05)], m['brass'], 'Domes', 2)

# ======================= BUKHARA DOME (rotunda vitrine + shop) + KHIVA GATE =======================
if 'rot' in D and not DETAIL:
    rx, ry, rr_ = D['rot']
    for k in range(8):                                                   # hanging plates / lanterns in the lattice drum
        a = 2 * math.pi * k / 8; cylinder('rot_plate', rx + 0.3 * math.cos(a), ry + 0.3 * math.sin(a), TER + 1.2 + 0.25 * (k % 3), TER + 1.23 + 0.25 * (k % 3), 0.12, m['majolica'], 'Bukhara_dome', n=12)
    cylinder('rot_glow', rx, ry, TER + 0.2, TER + 2.2, 0.2, m['glow_soft'], 'Bukhara_dome', n=10)
    bm = bmesh.new(); rows = []
    for rad, z in ((1.15, TER + 2.55), (1.15, TER + 2.7), (0.9, TER + 2.7), (0.9, TER + 2.55)):
        rows.append([bm.verts.new((rx + rad * math.cos(2 * math.pi * j / SEG), ry + rad * math.sin(2 * math.pi * j / SEG), z)) for j in range(SEG)])
    for a_, b_ in zip(rows, rows[1:] + rows[:1]):
        for j in range(SEG): bm.faces.new((a_[j], a_[(j + 1) % SEG], b_[(j + 1) % SEG], b_[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); new_obj('rot_canopy_ring', bm, [m['brass']], 'Bukhara_dome')
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2; px, py = rx + 1.02 * math.cos(a), ry + 1.02 * math.sin(a)
        cylinder('rot_post', px, py, TER, TER + 2.7, 0.04, m['bronze'], 'Bukhara_dome', n=8)
    g0, g1 = D['gate']
    boxes('gate_beam', [(g0 - 0.25, 36.35, TER + 2.85, g1 + 0.25, 36.5, TER + 3.25)], m['walnut'], 'North_gate')
    boxes('gate_arch_panel', [(g0, 36.38, TER + 2.55, g1, 36.47, TER + 2.85)], m['jali'], 'North_gate')

if DETAIL: exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'detail_r12.py')).read())

def flatten_materials():
    """glTF/FBX/OBJ cannot carry procedural shaders: bake each material to one representative flat colour"""
    for mm in bpy.data.materials:
        if not mm.use_nodes: continue
        b = mm.node_tree.nodes.get('Principled BSDF')
        if not b or not b.inputs['Base Color'].is_linked: continue
        src = b.inputs['Base Color'].links[0].from_node; col = None
        if src.type == 'TEX_IMAGE' and src.image:
            continue                                     # textured: exported with UVs by export_prep()
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

def export_prep():
    """image textures for glTF: box-projected (Object coords) textures -> UV map; box UVs computed per face from world coords"""
    boxmats = {}
    for mm in bpy.data.materials:
        if not mm.use_nodes: continue
        N, Lk = mm.node_tree.nodes, mm.node_tree.links
        for it in list(N):
            if it.type == 'TEX_IMAGE' and it.projection == 'BOX':
                size = 1.0
                if it.inputs['Vector'].is_linked:
                    mp = it.inputs['Vector'].links[0].from_node
                    if mp.type == 'MAPPING': size = 1 / max(1e-6, mp.inputs['Scale'].default_value[0])
                    for l in list(it.inputs['Vector'].links): Lk.remove(l)
                it.projection = 'FLAT'; uvn = N.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'; Lk.new(uvn.outputs['UV'], it.inputs['Vector'])
                boxmats[mm.name] = size
    for o in bpy.data.objects:
        if o.type != 'MESH': continue
        me = o.data; names = [ms.name if ms else '' for ms in me.materials]
        if me.get('kit'): continue                                        # kit assets carry their own UVs
        if not any(n in boxmats for n in names): continue
        bm = bmesh.new(); bm.from_mesh(me)
        uv = bm.loops.layers.uv.get('UVMap') or bm.loops.layers.uv.new('UVMap')
        mw = o.matrix_world
        for f in bm.faces:
            n = names[f.material_index] if f.material_index < len(names) else ''
            if n not in boxmats: continue
            sz = boxmats[n]; nr = f.normal; ax = max(range(3), key=lambda i: abs(nr[i]))
            for lp in f.loops:
                co = mw @ lp.vert.co
                lp[uv].uv = ((co.y, co.z) if ax == 0 else (co.x, co.z) if ax == 1 else (co.x, co.y))[0] / sz, ((co.y, co.z) if ax == 0 else (co.x, co.z) if ax == 1 else (co.x, co.y))[1] / sz
        bm.to_mesh(me); bm.free()
        if me.uv_layers.get('UVMap'): me.uv_layers.active = me.uv_layers['UVMap']
    print('export_prep: textured materials', len(boxmats))

# ======================= SAVE / EXPORT =======================
for o in bpy.data.objects: o.select_set(False)
base = os.path.join(OUTD, f'samarkand-base3d-{REV}')
bpy.ops.wm.save_as_mainfile(filepath=base + '.blend')
# ======================= RENDERS =======================
if DO_RENDER:
    w_ = sc.world.node_tree.nodes; w_['Background'].inputs['Strength'].default_value = 1.0
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    bl2.sun(elev=42, rot=120, strength=4.5, color=(1, 0.93, 0.84))
    for xx in (2.6, 6.4, 10.2):                                   # soft daylight fill under the roof (bounce from the street)
        for yy in range(2, 37, 4):
            if xx > xb(yy) - 1.6: continue
            ld = bpy.data.lights.new('fill', 'AREA'); ld.energy = 120; ld.size = 2.6; ld.color = (1.0, 0.92, 0.82)
            lo_ = bpy.data.objects.new('fill', ld); lo_.location = (xx, yy, top(xx) - 0.62); coll('Lights_fill').objects.link(lo_)
    def cam2p(loc, tgt, lens, shift):
        cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.shift_y = shift; cd.sensor_width = 36
        o = bpy.data.objects.new('cam', cd); coll('Cameras').objects.link(o); o.location = loc
        d_ = Vector((tgt[0] - loc[0], tgt[1] - loc[1], 0.0)); o.rotation_euler = d_.to_track_quat('-Z', 'Y').to_euler(); sc.camera = o
    BO_ = D['booths']; b4 = BO_[3]; b5 = BO_[4]
    VIEWS = [('01_street_facade', (27.0, 21.0, 0.45), (12.0, 20.5), 21, 0.18, [], -0.6),
             ('02_entrance_pishtaq', (17.6, 12.6, 0.4), (9.0, 17.4), 20, 0.12, [], -0.4),
             ('03_corridor_teleport', (10.35, 16.8, 1.0), (6.0, 16.8), 17, 0.08, [], -0.1),
             ('04_plaza_mangal', (5.6, 15.4, 1.55), (11.4, 7.0), 18, 0.14, [], -0.1),
             ('05_south_dome', (8.9, 9.6, 1.05), (4.8, 13.6), 15, 0.3, [], -0.1),
             ('06_booth_alley', (6.7, 17.6, 1.2), (8.2, 27.0), 19, 0.1, [], -0.1),
             ('07_booth_sea_view', (b4[2] - 0.45, (b4[0] + b4[1]) / 2 + 0.25, 0.75), (b4[3] + 4.0, (b4[0] + b4[1]) / 2), 17, 0.08, [], -0.1),
             ('08_booth_front', (BO_[2][2] - 2.2, BO_[2][0] + 0.7, 1.25), (BO_[2][2] + 0.9, BO_[2][0] + 1.1), 19, 0.08, [], -0.1),
             ('09_aivan', (3.1, 15.9, 1.2), (1.2, 23.5), 18, 0.12, [], -0.1),
             ('10_central_dome', (8.3, 18.6, 1.05), (4.6, 21.2), 15, 0.32, [], -0.1),
             ('11_fountain_court', (8.1, 27.2, 1.35), (4.6, 33.0), 18, 0.08, [], -0.1),
             ('12_bukhara_dome', (5.0, 30.6, 1.35), (6.1, 35.3), 19, 0.06, [], -0.1),
             ('13_tents_tapchan', (7.3, 30.1, 1.3), (2.8, 34.2), 17, 0.04, [], -0.1),
             ('14_khiva_gate', (6.9, 40.8, 0.9), (6.1, 33.0), 20, 0.12, [], -0.5),
             ('15_aerial_street', (40.0, 6.0, 20.0), (7.0, 20.0), 26, 0.0, [], -0.7),
             ('16_aerial_sea', (104.0, -2.0, 16.0), (8.0, 21.0), 40, 0.0, [], -0.9),
             ('17_khiva_arcade', (6.2, 23.4, 1.0), (3.2, 19.6), 18, 0.12, [], -0.1),
             ('18_dining_chairs', (5.3, 4.5, 0.75), (2.5, 7.5), 22, 0.06, [], -0.1),
             ('19_bar', (4.3, 14.6, 0.85), (0.6, 10.6), 20, 0.1, [], -0.1)]
    only = os.environ.get('VIEWS')
    for name, loc, tgt, lens, shift, hide, ev in VIEWS:
        if only and not any(name.startswith(v) for v in only.split(',')): continue
        sc.view_settings.exposure = ev
        for cn, c in COLS.items(): c.hide_render = cn in hide
        if name.startswith(('15', '16')):
            bl2.camera(loc, (tgt[0], tgt[1], 0.0), lens=lens)
        else: cam2p(loc, tgt, lens, shift)
        bl.render(os.path.join(OUTD, f'samarkand-R12-{name}.png'), W, H, S)

# ======================= EXPORT (flat colours) =======================
export_prep(); flatten_materials()
try: bpy.ops.export_scene.gltf(filepath=base + '.glb', export_format='GLB', export_apply=True, export_yup=True, export_image_format='JPEG', export_image_quality=78)
except TypeError: bpy.ops.export_scene.gltf(filepath=base + '.glb', export_format='GLB', export_apply=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=base + '.fbx', apply_unit_scale=True, axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE')
bpy.ops.wm.obj_export(filepath=base + '.obj', forward_axis='NEGATIVE_Z', up_axis='Y', export_materials=True)
print('saved', base, len(bpy.data.objects), 'objects')

