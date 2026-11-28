"""Localiza upm.ko en una instantánea WBI/prof y lee su último mensaje de apagado.

Uso (raíz del repo): python3 scripts/wbi/upm_modulo.py IMAGEN [IMAGEN...]
- Busca en la RAM el prólogo de k_upm_off_factor_handler_active (upm.ko .text+0xefb4) y traduce su página
  a VA con las tablas de páginas de im.elf (la zona de módulos 0x3f000000 es común a todos los procesos).
- Comprueba que .text+0xefec sea `ldr r3,[r4,#4]` (punto de scripts/cam/swd_upm_coldoff_0x27.cfg).
- Imprime g_off_factor+4/+0x14 (.data+0x60c/+0x61c): {0x920141, factor, motivo, código}. libObj
  GetInactiveFactor (0x7e7c18) lee ese motivo tras reanudar: 0x1b => OFF_TYPE_SUSPEND, 0x1c => COLDOFF.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fbm_tabla import Proceso
from snapram import Missing, Ram

KO = Path('analysis/camera-extract/usr/kmod/upm.ko')
HANDLER, PUNTO, LDR_R3_R4_4 = 0xefb4, 0xefec, 0xe5943004
TEXT_A_GOFF = 0x3f33af48 - 0x3f326000  # .data+0x608 respecto a .text, medido en Sony y CFW


def texto_ko():
    d = KO.read_bytes()
    shoff = struct.unpack_from('<I', d, 32)[0]
    shentsize, shnum, shstrndx = struct.unpack_from('<HHH', d, 46)
    sec = [struct.unpack_from('<10I', d, shoff + i * shentsize) for i in range(shnum)]
    names = sec[shstrndx][4]
    for s in sec:
        if d[names + s[0]:].split(b'\0')[0] == b'.text':
            return d[s[4]:s[4] + s[5]]
    raise SystemExit('upm.ko sin .text')


def localiza(r, texto):
    pat = texto[HANDLER:HANDLER + 20]
    lineales = {h & ~4095: h for h in r.finds(pat) if h & 4095 == HANDLER & 4095}
    pr = Proceso(r)
    for mb in range(0x3f0, 0x400):
        try:
            l1 = r.u(pr.pgd + 4 * mb)
        except Missing:
            continue
        if l1 & 3 != 1:
            continue
        for k in range(256):
            try:
                l2 = r.u((l1 & ~1023) - 0x40000000 + 4 * k)
            except Missing:
                continue
            pa = (l2 & ~4095) - 0x40000000
            if l2 & 2 and pa in lineales:
                return ((mb << 20) | (k << 12) | (HANDLER & 4095)) - HANDLER, pr
    raise SystemExit('no se encontró k_upm_off_factor_handler_active mapeado')


def lee_va(r, pr, va, n):
    l1 = r.u(pr.pgd + 4 * (va >> 20))
    l2 = r.u((l1 & ~1023) - 0x40000000 + 4 * ((va >> 12) & 255))
    return r.read((l2 & ~4095) - 0x40000000 + (va & 4095), n)


if __name__ == '__main__':
    texto = texto_ko()
    for img in sys.argv[1:]:
        r = Ram(Path(img))
        base, pr = localiza(r, texto)
        ins = struct.unpack('<I', lee_va(r, pr, base + PUNTO, 4))[0]
        reg = struct.unpack('<9I', lee_va(r, pr, base + TEXT_A_GOFF, 36))
        print(f'{img}: upm .text {base:#x}; .text+0xefec = {ins:#010x} '
              f'({"ldr r3,[r4,#4] OK" if ins == LDR_R3_R4_4 else "DISTINTO"})')
        print(f'  último apagado (+4): {reg[1]:#x} factor {reg[2]:#x} motivo {reg[3]:#x} código {reg[4]:#x}'
              f' | copia (+0x14): factor {reg[6]:#x} motivo {reg[7]:#x} código {reg[8]:#x}')
        print('  => tras reanudar libObj verá', {0x1b: 'OFF_TYPE_SUSPEND', 0x1c: 'OFF_TYPE_COLDOFF'}.get(reg[3], 'otro'))
