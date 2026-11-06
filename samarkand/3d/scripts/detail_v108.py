"""rev. 10.8 (owner: 'wooden elements still poor and generic — printed carving, wavy walnut'):
  * walnut: new straight-grain rift-sawn texture (tools/walnut_tex.py) replaces the wavy one on every walnut part
  * printed carving (chairs, tables, cabinets, hall door, skylight panjara, tapchan, cornice, rotunda, vitrines, Khiva gate) ->
    real chip carving: the ground is cut 5 mm down (dark walnut), the motifs stay at the face: 8-point stars with small
    diamonds between them (girih), cut on every face that carried the print
  * printed jali (Khiva gate, sarch) -> real lattice: crossed walnut slats 18 mm over a 15 mm deep dark void"""
from shapely.geometry import LineString as _LS
WDARK = mat('walnut_cut', (0.11, 0.06, 0.035), rough=0.7)
VOID = mat('jali_void', (0.015, 0.012, 0.01), rough=1.0)
WOOD = XW['wd']
def _stars_d(P, R, mm):
    sq = _box(-R * 0.72, -R * 0.72, R * 0.72, R * 0.72); star = sq.union(_aff.rotate(sq, 45, origin=(0, 0)))
    dia = _P([(0, -R * 0.42), (R * 0.42, 0), (0, R * 0.42), (-R * 0.42, 0)])
    def gen(u0, v0, u1, v1):
        for i in range(math.floor(u0 / P) - 1, math.ceil(u1 / P) + 1):
            for j in range(math.floor(v0 / P) - 1, math.ceil(v1 / P) + 1):
                yield _aff.translate(star, i * P, j * P), mm
                yield _aff.translate(dia, i * P + P / 2, j * P + P / 2), mm
    return gen
def _lattice(pitch, w, mm):
    def gen(u0, v0, u1, v1):
        L = (u1 - u0) + (v1 - v0) + 1
        for s in (1, -1):
            for k in range(math.floor((v0 - s * u1 - L) / pitch), math.ceil((v1 - s * u0 + L) / pitch)):
                c = k * pitch
                yield _LS([(u0 - 1, c + s * (u0 - 1)), (u1 + 1, c + s * (u1 + 1))]).buffer(w / 2, cap_style=2), mm
    return gen
PAT.clear()
PAT.update({
    'carvedref_t': (WDARK, 0.005, _stars_d(0.075, 0.03, WOOD), WOOD, 0.05),
    'carved_t': (WDARK, 0.006, _stars_d(0.12, 0.048, WOOD), WOOD, 0.07),
    'jali': (VOID, 0.015, _lattice(0.07, 0.018, WOOD), WOOD, 0.08),
})
SIDES.clear(); SIDES.update({'jali', 'carved_t'})
realize_all(skip=('Bukhara_vitrine_', 'vase'))
print('rev 10.8 carving: meshes', nmesh, 'objects', nobj, 'culled', ncull)
# joint: the plaster street bench ran into the sarch screen -> the bench stops at the screen's face (cut + closed end)
_s = bpy.data.objects.get('sarch'); _b = bpy.data.objects.get('Street_bench_plaster_5')
if _s and _b:
    import bmesh as _bmj
    lo_, hi_ = _bb(_s); xc = hi_[0] + 0.001
    bm_ = _bmj.new(); bm_.from_mesh(_b.data); bm_.transform(_b.matrix_world)
    geom = bm_.verts[:] + bm_.edges[:] + bm_.faces[:]
    r_ = _bmj.ops.bisect_plane(bm_, geom=geom, plane_co=(xc, 0, 0), plane_no=(1, 0, 0), clear_inner=True)
    cut = [e for e in r_['geom_cut'] if isinstance(e, _bmj.types.BMEdge)]
    if cut: _bmj.ops.holes_fill(bm_, edges=cut)
    bm_.transform(_b.matrix_world.inverted()); me_ = bpy.data.meshes.new(_b.data.name + '_cut'); bm_.to_mesh(me_); bm_.free()
    for mm in _b.data.materials: me_.materials.append(mm)
    _b.data = me_
