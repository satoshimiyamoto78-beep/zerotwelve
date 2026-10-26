"""Samarkand R12 — DETAIL PASS (LOD 300) on top of base3d_r12.py. Executed inside base3d's namespace (exec), so it uses
D, m, TER, SID, top, xb, bbox, cen, on_plat, new_obj, boxes, cylinder from there.
Adds: themed booths (carved partitions, epoch panels, pointed-arch portals, tied-back curtains, ceiling caps, cushions),
aivan cushions + wall carpets, flying carpets under the roof, carved chairs, table runners + tableware, majlis tents,
tapchan balusters + dastarkhan, corridor arches + museum niches, copper tandoor + firewood wall + hood, lotus hauz,
majolica aryk, Bukhara dome lattice + vitrines, Khiva gate bells + capitals, brass lanterns, street pishtaq arch,
textured domes, kids chests, tree uplights.
All geometry is batched by zone into a few meshes (bmesh), with UVs where a texture is one picture (carpets, panels)."""
import os, math, random
TEX2 = os.path.join(os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.', 'tex2')
RD = random.Random(42)

# ---------------- materials ----------------
def tex2(name, file, size, rough=0.6, bump=0.25, coat=0.0):
    return bl2.tile(name, os.path.join(TEX2, file), size, rough=rough, bump=bump, coat=coat)
def uvmat(name, file, rough=0.8, sheen=0.5, emit=0.0):
    """image mapped by the mesh UVs (one picture per face: carpets, panels)"""
    if name in bl._mats: return bl._mats[name]
    mm = bpy.data.materials.new(name); mm.use_nodes = True; N = mm.node_tree.nodes; Lk = mm.node_tree.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    b.inputs['Sheen Weight'].default_value = sheen
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(TEX2, file), check_existing=True)
    uv = N.new('ShaderNodeUVMap'); uv.uv_map = 'UVMap'; Lk.new(uv.outputs['UV'], it.inputs['Vector']); Lk.new(it.outputs['Color'], b.inputs['Base Color'])
    if emit:
        Lk.new(it.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    bl._mats[name] = mm; return mm
X = dict(
    carved=tex2('carved_t', 'carved.png', 0.9, rough=0.55, bump=0.5),
    kilim=bl2.fabric('kilim_f', os.path.join(TEX2, 'kilim.png'), 0.6),
    velvet=bl2.fabric('velvet_f', os.path.join(TEX2, 'velvet.png'), 0.8),
    tent=bl2.fabric('tent_f', os.path.join(TEX2, 'tentstripe.png'), 1.2),
    copper=tex2('copper_t', 'copper.png', 0.5, rough=0.3, bump=0.4),
    gajbrick=tex2('gajbrick_t', 'gajbrick.png', 1.4, rough=0.85, bump=0.6),
    dometile=tex2('dometile_t', 'dometile.png', 0.7, rough=0.55, bump=0.5),
    rope=mat('rope', (0.55, 0.42, 0.25), rough=0.9),
    lotus=mat('lotus', (0.16, 0.42, 0.14), rough=0.5), pinkfl=mat('pinkfl', (0.95, 0.55, 0.65), rough=0.5),
    meat=mat('meat', (0.42, 0.16, 0.08), rough=0.6), ember=mat('ember', (1, .3, .05), emit=(1.0, 0.28, 0.04), strength=6.0),
    lampglow=mat('lampglow', (1, .75, .45), emit=(1.0, 0.62, 0.30), strength=8.0),
    cream=mat('cream', (0.90, 0.84, 0.72), rough=0.7),
)
for k in ('carpet1', 'carpet2', 'carpet3', 'carpet4'): X[k] = uvmat(k + '_uv', k + '.png')
for th in ('sogd', 'sasan', 'saman', 'khorezm', 'timur', 'shahr', 'margil', 'pamir'): X['ep_' + th] = uvmat('ep_' + th + '_uv', 'ep_' + th + '.png', rough=0.5, sheen=0.1)

# ---------------- batch mesh builder ----------------
class Batch:
    def __init__(s, name, cname):
        s.name, s.cname = name, cname; s.bm = bmesh.new(); s.uv = s.bm.loops.layers.uv.new('UVMap'); s.mats = []
    def mi(s, mm):
        if mm not in s.mats: s.mats.append(mm)
        return s.mats.index(mm)
    def face(s, pts, mm, uvs=None):
        vs = [s.bm.verts.new(p) for p in pts]
        try: f = s.bm.faces.new(vs)
        except ValueError: return None
        f.material_index = s.mi(mm)
        if uvs:
            for lp, uv in zip(f.loops, uvs): lp[s.uv].uv = uv
        return f
    def prism(s, pts, z0, z1, mm):
        i = s.mi(mm); a = [s.bm.verts.new((x, y, z0)) for x, y in pts]; b = [s.bm.verts.new((x, y, z1)) for x, y in pts]
        fs = [s.bm.faces.new(list(reversed(a))), s.bm.faces.new(b)]; n = len(pts)
        fs += [s.bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])) for k in range(n)]
        for f in fs: f.material_index = i
    def box(s, x0, y0, z0, x1, y1, z1, mm):
        s.prism([(min(x0, x1), min(y0, y1)), (max(x0, x1), min(y0, y1)), (max(x0, x1), max(y0, y1)), (min(x0, x1), max(y0, y1))], min(z0, z1), max(z0, z1), mm)
    def extrude_yz(s, pts, x0, x1, mm):
        """polygon in the YZ plane (y, z) extruded along x"""
        i = s.mi(mm); a = [s.bm.verts.new((x0, y, z)) for y, z in pts]; b = [s.bm.verts.new((x1, y, z)) for y, z in pts]
        fs = [s.bm.faces.new(list(reversed(a))), s.bm.faces.new(b)]; n = len(pts)
        fs += [s.bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])) for k in range(n)]
        for f in fs: f.material_index = i
    def extrude_xz(s, pts, y0, y1, mm):
        i = s.mi(mm); a = [s.bm.verts.new((x, y0, z)) for x, z in pts]; b = [s.bm.verts.new((x, y1, z)) for x, z in pts]
        fs = [s.bm.faces.new(list(reversed(a))), s.bm.faces.new(b)]; n = len(pts)
        fs += [s.bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])) for k in range(n)]
        for f in fs: f.material_index = i
    def lathe(s, x, y, z, prof, mm, n=20):
        i = s.mi(mm); rings = [[s.bm.verts.new((x + r * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n), z + h)) for k in range(n)] for r, h in prof]
        for ra, rb in zip(rings[:-1], rings[1:]):
            for k in range(n):
                try: s.bm.faces.new((ra[k], ra[(k + 1) % n], rb[(k + 1) % n], rb[k])).material_index = i
                except ValueError: pass
    def cyl(s, x, y, z0, z1, r, mm, n=12, r2=None):
        s.lathe(x, y, z0, [(0.0, 0.0), (r, 0.0), (r if r2 is None else r2, z1 - z0), (0.0, z1 - z0)], mm, n)
    def rod(s, p, q, r, mm, n=6):
        """cylinder between two 3D points"""
        p, q = Vector(p), Vector(q); d = q - p; L = d.length
        if L < 1e-6: return
        u = d.normalized(); t = u.orthogonal().normalized(); w = u.cross(t)
        i = s.mi(mm); ra = [s.bm.verts.new(p + (t * math.cos(2 * math.pi * k / n) + w * math.sin(2 * math.pi * k / n)) * r) for k in range(n)]
        rb = [s.bm.verts.new(v.co + d) for v in ra]
        for k in range(n): s.bm.faces.new((ra[k], ra[(k + 1) % n], rb[(k + 1) % n], rb[k])).material_index = i
    def quad_uv(s, p0, p1, p2, p3, mm, two_sided=True):
        s.face([p0, p1, p2, p3], mm, [(0, 0), (1, 0), (1, 1), (0, 1)])
        if two_sided: s.face([p3, p2, p1, p0], mm, [(0, 1), (1, 1), (1, 0), (0, 0)])
    def done(s):
        if not s.bm.faces: s.bm.free(); return None
        o = new_obj(s.name, s.bm, s.mats, s.cname)
        for p in o.data.polygons: p.use_smooth = False
        return o
