import sys,os,numpy as np,rawpy,exifread
d=os.path.expanduser('~/Documents/a6000/test images')
def medir(n):
    f=f'{d}/DSC035{n}.ARW'
    tags=exifread.process_file(open(f,'rb'),details=False)
    ss=tags.get('EXIF ExposureTime'); iso=tags.get('EXIF ISOSpeedRatings'); fn=tags.get('EXIF FNumber')
    with rawpy.imread(f) as r:
        a=r.raw_image_visible.astype(np.float64); bl=np.mean(r.black_level_per_channel)
    a=a-bl; h,w=a.shape
    tira=lambda k: a[int(h*k[0]):int(h*k[1]),:].mean()
    bands=[tira((i/8,(i+1)/8)) for i in range(8)]
    return dict(n=n,ss=str(ss),iso=str(iso),f=str(fn),total=a.mean(),sup=bands[0],inf=bands[-1],bands=bands)
if __name__=='__main__':
    res={n:medir(n) for n in sys.argv[1:]}
    for n,r in res.items(): print(n,r['ss'],'ISO',r['iso'],'f',r['f'],'| media %.1f | franjas(8) '%r['total']+' '.join('%.1f'%b for b in r['bands']))
    ref=np.mean([res[n]['total'] for n in sys.argv[3:]]) if len(sys.argv)>3 else None
