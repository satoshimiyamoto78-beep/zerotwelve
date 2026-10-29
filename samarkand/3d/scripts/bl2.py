"""Detail upgrade over bl.py: procedural wood, tile relief, sheen fabrics, leaf bushes, dusk sky, props, DOF."""
import bpy, bmesh, math, os, random
from mathutils import Vector
import bl
from bl import *          # noqa: F401,F403  (re-export the base kit)

_box0 = bl.box
def box(x0, y0, z0, x1, y1, z1, m=None, bevel=0.0, name='box'):
    if not bevel and min(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)) > 0.025:
        bevel = 0.004
    return _box0(x0, y0, z0, x1, y1, z1, m, bevel, name)
bl.box = box

def reset(sky=True, sun_elev=3.0, sky_strength=0.3, exposure=0.55):
    sc = bl.reset()
    sc.view_settings.exposure = exposure
    sc.cycles.samples = 160
    if sky:
        w = sc.world; nt = w.node_tree; N = nt.nodes
        sk = N.new('ShaderNodeTexSky'); sk.sky_type = 'MULTIPLE_SCATTERING'
        sk.sun_elevation = math.radians(sun_elev); sk.sun_rotation = math.radians(100); sk.sun_disc = False
        bg = N['Background']; nt.links.new(sk.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = sky_strength
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, -0.07))
    g = bpy.context.active_object; g.data.materials.append(mat('ground_far', (0.11, 0.12, 0.09), rough=0.95, noise_var=0.03))
    return sc

