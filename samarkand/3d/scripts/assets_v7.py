"""Samarkand asset library v7 (owner references R12-v6): carved walnut armchair with pierced star-lattice back and arms,
arched apron with stepped brackets and kilim cushions; matching carved table (zellige top, arched apron, square legs, brass feet).
Pierced panels are real holes (shapely: panel minus 8-point stars, cut into hole-free pieces), so they read in every view."""
import math
from shapely.geometry import box as sbox, Polygon
from shapely.ops import unary_union

def _star(cx, cy, R, n=8):
    """8-point star = two squares, circumradius R"""
    a = [Polygon([(cx + R * math.cos(math.radians(45 * k + o)), cy + R * math.sin(math.radians(45 * k + o))) for k in (0, 2, 4, 6)]) for o in (0, 45)]
    return unary_union(a)

def _strips(poly):
    """hole-free pieces: intersect with horizontal strips between every hole top / bottom (robust when holes touch the cut at a tip)"""
    cuts = sorted({round(v, 6) for r in poly.interiors for v in (r.bounds[1], r.bounds[3])} | {round(poly.bounds[1], 6), round(poly.bounds[3], 6)})
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        if b - a < 1e-5: continue
        q = poly.intersection(sbox(poly.bounds[0] - 1, a, poly.bounds[2] + 1, b))
        for g in getattr(q, 'geoms', [q]):
            if g.geom_type == 'Polygon' and g.area > 1e-8:
                g = g.simplify(1e-6)
                if not g.interiors: out.append(g); continue
                xs = sorted({g.bounds[0] - 1, g.bounds[2] + 1} | {Polygon(r).centroid.x for r in g.interiors})     # tip-to-tip holes: cut vertically too
                for x0, x1 in zip(xs[:-1], xs[1:]):
                    h = g.intersection(sbox(x0, a - 1, x1, b + 1))
                    out.extend(k for k in getattr(h, 'geoms', [h]) if k.geom_type == 'Polygon' and k.area > 1e-8 and not k.interiors)
    return out

def ext_holes(b, poly, a0, a1, mm, plane):
    """watertight prism of a polygon WITH holes (constrained Delaunay caps + walls on every ring), one shell"""
    import shapely
    V = {}
    def P(u, v, w):
        k = (round(u, 7), round(v, 7), w)
        if k not in V: V[k] = b.bm.verts.new({'xy': (u, v, w), 'xz': (u, w, v), 'yz': (w, u, v)}[plane])
        return V[k]
    lo, hi = min(a0, a1), max(a0, a1); i = b.mi(mm); fs = []
    for t in shapely.constrained_delaunay_triangles(poly).geoms:
        c = list(t.exterior.coords)[:3]
        fs.append(b.bm.faces.new([P(u, v, lo) for u, v in c])); fs.append(b.bm.faces.new([P(u, v, hi) for u, v in reversed(c)]))
    for r in [poly.exterior] + list(poly.interiors):
        c = list(r.coords)[:-1]
        for k in range(len(c)):
            (u0, v0), (u1, v1) = c[k], c[(k + 1) % len(c)]
            fs.append(b.bm.faces.new((P(u0, v0, lo), P(u1, v1, lo), P(u1, v1, hi), P(u0, v0, hi))))
    for f in fs: f.material_index = i
    bmesh.ops.recalc_face_normals(b.bm, faces=fs)
    return fs

def jali(u0, v0, u1, v1, cell, rim):
    """pierced panel: rectangle minus a grid of 8-point stars (+ small diamond holes at the cell corners)"""
    W, H = u1 - u0, v1 - v0; nx = max(1, round((W - 2 * rim) / cell)); ny = max(1, round((H - 2 * rim) / cell))
    cu, cv = (W - 2 * rim) / nx, (H - 2 * rim) / ny; holes = []
    for i in range(nx):
        for j in range(ny):
            holes.append(_star(u0 + rim + (i + 0.5) * cu, v0 + rim + (j + 0.5) * cv, 0.36 * min(cu, cv)))
    for i in range(1, nx):
        for j in range(1, ny):
            x, y = u0 + rim + i * cu, v0 + rim + j * cv; r = 0.09 * min(cu, cv)
            holes.append(Polygon([(x - r, y), (x, y - r), (x + r, y), (x, y + r)]))
    return [sbox(u0, v0, u1, v1).difference(unary_union(holes))]

def arch_apron(u0, v0, u1, v1, spring, apex, step=0.02, nstep=3):
    """apron board with one pointed arch opening (open to the bottom) and stepped (muqarnas-like) brackets at both ends"""
    w = u1 - u0; m = 0.035 + nstep * step; c = (u0 + u1) / 2; half = w / 2 - m
    L = arch_left(c, 2 * half, spring, apex, 10)
    left = [(u, z) for u, z in L]; right = [(2 * c - u, z) for u, z in reversed(L[:-1])]
    hole = Polygon([(c - half, v0 - 0.01)] + left + right + [(c + half, v0 - 0.01)])
    steps = []
    for k in range(nstep):                                                       # bracket steps grow downwards from the arch to the leg
        z_ = spring - (k + 1) * (spring - v0) / (nstep + 1)
        steps.append(sbox(u0 + 0.035 + (nstep - k - 1) * step, v0 - 0.01, c - half, z_))
        steps.append(sbox(c + half, v0 - 0.01, u1 - 0.035 - (nstep - k - 1) * step, z_))
    g = sbox(u0, v0, u1, v1).difference(unary_union([hole] + steps)); return [q for q in getattr(g, 'geoms', [g]) if q.area > 1e-8]

