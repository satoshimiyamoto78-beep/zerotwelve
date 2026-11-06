import sys; sys.path.insert(0, sys.argv[1])
from cad import CAD, render
c = CAD(sys.argv[2])
bb = tuple(float(v) for v in sys.argv[4].split(','))
print(render(c, bb, sys.argv[3], w_px=int(sys.argv[5]), grid=float(sys.argv[6])))
