from pathlib import Path
ROOT=Path('/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter')
a=(ROOT/'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin').read_bytes()
b=Path('/tmp/avcam_cfw.bin').read_bytes()
idx=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
print('bytes distintos:', len(idx))
rangos=[]
s=p=idx[0]
for i in idx[1:]:
    if i-p<=16: p=i
    else: rangos.append((s,p)); s=p=i
rangos.append((s,p))
print('rangos:', len(rangos))
tot=0
for s,e in rangos:
    tot+=e-s+1
print('bytes cubiertos (con huecos<=16):', tot)
for s,e in sorted(rangos, key=lambda r:-(r[1]-r[0]))[:15]:
    print(f'  0x{s:08x}..0x{e:08x}  ({e-s+1} B)')
