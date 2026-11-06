"""rev. 10.4 (owner: 'the things on the tables stick out past the tables and hang in the air'): every table set is fitted to the
top of the table under it — centred, scaled down to the top minus a 40 mm margin, set on the top surface."""
TOPS = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(('Table_', 'Aivan_table_', 'Booth', 'Majlis_table', 'Tent_octatable', 'Tapchan_lowtable')) and 'table' in o.name.lower() and 'tableset' not in o.name.lower()]
TB = [(o, *_bb(o)) for o in TOPS]
nf = 0
for s_ in [o for o in bpy.data.objects if o.type == 'MESH' and ('tableset' in o.name.lower() or o.name.startswith(('Tableware', 'Aivan_tableware', 'booth_tableware', 'tables_tableware')))]:
    lo, hi = _bb(s_); cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    best = None
    for t, tl, th in TB:
        if tl[0] - 0.05 < cx < th[0] + 0.05 and tl[1] - 0.05 < cy < th[1] + 0.05 and abs(th[2] - lo[2]) < 0.25: best = (t, tl, th)
    if not best: continue
    t, tl, th = best; W, Dp = th[0] - tl[0] - 0.08, th[1] - tl[1] - 0.08
    k = min(1.0, W / max(1e-3, hi[0] - lo[0]), Dp / max(1e-3, hi[1] - lo[1]))
    s_.scale = (s_.scale[0] * k, s_.scale[1] * k, s_.scale[2]); bpy.context.view_layer.update()
    lo, hi = _bb(s_)
    s_.location.x += (tl[0] + th[0]) / 2 - (lo[0] + hi[0]) / 2; s_.location.y += (tl[1] + th[1]) / 2 - (lo[1] + hi[1]) / 2; s_.location.z += th[2] - lo[2]
    bpy.context.view_layer.update(); nf += 1
print('rev 10.4 table sets fitted', nf)
