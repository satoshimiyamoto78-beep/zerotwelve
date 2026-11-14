"""Export everything the 3D base model needs from layout_r12.py (+ roof geometry) into one JSON, in metres.
Args: zone.json base.dxf outdir  ->  outdir/samarkand-3d-data-R9.json
"""
import sys, json, runpy
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union, split

argv = sys.argv[:]
sys.argv = ['layout_r12.py'] + argv[1:4]
G = runpy.run_path(__file__.replace('export3d_r12.py', 'layout_r12.py'))
sys.argv = argv
OUT = argv[3]
xb, U = G['xb'], G['U']
k = 0.001
def rings(g):
    out = []
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty or p.geom_type != 'Polygon': continue
        out.append([[round(x * k, 4), round(y * k, 4)] for x, y in p.exterior.coords[:-1]])
    return out
def solid_pieces(g):
    g = g.buffer(-2, join_style=2).buffer(2, join_style=2)          # open pinch points (self-touching rings) and drop < 4 mm slivers
    return [q for q in holefree(g) if q.area > 1e3]
def holefree(g):
    """split polygons with holes into hole-free pieces (cuts along y through every hole)"""
    res = []
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty: continue
        if not p.interiors: res.append(p); continue
        cuts = sorted({round(y) for r in p.interiors for y in (r.bounds[1], r.bounds[3])})
        pieces = [p]
        for y in cuts:
            nxt = []
            for q in pieces:
                try: nxt.extend(split(q, LineString([(-1e5, y), (1e5, y)])).geoms)
                except Exception: nxt.append(q)
            pieces = nxt
        for q in pieces: res.extend(holefree(q) if q.interiors else [q])
    return res

