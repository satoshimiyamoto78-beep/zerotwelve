"""rev. 10.5 (owner: 'cushions everywhere must be real cushions — now they look like cheap square boxes'):
pillow(): a sewn cushion — the filling crowns in the middle and pinches to the seam (welt), piping cord on the seam,
optional button tufting, smoothed; used for every settee (aivan + booths), every carved chair, the majlis floor cushions and poufs."""
import bmesh as _bmesh
_UVC = {}
def uvcopy(mm):
    """cushion fabric: the material's image (rug / ikat / suzani photo) on the cushion UV, matte woven finish, soft dark sheen
    (no light facing mix -> no white rims on the rolled seams)"""
    if mm is None or not mm.use_nodes: return mm
    if mm.name in _UVC: return _UVC[mm.name]
    img = next((n.image for n in mm.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None)
    if img is None: _UVC[mm.name] = mm; return mm
    m2 = bpy.data.materials.new(mm.name + '_cush'); m2.use_nodes = True; nt = m2.node_tree; N, Lk = nt.nodes, nt.links
    bs = N.get('Principled BSDF'); uv = N.new('ShaderNodeUVMap'); uv.uv_map = 'UVMap'
    it = N.new('ShaderNodeTexImage'); it.image = img; it.interpolation = 'Cubic'; Lk.new(uv.outputs['UV'], it.inputs['Vector'])
    Lk.new(it.outputs['Color'], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = 0.88
    for k_, v_ in (('Sheen Weight', 0.25), ('Sheen Roughness', 0.6)):
        if k_ in bs.inputs: bs.inputs[k_].default_value = v_
    if 'Sheen Tint' in bs.inputs:
        try: bs.inputs['Sheen Tint'].default_value = (0.35, 0.2, 0.18, 1)
        except Exception: pass
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.15; bump.inputs['Distance'].default_value = 0.001
    Lk.new(it.outputs['Color'], bump.inputs['Height']); Lk.new(bump.outputs['Normal'], bs.inputs['Normal'])
    _UVC[mm.name] = m2; return m2
def pillow(name, w, d, h, mm, soft=0.5, pipe=None, buttons=(0, 0), upright=False, tilt=0.0, cuts=7):
    """cushion w (x) x d (y) x h (z), centred at the origin; soft 0 = box cushion, 1 = throw pillow; upright: thickness along y"""
    bm = _bmesh.new(); _bmesh.ops.create_cube(bm, size=1.0)
    _bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    bm.normal_update(); uvl = bm.loops.layers.uv.new('UVMap')                                    # each face shows the whole rug (medallion centred)
    for f in bm.faces:
        n_ = f.normal; ax = max(range(3), key=lambda i: abs(n_[i])); a_, b_ = [i for i in range(3) if i != ax]
        side = ax != 2                                                       # side welts: a narrow strip from the rug field, no photo border
        dims = (w, d, h); tsz = UVSIZE.get(mm.name)
        for lp in f.loops:
            uu, vv_ = lp.vert.co[a_] + 0.5, lp.vert.co[b_] + 0.5
            lp[uvl].uv = (0.12 + 0.76 * uu, 0.45 + 0.1 * vv_) if side else (0.1 + 0.8 * uu, 0.1 + 0.8 * vv_)
    kmin = 1.0 - soft * 0.7
    bx, by = buttons
    for v in bm.verts:
        u, vv, t = v.co.x * 2, v.co.y * 2, v.co.z * 2
        r = (1 - abs(u) ** 5) * (1 - abs(vv) ** 5)
        t2 = t * (kmin + (1 - kmin) * r)                                     # thickness pinches to the seam
        g = 1 + 0.04 * soft * (1 - t * t)                                    # the seam rolls out a little
        x, y, z = u * w / 2 * g, vv * d / 2 * g, t2 * h / 2
        if bx and abs(t) > 0.99:                                             # button dimples on both faces
            for i in range(bx):
                for j in range(by):
                    cx = -w / 2 + w * (i + 0.5) / bx; cy = -d / 2 + d * (j + 0.5) / by
                    dd = math.hypot(x - cx, y - cy)
                    if dd < 0.05: z -= math.copysign(0.018 * (1 - dd / 0.05) ** 2 * h / 0.12, t)
        v.co = Vector((x, y, z))
    mm = uvcopy(mm)
    me = bpy.data.meshes.new(name + '_raw'); bm.to_mesh(me); bm.free(); me.materials.append(mm)
    me = soften(me, 1)
    parts = [me]
    if pipe is not None or bx:
        b = MB()
        if pipe is not None:                                                 # piping cord round the seam
            hw, hd = w / 2 * (1 + 0.04 * soft) - 0.004, d / 2 * (1 + 0.04 * soft) - 0.004; cr = 0.035
            pts = []
            for (cx, cy, a0) in ((hw - cr, hd - cr, 0), (-hw + cr, hd - cr, 90), (-hw + cr, -hd + cr, 180), (hw - cr, -hd + cr, 270)):
                for k in range(5): a = math.radians(a0 + 22.5 * k); pts.append((cx + cr * math.cos(a), cy + cr * math.sin(a), 0.0))
            for p0, p1 in zip(pts, pts[1:] + pts[:1]): b.rod(p0, p1, 0.0045, pipe, 6)
        for i in range(bx):
            for j in range(by):
                cx = -w / 2 + w * (i + 0.5) / bx; cy = -d / 2 + d * (j + 0.5) / by
                for s in (-1, 1):
                    zf = s * (h / 2 - 0.018 * h / 0.12); b.lathe(cx, cy, zf - 0.004 if s > 0 else zf - 0.002, [(0.0, 0.0), (0.009, 0.0), (0.009, 0.004), (0.0, 0.006)], pipe or mm, 10)
        parts.append(b.mesh(name + '_trim'))
    out = merge(name, parts)
    if upright or tilt:
        for v in out.vertices:
            x, y, z = v.co
            if upright: y, z = -z, y                                          # thickness along y, height along z
            if tilt: y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
            v.co = Vector((x, y, z))
    return out
def at(me, dx, dy, dz, name):
    m2 = me.copy(); m2.name = name
    for v in m2.vertices: v.co = v.co + Vector((dx, dy, dz))
    return m2
PIPE = m['brass'] if False else mat('piping_wine', (0.25, 0.04, 0.05), rough=0.6)

# ---------------------------------------------------------------- settees (new cushions; the frame is kept)
_SETTEE_CACHE = {}
def no_soft(me, name):
    bm = _bmesh.new(); bm.from_mesh(me); soft_ = {XW['k1'], XW['k2']}
    _bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index < len(me.materials) and me.materials[f.material_index] in soft_], context='FACES')
    out = bpy.data.meshes.new(name); bm.to_mesh(out); bm.free()
    for mm in me.materials: out.materials.append(mm)
    return out
