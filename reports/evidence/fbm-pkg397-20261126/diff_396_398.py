import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'references/fwtool')
from e25_06 import audit_packages as A

a = Path('build/cfw_fbm31_pkg395/pkg-3.96-rollback/package-3.96/firmware_packed.dat').read_bytes()
b = Path('build/cfw_fbm31_pkg397/pkg-3.98-rollback/package-3.98/firmware_packed.dat').read_bytes()
c = Path('build/cfw_fbm31_pkg397/pkg-3.97/package-3.97/firmware_packed.dat').read_bytes()
difs = [i for i in range(len(a)) if a[i] != b[i]]
print('396 vs 398: mismo tamano', len(a) == len(b), 'bytes distintos', len(difs), 'rango', hex(difs[0]) if difs else None, hex(difs[-1]) if difs else None)
print('396 == 398 en todo menos la cabecera (primeros', hex(max(difs) + 1), 'B)?', a[max(difs) + 1:] == b[max(difs) + 1:])
for tag, dat in (('397', c), ('398', b), ('396', a)):
    info = A.parse_dat(dat)
    print(tag, 'dend_ok', info['dend_stored'] == info['dend_computed'], 'version', info.get('version'),
          'fdat_off', info['fdat_offset'], 'tamano', len(dat), 'sha', hashlib.sha256(dat).hexdigest()[:16])
print('397 interno libmpr? ver auditoria')
