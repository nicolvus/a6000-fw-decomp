"""Cuenta qué páginas de 4 KiB del WBI son páginas de ficheros de /usr y de av-cam.bin (método: SHA-1 por página)."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, 'references/fwtool')
from fwtool.sony import wbi

BASE15 = Path('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked')
AVCAM = Path('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin')
IMG5 = Path('firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha5')

def paginas(datos: bytes):
    for i in range(0, len(datos) - 4095, 4096):
        p = datos[i:i + 4096]
        if any(p):
            yield hashlib.sha1(p).hexdigest()

def main() -> int:
    indice = {}
    for f in sorted(BASE15.rglob('*')):
        if f.is_file() and f.stat().st_size >= 4096:
            for h in paginas(f.read_bytes()):
                indice.setdefault(h, set()).add(str(f.relative_to(BASE15)))
    ac = set(paginas(AVCAM.read_bytes()))
    print('páginas distintas indexadas de /usr:', len(indice))
    print('páginas distintas de av-cam.bin    :', len(ac))
    total = en_usr = en_ac = 0
    con = {}
    with IMG5.open('rb') as fh:
        for sec in wbi.readWbi(fh):
            datos = bytes(sec.contents.read())
            for i in range(0, len(datos) - 4095, 4096):
                p = datos[i:i + 4096]
                if not any(p):
                    continue
                total += 1
                h = hashlib.sha1(p).hexdigest()
                if h in ac:
                    en_ac += 1
                for nombre in indice.get(h, ()):
                    en_usr += 1
                    con[nombre] = con.get(nombre, 0) + 1
                    break
    print('páginas no nulas del WBI           :', total)
    print('  que son de av-cam.bin            :', en_ac)
    print('  que son de algún fichero de /usr :', en_usr)
    for k in ('lib/libObj.so', 'lib/viewUnified2.so', 'lib/CautionConfig.so', 'bin/im.elf'):
        print(f'  {k:26s}: {con.get(k, 0)}')
    print('  ficheros de /usr distintos vistos:', len(con))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
