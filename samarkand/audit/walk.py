import numpy as np, json
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
X0,Y0,X1,Y1=-8.0,-1.0,14.5,38.5; S=50; W,H=int((X1-X0)*S),int((Y1-Y0)*S)
def rast(f):
    T=np.load(f); im=Image.new('L',(W,H),0); d=ImageDraw.Draw(im)
    for p in T: d.polygon([((q[0]-X0)*S,(Y1-q[1])*S) for q in p],fill=255,outline=255)
    return np.asarray(im)>0
occ=rast('audit/occ_t.npy'); low=rast('audit/low_t.npy')
def px(x,y): return int((Y1-y)*S),int((x-X0)*S)
# terrace outline: inside x 0..street line, y 0..37.1 (+kids zone)
yy,xx=np.mgrid[0:H,0:W]; X=X0+xx/S; Y=Y1-yy/S
sx=12.639+(9.465-12.639)*(Y-4.1)/(36.3-4.1)
inside=((X>0.05)&(X<sx+0.3)&(Y>0.05)&(Y<37.0))
free=inside&~occ
dist=ndi.distance_transform_edt(free)/S          # m to nearest obstacle
seed=px(9.0,16.8)
out={}
for wdt in (0.6,0.75,0.9,1.2):
    ok=dist>=wdt/2; lab,n=ndi.label(ok); l0=lab[seed]
    reach=ndi.binary_dilation(lab==l0,iterations=int(wdt/2*S)+1)&free if l0 else np.zeros_like(free)
    out[wdt]=reach
D=json.load(open('cd/model_data.json'))
# targets
T={'bar front (stools)':(3.3,11.5),'bar staff aisle':(1.2,11.0),'bar staff entry (south)':(1.2,8.3),'aivan steps (bar side)':(1.0,14.9),'north tables':(4.6,33.3),'booth side aisle north':(6.75,33.3),
   'tent 1 opening':(4.4,32.3),'tent 2 opening':(4.4,35.2),'north gate':(6.4,36.0),'tapchan':(4.9,29.6),'hauz':(6.0,28.2),'mangal counter':(9.0,6.5),'majlis':(2.2,4.6),'dome centre':(6.0,19.9),
   'hall doors':(0.4,16.8),'kids entry':(0.4,2.9)}
for k,(lo,hi) in [(o[0],(o[1],o[2])) for o in D['booth']]:
    T[k+' opening']=(lo[0]-0.35,(lo[1]+hi[1])/2)
for name,(x,y) in T.items():
    r=[w for w in (0.6,0.75,0.9,1.2) if out[w][px(x,y)]]
    print(f'{name:28s} local clear {2*dist[px(x,y)]:.2f}  reachable at widths {r}')
# narrowest spots: free cells reachable at 0.6 but not at 0.9 -> pinch map
img=np.zeros((H,W,3),np.uint8)+255
img[~inside]=(235,235,235); img[occ]=(60,60,60)
img[out[0.6]&~out[0.75]]=(230,60,60); img[out[0.75]&~out[0.9]]=(245,170,60); img[out[0.9]&~out[1.2]]=(250,235,120); img[out[1.2]]=(170,220,170)
img[free&~out[0.6]&inside]=(150,150,210)
img[low&free]=(255,0,255)
Image.fromarray(img).rotate(90,expand=True).save('audit/walk.png')
np.save('audit/dist.npy',dist.astype(np.float32))
print('areas m2: >=1.2',out[1.2].sum()/S/S,' 0.9-1.2',(out[0.9]&~out[1.2]).sum()/S/S,' 0.75-0.9',(out[0.75]&~out[0.9]).sum()/S/S,' 0.6-0.75',(out[0.6]&~out[0.75]).sum()/S/S,' unreachable',(free&~out[0.6]).sum()/S/S)
