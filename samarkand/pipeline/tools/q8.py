import sys, collections; sys.path.insert(0, sys.argv[1])
from cad import CAD
c = CAD(sys.argv[2])
x0,y0,x1,y1=[float(v) for v in sys.argv[3].split(',')]
cnt=collections.Counter(); ex={}
for kind,d,lay,e in c.explode():
    if kind in('seg','poly'):
        if any(x0<=x<=x1 and y0<=y<=y1 for x,y in d) and max(x for x,y in d)<990000:
            cnt[(lay,e['type'])]+=1; ex.setdefault((lay,e['type']),[]).append([(round(x),round(y)) for x,y in d][:4])
for k,v in cnt.most_common(): print(k,v, ex[k][:3])
