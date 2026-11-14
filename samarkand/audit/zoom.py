import numpy as np, sys
from PIL import Image, ImageDraw
X0,Y0,X1,Y1=-8.0,-1.0,14.5,38.5; S=50
dist=np.load('audit/dist.npy'); H,W=dist.shape
x0,y0,x1,y1=[float(a) for a in sys.argv[1:5]]; out=sys.argv[5]
r0,r1=int((Y1-y1)*S),int((Y1-y0)*S); c0,c1=int((x0-X0)*S),int((x1-X0)*S)
d=dist[r0:r1,c0:c1]; img=np.zeros(d.shape+(3,),np.uint8)
img[d==0]=(50,50,50)
for lo,hi,col in ((0.001,0.3,(230,60,60)),(0.3,0.375,(245,150,60)),(0.375,0.45,(250,220,110)),(0.45,0.6,(190,230,170)),(0.6,99,(140,200,150))): img[(d>lo)&(d<=hi)]=col
im=Image.fromarray(img).resize((d.shape[1]*3,d.shape[0]*3),Image.NEAREST); dr=ImageDraw.Draw(im)
k=S*3
import math
for xg in range(math.ceil(x0),int(x1)+1): dr.line([((xg-x0)*k,0),((xg-x0)*k,im.size[1])],fill=(0,0,255)); dr.text(((xg-x0)*k+2,2),f'x{xg}',fill=(0,0,255))
for yg in range(math.ceil(y0),int(y1)+1): dr.line([(0,(y1-yg)*k),(im.size[0],(y1-yg)*k)],fill=(0,0,255)); dr.text((2,(y1-yg)*k+2),f'y{yg}',fill=(0,0,255))
im.save(out)
