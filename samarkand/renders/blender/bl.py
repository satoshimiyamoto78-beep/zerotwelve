"""Small modelling kit for the Samarkand renders (Blender 5.x, bpy)."""
import bpy, bmesh, math, os, random
from mathutils import Vector

TEX = os.path.join(os.path.dirname(__file__), 'tex')
WARM = (1.0, 0.72, 0.42)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 3; sc.cycles.transmission_bounces = 4
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Medium High Contrast'
        sc.view_settings.exposure = 0.55
    except Exception: pass
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.02, 0.028, 0.05, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 1.0
    return sc

_mats = {}
def mat(name, color=(0.8, 0.8, 0.8), rough=0.5, metal=0.0, emit=None, strength=0.0, tex=None, scale=(1, 1, 1), bump=0.0,
        coat=0.0, transmission=0.0, offset=(0, 0, 0), noise_var=0.0):
    if name in _mats: return _mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    b = N['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if coat: b.inputs['Coat Weight'].default_value = coat
    if transmission: b.inputs['Transmission Weight'].default_value = transmission
    col_out = None
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / scale[0], 1 / scale[1], 1 / scale[2]); mp.inputs['Location'].default_value = offset
    Lk.new(tc.outputs['Object'], mp.inputs['Vector'])
    if tex:
        it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(TEX, tex), check_existing=True)
        it.projection = 'BOX'; it.projection_blend = 0.15
        Lk.new(mp.outputs['Vector'], it.inputs['Vector']); col_out = it.outputs['Color']
    if col_out is not None:
        Lk.new(col_out, b.inputs['Base Color'])
    else:
        if noise_var:
            nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 8
            Lk.new(mp.outputs['Vector'], nz.inputs['Vector'])
            mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'
            mix.inputs['A'].default_value = (*[max(0, c - noise_var) for c in color], 1); mix.inputs['B'].default_value = (*[min(1, c + noise_var) for c in color], 1)
            Lk.new(nz.outputs['Fac'], mix.inputs['Factor']); Lk.new(mix.outputs['Result'], b.inputs['Base Color'])
        else:
            b.inputs['Base Color'].default_value = (*color, 1)
    if bump:
        nz2 = N.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 40.0; nz2.inputs['Detail'].default_value = 10
        Lk.new(tc.outputs['Object'], nz2.inputs['Vector'])
        bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
        Lk.new(nz2.outputs['Fac'], bp.inputs['Height']); Lk.new(bp.outputs['Normal'], b.inputs['Normal'])
    if emit is not None:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = strength
    _mats[name] = m; return m

def _finish(o, m, bevel=0.0, smooth=False):
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o.select_set(False)
    if m: o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 3; bv.limit_method = 'ANGLE'
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    return o

def box(x0, y0, z0, x1, y1, z1, m=None, bevel=0.0, name='box'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.active_object; o.name = name; o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    return _finish(o, m, bevel)

def cyl(x, y, z, r, h, m=None, axis='Z', verts=48, r2=None, name='cyl', bevel=0.0):
    rot = {'Z': (0, 0, 0), 'X': (0, math.pi / 2, 0), 'Y': (math.pi / 2, 0, 0)}[axis]
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(x, y, z), rotation=rot, vertices=verts)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=h, location=(x, y, z), rotation=rot, vertices=verts)
    o = bpy.context.active_object; o.name = name
    return _finish(o, m, bevel, smooth=True)

def sphere(x, y, z, r, m=None, scale=(1, 1, 1), name='sph'):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z), segments=48, ring_count=24)
    o = bpy.context.active_object; o.name = name; o.scale = scale
    return _finish(o, m, smooth=True)

def torus(x, y, z, R, r, m=None, axis='Z'):
    rot = {'Z': (0, 0, 0), 'X': (0, math.pi / 2, 0), 'Y': (math.pi / 2, 0, 0)}[axis]
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=(x, y, z), rotation=rot, major_segments=64, minor_segments=12)
    o = bpy.context.active_object
    return _finish(o, m, smooth=True)

