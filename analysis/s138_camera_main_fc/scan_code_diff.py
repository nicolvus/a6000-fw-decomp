#!/usr/bin/env python3
"""S138 — ¿existe el mismo código (módulo `[CAMERA_MAIN_FC]`) en los otros firmwares?

Compara secuencias de bytes del A6000 fw3.21 con las imágenes de la A7S fw3.20 y
del A6300 fw2.01. Una coincidencia exacta indicaría que el módulo existe allí con
otra etiqueta; la ausencia indicaría código propio de la A6000 fw3.21.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
A6 = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
A7 = os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A63 = os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")

# (etiqueta, inicio, longitud) — fragmentos inequívocos de cada función del módulo
FRAGMENTS = [
    ("ReplyForTouchShutter", 0x437b7f8a, 0x30),
    ("SetRequestReplyForTouchShutter", 0x437b81f0, 0x30),
    ("BatteryInfo", 0x437b7d6c, 0x30),
    ("osal_free_timer", 0x437b777c, 0x40),
    ("EyeData(lc flag)", 0x437b7260, 0x30),
    ("APP MODE face_on/obj_on", 0x437b7844, 0x40),
    ("osaltimer alloc/set", 0x437b74a4, 0x40),
    ("FaceAreaSet", 0x437b7598, 0x40),
]


def main():
    a6 = open(A6, "rb").read()
    others = {"a7s": open(A7, "rb").read(), "a6300": open(A63, "rb").read()}
    print(f"{'fragmento':32s} {'dir':10s} {'A7S':>6s} {'A6300':>6s}  direcciones")
    for name, addr, ln in FRAGMENTS:
        frag = a6[addr - BASE:addr - BASE + ln]
        row = []
        for k, data in others.items():
            hits = []
            i = data.find(frag)
            while i >= 0:
                hits.append(BASE + i)
                i = data.find(frag, i + 1)
            row.append(hits)
        print(f"{name:32s} 0x{addr:x} {len(row[0]):6d} {len(row[1]):6d}  "
              f"a7s={[hex(h) for h in row[0]]} a6300={[hex(h) for h in row[1]]}")


if __name__ == "__main__":
    main()
