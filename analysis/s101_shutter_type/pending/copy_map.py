"""S71-15: mapa origen->destino de la copia en bloque hacia captura+0x730..0x760 en A6000 y A7S."""
import re
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

A7 = "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
base = 0x43541000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True


def mapa(path, lo, hi):
    b = Path(path).read_bytes()
    prev, out = None, {}
    for i in md.disasm(b[lo - base:hi - base], lo):
        m = re.match(r"(\w+), \[(\w+)(?:, #(0x[0-9a-f]+))?\]$", i.op_str)
        if not m:
            continue
        if i.mnemonic.startswith("ldrb"):
            prev = (m.group(1), int(m.group(3) or "0", 16))
        elif i.mnemonic.startswith("strb") and m.group(3) and prev and prev[0] == m.group(1):
            d = int(m.group(3), 16)
            if 0x730 <= d < 0x760:
                out[d] = prev[1]
    return out


a6 = mapa("analysis/rea-independent/input/av-cam.bin", 0x438ab3e8, 0x438ad400)
a7 = mapa(A7, 0x4389e000, 0x438a0400)
print("A6000 dst<-src:", {hex(k): hex(v) for k, v in sorted(a6.items())})
print("A7S   dst<-src:", {hex(k): hex(v) for k, v in sorted(a7.items())})
