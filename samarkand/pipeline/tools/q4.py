import sys, re, collections; sys.path.insert(0, sys.argv[1])
from cad import CAD
c = CAD(sys.argv[2])
# fp2 grid lines + balcony geometry east of facade
hl=set(); east=collections.defaultdict(list); lv=[]
for kind,d,lay,e in c.explode():
    if kind in('seg','poly'):
        xs=[p[0] for p in d]; ys=[p[1] for p in d]
        if lay=='8l NET TO' and kind=='seg' and abs(ys[0]-ys[1])<1 and -447000<ys[0]<-400000 and max(xs)>960000: hl.add(round(ys[0]))
        if -447000<min(ys) and max(ys)<-400000 and max(xs)>965600 and min(xs)>964000 and max(xs)<969500:
            east[lay].append([(round(x),round(y)) for x,y in d] if len(d)<8 else ('poly',len(d),round(min(xs)),round(min(ys)),round(max(xs)),round(max(ys))))
    elif kind=='text':
        p,s,h=d
        if re.match(r'^\s*[+±-]?\s*\d+[.,]\d{3}\s*$',s) and 1030000<p[0]<1075000 and -600000<p[1]<-350000: lv.append((round(p[0]),round(p[1]),s.strip(),lay))
print('fp2 grid y',sorted(hl))
for k,v in east.items():
    print('==',k,len(v))
    for x in v[:25]: print('   ',x)
print('levels in elevations:'); 
for x in sorted(lv,key=lambda t:(t[1]//50000,t[0])): print('  ',x)