from mathutils import Vector

def arch_curve(c, w, zs, za, n=10):
    """left half of a pointed arch in (u, z): from the left spring up to the apex"""
    h = w / 2; pts = []
    for i in range(n + 1):
        t = i / n; p0 = (c - h, zs); p1 = (c - h, zs + (za - zs) * 0.62); p2 = (c, za)
        pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return pts
def spandrels(c, w, zs, za, ztop, wout):
    """two spandrel polygons (u, z) of a portal head between the posts (opening w, outer width wout)"""
    L = arch_curve(c, w, zs, za); R_ = [(2 * c - u, z) for u, z in L]
    left = [(c - wout / 2, zs)] + L + [(c, ztop), (c - wout / 2, ztop)]
    right = [(c + wout / 2, ztop), (c, ztop)] + list(reversed(R_)) + [(c + wout / 2, zs)]
    return left, right[::-1]

def lantern(bt, x, y, z, s=1.0, rod_top=None):
    h, r = 0.34 * s, 0.15 * s
    bt.cyl(x, y, z - h / 2, z + h / 2, r * 0.9, X['lampglow'], n=10)
    for k in range(8):
        a = 2 * math.pi * k / 8; bt.box(x + r * math.cos(a) - 0.008, y + r * math.sin(a) - 0.008, z - h / 2, x + r * math.cos(a) + 0.008, y + r * math.sin(a) + 0.008, z + h / 2, m['brass'])
    bt.lathe(x, y, z + h / 2, [(0, 0), (r * 1.05, 0), (r * 0.7, 0.08 * s), (r * 0.25, 0.16 * s), (0.015, 0.22 * s), (0, 0.22 * s)], m['brass'], 12)
    bt.lathe(x, y, z - h / 2, [(0, 0), (r, 0), (r * 0.5, -0.07 * s), (0, -0.12 * s)], m['brass'], 12)
    if rod_top and rod_top > z + h / 2 + 0.25 * s: bt.cyl(x, y, z + h / 2 + 0.22 * s, rod_top, 0.006, m['brass'], n=5)

def tableware(bt, x, y, z, seats, along='x', L=1.4, runner=True, teapot=True):
    """plates + pialas per seat, a suzani runner and a lapis teapot"""
    if runner:
        if along == 'x': bt.quad_uv((x - L / 2 + 0.05, y - 0.17, z + 0.003), (x + L / 2 - 0.05, y - 0.17, z + 0.003), (x + L / 2 - 0.05, y + 0.17, z + 0.003), (x - L / 2 + 0.05, y + 0.17, z + 0.003), X['carpet2'], False)
        else: bt.quad_uv((x - 0.17, y - L / 2 + 0.05, z + 0.003), (x + 0.17, y - L / 2 + 0.05, z + 0.003), (x + 0.17, y + L / 2 - 0.05, z + 0.003), (x - 0.17, y + L / 2 - 0.05, z + 0.003), X['carpet2'], False)
    for px, py in seats:
        bt.lathe(px, py, z, [(0, 0), (0.07, 0), (0.12, 0.012), (0.13, 0.022), (0, 0.012)], m['ceramic'], 16)
        bt.lathe(px + 0.12 * (1 if along == 'x' else 0) + 0.0, py + (0 if along == 'x' else 0.12), z, [(0, 0), (0.022, 0), (0.045, 0.045), (0.0, 0.045)], m['turq'], 10)
    if teapot:
        bt.lathe(x, y, z, [(0, 0), (0.05, 0), (0.08, 0.05), (0.075, 0.1), (0.04, 0.125), (0.02, 0.14), (0, 0.145)], m['lapis'], 14)
        bt.rod((x + 0.07, y, z + 0.06), (x + 0.14, y, z + 0.12), 0.01, m['lapis'])