def settee_soft(L, n, old):
    key = f'Settee2_{int(L * 100)}_{n}'
    if key in bpy.data.meshes: return bpy.data.meshes[key]
    frame = no_soft(old, '_sf')
    ix = L / 2 - 0.05; hw = (2 * ix - 0.012 * (n - 1)) / n / 2; parts = [frame]
    for k in range(n):
        cx = -ix + hw + k * (2 * hw + 0.012); kil = XW['k1' if k % 2 else 'k2']
        parts.append(at(pillow(f'_seat_{key}_{k}', 2 * hw - 0.006, 0.43, 0.10, kil, soft=0.35, pipe=PIPE), cx, 0.0, 0.47, f'_s{key}{k}'))
        parts.append(at(pillow(f'_back_{key}_{k}', 2 * hw - 0.05, 0.25, 0.12, XW['k2' if k % 2 else 'k1'], soft=0.85, pipe=PIPE, buttons=(2, 1), upright=True, tilt=0.15), cx, -0.14, 0.645, f'_b{key}{k}'))
    return merge(key, parts)
ns = 0
for o_ in [o for o in bpy.data.objects if o.type == 'MESH' and 'settee' in o.name.lower()]:
    nm_ = o_.data.name                                                       # Settee_<L>_<n>
    p_ = nm_.split('_')
    if len(p_) < 3 or not p_[1].isdigit(): continue
    L_, n_ = int(p_[1]) / 100, int(p_[2].split('.')[0]) if len(p_) > 2 and p_[2].split('.')[0].isdigit() else 2
    o_.data = settee_soft(L_, n_, o_.data); ns += 1
