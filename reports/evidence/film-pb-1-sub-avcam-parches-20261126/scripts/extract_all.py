import sys, hashlib
from pathlib import Path
ROOT = Path('/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter')
sys.path.insert(0, str(ROOT/'scripts'))
from e25_27 import tarball, tpzl, fatimg, build

for name in ('base', 'pp', 'film', 'exfine'):
    p = ROOT/'build/cfw_func393'/name/'base-film.tar'
    if not p.is_file():
        print(name, 'no existe'); continue
    entries, _ = tarball.parse(p.read_bytes())
    m = {e.name: e.data for e in entries}
    part = tpzl.TpzlImage.parse(m[build.NFLASHA3])
    fat = fatimg.Fat16.parse(part.decompressed(workers=1))
    av = fat.read(build.AVCAM_NAME)
    out = Path(f'/tmp/avc/avcam_{name}.bin'); out.write_bytes(av)
    print(f'{name:8s} {len(av)} sha {hashlib.sha256(av).hexdigest()[:16]} -> {out}')