# =============== 1. THEMED BOOTHS ===============
bt = Batch('booth_detail', 'Booths'); bl_ = Batch('booth_lanterns', 'Lights'); bset = Batch('booth_tableware', 'Furniture')
for k, (y0, y1, xw, xe, th) in enumerate(D['booths']):
    zt = TER + 2.2
    walls = [y0] + ([y1] if k == len(D['booths']) - 1 else [])
    for yw in walls:                                         # carved partition: frame + carved infill
        bt.box(xw, yw, TER, xe, yw + 0.06, TER + 0.1, m['walnut'])
        bt.box(xw + 0.04, yw + 0.01, TER + 0.1, xe - 0.04, yw + 0.05, zt - 0.08, X['carved'])
        bt.box(xw, yw - 0.01, zt - 0.08, xe, yw + 0.07, zt, m['walnut'])
        for xx in (xw, xe - 0.06): bt.box(xx, yw - 0.01, TER, xx + 0.06, yw + 0.07, zt, m['walnut'])
    # epoch panel on the back wall (street side) + kilim wainscot
    bt.quad_uv((xe - 0.04, y1 - 0.1, TER + 0.62), (xe - 0.04, y0 + 0.16, TER + 0.62), (xe - 0.04, y0 + 0.16, zt - 0.12), (xe - 0.04, y1 - 0.1, zt - 0.12), X['ep_' + th], False)
    bt.box(xe - 0.035, y0 + 0.06, TER + 0.6, xe, y1, zt - 0.1, m['brass'])
    bt.box(xe - 0.06, y0 + 0.06, TER, xe, y1, TER + 0.6, X['kilim'])
    # ceiling cap (velvet) with a brass rim
    bt.box(xw - 0.06, y0, zt, xe, y1, zt + 0.05, X['velvet']); bt.box(xw - 0.08, y0, zt - 0.06, xw - 0.04, y1, zt + 0.05, m['brass'])
    # portal head: pointed arch between the posts, carved spandrels
    c = (y0 + y1) / 2; wo = (y1 - y0); wi = wo - 0.44
    for poly in spandrels(c, wi, TER + 1.8, TER + 2.12, zt, wo): bt.extrude_yz(poly, xw - 0.07, xw - 0.01, X['carved'])
    for yy in (y0, y1 - 0.22): bt.box(xw - 0.07, yy, TER, xw - 0.01, yy + 0.22, zt, m['walnut'])
    # tied-back curtains (velvet), each a gathered sheet: top at the arch spring, tie at 1.0 m, flared to the floor
    for side in (-1, 1):
        ya = y0 + 0.22 if side < 0 else y1 - 0.22; s = 1 if side < 0 else -1
        top_ = [(ya, TER + 1.95), (ya + s * 0.42, TER + 1.95)]; tie = (ya + s * 0.06, TER + 1.0); bot = [(ya, TER + 0.02), (ya + s * 0.2, TER + 0.02)]
        rows = [top_, [(ya, TER + 1.45), (ya + s * 0.2, TER + 1.45)], [tie, (tie[0] + s * 0.05, tie[1])], [(ya, TER + 0.5), (ya + s * 0.12, TER + 0.5)], bot]
        for ra, rb in zip(rows[:-1], rows[1:]):
            for j in range(6):
                t0, t1 = j / 6, (j + 1) / 6
                def P(row, t, z_off=0.0):
                    (u0, z0), (u1, z1) = row; u = u0 + (u1 - u0) * t; z = z0 + (z1 - z0) * t
                    return (xw - 0.12 - 0.05 * math.sin(t * math.pi * 3), u, z)
                bt.face([P(ra, t0), P(ra, t1), P(rb, t1), P(rb, t0)], X['velvet'])
                bt.face([P(rb, t0), P(rb, t1), P(ra, t1), P(ra, t0)], X['velvet'])
        bt.cyl(xw - 0.13, tie[0], tie[1] - 0.03, tie[1] + 0.03, 0.05, m['brass'], n=8)
    # cushions: backrests along the partitions + seat pads
    for yb, yc in ((y0 + 0.06, y0 + 0.2), (y1 - 0.2, y1 - 0.06)):
        bt.box(xw + 0.1, yb, TER + 0.47, xe - 0.1, yc, TER + 0.92, X['kilim'])
    for yb, yc in ((y0 + 0.12, y0 + 0.58), (y1 - 0.58, y1 - 0.12)): bt.box(xw + 0.1, yb, TER + 0.45, xe - 0.08, yc, TER + 0.52, m['ikat'])
    # plaque on the portal post + lantern under the cap + tableware
    bt.box(xw - 0.075, y0 + 0.04, TER + 1.45, xw - 0.068, y0 + 0.18, TER + 1.62, m['brass'])
    xc = (xw + xe) / 2; lantern(bl_, xc, c, TER + 1.85, 0.9, zt)
    tableware(bset, xc, c, TER + 0.76, [(xc - 0.25, c - 0.25), (xc + 0.25, c - 0.25), (xc - 0.25, c + 0.25), (xc + 0.25, c + 0.25)], along='y', L=0.6, runner=False)
bt.done(); bl_.done(); bset.done()