def wood(name, base, dark, rough=0.45, scale=1.0, along='X'):
    if name in bl._mats: return bl._mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; Lk = m.node_tree.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping')
    st = {'X': (0.4 * scale, 6 * scale, 6 * scale), 'Y': (6 * scale, 0.4 * scale, 6 * scale), 'Z': (6 * scale, 6 * scale, 0.4 * scale)}[along]
    mp.inputs['Scale'].default_value = st; Lk.new(tc.outputs['Object'], mp.inputs['Vector'])
    wv = N.new('ShaderNodeTexWave'); wv.wave_type = 'RINGS'; wv.inputs['Scale'].default_value = 2.2; wv.inputs['Distortion'].default_value = 7.0; wv.inputs['Detail'].default_value = 4
    Lk.new(mp.outputs['Vector'], wv.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 30; Lk.new(mp.outputs['Vector'], nz.inputs['Vector'])
    mx = N.new('ShaderNodeMath'); mx.operation = 'MULTIPLY_ADD'; mx.inputs[1].default_value = 0.75
    Lk.new(wv.outputs['Fac'], mx.inputs[0]); Lk.new(nz.outputs['Fac'], mx.inputs[2])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (*dark, 1); cr.color_ramp.elements[1].color = (*base, 1)
    cr.color_ramp.elements[0].position = 0.25; cr.color_ramp.elements[1].position = 0.85
    Lk.new(mx.outputs['Value'], cr.inputs['Fac']); Lk.new(cr.outputs['Color'], b.inputs['Base Color'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.08; Lk.new(wv.outputs['Fac'], bp.inputs['Height']); Lk.new(bp.outputs['Normal'], b.inputs['Normal'])
    bl._mats[name] = m; return m

def tile(name, texfile, size, rough=0.35, bump=0.25, coat=0.0):
    if name in bl._mats: return bl._mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; Lk = m.node_tree.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    if coat: b.inputs['Coat Weight'].default_value = coat
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / size, 1 / size, 1 / size)
    Lk.new(tc.outputs['Object'], mp.inputs['Vector'])
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(os.path.join(bl.TEX, texfile), check_existing=True); it.projection = 'BOX'; it.projection_blend = 0.15
    Lk.new(mp.outputs['Vector'], it.inputs['Vector']); Lk.new(it.outputs['Color'], b.inputs['Base Color'])
    bw = N.new('ShaderNodeRGBToBW'); Lk.new(it.outputs['Color'], bw.inputs['Color'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.002
    Lk.new(bw.outputs['Val'], bp.inputs['Height']); Lk.new(bp.outputs['Normal'], b.inputs['Normal'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6; Lk.new(mp.outputs['Vector'], nz.inputs['Vector'])
    rr = N.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = rough * 0.6; rr.inputs['To Max'].default_value = rough * 1.4
    Lk.new(nz.outputs['Fac'], rr.inputs['Value']); Lk.new(rr.outputs['Result'], b.inputs['Roughness'])
    bl._mats[name] = m; return m

def fabric(name, texfile, size=0.5):
    if name in bl._mats: return bl._mats[name]
    m = tile(name + '_t', texfile, size, rough=0.85, bump=0.4)
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Sheen Weight'].default_value = 0.6; b.inputs['Sheen Roughness'].default_value = 0.4
    bl._mats[name] = m; return m

def M2():
    m = bl.M()
    m.update(
        walnut=wood('walnut2', (0.26, 0.15, 0.08), (0.10, 0.05, 0.025)),
        oak=wood('oak2', (0.55, 0.37, 0.21), (0.30, 0.18, 0.09)),
        deck=wood('deck2', (0.50, 0.33, 0.19), (0.26, 0.15, 0.07), rough=0.55, along='Y'),
        floor=tile('floor2', 'floor.png', 1.2, rough=0.4, bump=0.35),
        girih=tile('girih2', 'girih.png', 0.6, rough=0.25, bump=0.4, coat=0.3),
        majolica=tile('majolica2', 'majolica.png', 0.6, rough=0.15, bump=0.3, coat=0.5),
        band=tile('band2', 'band.png', 1.2, rough=0.18, bump=0.3, coat=0.5),
        ikat=fabric('ikat2', 'ikat.png', 0.5), suzani=fabric('suzani2', 'suzani.png', 0.6),
        ceramic=mat('ceramic', (0.93, 0.92, 0.88), rough=0.12, coat=0.6),
        linen=mat('linen', (0.86, 0.80, 0.70), rough=0.9),
        candle=mat('candle', (1, .85, .6), emit=(1.0, 0.62, 0.3), strength=25.0),
    )
    m['ikat'].name; return m

def leafy(m, x, y, z, r, n=None, seed=1, leaf=0.11):
    """Bush built from individual leaves on a fuzzy sphere (one mesh, two greens)."""
    rr = random.Random(seed); n = n or int(420 * (r / 0.6) ** 2)
    bm = bmesh.new()
    for k in range(n):
        u, v = rr.uniform(-1, 1), rr.uniform(0, 2 * math.pi); s = math.sqrt(1 - u * u)
        d = Vector((s * math.cos(v), s * math.sin(v), u * 0.8)); p = Vector((x, y, z + r * 0.7)) + d * r * rr.uniform(0.55, 1.0)
        t1 = d.orthogonal().normalized(); t1.rotate(Vector((rr.random(), rr.random(), rr.random())).to_track_quat('Z', 'Y')); t2 = d.cross(t1).normalized()
        L, W = leaf * rr.uniform(0.7, 1.3), leaf * 0.45
        vs = [bm.verts.new(p - t1 * L / 2), bm.verts.new(p + t2 * W / 2), bm.verts.new(p + t1 * L / 2), bm.verts.new(p - t2 * W / 2)]
        f = bm.faces.new(vs); f.material_index = k % 2
    me = bpy.data.meshes.new('bush'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('bush', me); bpy.context.collection.objects.link(o)
    me.materials.append(m['leaf']); me.materials.append(m['leaf2'])
    return o
bl.bush = lambda m, x, y, z, r, n=12, seed=1: leafy(m, x, y, z, r, seed=seed)

def plate(m, x, y, z, r=0.13):
    lathe(x, y, z, [(0, 0), (r * 0.55, 0), (r * 0.9, 0.012), (r, 0.022), (r * 0.97, 0.024), (0, 0.01)], m['ceramic'], steps=40)
    torus(x, y, z + 0.022, r * 0.98, 0.004, m['lapis'])

def tea_glass(m, x, y, z):
    lathe(x, y, z, [(0, 0), (0.025, 0), (0.03, 0.03), (0.024, 0.06), (0.03, 0.09), (0, 0.09)], m['glass'], steps=24)

def piala(m, x, y, z):
    lathe(x, y, z, [(0, 0), (0.022, 0), (0.045, 0.045), (0.043, 0.047), (0.02, 0.006), (0, 0.006)], m['turq'], steps=28)

def teapot(m, x, y, z, s=1.0):
    lathe(x, y, z, [(0, 0), (0.05 * s, 0), (0.08 * s, 0.05 * s), (0.075 * s, 0.1 * s), (0.04 * s, 0.125 * s), (0.02 * s, 0.14 * s), (0, 0.145 * s)], m['lapis'], steps=32)
    o = cyl(x + 0.09 * s, y, z + 0.08 * s, 0.01 * s, 0.09 * s, m['lapis'], verts=12); o.rotation_euler = (0, math.radians(50), 0)

def candle(m, x, y, z):
    cyl(x, y, z + 0.04, 0.035, 0.08, m['brass'], verts=20)
    cyl(x, y, z + 0.07, 0.025, 0.05, m['candle'], verts=16)
    point(x, y, z + 0.11, 3.0, radius=0.02)

def cushion(m, x0, y0, z0, x1, y1, z1, mm):
    return _box0(x0, y0, z0, x1, y1, z1, mm, bevel=min(0.05, (z1 - z0) * 0.45))

def table_set(m, x, y, n=4, w=1.2, h=0.75, seed=0):
    rr = random.Random(seed)
    pos = [(-w / 4, -0.22), (w / 4, -0.22), (-w / 4, 0.22), (w / 4, 0.22)][:n]
    for dx, dy in pos:
        plate(m, x + dx, y + dy, h); tea_glass(m, x + dx + 0.13, y + dy * 0.6, h)
    candle(m, x, y, h)
    if rr.random() < 0.7: teapot(m, x + 0.12, y + 0.02, h)

def table4(m, x, y, w=1.2, d=0.8, h=0.75, chairs='NS', seed=0):
    table(m, x, y, w, d, h)
    if chairs == 'NS':
        for sx in (-w / 4, w / 4):
            chair(m, x + sx, y - d / 2 - 0.28, face=math.pi / 2); chair(m, x + sx, y + d / 2 + 0.28, face=-math.pi / 2)
    else:
        for sy in (-d / 4 * 1.5, d / 4 * 1.5):
            chair(m, x - w / 2 - 0.28, y + sy, face=0.0); chair(m, x + w / 2 + 0.28, y + sy, face=math.pi)
    table_set(m, x, y, 4, w, h, seed)

def camera(loc, target, lens=26, fstop=0.0, focus=None):
    o = bl.camera(loc, target, lens)
    if fstop:
        o.data.dof.use_dof = True; o.data.dof.aperture_fstop = fstop
        o.data.dof.focus_distance = focus or (Vector(target) - Vector(loc)).length
    return o

def sun(elev=12, rot=110, strength=2.5, color=(1, 0.8, 0.6)):
    ld = bpy.data.lights.new('sun', 'SUN'); ld.energy = strength; ld.color = color; ld.angle = math.radians(1.5)
    o = bpy.data.objects.new('sun', ld); bpy.context.collection.objects.link(o)
    o.rotation_euler = (math.radians(90 - elev), 0, math.radians(rot)); return o
bush = bl.bush