def lathe(x, y, z, prof, m=None, steps=48, name='lathe'):
    """prof: list of (radius, height) bottom->top; revolved around Z."""
    bm = bmesh.new(); rings = []
    for k in range(steps):
        a = 2 * math.pi * k / steps; ring = []
        for r, h in prof: ring.append(bm.verts.new((x + r * math.cos(a), y + r * math.sin(a), z + h)))
        rings.append(ring)
    for k in range(steps):
        r0, r1 = rings[k], rings[(k + 1) % steps]
        for i in range(len(prof) - 1):
            bm.faces.new((r0[i], r1[i], r1[i + 1], r0[i + 1]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    for p in me.polygons: p.use_smooth = True
    if m: me.materials.append(m)
    return o

def prism_xz(pts, y0, y1, m=None, name='prism'):
    """Extrude a polygon given in the XZ plane between y0 and y1."""
    bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts]; b = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    n = len(pts)
    for i in range(n):
        bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    if m: me.materials.append(m)
    return o

def arch_pts(cx, w, z0, zs, za, n=20):
    """Pointed (Timurid) arch outline in XZ: jambs to the spring line, two curved halves meeting at the apex."""
    h = w / 2; right = []
    for i in range(n + 1):
        t = i / n; p0 = (cx + h, zs); p1 = (cx + h, zs + (za - zs) * 0.62); p2 = (cx, za)
        right.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    left = [(2 * cx - x, z) for x, z in reversed(right[:-1])]
    return [(cx - h, z0), (cx + h, z0)] + right + left

def cut(target, cutter, apply=True):
    md = target.modifiers.new('cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cutter; md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def point(x, y, z, energy, color=WARM, radius=0.05):
    ld = bpy.data.lights.new('pt', 'POINT'); ld.energy = energy; ld.color = color; ld.shadow_soft_size = radius
    o = bpy.data.objects.new('pt', ld); o.location = (x, y, z); bpy.context.collection.objects.link(o); return o

def area(x, y, z, size, energy, color=(1, .85, .7), rot=(0, 0, 0), shape='SQUARE', size_y=None):
    ld = bpy.data.lights.new('ar', 'AREA'); ld.energy = energy; ld.color = color; ld.size = size; ld.shape = shape
    if size_y: ld.size_y = size_y
    o = bpy.data.objects.new('ar', ld); o.location = (x, y, z); o.rotation_euler = rot; bpy.context.collection.objects.link(o); return o

def camera(loc, target, lens=26, shift_y=0.0):
    cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.shift_y = shift_y
    o = bpy.data.objects.new('cam', cd); bpy.context.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = o; return o

def render(path, w=1600, h=900, samples=128):
    sc = bpy.context.scene; sc.render.resolution_x = w; sc.render.resolution_y = h; sc.render.resolution_percentage = 100
    sc.cycles.samples = samples; sc.render.filepath = path; sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)

# ---------- shared kit of parts ----------
def M():
    return dict(
        plaster=mat('plaster', (0.80, 0.68, 0.52), rough=0.92, bump=0.12, noise_var=0.04),
        plaster_l=mat('plaster_l', (0.90, 0.83, 0.72), rough=0.9, bump=0.08, noise_var=0.03),
        floor=mat('floor', tex='floor.png', scale=(1.2, 1.2, 1.2), rough=0.45),
        girih=mat('girih', tex='girih.png', scale=(0.6, 0.6, 0.6), rough=0.3),
        majolica=mat('majolica', tex='majolica.png', scale=(0.6, 0.6, 0.6), rough=0.18, coat=0.4),
        band=mat('band', tex='band.png', scale=(1.2, 1.2, 0.3), rough=0.2, coat=0.4),
        lapis=mat('lapis', (0.04, 0.09, 0.32), rough=0.12, coat=0.6),
        turq=mat('turq', (0.05, 0.42, 0.47), rough=0.15, coat=0.5),
        walnut=mat('walnut', (0.20, 0.11, 0.06), rough=0.45, noise_var=0.03),
        oak=mat('oak', (0.45, 0.29, 0.16), rough=0.5, noise_var=0.04),
        brass=mat('brass', (0.86, 0.62, 0.30), rough=0.22, metal=1.0),
        terrazzo=mat('terrazzo', (0.88, 0.83, 0.75), rough=0.2, noise_var=0.05),
        brick=mat('brick', (0.55, 0.26, 0.15), rough=0.85, bump=0.2, noise_var=0.06),
        ikat=mat('ikat', tex='ikat.png', scale=(0.5, 0.5, 0.5), rough=0.8),
        jali=mat('jali', tex='jali.png', scale=(0.5, 0.5, 0.5), rough=0.55),
        sky=mat('sky', tex='sky.png', scale=(1, 1, 1), emit=(1, 1, 1), strength=0.0),
        suzani=mat('suzani', tex='suzani.png', scale=(0.6, 0.6, 0.6), rough=0.85),
        red=mat('red', (0.45, 0.06, 0.07), rough=0.75),
        glow=mat('glow', (1, .8, .55), emit=(1.0, 0.68, 0.36), strength=14.0),
        glow_soft=mat('glow_soft', (1, .8, .55), emit=(1.0, 0.70, 0.40), strength=3.0),
        leaf=mat('leaf', (0.10, 0.25, 0.08), rough=0.6, noise_var=0.05),
        leaf2=mat('leaf2', (0.18, 0.32, 0.12), rough=0.6),
        clay=mat('clay', (0.62, 0.36, 0.22), rough=0.8, noise_var=0.05),
        glass=mat('glass', (0.95, 0.97, 0.98), rough=0.02, transmission=1.0),
        darkglass=mat('darkglass', (0.06, 0.09, 0.07), rough=0.08, coat=0.5),
        amber=mat('amber', (0.35, 0.14, 0.03), rough=0.06, coat=0.6),
        steel=mat('steel', (0.62, 0.62, 0.62), rough=0.3, metal=1.0),
        black=mat('black', (0.02, 0.02, 0.02), rough=0.4, metal=0.6),
        water=mat('water', (0.10, 0.45, 0.55), rough=0.02, transmission=0.6, coat=1.0),
    )

def slat_ceiling(m, x0, x1, y0, y1, z, step=0.12, w=0.05, d=0.08, axis='X'):
    if axis == 'X':
        o = box(x0, y0, z, x1, y0 + w, z + d, m['oak'])
        ar = o.modifiers.new('ar', 'ARRAY'); ar.count = int((y1 - y0) / step); ar.use_relative_offset = False; ar.use_constant_offset = True; ar.constant_offset_displace = (0, step, 0)
    else:
        o = box(x0, y0, z, x0 + w, y1, z + d, m['oak'])
        ar = o.modifiers.new('ar', 'ARRAY'); ar.count = int((x1 - x0) / step); ar.use_relative_offset = False; ar.use_constant_offset = True; ar.constant_offset_displace = (step, 0, 0)
    box(x0, y0, z + d, x1, y1, z + d + 0.02, mat('ceilback', (0.03, 0.025, 0.02), rough=0.9))

def lantern(m, x, y, z, s=1.0, rod_top=None, energy=30):
    """Brass lantern: glowing glass drum, ribs, dome cap; hung on a rod."""
    h = 0.36 * s; r = 0.16 * s
    cyl(x, y, z, r * 0.92, h, m['glow_soft'], verts=32)
    for k in range(10):
        a = 2 * math.pi * k / 10
        box(x + r * math.cos(a) - 0.007, y + r * math.sin(a) - 0.007, z - h / 2, x + r * math.cos(a) + 0.007, y + r * math.sin(a) + 0.007, z + h / 2, m['brass'])
    torus(x, y, z - h / 2, r, 0.012 * s, m['brass']); torus(x, y, z + h / 2, r, 0.012 * s, m['brass'])
    lathe(x, y, z + h / 2, [(r * 1.05, 0), (r * 0.8, 0.07 * s), (r * 0.35, 0.14 * s), (0.02, 0.2 * s)], m['brass'])
    lathe(x, y, z - h / 2, [(r, 0), (r * 0.6, -0.06 * s), (0.02, -0.1 * s)], m['brass'])
    if rod_top: cyl(x, y, (z + h / 2 + 0.2 * s + rod_top) / 2, 0.006, rod_top - (z + h / 2 + 0.2 * s), m['brass'], verts=12)
    point(x, y, z, energy, radius=0.08)

def stool(m, x, y, rot=0.0, h=0.75):
    cyl(x, y, h - 0.03, 0.21, 0.07, m['ikat'], verts=40, bevel=0.01)
    for k in range(4):
        a = rot + math.pi / 4 + k * math.pi / 2
        bx, by = x + 0.2 * math.cos(a), y + 0.2 * math.sin(a); tx_, ty_ = x + 0.14 * math.cos(a), y + 0.14 * math.sin(a)
        L = math.dist((bx, by, 0), (tx_, ty_, h - 0.06)); o = cyl((bx + tx_) / 2, (by + ty_) / 2, (h - 0.06) / 2, 0.018, L, m['walnut'], verts=12)
        o.rotation_euler = (0, 0, 0)
        d = Vector((tx_ - bx, ty_ - by, h - 0.06)).normalized(); o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    torus(x, y, 0.3, 0.175, 0.012, m['brass'])

def bottle(m, x, y, z, kind=0):
    mm = [m['darkglass'], m['amber'], m['glass']][kind % 3]
    lathe(x, y, z, [(0.0, 0), (0.035, 0), (0.037, 0.18), (0.015, 0.24), (0.012, 0.3), (0.0, 0.3)], mm, steps=24)

def samovar(m, x, y, z, s=1.0):
    lathe(x, y, z, [(0.0, 0), (0.09 * s, 0), (0.08 * s, 0.03 * s), (0.05 * s, 0.06 * s), (0.06 * s, 0.09 * s), (0.15 * s, 0.16 * s), (0.17 * s, 0.28 * s),
                    (0.16 * s, 0.4 * s), (0.11 * s, 0.47 * s), (0.06 * s, 0.5 * s), (0.08 * s, 0.53 * s), (0.04 * s, 0.6 * s), (0.05 * s, 0.68 * s), (0.0, 0.7 * s)], m['brass'], steps=48)
    cyl(x + 0.19 * s, y, z + 0.14 * s, 0.012 * s, 0.1 * s, m['brass'], axis='X')
    lathe(x, y, z + 0.7 * s, [(0.0, 0), (0.06 * s, 0), (0.08 * s, 0.05 * s), (0.06 * s, 0.11 * s), (0.02 * s, 0.14 * s), (0, 0.15 * s)], m['turq'], steps=32)

def bush(m, x, y, z, r, n=12, seed=1):
    rr = random.Random(seed)
    for k in range(n):
        a = rr.uniform(0, 2 * math.pi); d = rr.uniform(0, r * 0.5)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r * rr.uniform(0.32, 0.5), location=(x + d * math.cos(a), y + d * math.sin(a), z + rr.uniform(0, r * 0.6)))
        o = bpy.context.active_object
        dp = o.modifiers.new('d', 'DISPLACE'); tx = bpy.data.textures.new('n', 'CLOUDS'); tx.noise_scale = 0.06; dp.texture = tx; dp.strength = r * 0.22
        o.data.materials.append(m['leaf'] if k % 2 else m['leaf2'])
        for p in o.data.polygons: p.use_smooth = True

