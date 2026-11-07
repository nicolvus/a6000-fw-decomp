"""Cociente EFCS on/off por franjas. Uso: onoff.py DIR ON_500 OFF_500 ON_1000 OFF_1000 (nombres sin .ARW)."""
import sys,numpy as np,rawpy
d=sys.argv[1]; NB=10
def m(n):
    with rawpy.imread(f'{d}/{n}.ARW') as r: a=r.raw_image_visible.astype(np.float64)-np.mean(r.black_level_per_channel)
    h=a.shape[0]; return np.array([a[h*i//NB:h*(i+1)//NB].mean() for i in range(NB)])
for t,on,off in (('1/500',sys.argv[2],sys.argv[3]),('1/1000',sys.argv[4],sys.argv[5])):
    a,b=m(on),m(off); print('%-6s on/off %.3f | medias on %.1f off %.1f | franjas '%(t,a.mean()/b.mean(),a.mean(),b.mean())+' '.join('%.2f'%x for x in a/b))
