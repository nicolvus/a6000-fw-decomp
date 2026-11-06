import numpy as np,rawpy
P='/home/nicolas/Documents/a6000/test images/DSC0%d.ARW'; NB=10
def m(n):
    with rawpy.imread(P%n) as r:
        a=r.raw_image_visible.astype(np.float64)-np.mean(r.black_level_per_channel)
    h=a.shape[0]; return np.array([a[h*i//NB:h*(i+1)//NB].mean() for i in range(NB)])
pairs={2.0:(3555,3562),4.0:(3556,3561),5.0:(3557,3560),8.0:(3558,3559)}
R={t:(m(a),m(b)) for t,(a,b) in pairs.items()}
for t,(on,off) in sorted(R.items()):
    q=on/off
    print('T=%.0f ms  on/off global %.3f | por franja: '%(t,on.mean()/off.mean())+' '.join('%.2f'%x for x in q))
k=R[8.0][0]/R[8.0][1]
print('δ (ms) normalizado a 1/125:')
for t,(on,off) in sorted(R.items()): print('T=%.0f '%t+' '.join('%5.2f'%x for x in t*(1-(on/off)/k)), ' global %.2f'%(t*(1-(on.mean()/off.mean())/k.mean())))
print('off: exposición/T normalizada a 1/125:'); 
for t,(on,off) in sorted(R.items()): print('T=%.0f '%t+' '.join('%.2f'%x for x in off/R[8.0][1]*8/t))