# =============== 2. AIVAN SEDIR BOOTHS ===============
ba = Batch('aivan_detail', 'Aivan')
abs_ = [it for it in D['items'] if it['kind'] == 'abench']; ats = [cen(it['poly'][0]) for it in D['items'] if it['kind'] == 'atable']
for it in abs_:
    x0, y0, x1, y1 = bbox(it['poly'][0]); cy = (y0 + y1) / 2
    tc = min(ats, key=lambda p: abs(p[1] - cy)); outer_y = y0 if tc[1] > cy else y1; s = 1 if outer_y == y0 else -1
    ba.box(x0 + 0.05, min(outer_y, outer_y + s * 0.14), 0.45, x1 - 0.05, max(outer_y, outer_y + s * 0.14), 0.88, X['kilim'])
for i, (x, y) in enumerate(ats):
    ba.quad_uv((0.09, y - 0.85, 0.75), (0.09, y + 0.85, 0.75), (0.09, y + 0.85, 2.25), (0.09, y - 0.85, 2.25), X['carpet%d' % (1 + i % 4)], False)
    ba.box(0.06, y - 0.9, 2.25, 0.12, y + 0.9, 2.29, m['brass'])
    tableware(ba, x, y, 0.76, [(x - 0.35, y - 0.25), (x + 0.35, y - 0.25), (x - 0.35, y + 0.25), (x + 0.35, y + 0.25)], along='x', L=1.6)
    lantern(ba, x, y, 1.95, 1.0, 3.7)
ba.done()

# =============== 3. FLYING CARPETS under the roof ===============
fc = Batch('flying_carpets', 'Carpet_ceiling')
ZONES = [(2.6, 8.6, 5.3, 9.3), (8.0, 11.0, 10.4, 14.6), (3.6, 7.8, 22.9, 24.8), (4.4, 7.6, 30.2, 34.0), (1.7, 3.2, 15.6, 28.2)]
def clear_of_domes(x, y, pad=0.5): return all(math.hypot(x - d['c'][0], y - d['c'][1]) > d['r'] + pad for d in D['domes'])
n_c = 0
for zx0, zx1, zy0, zy1 in ZONES:
    y = zy0 + 1.1
    while y < zy1 - 0.9:
        x = zx0 + 0.75
        while x < zx1 - 0.6:
            if clear_of_domes(x, y, 0.9):
                w, l = 1.25, 1.9; tilt = math.radians(RD.uniform(-10, 10)); zc = top(x) - 0.75 + RD.uniform(-0.08, 0.05); rot = RD.choice((0, math.pi / 2)) if zx1 - zx0 > 2 else 0
                c_, s_ = math.cos(rot), math.sin(rot)
                def Pp(u, v):
                    return (x + u * c_ - v * s_, y + u * s_ + v * c_, zc + u * math.sin(tilt) + 0.06 * math.sin(v / l * math.pi * 2))
                pts = [Pp(-w / 2, -l / 2), Pp(w / 2, -l / 2), Pp(w / 2, l / 2), Pp(-w / 2, l / 2)]
                # gentle wave: split along the length in 6 strips
                for j in range(6):
                    v0, v1 = -l / 2 + l * j / 6, -l / 2 + l * (j + 1) / 6
                    a0, a1, b0, b1 = Pp(-w / 2, v0), Pp(w / 2, v0), Pp(w / 2, v1), Pp(-w / 2, v1)
                    uv = [(0, j / 6), (1, j / 6), (1, (j + 1) / 6), (0, (j + 1) / 6)]
                    fc.face([a0, a1, b1, b0], X['carpet%d' % (1 + n_c % 4)], uv); fc.face([b0, b1, a1, a0], X['carpet%d' % (1 + n_c % 4)], uv[::-1])
                for corner in pts: fc.rod(corner, (corner[0], corner[1], top(corner[0]) - 0.3), 0.005, X['rope'], 4)
                n_c += 1
            x += 1.75
        y += 2.35
fc.done()
print('flying carpets', n_c)

# =============== 4. CARVED CHAIRS + TABLE SETTINGS ===============
ch = Batch('chairs_carved', 'Furniture'); tw = Batch('tables_tableware', 'Furniture')
for it in D['items']:
    if it['kind'] == 'chair':
        for r in it['poly']:
            base = 0.0 if on_plat(r) else TER; x0, y0, x1, y1 = bbox(r); bk = it.get('back', 'n')
            for lx, ly in ((x0 + .05, y0 + .05), (x1 - .05, y0 + .05), (x0 + .05, y1 - .05), (x1 - .05, y1 - .05)): ch.cyl(lx, ly, base, base + 0.43, 0.018, m['walnut'], n=6)
            ch.box(x0 + .03, y0 + .03, base + 0.40, x1 - .03, y1 - .03, base + 0.44, m['walnut'])
            ch.box(x0 + .05, y0 + .05, base + 0.44, x1 - .05, y1 - .05, base + 0.5, m['ikat'])
            # back: two posts, carved panel, pointed crest
            if bk in ('n', 's'):
                yb = y1 - 0.04 if bk == 'n' else y0
                for xx in (x0 + 0.03, x1 - 0.07): ch.box(xx, yb, base + 0.44, xx + 0.04, yb + 0.04, base + 0.92, m['walnut'])
                ch.box(x0 + 0.07, yb + 0.01, base + 0.58, x1 - 0.07, yb + 0.03, base + 0.86, X['carved'])
                ch.extrude_xz([(x0 + 0.03, base + 0.88), (x1 - 0.03, base + 0.88), (x1 - 0.03, base + 0.92), ((x0 + x1) / 2, base + 1.0), (x0 + 0.03, base + 0.92)], yb, yb + 0.04, m['walnut'])
            else:
                xb_ = x1 - 0.04 if bk == 'e' else x0
                for yy in (y0 + 0.03, y1 - 0.07): ch.box(xb_, yy, base + 0.44, xb_ + 0.04, yy + 0.04, base + 0.92, m['walnut'])
                ch.box(xb_ + 0.01, y0 + 0.07, base + 0.58, xb_ + 0.03, y1 - 0.07, base + 0.86, X['carved'])
                ch.extrude_yz([(y0 + 0.03, base + 0.88), (y1 - 0.03, base + 0.88), (y1 - 0.03, base + 0.92), ((y0 + y1) / 2, base + 1.0), (y0 + 0.03, base + 0.92)], xb_, xb_ + 0.04, m['walnut'])
    if it['kind'] == 'table':
        for r in it['poly']:
            base = 0.0 if on_plat(r) else TER; x0, y0, x1, y1 = bbox(r); n = it.get('mods', 1); ax = it.get('axis', 'x')
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; seats = []
            for j in range(n):
                if ax == 'x': sx = x0 + (j + .5) * (x1 - x0) / n; seats += [(sx, y0 + 0.17), (sx, y1 - 0.17)]
                else: sy = y0 + (j + .5) * (y1 - y0) / n; seats += [(x0 + 0.17, sy), (x1 - 0.17, sy)]
            tableware(tw, cx, cy, base + 0.76, seats, along=ax, L=max(x1 - x0, y1 - y0), teapot=n >= 2)
