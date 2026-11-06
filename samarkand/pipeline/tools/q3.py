import sys, collections; sys.path.insert(0, sys.argv[1])
from cad import CAD
c = CAD(sys.argv[2])
x0,y0,x1,y1 = [float(v) for v in sys.argv[3].split(",")]
by = collections.defaultdict(list)
for kind,d,lay,e in c.explode():
    if kind in('seg','poly'):
        if any(x0<=x<=x1 and y0<=y<=y1 for x,y in d):
            by[(lay,e['type'])].append(d)
    elif kind=='text':
        p,s,h=d
        if x0<=p[0]<=x1 and y0<=p[1]<=y1: print('TEXT',lay,round(p[0]),round(p[1]),s)
    elif kind=='dim':
        p=e.get('textPoint')
        if p and x0<=p['x']<=x1 and y0<=p['y']<=y1: print('DIM',lay,round(e['measurement']),[ (round(e[k]['x']),round(e[k]['y'])) for k in ('subDefinitionPoint1','subDefinitionPoint2','definitionPoint') if k in e])
for k,v in sorted(by.items()):
    print('==',k,len(v))
    for d in v[:40]:
        if len(d)<=6: print('   ',[(round(x),round(y)) for x,y in d])
        else:
            xs=[p[0] for p in d]; ys=[p[1] for p in d]; print('    poly n=%d bbox %d,%d..%d,%d'%(len(d),min(xs),min(ys),max(xs),max(ys)))
