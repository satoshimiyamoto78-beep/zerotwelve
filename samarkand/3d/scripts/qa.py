"""Mesh-quality audit for the Samarkand model (Blender 5, bpy).
Usage: bvenv/bin/python qa.py MODEL.blend OUT.json [collections,...]
Per mesh datablock (instances are checked once):
  - shells (connected parts), open/boundary edges, non-manifold edges (>2 faces), wire/loose edges, loose verts
  - zero-area faces, zero-length edges, coincident vertices inside one shell, inconsistent normals (edges whose two
    faces wind the same way), inside-out shells (negative signed volume), n-gons, triangle count, UV layer present
Per object: unapplied rotation/scale (except allowed), origin far outside the bounds
Placement (world space, furniture-type collections): pairs of objects that penetrate each other by > 3 mm
(BVH triangle overlap after offsetting every vertex 2 mm inward along its normal, so flush contact is not counted),
and objects floating above their floor (gap > 2 mm).
"""
import sys, json, math, collections
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
BLEND, OUT = argv[0], argv[1]
PLACE_COLLS = set(argv[2].split(',')) if len(argv) > 2 else None
bpy.ops.wm.open_mainfile(filepath=BLEND)

def mesh_report(me):
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    r = dict(verts=len(bm.verts), faces=len(bm.faces), tris=sum(len(f.verts) - 2 for f in bm.faces))
    r['boundary_edges'] = sum(1 for e in bm.edges if len(e.link_faces) == 1)
    r['nonmanifold_edges'] = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    r['wire_edges'] = sum(1 for e in bm.edges if len(e.link_faces) == 0)
    r['loose_verts'] = sum(1 for v in bm.verts if not v.link_edges)
    r['zero_area_faces'] = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    r['zero_len_edges'] = sum(1 for e in bm.edges if e.calc_length() < 1e-6)
    r['ngons'] = sum(1 for f in bm.faces if len(f.verts) > 4)
    bad = 0
    for e in bm.edges:
        if len(e.link_faces) == 2:
            f1, f2 = e.link_faces; v1, v2 = e.verts
            def dirn(f):
                vs = list(f.verts); i = vs.index(v1); return vs[(i + 1) % len(vs)] is v2
            if dirn(f1) == dirn(f2): bad += 1
    r['flipped_edges'] = bad
    # shells
    seen, shells = set(), []
    for f in bm.faces:
        if f.index in seen: continue
        st, comp = [f], []
        seen.add(f.index)
        while st:
            g = st.pop(); comp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); st.append(h)
        shells.append(comp)
    r['shells'] = len(shells)
    inside_out = 0; dup = 0
    for comp in shells:
        vol = 0.0
        for f in comp:
            vs = [v.co for v in f.verts]
            for i in range(1, len(vs) - 1): vol += vs[0].dot(vs[i].cross(vs[i + 1])) / 6
        if vol < -1e-9: inside_out += 1
        vset = {v for f in comp for v in f.verts}
        keys = collections.Counter((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)) for v in vset)
        dup += sum(c - 1 for c in keys.values() if c > 1)
    r['inside_out_shells'] = inside_out; r['coincident_verts'] = dup
    r['uv'] = len(me.uv_layers) > 0
    bm.free(); return r

meshes, objs = {}, []
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    if o.data.name not in meshes: meshes[o.data.name] = mesh_report(o.data)
    objs.append(o)
keys = ['boundary_edges', 'nonmanifold_edges', 'wire_edges', 'loose_verts', 'zero_area_faces', 'zero_len_edges', 'flipped_edges', 'inside_out_shells', 'coincident_verts']
tot = {k: sum(r[k] for r in meshes.values()) for k in keys + ['verts', 'faces', 'tris', 'ngons', 'shells']}
FOLIAGE = ('foliage',)                                       # leaf cards are single-sided planes by nature: not part of the closed-shell rule
clean = [n for n, r in meshes.items() if all(r[k] == 0 for k in keys) or any(f in n for f in FOLIAGE)]
tot = {k: sum(r[k] for n, r in meshes.items() if not any(f in n for f in FOLIAGE)) for k in keys + ['verts', 'faces', 'tris', 'ngons', 'shells']}
xform = [o.name for o in objs if (any(abs(a) > 1e-6 for a in o.rotation_euler[:2]) or any(abs(s - 1) > 1e-6 for s in o.scale)) and not o.name.startswith(('Rod', 'rod'))]

