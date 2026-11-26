#!/usr/bin/env python3
"""Fuerza la creación del WBI (im.elf → `/sys/power/state = "warm"`) saltando la compuerta del contador de Backup.

Motivo (FILM-PB-1, 28-11-2026): en frío el core AV nunca arranca el decodificador y no se reproduce vídeo; en
caliente sí. El único modo de tener a la vez reproducción y el `/usr` del CFW (donde vive el menú Silent) es que
la cámara **regenera su propia instantánea** después de instalar. Eso lo decide `im.elf` en el apagado:

    0x9F44  int warm_permitido(void)   lectura del límite y del contador persistente
    0x9F68  incrementa el contador     Backup_write(canal 0x94, elemento 0x940004)
    0x9FB4  escribe "warm" (4 B) o "mem" (3 B) en /sys/power/state según el modo y esa compuerta

Con el contador por encima del límite, escribe `"mem"` y la instantánea no se rehace nunca: por eso el CFW
instalado en frío se queda en frío para siempre. Parche: `0x9F44` pasa a devolver 1 siempre
(`movs r0,#1 ; bx lr`), así el apagado siguiente escribe "warm" una vez y el WBI se crea con el sistema actual.

El efecto se agota solo: cuando el WBI existe, Loader3 elige BootMode 11, no se ejecuta `/sbin/init` y `im.elf`
no vuelve a correr.

Uso:  patch_im_elf_warm.py IM_ELF_ENTRADA SALIDA   (o `--verifica` sobre el resultado)
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

GATE_VA = 0x9F44          # int warm_permitido(void)
GATE_ORIGINAL = bytes.fromhex("064b80b5")   # ldr r3,[pc,#0x18] ; push {r7,lr}
GATE_PARCHE = bytes.fromhex("01207047")     # movs r0,#1 ; bx lr
TEXT_LO, TEXT_HI = 0x8000, 0xCB40           # primer PT_LOAD del ELF: fichero 0 → VA 0x8000


def _offset(va: int) -> int:
    return va - TEXT_LO


def parchea(original: bytes) -> bytes:
    """Devuelve la imagen con la compuerta puenteada. Verifica antes y después."""
    off = _offset(GATE_VA)
    assert original[off:off + 4] == GATE_ORIGINAL, (
        f"0x{GATE_VA:X}: se esperaba {GATE_ORIGINAL.hex()} y hay {original[off:off + 4].hex()}")
    parcheado = bytearray(original)
    parcheado[off:off + 4] = GATE_PARCHE
    cambios = [i for i in range(len(original)) if original[i] != parcheado[i]]
    assert cambios == list(range(off, off + 4)), f"cambia más de lo previsto: {cambios[:8]}"
    # el ELF sigue siendo el mismo fichero: tamaño y cabecera intactos
    assert parcheado[:0x34] == original[:0x34] and len(parcheado) == len(original)
    return bytes(parcheado)


def main(entrada: Path, salida: Path) -> dict:
    original = entrada.read_bytes()
    parcheado = parchea(original)
    salida.write_bytes(parcheado)
    return {
        "entrada": str(entrada),
        "salida": str(salida),
        "sha256_entrada": hashlib.sha256(original).hexdigest(),
        "sha256_salida": hashlib.sha256(parcheado).hexdigest(),
        "parche": {"va": hex(GATE_VA), "antes": GATE_ORIGINAL.hex(), "despues": GATE_PARCHE.hex(),
                   "bytes_cambiados": 4},
        "efecto": "warm_permitido() devuelve 1: el apagado escribe 'warm' y la cámara crea su WBI",
    }


if __name__ == "__main__":
    import json
    if len(sys.argv) == 3 and sys.argv[1] == "--verifica":
        assert Path(sys.argv[2]).read_bytes()[_offset(GATE_VA):_offset(GATE_VA) + 4] == GATE_PARCHE
        print("parche presente")
    else:
        print(json.dumps(main(Path(sys.argv[1]), Path(sys.argv[2])), indent=1))
