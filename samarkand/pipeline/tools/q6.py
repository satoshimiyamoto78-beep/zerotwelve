import sys, json; sys.path.insert(0, sys.argv[1])
from cad import CAD
c = CAD(sys.argv[2])
for kind,d,lay,e in c.explode():
    if kind=='poly' and e.get('handle')=='3214':
        pts=[(round(x,1),round(y,1)) for x,y in d]
        i=[k for k,p in enumerate(pts) if abs(p[0]-1016605)<2][0]
        print(i, len(pts), pts[max(0,i-4):i+8], 'last', pts[-3:], 'first', pts[:3])
        json.dump(pts, open(sys.argv[3],'w'))
