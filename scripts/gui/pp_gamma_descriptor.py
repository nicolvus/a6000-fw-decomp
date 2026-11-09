#!/usr/bin/env python3
"""G23 — descriptor de Gamma (Picture Profile) en `cmn_view_processDataMgr.so` (A6000 fw3.21), ProcessId 0x3c (LocalAreaLimitation, inerte).

Layout verificado por desensamblado de `CmnViewProcessDataElementNormal::getDataModel*` (G23 §Layout):
  desc +0x04 cautions por opción · +0x15 nº de opciones · +0x18 modelo · +0x1c nº de modelos
  modelo +0 nombre · +4 update · +8 evento de escritura · +0xc id de lectura · +0x10 claves de escritura · +0x14 claves de lectura
         +0x18 tipos (1 = número) · +0x1c tabla opción→valor [opción·nclaves + clave] · +0x20 nclaves · +0x21 nº de entradas de la tabla
Escritura `@M00B` 0x40 clave 0x214; lectura `model/CAMERA` 0x49 clave 0x216 (G19 §2b). Valores de la A6000 (G20 §1).
Uso: pp_gamma_descriptor.py ENTRADA.so SALIDA.so
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A
import pp_descriptors

PID = 0x3C
TABLA_D = 0x8C268
DESC_PALABRAS, MODEL_PALABRAS = 19, 9
PID_M00B = 0x3F                       # descriptor real con "@M00B": de él se copia el puntero al nombre
EVENTO_SET, ID_GET, CLAVE_SET, CLAVE_GET = 0x40, 0x49, 0x214, 0x216
GAMMAS = (4, 5, 3, 6, 7, 8, 9)         # Movie, Still, ITU709, Cine1–4 (orden del menú)
NADA = 0xA45                            # relleno de caution que usa el descriptor inerte


def patch(d: bytes) -> bytes:
    return pp_descriptors.patch(d, [pp_descriptors.Ajuste(PID, CLAVE_SET, GAMMAS)])


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
