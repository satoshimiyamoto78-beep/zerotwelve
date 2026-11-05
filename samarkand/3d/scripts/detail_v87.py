"""rev. 8.7 — central dome: gilded alem finial on the lantern cap (owner: 'nothing on the crown'); the dome itself is Ø5.0 now
(layout: clear of the aivan arcade and the booth fronts, centred on the 4-top axis x 6.0)"""
_rm('dome_finial')
GILT = mat('gilt_alem', (0.86, 0.63, 0.24), rough=0.22, metal=1.0)
for o_ in [o for o in bpy.data.objects if o.name.startswith('dome_lantern_cap_')]:
    lo_, hi_ = _bb(o_); cx_, cy_ = (lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2
    b = MB()
    b.lathe(0, 0, 0, [(0.0, 0.0), (0.075, 0.0), (0.075, 0.06), (0.05, 0.08), (0.06, 0.1), (0.04, 0.12), (0.035, 0.13)] +
            [(0.035 + 0.11 * math.sin(math.pi * k / 12), 0.13 + 0.22 * k / 12) for k in range(13)] +               # ball 1  (Ø 0.29)
            [(0.03, 0.37), (0.045, 0.39), (0.03, 0.41)] +
            [(0.03 + 0.08 * math.sin(math.pi * k / 12), 0.41 + 0.16 * k / 12) for k in range(13)] +                # ball 2  (Ø 0.22)
            [(0.025, 0.59), (0.04, 0.61), (0.025, 0.63)] +
            [(0.025 + 0.06 * math.sin(math.pi * min(1.0, k / 8)) * (1.0 if k <= 8 else 0.0), 0.63 + 0.02 * k) for k in range(1, 9)] +   # onion
            [(0.022, 0.80), (0.012, 0.9), (0.006, 1.0), (0.0, 1.06)], GILT, 32)                                       # spire
    inst(b.mesh('Dome_alem'), f'Dome_alem_{o_.name[-1]}', (cx_, cy_, hi_[2]), 0, 'Domes')
print('rev 8.7 dome alem ok')

# ---------------------------------------------------------------- CASCADE CHANDELIER under the dome (owner refs: Turkish cascade of
# perforated brass / copper globes on decorative chains from a pierced canopy plate; inverted cone, lowest over the centre table)
def perf_mat(name, col):
    """perforated sheet metal: dot holes (voronoi) glowing warm, metal between them"""
    if name in bl._mats: return bl._mats[name]
    mm = bpy.data.materials.new(name); mm.use_nodes = True; N = mm.node_tree.nodes; Lk = mm.node_tree.links
    out = N['Material Output']; pb = N['Principled BSDF']
    pb.inputs['Base Color'].default_value = (*col, 1); pb.inputs['Metallic'].default_value = 1.0; pb.inputs['Roughness'].default_value = 0.32
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (55, 55, 55)
    Lk.new(tc.outputs['Object'], mp.inputs['Vector'])
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'F1'; vo.inputs['Randomness'].default_value = 0.0; Lk.new(mp.outputs['Vector'], vo.inputs['Vector'])
    lt = N.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.2; Lk.new(vo.outputs['Distance'], lt.inputs[0])
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (1.0, 0.6, 0.25, 1); em.inputs['Strength'].default_value = 7.0
    mx = N.new('ShaderNodeMixShader'); Lk.new(lt.outputs['Value'], mx.inputs['Fac']); Lk.new(pb.outputs['BSDF'], mx.inputs[1]); Lk.new(em.outputs['Emission'], mx.inputs[2])
    Lk.new(mx.outputs['Shader'], out.inputs['Surface'])
    bl._mats[name] = mm; return mm
PERF = [perf_mat('perf_brass', (0.80, 0.60, 0.26)), perf_mat('perf_copper', (0.78, 0.40, 0.22))]
BRZ = mat('lamp_bronze', (0.22, 0.17, 0.12), rough=0.4, metal=1.0)
def _globe(b, x, y, zt, R, mm):
    """globe lamp whose hook is at (x, y, zt): collar, perforated sphere R with an equator band, bronze bottom cone + drop finial"""
    b.lathe(x, y, zt - 0.06, [(0.0, 0.0), (0.03, 0.0), (0.045, 0.02), (0.03, 0.045), (0.012, 0.055), (0.0, 0.06)], BRZ, 16)
    zc = zt - 0.06 - R * 0.95
    b.lathe(x, y, zc - R, [(R * math.sin(math.pi * k / 16), R * (1 - math.cos(math.pi * k / 16))) for k in range(17)], mm, 28)
    b.lathe(x, y, zc - 0.012, [(0.0, 0.0), (R * 1.015, 0.0), (R * 1.015, 0.024), (0.0, 0.024)], BRZ, 28)
    zb = zc - R * 0.92
    b.lathe(x, y, zb - 0.14, [(0.0, 0.0), (0.006, 0.0), (0.016, 0.03), (0.01, 0.05), (0.03, 0.08), (0.05, 0.12), (R * 0.45, 0.14), (0.0, 0.14)], BRZ, 16)
    return zb - 0.14
def _chain(b, x, y, z0, z1):
    """decorative chain as a beaded rod from z0 (top) down to z1"""
    L = z0 - z1; n = max(2, int(L / 0.045))
    prof = [(0.0, 0.0)] + [(0.006 + 0.005 * abs(math.sin(math.pi * k / 2)), L * k / (2 * n)) for k in range(2 * n + 1)] + [(0.0, L)]
    b.lathe(x, y, z1, prof, BRZ, 8)
_rm('Chandelier_dome')
dg_ = bpy.context.evaluated_depsgraph_get()
for d in D['domes']:
    cx, cy = d['c']
    hit = bpy.context.scene.ray_cast(dg_, Vector((cx, cy, 3.5)), Vector((0, 0, 1)), distance=6.0)
    zcrown = hit[1].z if hit[0] else ZR + d['rise']
    ZCAN = min(zcrown - 0.35, ZR + 0.55); RC = min(0.95, d['r'] * 0.4)
    b = MB()
    b.cyl(cx, cy, ZCAN + 0.012, zcrown, 0.016, BRZ, 10)                                    # hanging rod to the crown hook
    disc = SPt(cx, cy).buffer(RC, 64)
    cut = [SPt(cx + 0.62 * RC * math.cos(2 * math.pi * k / 12), cy + 0.62 * RC * math.sin(2 * math.pi * k / 12)).buffer(0.11 * RC, 24) for k in range(12)]
    cut += [star8(cx + 0.3 * RC * math.cos(2 * math.pi * k / 6 + 0.26), cy + 0.3 * RC * math.sin(2 * math.pi * k / 6 + 0.26), 0.09 * RC) for k in range(6)]
    put(b, disc.difference(SUnion(cut)).difference(SPt(cx, cy).buffer(0.05, 16)), ZCAN, ZCAN + 0.012, BRZ, 'xy')    # pierced canopy plate
    put(b, SPt(cx, cy).buffer(RC + 0.02, 64).difference(SPt(cx, cy).buffer(RC - 0.025, 64)), ZCAN - 0.02, ZCAN + 0.012, BRZ, 'xy')
    put(b, SPt(cx, cy).buffer(0.08, 24), ZCAN - 0.02, ZCAN + 0.012, BRZ, 'xy')
    LOW = TER + 2.3; HIGH = ZCAN - 0.75
    rings = [(0.0, 1), (0.33, 6), (0.6, 10), (0.85, 14)]                 # >= 330 between globe centres
    nlamp = 0
    for ri, (rr, n) in enumerate(rings):
        for k in range(n):
            a = 2 * math.pi * k / n + 0.3 * ri; x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            R = (0.16, 0.14, 0.12, 0.11)[ri] * (1.0 if k % 2 == 0 else 0.86)
            zbot = LOW + (HIGH - LOW) * (rr / 0.85) ** 1.2 + (0.0 if n == 1 else (0.19 if k % 2 else -0.0))
            ztop = zbot + 0.20 + 1.87 * R
            ztop = min(ztop, ZCAN - 0.08)
            _chain(b, x, y, ZCAN - 0.02, ztop); _globe(b, x, y, ztop, R, PERF[(k + ri) % 2]); nlamp += 1
    inst(b.mesh(f'Chandelier_cascade_{d["key"]}'), f'Chandelier_dome_{d["key"]}', (0, 0, 0), 0, 'Lights')
    for zz, ee in ((LOW + 0.5, 60), (LOW + 1.1, 50)):                                   # warm light from inside the cluster
        ld = bpy.data.lights.new(f'chand_light_{zz:.1f}', 'POINT'); ld.energy = ee; ld.color = (1.0, 0.7, 0.4); ld.shadow_soft_size = 0.4
        lo = bpy.data.objects.new(ld.name, ld); lo.location = (cx, cy, zz); coll('Lights').objects.link(lo)
    print('cascade chandelier', nlamp, 'globes, canopy z', round(ZCAN, 3), 'lowest', round(LOW, 3))

# ---------------------------------------------------------------- THE REAL TREE (owner photo): multi-stem mango-type tree, glossy
# lanceolate leaves in tip rosettes, crotons round the trunk. Replaces the 'trained chinar'. Crown kept under the skylight panjara.
MBARK = mat('mango_bark', (0.20, 0.17, 0.14), rough=0.9)
LEAF = [mat('mango_leaf_a', (0.06, 0.20, 0.05), rough=0.35), mat('mango_leaf_b', (0.10, 0.28, 0.07), rough=0.35)]
CROT = [mat('croton_red', (0.45, 0.06, 0.04), rough=0.4), mat('croton_orange', (0.75, 0.32, 0.05), rough=0.4), mat('croton_yellow', (0.70, 0.62, 0.12), rough=0.4), mat('croton_green', (0.08, 0.22, 0.06), rough=0.4)]
def _leaf(bm, mats_i, c, n_, t_, L, W):
    """lanceolate leaf polygon (6 verts) at c, blade along t_, facing n_"""
    u_ = n_.cross(t_).normalized()
    pts = [c, c + t_ * (L * 0.25) + u_ * (W * 0.5), c + t_ * (L * 0.6) + u_ * (W * 0.45), c + t_ * L, c + t_ * (L * 0.6) - u_ * (W * 0.45), c + t_ * (L * 0.25) - u_ * (W * 0.5)]
    f = bm.faces.new([bm.verts.new(p) for p in pts]); f.material_index = mats_i; return f
@cached
def a_mango(seed=7, ztop=3.35):
    import random; R_ = random.Random(seed); b = MB()
    b.lathe(0, 0, 0, [(0.0, 0.0), (0.26, 0.0), (0.2, 0.12), (0.17, 0.4), (0.18, 0.7), (0.22, 0.85), (0.0, 0.85)], MBARK, 20)
    tips = []
    for k in range(4):                                        # four stems from the low fork, leaning out
        a = 2 * math.pi * k / 4 + R_.uniform(-0.3, 0.3); p0 = (0.08 * math.cos(a), 0.08 * math.sin(a), 0.8)
        p1 = (0.45 * math.cos(a), 0.45 * math.sin(a), R_.uniform(2.0, 2.3)); b.rod(p0, p1, R_.uniform(0.075, 0.095), MBARK, 12)
        for j in range(3):                                    # branches into the crown
            a2 = a + R_.uniform(-0.7, 0.7); r2 = R_.uniform(0.85, 1.25); p2 = (r2 * math.cos(a2), r2 * math.sin(a2), R_.uniform(2.5, 2.85))
            b.rod(p1, p2, 0.04, MBARK, 8)
            for q in range(3):
                a3 = a2 + R_.uniform(-0.5, 0.5); r3 = r2 + R_.uniform(0.15, 0.4); p3 = (r3 * math.cos(a3), r3 * math.sin(a3), min(ztop - 0.25, p2[2] + R_.uniform(0.05, 0.35)))
                b.rod(p2, p3, 0.015, MBARK, 6); tips.append(p3)
    wood = b.mesh('Mango_wood')
    bm = bmesh.new(); V_ = Vector
    for p in tips:                                            # leaf rosettes at the shoot tips + infill clumps
        for _ in range(R_.randint(22, 30)):
            d = V_((R_.gauss(0, 1), R_.gauss(0, 1), R_.gauss(0, 0.6))).normalized()
            c = V_(p) + d * R_.uniform(0.0, 0.18); t_ = (d + V_((0, 0, -0.35))).normalized()
            n_ = (V_((R_.gauss(0, 0.5), R_.gauss(0, 0.5), 1.0))).normalized()
            if abs(n_.dot(t_)) > 0.95: continue
            if (c + t_ * 0.24).z > ztop: t_ = V_((t_.x, t_.y, -abs(t_.z))).normalized()
            _leaf(bm, R_.randrange(2), c, n_, t_, R_.uniform(0.18, 0.26), R_.uniform(0.045, 0.06))
    me = bpy.data.meshes.new('Mango_foliage'); bm.to_mesh(me); bm.free()
    for mm in LEAF: me.materials.append(mm)
    me['kit'] = 1
    return wood, me
@cached
def a_crotons(seed=11, r0=0.35, r1=0.92, n=9):
    import random; R_ = random.Random(seed); bm = bmesh.new(); V_ = Vector
    for k in range(n):
        a = 2 * math.pi * k / n + R_.uniform(-0.15, 0.15); rr = R_.uniform(r0 + 0.12, r1 - 0.15); cx, cy = rr * math.cos(a), rr * math.sin(a)
        for _ in range(38):
            az = R_.uniform(0, 2 * math.pi); el = R_.uniform(0.15, 1.0)
            t_ = V_((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el))).normalized()
            c = V_((cx, cy, R_.uniform(0.05, 0.35))); n_ = t_.cross(V_((-math.sin(az), math.cos(az), 0))).normalized()
            _leaf(bm, R_.randrange(4), c, n_, t_, R_.uniform(0.16, 0.24), R_.uniform(0.05, 0.075))
    me = bpy.data.meshes.new('Croton_foliage'); bm.to_mesh(me); bm.free()
    for mm in CROT: me.materials.append(mm)
    me['kit'] = 1
    return me
_rm('Chinar_trained', 'Chinar_crown')
for i_, (x, y) in enumerate(D['trees']):
    mb = MB(); mb.cyl(x, y, TER, TER + 0.06, 0.78, m['soil'] if 'soil' in m else MBARK, 48); inst(mb.mesh('Tree_soil'), f'Tree_soil_{i_ + 1}', (0, 0, 0), 0, 'Trees')
    wd_, fo_ = a_mango()
    inst(wd_, f'Chinar_trained_{i_ + 1}', (x, y, TER + 0.06), 0.3, 'Trees'); inst(fo_, f'Chinar_crown_{i_ + 1}', (x, y, TER + 0.06), 0.3, 'Trees')
    inst(a_crotons(), f'Croton_foliage_{i_ + 1}', (x, y, TER + 0.06), 0.0, 'Planting')
print('rev 8.7 mango tree + crotons ok')