XW = dict(wd=tex2('walnutgrain_t', 'walnutgrain.png', 0.6, rough=0.55, bump=0.15), cv=tex2('carvedref_t', 'carvedref.png', 0.32, rough=0.5, bump=0.9),
          k1=bl2.fabric('kilimref_f', os.path.join(TEX2, 'kilimref.png'), 0.55), k2=bl2.fabric('kilimref2_f', os.path.join(TEX2, 'kilimref2.png'), 0.55),
          zt=tex2('zfield_t', 'zfield.png', 0.30, rough=0.12, bump=0.35, coat=0.6))
@cached
def a_carvedchair(kil='k1'):
    """carved walnut armchair 580 x 550 (ref: Damascene / Bukhara carved chair): square posts on brass bun feet, arched aprons,
    pierced star-lattice arm and back panels, moulded arm rails, kilim seat cushion + back cushion.
    Back on the -Y side, the sitter faces +Y; origin at the floor centre; seat (cushion top) +0.50, arms +0.66, back +0.97."""
    b = MB(); W = XW['wd']; CV = XW['cv']; BR = m['brass']
    px0, px1 = 0.23, 0.28; py0, py1 = 0.21, 0.26
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * px0, sx * px1)); y0, y1 = sorted((sy * py0, sy * py1)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            b.lathe(cx, cy, 0.0, [(0.0, 0.0), (0.012, 0.0), (0.022, 0.012), (0.021, 0.026), (0.016, 0.035), (0.0, 0.035)], BR, 16)
            top_ = 0.62 if sy > 0 else 0.955
            b.box(x0, y0, 0.035, x1, y1, top_, W, 0.004)
            if sy < 0: b.lathe(cx, cy, 0.955, [(0.0, 0.0), (0.03, 0.0), (0.03, 0.012), (0.018, 0.022), (0.008, 0.034), (0.0, 0.036)], W, 12)   # post cap
            else: b.box(x0 - 0.004, y0 - 0.004, 0.33, x1 + 0.004, y1 + 0.004, 0.345, W, 0.002)                                        # collar
    # seat rails (carved) + deck
    b.box(-px0, 0.22, 0.36, px0, 0.25, 0.43, CV, 0.003); b.box(-px0, -0.25, 0.36, px0, -0.22, 0.43, CV, 0.003)
    for sx in (-1, 1): b.box(sx * 0.235, -py0, 0.36, sx * 0.268, py0, 0.43, CV, 0.003)
    b.box(-0.235, -0.22, 0.40, 0.235, 0.22, 0.42, W)
    # arched aprons under the rails
    for q in arch_apron(-px0, 0.13, px0, 0.36, 0.25, 0.33): b.extrude(list(q.exterior.coords)[:-1], 0.226, 0.244, W, 'xz')
    for q in arch_apron(-px0, 0.13, px0, 0.36, 0.25, 0.33): b.extrude(list(q.exterior.coords)[:-1], -0.244, -0.226, W, 'xz')
    for sx in (-1, 1):
        for q in arch_apron(-py0, 0.13, py0, 0.36, 0.25, 0.33): b.extrude(list(q.exterior.coords)[:-1], sx * 0.242, sx * 0.258, W, 'yz')
    # arms: pierced side panel + moulded rail
    for sx in (-1, 1):
        b.box(sx * 0.235, -py0, 0.43, sx * 0.268, py0, 0.455, W, 0.002)
        for q in jali(-py0, 0.455, py0, 0.615, 0.053, 0.012): ext_holes(b, q, sx * 0.244, sx * 0.258, W, 'yz')
        x0, x1 = sorted((sx * 0.226, sx * 0.292))
        b.box(x0, -py0, 0.62, x1, 0.29, 0.645, W, 0.006); b.box(x0 + 0.006, -py0, 0.645, x1 - 0.006, 0.282, 0.66, W, 0.004)
    # back: carved lower rail, pierced panel, crest rail
    b.box(-px0, -0.25, 0.43, px0, -0.222, 0.55, CV, 0.003)
    for q in jali(-px0, 0.55, px0, 0.875, 0.058, 0.014): ext_holes(b, q, -0.244, -0.228, W, 'xz')
    b.box(-px0, -0.252, 0.875, px0, -0.218, 0.94, CV, 0.004); b.box(-px0 - 0.0, -0.256, 0.94, px0, -0.214, 0.955, W, 0.004)
    hard = b.mesh('Carvedchair_frame')
    s = MB(); s.box(-0.226, -0.21, 0.42, 0.226, 0.215, 0.515, XW[kil], 0.03)
    s.box(-0.205, -0.219, 0.515, 0.205, -0.15, 0.71, XW['k2' if kil == 'k1' else 'k1'], 0.03)
    return merge(f'Carvedchair_{kil}', [hard, soften(s.mesh('Carvedchair_cushions'), 2)])

@cached
def a_carvedtable(n):
    """module table n x 700 x 800 to match the carved chair: walnut frame top with a flush zellige inlay (+0.72..0.76),
    shallow arched aprons with stepped brackets (knee clearance 0.685 in the middle), square legs on brass feet"""
    b = MB(); Lx = 0.7 * n; W = XW['wd']; hx, hy = Lx / 2, 0.4; f = 0.07
    b.box(-hx, -hy, 0.72, hx, -hy + f, 0.76, W, 0.006); b.box(-hx, hy - f, 0.72, hx, hy, 0.76, W, 0.006)
    b.box(-hx, -hy + f, 0.72, -hx + f, hy - f, 0.76, W, 0.006); b.box(hx - f, -hy + f, 0.72, hx, hy - f, 0.76, W, 0.006)
    b.box(-hx + f, -hy + f, 0.72, hx - f, hy - f, 0.76, XW['zt'])
    a = 0.045; lg = 0.055
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (hx - a - lg / 2), sy * (hy - a - lg / 2)
            b.lathe(cx, cy, 0.0, [(0.0, 0.0), (0.014, 0.0), (0.026, 0.014), (0.025, 0.03), (0.019, 0.04), (0.0, 0.04)], m['brass'], 16)
            b.box(cx - lg / 2, cy - lg / 2, 0.04, cx + lg / 2, cy + lg / 2, 0.72, W, 0.004)
            b.box(cx - lg / 2 - 0.005, cy - lg / 2 - 0.005, 0.10, cx + lg / 2 + 0.005, cy + lg / 2 + 0.005, 0.115, W, 0.002)
    ux0, ux1 = -hx + a + lg, hx - a - lg; uy0, uy1 = -hy + a + lg, hy - a - lg
    for sy in (-1, 1):
        y_ = sy * (hy - a - lg / 2)
        for q in arch_apron(ux0, 0.61, ux1, 0.72, 0.655, 0.705, 0.012, 2): b.extrude(list(q.exterior.coords)[:-1], y_ - 0.011, y_ + 0.011, XW['cv'], 'xz')
    for sx in (-1, 1):
        x_ = sx * (hx - a - lg / 2)
        for q in arch_apron(uy0, 0.61, uy1, 0.72, 0.655, 0.705, 0.012, 2): b.extrude(list(q.exterior.coords)[:-1], x_ - 0.011, x_ + 0.011, XW['cv'], 'yz')
    return b.mesh(f'Carvedtable_{2 * n}p')

# ---------------------------------------------------------------- PIERCED BRASS LANTERNS (owner refs: pendant with jewels, lantern clusters)
def pierced_brass_mat(name):
    """brass sheet with the pierced pattern glowing warm from inside, coloured glass jewels in some rosettes"""
    if name in bl._mats: return bl._mats[name]
    mm = bpy.data.materials.new(name); N = mm.node_tree.nodes; Lk = mm.node_tree.links; b = N['Principled BSDF']
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(TEX2, 'piercedbrass.png'), check_existing=True)
    uv = N.new('ShaderNodeUVMap'); uv.uv_map = 'UVMap'; Lk.new(uv.outputs['UV'], it.inputs['Vector'])
    bw = N.new('ShaderNodeRGBToBW'); Lk.new(it.outputs['Color'], bw.inputs['Color'])
    mk = N.new('ShaderNodeMapRange'); mk.inputs['From Min'].default_value = 0.05; mk.inputs['From Max'].default_value = 0.25; Lk.new(bw.outputs['Val'], mk.inputs['Value'])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.inputs['A'].default_value = (0.40, 0.25, 0.08, 1)
    Lk.new(mk.outputs['Result'], mix.inputs['Factor']); Lk.new(it.outputs['Color'], mix.inputs['B']); Lk.new(mix.outputs['Result'], b.inputs['Base Color'])
    inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; Lk.new(mk.outputs['Result'], inv.inputs[1]); Lk.new(inv.outputs[0], b.inputs['Metallic'])
    Lk.new(it.outputs['Color'], b.inputs['Emission Color'])
    em = N.new('ShaderNodeMath'); em.operation = 'MULTIPLY'; em.inputs[1].default_value = 4.0; Lk.new(mk.outputs['Result'], em.inputs[0]); Lk.new(em.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Roughness'].default_value = 0.32
    bl._mats[name] = mm; return mm
X['pierced'] = pierced_brass_mat('pierced_brass'); register_uv_size(X['pierced'], 0.24)
def _pierced(b, x, y, z, s=1.0):
    """octagonal pierced-brass lantern hanging from (x, y, z), same 0.5*s envelope as before: hook, onion crown, collar,
    faceted pierced body with a brass waist band, bottom collar, drop finial"""
    B = m['brass']; P = X['pierced']
    b.cyl(x, y, z - 0.03 * s, z, 0.008, B, 6)
    b.lathe(x, y, z - 0.10 * s, [(0.0, 0.0), (0.062 * s, 0.0), (0.066 * s, 0.01 * s), (0.05 * s, 0.03 * s), (0.03 * s, 0.05 * s), (0.034 * s, 0.058 * s),
                                 (0.012 * s, 0.068 * s), (0.0, 0.07 * s)], P, 8, smooth=False)
    b.lathe(x, y, z - 0.118 * s, [(0.0, 0.0), (0.075 * s, 0.0), (0.075 * s, 0.018 * s), (0.0, 0.018 * s)], B, 8, smooth=False)
    b.lathe(x, y, z - 0.40 * s, [(0.0, 0.0), (0.034 * s, 0.0), (0.075 * s, 0.035 * s), (0.118 * s, 0.10 * s), (0.13 * s, 0.165 * s), (0.122 * s, 0.215 * s),
                                 (0.09 * s, 0.26 * s), (0.062 * s, 0.282 * s), (0.0, 0.282 * s)], P, 8, smooth=False)
    b.lathe(x, y, z - 0.25 * s, [(0.0, 0.0), (0.134 * s, 0.0), (0.134 * s, 0.014 * s), (0.0, 0.014 * s)], B, 8, smooth=False)
    b.lathe(x, y, z - 0.418 * s, [(0.0, 0.0), (0.04 * s, 0.0), (0.04 * s, 0.018 * s), (0.0, 0.018 * s)], B, 8, smooth=False)
    b.lathe(x, y, z - 0.5 * s, [(0.0, 0.0), (0.005 * s, 0.0), (0.016 * s, 0.03 * s), (0.026 * s, 0.055 * s), (0.028 * s, 0.07 * s), (0.026 * s, 0.082 * s), (0.0, 0.082 * s)], B, 8)

# ---------------------------------------------------------------- CARVED JALI CABINET (owner ref: sideboard with arched jali doors)
@cached
def a_jali_cabinet(Wd, Dp, H, n=1):
    """carved walnut cabinet Wd x Dp x H on turned bun feet: carved face frame, n doors with cusped pointed-arch openings
    filled with pierced star lattice, turned pilasters at the door edges, brass knobs, moulded top with a rope band.
    Origin = floor centre, front face +Y (towards the guests)."""
    b = MB(); W = XW['wd']; CV = XW['cv']; hx, hy = Wd / 2, Dp / 2; zf = 0.10; zt = H - 0.045
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.lathe(sx * (hx - 0.055), sy * (hy - 0.055), 0.0, [(0.0, 0.0), (0.02, 0.0), (0.036, 0.03), (0.038, 0.055), (0.03, 0.08), (0.024, 0.1), (0.0, 0.1)], W, 16)
    b.box(-hx, -hy, zf, hx, hy - 0.03, zt, W, 0.004)                                   # carcass
    fy0, fy1 = hy - 0.03, hy - 0.005
    m_ = 0.07; dw = (Wd - m_ * (n + 1)) / n; z0, z1 = zf + 0.07, zt - 0.11
    ops = []
    for k in range(n):
        x0 = -hx + m_ + k * (dw + m_); c = x0 + dw / 2; L = arch_left(c, dw, z1 - 0.42 * dw, z1, 10)
        ops.append(Polygon([(x0, z0)] + L + [(2 * c - u, z) for u, z in reversed(L[:-1])] + [(x0 + dw, z0)]))
    face = sbox(-hx, zf, hx, zt).difference(unary_union(ops))
    for q in getattr(face, 'geoms', [face]):
        if q.interiors: ext_holes(b, q, fy0, fy1, CV, 'xz')
        else: b.extrude(list(q.exterior.coords)[:-1], fy0, fy1, CV, 'xz')
    for op in ops:
        x0, _, x1, _ = op.bounds
        for g in jali(x0 - 0.01, z0 - 0.01, x1 + 0.01, z1 + 0.01, 0.06, 0.0):
            p = g.intersection(op.buffer(0.012))
            for q in getattr(p, 'geoms', [p]):
                if q.geom_type == 'Polygon' and q.area > 1e-6: ext_holes(b, q.simplify(1e-5), fy0 - 0.012, fy0, W, 'xz')
        sp = z1 - 0.42 * (x1 - x0)
        for u in (x0 - 0.016, x1 + 0.016):                                              # turned pilasters
            b.lathe(u, fy1 + 0.008, z0, [(0.014, 0.0), (0.016, 0.02), (0.011, 0.04), (0.011, sp - z0 - 0.06), (0.016, sp - z0 - 0.04), (0.013, sp - z0 - 0.02), (0.0, sp - z0)], W, 12)
        b.rod((x1 - 0.03, fy1, (z0 + sp) / 2), (x1 - 0.03, fy1 + 0.03, (z0 + sp) / 2), 0.009, m['brass'], 10)
        b.lathe(x1 - 0.03, fy1 + 0.03, (z0 + sp) / 2 - 0.02, [(0.0, 0.0), (0.018, 0.0), (0.02, 0.02), (0.012, 0.04), (0.0, 0.04)], m['brass'], 12)
    b.box(-hx - 0.015, -hy - 0.01, zt, hx + 0.015, hy + 0.015, zt + 0.02, CV, 0.003)    # rope band + top board
    b.box(-hx - 0.025, -hy - 0.015, zt + 0.02, hx + 0.025, hy + 0.025, H, W, 0.006)
    b.box(-hx - 0.008, -hy - 0.006, zf - 0.02, hx + 0.008, hy + 0.008, zf + 0.02, CV, 0.003)  # plinth band
    return b.mesh(f'Jalicabinet_{int(Wd * 100)}x{int(Dp * 100)}x{int(H * 100)}_{n}')

@cached
def a_sconce():
    """pierced-brass wall sconce (owner ref): tall hexagonal lantern with onion cap and drop, on a brass backplate + arm.
    Origin = wall surface at the lantern centre height; local +Y points out of the wall."""
    b = MB(); B = m['brass']; P = X['pierced']; c = 0.085
    b.box(-0.04, 0.0, -0.10, 0.04, 0.012, 0.10, B, 0.003)                              # backplate
    b.box(-0.012, 0.012, -0.012, 0.012, c - 0.05, 0.012, B, 0.002)                     # arm
    b.lathe(0, c, -0.17, [(0.0, 0.0), (0.06, 0.0), (0.075, 0.03), (0.075, 0.30), (0.06, 0.34), (0.0, 0.34)], P, 6, smooth=False)
    b.lathe(0, c, 0.17, [(0.0, 0.0), (0.064, 0.0), (0.05, 0.035), (0.028, 0.065), (0.032, 0.075), (0.0, 0.09)], P, 6, smooth=False)
    b.lathe(0, c, -0.26, [(0.0, 0.0), (0.03, 0.015), (0.05, 0.05), (0.064, 0.09), (0.0, 0.09)], P, 6, smooth=False)
    for z in (-0.172, 0.168): b.lathe(0, c, z, [(0.0, 0.0), (0.08, 0.0), (0.08, 0.008), (0.0, 0.008)], B, 6, smooth=False)
    b.lathe(0, c, 0.26, [(0.0, 0.0), (0.008, 0.0), (0.004, 0.03), (0.0, 0.035)], B, 8)
    b.lathe(0, c, -0.31, [(0.0, 0.0), (0.006, 0.02), (0.014, 0.04), (0.0, 0.05)], B, 8)
    return b.mesh('Sconce_pierced')

# ---------------------------------------------------------------- TRAINED CHINAR UNDER THE ROOF (owner rev. 7)
def leaf_card_mat():
    """plane-tree leaf cards: alpha-clipped atlas (glTF exports as MASK), slightly glossy upper side"""
    if 'leaf_card' in bl._mats: return bl._mats['leaf_card']
    mm = bpy.data.materials.new('leaf_card'); N = mm.node_tree.nodes; Lk = mm.node_tree.links; b = N['Principled BSDF']
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(TEX2, 'platanleaf.png'), check_existing=True)
    uv = N.new('ShaderNodeUVMap'); uv.uv_map = 'UVMap'; Lk.new(uv.outputs['UV'], it.inputs['Vector']); Lk.new(it.outputs['Color'], b.inputs['Base Color'])
    rd = N.new('ShaderNodeMath'); rd.operation = 'ROUND'; Lk.new(it.outputs['Alpha'], rd.inputs[0]); Lk.new(rd.outputs[0], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = 0.5
    try: b.inputs['Subsurface Weight'].default_value = 0.15
    except Exception: pass
    bl._mats['leaf_card'] = mm; return mm
@cached
def a_chinar_trained(seed=3):
    """plane tree kept under the roof: buttressed trunk to +2.05 (bark), five scaffold limbs + forks spreading to r 1.45 at
    +2.5..2.85, foliage as ~70 lumpy leaf clumps forming a low umbrella (top <= +3.15, underside >= +1.75 over the ring bench).
    Returns (wood, foliage) meshes; origin at the terrace surface in the trunk axis."""
    import random; R_ = random.Random(seed); b = MB(); N = 28; H = 2.05; r0, r1 = 0.30, 0.22
    prof = [(0.0, r0 * 1.9), (0.08, r0 * 1.6), (0.25, r0 * 1.2), (0.5, r0 * 1.05), (1.2, r0), (1.8, (r0 + r1) / 2), (H, r1)]
    rings = []
    for z, r in prof:
        fl = max(0.0, 1 - z / 0.6)
        rings.append([b.bm.verts.new(((r * (1 + 0.28 * fl * max(0, math.cos(3 * a)) ** 3 + 0.035 * math.sin(11 * a + z * 1.7))) * math.cos(a),
                                      (r * (1 + 0.28 * fl * max(0, math.cos(3 * a)) ** 3 + 0.035 * math.sin(11 * a + z * 1.7))) * math.sin(a), z)) for a in [2 * math.pi * k / N for k in range(N)]])
    BK = tex2('platanbark_t', 'platanbark.png', 0.8, rough=0.8, bump=0.6); register_uv_size(BK, 0.8)
    i = b.mi(BK); fs = []
    for p_, q_ in zip(rings[:-1], rings[1:]):
        for k in range(N): fs.append(b.bm.faces.new((p_[k], p_[(k + 1) % N], q_[(k + 1) % N], q_[k])))
    fs.append(b.bm.faces.new(list(reversed(rings[0])))); fs.append(b.bm.faces.new(rings[-1]))
    for f in fs: f.material_index = i; b.smooth.add(f)
    bmesh.ops.recalc_face_normals(b.bm, faces=fs)
    tips = []
    for k in range(5):
        a = 2 * math.pi * k / 5 + R_.uniform(-0.25, 0.25); rr = R_.uniform(0.85, 1.05); zt = R_.uniform(2.5, 2.7)
        p0 = (0.06 * math.cos(a), 0.06 * math.sin(a), H - 0.12); p1 = (rr * math.cos(a), rr * math.sin(a), zt)
        pm = tuple(p0[j] * 0.45 + p1[j] * 0.55 for j in range(3)); b.rod(p0, pm, 0.09, BK, 10); b.rod(pm, p1, 0.062, BK, 10)
        for s_ in (-1, 1):                                                    # fork into two shoots
            a2 = a + s_ * R_.uniform(0.3, 0.5); r2 = rr + R_.uniform(0.3, 0.45); p2 = (r2 * math.cos(a2), r2 * math.sin(a2), zt + R_.uniform(0.1, 0.22))
            b.rod(p1, p2, 0.04, BK, 8); tips.append(p2)
            for _t in range(3):                                               # twigs into the crown
                a3 = a2 + R_.uniform(-0.6, 0.6); r3 = r2 + R_.uniform(0.15, 0.35); p3 = (r3 * math.cos(a3), r3 * math.sin(a3), p2[2] + R_.uniform(0.05, 0.25))
                b.rod(p2, p3, 0.016, BK, 6); tips.append(p3)
        tips.append(p1)
    wood = b.mesh('Chinar_trained_wood')
    # foliage: ~2600 plane-tree leaf cards (alpha atlas, 4 tints) in ~85 clumps forming a low umbrella
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap'); pts = []
    for p in tips: pts.append((p[0], p[1], p[2] + 0.1, R_.uniform(0.24, 0.3)))
    while len(pts) < 115:
        rho = 1.55 * math.sqrt(R_.random()); a = R_.uniform(0, 2 * math.pi)
        z = 2.45 + 0.42 * (1 - (rho / 1.6) ** 2) + R_.uniform(-0.12, 0.1); rad = R_.uniform(0.2, 0.3)
        if z + rad > 3.12: z = 3.12 - rad
        if z - rad < 1.8: continue
        pts.append((rho * math.cos(a), rho * math.sin(a), z, rad))
    from mathutils import Vector as V_
    for x, y, z, r in pts:
        for _ in range(int(62 * (r / 0.25) ** 2)):
            while True:
                d = V_((R_.uniform(-1, 1), R_.uniform(-1, 1), R_.uniform(-1, 1)))
                if d.length <= 1: break
            c = V_((x, y, z)) + d * r * V_((1, 1, 0.75))
            n_ = (V_((R_.gauss(0, 0.6), R_.gauss(0, 0.6), 1.0)) + (c - V_((0, 0, 2.2))).normalized() * 0.6).normalized()
            t_ = n_.cross(V_((R_.uniform(-1, 1), R_.uniform(-1, 1), R_.uniform(-.2, .2)))).normalized(); u_ = n_.cross(t_)
            sz = R_.uniform(0.13, 0.19); vs = [bm.verts.new(c + t_ * (sx * sz / 2) + u_ * (sy * sz)) for sx, sy in ((-1, -0.1), (1, -0.1), (1, 0.9), (-1, 0.9))]
            f = bm.faces.new(vs); ci, cj = R_.randrange(2), R_.randrange(2)
            for lp, (uu, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = ((ci + uu) / 2, (cj + vv) / 2)
    fol = bpy.data.meshes.new('Chinar_trained_foliage'); bm.to_mesh(fol); bm.free()
    fol.materials.append(leaf_card_mat()); fol['kit'] = 1
    return wood, fol

# ---------------------------------------------------------------- PLANT KIT (rev. 7): leaf / flower cards instead of low-poly blobs
def card_mat(name, file, rough=0.5):
    """alpha-clipped card material (exports to glTF as MASK)"""
    if name in bl._mats: return bl._mats[name]
    mm = bpy.data.materials.new(name); N = mm.node_tree.nodes; Lk = mm.node_tree.links; b = N['Principled BSDF']
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(TEX2, file), check_existing=True)
    uv = N.new('ShaderNodeUVMap'); uv.uv_map = 'UVMap'; Lk.new(uv.outputs['UV'], it.inputs['Vector']); Lk.new(it.outputs['Color'], b.inputs['Base Color'])
    rd = N.new('ShaderNodeMath'); rd.operation = 'ROUND'; Lk.new(it.outputs['Alpha'], rd.inputs[0]); Lk.new(rd.outputs[0], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = rough
    bl._mats[name] = mm; return mm
class Cards:
    """bmesh of alpha cards; add(centre, radius, n, size, cells) scatters quads in an ellipsoid, faces lean upward/outward"""
    def __init__(s, seed):
        import random; s.R = random.Random(seed); s.bm = bmesh.new(); s.uv = s.bm.loops.layers.uv.new('UVMap'); s.mats = []
    def add(s, c, r, n, size, mm, cells=None, squash=0.8, up=1.0, axis=None):
        from mathutils import Vector as V_
        if mm not in s.mats: s.mats.append(mm)
        mi = s.mats.index(mm); R_ = s.R; c = V_(c)
        for _ in range(n):
            while True:
                d = V_((R_.uniform(-1, 1), R_.uniform(-1, 1), R_.uniform(-1, 1)))
                if d.length <= 1: break
            p = c + V_((d.x * r, d.y * r, d.z * r * squash))
            n_ = (V_((R_.gauss(0, .6), R_.gauss(0, .6), up)) + (p - c).normalized() * .7).normalized()
            t_ = n_.cross(V_((R_.uniform(-1, 1), R_.uniform(-1, 1), R_.uniform(-.2, .2)))).normalized(); u_ = n_.cross(t_)
            sz = R_.uniform(*size)
            vs = [s.bm.verts.new(p + t_ * (sx * sz / 2) + u_ * (sy * sz)) for sx, sy in ((-1, -.1), (1, -.1), (1, .9), (-1, .9))]
            f = s.bm.faces.new(vs); f.material_index = mi
            ci, cj = (R_.randrange(2), R_.randrange(2)) if cells is None else cells[R_.randrange(len(cells))]
            for lp, (uu, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[s.uv].uv = ((ci + uu) / 2, (cj + vv) / 2)
    def mesh(s, name, zfloor=None):
        if zfloor is not None:
            for v in s.bm.verts: v.co.z = max(v.co.z, zfloor)                 # no leaf below the soil line
        me = bpy.data.meshes.new(name); s.bm.to_mesh(me); s.bm.free()
        for mm in s.mats: me.materials.append(mm)
        me['kit'] = 1; return me
def _plantmats():
    return dict(leafn=card_mat('leaf_narrow', 'narrowleaf.png', 0.4), flower=card_mat('flower_card', 'flowers.png', 0.6),
                bark=tex2('platanbark_t', 'platanbark.png', 0.8, rough=0.8, bump=0.6), smooth=mat('bark_smooth', (0.36, 0.33, 0.28), rough=0.7, noise_var=0.05),
                palm=mat('palm_leaflet', (0.16, 0.36, 0.08), rough=0.45, noise_var=0.12), stem=mat('palm_stem', (0.42, 0.48, 0.2), rough=0.5, noise_var=0.08),
                banana=mat('banana_leaf_v7', (0.07, 0.24, 0.05), rough=0.4, noise_var=0.1), fruit=m.get('pomfruit') or mat('pomfruit_g', (0.45, 0.04, 0.05), rough=0.3, coat=0.4))
@cached
def a_pomegranate(seed=1):
    """pomegranate (anor), multi-stem small tree ~1.9 m: narrow leaves, scarlet flowers, red fruit; origin = soil surface"""
    P = _plantmats(); import random; R_ = random.Random(seed); b = MB(); tips = []
    for k in range(3):
        a = 2 * math.pi * k / 3 + R_.uniform(-.3, .3); t = (0.18 * math.cos(a), 0.18 * math.sin(a), 1.25)
        b.rod((0.02 * math.cos(a), 0.02 * math.sin(a), 0.004), t, 0.035, P['smooth'], 8); tips.append(t)
    cd = Cards(seed)
    for t in tips: cd.add((t[0] * 1.6, t[1] * 1.6, 1.55), 0.42, 560, (0.08, 0.11), P['leafn'])
    cd.add((0, 0, 1.75), 0.38, 320, (0.08, 0.11), P['leafn'])
    cd.add((0, 0, 1.6), 0.5, 22, (0.05, 0.07), P['flower'], cells=[(1, 1)])
    for k in range(9):
        a = R_.uniform(0, 2 * math.pi); rr = R_.uniform(0.25, 0.48); b.lathe(rr * math.cos(a), rr * math.sin(a), R_.uniform(1.25, 1.75), [(0.0, 0.0), (0.04, 0.012), (0.045, 0.045), (0.035, 0.075), (0.015, 0.085), (0.012, 0.1), (0.0, 0.1)], P['fruit'], 10)
    return merge('Pomegranate_foliage', [b.mesh('pom_wood'), cd.mesh('pom_cards')])
@cached
def a_plumeria(seed=2):
    """frangipani ~2.3 m: thick grey forking branches, rosettes of long leaves at the tips, cream-yellow flower clusters"""
    P = _plantmats(); import random; R_ = random.Random(seed); b = MB(); cd = Cards(seed)
    b.rod((0, 0, 0.0), (0, 0, 1.1), 0.075, P['smooth'], 10)
    for k in range(5):
        a = 2 * math.pi * k / 5 + R_.uniform(-.3, .3); p1 = (0.35 * math.cos(a), 0.35 * math.sin(a), 1.6); b.rod((0, 0, 1.05), p1, 0.05, P['smooth'], 8)
        for s_ in (-1, 1):
            a2 = a + s_ * 0.45; p2 = (p1[0] + 0.3 * math.cos(a2), p1[1] + 0.3 * math.sin(a2), 2.0 + R_.uniform(-.1, .1)); b.rod(p1, p2, 0.035, P['smooth'], 8)
            cd.add((p2[0], p2[1], p2[2] + 0.08), 0.22, 26, (0.22, 0.3), P['leafn'], up=1.6)
            cd.add((p2[0], p2[1], p2[2] + 0.2), 0.1, 12, (0.06, 0.08), P['flower'], cells=[(0, 0)], up=2.0)
    return merge('Plumeria_foliage', [b.mesh('plum_wood'), cd.mesh('plum_cards')])
def _frond(bm, base, a, L, droop, nleaf, mm_i, R_, w=0.022, ll=0.32):
    """palm frond: arching rachis (tube approximated by a thin strip) with alternate drooping leaflets (thin quads)"""
    from mathutils import Vector as V_
    pts = []
    for k in range(13):
        u = k / 12; pts.append(V_((base[0] + math.cos(a) * L * u, base[1] + math.sin(a) * L * u, base[2] + L * 0.55 * u - droop * u * u)))
    side = V_((-math.sin(a), math.cos(a), 0))
    for k in range(12):
        p0, p1 = pts[k], pts[k + 1]; f = bm.faces.new([bm.verts.new(p0 - side * .008), bm.verts.new(p0 + side * .008), bm.verts.new(p1 + side * .008), bm.verts.new(p1 - side * .008)]); f.material_index = mm_i
    for k in range(nleaf):
        u = 0.12 + 0.86 * k / nleaf; i0 = min(11, int(u * 12)); p = pts[i0].lerp(pts[i0 + 1], u * 12 - i0)
        for sg in (-1, 1):
            l_ = ll * math.sin(math.pi * min(1, u * 1.15)) + 0.06
            tip = p + side * sg * l_ * 0.8 + V_((math.cos(a), math.sin(a), 0)) * l_ * 0.35 + V_((0, 0, -l_ * 0.45))
            dv = (tip - p).normalized(); nn = dv.cross(V_((0, 0, 1))).normalized() * w
            f = bm.faces.new([bm.verts.new(p - nn * .3), bm.verts.new(p + nn * .3), bm.verts.new(tip + nn * .15), bm.verts.new(tip - nn * .15)]); f.material_index = mm_i
@cached
def a_areca(seed=3):
    """areca (golden cane) clump ~2.2 m: 4 ringed yellow-green canes, 5 arching pinnate fronds each"""
    P = _plantmats(); import random; R_ = random.Random(seed); b = MB(); bm = bmesh.new()
    for k in range(4):
        a = 2 * math.pi * k / 4 + R_.uniform(-.4, .4); h = R_.uniform(1.1, 1.6); top_ = (0.12 * math.cos(a), 0.12 * math.sin(a), h)
        b.rod((0.03 * math.cos(a), 0.03 * math.sin(a), 0.0), top_, 0.028, P['stem'], 8)
        for j in range(5): _frond(bm, top_, a + (j - 2) * 0.75 + R_.uniform(-.2, .2), R_.uniform(0.8, 1.1), R_.uniform(0.55, 0.8), 22, 0, R_)
    fr = bpy.data.meshes.new('areca_fronds'); bm.to_mesh(fr); bm.free(); fr.materials.append(P['palm']); fr['kit'] = 1
    return merge('Areca_foliage', [b.mesh('areca_canes'), fr])
@cached
def a_banana(seed=4):
    """banana / strelitzia clump ~2.4 m: pseudostem + 7 broad paddle leaves (curved strips with a midrib fold and a few tears)"""
    from mathutils import Vector as V_
    P = _plantmats(); import random; R_ = random.Random(seed); b = MB(); bm = bmesh.new()
    b.cyl(0, 0, 0.0, 1.3, 0.09, P['stem'], 12, r2=0.06)
    for k in range(9):
        a = 2 * math.pi * k / 9 + R_.uniform(-.2, .2); L = R_.uniform(1.2, 1.6); W = R_.uniform(0.3, 0.38); base = V_((0, 0, 1.2 + R_.uniform(0, .25)))
        d = V_((math.cos(a), math.sin(a), 0)); side = V_((-math.sin(a), math.cos(a), 0)); rows = []
        for j in range(9):
            u = j / 8; c = base + d * (0.25 + L * u) + V_((0, 0, 0.55 * u - 0.75 * u * u))
            w = W * math.sin(math.pi * min(1, 0.15 + u)) ** 0.7
            rows.append([bm.verts.new(c - side * w + V_((0, 0, -0.04))), bm.verts.new(c), bm.verts.new(c + side * w + V_((0, 0, -0.04)))])
        for j in range(8):
            for i in range(2):
                if j > 3 and R_.random() < 0.18: continue                          # wind tears
                bm.faces.new([rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]])
        b.rod((0, 0, 1.15), tuple(base + d * 0.25), 0.03, P['stem'], 6)
    lv = bpy.data.meshes.new('banana_leaves'); bm.to_mesh(lv); bm.free(); lv.materials.append(P['banana']); lv['kit'] = 1
    return merge('Banana_foliage', [b.mesh('banana_stem'), lv])
@cached
def a_shrub(seed, kind='green'):
    """low ball shrub r ~0.35 of narrow-leaf cards (green / bougainvillea / jasmine / herbs)"""
    P = _plantmats(); cd = Cards(seed); b = MB(); b.cyl(0, 0, 0.0, 0.15, 0.02, P['smooth'], 6)
    if kind == 'herb': cd.add((0, 0, 0.16), 0.2, 230, (0.05, 0.07), P['leafn'], squash=0.6)
    else: cd.add((0, 0, 0.3), 0.33, 480, (0.07, 0.1), P['leafn'], squash=0.85)
    if kind == 'bou': cd.add((0, 0, 0.33), 0.35, 170, (0.05, 0.07), P['flower'], cells=[(1, 0)])
    if kind == 'jas': cd.add((0, 0, 0.32), 0.34, 110, (0.035, 0.05), P['flower'], cells=[(0, 1)])
    return merge(f'Shrub_{kind}_{seed}_foliage', [b.mesh('shrub_stem'), cd.mesh('shrub_cards', 0.01)])

@cached
def a_lowtable(L, W, H):
    """low carved dastarkhan table L x W x H (tapchan): walnut frame top with a zellige inlay, arched aprons, square legs"""
    b = MB(); WD = XW['wd']; hx, hy = L / 2, W / 2; f = 0.06; t = 0.035
    b.box(-hx, -hy, H - t, hx, -hy + f, H, WD, 0.004); b.box(-hx, hy - f, H - t, hx, hy, H, WD, 0.004)
    b.box(-hx, -hy + f, H - t, -hx + f, hy - f, H, WD, 0.004); b.box(hx - f, -hy + f, H - t, hx, hy - f, H, WD, 0.004)
    b.box(-hx + f, -hy + f, H - t, hx - f, hy - f, H, XW['zt'])
    lg = 0.05; a = 0.03
    for sx in (-1, 1):
        for sy in (-1, 1): b.box(sx * (hx - a - lg) , sy * (hy - a - lg), 0.0, sx * (hx - a), sy * (hy - a), H - t, WD, 0.003)
    for sy in (-1, 1):
        y_ = sy * (hy - a - lg / 2)
        for q in arch_apron(-hx + a + lg, H - t - 0.12, hx - a - lg, H - t, H - t - 0.07, H - t - 0.02, 0.01, 2): b.extrude(list(q.exterior.coords)[:-1], y_ - 0.01, y_ + 0.01, XW['cv'], 'xz')
    for sx in (-1, 1):
        x_ = sx * (hx - a - lg / 2)
        for q in arch_apron(-hy + a + lg, H - t - 0.12, hy - a - lg, H - t, H - t - 0.07, H - t - 0.02, 0.01, 2): b.extrude(list(q.exterior.coords)[:-1], x_ - 0.01, x_ + 0.01, XW['cv'], 'yz')
    return b.mesh(f'Lowtable_{int(L * 100)}x{int(W * 100)}')