ch.done(); tw.done()

# =============== 5. MAJLIS TENTS ===============
te = Batch('majlis_tents', 'Tapchans_tent')
for tx0, ty0, tx1, ty1 in D.get('tents', [D['tent']]):
    a0, b0, a1, b1 = tx0 - 0.05, ty0 - 0.05, tx1 + 0.05, ty1 + 0.05; zw = TER + 2.25; ap = TER + 3.0
    for px, py in ((a0, b0), (a1, b0), (a0, b1), (a1, b1)):
        te.cyl(px, py, TER, zw + 0.15, 0.05, m['walnut'], n=8); te.lathe(px, py, zw + 0.15, [(0, 0), (0.07, 0), (0.05, 0.08), (0.02, 0.16), (0, 0.2)], m['brass'], 8)
    te.box(a0, b0, TER, a0 + 0.03, b1, zw, X['tent'])                                          # back wall (ramp side)
    te.box(a0, b0, TER, a1, b0 + 0.03, zw, X['tent']); te.box(a0, b1 - 0.03, TER, a1, b1, zw, X['tent'])
    # pyramid roof (stripes) + scalloped velvet valance
    ce = ((a0 + a1) / 2, (b0 + b1) / 2, ap); cs = [(a0 - 0.08, b0 - 0.08, zw), (a1 + 0.08, b0 - 0.08, zw), (a1 + 0.08, b1 + 0.08, zw), (a0 - 0.08, b1 + 0.08, zw)]
    for i in range(4): te.face([cs[i], cs[(i + 1) % 4], ce], X['tent']); te.face([ce, cs[(i + 1) % 4], cs[i]], X['tent'])
    for i in range(4):
        p, q = cs[i], cs[(i + 1) % 4]; L = math.dist(p[:2], q[:2]); nsc = max(4, int(L / 0.3))
        for j in range(nsc):
            t0, t1, tm = j / nsc, (j + 1) / nsc, (j + .5) / nsc
            A = (p[0] + (q[0] - p[0]) * t0, p[1] + (q[1] - p[1]) * t0, zw); Bq = (p[0] + (q[0] - p[0]) * t1, p[1] + (q[1] - p[1]) * t1, zw)
            Cq = (p[0] + (q[0] - p[0]) * tm, p[1] + (q[1] - p[1]) * tm, zw - 0.22)
            te.face([A, Bq, (Bq[0], Bq[1], zw - 0.1), Cq, (A[0], A[1], zw - 0.1)], X['velvet']); te.face([(A[0], A[1], zw - 0.1), Cq, (Bq[0], Bq[1], zw - 0.1), Bq, A], X['velvet'])
    # tied-back front curtains (east side)
    for yy, s in ((b0 + 0.05, 1), (b1 - 0.05, -1)):
        te.face([(a1, yy, zw - 0.1), (a1, yy + s * 0.55, zw - 0.1), (a1 + 0.05, yy + s * 0.1, TER + 1.0), (a1 + 0.05, yy, TER + 1.0)], X['tent'])
        te.face([(a1 + 0.05, yy, TER + 1.0), (a1 + 0.05, yy + s * 0.1, TER + 1.0), (a1, yy + s * 0.25, TER), (a1, yy, TER)], X['tent'])
    # sofa back cushions (kilim) + brass trays + 2 hanging lanterns
    te.box(tx0 + 0.04, ty0 + 0.1, TER + 0.42, tx0 + 0.18, ty1 - 0.1, TER + 0.85, X['kilim'])
    for yy in (ty0 + 0.04, ty1 - 0.18): te.box(tx0 + 0.65, yy, TER + 0.42, tx1 - 0.3, yy + 0.14, TER + 0.85, X['kilim'])
    for it in D['items']:
        if it['kind'] == 'otable':
            ox, oy = cen(it['poly'][0])
            if tx0 <= ox <= tx1 and ty0 <= oy <= ty1:
                te.cyl(ox, oy, TER + 0.45, TER + 0.47, 0.33, m['brass'], n=16); tableware(te, ox, oy, TER + 0.47, [(ox - 0.15, oy), (ox + 0.15, oy)], runner=False)
    for yy in (ty0 + 0.9, ty1 - 0.9): lantern(te, (tx0 + tx1) / 2 + 0.2, yy, TER + 1.95, 0.9, ap - 0.3)
te.done()

