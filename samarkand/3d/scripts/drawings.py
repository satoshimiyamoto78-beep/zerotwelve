"""Line drawings straight from the 3D model (no Freestyle in this Blender build):
for each view — orthographic direction, optional section plane, object filter —
  * CUT: exact section polylines (bmesh bisect of every mesh with the section plane)
  * VISIBLE: feature edges (boundary, crease > 28 deg) + silhouette edges of the geometry behind the plane,
    sampled and ray-tested against the clipped scene (hidden-line removal)
Output: JSON {view: {u_axis, v_axis, cut: [[(u, v), ...]], vis: [[(u, v), (u, v)], ...], bbox}} in metres (view plane coords).
Usage: bvenv/bin/python r3d/drawings.py MODEL.blend VIEWS.json OUT.json"""
import sys, json, math, bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BLEND, VIEWS, OUT = sys.argv[1:4]
bpy.ops.wm.open_mainfile(filepath=BLEND)
views = json.load(open(VIEWS))
CREASE = math.radians(28)

def pick(spec):
    """spec: {'prefix': [...], 'coll': [...], 'exclude': [...], 'box': [x0, y0, z0, x1, y1, z1]}"""
    out = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render: continue
        ok = any(o.name.startswith(p) for p in spec.get('prefix', [])) or any(c.name in spec.get('coll', []) for c in o.users_collection)
        if not ok or any(o.name.startswith(p) for p in spec.get('exclude', [])): continue
        if 'box' in spec:
            x0, y0, z0, x1, y1, z1 = spec['box']; mw = o.matrix_world
            cs = [mw @ Vector(c) for c in o.bound_box]
            if max(c.x for c in cs) < x0 or min(c.x for c in cs) > x1 or max(c.y for c in cs) < y0 or min(c.y for c in cs) > y1 or max(c.z for c in cs) < z0 or min(c.z for c in cs) > z1: continue
        out.append(o)
    return out

def world_bm(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    return bm

for name, V in views.items():
    d = Vector(V['dir']).normalized()                      # viewing direction (from the viewer into the scene)
    up = Vector(V.get('up', (0, 0, 1)))
    u_ax = d.cross(up).normalized() if abs(d.dot(up)) < 0.99 else Vector((1, 0, 0)); v_ax = u_ax.cross(d).normalized()
    if V.get('flip_u'): u_ax = -u_ax
    P = lambda p: (round(p.dot(u_ax), 5), round(p.dot(v_ax), 5))
    plane = V.get('section')                               # {'co': [...], 'no': [...]} keep the side the normal points to (= away from the viewer)
    objs = pick(V['objects'])
    cut, vis, tris_all, feats = [], [], [], []
    for o in objs:
        bm = world_bm(o)
        if plane:
            co, no = Vector(plane['co']), Vector(plane['no']).normalized()
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            r = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=co, plane_no=no, clear_inner=True)
            cut_edges = [e for e in r['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
            # chain the cut edges into polylines
            from collections import defaultdict
            adj = defaultdict(list)
            for e in cut_edges: a, b = e.verts; adj[a].append(b); adj[b].append(a)
            seen = set()
            for e in cut_edges:
                a, b = e.verts
                if (a, b) in seen or (b, a) in seen: continue
                line = [a, b]; seen.add((a, b))
                for end in (0, 1):
                    while True:
                        cur = line[-1] if end == 0 else line[0]; prev = line[-2] if end == 0 else line[1]
                        nxt = [w for w in adj[cur] if w is not prev and (cur, w) not in seen and (w, cur) not in seen]
                        if not nxt: break
                        w = nxt[0]; seen.add((cur, w))
                        if end == 0: line.append(w)
                        else: line.insert(0, w)
                        if w is line[0 if end == 0 else -1]: break
                cut.append([P(v.co) for v in line])
        bm.faces.ensure_lookup_table()
        base = len(tris_all)
        for f in bm.faces: tris_all.append([v.co.copy() for v in f.verts])
        for e in bm.edges:
            lf = e.link_faces
            if len(lf) != 2: feats.append((e.verts[0].co.copy(), e.verts[1].co.copy())); continue
            n1, n2 = lf[0].normal, lf[1].normal
            if n1.angle(n2, 0) > CREASE or (n1.dot(d) > 0) != (n2.dot(d) > 0):          # crease or silhouette
                feats.append((e.verts[0].co.copy(), e.verts[1].co.copy()))
        bm.free()
    if not tris_all: print(name, 'EMPTY'); continue
    verts, polys = [], []
    for t in tris_all:
        polys.append(list(range(len(verts), len(verts) + len(t)))); verts.extend(t)
    tree = BVHTree.FromPolygons(verts, polys)
    step = V.get('step', 0.01)
    for a, b in feats:
        L = (b - a).length
        if L < 1e-6: continue
        n = max(1, int(L / step)); run = None
        for k in range(n + 1):
            p = a + (b - a) * (k / n)
            h = tree.ray_cast(p - d * 2e-4, -d)
            visible = h[0] is None
            if visible and run is None: run = p
            if (not visible or k == n) and run is not None:
                q = p if visible else a + (b - a) * ((k - 0.5) / n)
                if (q - run).length > 1e-4: vis.append([P(run), P(q)])
                run = None
    pts = [c for pl in cut for c in pl] + [c for s in vis for c in s]
    bb = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)] if pts else [0, 0, 0, 0]
    V.update(cut=cut, vis=vis, bbox=bb, u_axis=list(u_ax), v_axis=list(v_ax))
    print(name, 'objects', len(objs), 'cut', len(cut), 'vis', len(vis), 'bbox', [round(x, 2) for x in bb])
json.dump(views, open(OUT, 'w'))
