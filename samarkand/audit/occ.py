import bpy, numpy as np, json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
TER=-0.45; X0,Y0,X1,Y1=-8.0,-1.0,14.5,38.5; S=50   # px per m
W,H=int((X1-X0)*S),int((Y1-Y0)*S)
SKIPC={'People','Context','Roof_skin','Roof_structure','Carpet_ceiling','Floors','Lights','Lights.001','Building'}
SOFT=('foliage','leaf','Banana','shrub','flowers','curtain','Curtain','Jasmine','Bougain','Herbs','rug','carpet','Carpet','swag','canopy','Areca','palm','Palm','Ficus_foliage','Olive_foliage','frond','Pomegranate','Plumeria','sash')
def raster(z0,z1,only=None):
    T=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render: continue
        c=o.users_collection[0].name if o.users_collection else ''
        if only is None and (c in SKIPC or any(s in o.name for s in SOFT)): continue
        if only is not None and c not in only: continue
        mw=o.matrix_world; me=o.data; me.calc_loop_triangles()
        co=np.array([mw@v.co for v in me.vertices]) if len(me.vertices) else None
        if co is None: continue
        if co[:,2].max()<z0 or co[:,2].min()>z1: continue
        for t in me.loop_triangles:
            p=co[list(t.vertices)]
            if p[:,2].max()<z0 or p[:,2].min()>z1: continue
            T.append(p[:,:2].copy())
    return np.array(T,dtype=np.float32)
occ=raster(TER+0.20,TER+1.90); np.save('audit/occ_t.npy',occ)
low=raster(TER+1.90,TER+2.10,only={'Lights','Lights.001','Carpet_ceiling','Roof_structure','Bukhara_dome','Bukhara_dome.001','Corridor','Corridor.001','Aivan','Booths','Tapchans_tent','Bar','Furniture','Mangal','Street_facade','North_gate'})
np.save('audit/low_t.npy',low)
# object list of low headroom items
res=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    c=o.users_collection[0].name if o.users_collection else ''
    if c in ('Lights','Lights.001','Carpet_ceiling','Roof_structure','Bukhara_dome','Bukhara_dome.001','Corridor','Corridor.001','North_gate'):
        P=[o.matrix_world@Vector(b) for b in o.bound_box]; zmin=min(p.z for p in P)
        if zmin-TER<2.12: res.append((o.name,c,round(zmin-TER,2),round(sum(p.x for p in P)/8,2),round(sum(p.y for p in P)/8,2)))
json.dump(res,open('audit/lowobj.json','w')); print(len(res))
