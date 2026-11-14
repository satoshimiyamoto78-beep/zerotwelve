import bpy, numpy as np, json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='r12v83/samarkand-base3d-R12.blend')
TER=-0.45; sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.users_collection and o.users_collection[0].name in ('People','Context'): o.hide_viewport=True; o.hide_set(True)
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
dist=np.load('audit/dist.npy'); X0,Y1,S=-8.0,38.5,50
def clear(x,y): return dist[int((Y1-y)*S),int((x-X0)*S)]
def sx(y): return 12.639+(9.465-12.639)*(y-4.1)/(36.3-4.1)
# 1 headroom over walkable cells + roof cover
low=[]; unc=[]; hs=[]
for yi in range(2,371,2):
    y=yi/10
    for xi in range(2,int(sx(y)*10),2):
        x=xi/10
        if clear(x,y)<0.3: continue
        hit,p,n,i,o,m=sc.ray_cast(dg,(x,y,TER+0.3),(0,0,1))
        if not hit: unc.append((x,y)); continue
        h=p.z-TER; hs.append(h)
        if h<2.1: low.append((round(h,2),x,y,o.name))
import collections
c=collections.defaultdict(list)
for h,x,y,nm in low: c[nm].append((h,x,y))
print('LOW HEADROOM (<2.10 over walkable floor):')
for nm,v in sorted(c.items(), key=lambda kv:min(kv[1])): print('  ',nm,'min',min(v)[0],'cells',len(v),'at',min(v)[1:])
print('UNCOVERED walkable cells (no roof above):',len(unc))
if unc:
    a=np.array(unc); print('  bbox x',a[:,0].min(),a[:,0].max(),'y',a[:,1].min(),a[:,1].max())
    for y0 in range(0,38,4):
        s=a[(a[:,1]>=y0)&(a[:,1]<y0+4)]
        if len(s): print('   y',y0,'-',y0+4,':',len(s),'cells, x',s[:,0].min(),'-',s[:,0].max())
print('ceiling height over walkable floor: min %.2f median %.2f max %.2f'%(min(hs),np.median(hs),max(hs)))
# 2 structure: columns vs beams
def bb(o):
    P=[o.matrix_world@Vector(b) for b in o.bound_box]; return np.array([[min(p[i] for p in P) for i in range(3)],[max(p[i] for p in P) for i in range(3)]])
RS=[o for o in bpy.data.objects if o.type=='MESH' and o.users_collection and o.users_collection[0].name=='Roof_structure']
print('ROOF STRUCTURE objects:',len(RS))
cols=[o for o in RS if o.name.lower().startswith(('column','steel_col','dome_column','edge_post','pocket_column')) and 'plate' not in o.name.lower()]
beams=[o for o in RS if 'beam' in o.name.lower()]
purl=[o for o in RS if o.name.lower().startswith('purlin') and 'cleat' not in o.name.lower()]
print(' columns',len(cols),'beams',len(beams),'purlins',len(purl))
for o in cols:
    b=bb(o); top=b[1][2]; cx,cy=(b[0][0]+b[1][0])/2,(b[0][1]+b[1][1])/2
    hit,p,n,i,ob,m=sc.ray_cast(dg,(cx,cy,top+0.01),(0,0,1),distance=0.6)
    foot=b[0][2]-TER
    flag='' if (hit and p.z-top<0.05) else '  <-- NOTHING ON TOP within 50 mm' 
    print(f'  {o.name:28s} x {cx:5.2f} y {cy:5.2f} foot {foot:+.2f} top {top-TER:+.2f} carries {ob.name if hit else None} gap {((p.z-top)*1000 if hit else -1):.0f} mm{flag}')
sp=sorted(set(round(bb(o)[0][0]+0.04,2) for o in purl)); print(' purlin x lines',sp,'spacing',[round(b-a,2) for a,b in zip(sp,sp[1:])])
for o in beams:
    b=bb(o); print(f'  {o.name:22s} x {b[0][0]:.2f}..{b[1][0]:.2f} y {b[0][1]:.2f}..{b[1][1]:.2f} z {b[0][2]-TER:.2f}..{b[1][2]-TER:.2f} span {max(b[1][0]-b[0][0],b[1][1]-b[0][1]):.2f}')
