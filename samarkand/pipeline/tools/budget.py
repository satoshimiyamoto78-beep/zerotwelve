import json, sys
from shapely.geometry import shape, Polygon, box
from shapely.ops import unary_union
d = json.load(open(sys.argv[1]))
z = json.load(open(sys.argv[2]))
print('usable', d.get('zones_m2'))