COURTS = []                                                          # rev. 7: no open courts; one skylight over the chinar
C_ = G['C']
roof_p = U.difference(unary_union([C_(*d['c'], d['r'], 96) for d in G['DOMES']]))     # purlins run on under the skylight glass
roof = roof_p.difference(G['SKY'])
D = dict(
    rev=G['REV'],
    items=[dict(kind=it['kind'], poly=rings(it['geom']) if it['geom'].geom_type != 'LineString' else [[[round(x * k, 4), round(y * k, 4)] for x, y in it['geom'].coords]],
                **({'back': it['back']} if 'back' in it else {}), **({'mods': it['mods'], 'axis': it['axis']} if 'mods' in it else {}))
           for it in G['items']],
    floor=rings(G['FLOOR']), plat=rings(G['PLAT']), alley=rings(G['ALLEY']), kids=rings(G['KIDS']), planter=[rings(q)[0] for q in solid_pieces(G['planter'].difference(box(G['BX0'], G['BY0'], G['BX1'], G['BY1'])))],
    photo_plant=rings(G['photo_plant']), bbq_plant=rings(G['bbq_plant'].difference(unary_union([box(cx - 380, cy - 380, cx + 380, cy + 380) for cx, cy in G['cols']])).buffer(0)), zone=rings(U),
    roof=[rings(q)[0] for q in holefree(roof)], courts=[rings(c)[0] for c in COURTS],
    beams=[[round(y * k, 4), round(xb(y) * k, 4)] for y in G['TRUSS_Y']],
    cols=[[round(x * k, 4), round(y * k, 4)] for x, y in G['cols']],
    lot=[[round(xb(y) * k, 4), round(y * k, 4)] for y in (-3000, 42000)],
    trees=[[t[0] * k, t[1] * k] for t in (G['TREE_S'],)], skylight=[round(v * k, 4) for v in G['SKY'].bounds],
    plants=[[sp, round(x * k, 4), round(y * k, 4), round(r * k, 4)] for sp, x, y, r in G['PL']],
    doors=[[a * k, b * k, op] for a, b, op in G['DOORS'].values()],
    ent=[G['ENT'][0] * k, G['ENT'][1] * k], tun=[G['TUN'][0] * k, G['TUN'][1] * k],
    hz=[G['HZC'][0] * k, G['HZC'][1] * k], tent=[v * k for v in (G['TX0'], G['TY0'], G['TX1'], G['TY1'])], tents=[[v * k for v in T] for T in G['TENTS']],
    domes=[dict(key=d['key'], c=[d['c'][0] * k, d['c'][1] * k], r=d['r'] * k, oc=d['oc'] * k, rise=d['rise'] * k, lantern=d.get('lantern', 0) * k) for d in G['DOMES']],
    dome_ring=G['DOME_RING'] * k, rot=[G['ROTC'][0] * k, G['ROTC'][1] * k, G['ROTR'] * k], gate=[G['GATE'][0] * k, G['GATE'][1] * k],
    staff=rings(G['STAFF']),
    **(lambda: (lambda FL, MED, BBQ, AR, HB, HZ: dict(
        floor_main=[rings(q)[0] for q in solid_pieces(FL.difference(unary_union([G['ALLEY'], G['KIDS'], BBQ, MED, AR, box(G['xi'](G['ENT'][0]) - 200, G['ENT'][0], xb(G['ENT'][0]) + 300, G['ENT'][1])])))],
        inlays=dict(alley=[rings(q)[0] for q in solid_pieces(G['ALLEY'])], kids=[rings(q)[0] for q in solid_pieces(G['KIDS'])], bbq=rings(BBQ),
                    medallion=[rings(q)[0] for q in solid_pieces(MED.difference(AR))], aryk=rings(AR)),
        hauz_ring=[rings(q)[0] for q in solid_pieces(HB.difference(HZ))], hauz_rim_y1=HB.bounds[3] * k))(
        G['FLOOR'], [it['geom'] for it in G['items'] if it['kind'] == 'medallion'][0], G['R'](G['BX0'], G['BY0'], G['BX1'], G['BY1']), G['ARYK'],
        [it['geom'] for it in G['items'] if it['kind'] == 'hauzborder'][0], [it['geom'] for it in G['items'] if it['kind'] == 'hauz'][0]))(),
    booths=[[a * k, b * k, xw * k, G['xi'](b) * k, th] for (a, b, xw), th in zip(G['booth_west'], ['sogd', 'sasan', 'saman', 'khorezm', 'timur', 'shahr', 'margil', 'pamir'])],
    booth_names=G['T']['ru']['themes'][:8] if 'T' in G else [],
    bbq=[v * k for v in (G['BX0'], G['BX1'], G['BY0'], G['BY1'])], tap=[y * k for y in G['TAP']], hzc=[G['HZC'][0] * k, G['HZC'][1] * k],
    ab=dict(y=[y * k for y in G['AB_Y']], x1=G['AB_X1'] * k),
    rail=[[[a[0] * k, a[1] * k], [b[0] * k, b[1] * k]] for a, b in G['RAIL']],
    drive=rings(Polygon([(0, G['yr'](0)), (xb(36500), G['yr'](xb(36500))), tuple(G['Z2']), (0, G['V']['Z1_NW'][1])])),
    seats=G['total'],
)
# purlins (constant x lines clipped to the roof) and the street steps of the entrance gap
pur = []
for kx in range(1, 14):
    x = kx * 1000 - 200
    ln_ = LineString([(x, -3000), (x, 41000)]).intersection(roof_p)
    for g in getattr(ln_, 'geoms', [ln_]):
        if g.length > 300: c = list(g.coords); pur.append([round(x * k, 4), round(min(c[0][1], c[-1][1]) * k, 4), round(max(c[0][1], c[-1][1]) * k, 4)])
D['purlins'] = pur
D['street_steps'] = [round((G['xi'](G['ENT'][0]) - 200) * k, 4), round((xb(G['ENT'][0]) + 300) * k, 4)]
D['yr0'] = G['yr'](0) * k
json.dump(D, open(f'{OUT}/samarkand-3d-data-{G["REV"]}.json', 'w'))
print('3d data ok', len(D['items']), 'items,', len(D['roof']), 'roof pieces')
