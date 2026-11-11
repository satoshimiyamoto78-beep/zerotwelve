"""rev. 12.0 block 3 — STREET FRONT (owner: 'the facade is unclear, optimise / lighten it; holes by the benches'):
  * the terrace plinth along the street is one plastered element: the planter top is re-made as a continuous slab (the round
    recesses left by removed tubs are gone) and takes the same white lime render as the benches; the brick band under it too
  * (beam ends at the columns: plain boxed casing, no stepped corbels — detail_v110)"""
_LIME2 = bpy.data.materials.get('lime_render') or mat('lime_render', (0.86, 0.83, 0.77), rough=0.95)
for o_ in [o for o in bpy.data.objects if o.name == 'planter_soil' or o.name.startswith('planter_soil.')]: bpy.data.objects.remove(o_)
prism('planter_soil', D['planter'], TER - 0.03, TER, _LIME2, 'Planting')
for nm_ in ('planter_band',):
    for o_ in [o for o in bpy.data.objects if o.name == nm_ or o.name.startswith(nm_ + '_real')]:
        for i_ in range(len(o_.data.materials)): o_.data.materials[i_] = _LIME2
print('rev 12.0 block 3: street plinth unified')
# close what is still open: cells where the plinth body shows from above (not covered by the top slab)
bpy.context.view_layer.update(); _dg = bpy.context.evaluated_depsgraph_get(); _dg.update()
_hid = [o for o in bpy.data.objects if o.users_collection and o.users_collection[0].name in ('Planting', 'Trees', 'People') and o.name != 'planter_soil' and not o.hide_get()]
for o_ in _hid: o_.hide_set(True)
_dg = bpy.context.evaluated_depsgraph_get(); _dg.update()
_bo = bpy.data.objects.get('planter_band'); _lo, _hi = _bb(_bo); _S = 25
_cells = set()
for j in range(int((_hi[1] - _lo[1]) * _S)):
    for i in range(int((_hi[0] - _lo[0]) * _S)):
        x, y = _lo[0] + (i + .5) / _S, _lo[1] + (j + .5) / _S
        h = bpy.context.scene.ray_cast(_dg, (x, y, TER + 0.02), (0, 0, -1), distance=0.2)
        if h[0] and h[4].name.startswith('planter_band') and h[1].z < TER - 0.02: _cells.add((i, j))
for o_ in _hid: o_.hide_set(False)
_cl = []
while _cells:
    st = [_cells.pop()]; cur = [st[0]]
    while st:
        i, j = st.pop()
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (i + d[0], j + d[1])
            if q in _cells: _cells.remove(q); st.append(q); cur.append(q)
    _cl.append(cur)
b = MB(); nfill = 0
for cur in _cl:
    if len(cur) < 4: continue
    xs = [c[0] for c in cur]; ys = [c[1] for c in cur]
    x0, x1 = _lo[0] + min(xs) / _S, _lo[0] + (max(xs) + 1) / _S; y0, y1 = _lo[1] + min(ys) / _S, _lo[1] + (max(ys) + 1) / _S
    if x1 - x0 > 1.6 or y1 - y0 > 1.6: continue                      # long strips = the band's own exposed edge, not a hole
    r = max(x1 - x0, y1 - y0) / 2 + 0.03
    b.cyl((x0 + x1) / 2, (y0 + y1) / 2, TER - 0.029, TER - 0.0005, r, _LIME2, 32); nfill += 1
if nfill: inst(b.mesh('Street_plinth_caps'), 'Street_plinth_caps', (0, 0, 0), 0, 'Street_facade')
print('rev 12.0 block 3: plinth holes closed', nfill, 'clusters', len(_cl))
