import sys, hashlib
from pathlib import Path
ROOT=Path('/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter')
sys.path.insert(0,str(ROOT/'scripts'))
from e25_27 import tarball, tpzl, fatimg, build
def files_tar(tar_path):
    tar=Path(tar_path).read_bytes()
    entries,_=tarball.parse(tar)
    members={e.name:e.data for e in entries}
    part=tpzl.TpzlImage.parse(members[build.NFLASHA3])
    return fatimg.Fat16.parse(part.decompressed(workers=1))
stock=ROOT/'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked'
cfw=files_tar(ROOT/'build/cfw_func393/pp/base-film.tar')
import os
for name in sorted(os.listdir(stock)):
    p=stock/name
    if not p.is_file(): continue
    o=p.read_bytes()
    try:
        n=cfw.read(name.upper())
    except Exception as e:
        print(f'{name:20s} no en FAT: {e}'); continue
    same = o==n
    diff = sum(1 for a,b in zip(o,n) if a!=b) if len(o)==len(n) else -1
    print(f'{name:20s} stock={len(o):9d} cfw={len(n):9d} igual={same} distintos={diff}')
# listado de la FAT