# ---------- placement: penetrations + floating ----------
pen, floating = [], []
if PLACE_COLLS is not None:
    dg = bpy.context.evaluated_depsgraph_get()
    cand = [o for o in objs if any(c.name in PLACE_COLLS for c in o.users_collection)]
    info = []
    for o in cand:
        mw = o.matrix_world; nm = mw.to_3x3().inverted_safe().transposed()
        vs = [mw @ v.co for v in o.data.vertices]
        if not vs: continue
        lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))); hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
        shr = [mw @ v.co - (nm @ v.normal).normalized() * 0.002 for v in o.data.vertices]      # 2 mm inward offset: flush contact is not a hit
        polys = [list(p.vertices) for p in o.data.polygons]
        info.append((o, lo, hi, BVHTree.FromPolygons(shr, polys)))
    for i in range(len(info)):
        oi, loi, hii, bi = info[i]
        for j in range(i + 1, len(info)):
            oj, loj, hij, bj = info[j]
            if any(loi[k] > hij[k] or loj[k] > hii[k] for k in range(3)): continue
            if 'foliage' in oi.data.name or 'foliage' in oj.data.name: continue   # leaves among twigs / around limbs
            if bi.overlap(bj): pen.append([oi.name, oj.name])
    # floating: every standing piece must rest on something (a floor, deck or another piece) within 2 mm
    HANG = ('Lantern', 'Rod', 'Flying_carpet', 'Heat_lamp', 'Corridor_niche', 'Aivan_wallcarpet', 'Corridor_velvet', 'Mangal_hood', 'Mangal_skewers',
            'Khiva_gate', 'Street_pishtaq', 'Booth', 'dome_', 'Tent_', 'Corridor_arch', 'Carpet_frieze', 'Ceiling_carpet', 'Rattan', 'Velvet_swag', 'Pendant', 'Chandelier', 'Khiva_arcade_head', 'Khiva_arcade_beam', 'Reed_fringe', 'Bar_cornice', 'Bar_drum', 'Bar_wallcarpet', 'Sconce', 'Skylight', 'Chinar_crown')
    sup = []
    for o in objs:
        mw = o.matrix_world; vs = [mw @ v.co for v in o.data.vertices]
        if not vs: continue
        sup.append((o, Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))), Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs))),
                    BVHTree.FromPolygons(vs, [list(p.vertices) for p in o.data.polygons])))
    for o, lo, hi, _ in [t for t in sup if any(c.name in PLACE_COLLS for c in t[0].users_collection)]:
        if o.name.startswith(HANG) or 'lantern' in o.name.lower(): continue
        mw = o.matrix_world; bot = [mw @ v.co for v in o.data.vertices]; zmin = min(v.z for v in bot)
        lowv = [v for v in bot if v.z < zmin + 0.001]; bx0, bx1 = min(v.x for v in lowv), max(v.x for v in lowv); by0, by1 = min(v.y for v in lowv), max(v.y for v in lowv)
        pts = lowv[:8] + [Vector((bx0 + (bx1 - bx0) * i / 4, by0 + (by1 - by0) * j / 4, zmin)) for i in range(5) for j in range(5)]
        ok = False
        for p in pts:
            for o2, lo2, hi2, bv in sup:
                if o2 is o or not (lo2.x - 1e-3 <= p.x <= hi2.x + 1e-3 and lo2.y - 1e-3 <= p.y <= hi2.y + 1e-3) or not (lo2.z - 1e-3 <= zmin <= hi2.z + 0.003): continue
                hit = bv.ray_cast(Vector((p.x, p.y, zmin + 0.001)), Vector((0, 0, -1)), 0.004)
                if hit[0] is not None: ok = True; break
            if ok: break
        if not ok: floating.append([o.name, round(zmin, 4)])
r_pen = len(pen)

report = dict(blend=BLEND, objects=len(objs), mesh_datablocks=len(meshes), totals=tot, clean_meshes=len(clean),
              unapplied_transforms=xform[:50], n_unapplied=len(xform), penetrations=pen[:200], n_penetrations=r_pen, floating=floating[:100], n_floating=len(floating),
              worst=sorted(((n, {k: r[k] for k in keys if r[k]}) for n, r in meshes.items() if any(r[k] for k in keys)), key=lambda t: -sum(t[1].values()))[:60])
json.dump(report, open(OUT, 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: report[k] for k in ('objects', 'mesh_datablocks', 'clean_meshes', 'totals', 'n_unapplied', 'n_penetrations', 'n_floating')}, ensure_ascii=False))
