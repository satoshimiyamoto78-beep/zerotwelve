"""rev. 9.6 (owner 2026-11-05: 'Carpets' folder in Drive, 19 Persian / tribal rug photos): every Persian-rug material in the model
(wall carpets, ceiling + flying carpets, corridor rugs, bar wall carpet, majlis backdrop medallion) is replaced by one of the owner's
photographed rugs; each object gets its own rug in turn, orientation chosen from the UV direction so nothing is stretched sideways."""
RUGMATS = {'carpet1_uv', 'carpet2_uv', 'oldrug_uv', 'rug_old_crop_uv', 'rug_persian_navy_uv', 'rug_persian_uv'}
NRUG = 19
def rugmat(k, rot):
    nm = f'rug_p{k:02d}{"_r" if rot else ""}_uv'
    if nm in bl._mats: return bl._mats[nm]
    mm = uvmat(nm, f'rug_p{k:02d}{"_r" if rot else ""}.jpg', rough=0.92, sheen=0.6); pile_shader(mm); return mm
def uv_aspect(o_, slot):
    """world length of one UV unit along u and along v, averaged over the faces using `slot`"""
    me = o_.data; uvl = me.uv_layers.active
    if uvl is None: return 1.0, 1.0
    mw = o_.matrix_world; Lu = Lv = 0.0; n = 0
    for p in me.polygons:
        if p.material_index != slot or len(p.loop_indices) < 3: continue
        li = list(p.loop_indices); a, b, c = li[0], li[1], li[2]
        P = [mw @ me.vertices[me.loops[i].vertex_index].co for i in (a, b, c)]; U = [uvl.data[i].uv for i in (a, b, c)]
        e1, e2 = P[1] - P[0], P[2] - P[0]; d1, d2 = U[1] - U[0], U[2] - U[0]
        det = d1.x * d2.y - d2.x * d1.y
        if abs(det) < 1e-9: continue
        dPdu = (e1 * d2.y - e2 * d1.y) / det; dPdv = (e2 * d1.x - e1 * d2.x) / det
        Lu += dPdu.length; Lv += dPdv.length; n += 1
        if n > 40: break
    return (Lu / n, Lv / n) if n else (1.0, 1.0)
k_ = 0; done = []
for o_ in sorted([o for o in bpy.data.objects if o.type == 'MESH'], key=lambda o: o.name):
    for si, mm in enumerate(o_.data.materials):
        if mm and mm.name in RUGMATS:
            Lu, Lv = uv_aspect(o_, si)
            if o_.data.users > 1: o_.data = o_.data.copy()
            o_.data.materials[si] = rugmat(k_ % NRUG + 1, Lu > Lv * 1.05); done.append((o_.name, k_ % NRUG + 1, Lu > Lv * 1.05)); k_ += 1
print('rev 9.6 rugs replaced on', len(done), 'slots:', done[:40])
