"""Seguimiento S402: bloque de ajustes G (A7S `S[0]`≡G, A6000 `+0x238`) y emisor del mensaje (0x3a49, 0x3026).

Solo bytes originales y Capstone; no se ejecuta firmware. Resultado en followup_blocks.json.
"""

import json
import re
import struct
from collections import defaultdict
from pathlib import Path

import fw
import rawfw
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

OUT = Path(__file__).with_name("followup_blocks.json")
G = {"A6000": 0x43EDF684, "A7S": 0x43EA1D84}
PCREL = re.compile(r"\[pc, #(-?)(0x[0-9a-f]+|\d+)\]")


def disasm(model: str):
    lib = rawfw.RawLib(model)
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.skipdata = True
    return lib, list(cs.disasm_lite(lib.e.data, rawfw.BASE))


def anchors(lib, ins, target: int):
    """Índices (ldr literal, add pc) cuyo destino PIC es `target` (± 0x700) y desplazamiento al destino."""
    base = rawfw.BASE
    for i, (a, _, m, o) in enumerate(ins):
        mm = PCREL.search(o)
        if not (m.startswith("ldr") and mm):
            continue
        pool = ((a + 4) & ~3) + int(mm[2], 0) * (-1 if mm[1] else 1)
        if not base <= pool < base + len(lib.e.data) - 3:
            continue
        value, reg = struct.unpack_from("<I", lib.e.data, pool - base)[0], o.split(",")[0]
        for k in range(i + 1, min(i + 6, len(ins))):
            if ins[k][2] == "add" and ins[k][3] == f"{reg}, pc":
                resolved = (value + ins[k][0] + 4) & 0xFFFFFFFF
                if 0 <= target - resolved < 0x700:
                    yield k, reg, target - resolved
                break


def writers_and_readers(model: str, offsets: list[int]) -> dict:
    """Escritores directos (ancla PIC de G) y lectores `ldr rY,[rX]; ldr.w rZ,[rY,#off]` por doble indirección."""
    lib, ins = disasm(model)
    res: dict = {hex(o): {"anchor_stores": [], "double_indirect_reads": []} for o in offsets}
    for off in offsets:
        for k, reg, delta in anchors(lib, ins, G[model] + off):
            for x in ins[k + 1:k + 30]:
                if re.search(rf"\[{reg}, #{hex(delta)}\]", x[3]) and x[2].startswith("str"):
                    res[hex(off)]["anchor_stores"].append(hex(x[0]))
        for i, (a, _, m, o) in enumerate(ins):
            mm = re.fullmatch(r"(\w+), \[(\w+), #(0x[0-9a-f]+)\]", o)
            if mm and m.startswith("ldr") and int(mm[3], 16) == off and any(
                p[2].startswith("ldr") and re.fullmatch(rf"{mm[2]}, \[\w+\]", p[3]) for p in ins[max(0, i - 3):i]
            ):
                res[hex(off)]["double_indirect_reads"].append(hex(a))
    for v in res.values():
        v["anchor_stores"] = sorted(set(v["anchor_stores"]))
    return res


def emitter_3026() -> dict:
    """Constructores `ObjMsg::SetCateIdMsgId(cat, 0x3026)` en libObj A6000 (barrido de .text, movw r2 + llamada)."""
    lib = fw.Lib("A6000")
    text = lib.e.sections[".text"]
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    cs.skipdata = True
    ins = list(cs.disasm_lite(lib.e.read(text[3], text[5]), text[3]))
    hits: dict = defaultdict(list)
    for i, (a, _, m, o) in enumerate(ins):
        if m != "movw" or o != "r2, #0x3026":
            continue
        call = next((x for x in ins[i + 1:i + 3] if x[2] in ("bl", "blx") and x[3].startswith("#")), None)
        if call and lib.name(int(call[3][1:], 16)) == "_ZN3MWF6ObjMsg14SetCateIdMsgIdEjj":
            cat = next((x[3] for x in ins[max(0, i - 3):i] if x[2] == "movw" and x[3].startswith("r1,")), "?")
            hits[hex(lib.fstart(a))].append({"site": hex(a), "cat": cat.split("#")[-1]})
    callers = [hex(a) for a, _, m, o in ins if m in ("bl", "blx") and o in {f"#{k}" for k in hits}]
    return {"constructores": dict(hits), "llamadores": callers}


def main() -> None:
    a7s = writers_and_readers("A7S", [0x250, 0x56C, 0x570])
    a6000 = writers_and_readers("A6000", [0x238])
    emitters = emitter_3026()
    result = {
        "A7S_G_0x43ea1d84": a7s,
        "A6000_G_0x43edf684": a6000,
        "emisor_ObjMsg_cat_0x3026": emitters,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    main()