# ---------------------------------------------------------------- carved chairs
nc = 0
for kil in ('k1', 'k2'):
    old_ = next((o.data for o in bpy.data.objects if o.type == 'MESH' and o.data.name.startswith(f'Carvedchair_{kil}')), None)
    if not old_: continue
    fr_ = no_soft(old_, '_cf')
    seat = at(pillow(f'_chseat_{kil}', 0.448, 0.42, 0.095, XW[kil], soft=0.35, pipe=PIPE), 0.0, 0.0, 0.468, f'_cs{kil}')
    back = at(pillow(f'_chback_{kil}', 0.39, 0.2, 0.11, XW['k2' if kil == 'k1' else 'k1'], soft=0.85, pipe=PIPE, buttons=(1, 1), upright=True, tilt=0.15), 0.0, -0.145, 0.625, f'_cb{kil}')
    newm = merge(f'Carvedchair2_{kil}', [fr_, seat, back])
    for o_ in [o for o in bpy.data.objects if o.type == 'MESH' and o.data.name.startswith(f'Carvedchair_{kil}')]: o_.data = newm; nc += 1
# ---------------------------------------------------------------- helpers: keep the hard (timber) part of an old mesh
def hard_only(me, how, name):
    """how 'low': keep the material of the lowest face (timber legs / plinth); a float: keep materials that never rise above that z"""
    bm = _bmesh.new(); bm.from_mesh(me)
    if isinstance(how, tuple):                                               # ('z', zc): keep the faces below zc (plinth)
        _bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().z > how[1]], context='FACES')
        out = bpy.data.meshes.new(name); bm.to_mesh(out); bm.free()
        for mm in me.materials: out.materials.append(mm)
        return out
    if how == 'low':
        f0 = min(bm.faces, key=lambda f: f.calc_center_median().z); keep = {f0.material_index}
    else:
        mz = {}
        for f in bm.faces: mz[f.material_index] = max(mz.get(f.material_index, -9), max(v.co.z for v in f.verts))
        keep = {i for i, z in mz.items() if z <= how}
    _bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in keep], context='FACES')
    out = bpy.data.meshes.new(name); bm.to_mesh(out); bm.free()
    for mm in me.materials: out.materials.append(mm)
    return out
def swap(prefix, build):
    done = {}; n = 0
    for o_ in [o for o in bpy.data.objects if o.type == 'MESH' and o.data.name.startswith(prefix) and not o.data.name.startswith(prefix + 'R')]:
        k = o_.data.name.split('.')[0]
        if k not in done: done[k] = build(o_.data)
        o_.data = done[k]; n += 1
    return n
VW = X['velvet_wine']; IK = m['ikat']; SZ = m['suzani']; KIL_ = X82['majlis']
# ---------------------------------------------------------------- majlis floor cushions (tufted mattress) + poufs (drum, button)
def b_floor(me):
    lo, hi = me_bb(me); w, d, h = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]
    return at(pillow('_fc', w, d, h, me.materials[0], soft=0.45, pipe=PIPE, buttons=(max(1, round(w / 0.22)), max(1, round(d / 0.22)))), (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2] + h / 2, me.name.split('.')[0] + 'R')
def b_pouf(me):
    lo, hi = me_bb(me); w, h = hi[0] - lo[0], hi[2] - lo[2]
    return at(pillow('_pf', w * 0.98, w * 0.98, h, me.materials[0], soft=0.3, pipe=PIPE, buttons=(1, 1)), 0, 0, h / 2, me.name.split('.')[0] + 'R')
def me_bb(me):
    vs = me.vertices; return [min(v.co[i] for v in vs) for i in range(3)], [max(v.co[i] for v in vs) for i in range(3)]
nfc = swap('Floor_cushion_', b_floor); npf = swap('Kilim_pouf_', b_pouf)
# ---------------------------------------------------------------- majlis benches: walnut frame kept, piped seat + 3 back pillows
def b_bench(me):
    lo, hi = me_bb(me); hl, hw = hi[0], hi[1]
    parts = [hard_only(me, 'low', '_bh')]
    parts.append(at(pillow('_bs', 2 * hl - 0.09, 2 * hw - 0.09, 0.09, X['velvet'], soft=0.3, pipe=PIPE), 0, 0.015, 0.515, '_bs2'))
    for k, cx in enumerate((-hl * 0.55, 0.0, hl * 0.55)):
        parts.append(at(pillow('_bp', 0.42, 0.38, 0.12, KIL_ if k != 1 else VW, soft=0.95, pipe=PIPE if k == 1 else None, upright=True, tilt=0.18), cx, -hw + 0.15, 0.75, '_bp2'))
    return merge(me.name.split('.')[0] + 'R', parts)