# =============== 6. TAPCHAN ===============
tp = Batch('tapchan_detail', 'Tapchans_tent')
for y0 in D['tap']:
    x0, x1, y1 = 2.55, 4.55, y0 + 2.2
    for t in [i / 10 for i in range(11)]:
        tp.cyl(x0 + (x1 - x0) * t, y0 + 0.025, TER + 0.45, TER + 0.75, 0.018, m['walnut'], n=6); tp.cyl(x0 + (x1 - x0) * t, y1 - 0.025, TER + 0.45, TER + 0.75, 0.018, m['walnut'], n=6)
    for t in [i / 11 for i in range(12)]: tp.cyl(x0 + 0.025, y0 + (y1 - y0) * t, TER + 0.45, TER + 0.75, 0.018, m['walnut'], n=6)
    for px, py in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)): tp.lathe(px, py, TER + 0.75, [(0, 0), (0.05, 0), (0.04, 0.06), (0.015, 0.12), (0, 0.14)], m['brass'], 8)
    tp.rod((x0 + 0.25, y0 + 0.25, TER + 0.66), (x0 + 0.25, y1 - 0.25, TER + 0.66), 0.09, m['ikat'], 10)           # bolster
    tp.quad_uv((3.25, y0 + 0.65, TER + 0.785), (4.35, y0 + 0.65, TER + 0.785), (4.35, y0 + 1.55, TER + 0.785), (3.25, y0 + 1.55, TER + 0.785), X['carpet3'], False)
    tableware(tp, 3.8, y0 + 1.1, TER + 0.79, [(3.5, y0 + 0.85), (3.5, y0 + 1.35), (4.1, y0 + 0.85), (4.1, y0 + 1.35)], runner=False)
    tp.lathe(3.8, y0 + 1.1, TER + 0.79, [(0, 0), (0.12, 0), (0.22, 0.03), (0.24, 0.05), (0, 0.03)], m['majolica'], 20)       # lagan with plov
tp.done()

# =============== 7. CORRIDOR: arches + museum niches ===============
co = Batch('corridor_detail', 'Corridor')
e0, e1 = D['ent']; t0, t1 = D['tun']; cy_ = (e0 + e1) / 2; W_ = e1 - e0
for x in [t0 + 0.2 + 0.9 * i for i in range(int((t1 - t0) / 0.9) + 1)]:
    for poly in spandrels(cy_, W_ - 0.3, TER + 2.0, TER + 2.62, TER + 2.75, W_ + 0.1): co.extrude_yz(poly, x, x + 0.08, X['velvet'])
    for yy in (e0 + 0.05, e1 - 0.15): co.box(x, yy, TER, x + 0.08, yy + 0.1, TER + 2.75, m['walnut'])
for i in range(int((t1 - t0) / 0.9)):                                  # sagging velvet ceiling between the arches
    xa, xb2 = t0 + 0.28 + 0.9 * i, t0 + 0.28 + 0.9 * (i + 1) - 0.08
    if xb2 > t1: break
    for j in range(8):
        ya, yb2 = e0 + 0.1 + (W_ - 0.2) * j / 8, e0 + 0.1 + (W_ - 0.2) * (j + 1) / 8
        za = TER + 2.72 - 0.28 * math.sin(math.pi * (j) / 8); zb = TER + 2.72 - 0.28 * math.sin(math.pi * (j + 1) / 8)
        for xx0, xx1, sag in ((xa, (xa + xb2) / 2, 0.0), ((xa + xb2) / 2, xb2, 0.0)):
            dz0 = -0.12 if xx0 != xa else 0.0; dz1 = -0.12 if xx1 != xb2 else 0.0
            co.face([(xx0, ya, za + dz0), (xx1, ya, za + dz1), (xx1, yb2, zb + dz1), (xx0, yb2, zb + dz0)], X['velvet'])
for side, yw in ((1, e0 + 0.09), (-1, e1 - 0.09)):
    for x in (t0 + 0.65, t0 + 1.55, t0 + 2.45):
        if x + 0.3 > t1: continue
        y_in = yw + side * 0.26
        co.box(x - 0.3, min(yw, y_in), TER + 0.9, x + 0.3, max(yw, y_in), TER + 0.95, m['walnut'])
        co.box(x - 0.3, min(yw, y_in), TER + 1.75, x + 0.3, max(yw, y_in), TER + 1.8, m['walnut'])
        for xx in (x - 0.3, x + 0.26): co.box(xx, min(yw, y_in), TER + 0.9, xx + 0.04, max(yw, y_in), TER + 1.8, m['walnut'])
        co.box(x - 0.26, yw - side * 0.0, TER + 0.95, x + 0.26, yw + side * 0.02, TER + 1.75, X['velvet'])
        co.box(x - 0.26, min(yw, y_in), TER + 1.74, x + 0.26, max(yw, y_in), TER + 1.75, X['lampglow'])
        mid = (yw + y_in) / 2
        co.lathe(x - 0.12, mid, TER + 0.95, [(0, 0), (0.05, 0), (0.09, 0.12), (0.06, 0.26), (0.03, 0.3), (0.045, 0.34), (0, 0.34)], m['clay'], 14)
        co.lathe(x + 0.1, mid, TER + 0.95, [(0, 0), (0.04, 0), (0.07, 0.08), (0.05, 0.2), (0.025, 0.24), (0, 0.25)], m['turq'], 14)
        co.box(x - 0.18, min(yw, y_in), TER + 1.3, x + 0.18, max(yw, y_in), TER + 1.32, m['glass'])
        co.box(x - 0.1, mid - 0.01, TER + 0.58, x + 0.1, mid + 0.01, TER + 0.66, m['brass'])          # plaque
for xx, yy in ((t0 + 0.35, e0 + 0.35), (t1 - 0.3, e0 + 0.35), (t0 + 0.35, e1 - 0.35), (t1 - 0.3, e1 - 0.35)):
    co.lathe(xx, yy, TER, [(0, 0), (0.12, 0), (0.24, 0.3), (0.22, 0.6), (0.1, 0.78), (0.13, 0.84), (0, 0.84)], m['clay'], 16)
co.done()

