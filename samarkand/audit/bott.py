import numpy as np, json, sys
from scipy import ndimage as ndi
X0,Y0,X1,Y1=-8.0,-1.0,14.5,38.5; S=50
dist=np.load('audit/dist.npy'); H,W=dist.shape
def px(x,y): return int((Y1-y)*S),int((x-X0)*S)
seed=px(9.0,16.8)
T=json.load(open('audit/targets.json'))
ws=[round(0.4+0.05*k,2) for k in range(30)]
labs={}
for w in ws:
    lab,n=ndi.label(dist>=w/2); labs[w]=(lab,lab[seed])
for name,(x,y) in T.items():
    # nearest free cell with decent clearance around the target
    r0,c0=px(x,y); best=0
    for w in ws:
        lab,l0=labs[w]
        if l0==0: break
        win=lab[max(0,r0-20):r0+21,max(0,c0-20):c0+21]
        if (win==l0).any(): best=w
    print(f'{name:30s} bottleneck from entrance: {best:.2f} m')
