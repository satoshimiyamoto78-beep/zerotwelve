"""Samarkand asset library v5 — Timurid architecture for the common areas (Shah-i-Zinda / Gur-e-Amir references):
- a_sam_column: stone octagonal base, majolica tube shaft (clads the steel column), kufic bands, stepped muqarnas capital
- a_pishtaq: Gur-e-Amir style portal — bannai pylons with kufic frames and majolica panels, epigraphic band, pointed arch
  with tile spandrels and a muqarnas half-vault of niche cells, cornice
- a_frieze: epigraphic majolica band + kufic border for the building face
- gonbad(): the karbandi dome interior (imported mesh) scaled into the central dome as a closed shell
All parts are closed shells; parts of an asset meet flush."""
import math

def _oct(r, n=8, rot=math.pi / 8): return [(r * math.cos(rot + 2 * math.pi * k / n), r * math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]
def _tube(b, z0, z1, ri, ro, mm, n=32, ro2=None):
    """closed tube (annulus prism) around the steel core"""
    ro2 = ro if ro2 is None else ro2
    return b.ring(0, 0, z0, [(ri, 0.0), (ro, 0.0), (ro2, z1 - z0), (ri, z1 - z0)], mm, n)

@cached
def a_sam_column(H):
    """Samarkand column cladding around a 150 mm steel column, floor at 0, capital top at H (beam underside)"""
    b = MB(); ST = X['stone']; ri = 0.115
    # octagonal base as closed annuli around the steel: plinth, girih-tiled die, moulded cap
    for z0, z1, r, mm in ((0.0, 0.06, 0.27, ST), (0.06, 0.40, 0.23, X['girihstar']), (0.40, 0.46, 0.25, ST)):
        b.ring(0, 0, z0, [(ri, 0.0), (r, 0.0), (r, z1 - z0), (ri, z1 - z0)], mm, 8)
    zc = H - 0.5                                                                       # capital starts here
    segs = [(0.46, 0.52, 0.19, ST), (0.52, 0.64, 0.175, X['kufic']), (0.64, zc - 0.2, 0.165, X['majcobalt']), (zc - 0.2, zc - 0.08, 0.175, X['kufic']), (zc - 0.08, zc, 0.19, ST)]
    for z0, z1, r, mm in segs: _tube(b, z0, z1, ri, r, mm, 32)
    # muqarnas capital: 4 tiers of 16 faceted corbels stepping out, turquoise / girih, abacus on top
    tiers = [(0.19, 0.23, X['domeglaze']), (0.23, 0.27, X['girihstar']), (0.27, 0.31, X['domeglaze']), (0.31, 0.34, X['girihstar'])]
    z = zc
    for k, (r0, r1, mm) in enumerate(tiers):
        h = 0.1
        b.ring(0, 0, z, [(ri, 0.0), (r0, 0.0), (r1, h * 0.75), (r1, h), (ri, h)], mm, 16); z += h
    b.ring(0, 0, z, [(ri, 0.0), (0.36, 0.0), (0.36, H - z), (ri, H - z)], ST, 8)
    return b.mesh(f'Sam_column_{int(H * 1000)}')

# ---------------------------------------------------------------- PISHTAQ (Gur-e-Amir)
def _muqarnas(b, cx, R, zs, za, T=5, depth=None):
    """half-vault of niche cells over the semicircle (flat side on x = cx, curved side towards -x):
    tier t: cells on radius r_t, each a pointed-arch hood plate facing the centre; annular shelves close each tier"""
    hz = (za - zs) / T
    depth = depth or (0.92 * R / T + 0.004)                                # cells fill the whole step between tiers
    for t in range(T):
        r_out = R * (1 - t / T * 0.92); r_in = R * (1 - (t + 1) / T * 0.92); z0 = zs + t * hz; z1 = z0 + hz
        n = max(3, int(round(math.pi * r_out / 0.24)))
        for j in range(n):
            a0 = math.pi / 2 + math.pi * j / n; a1 = math.pi / 2 + math.pi * (j + 1) / n; am = (a0 + a1) / 2
            cw = 2 * r_out * math.sin((a1 - a0) / 2)
            # hood: pointed-arch outline in the cell's own (s, z) plane, extruded radially by `depth`
            outline = [(-cw / 2, 0.0), (cw / 2, 0.0), (cw / 2, hz * 0.4), (cw * 0.22, hz * 0.85), (0.0, hz), (-cw * 0.22, hz * 0.85), (-cw / 2, hz * 0.4)]
            mm = X['majcobalt'] if (j + t) % 2 else X['domeglaze']
            fs = b.extrude(outline, -depth / 2, depth / 2, mm, 'xz')
            vs = {v for f in fs for v in f.verts}
            ca, sa = math.cos(am), math.sin(am); rc = r_out - depth / 2
            for v in vs:                                                    # local (s, d, z) -> world: s along the tangent, d radial
                s_, d_, z_ = v.co.x, v.co.y, v.co.z
                v.co.x = cx + (rc - d_) * ca - s_ * sa; v.co.y = (rc - d_) * sa + s_ * ca; v.co.z = z0 + z_
        # shelf closing the tier (half annulus from r_in to r_out at the top of the tier)
        ra, rb_ = max(0.02, r_in - depth), r_out - depth                    # under the next tier's cells .. inside this tier's cells
        pts_o = [(cx + rb_ * math.cos(math.pi / 2 + math.pi * k / 16), rb_ * math.sin(math.pi / 2 + math.pi * k / 16)) for k in range(17)]
        pts_i = [(cx + ra * math.cos(math.pi / 2 + math.pi * k / 16), ra * math.sin(math.pi / 2 + math.pi * k / 16)) for k in range(17)]
        if rb_ - ra > 0.02: b.extrude(pts_o + pts_i[::-1], z1 - 0.02, z1, X['girihstar'], 'xy')
    # crown: small turquoise cap closing the top
    b.lathe(cx - 0.02, 0, za, [(0.0, 0.0), (0.1, 0.0), (0.0, 0.08)], X['domeglaze'], 16)

@cached
def a_pishtaq(W, Hp, D, zfloor=0.0, flat=False):
    """portal: opening width W (along local Y), pylons 0.7 wide, depth D (local X, +X = street face), total height Hp.
    Origin: opening centre on the pylon mid-depth at the sidewalk level.
    flat (rev. 7): slimmer lintel band and a flatter arch so the muqarnas hood clears 2.3 m over the terrace floor"""
    b = MB(); hw = W / 2; P = 0.7; xf, xr = D / 2, -D / 2; ST = X['stone']
    zl = Hp - (0.62 if flat else 0.75); za = zl - (0.06 if flat else 0.1); zs = za - (0.36 if flat else 0.7)      # lintel bottom, arch apex, springing
    for sg in (-1, 1):
        y0, y1 = sorted((sg * hw, sg * (hw + P)))
        b.box(xr, y0, 0.0, xf, y1, 0.55, ST, 0.01)                                   # stone plinth
        b.box(xr + 0.02, y0 + 0.02, 0.55, xf - 0.02, y1 - 0.02, zl, X['hazarbaf'])   # glazed-brick pylon core
        # street face: kufic frame + majolica panel with a pointed niche
        fx = xf - 0.02
        b.box(fx, y0 + 0.02, 0.55, fx + 0.03, y0 + 0.12, zl, X['kufic']); b.box(fx, y1 - 0.12, 0.55, fx + 0.03, y1 - 0.02, zl, X['kufic'])
        b.box(fx, y0 + 0.12, 0.55, fx + 0.03, y1 - 0.12, 0.65, X['kufic']); b.box(fx, y0 + 0.12, zl - 0.1, fx + 0.03, y1 - 0.12, zl, X['kufic'])
        b.box(fx, y0 + 0.12, 0.65, fx + 0.015, y1 - 0.12, zl - 0.1, X['majcobalt'])
        c = (y0 + y1) / 2; w = (y1 - y0) - 0.36
        for poly in spandrel_polys(c, w, zl - 0.75, zl - 0.25, zl - 0.12): b.extrude(poly, fx + 0.015, fx + 0.03, X['girihstar'], 'yz')
        # inner (passage) faces: girih tile dado + majolica above
        ix = sg * hw
        b.box(xr + 0.02, ix - (0.015 if sg > 0 else 0.0), max(0.55, zfloor), xf - 0.02, ix + (0.0 if sg > 0 else 0.015), zs, X['girihstar'])
    # lintel block over the opening and the pylons
    b.box(xr, -hw - P, zl, xf, hw + P, Hp - 0.35, X['bannai'])
    b.picture_box(xf, -hw - P + 0.1, zl + (0.06 if flat else 0.1), xf + 0.03, hw + P - 0.1, Hp - (0.41 if flat else 0.45), X['epigraph_uv'], '+x')
    kb_, kt_ = (0.06, 0.41) if flat else (0.1, 0.45)
    b.box(xf, -hw - P, zl, xf + 0.03, hw + P, zl + kb_, X['kufic']); b.box(xf, -hw - P, Hp - kt_, xf + 0.03, hw + P, Hp - 0.35, X['kufic'])
    b.box(xf, -hw - P, zl + kb_, xf + 0.03, -hw - P + 0.1, Hp - kt_, X['kufic']); b.box(xf, hw + P - 0.1, zl + kb_, xf + 0.03, hw + P, Hp - kt_, X['kufic'])
    # cornice: stepped stone mouldings + turquoise crenellation
    b.box(xr - 0.04, -hw - P - 0.04, Hp - 0.35, xf + 0.08, hw + P + 0.04, Hp - 0.25, ST, 0.01)
    b.box(xr - 0.08, -hw - P - 0.08, Hp - 0.25, xf + 0.12, hw + P + 0.08, Hp - 0.15, X['domeglaze'], 0.01)
    nmer = int((W + 2 * P) / 0.32)
    for k in range(nmer):
        y = -hw - P + (W + 2 * P) * (k + 0.5) / nmer
        zm = Hp - 0.15
        b.extrude([(y - 0.11, zm), (y + 0.11, zm), (y + 0.11, zm + 0.1), (y, zm + 0.15), (y - 0.11, zm + 0.1)], xf - 0.1, xf + 0.06, X['domeglaze'], 'yz')
    # arch: spandrels in the street plane + edge roll, muqarnas half-vault behind
    for poly in spandrel_polys(0.0, W, zs, za, zl): b.extrude(poly, xf - 0.12, xf, X['majcobalt'], 'yz')
    L_ = arch_left(0.0, W, zs, za, 12); R_ = [(-u, z) for u, z in L_][::-1]
    for (u0, z0), (u1, z1) in zip(L_ + R_[1:], (L_ + R_[1:])[1:]):
        b.rod((xf + 0.005, u0, z0), (xf + 0.005, u1, z1), 0.035, X['domeglaze'], 10)
    _muqarnas(b, xf - 0.12, hw - 0.02, zs, za + 0.05, 3 if flat else 6)
    b.box(xr, -hw, zs, xr + 0.12, hw, zl, X['girihstar'])                            # back tympanum over the passage
    return b.mesh(f'Pishtaq_{int(W * 1000)}')

@cached
def a_frieze(L, Hf=0.58):
    """building-face frieze, local x = depth (0..0.03, +x = room side), y 0..L along the facade, z 0..Hf"""
    b = MB()
    b.box(0.0, 0.0, 0.0, 0.03, L, 0.07, X['kufic']); b.box(0.0, 0.0, Hf - 0.07, 0.03, L, Hf, X['kufic'])
    n = max(1, int(round(L / 1.6)))
    for k in range(n):
        b.picture_box(0.0, L * k / n, 0.07, 0.025, L * (k + 1) / n, Hf - 0.07, X['epigraph_uv'], '+x')
    return b.mesh(f'Frieze_{int(L * 1000)}')

def gonbad(cx, cy, z_base, r_base, path_obj, coll_name='Domes'):
    """import the karbandi dome surface, scale it to r_base, give it 20 mm thickness outwards -> closed shell"""
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=path_obj)
    o = [x for x in bpy.data.objects if x not in before][0]
    bpy.context.view_layer.update()
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    nm = [e for e in bm.edges if len(e.link_faces) > 2]                     # 5 edges where two rib sheets touch: split into separate sheets
    if nm:
        vs_ = {v for e in nm for v in e.verts}; bmesh.ops.split_edges(bm, edges=nm)
        from collections import defaultdict
        grp = defaultdict(list)
        for v in bm.verts: grp[(round(v.co.x, 4), round(v.co.y, 4), round(v.co.z, 4))].append(v)
        for vl in grp.values():
            if len(vl) < 2: continue
            for v in vl:                                                    # pull each copy 0.6 mm (after scaling) into its own sheet
                c_ = sum((f.calc_center_median() for f in v.link_faces), Vector()) / max(1, len(v.link_faces))
                v.co += (c_ - v.co).normalized() * 0.005
    zs = [v.co.z for v in bm.verts]; z0 = min(zs)
    rb = max(v.co.xy.length for v in bm.verts if v.co.z < z0 + 0.3); s = r_base / rb
    for v in bm.verts: v.co = Vector(((v.co.x) * s + cx, (v.co.y) * s + cy, (v.co.z - z0) * s + z_base))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    c = Vector((cx, cy, z_base))
    if sum(f.normal.dot(f.calc_center_median() - c) for f in bm.faces) > 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)     # visible side faces inward / down
    faces = list(bm.faces)
    bmesh.ops.solidify(bm, geom=faces, thickness=0.02)                      # grows opposite to the normal = outwards
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('dome_karbandi'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    mm = uvmat('gonbad_uv', 'gonbad.jpg', rough=0.35, sheen=0.0); me.materials.append(mm); me['kit'] = 1
    bpy.data.objects.remove(o)
    ob = bpy.data.objects.new('dome_karbandi_C', me); coll(coll_name).objects.link(ob)
    return ob