# =============== 8. MANGAL: copper tandoor, firewood wall, hood, skewers ===============
mg = Batch('mangal_detail', 'Mangal'); BX0, BX1, BY0, BY1 = D['bbq']
for it in D['items']:
    if it['kind'] == 'tandoor':
        tx_, ty_ = cen(it['poly'][0])
        mg.lathe(tx_, ty_, TER + 0.85, [(0, 0), (0.46, 0), (0.48, 0.1), (0.44, 0.45), (0.3, 0.62), (0.22, 0.66), (0, 0.66)], X['copper'], 24)
        mg.lathe(tx_, ty_, TER + 1.51, [(0.2, 0), (0.24, 0.02), (0.2, 0.04)], m['brass'], 16)
    if it['kind'] == 'kazan':
        kx, ky = cen(it['poly'][0]); mg.lathe(kx, ky, TER + 0.7, [(0, 0), (0.15, 0), (0.36, 0.18), (0.4, 0.3), (0.42, 0.32)], m['black'], 20)
    if it['kind'] == 'mangal':
        x0, y0, x1, y1 = bbox(it['poly'][0])
        mg.box(x0 + 0.05, y0 + 0.05, TER + 0.8, x1 - 0.05, y1 - 0.05, TER + 0.83, X['ember'])
        for j in range(14):
            yy = y0 + 0.1 + j * (y1 - y0 - 0.2) / 13
            mg.rod((x0 - 0.05, yy, TER + 0.9), (x1 + 0.08, yy, TER + 0.9), 0.004, m['steel'], 4)
            for kk in range(4): mg.box(x0 + 0.08 + kk * 0.1, yy - 0.02, TER + 0.88, x0 + 0.14 + kk * 0.1, yy + 0.02, TER + 0.93, X['meat'])
    if it['kind'] == 'woodstack':
        x0, y0, x1, y1 = bbox(it['poly'][0])
        mg.box(x0, y0, TER, x1, y1, TER + 0.08, m['walnut']); mg.box(x0, y0, TER + 1.95, x1, y1, TER + 2.02, m['walnut'])
        for yy in (y0, y1 - 0.06): mg.box(x0, yy, TER, x1, yy + 0.06, TER + 2.02, m['walnut'])
        zz = TER + 0.14; row = 0
        while zz < TER + 1.9:
            yy = y0 + 0.12 + (0.06 if row % 2 else 0)
            while yy < y1 - 0.1: mg.rod((x0 + 0.02, yy, zz), (x1 - 0.02, yy, zz), 0.055 + 0.01 * RD.random(), m['oak'], 7); yy += 0.125
            zz += 0.108; row += 1
    if it['kind'] == 'hood':
        x0, y0, x1, y1 = bbox(it['poly'][0]); zb = TER + 2.0
        hx, hy = (x0 + x1) / 2, (y0 + y1) / 2
        mg.face([(x0, y0, zb), (x1, y0, zb), (hx + 0.25, hy - 0.4, zb + 0.6), (hx - 0.25, hy - 0.4, zb + 0.6)], m['black'])
        mg.face([(x1, y0, zb), (x1, y1, zb), (hx + 0.25, hy + 0.4, zb + 0.6), (hx + 0.25, hy - 0.4, zb + 0.6)], m['black'])
        mg.face([(x1, y1, zb), (x0, y1, zb), (hx - 0.25, hy + 0.4, zb + 0.6), (hx + 0.25, hy + 0.4, zb + 0.6)], m['black'])
        mg.face([(x0, y1, zb), (x0, y0, zb), (hx - 0.25, hy - 0.4, zb + 0.6), (hx - 0.25, hy + 0.4, zb + 0.6)], m['black'])
        mg.box(x0, y0, zb - 0.12, x1, y1, zb, m['steel']); mg.box(x0 - 0.01, y0 - 0.01, zb - 0.3, x1 + 0.01, y0 + 0.02, zb - 0.12, m['majolica'])
    if it['kind'] == 'pass':
        x0, y0, x1, y1 = bbox(it['poly'][0])
        for xx in [x0 + 0.4 + 0.6 * i for i in range(int((x1 - x0) / 0.6))]: mg.lathe(xx, (y0 + y1) / 2, TER + 1.75, [(0, 0), (0.1, 0), (0.06, 0.12), (0, 0.14)], m['black'], 10); mg.cyl(xx, (y0 + y1) / 2, TER + 1.7, TER + 1.75, 0.07, X['lampglow'], n=10)
mg.box(BX1 - 0.16, BY0, TER + 2.3, BX1, BY1, TER + 2.5, m['majolica'])
mg.done()

# =============== 9. HAUZ lotus + jet, ARYK majolica edges ===============
hz = Batch('hauz_detail', 'Fountain'); hx, hy = D['hzc']
for k in range(7):
    a = k * 0.9 + 0.3; r_ = 0.22 + 0.1 * (k % 3); px, py = hx + r_ * math.cos(a), hy + r_ * math.sin(a)
    hz.cyl(px, py, TER + 0.36, TER + 0.37, 0.07 + 0.02 * (k % 2), X['lotus'], n=10)
    if k % 3 == 0: hz.lathe(px, py, TER + 0.37, [(0, 0), (0.04, 0.0), (0.05, 0.04), (0, 0.05)], X['pinkfl'], 8)
hz.lathe(hx, hy, TER + 0.36, [(0, 0), (0.06, 0), (0.02, 0.5), (0, 0.55)], m['glass'], 10)
for it in D['items']:
    if it['kind'] == 'aryk':
        x0, y0, x1, y1 = bbox(it['poly'][0])
        for xx in (x0 - 0.08, x1): hz.box(xx, y0, TER - 0.02, xx + 0.08, y1, TER + 0.06, m['majolica'])
hz.done()