def potted_tree(m, x, y, s=1.0, seed=2):
    lathe(x, y, 0, [(0, 0), (0.22 * s, 0), (0.32 * s, 0.25 * s), (0.34 * s, 0.55 * s), (0.30 * s, 0.6 * s), (0, 0.6 * s)], m['clay'])
    cyl(x, y, 0.6 * s + 0.5 * s, 0.04 * s, 1.0 * s, m['walnut'], verts=12)
    bush(m, x, y, 1.45 * s, 0.55 * s, n=8, seed=seed)

def pointed_frame(m_frame, cx, y0, y1, w, zs, za, t=0.12, z0=0.0, m_inner=None):
    """Thin pointed-arch frame (portal) made of an outer arch minus an inner arch."""
    outer = prism_xz(arch_pts(cx, w + 2 * t, z0, zs, za + t * 1.2), y0, y1, m_frame, 'frame')
    inner = prism_xz(arch_pts(cx, w, z0 - 0.1, zs, za), y0 - 0.1, y1 + 0.1, None, 'cutter')
    cut(outer, inner); return outer

def sky_plane(x, y, z, w, h, rot_z=0.0, strength=1.2):
    """Vertical emissive backdrop: dusk sky over the sea (UV-mapped gradient)."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z), rotation=(math.pi / 2, 0, rot_z))
    o = bpy.context.active_object; o.scale = (w, h, 1)
    m = bpy.data.materials.new('skyp'); m.use_nodes = True; N = m.node_tree.nodes; Lk = m.node_tree.links
    for n in list(N): N.remove(n)
    out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); it = N.new('ShaderNodeTexImage')
    it.image = bpy.data.images.load(os.path.join(TEX, 'sky.png'), check_existing=True); uv = N.new('ShaderNodeTexCoord')
    fl = N.new('ShaderNodeMapping'); fl.inputs['Scale'].default_value = (1, -1, 1); fl.inputs['Location'].default_value = (0, 1, 0)
    Lk.new(uv.outputs['UV'], fl.inputs['Vector']); Lk.new(fl.outputs['Vector'], it.inputs['Vector'])
    Lk.new(it.outputs['Color'], em.inputs['Color']); em.inputs['Strength'].default_value = strength; Lk.new(em.outputs['Emission'], out.inputs['Surface'])
    o.data.materials.append(m); return o

def chair(m, x, y, face=0.0):
    """Walnut chair with ikat seat; face = direction the sitter looks (radians)."""
    import mathutils
    parts = []
    c, s = math.cos(face), math.sin(face)
    def P(dx, dy): return (x + dx * c - dy * s, y + dx * s + dy * c)
    for dx, dy in ((0.19, 0.19), (0.19, -0.19), (-0.19, 0.19), (-0.19, -0.19)):
        px, py = P(dx, dy); cyl(px, py, 0.22, 0.017, 0.44, m['walnut'], verts=10)
    sx, sy = P(0, 0); o = box(sx - 0.22, sy - 0.22, 0.44, sx + 0.22, sy + 0.22, 0.5, m['ikat'], bevel=0.015); o.rotation_euler[2] = face
    bx, by = P(-0.2, 0); o = box(bx - 0.025, by - 0.21, 0.5, bx + 0.025, by + 0.21, 0.88, m['walnut'], bevel=0.01); o.rotation_euler[2] = face

def table(m, x, y, w=1.2, d=0.8, h=0.75, top='walnut'):
    box(x - w / 2, y - d / 2, h - 0.04, x + w / 2, y + d / 2, h, m[top], bevel=0.008)
    box(x - w / 2, y - d / 2, h - 0.045, x + w / 2, y + d / 2, h - 0.035, m['brass'])
    for dx in (-w / 2 + 0.08, w / 2 - 0.08):
        for dy in (-d / 2 + 0.08, d / 2 - 0.08): cyl(x + dx, y + dy, (h - 0.04) / 2, 0.025, h - 0.04, m['walnut'], verts=12)
