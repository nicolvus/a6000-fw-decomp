"""S71-13: clasifica los escritores de +0x133 (A6000) / +0x13d (A7S) en copias (ldrb de otra estructura) y constantes."""
import os
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

A7 = "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
modelo, off = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("a6000", "0x133")
path = A7 if modelo == "a7s" else "analysis/rea-independent/input/av-cam.bin"
b = Path(path).read_bytes()
base = int(os.environ.get("BASE", "0x43541000"), 16)
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True
ins = list(md.disasm(b[:0x9c0000], base))
for k, i in enumerate(ins):
    m = re.match(rf"(\w+), \[(\w+), #{off}\]$", i.op_str)
    if not (i.mnemonic.startswith("strb") and m):
        continue
    src = "?"
    for x in reversed(ins[max(0, k - 4):k]):
        if re.match(rf"{m.group(1)}, ", x.op_str):
            mm = re.match(r"\w+, \[(\w+)(?:, #(0x[0-9a-f]+))?\]$", x.op_str)
            src = f"{x.mnemonic} {x.op_str}" if not mm else f"copia {mm.group(1)}+{mm.group(2) or 0}"
            break
    print(hex(i.address), src)
