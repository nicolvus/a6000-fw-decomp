#!/usr/bin/env python3
"""S164 — desensamblado anotado: resuelve los pares PIC (ldr [pc,#imm] + add rX,pc)
a la cadena apuntada y marca los `bl` con su destino.

Uso: disasm.py 0xADDR [N_INSTR]
"""
import json
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
REFS = json.loads((ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json").read_text())
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False

STR = {}
for m in re.finditer(rb"[\x20-\x7e]{4,}", DATA):
    STR[BASE + m.start()] = m.group().decode("latin1")
REFBY = {}
for k, v in REFS.items():
    REFBY.setdefault(int(k, 16), []).extend(v)


def main():
    a = int(sys.argv[1], 0)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    for i in MD.disasm(DATA[a - BASE:a - BASE + n * 4], a):
        extra = ""
        if i.mnemonic == "add" and i.op_str.startswith("r") and i.op_str.endswith(", pc"):
            reg = i.op_str.split(",")[0].strip()
            for dest, sites in REFBY.items():
                if i.address in sites:
                    extra = "   ; -> %08x %r" % (dest, STR.get(dest, "?"))
                    break
        print("%08x  %-9s %-28s%s" % (i.address, i.mnemonic, i.op_str, extra))


if __name__ == "__main__":
    main()
