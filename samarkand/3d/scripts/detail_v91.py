"""rev. 9.1 (owner 2026-11-05):
  * south lot line behind the majlis / photo zone and the mangal: the existing boundary fence gets a hand-trowelled clay
    (earth-plaster) skin, 35 mm, to +2.7 with a rounded coping, cut round the two kept pergola posts; outside the pergola
    shallow sculpted arched panels in the same clay
  * kids corner: sandbox removed (sand gets carried around) -> two walnut rocking camels + soft foam play blocks
    (a swing needs ~3.5 m clear swing run; the corner is 2.4 m deep, so no swing)"""
import math
# ---------------------------------------------------------------- clay plaster material
def clay_mat(name, base):
    if name in bl._mats: return bl._mats[name]
    mm = bpy.data.materials.new(name); mm.use_nodes = True; N = mm.node_tree.nodes; Lk = mm.node_tree.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = 0.92
    tc = N.new('ShaderNodeTexCoord')
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 2.2; n1.inputs['Detail'].default_value = 5; n1.inputs['Distortion'].default_value = 0.6
    Lk.new(tc.outputs['Object'], n1.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (*[c * 0.8 for c in base], 1); cr.color_ramp.elements[1].color = (*[min(1, c * 1.18) for c in base], 1)
    Lk.new(n1.outputs['Fac'], cr.inputs['Fac']); Lk.new(cr.outputs['Color'], b.inputs['Base Color'])
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 7.0; n2.inputs['Distortion'].default_value = 2.5; Lk.new(tc.outputs['Object'], n2.inputs['Vector'])  # trowel sweeps
    n3 = N.new('ShaderNodeTexNoise'); n3.inputs['Scale'].default_value = 260.0; Lk.new(tc.outputs['Object'], n3.inputs['Vector'])                                       # sand grain
    ad = N.new('ShaderNodeMath'); ad.operation = 'ADD'; Lk.new(n2.outputs['Fac'], ad.inputs[0]); Lk.new(n3.outputs['Fac'], ad.inputs[1])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35; bp.inputs['Distance'].default_value = 0.004
    Lk.new(ad.outputs['Value'], bp.inputs['Height']); Lk.new(bp.outputs['Normal'], b.inputs['Normal'])
    bl._mats[name] = mm; return mm
CLAY = clay_mat('clay_plaster', (0.55, 0.37, 0.25)); CLAY2 = clay_mat('clay_plaster_relief', (0.6, 0.42, 0.29))

# ---------------------------------------------------------------- south lot-line clay wall (local u along the line, v inwards)
A_ = (-0.1675, 0.0); ANG = math.atan2(3.3892, 13.4586 + 0.1675)
def to_uv(x, y):
    dx, dy = x - A_[0], y - A_[1]; return dx * math.cos(ANG) + dy * math.sin(ANG), -dx * math.sin(ANG) + dy * math.cos(ANG)
U1 = to_uv(12.25, 3.05)[0]; HW_ = TER + 2.7; TV = 0.035
cuts = sorted(to_uv(*[p / 1000 for p in pp])[0] for pp in ((4552, 1277), (10180, 2677)))
spans, u0 = [], 0.0
for uc in cuts: spans.append((u0, uc - 0.18)); u0 = uc + 0.18
spans.append((u0, U1))
mb = MB()
for i_, (a, b_) in enumerate(spans):
    tv = 0.03 if i_ == 1 else TV                                                                      # behind the majlis backdrop: 30 mm skin only
    mb.box(a, 0.0, TER, b_, tv, HW_ - tv / 2, CLAY)
    mb.rod((a, tv / 2, HW_ - tv / 2), (b_, tv / 2, HW_ - tv / 2), tv / 2, CLAY, 16)                  # rounded coping
    if i_ != 1: mb.box(a, 0.0, TER, b_, tv + 0.012, TER + 0.12, CLAY2)                                # clay skirting
# sculpted arched panels outside the pergola (raised 15 mm bands), owner: simple, buildable
PG0, PG1 = cuts[0] - 0.18, cuts[1] + 0.18
panels = [(0.55 + 1.3 * k, 1.05) for k in range(3)] + [(PG1 + 0.35 + 1.25 * k, 1.0) for k in range(int((U1 - PG1 - 0.5) / 1.25))]
for uc0, w in panels:
    c = uc0 + w / 2; zs, za = TER + 1.65, TER + 2.3
    Lp = arch_left(c, w, zs, za, 14); Rp = [(2 * c - u, z) for u, z in Lp]
    outer = SPoly([(uc0, TER + 0.3), (uc0 + w, TER + 0.3)] + Rp + Lp[::-1][1:])
    inner = outer.buffer(-0.07, join_style=2)
    band = outer.difference(inner)
    for q in ([band] if band.geom_type == 'Polygon' else list(band.geoms)): ext_holes(mb, q, TV, TV + 0.015, CLAY2, 'xz')
inst(mb.mesh('Boundary_clay_wall'), 'Boundary_clay_wall', (A_[0], A_[1], 0.0), ANG, 'Street_facade')
PVv = (-math.sin(ANG), math.cos(ANG))
for n_, dv in (('photo_plant', 0.06), ('photo_plant_soil', 0.06), ('Areca', 0.3)):                    # planter bed off the new wall skin
    o_ = bpy.data.objects.get(n_)
    if o_: o_.location.x += PVv[0] * dv; o_.location.y += PVv[1] * dv
print('clay wall u 0 ..', round(U1, 2), 'cuts', [round(c, 2) for c in cuts], 'panels', len(panels))

# ---------------------------------------------------------------- kids: rocking camels + foam blocks instead of the sandbox
_rm('Kids_sandbox', 'Kids_sand_toys')
@cached
def a_rock_camel():
    """walnut rocking camel 900 x 360 x 620: two arc rockers, two camel side boards, seat with kilim pad between the humps, handle"""
    b = MB(); W_ = XW['wd']
    rk = [(x / 20 * 0.9 - 0.45, 0.07 * ((x / 20 * 0.9 - 0.45) / 0.45) ** 2) for x in range(21)]
    rpoly = rk + [(x, z + 0.055) for x, z in rk[::-1]]
    for y in (-0.165, 0.14): b.extrude(rpoly, y, y + 0.025, W_, 'xz')
    zb = lambda x: 0.07 * (x / 0.45) ** 2 + 0.03
    body = [(-0.3, zb(-0.3)), (-0.32, 0.3), (-0.22, 0.42), (-0.1, 0.36), (0.02, 0.45), (0.14, 0.35), (0.22, 0.36), (0.29, 0.52), (0.33, 0.6),
            (0.42, 0.61), (0.45, 0.56), (0.37, 0.52), (0.31, 0.34), (0.24, zb(0.24))]
    for y in (-0.115, 0.09): b.extrude(body, y, y + 0.025, W_, 'xz')
    for x in (-0.26, 0.2): b.box(x - 0.025, -0.165, zb(x) + 0.01, x + 0.025, 0.165, zb(x) + 0.05, W_, 0.003)   # stretchers tie rockers + boards
    b.box(-0.2, -0.115, 0.31, 0.08, 0.115, 0.34, W_, 0.004); b.box(-0.18, -0.1, 0.34, 0.06, 0.1, 0.37, X['kilim'] if 'kilim' in X else W_, 0.01)
    b.rod((0.24, -0.15, 0.47), (0.24, 0.15, 0.47), 0.014, W_, 12)
    return b.mesh('Kids_rocking_camel')
inst(a_rock_camel(), 'Kids_rocking_camel_1', (-1.35, 3.3, TER), 0.0, 'Kids')
inst(a_rock_camel(), 'Kids_rocking_camel_2', (-1.05, 2.42, TER), 0.35, 'Kids')
mb = MB(); FC = [K['c2'], K['c3'], K['c1'], K['c4']]
mb.box(-0.62, 3.62, TER, -0.3, 3.94, TER + 0.32, FC[0], 0.03); mb.box(-0.62, 3.62, TER + 0.32, -0.36, 3.88, TER + 0.58, FC[1], 0.03)
mb.box(-0.9, 3.66, TER, -0.66, 3.9, TER + 0.24, FC[3], 0.03)
inst(mb.mesh('Kids_foam_blocks'), 'Kids_foam_blocks', (0, 0, 0), 0, 'Kids')
print('rev 9.1 wall + kids ok')

# ---------------------------------------------------------------- velvet look on every image-textured velvet in the model
def velvetize(mm):
    if not mm.use_nodes or mm.get('velvetized'): return
    N = mm.node_tree.nodes; Lk = mm.node_tree.links; b = N.get('Principled BSDF')
    if not b or not b.inputs['Base Color'].is_linked: return
    src = b.inputs['Base Color'].links[0].from_socket
    lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.45
    dk = N.new('ShaderNodeMix'); dk.data_type = 'RGBA'; dk.inputs['Factor'].default_value = 0.4; Lk.new(src, dk.inputs[6]); dk.inputs[7].default_value = (0, 0, 0, 1)
    lt = N.new('ShaderNodeMix'); lt.data_type = 'RGBA'; lt.blend_type = 'SCREEN'; lt.inputs['Factor'].default_value = 0.18; Lk.new(src, lt.inputs[6]); lt.inputs[7].default_value = (0.9, 0.55, 0.4, 1)
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; Lk.new(lw.outputs['Facing'], mx.inputs['Factor']); Lk.new(dk.outputs[2], mx.inputs[6]); Lk.new(lt.outputs[2], mx.inputs[7])
    Lk.new(mx.outputs[2], b.inputs['Base Color'])
    b.inputs['Sheen Weight'].default_value = 0.6; b.inputs['Sheen Roughness'].default_value = 0.35; b.inputs['Roughness'].default_value = max(0.7, b.inputs['Roughness'].default_value)
    mm['velvetized'] = 1
nv = 0
for mm in bpy.data.materials:
    if 'velvet' in mm.name.lower() and not mm.name.startswith(('velvet_rust', 'velvet_copper', 'velvet_wine89', 'velvet_ochre')): velvetize(mm); nv += 1
print('velvetized', nv)
