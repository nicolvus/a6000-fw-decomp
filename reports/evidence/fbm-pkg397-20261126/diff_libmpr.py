import hashlib, json, struct, sys
from pathlib import Path
sys.path.insert(0, 'scripts')

W = Path('build/cfw_fbm31_pkg397/work')
P = Path('build/cfw_fbm31_pkg397')
base = (W / 'libmpr-394.so').read_bytes()
new = Path('build/cfw_fbm_sector31_c/libmpr.so').read_bytes()
assert len(base) == len(new)
dif = [i for i in range(len(base)) if base[i] != new[i]]
# agrupar en rangos contiguos
rng, s = [], None
for i in dif:
    if s is None:
        s = p = i
    elif i == p + 1:
        p = i
    else:
        rng.append((s, p)); s = p = i
if s is not None:
    rng.append((s, p))
res = {
    'sha_base': hashlib.sha256(base).hexdigest(),
    'sha_nuevo': hashlib.sha256(new).hexdigest(),
    'tamano': len(new), 'tamano_igual': len(base) == len(new),
    'bytes_distintos': len(dif),
    'rangos': [{'ini': hex(a), 'fin': hex(b), 'largo': b - a + 1,
                'antes': base[a:b + 1].hex(), 'despues': new[a:b + 1].hex()} for a, b in rng],
    'elf_header_igual': base[:52] == new[:52],
}
# cabeceras de sección (e_shoff del ELF32 little endian)
shoff = struct.unpack_from('<I', base, 0x20)[0]
shentsize, shnum = struct.unpack_from('<HH', base, 0x2E)
print('shoff', hex(shoff), 'shnum', shnum, 'entsize', shentsize)
res['secciones_iguales'] = base[shoff:shoff + shentsize * shnum] == new[shoff:shoff + shentsize * shnum]
# relocaciones que caen dentro de los rangos (busca los 4/8 bytes de las direcciones en tablas .rel.dyn)
hits = []
for a, b in rng:
    for width, fmt in ((4, '<I'), (8, '<Q')):
        for off in (a, b - width + 1):
            pass
res['rangos_len'] = len(rng)
print(json.dumps(res, indent=1))
(P / 'libmpr-diff.json').write_text(json.dumps(res, indent=1))
(P / 'libmpr.so').write_bytes(new)
