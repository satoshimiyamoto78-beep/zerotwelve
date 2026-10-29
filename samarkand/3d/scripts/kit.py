"""Samarkand asset kit (Blender 5, bmesh). Every part is a CLOSED, outward-facing shell; parts of one asset meet flush
(shared planes, no penetration); hard edges get a small chamfer; every mesh has a UV map (box UV at real-world texel
density, or a 0..1 picture UV for carpets / panels); origin at the base centre (furniture) or a stated anchor.
Assets are mesh datablocks, placed as linked instances (one mesh, many objects).
Executed inside base3d's namespace (needs bpy, bmesh, math, coll)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

UVSIZE = {}            # material name -> texture tile size in metres (box UV); filled by register_uv_size()
def register_uv_size(mm, size): UVSIZE[mm.name] = size

class MB:
    """mesh builder of closed parts"""
    def __init__(s):
        s.bm = bmesh.new(); s.uv = s.bm.loops.layers.uv.new('UVMap'); s.mats = []; s.fixed = set(); s.smooth = set()
    def mi(s, mm):
        if mm not in s.mats: s.mats.append(mm)
        return s.mats.index(mm)
    # ---- low level ----
    def _faces(s, vs, rings_closed, i):
        pass
    def _poly_ccw(s, poly):
        a = sum(poly[k][0] * poly[(k + 1) % len(poly)][1] - poly[(k + 1) % len(poly)][0] * poly[k][1] for k in range(len(poly)))
        return poly if a > 0 else list(reversed(poly))
    def extrude(s, poly, a0, a1, mm, plane='xy', bevel=0.0, fixed_uv=None):
        """closed prism: 2D polygon in `plane` extruded along the remaining axis from a0 to a1"""
        poly = s._poly_ccw([p for k, p in enumerate(poly) if k == 0 or (abs(p[0] - poly[k - 1][0]) + abs(p[1] - poly[k - 1][1])) > 1e-7])
        if abs(poly[0][0] - poly[-1][0]) + abs(poly[0][1] - poly[-1][1]) < 1e-7: poly = poly[:-1]
        def V(u, v, w):
            return {'xy': (u, v, w), 'xz': (u, w, v), 'yz': (w, u, v)}[plane]
        lo, hi = min(a0, a1), max(a0, a1)
        A = [s.bm.verts.new(V(u, v, lo)) for u, v in poly]; B = [s.bm.verts.new(V(u, v, hi)) for u, v in poly]
        i = s.mi(mm); n = len(poly); fs = [s.bm.faces.new(list(reversed(A))), s.bm.faces.new(B)]
        fs += [s.bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k])) for k in range(n)]
        for f in fs: f.material_index = i
        bmesh.ops.recalc_face_normals(s.bm, faces=fs)
        if bevel > 0:
            ed = list({e for f in fs for e in f.edges})
            bmesh.ops.bevel(s.bm, geom=ed + A + B, offset=bevel, offset_type='OFFSET', segments=1, profile=0.5, affect='EDGES', clamp_overlap=True)
        return fs
    def box(s, x0, y0, z0, x1, y1, z1, mm, bevel=0.0):
        x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
        return s.extrude([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mm, 'xy', bevel)
    def obox(s, cx, cy, z0, z1, L, W, ang, mm, bevel=0.0):
        """box rotated about Z: length L along `ang`, width W"""
        c, sn = math.cos(ang), math.sin(ang); hl, hw = L / 2, W / 2
        pts = [(cx + u * c - v * sn, cy + u * sn + v * c) for u, v in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))]
        return s.extrude(pts, z0, z1, mm, 'xy', bevel)
    def ring(s, x, y, z, prof, mm, n=32):
        """closed torus-like solid: prof is a closed loop of (r, h) (first point not repeated)"""
        i = s.mi(mm)
        rings = [[s.bm.verts.new((x + r * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n), z + h)) for k in range(n)] for r, h in prof]
        fs = []
        for a_, b_ in zip(rings, rings[1:] + rings[:1]):
            for k in range(n): fs.append(s.bm.faces.new((a_[k], a_[(k + 1) % n], b_[(k + 1) % n], b_[k])))
        for f in fs: f.material_index = i
        bmesh.ops.recalc_face_normals(s.bm, faces=fs)
        return fs
    def lathe(s, x, y, z, prof, mm, n=24, smooth=True):
        """closed solid of revolution; prof = [(r, h)] bottom -> top; r = 0 ends become single pole vertices"""
        i = s.mi(mm); rings = []
        for r, h in prof:
            if r < 1e-7: rings.append([s.bm.verts.new((x, y, z + h))])
            else: rings.append([s.bm.verts.new((x + r * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n), z + h)) for k in range(n)])
        fs = []
        for ra, rb in zip(rings[:-1], rings[1:]):
            if len(ra) == 1 and len(rb) == 1: continue
            for k in range(n):
                if len(ra) == 1: fs.append(s.bm.faces.new((ra[0], rb[k], rb[(k + 1) % n])))
                elif len(rb) == 1: fs.append(s.bm.faces.new((ra[k], ra[(k + 1) % n], rb[0])))
                else: fs.append(s.bm.faces.new((ra[k], ra[(k + 1) % n], rb[(k + 1) % n], rb[k])))
        if len(rings[0]) > 1: fs.append(s.bm.faces.new(list(reversed(rings[0]))))
        if len(rings[-1]) > 1: fs.append(s.bm.faces.new(rings[-1]))
        for f in fs:
            f.material_index = i
            if smooth and len(f.verts) <= 4: s.smooth.add(f)
        bmesh.ops.recalc_face_normals(s.bm, faces=fs)
        return fs
    def cyl(s, x, y, z0, z1, r, mm, n=16, r2=None):
        return s.lathe(x, y, z0, [(r, 0.0), (r if r2 is None else r2, z1 - z0)], mm, n)
    def rod(s, p, q, r, mm, n=8):
        """closed cylinder between two 3D points"""
        p, q = Vector(p), Vector(q); d = q - p
        if d.length < 1e-6: return []
        u = d.normalized(); t = u.orthogonal().normalized(); w = u.cross(t)
        A = [s.bm.verts.new(p + (t * math.cos(2 * math.pi * k / n) + w * math.sin(2 * math.pi * k / n)) * r) for k in range(n)]
        B = [s.bm.verts.new(v.co + d) for v in A]; i = s.mi(mm)
        fs = [s.bm.faces.new(list(reversed(A))), s.bm.faces.new(B)] + [s.bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k])) for k in range(n)]
        for f in fs: f.material_index = i
        for f in fs[2:]: s.smooth.add(f)
        bmesh.ops.recalc_face_normals(s.bm, faces=fs)
        return fs
    def sheet(s, grid, mm, thick, picture=True):
        """closed thin solid from a grid of 3D points rows x cols (cloth, carpets); picture UV 0..1 on both big faces"""
        R_, C_ = len(grid), len(grid[0]); i = s.mi(mm)
        V = [[s.bm.verts.new(grid[r][c]) for c in range(C_)] for r in range(R_)]
        top = []
        for r in range(R_ - 1):
            for c in range(C_ - 1):
                f = s.bm.faces.new((V[r][c], V[r][c + 1], V[r + 1][c + 1], V[r + 1][c])); f.material_index = i; top.append(f)
                if picture:
                    for lp, uv in zip(f.loops, ((c / (C_ - 1), r / (R_ - 1)), ((c + 1) / (C_ - 1), r / (R_ - 1)), ((c + 1) / (C_ - 1), (r + 1) / (R_ - 1)), (c / (C_ - 1), (r + 1) / (R_ - 1)))): lp[s.uv].uv = uv
        bmesh.ops.recalc_face_normals(s.bm, faces=top)
        nz = sum(f.normal.z * f.calc_area() for f in top)
        if nz < 0: bmesh.ops.reverse_faces(s.bm, faces=top)                 # horizontal sheets: thickness always grows downward
        ret = bmesh.ops.solidify(s.bm, geom=top, thickness=thick)
        fs = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMFace)] + top
        for f in fs:
            f.material_index = i
            if picture: s.fixed.add(f)
        bmesh.ops.recalc_face_normals(s.bm, faces=list(set(fs)))
        return fs
    def picture_box(s, x0, y0, z0, x1, y1, z1, mm, face):
        """thin closed board whose `face` ('+x','-x','+y','-y','+z') carries a 0..1 picture"""
        fs = s.box(x0, y0, z0, x1, y1, z1, mm)
        ax = {'x': 0, 'y': 1, 'z': 2}[face[1]]; sg = 1 if face[0] == '+' else -1
        for f in fs:
            n = f.normal
            if n[ax] * sg > 0.9:
                cs = [l.vert.co for l in f.loops]
                # u runs to the viewer's right when looking at the face from outside, v runs up
                if ax == 0: us = [(((c.y - y0) / (y1 - y0)) if sg > 0 else 1 - (c.y - y0) / (y1 - y0), (c.z - z0) / (z1 - z0)) for c in cs]
                elif ax == 1: us = [((1 - (c.x - x0) / (x1 - x0)) if sg > 0 else (c.x - x0) / (x1 - x0), (c.z - z0) / (z1 - z0)) for c in cs]
                else: us = [((c.x - x0) / (x1 - x0), (c.y - y0) / (y1 - y0)) for c in cs]
                for l, uv in zip(f.loops, us): l[s.uv].uv = uv
                s.fixed.add(f)
        return fs
    # ---- finish ----
    def mesh(s, name):
        bm = s.bm
        for f in bm.faces:
            if f in s.fixed: continue
            sz = UVSIZE.get(s.mats[f.material_index].name, 1.0); n = f.normal; ax = max(range(3), key=lambda k: abs(n[k]))
            for lp in f.loops:
                c = lp.vert.co; u, v = ((c.y, c.z) if ax == 0 else (c.x, c.z) if ax == 1 else (c.x, c.y))
                lp[s.uv].uv = (u / sz, v / sz)
        for f in bm.faces: f.smooth = f in s.smooth
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for mm in s.mats: me.materials.append(mm)
        me['kit'] = 1
        try: me.set_sharp_from_angle(angle=math.radians(40))
        except Exception: pass
        return me

ASSETS = {}
def inst(me, name, loc, rotz=0.0, cname='Furniture', scale=None):
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = (0, 0, rotz)
    if scale: o.scale = scale
    coll(cname).objects.link(o); return o

def arch_left(c, w, zs, za, n=10):
    """left half of a pointed arch (u, z) from the left spring point up to the apex"""
    h = w / 2; out = []
    for k in range(n + 1):
        t = k / n; p0 = (c - h, zs); p1 = (c - h, zs + (za - zs) * 0.62); p2 = (c, za)
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out
def spandrel_polys(c, w, zs, za, ztop):
    """the two spandrels of a pointed-arch head that fills exactly the opening [c-w/2, c+w/2] x [zs, ztop]"""
    L = arch_left(c, w, zs, za)
    left = L + [(c, ztop), (c - w / 2, ztop)]
    right = [(2 * c - u, z) for u, z in L] + [(c, ztop), (c + w / 2, ztop)]
    return left, right
