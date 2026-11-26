import sys, hashlib
from pathlib import Path
ROOT=Path('/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter')
sys.path.insert(0,str(ROOT/'scripts'))
from e25_27 import tarball, tpzl, fatimg, build
import inspect
print('firma decompressed:', inspect.signature(tpzl.TpzlImage.decompressed))
tar=(ROOT/'build/cfw_func393/pp/base-film.tar').read_bytes()
entries,_=tarball.parse(tar)
members={e.name:e.data for e in entries}
part=tpzl.TpzlImage.parse(members[build.NFLASHA3])
dec=part.decompressed(workers=1)
print('descomprimido:', len(dec))
fat=fatimg.Fat16.parse(dec)
av=fat.read(build.AVCAM_NAME)
print('AVCAM_NAME:', build.AVCAM_NAME, 'len', len(av), 'sha256', hashlib.sha256(av).hexdigest()[:16])
orig=(ROOT/'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin').read_bytes()
print('av-cam 3.21 len', len(orig), 'sha256', hashlib.sha256(orig).hexdigest()[:16])
print('identicos:', av==orig)
n=min(len(av),len(orig))
print('bytes distintos:', sum(1 for a,b in zip(av[:n],orig[:n]) if a!=b))
(Path('/tmp/avcam_cfw.bin')).write_bytes(av)
