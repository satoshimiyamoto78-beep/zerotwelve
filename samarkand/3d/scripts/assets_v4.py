"""Samarkand asset library v4: soft (subdivided) upholstery and figures.
- soften(): Catmull-Clark subdivision of a closed MB mesh (stays watertight), used for cushions, shells, banquettes
- merge(): one mesh from a hard part (crisp joinery) and a soft part (upholstery)
- velvet tub armchair, tiled walnut table with turned legs, channel-tufted banquette, pierced-brass lanterns and the
  dome chandelier, Khiva carved column + aivan arcade bay, skin-modifier people (standing / seated)."""
import math

def soften(me, levels=2):
    sc_ = bpy.context.scene
    o = bpy.data.objects.new('_tmp_soft', me); sc_.collection.objects.link(o)
    md = o.modifiers.new('ss', 'SUBSURF'); md.levels = levels; md.render_levels = levels
    try: md.uv_smooth = 'PRESERVE_BOUNDARIES'
    except Exception: pass
    dg = bpy.context.evaluated_depsgraph_get(); me2 = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    sc_.collection.objects.unlink(o); bpy.data.objects.remove(o)
    for p in me2.polygons: p.use_smooth = True
    me2['kit'] = 1; return me2
def merge(name, parts):
    """parts: list of meshes -> one mesh (materials concatenated, indices remapped)"""
    bm = bmesh.new(); mats = []
    for me in parts:
        n0 = len(bm.faces); bm.from_mesh(me); bm.faces.ensure_lookup_table()
        idx = []
        for mm in me.materials:
            if mm not in mats: mats.append(mm)
            idx.append(mats.index(mm))
        for f in list(bm.faces)[n0:]: f.material_index = idx[f.material_index] if f.material_index < len(idx) else 0
    out = bpy.data.meshes.new(name); bm.to_mesh(out); bm.free()
    for mm in mats: out.materials.append(mm)
    out['kit'] = 1
    for me in parts: bpy.data.meshes.remove(me)
    return out

# ---------------------------------------------------------------- VELVET TUB ARMCHAIR (refs 06, 19)
@cached
def a_tubchair(col):
    """upholstered horseshoe armchair 500 x 480: a soft velvet tub (base + horseshoe back/arms in one body) on a slim walnut
    apron with splayed tapered legs and brass sabots; loose seat cushion +0.44..0.52, back top +0.82.
    Back on the -Y side, the sitter faces +Y; origin at the floor centre."""
    V = X['velvet_' + col]; W = m['walnut']; h = MB()
    h.box(-0.19, -0.17, 0.33, 0.19, 0.19, 0.36, W, 0.004)
    for (tx, ty), (fx, fy) in (((0.16, 0.16), (0.215, 0.215)), ((-0.16, 0.16), (-0.215, 0.215)), ((0.16, -0.14), (0.215, -0.2)), ((-0.16, -0.14), (-0.215, -0.2))):
        h.rod((tx, ty, 0.33), (fx, fy, 0.025), 0.017, W, 12)
        h.cyl(fx, fy, 0.0, 0.025, 0.021, m['brass'], 12)
    # tub: outer horseshoe wall + seat base as ONE quad-grid body (stations around the horseshoe), softened
    s = MB(); ax, ay, t = 0.25, 0.235, 0.075; N = 16; A = math.radians(128)
    phis = [-A + 2 * A * k / N for k in range(N + 1)]; st = []
    for ph in phis:
        top_ = 0.6 + 0.22 * math.cos(ph * 0.7) ** 1.5
        o_ = (ax * math.sin(ph), -ay * math.cos(ph)); i_ = ((ax - t) * math.sin(ph), -(ay - t) * math.cos(ph))
        st.append([s.bm.verts.new((o_[0], o_[1], 0.36)), s.bm.verts.new((i_[0] * 0.2, i_[1] * 0.2 + 0.03, 0.36)), s.bm.verts.new((i_[0] * 0.2, i_[1] * 0.2 + 0.03, 0.44)),
                   s.bm.verts.new((i_[0], i_[1], 0.44)), s.bm.verts.new((i_[0], i_[1], top_)), s.bm.verts.new((o_[0], o_[1], top_))])
    i = s.mi(V); fs = []
    for p_, q_ in zip(st[:-1], st[1:]):
        for k in range(6): fs.append(s.bm.faces.new((p_[k], p_[(k + 1) % 6], q_[(k + 1) % 6], q_[k])))
    for ring_ in (st[0], st[-1]):                                          # end caps as quads
        fs.append(s.bm.faces.new((ring_[0], ring_[1], ring_[2], ring_[3]))); fs.append(s.bm.faces.new((ring_[0], ring_[3], ring_[4], ring_[5])))
    for f in fs: f.material_index = i
    bmesh.ops.recalc_face_normals(s.bm, faces=fs)
    # front seat block between the horseshoe ends
    fy0 = -ay * math.cos(A) - 0.02
    s.box(-0.215, fy0 - 0.12, 0.36, 0.215, 0.245, 0.44, V, 0.03)
    tub = soften(s.mesh('Tubchair_tub'), 2)
    c = MB(); c.lathe(0, 0, 0, [(0.0, 0.0), (0.9, 0.0), (1.0, 0.25), (1.0, 0.65), (0.9, 0.95), (0.0, 1.0)], V, 24)
    for v in c.bm.verts: v.co.x *= 0.175; v.co.y = v.co.y * 0.2 + 0.035; v.co.z = 0.44 + v.co.z * 0.085
    cushion = soften(c.mesh('Tubchair_cushion'), 1)
    return merge(f'Tubchair_{col}', [h.mesh('Tubchair_frame'), tub, cushion])

