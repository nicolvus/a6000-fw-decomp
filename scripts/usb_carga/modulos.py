#!/usr/bin/env python3
"""Prepara los módulos de carga USB de la A6300 para la A6000 (USB-CARGA).

La A6000 trae `libUsbBusPower.so` (sabe cargar `/usr/kmod/usb_darwin.ko`, tipo 6 de la NVRAM
`0x1210001`) y el servicio `0x2804d3` en av-cam, pero no los módulos. Se toman de la A6300 2.01
(mismo kernel `3.0.27_nl-rt106`, `struct module` de 0x12c, sin modversions) y se neutralizan las
4 llamadas GPIO de `usb_darwin.ko`: su pin sale de la NVRAM `0xf90397/98`, que en la A6000 vale
`0xffffffff`. Cada `bl gpio_*` pasa a NOP y su reubicación a `R_ARM_NONE` (el cargador de módulos
de Sony la ignora). `usb_buspwr.ko` no usa GPIO y se copia tal cual.

Uso: modulos.py [--kmod DIR_A6300] [--out DIR]
"""
import argparse
import hashlib
import pathlib
import shutil
import struct

RAIZ = pathlib.Path(__file__).resolve().parents[2]
KMOD_A6300 = RAIZ / 'firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/kmod'
SALIDA = RAIZ / 'analysis/usb-carga/build'
GPIO = {b'gpio_set_mode_bit', b'gpio_set_data_bit'}
R_ARM_NONE, R_ARM_CALL, SHT_REL = 0, 28, 9
NOP = struct.pack('<I', 0xE1A00000)  # mov r0, r0


def secciones(d: bytes) -> list[tuple]:
    shoff, = struct.unpack_from('<I', d, 0x20)
    shentsize, shnum, shstrndx = struct.unpack_from('<HHH', d, 0x2E)
    sh = [struct.unpack_from('<IIIIIIIIII', d, shoff + i * shentsize) for i in range(shnum)]
    nombres = sh[shstrndx][4]
    return [(d[nombres + s[0]:d.index(b'\0', nombres + s[0])], *s) for s in sh]


def sitios_gpio(d: bytes) -> list[tuple[int, int]]:
    """(offset en fichero de la entrada REL, offset en fichero de la instrucción) de cada bl gpio_*."""
    sh = secciones(d)
    symtab = next(s for s in sh if s[0] == b'.symtab')
    strtab = sh[symtab[7]]  # sh_link
    def nombre(i: int) -> bytes:
        st_name, = struct.unpack_from('<I', d, symtab[5] + i * 16)
        return d[strtab[5] + st_name:d.index(b'\0', strtab[5] + st_name)]
    out = []
    for s in sh:
        if s[2] != SHT_REL:
            continue
        destino = sh[s[8]]  # sh_info = sección a la que se aplica
        for k in range(s[6] // 8):
            ent = s[5] + k * 8
            r_off, r_info = struct.unpack_from('<II', d, ent)
            if nombre(r_info >> 8) in GPIO:
                out.append((ent, destino[5] + r_off))
    return out


def parchear(d: bytes) -> bytes:
    b = bytearray(d)
    sitios = sitios_gpio(d)
    assert len(sitios) == 4, sitios  # 1 gpio_set_mode_bit (init) + 3 gpio_set_data_bit
    for ent, ins in sitios:
        assert b[ent + 4] == R_ARM_CALL and b[ins + 3] == 0xEB, f'no es bl: {b[ins:ins + 4].hex()}'
        b[ins:ins + 4] = NOP
        r_info, = struct.unpack_from('<I', b, ent + 4)
        struct.pack_into('<I', b, ent + 4, (r_info & ~0xFF) | R_ARM_NONE)
    return bytes(b)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--kmod', type=pathlib.Path, default=KMOD_A6300)
    ap.add_argument('--out', type=pathlib.Path, default=SALIDA)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / 'usb_darwin.ko').write_bytes(parchear((a.kmod / 'usb_darwin.ko').read_bytes()))
    shutil.copyfile(a.kmod / 'usb_buspwr.ko', a.out / 'usb_buspwr.ko')
    for f in ('usb_darwin.ko', 'usb_buspwr.ko'):
        print(hashlib.sha256((a.out / f).read_bytes()).hexdigest(), a.out / f)


if __name__ == '__main__':
    main()
