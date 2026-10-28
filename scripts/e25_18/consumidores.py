"""E25-18 — consumidores de un campo de un objeto global (resuelve `ldr rX,[pc];add rX,pc` -> base y busca accesos [rX,#off])."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "e25_17"))
import fw  # type: ignore[import-not-found]

BASE_OBJ = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x43E849C0
OFFS = {int(x, 0) for x in sys.argv[2:]} or {0x40}


def barrer(lo: int = 0x43541000, hi: int = 0x43B40000) -> list[dict]:
    res: list[dict] = []
    ins: list = []
    a = lo
    while a < hi:  # capstone se detiene en datos: se resincroniza 2 bytes
        got = False
        for i in fw._md.disasm(fw.rd(a, min(0x4000, hi - a)), a):
            got = True
            ins.append(i)
            a = i.address + i.size
        if not got:
            a += 2
    for k, i in enumerate(ins):
        if not (i.mnemonic.startswith("ldr") and "[pc" in i.op_str):
            continue
        reg = i.op_str.split(",")[0]
        try:
            lit = fw.u32(((i.address + 4) & ~3) + int(i.op_str.split("#")[1].rstrip("]"), 16))
        except (ValueError, IndexError):
            continue
        for j in ins[k + 1:k + 4]:
            if j.mnemonic == "add" and j.op_str == f"{reg}, pc":
                if (lit + j.address + 4) & 0xFFFFFFFF != BASE_OBJ:
                    break
                for m in ins[k + 2:k + 14]:
                    for off in OFFS:
                        if f"[{reg}, #{hex(off)}]" in m.op_str:
                            res.append({"literal_en": hex(i.address), "acceso": hex(m.address), "insn": f"{m.mnemonic} {m.op_str}"})
                break
    return res


if __name__ == "__main__":
    r = barrer()
    print(json.dumps(r, indent=1))
