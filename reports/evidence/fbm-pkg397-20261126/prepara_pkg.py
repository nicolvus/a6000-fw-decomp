import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, 'scripts')

P = Path('build/cfw_fbm31_pkg397')
OLD = Path('build/cfw_fbm31_pkg395/files')
W = P / 'work'
def sh(b): return hashlib.sha256(b).hexdigest()

# 1. paquete: copia del de la 3.95 con el libmpr C
if (P / 'files').exists():
    shutil.rmtree(P / 'files')
shutil.copytree(OLD, P / 'files')
man = json.loads((P / 'files' / 'MANIFEST.json').read_text())
man['parcheados']['lib/libmpr.so'] = sh((P / 'libmpr.so').read_bytes())
assert man['originales']['lib/libmpr.so'] == sh((W / 'libmpr-394.so').read_bytes()) == \
    '9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30'
(P / 'files' / 'lib' / 'libmpr.so').write_bytes((P / 'libmpr.so').read_bytes())
(P / 'files' / 'MANIFEST.json').write_text(json.dumps(man, indent=1))

# 2. los otros 30 ficheros deben ser byte a byte los que ya lleva la base 3.94
malos = []
for rel, h in sorted(man['parcheados'].items()):
    if rel == 'lib/libmpr.so':
        continue
    got = sh((P / 'files' / rel).read_bytes())
    if got != h:
        malos.append((rel, 'hash del manifiesto != contenido del paquete'))
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(['debugfs', '-R', f'dump /{rel} {t}/f', str(W / 'usr394.ext2')], capture_output=True, check=True)
        if sh(Path(t, 'f').read_bytes()) != got:
            malos.append((rel, 'distinto del que lleva la base 3.94'))
print('ficheros del paquete:', len(man['parcheados']), 'nuevos:', len(man['nuevos']))
print('libmpr.so del paquete:', man['parcheados']['lib/libmpr.so'])
print('los otros 30 == base 3.94:', not malos, malos)
assert not malos