# ---------------------------------------------------------------- WALNUT TABLE WITH A ZELLIGE INLAY
@cached
def a_tiletable(n):
    """module table n x 700 x 800, walnut frame top with a flush zellige inlay (+0.72..0.76), apron, turned legs"""
    b = MB(); Lx = 0.7 * n; W = m['walnut']; hx, hy = Lx / 2, 0.4; f = 0.07
    b.box(-hx, -hy, 0.72, hx, -hy + f, 0.76, W, 0.006); b.box(-hx, hy - f, 0.72, hx, hy, 0.76, W, 0.006)
    b.box(-hx, -hy + f, 0.72, -hx + f, hy - f, 0.76, W, 0.006); b.box(hx - f, -hy + f, 0.72, hx, hy - f, 0.76, W, 0.006)
    b.box(-hx + f, -hy + f, 0.72, hx - f, hy - f, 0.76, X['zellige'])
    a = 0.045
    for y0, y1 in ((-hy + a, -hy + a + 0.025), (hy - a - 0.025, hy - a)): b.box(-hx + a + 0.06, y0, 0.64, hx - a - 0.06, y1, 0.72, W, 0.003)
    for x0, x1 in ((-hx + a, -hx + a + 0.025), (hx - a - 0.025, hx - a)): b.box(x0, -hy + a + 0.06, 0.64, x1, hy - a - 0.06, 0.72, W, 0.003)
    prof = [(0.0, 0.0), (0.024, 0.0), (0.024, 0.03), (0.02, 0.05), (0.026, 0.09), (0.02, 0.14), (0.023, 0.3), (0.03, 0.34), (0.022, 0.38), (0.028, 0.56), (0.034, 0.6), (0.034, 0.72), (0.0, 0.72)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (hx - a - 0.03), sy * (hy - a - 0.03)
            b.lathe(cx, cy, 0.0, [(0.0, 0.0), (0.024, 0.0), (0.024, 0.03), (0.0, 0.03)], m['brass'], 16)
            b.lathe(cx, cy, 0.03, [(r, z - 0.03) for r, z in prof[2:-1]] + [(0.0, 0.69)], W, 16)
    return b.mesh(f'Tiletable_{2 * n}p')

# ---------------------------------------------------------------- CHANNEL-TUFTED BANQUETTE (refs 02, 13, 16)
@cached
def a_banquette(L, D, col, pillow):
    """banquette L (along X) x D (along Y), back at y = 0, sitter faces +Y: walnut plinth, velvet base, soft seat cushion,
    channel-tufted back (vertical flutes on a backboard) with a walnut cap rail, kilim lumbar pillows; origin = back-left floor corner"""
    V = X['velvet_' + col]; h = MB()
    h.box(0.0, 0.0, 0.0, L, D, 0.07, m['walnut'], 0.004)
    h.box(0.0, 0.0, 0.07, L, D, 0.32, V, 0.01)
    h.box(0.0, 0.0, 0.32, L, 0.06, 0.92, V, 0.01)                                   # backboard
    h.box(0.0, 0.0, 0.92, L, 0.07, 0.95, m['walnut'], 0.005)                        # cap rail
    s = MB(); s.box(0.012, 0.165, 0.32, L - 0.012, D - 0.008, 0.44, V, 0.035)
    nch = max(3, int(round(L / 0.17))); wch = (L - 0.02) / nch
    for k in range(nch): s.box(0.01 + k * wch + 0.002, 0.06, 0.44, 0.01 + (k + 1) * wch - 0.002, 0.16, 0.9, V, 0.03)
    s.box(0.012, 0.06, 0.32, L - 0.012, 0.165, 0.44, V, 0.02)
    soft = soften(s.mesh('Banq_soft'), 2)
    pp = MB(); npl = max(1, int(L / 0.85))
    for k in range(npl):
        cx = L * (k + 0.5) / npl; pp.box(cx - 0.2, 0.162, 0.44, cx + 0.2, 0.25, 0.72, X[pillow] if pillow in X else m[pillow], 0.04)
    return merge(f'Banquette_{int(L * 1000)}x{int(D * 1000)}_{col}', [h.mesh('Banq_base'), soft, soften(pp.mesh('Banq_pillow'), 2)])

# ---------------------------------------------------------------- PIERCED BRASS LANTERNS + CHANDELIER (refs 11, 01)
def _pierced(b, x, y, z, s=1.0):
    """onion lantern hanging from (x, y, z): cap + chain stub at the top, pierced globe below"""
    b.cyl(x, y, z - 0.03 * s, z, 0.008, m['brass'], 6)
    b.lathe(x, y, z - 0.09 * s, [(0.0, 0.0), (0.05 * s, 0.0), (0.03 * s, 0.04 * s), (0.012 * s, 0.06 * s), (0.0, 0.06 * s)], m['brass'], 16)
    b.lathe(x, y, z - 0.42 * s, [(0.0, 0.0), (0.04 * s, 0.01 * s), (0.11 * s, 0.1 * s), (0.13 * s, 0.18 * s), (0.1 * s, 0.27 * s), (0.05 * s, 0.33 * s), (0.0, 0.33 * s)], X['pierced'], 24)
    b.lathe(x, y, z - 0.5 * s, [(0.0, 0.0), (0.012 * s, 0.0), (0.03 * s, 0.06 * s), (0.04 * s, 0.08 * s), (0.0, 0.08 * s)], m['brass'], 12)
@cached
def a_pendant_cluster(k, Ls=(0.35, 0.6, 0.85)):
    """k pierced lanterns (spaced 0.3 apart on a 0.17 circle) on rods of lengths Ls from one brass canopy; origin = canopy top (ceiling contact)"""
    b = MB(); b.cyl(0, 0, -0.04, 0.0, 0.24, m['brass'], 32)
    for j in range(k):
        a = 2 * math.pi * j / k + 0.4; dx, dy = (0.0, 0.0) if k == 1 else (0.17 * math.cos(a), 0.17 * math.sin(a)); L = Ls[j % len(Ls)]
        b.cyl(dx, dy, -0.04 - L, -0.04, 0.005, m['brass'], 6); _pierced(b, dx, dy, -0.04 - L, 1.0)
    return b.mesh(f'Pendant_cluster_{k}_' + '_'.join(str(int(L * 100)) for L in Ls))
@cached
def a_pierced_lantern(s=1.0):
    """single pierced lantern with the a_lantern API: origin = globe centre, hook top at +0.39*s"""
    b = MB(); _pierced(b, 0, 0, 0.39 * s, 1.2 * s); return b.mesh(f'Lantern_pierced_{s:.2f}')
def lantern_at(x, y, z, s, ceil_z, cname='Lights', name='Lantern'):
    inst(a_pierced_lantern(s), name, (x, y, z), 0, cname)
    top_ = z + 0.39 * s
    if ceil_z - top_ > 0.005: inst(a_rod(), 'Rod', (x, y, top_), 0, cname, scale=(1, 1, ceil_z - top_))
@cached
def a_chandelier(drop, R=0.55, n=8):
    """dome chandelier: rod of length `drop` from the attachment point (origin) to a brass hoop of radius R carrying n pierced
    lanterns at alternating heights, a smaller inner hoop and a large central lantern"""
    b = MB(); zr = -drop
    b.cyl(0, 0, zr, 0.0, 0.014, m['brass'], 8)
    for RR in (R, R * 0.5):
        b.ring(0, 0, zr - 0.03, [(RR - 0.02, 0.0), (RR + 0.02, 0.0), (RR + 0.02, 0.03), (RR - 0.02, 0.03)], m['brass'], 64)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4; b.rod((0, 0, zr), (R * math.cos(a), R * math.sin(a), zr - 0.015), 0.007, m['brass'], 6)
    for k in range(n):
        a = 2 * math.pi * k / n + math.pi / n; L = 0.16 if k % 2 else 0.46; x, y = R * math.cos(a), R * math.sin(a)
        b.cyl(x, y, zr - 0.03 - L, zr - 0.03, 0.004, m['brass'], 6); _pierced(b, x, y, zr - 0.03 - L, 0.9)
    for k in range(n // 2):
        a = 4 * math.pi * k / n; x, y = 0.5 * R * math.cos(a), 0.5 * R * math.sin(a)
        b.cyl(x, y, zr - 0.33, zr - 0.03, 0.004, m['brass'], 6); _pierced(b, x, y, zr - 0.33, 0.7)
    _pierced(b, 0, 0, zr, 1.7)
    return b.mesh(f'Chandelier_{int(drop * 100)}_{int(R * 100)}')

# ---------------------------------------------------------------- KHIVA CARVED COLUMN + AIVAN ARCADE (unique divider)
@cached
def a_khiva_column(H):
    """Khiva-style carved elm column on a Rishtan-tiled plinth: plinth 0.24 sq x 0.45, jug ('kuza') base, tapered carved
    shaft with turned rings, stepped capital; top of the capital at H; origin at the floor centre"""
    b = MB(); W = X['carved']
    b.box(-0.12, -0.12, 0.0, 0.12, 0.12, 0.45, m['majolica'], 0.006)
    b.lathe(0, 0, 0.45, [(0.0, 0.0), (0.09, 0.0), (0.12, 0.08), (0.115, 0.16), (0.08, 0.24), (0.06, 0.3), (0.0, 0.3)], W, 24)
    z0, z1 = 0.75, H - 0.22
    prof = [(0.0, 0.0), (0.075, 0.0)]
    n = 6
    for k in range(n):
        zz = (z1 - z0) * k / n; rr = 0.075 - 0.015 * k / n
        prof += [(rr, zz + 0.02), (rr + 0.012, zz + 0.04), (rr, zz + 0.06)]
    prof += [(0.06, z1 - z0), (0.0, z1 - z0)]
    b.lathe(0, 0, z0, prof, W, 20)
    b.lathe(0, 0, z1, [(0.0, 0.0), (0.07, 0.0), (0.1, 0.06), (0.1, 0.09), (0.13, 0.13), (0.13, 0.16), (0.15, 0.2), (0.15, 0.22), (0.0, 0.22)], m['walnut'], 24)
    return b.mesh(f'Khiva_column_{int(H * 100)}')
@cached
def a_arcade_bay(L, kind):
    """bay between two column centres (local y 0..L along the arcade, x -0.08..0.08 across; +x faces the hall):
    Rishtan-tiled parapet with a walnut cap; 'plant' = terracotta planter with clipped myrtle balls, 'jali' = backlit carved
    jali screen in a walnut frame. The plinths of the columns take y 0..0.12 and L-0.12..L."""
    b = MB(); y0, y1 = 0.13, L - 0.13
    b.box(-0.08, y0, 0.0, 0.08, y1, 0.5, m['majolica'], 0.004); b.box(-0.1, y0, 0.5, 0.1, y1, 0.56, m['walnut'], 0.004)
    if kind == 'plant':
        b.box(-0.08, y0 + 0.04, 0.56, 0.08, y1 - 0.04, 0.74, m['clay'], 0.006)
        nb = max(2, int((y1 - y0) / 0.28))
        for k in range(nb):
            cy = y0 + 0.16 + (y1 - y0 - 0.32) * k / (nb - 1); hh = 0.26 + 0.06 * (k % 2)
            b.lathe(0, cy, 0.74, [(0.0, 0.0), (0.06, 0.0), (0.115, 0.07), (0.12, 0.13), (0.1, hh * 0.75), (0.05, hh * 0.95), (0.0, hh)], X['lotus'], 16)
    else:
        b.box(-0.04, y0, 0.56, 0.04, y0 + 0.04, 1.96, m['walnut'], 0.003); b.box(-0.04, y1 - 0.04, 0.56, 0.04, y1, 1.96, m['walnut'], 0.003)
        b.box(-0.04, y0 + 0.04, 1.92, 0.04, y1 - 0.04, 1.96, m['walnut'], 0.003)
        b.box(-0.012, y0 + 0.04, 0.56, 0.012, y1 - 0.04, 1.92, m['jali'])
        b.box(-0.04, y0 + 0.04, 0.56, -0.012, y1 - 0.04, 0.6, X['lampglow'])
    return b.mesh(f'Arcade_bay_{int(L * 1000)}_{kind}')
@cached
def a_arcade_head(L, zb, open_=False):
    """carved pointed-arch head of one bay: two spandrels (x -0.05..0.05) filling y 0.15..L-0.15 from the springing up to the beam
    underside zb, a brass edge bead, and a small pierced lantern hanging at the apex (closed bays only)"""
    b = MB(); w = L - 0.3; zs = zb - (0.75 if open_ else 0.62); za = zb - 0.1
    for poly in spandrel_polys(L / 2, w, zs, za, zb): b.extrude(poly, -0.05, 0.05, X['carved'], 'yz')
    if not open_: _pierced(b, 0, L / 2, za, 0.7)
    return b.mesh(f'Arcade_head_{int(L * 1000)}_{int(open_)}')

# ---------------------------------------------------------------- PEOPLE (skin modifier + subdivision)
def _skin_part(name, joints, edges, mm, levels=2):
    """joints: [(x, y, z, rx, ry)], edges: [(i, j)]; joint 0 is the root"""
    bm = bmesh.new(); sk = bm.verts.layers.skin.verify()
    vs = [bm.verts.new(p[:3]) for p in joints]
    for v, p in zip(vs, joints): v[sk].radius = (p[3], p[4]); v[sk].use_root = False
    for i, j in edges: bm.edges.new((vs[i], vs[j]))
    seen = set()
    for v0 in vs:                                                      # one root per connected limb chain
        if v0 in seen: continue
        v0[sk].use_root = True; st = [v0]
        while st:
            v = st.pop()
            if v in seen: continue
            seen.add(v); st += [e.other_vert(v) for e in v.link_edges]
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    sc_ = bpy.context.scene; o = bpy.data.objects.new('_tmp_skin', me); sc_.collection.objects.link(o)
    o.modifiers.new('sk', 'SKIN'); ss = o.modifiers.new('ss', 'SUBSURF'); ss.levels = levels; ss.render_levels = levels
    dg = bpy.context.evaluated_depsgraph_get(); me2 = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    sc_.collection.objects.unlink(o); bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
    me2.materials.clear(); me2.materials.append(mm)
    for p in me2.polygons: p.use_smooth = True
    return me2
CLOTHES = {k: 'cloth_' + k for k in ('linen', 'denim', 'silk_ikat', 'white', 'olive', 'black', 'rose', 'sand', 'terra')}
SKINC = [(0.78, 0.58, 0.45), (0.62, 0.44, 0.32), (0.86, 0.68, 0.56), (0.5, 0.35, 0.25)]
def _egg(b, c, rx, ry, h, mm, n=24, tilt=0.0):
    """smooth egg / ellipsoid about the vertical axis, base at c (z), rx across, ry deep, height h"""
    prof = [(0.0, 0.0)] + [(math.sin(math.pi * t / 10) * (0.82 + 0.18 * t / 10), h * (1 - math.cos(math.pi * t / 10)) / 2) for t in range(1, 10)] + [(0.0, h)]
    fs = b.lathe(c[0], c[1], c[2], prof, mm, n)
    vs = {v for f in fs for v in f.verts}
    for v in vs:
        v.co.x = c[0] + (v.co.x - c[0]) * rx; v.co.y = c[1] + (v.co.y - c[1]) * ry
        v.co.y += tilt * (v.co.z - c[2])
    return fs
@cached
def a_human(pose, top_, bot, skin, hair, female, sleeve='long'):
    """stylised, anatomically proportioned figure (~1.70 m) built from smooth skin-modifier limb chains (one chain per limb,
    no branch joints), lathe head with a nose and a hair cap, rounded shoes. pose 'stand' | 'chair' (seat +0.50).
    Faces +Y, origin on the floor under the pelvis."""
    S = mat(f'h_skin_{skin}', SKINC[skin], rough=0.45); T = X[CLOTHES[top_]]; B_ = X[CLOTHES[bot]]
    Hm = mat(f'h_hair_{hair}', [(0.03, 0.025, 0.02), (0.16, 0.09, 0.05), (0.38, 0.33, 0.3)][hair], rough=0.45); shoe = mat('h_shoe', (0.12, 0.07, 0.045), rough=0.35)
    if pose == 'stand':
        P = dict(hipL=(.09, 0, .9), thL=(.1, .01, .7), knL=(.1, .01, .5), caL=(.1, -.015, .36), anL=(.1, -.01, .09), pel=(0, 0, .9), wai=(0, .005, 1.06),
                 che=(0, .01, 1.24), shb=(0, -.005, 1.37), nb=(0, 0, 1.42), shL=(.17, -.01, 1.38), elL=(.215, -.03, 1.12), fa=(.235, 0, 1.0), wrL=(.245, .02, .875),
                 haL=(.255, .04, .77), nt=(0, .01, 1.5))
    else:
        zs = 0.05
        P = dict(hipL=(.09, -.03, .56 + zs), thL=(.1, .17, .56 + zs), knL=(.1, .38, .55 + zs), caL=(.1, .41, .38), anL=(.1, .43, .09), pel=(0, -.06, .57 + zs),
                 wai=(0, -.07, .72 + zs), che=(0, -.065, .89 + zs), shb=(0, -.075, 1.01 + zs), nb=(0, -.065, 1.06 + zs), shL=(.17, -.075, 1.02 + zs),
                 elL=(.21, .0, .81 + zs), fa=(.2, .13, .80 + zs), wrL=(.17, .27, .79 + zs), haL=(.15, .35, .785 + zs), nt=(0, -.055, 1.14 + zs))
    def J(key, rx, ry=None, mirror=False):
        x, y, z = P[key]; return (-x if mirror else x, y, z, rx, ry or rx)
    W_ = 1.1 if female else 1.0; C_ = 0.9 if female else 1.0; parts = []
    for mir in (False, True):                                             # legs: one chain each, from the hip joint down
        parts.append(_skin_part('leg', [J('hipL', .085 * W_, .085, mir), J('thL', .07, mirror=mir), J('knL', .05, mirror=mir), J('caL', .054, .058, mir), J('anL', .035, mirror=mir)],
                                [(0, 1), (1, 2), (2, 3), (3, 4)], B_, 2))
    hx = P['hipL'][0] * (1.0 if not female else 1.05)
    parts.append(_skin_part('hips', [(-hx, P['hipL'][1], P['hipL'][2] + .02, .1 * W_, .1), (hx, P['hipL'][1], P['hipL'][2] + .02, .1 * W_, .1)], [(0, 1)], B_, 2))
    parts.append(_skin_part('torso', [J('pel', .14 * W_, .1), J('wai', .118 * C_, .085), J('che', .15 * C_, .098), J('shb', .135 * C_, .075), J('nb', .05)],
                            [(0, 1), (1, 2), (2, 3), (3, 4)], T, 2))
    for mir in (False, True):                                             # arms: sleeve chain + skin forearm/hand chain
        si = (P['shL'][0] * 0.5 * (-1 if mir else 1), P['shL'][1], P['shL'][2] - 0.015, .07 * C_, .065)          # shoulder blends into the chest
        if sleeve == 'long':
            parts.append(_skin_part('arm', [si, J('shL', .056, mirror=mir), J('elL', .042, mirror=mir), J('fa', .04, mirror=mir), J('wrL', .034, mirror=mir)], [(0, 1), (1, 2), (2, 3), (3, 4)], T, 2))
            parts.append(_skin_part('hand', [J('wrL', .026, .022, mir), J('haL', .04, .017, mir)], [(0, 1)], S, 2))
        else:
            parts.append(_skin_part('arm', [si, J('shL', .058, mirror=mir), J('elL', .047, mirror=mir)], [(0, 1), (1, 2)], T, 2))
            parts.append(_skin_part('fore', [J('elL', .036, mirror=mir), J('fa', .034, mirror=mir), J('wrL', .026, .022, mir), J('haL', .04, .017, mir)], [(0, 1), (1, 2), (2, 3)], S, 2))
    parts.append(_skin_part('neck', [J('nb', .046), J('nt', .043)], [(0, 1)], S, 2))
    hx_, hy_, hz_ = P['nt'][0], P['nt'][1] + .012, P['nt'][2] - .02
    hb = MB(); _egg(hb, (hx_, hy_, hz_), 0.078, 0.092, 0.235, S, 24, tilt=0.05)
    hb.extrude([(-0.012, 0.0), (0.012, 0.0), (0.0, 0.03)], hz_ + 0.085, hz_ + 0.125, S, 'xy', 0.0)                # nose
    for v in hb.bm.verts:
        if v.co.z > hz_ + 0.084 and v.co.z < hz_ + 0.126 and abs(v.co.x) < 0.013 and v.co.y < 0.031:
            v.co.y += hy_ + 0.072
    parts.append(soften(hb.mesh('head'), 2))
    hc = MB()                                                             # hair cap over the crown (and a fall at the back for long hair)
    _egg(hc, (hx_, hy_ - 0.008, hz_ + 0.075), 0.088, 0.1, 0.175, Hm, 24, tilt=0.06)
    if female: _egg(hc, (hx_, hy_ - 0.06, hz_ - 0.17 if pose == 'stand' else hz_ - 0.14), 0.07, 0.035, 0.29, Hm, 20)
    parts.append(soften(hc.mesh('hair'), 1))
    sh = MB()
    for sx in (-1, 1):
        ax_, ay_, _ = P['anL']; ax_ = sx * ax_
        out_ = [(ax_ + 0.04 * math.cos(a), ay_ + 0.11 + 0.075 * math.sin(a)) for a in [math.pi * t / 6 for t in range(7)]]      # rounded toe
        out_ += [(ax_ - 0.036, ay_ - 0.02), (ax_ - 0.03, ay_ - 0.065), (ax_ + 0.03, ay_ - 0.065), (ax_ + 0.036, ay_ - 0.02)]
        sh.extrude(out_, 0.0, 0.07, shoe, 'xy', 0.012)
    parts.append(soften(sh.mesh('shoes'), 2))
    if female and pose == 'stand':
        sk = MB(); sk.lathe(0, 0, 0.44, [(0.0, 0.0), (0.21, 0.0), (0.19, 0.2), (0.16, 0.42), (0.13, 0.6), (0.0, 0.62)], T, 32)
        parts.append(soften(sk.mesh('skirt'), 1))
    return merge(f'Human_{pose}_{top_}_{bot}_{skin}{hair}{int(female)}{sleeve[0]}', parts)
