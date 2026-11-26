import sys, hashlib, subprocess
from pathlib import Path
sys.path.insert(0, 'scripts')
from e25_27 import tarball, tpzl

W = Path('build/cfw_fbm31_pkg397/work')
m = {e.name: e.data for e in tarball.parse(open('build/cfw_avcam_limpio/pkg-3.94/firmware.tar', 'rb').read())[0]}
n15 = m['0700_part_image/dev/nflasha15']
(W / 'nflasha15-394.bin').write_bytes(n15)
img = tpzl.TpzlImage.parse(n15)
ext = img.decompressed(workers=1)
(W / 'usr394.ext2').write_bytes(ext)
print('n15_sha', hashlib.sha256(n15).hexdigest(), len(n15))
print('ext2_sha', hashlib.sha256(ext).hexdigest(), len(ext))
r = subprocess.run(['debugfs', '-R', f'dump /lib/libmpr.so {W}/libmpr-394.so',
                    '-R', 'stat /lib/libmpr.so', str(W / 'usr394.ext2')], capture_output=True, text=True)
print(r.stdout[:500], r.stderr[:200])
print('libmpr_base_sha', hashlib.sha256((W / 'libmpr-394.so').read_bytes()).hexdigest())
st = tpzl.TpzlImage.parse(Path('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15').read_bytes())
print('bloques', len(img.entries), 'bloque0_igual_stock', img.block(0) == st.block(0))
