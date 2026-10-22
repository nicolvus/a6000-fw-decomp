#!/usr/bin/env python3
"""S139 — decodifica el despachador de mensajes de `ProcAvcMsg` ( tbh ) y asocia
cada id numérico con el nombre `MSGID_AVC_ENC_VIDEO_*` que el caso registra.

El despachador calcula `idx = msgid - 0x8101` (mvn r3,#0x8100 → adds) y salta con
`tbh [pc, idx, lsl #1]`; la tabla base es (tbh+4) y el destino = base + 2*halfword.

Uso: .venv/bin/python analysis/s139_encseqctrl/msgid_table.py <tbh_addr> <fin_funcion>
"""
import os
import struct
import sys

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BINS = {
    "a6000": "analysis/rea-independent/input/av-cam.bin",
    "a7s": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}


def hw(b, a):
    return struct.unpack_from("<H", b, a - BASE)[0]


def main():
    name = sys.argv[1]
    tbh = int(sys.argv[2], 0)
    b = open(os.path.join(ROOT, BINS[name]), "rb").read()
    base = tbh + 4
    # 18 entradas
    tbl = [hw(b, base + 2 * i) for i in range(18)]
    targets = [base + 2 * t for t in tbl]
    # En cada rango [target, target_siguiente) buscar la cadena MSGID_ referenciada por PIC
    # (aquí se listan los targets; el mapeo a nombres se hace a mano en el informe)
    print(f"{name}: tbh=0x{tbh:x} base=0x{base:x}")
    for i, (t, tgt) in enumerate(zip(tbl, targets)):
        print(f"   idx {i:2d}  msgid 0x{0x8101+i:04x}  hw=0x{t:04x}  -> 0x{tgt:x}")


if __name__ == "__main__":
    main()
