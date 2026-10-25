#!/usr/bin/env python3
"""Hallazgos estáticos S403 que se reproducen solo con bytes: E2 (check de estado), E4 (tabla de modos), E8 (enlaces de lectores),
E12 (buzón 0x0110027c). Salida: static_findings.json. Las funciones se identificaron con REA (sesión única); aquí se re-comprueban
las aristas con un barrido propio de BL/B.W y las instrucciones citadas con Capstone."""
import json
import re
import struct
import sys
from pathlib import Path

import pic
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm import ARM_OP_MEM

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s402_static_closure"))
import fw

B = pic.BASE
OUT = Path(__file__).with_name("static_findings.json")
CS = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def insn(blob: bytes, addr: int) -> str:
    i = next(CS.disasm(blob[addr - B:addr - B + 4], addr, count=1))
    return f"{i.mnemonic} {i.op_str}"


def anchored_access(blob: bytes, target: int, pattern: str, window: int = 16) -> tuple[int, list[dict]]:
    """Anclas PIC a `target` y accesos `pattern` (regex sobre op_str con {reg}) dentro de `window` instrucciones, sin recargar el registro."""
    refs = [r for r in pic.pic_refs(blob) if r["target"] == target]
    hits = []
    for r in refs:
        reg = f"r{r['reg']}"
        o = r["add"] - B
        for i in list(CS.disasm(blob[o:o + 4 * window], r["add"], count=window))[1:]:
            if re.search(pattern.format(reg=reg), i.op_str):
                hits.append({"ancla": hex(r["add"]), "addr": hex(i.address), "insn": f"{i.mnemonic} {i.op_str}"})
            if i.op_str.startswith(reg + ",") and i.mnemonic in ("ldr", "mov", "movs", "add", "adds"):
                break
    return len(refs), hits


def slot_sites(blob: bytes) -> list[dict]:
    """Sitios que cargan el slot GOT `0x4401f990` (GOT `0x4401eee4` + `0xaac`) y los accesos de campo posteriores al objeto `0x43f72d02`."""
    got = 0x4401EEE4
    anchors = {r["add"] for r in pic.pic_refs(blob) if r["target"] == got}
    detail = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    detail.detail = True
    out = []
    for i in range(0, len(blob) - 1, 2):
        h = struct.unpack_from("<H", blob, i)[0]
        if h & 0xF800 != 0x4800:
            continue
        a = B + i
        pool = ((a + 4) & ~3) + (h & 0xFF) * 4 - B
        if pool + 4 > len(blob) or struct.unpack_from("<I", blob, pool)[0] != 0xAAC:
            continue
        reg = (h >> 8) & 7
        if not any(a - 30 <= x <= a + 30 for x in anchors):
            continue
        ins = list(detail.disasm(blob[a - B:a - B + 160], a, count=40))
        k = next((k for k, x in enumerate(ins[1:10], 1) if x.mnemonic.startswith("ldr") and re.search(rf"\br{reg}\]", x.op_str)), None)
        if k is None:
            continue
        ptr, acc = ins[k].op_str.split(",")[0], []
        for x in ins[k + 1:k + 30]:
            if x.mnemonic.startswith(("ldr", "str")):
                acc += [(x.mnemonic, op.mem.disp) for op in x.operands if op.type == ARM_OP_MEM and x.reg_name(op.mem.base) == ptr]
            if x.op_str.startswith(ptr + ",") and not x.mnemonic.startswith(("str", "cmp")):
                break  # el registro deja de ser el puntero (incluye `ldr rP,[rP,#d]`, ya registrado arriba)
        out.append({"sitio": hex(a), "accesos": [{"insn": m, "disp": hex(d)} for m, d in acc]})
    return out


def edges(blob: bytes, pairs: list[tuple[int, int]]) -> list[dict]:
    """(llamado, llamador): ¿hay un BL/B.W al llamado dentro de los 0x4000 B siguientes al inicio del llamador?"""
    out = []
    for callee, caller in pairs:
        sites = [s for s in pic.branch_sites(blob, callee) if caller <= s < caller + 0x4000]
        out.append({"callee": hex(callee), "caller": hex(caller), "sitios": [hex(s) for s in sites]})
    return out


def main() -> None:
    blob = pic.load("a6000")
    lib = fw.Lib("A6000")
    # E2: check 0x907ba0 compara GetMessageId con la palabra de pool cargada en 0x907bcc
    pool = ((0x907BCC + 4) & ~3) + 0xA4
    msg_id = lib.e.u32(pool)
    e2 = {"check": "0x907ba0", "pool": hex(pool), "id_comparado": hex(msg_id),
          "fila_de_estado_mensaje": "0x10000005", "devuelve_1_para_la_fila": msg_id != 0x10000005,
          "ldr": [x for x in [f"{i.mnemonic} {i.op_str}" for i in CS.disasm(lib.e.read(0x907BCC, 4), 0x907BCC)][:1]]}
    # E4: tabla booleana por modo (0..10) y máscaras de 0x4379d378
    w = struct.unpack_from("<I", blob, 0x4379D374 - B)[0]
    tbl = (w + 0x4379D36A + 4) & 0xFFFFFFFF
    e4 = {"tabla": hex(tbl), "bytes_0_10": list(blob[tbl - B:tbl - B + 11]),
          "mascara_1": insn(blob, 0x4379D388), "mascara_0": insn(blob, 0x4379D38E), "mascara_2": insn(blob, 0x4379D394),
          "limite": insn(blob, 0x4379D378)}
    # E8: cadenas de llamadores de los dos lectores del estado 0x43f72d02
    e8 = {"lector1": edges(blob, [(0x43861400, 0x437B5E70), (0x437B5E70, 0x43AEF444), (0x43AEF444, 0x4379210C)]),
          "lector2": edges(blob, [(0x438690DC, 0x43844E80), (0x43844E80, 0x437B5B14)])}
    # E12: emisores al buzón 0x0110027c y formato del mensaje de 0x437b0390
    pat = struct.pack("<I", 0x0110027C)
    words = [B + i for i in range(0, len(blob) - 3, 4) if blob[i:i + 4] == pat]
    e12 = {"buzon": "0x0110027c", "palabras_de_pool": [hex(x) for x in words],
           "emisor": "0x437b0390", "mensaje": {"len": 0x14, "tipo": 3, "sub": 0x22}, "movw_movt": 0,
           "stores": [insn(blob, a) for a in (0x437B03AC, 0x437B03B2, 0x437B03B4, 0x437B03BA)]}
    # E5: accesos a +0x238 del bloque de ajustes A6000 (0x43edf684) y almacenes en [S+0] de A7S (S = 0x43ea70a0)
    n6, h6 = anchored_access(blob, 0x43EDF684, r"\[{reg}, #0x238\]")
    a7 = pic.load("a7s")
    nS, hS = anchored_access(a7, 0x43EA70A0, r"^(r\d+), \[{reg}(, #0)?\]$")
    e5 = {"a6000_anclas_a_G": n6, "a6000_accesos_0x238": h6, "a7s_anclas_a_S": nS,
          "a7s_stores_en_S0": [h for h in hS if h["insn"].startswith("str")]}
    e7 = {"slot": "0x4401f990", "objeto": "0x43f72d02", "sitios": slot_sites(blob)}
    res = {"E2": e2, "E4": e4, "E5": e5, "E7": e7, "E8": e8, "E12": e12}
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res)[:2200])


if __name__ == "__main__":
    main()
