import sys; sys.path.insert(0, sys.argv[1])
from cad import CAD
c = CAD(sys.argv[2])
for kind,d,lay,e in c.explode():
    if kind=='poly' and lay in('DMANH','8l NET TO') and len(d)>=10 and max(x for x,y in d)>1015000 and min(y for x,y in d)>-300000 and max(y for x,y in d)>-230000:
        print(lay, e['type'], e.get('handle'), len(d), e.get('flag'))
        print('   ', [(round(x),round(y)) for x,y in d if x>995000])
