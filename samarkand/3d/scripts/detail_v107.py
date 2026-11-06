"""rev. 10.7 (owner: 'walls, columns — pictures instead of the real thing; bricks and patterns must be real'):
every face of the architecture that still carried a photo texture (hazarbaf, bannai, kufic, girih star, cobalt majolica, dome glaze,
stone, epigraph, kazan-block brick, hood majolica) is rebuilt as real pieces: the ground of the face (mortar / glazed field) is pulled
back 6-12 mm and real bricks / tiles / stars / ashlar blocks are built flush in front of it, each its own glazed or fired material.
Faces too small to hold one piece (curved facets of the dome shell, fluted counter, pendant drums) get the solid glazed colour of
their pattern, so no photo is left on walls, columns, pishtaq, sebil, bar, planter bands, mangal and the dome."""
import bmesh as _bm7
from shapely.geometry import Polygon as _P, box as _box
from shapely import affinity as _aff
rnd7 = _rnd.Random(107)
TURQ = [mat(f'glaze_turq_{k}', c, rough=0.15, coat=0.8) for k, c in enumerate(((0.05, 0.45, 0.5), (0.04, 0.4, 0.47), (0.07, 0.5, 0.53)))]
STONE3 = [mat(f'ashlar_{k}', c, rough=0.6, bump=0.3, noise_var=0.04) for k, c in enumerate(((0.85, 0.78, 0.64), (0.81, 0.74, 0.6), (0.88, 0.81, 0.68)))]
WGLZ = TILE[1]; COB = TILE[0]
KUF = ["##########",
       "#........#",
       "#.######.#",
       "#.#....#.#",
       "#.#.##.#.#",
       "#.#.#..#.#",
       "#.#.####.#",
       "#.#......#",
       "#.########",
       "#........."]
def _bricks(color, BL=0.24, BH=0.06, J=0.012):
    def gen(u0, v0, u1, v1):
        r0 = math.floor(v0 / (BH + J)); r1 = math.ceil(v1 / (BH + J))
        for r in range(r0, r1):
            v = r * (BH + J); off = (BL + J) / 2 if r % 2 else 0.0
            k0 = math.floor((u0 - off) / (BL + J)); k1 = math.ceil((u1 - off) / (BL + J))
            for k in range(k0, k1):
                u = off + k * (BL + J); yield _box(u, v, u + BL, v + BH), color(u + BL / 2, v + BH / 2, k, r)
    return gen
def _grid(color, T, J):
    def gen(u0, v0, u1, v1):
        for i in range(math.floor(u0 / (T + J)), math.ceil(u1 / (T + J))):
            for j in range(math.floor(v0 / (T + J)), math.ceil(v1 / (T + J))):
                u, v = i * (T + J), j * (T + J); yield _box(u, v, u + T, v + T), color(i, j)
    return gen
def _stars(P, R, cols):
    sq = _box(-R * 0.72, -R * 0.72, R * 0.72, R * 0.72); star = sq.union(_aff.rotate(sq, 45, origin=(0, 0)))
    def gen(u0, v0, u1, v1):
        for i in range(math.floor(u0 / P) - 1, math.ceil(u1 / P) + 1):
            for j in range(math.floor(v0 / P) - 1, math.ceil(v1 / P) + 1):
                yield _aff.translate(star, i * P, j * P), cols[(i + j) % len(cols)]
    return gen
