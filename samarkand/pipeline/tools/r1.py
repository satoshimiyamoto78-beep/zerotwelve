import sys; sys.path.insert(0, sys.argv[1])
from cad import CAD, render
c = CAD(sys.argv[2])
import pickle
print(render(c, (918000, -320000, 1080000, -195000), sys.argv[3], w_px=3200, grid=10000))