nbe = swap('Majlis_bench_', b_bench)
# ---------------------------------------------------------------- tent majlis seats: plinth kept, piped mattress, buttoned back cushions, lumbar pillows
def b_majlis(me):
    lo, hi = me_bb(me); L, Dp = hi[0], hi[1]
    parts = [hard_only(me, ('z', 0.145), '_mh')]
    parts.append(at(pillow('_mm', L - 0.035, Dp - 0.03, 0.16, KIL_, soft=0.25, pipe=PIPE), L / 2, Dp / 2, 0.22, '_mm2'))
    n = max(1, int(round((L - 0.04) / 0.62))); w = (L - 0.04) / n
    for k in range(n):
        cx = 0.02 + (k + 0.5) * w
        parts.append(at(pillow('_mb', w - 0.03, 0.46, 0.17, KIL_, soft=0.8, pipe=PIPE, buttons=(2, 2), upright=True, tilt=0.12), cx, 0.14, 0.535, '_mb2'))
        parts.append(at(pillow('_ml', w - 0.26, 0.28, 0.12, IK, soft=1.0, upright=True, tilt=0.2), cx, 0.25, 0.44, '_ml2'))
    return merge(me.name.split('.')[0] + 'R', parts)
nmj = swap('Majlis_', lambda me: b_majlis(me) if 'x' in me.name else me)
# ---------------------------------------------------------------- tapchan: kurpacha mattresses + pillows + bolsters
def b_tapchan(me):
    W, Dp = 2.0, 2.2
    parts = [hard_only(me, 0.0065, '_th')]
    for (x0, y0, x1, y1) in ((0.07, 0.125, 0.6, Dp - 0.125), (0.6, 0.08, W - 0.125, 0.6), (0.6, Dp - 0.6, W - 0.125, Dp - 0.1)):
        parts.append(at(pillow('_tk', x1 - x0 - 0.008, y1 - y0 - 0.008, 0.1, VW, soft=0.25, pipe=PIPE, buttons=(max(1, round((x1 - x0) / 0.3)), max(1, round((y1 - y0) / 0.3)))), (x0 + x1) / 2, (y0 + y1) / 2, 0.05, '_tk2'))
    for (x0, y0, x1, y1), mm in (((0.07, 0.5, 0.21, 0.94), IK), ((0.07, 1.26, 0.21, 1.7), SZ), ((0.7, 0.08, 1.14, 0.22), SZ),
                                 ((1.3, 0.08, 1.74, 0.22), IK), ((0.7, Dp - 0.24, 1.14, Dp - 0.1), IK), ((1.3, Dp - 0.24, 1.74, Dp - 0.1), SZ)):
        along_x = (x1 - x0) > (y1 - y0); w_ = max(x1 - x0, y1 - y0)
        pl = pillow('_tp', w_, 0.38, 0.14, mm, soft=1.0, pipe=PIPE, upright=True, tilt=0.2)
        if not along_x:
            for v in pl.vertices: v.co = Vector((v.co.y, -v.co.x, v.co.z))
        if (along_x and y0 > 1) or (not along_x and x0 > 1): 
            for v in pl.vertices: v.co = Vector((-v.co.x, -v.co.y, v.co.z))
        sh = 0.05; dx_, dy_ = (0, sh if y0 < 1 else -sh) if along_x else (sh, 0)
        parts.append(at(pl, (x0 + x1) / 2 + dx_, (y0 + y1) / 2 + dy_, 0.29, '_tp2'))
    b = MB()
    for yy in (0.24, Dp - 0.26):
        b.rod((0.14, yy, 0.19), (0.5, yy, 0.19), 0.09, IK, 20)
    parts.append(soften(b.mesh('_tb'), 1))
    return merge('Tapchan_softR', parts)
ntp = swap('Tapchan_soft', b_tapchan)
print('rev 10.5 cushions: settees', ns, 'chairs', nc, 'floor', nfc, 'poufs', npf, 'benches', nbe, 'tent majlis', nmj, 'tapchan', ntp)
