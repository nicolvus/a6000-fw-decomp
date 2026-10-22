#!/usr/bin/env python3
"""S166 — barrido de llamadas `bl`/`blx` en la imagen de la A6000 fw3.21.

Uso: calls.py 0xTARGET [0xTARGET ...]
Salida: JSON en stdout con {"target": [...callers...], "all": {...}}
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False


def sweep():
    calls = defaultdict(list)
    off = 0
    n = len(DATA)
    while off < n:
        got = False
        for ins in MD.disasm(DATA[off:off + 16], BASE + off):
            got = True
            if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#0x"):
                calls[int(ins.op_str[1:], 16)].append(ins.address)
            off += ins.size
        if not got:
            off += 2
    return calls


def main():
    targets = [int(x, 0) for x in sys.argv[1:]]
    calls = sweep()
    out = {}
    for t in targets:
        out["0x%x" % t] = ["0x%x" % c for c in calls.get(t, [])]
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