# =============== 10. BUKHARA DOME: lattice drum, vitrines, cap ===============
bk = Batch('bukhara_dome_detail', 'Bukhara_dome')
if 'rot' in D:
    rx, ry, rr_ = D['rot']; z0 = TER + 0.15
    for k in range(20):
        a = 2 * math.pi * k / 20; bk.box(rx + 0.45 * math.cos(a) - 0.02, ry + 0.45 * math.sin(a) - 0.02, z0, rx + 0.45 * math.cos(a) + 0.02, ry + 0.45 * math.sin(a) + 0.02, TER + 2.3, m['walnut'])
    for zz in (z0 + 0.05, TER + 0.9, TER + 1.6, TER + 2.25): bk.lathe(rx, ry, zz, [(0.43, 0), (0.49, 0), (0.49, 0.05), (0.43, 0.05), (0.43, 0)], m['brass'], 28)
    for zz in (TER + 0.9, TER + 1.6):
        for k in range(10):
            a = 2 * math.pi * k / 10 + 0.3; px, py = rx + 0.3 * math.cos(a), ry + 0.3 * math.sin(a)
            bk.lathe(px, py, zz + 0.05, [(0, 0), (0.04, 0), (0.065, 0.1), (0.04, 0.2), (0.025, 0.24), (0, 0.24)], [m['clay'], m['turq'], m['majolica'], m['lapis']][k % 4], 10)
    bk.lathe(rx, ry, TER + 2.3, [(0, 0), (0.55, 0), (0.52, 0.12), (0.4, 0.3), (0.2, 0.42), (0.05, 0.47), (0.05, 0.6), (0, 0.62)], X['copper'], 28)
    for it in D['items']:
        if it['kind'] == 'rbox':
            x0, y0, x1, y1 = bbox(it['poly'][0])
            bk.box(x0, y0, z0, x1, y1, TER + 0.55, m['walnut']); bk.box(x0 + 0.02, y0 + 0.02, TER + 0.55, x1 - 0.02, y1 - 0.02, TER + 1.05, m['glass'])
            for xx, yy in ((x0, y0), (x1 - 0.025, y0), (x0, y1 - 0.025), (x1 - 0.025, y1 - 0.025)): bk.box(xx, yy, TER + 0.55, xx + 0.025, yy + 0.025, TER + 1.07, m['brass'])
            bk.box(x0, y0, TER + 1.05, x1, y1, TER + 1.08, m['brass'])
            cx_, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
            bk.lathe(cx_, cy_, TER + 0.56, [(0, 0), (0.06, 0), (0.1, 0.12), (0.06, 0.24), (0.02, 0.3), (0, 0.3)], m['majolica'], 12)
            bk.box(cx_ - 0.12, cy_ - 0.12, TER + 0.56, cx_ + 0.12, cy_ + 0.12, TER + 0.57, X['lampglow'])
    g0, g1 = D['gate']
    for gx in (g0 - 0.125, g1 + 0.125):                                                   # gate capitals + carved post faces
        bk.lathe(gx, 36.425, TER + 2.55, [(0, 0), (0.16, 0), (0.22, 0.12), (0.22, 0.2), (0, 0.2)], m['brass'], 12)
        bk.box(gx - 0.13, 36.29, TER + 0.3, gx + 0.13, 36.31, TER + 2.4, X['carved'])
    for k in range(7):                                                                     # bells
        gx = g0 + (g1 - g0) * (k + 1) / 8; bk.cyl(gx, 36.425, TER + 2.45, TER + 2.85, 0.004, m['brass'], n=4)
        bk.lathe(gx, 36.425, TER + 2.3, [(0, 0), (0.06, 0), (0.05, 0.08), (0.02, 0.15), (0, 0.15)], m['brass'], 10)
bk.done()

# =============== 11. BRASS LANTERNS (all lantern points from the plan) ===============
ln_ = Batch('lanterns_brass', 'Lights')
for it in D['items']:
    if it['kind'] == 'lantern':
        for r in it['poly']:
            cx, cy = cen(r); base = 0.0 if on_plat(r) else TER
            if any(y0 <= cy <= y1 and xw <= cx <= xe for y0, y1, xw, xe, _ in D['booths']): continue   # booths have their own
            lantern(ln_, cx, cy, base + 2.0, 1.0, top(cx) - 0.55)
ln_.done()

# =============== 12. STREET PISHTAQ ARCH + tree uplights + kids chests ===============
st = Batch('street_portal_detail', 'Street_facade')
e0, e1 = D['ent']; xs = xb((e0 + e1) / 2) - 0.75
for poly in spandrels((e0 + e1) / 2, (e1 - e0), SID + 2.55, SID + 3.25, SID + 3.45, (e1 - e0) + 0.02): st.extrude_yz(poly, xs - 0.15, xs + 0.15, m['majolica'])
st.box(xs - 0.17, e0 - 0.7, SID + 3.4, xs + 0.17, e1 + 0.7, SID + 3.62, m['band'])
lantern(st, xs, (e0 + e1) / 2, SID + 2.7, 1.3, SID + 3.2)
for x, y in D['trees']:
    for a in (0.5, 2.6, 4.7): st.cyl(x + 0.75 * math.cos(a), y + 0.75 * math.sin(a), TER, TER + 0.06, 0.07, X['lampglow'], n=8)
for i, (x0, y0) in enumerate(((-6.6, 1.8), (-5.4, 1.8), (-1.2, 0.5))):
    st.box(x0, y0, TER, x0 + 0.7, y0 + 0.45, TER + 0.45, [m['majolica'], X['carved'], m['turq']][i]); st.box(x0 - 0.02, y0 - 0.02, TER + 0.45, x0 + 0.72, y0 + 0.47, TER + 0.5, m['brass'])
st.done()

# =============== 13. DOME FINISHES: brick-girih lining inside, terracotta scale tiles outside ===============
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    if o.name.startswith('dome_inner') or o.name.startswith('dome_ribs'): o.data.materials[0] = X['gajbrick']
    if o.name.startswith('dome_shell') or o.name.startswith('dome_lip'): o.data.materials[0] = X['dometile']
print('detail pass ok')
