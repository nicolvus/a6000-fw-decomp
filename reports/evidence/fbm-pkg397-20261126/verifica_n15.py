import hashlib, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from e25_27 import tpzl

W = Path('build/cfw_fbm31_pkg397/work')
P = Path('build/cfw_fbm31_pkg397')
STOCK = Path('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15')
def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

# volcados de referencia (una vez): fábrica y 3.94
for tag, img in (('xs', W / 'usr_stock.ext2'), ('xn', W / 'usr394.ext2')):
    dst = W / tag
    dst.mkdir(exist_ok=True)
    if not img.exists():
        img.write_bytes(tpzl.TpzlImage.parse(STOCK.read_bytes()).decompressed(workers=1))
    if not any(dst.iterdir()):
        subprocess.run(['debugfs', '-R', f'rdump / {dst}', str(img)], capture_output=True, check=True)

new = (P / 'nflasha15-397.bin').read_bytes()
im = tpzl.TpzlImage.parse(new)
ims = tpzl.TpzlImage.parse(STOCK.read_bytes())
imo = tpzl.TpzlImage.parse((W / 'nflasha15-394.bin').read_bytes())
n395 = P.parent / 'cfw_fbm31_pkg395' / 'nflasha15-395.bin'
im5 = tpzl.TpzlImage.parse(n395.read_bytes()) if n395.exists() else None
ext = im.decompressed(workers=1)
(W / 'usr397.ext2').write_bytes(ext)
d = W / 'xn397'
d.mkdir(exist_ok=True)
subprocess.run(['debugfs', '-R', f'rdump / {d}', str(W / 'usr397.ext2')], capture_output=True, check=True)

def arbol(p):
    return {str(f.relative_to(p)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(Path(p).rglob('*')) if f.is_file()}

an, asx, a94 = arbol(d), arbol(W / 'xs'), arbol(W / 'xn')
res = {
    'nflasha15_397_sha256': hashlib.sha256(new).hexdigest(), 'bytes': len(new),
    'nflasha15_394_sha256': hashlib.sha256((W / 'nflasha15-394.bin').read_bytes()).hexdigest(),
    'nflasha15_395_sha256': hashlib.sha256(n395.read_bytes()).hexdigest() if n395.exists() else None,
    'bloques': len(im.entries), 'bloques_stock': len(ims.entries), 'bloques_394': len(imo.entries),
    'bloque0_igual_que_stock': im.block(0) == ims.block(0),
    'bloques_distintos_vs_394': sum(1 for i in range(len(im.entries)) if im.block(i) != imo.block(i)),
    'bloques_distintos_vs_395': sum(1 for i in range(len(im.entries)) if im5 and im.block(i) != im5.block(i)),
    'libmpr_en_imagen_sha256': sh(d / 'lib/libmpr.so'),
    'libmpr_tamano': (d / 'lib/libmpr.so').stat().st_size,
    'cabe_en_particion': len(new) <= 104857600,
    'alineado_512': all(o % 512 == 0 for o, _ in im.entries),
    'violaciones_ldec': len(tpzl.hardware_violations(im)),
    'max_sectores': max(-(-s // 512) for _, s in im.entries),
    'ficheros_ext2': len(an),
    'ficheros_distintos_vs_stock': sorted(k for k in set(an) | set(asx) if an.get(k) != asx.get(k)),
    'ficheros_distintos_vs_394': sorted(k for k in set(an) | set(a94) if an.get(k) != a94.get(k)),
    'ficheros_distintos_vs_395': sorted(k for k in set(an) | set(arbol(P.parent / 'cfw_fbm31_pkg395/work/xn395'))
                                     if an.get(k) != arbol(P.parent / 'cfw_fbm31_pkg395/work/xn395').get(k))
    if (P.parent / 'cfw_fbm31_pkg395/work/xn395').exists() else None,
}
st = subprocess.run(['debugfs', '-R', 'stat /lib/libmpr.so', str(W / 'usr397.ext2')], capture_output=True, text=True).stdout
res['libmpr_mode_uid_gid'] = [oct(int(st.split('Mode:')[1].split()[0], 8)),
                              int(st.split('User:')[1].split()[0]), int(st.split('Group:')[1].split()[0])]
print(json.dumps(res, indent=1, ensure_ascii=False))
(P / 'nflasha15-397.json').write_text(json.dumps(res, indent=1))