def _haz_col(u, v, k, r): return haz(u - 3.0, v) or BUFF[rnd7.randrange(3)]
def _ban_col(u, v, k, r): return GLZ[(k // 4) % 2] if ((k + r // 2) % 4 == 0 and r % 2 == 0) else BRK[rnd7.randrange(4)]
def _kuf(on, off):
    return lambda i, j: on if KUF[(-j) % 10][i % 10] == '#' else off
# material -> (ground material, inset, generator, solid fallback, min piece size)
PAT = {
    'hazarbaf_t': (MORTAR, 0.012, _bricks(_haz_col), BUFF[0], 0.1),
    'bannai_t': (MORTAR, 0.012, _bricks(_ban_col), BRK[0], 0.1),
    'bannai2_t': (MORTAR, 0.012, _bricks(_ban_col), BRK[1], 0.1),
    'kufic_t': (MORTAR, 0.004, _grid(_kuf(COB, BUFF[0]), 0.058, 0.008), COB, 0.07),
    'epigraph_uv': (MORTAR, 0.004, _grid(_kuf(WGLZ, COB), 0.058, 0.008), COB, 0.07),
    'girihstar_t': (WGLZ, 0.004, _stars(0.26, 0.11, [COB, TILE[2]]), COB, 0.1),
    'majcobalt_t': (COB, 0.004, _stars(0.18, 0.07, [WGLZ, TILE[2]]), COB, 0.08),
    'majolica2': (COB, 0.004, _stars(0.18, 0.07, [WGLZ, TILE[3]]), COB, 0.08),
    'domeglaze_t': (MORTAR, 0.004, _grid(lambda i, j: TURQ[(i * 7 + j * 3) % 3], 0.12, 0.006), TURQ[0], 0.13),
    'stone_t': (MORTAR, 0.008, _bricks(lambda u, v, k, r: STONE3[rnd7.randrange(3)], 0.44, 0.21, 0.006), STONE3[0], 0.12),
}
# ---------------------------------------------------------------- Samarkand columns: curved real courses on the round shaft
def _sector(b, r0, r1, a0, a1, z0, z1, mm, n=3):
    """closed ring sector (one curved brick / tile): radii r0..r1, angles a0..a1, z0..z1"""
    i = b.mi(mm); V = []
    for r in (r0, r1):
        for z in (z0, z1):
            V.append([b.bm.verts.new((r * math.cos(a0 + (a1 - a0) * k / n), r * math.sin(a0 + (a1 - a0) * k / n), z)) for k in range(n + 1)])
    ib, it_, ob, ot = V
    fs = []
    for k in range(n):
        fs.append(b.bm.faces.new((ob[k], ob[k + 1], ot[k + 1], ot[k])))
        fs.append(b.bm.faces.new((ib[k + 1], ib[k], it_[k], it_[k + 1])))
        fs.append(b.bm.faces.new((ot[k], ot[k + 1], it_[k + 1], it_[k])))
        fs.append(b.bm.faces.new((ib[k], ib[k + 1], ob[k + 1], ob[k])))
    fs.append(b.bm.faces.new((ib[0], ob[0], ot[0], it_[0]))); fs.append(b.bm.faces.new((ob[n], ib[n], it_[n], ot[n])))
    for f in fs: f.material_index = i
def _courses(b, z0, z1, rc, rb, BL, BH, J, col, bond=True):
    """real curved courses on a round shaft: mortar core rc, pieces out to rb"""
    _tube(b, z0, z1, 0.115, rc, MORTAR, 32)
    C = 2 * math.pi * rb; nb = max(6, round(C / (BL + J))); da = 2 * math.pi / nb; ja = J / rb
    row = 0; z = z0 + J / 2
    while z + BH <= z1 - J / 2 + 1e-6:
        off = da / 2 if (bond and row % 2) else 0.0
        for k in range(nb):
            a0 = off + k * da + ja / 2; _sector(b, rc - 0.0005, rb, a0, a0 + da - ja, z, z + BH, col(k, row, nb))
        z += BH + J; row += 1
def _shaft_col(k, r, nb):
    d1, d2 = (k + r) % 8, (k - r) % 8                                   # helical diamond lattice of glazed bricks (hazarbaf)
    if d1 == 0 or d2 == 0: return GLZ[1]
    if d1 == 4 and d2 == 4: return GLZ[0]
    return BUFF[(k * 3 + r) % 3]
def _kuf_col(k, r, nb): return GLZ[1] if KUF[r % 10][k % 10] == '#' else BUFF[0]
@cached
def a_sam_column2(H):
    """Samarkand column, every surface real: octagonal ashlar base with a girih-tiled die, shaft in curved buff bricks with a
    helical glazed-brick diamond lattice, square-kufic bands in glazed brick, stepped muqarnas capital in glazed ceramic"""
    b = MB(); ri = 0.115
    for z0, z1, r, mm in ((0.0, 0.06, 0.27, X['stone']), (0.06, 0.40, 0.23, X['girihstar']), (0.40, 0.46, 0.25, X['stone'])):
        b.ring(0, 0, z0, [(ri, 0.0), (r, 0.0), (r, z1 - z0), (ri, z1 - z0)], mm, 8)
    zc = H - 0.5
    _tube(b, 0.46, 0.52, ri, 0.19, STONE3[0], 32)
    _courses(b, 0.52, 0.64, 0.163, 0.175, 0.03, 0.03, 0.006, _kuf_col, bond=False)
    _courses(b, 0.64, zc - 0.2, 0.153, 0.165, 0.12, 0.05, 0.008, _shaft_col)
    _courses(b, zc - 0.2, zc - 0.08, 0.163, 0.175, 0.03, 0.03, 0.006, _kuf_col, bond=False)
    _tube(b, zc - 0.08, zc, ri, 0.19, STONE3[0], 32)
    z = zc
    for k, (r0, r1, mm) in enumerate([(0.19, 0.23, TURQ[0]), (0.23, 0.27, COB), (0.27, 0.31, TURQ[1]), (0.31, 0.34, COB)]):
        b.ring(0, 0, z, [(ri, 0.0), (r0, 0.0), (r1, 0.075), (r1, 0.1), (ri, 0.1)], mm, 16); z += 0.1
    b.ring(0, 0, z, [(ri, 0.0), (0.36, 0.0), (0.36, H - z), (ri, H - z)], X['stone'], 8)
    return b.mesh(f'Sam_column2_{int(H * 1000)}')
ncol = 0
for o in [o for o in bpy.data.objects if o.name.startswith('Sam_column_') and o.data.name.startswith('Sam_column_')]:
    o.data = a_sam_column2(int(o.data.name.split('_')[-1].split('.')[0]) / 1000); ncol += 1
print('rev 10.7 columns rebuilt', ncol)
SKIP = ('Booth', 'Bukhara_vitrine', 'Bukhara_rotunda', 'vase', 'Aivan_tableset', 'Tableset', 'Tapchan', 'aryk', 'street_steps', 'Tree_planter', 'Bar_drum')
SIDES = {'hazarbaf_t', 'bannai_t', 'bannai2_t', 'stone_t'}            # fired bricks / ashlar get real arrises; glazed tiles are thin slips
def realize(me, zf=-99.0):
    """me: mesh in local coords; returns cladding mesh (or None); edits me in place (ground pulled back, photo mats swapped)"""
    idx = {i: m_.name for i, m_ in enumerate(me.materials) if m_ and m_.name in PAT}
    if not idx: return None
    cb = _bm7.new(); cmats = []
    def mi(mm):
        if mm not in cmats: cmats.append(mm)
        return cmats.index(mm)
    push = {}; nf = 0; realf = set(); pieces.clear()
    vol = 0.0                                                                          # inside-out meshes: work with the true outward normal
    for p in me.polygons:
        vs_ = [me.vertices[i].co for i in p.vertices]
        for k in range(1, len(vs_) - 1): vol += vs_[0].dot(vs_[k].cross(vs_[k + 1]))
    sgn = -1.0 if vol < 0 else 1.0
    for p in me.polygons:
        if p.material_index not in idx: continue
        ground, ins, gen, solid, mn = PAT[idx[p.material_index]]
        n = p.normal.copy() * sgn
        if n.length < 0.5 or abs(n.z) > 0.5: continue                              # walls only: tops / soffits / bottoms stay solid
        u = Vector((0, 0, 1)).cross(n) if abs(n.z) < 0.9 else Vector((1, 0, 0)) - n * n.x
        u.normalize(); v = n.cross(u)
        P3 = [me.vertices[i].co for i in p.vertices]
        pts = [(q.dot(u), q.dot(v)) for q in P3]; d0 = P3[0].dot(n)
        try: poly = _P(pts).buffer(0).buffer(-0.004).intersection(_box(-1e4, zf + 0.004, 1e4, 1e4))   # nothing below the finished floor
        except Exception: continue
        if poly.is_empty: continue
        bx = poly.bounds
        if min(bx[2] - bx[0], bx[3] - bx[1]) < mn or poly.area < mn * mn: continue      # too small: solid colour (below)
        nf += 1
        for i in p.vertices: push.setdefault(i, []).append((n, ins))
        realf.add(p.index)
        for cell, mm in gen(*bx):
            c = cell.intersection(poly)
            if c.is_empty or c.area < 2e-4: continue
            for g in (getattr(c, 'geoms', None) or [c]):
                if g.geom_type != 'Polygon' or g.area < 2e-4: continue
                ring = list(g.exterior.coords)[:-1]
                if len(ring) < 3: continue
                lo = [cb.verts.new(u * a + v * b_ + n * (d0 - ins + 0.0005)) for a, b_ in ring]
                hi = [cb.verts.new(u * a + v * b_ + n * d0) for a, b_ in ring]
                k_ = mi(mm); f0 = len(cb.faces)
                try:
                    f = cb.faces.new(hi); f.material_index = k_
                    if idx[p.material_index] in SIDES:
                        for a in range(len(ring)):
                            s = cb.faces.new((lo[a], lo[(a + 1) % len(ring)], hi[(a + 1) % len(ring)], hi[a])); s.material_index = k_
                    else:
                        for q in lo: cb.verts.remove(q)
                except ValueError: pass
                pieces.append((f0, len(cb.faces)))
    # pull back the ground of the realized faces (distinct normals at a vertex add up: box corners stay square)
    for i, lst in push.items():
        acc = Vector((0, 0, 0)); seen = []
        for n, ins in lst:
            if any(n.dot(s_) > 0.985 for s_ in seen): continue
            seen.append(n); acc -= n * ins
        me.vertices[i].co += acc
    # ground / solid materials replace the photo ones
    gm = {}
    for p in me.polygons:
        if p.material_index in idx:
            nm = idx[p.material_index]; ground, ins, gen, solid, mn = PAT[nm]
            key = (nm, 'g' if p.index in realf else 's')
            gm.setdefault(key, []).append(p.index)
    for (nm, kind), lst in gm.items():
        ground, ins, gen, solid, mn = PAT[nm]; mm = ground if kind == 'g' else solid
        if mm.name not in [m_.name for m_ in me.materials if m_]: me.materials.append(mm)
        k_ = [m_.name if m_ else '' for m_ in me.materials].index(mm.name)
        for pi in lst: me.polygons[pi].material_index = k_
    out = None
    if len(cb.faces):
        out = bpy.data.meshes.new(me.name + '_real'); cb.normal_update(); cb.to_mesh(out)
        for mm in cmats: out.materials.append(mm)
        out['kit'] = 1
    cb.free(); return out
pieces = []; PIECES = {}
def cull(c2, host):
    """remove the pieces that would sit inside anything else (soil in a planter, a logo or a hood set into the wall, a carpet ...)"""
    from mathutils.bvhtree import BVHTree
    lo, hi = _bb(c2); bad = set(); fr = PIECES[c2.data.name]
    def tree(o):                                                                  # same test as the QA: 2 mm inward offset
        b_ = _bm7.new(); b_.from_mesh(o.data); b_.transform(o.matrix_world); b_.normal_update()
        for v_ in b_.verts: v_.co -= v_.normal * 0.002
        t = BVHTree.FromBMesh(b_); b_.free(); return t
    tc = tree(c2)
    for o in bpy.data.objects:
        if o.type != 'MESH' or o is c2 or o.name.endswith('_real') or 'foliage' in o.data.name: continue
        l2, h2 = _bb(o)
        if any(h2[i] < lo[i] or l2[i] > hi[i] for i in range(3)): continue
        for a, b_ in tc.overlap(tree(o)): bad.add(a)
    if not bad: return 0
    starts = [a for a, b_ in fr]; import bisect
    kill = {bisect.bisect_right(starts, f) - 1 for f in bad}
    b_ = _bm7.new(); b_.from_mesh(c2.data); b_.faces.ensure_lookup_table()
    dead = [b_.faces[f] for k in kill for f in range(*fr[k])]
    _bm7.ops.delete(b_, geom=list({f for f in dead}), context='FACES')
    me2 = bpy.data.meshes.new(c2.data.name + 'c'); b_.to_mesh(me2); b_.free()
    for mm in c2.data.materials: me2.materials.append(mm)
    c2.data = me2; return len(kill)
nobj = nmesh = ncull = 0
def realize_all(skip=SKIP):
    global nobj, nmesh, ncull
    done7 = {}; nobj = 0; nmesh = 0; ncull = 0
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or o.name.endswith('_real') or o.name.startswith(skip): continue
        me = o.data
        if not any(m_ and m_.name in PAT for m_ in me.materials): continue
        if any(abs(s_ - 1) > 1e-3 for s_ in o.scale):
            for i, m_ in enumerate(me.materials):                                   # scaled instances: solid colours only
                if m_ and m_.name in PAT: me.materials[i] = PAT[m_.name][3]
            continue
        if me.name not in done7:
            done7[me.name] = realize(me, TER - o.matrix_world.translation.z); nmesh += 1
            if done7[me.name]: PIECES[done7[me.name].name] = list(pieces)
        cl = done7[me.name]
        if cl:
            c2 = bpy.data.objects.new(o.name + '_real', cl); c2.matrix_world = o.matrix_world.copy()
            for col in o.users_collection: col.objects.link(c2)
            bpy.context.view_layer.update(); PIECES[c2.data.name] = PIECES[cl.name]; ncull += cull(c2, o); nobj += 1
    for o in bpy.data.objects:                                                      # small decor keeps nothing photographic either
        if o.type == 'MESH':
            for i, m_ in enumerate(o.data.materials):
                if m_ and m_.name in PAT: o.data.materials[i] = PAT[m_.name][3]
    return nmesh, nobj, ncull
realize_all()
print('rev 10.7 realized meshes', nmesh, 'cladding objects', nobj, 'pieces culled', ncull)
