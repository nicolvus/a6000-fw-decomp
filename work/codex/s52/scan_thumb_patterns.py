#!/usr/bin/env python3
"""Escáner reproducible de patrones Thumb para S52 (sin descompilar)."""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
MEM_RE = re.compile(r"\[(r(?:[0-9]|1[0-2]|[a-z]+)|pc), #?(0x[0-9a-f]+|[0-9]+)\]")


def main() -> None:
    path = Path(sys.argv[1])
    blob = path.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.skipdata = True
    ins = list(md.disasm(blob, BASE))
    target_lo, target_hi = (int(x, 16) for x in sys.argv[2:4])
    last_literal: dict[str, tuple[int, int]] = {}
    for i, x in enumerate(ins):
        ops = x.op_str.replace(" ", "")
        if x.mnemonic.startswith("ldr") and ",[pc," in ops:
            reg = ops.split(",", 1)[0]
            m = MEM_RE.search(x.op_str)
            if m:
                literal = ((x.address + 4) & ~3) + int(m.group(2), 0)
                if BASE <= literal <= BASE + len(blob) - 4:
                    last_literal[reg] = (x.address, struct.unpack_from("<I", blob, literal - BASE)[0])
        if x.mnemonic == "add" and ",pc" in ops:
            reg = ops.split(",", 1)[0]
            if reg in last_literal:
                ldr, value = last_literal[reg]
                resolved = (value + x.address + 4) & 0xFFFFFFFF
                if target_lo <= resolved <= target_hi:
                    print(f"PCREL {resolved:#x} ldr={ldr:#x} add={x.address:#x} {x.mnemonic} {x.op_str}")
        if x.mnemonic == "blx":
            reg = ops
            for prev in ins[max(0, i - 8):i]:
                pm = MEM_RE.search(prev.op_str)
                if prev.mnemonic.startswith("ldr") and pm and int(pm.group(2), 0) == 0x28 and prev.op_str.split(",", 1)[0] == reg:
                    print(f"VTABLE28 blx={x.address:#x} target_reg={reg} ldr={prev.address:#x} {prev.op_str}")


if __name__ == "__main__":
    main()
