import sys, collections; sys.path.insert(0, sys.argv[1])
from cad import CAD
c = CAD(sys.argv[2])
x0,y0,x1,y1=[float(v) for v in sys.argv[3].split(',')]
skip=set(sys.argv[4].split('|'))
by=collections.defaultdict(list)
for kind,d,lay,e in c.explode():
    if kind in('seg','poly') and lay not in skip:
        xs=[p[0] for p in d]; ys=[p[1] for p in d]
        if max(xs)>=x0 and min(xs)<=x1 and max(ys)>=y0 and min(ys)<=y1 and (max(ys)-min(ys)>3000 or max(xs)-min(xs)>1500):
            by[lay].append(d)
for k,v in by.items():
    print('==',k,len(v))
    for d in v[:30]:
        xs=[p[0] for p in d]; ys=[p[1] for p in d]
        print('   n=%d bbox %d,%d..%d,%d'%(len(d),min(xs),min(ys),max(xs),max(ys)), [(round(x),round(y)) for x,y in d][:6])
