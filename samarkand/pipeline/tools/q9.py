import sys; sys.path.insert(0, sys.argv[1])
from cad import CAD
c = CAD(sys.argv[2])
circ=[];txt=[]
for kind,d,lay,e in c.explode():
    if kind=='text':
        p,s,h=d
        if 925000<p[0]<975000 and -388000<p[1]<-335000 and len(s)<=3: txt.append((round(p[0]),round(p[1]),s,lay,round(h)))
for t in sorted(txt,key=lambda t:(t[0],t[1])):
    if t[0]>969000 or t[1]>-341000 or t[1]<-381000: print(t)
