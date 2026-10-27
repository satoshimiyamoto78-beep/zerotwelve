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

XW = dict(wd=mat('walnut_dark', (0.072, 0.034, 0.016), rough=0.42, noise_var=0.05), cv=tex2('carvedref_t', 'carvedref.png', 0.32, rough=0.5, bump=0.9),
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
    em = N.new('ShaderNodeMath'); em.operation = 'MULTIPLY'; em.inputs[1].default_value = 6.0; Lk.new(mk.outputs['Result'], em.inputs[0]); Lk.new(em.outputs[0], b.inputs['Emission Strength'])
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
