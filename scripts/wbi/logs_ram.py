"""Extrae el texto imprimible de una zona física de una instantánea WBI/prof.

Uso: python3 scripts/wbi/logs_ram.py IMAGEN PA_INICIO LONGITUD [SALIDA]
PA en hexadecimal (p. ej. 0x83400000). VA del kernel = PA - 0x40000000.
Las páginas que no están en la imagen se cuentan y se omiten.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapram import Missing, Ram


def zona(r, pa, n):
    va, faltan, out = pa - 0x40000000, 0, bytearray()
    for off in range(0, n, 4096):
        try:
            out += r.read(va + off, min(4096, n - off))
        except Missing:
            faltan += 1
            out += b'\0' * min(4096, n - off)
    return bytes(out), faltan


if __name__ == '__main__':
    img, pa, n = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
    datos, faltan = zona(Ram(Path(img)), pa, n)
    lineas = [m.decode('latin1') for m in re.findall(rb'[\x20-\x7e\t]{6,}', datos)]
    print(f'# {img} PA {pa:#x}+{n:#x}: {faltan} páginas ausentes, {len(lineas)} cadenas')
    texto = '\n'.join(lineas) + '\n'
    if len(sys.argv) > 4:
        Path(sys.argv[4]).write_text(texto)
    else:
        sys.stdout.write(texto)
