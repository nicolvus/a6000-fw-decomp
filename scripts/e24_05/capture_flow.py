"""E24-05a: flujo de captura BIONZ -> Darwin -> máquina de 49 estados -> respuesta (solo lectura de bytes).

Reproducible: `python scripts/e24_05/capture_flow.py` imprime el JSON y lo guarda en analysis/e24-05a/capture-flow.json.
Cada hecho se calcula desde `darwin_core.bin` (3.21) o, para el lado BIONZ, desde `av-cam.bin` (si existe).
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dwn import ROOT, Core

AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
AV_BASE = 0x43541000

DESC, TABLE, N_STATES = 0x28FDC, 0x28FF8, 0x31
LIST_PTRS = {0x28F88: "S+0x32=0 o S+0x3c fuera de 1..4", 0x28F98: "tipo 1, S+0x44.b0=0", 0x28FA8: "tipo 1, S+0x44.b0=1",
             0x28FBA: "tipo 2-4, S+0x44.b0=0", 0x28FCA: "tipo 2-4, S+0x44.b0=1"}
MSG_TABLE, MSG_FIRST = 0x27C68, 0x0B


def states(c: Core) -> dict[int, int]:
    """{id: manejador Thumb}: la tabla son pares (id, puntero) de 8 B; el id coincide con el índice."""
    return {c.u32(TABLE + 8 * k): c.u32(TABLE + 8 * k + 4) - 1 for k in range(N_STATES)}


def state_lists(c: Core) -> dict[int, list[int]]:
    out = {}
    for ptr in LIST_PTRS:
        ids, a = [], ptr
        while True:
            ids.append(c.u8(a))
            a += 1
            if ids[-1] == N_STATES:  # 0x31 = id terminal
                break
        out[ptr] = ids
    return out


def message_table(c: Core) -> list[dict]:
    rows, a, i = [], MSG_TABLE, MSG_FIRST
    while True:
        tx, rx, ln, code = (c.u32(a + 4 * k) for k in range(4))
        if code & 0xFF != 3 or not all(v == 0 or 0x20000000 <= v < 0x20010000 for v in (tx, rx)):
            break
        rows.append({"id": i, "dir": {1: "Darwin→BIONZ", 2: "BIONZ→Darwin"}[(code >> 16) & 0xFF], "len": ln,
                     "buf": tx or rx, "addr": a, "sub": (code >> 8) & 0xFF})
        a += 16
        i += 1
    return rows


def busy_bit_decode(c: Core) -> dict[int, int]:
    """S+0x43 = f(máscara de ocupación): bit -> código, leído del cascada `lsls rX,r0,#k; bpl` de 0x17e94."""
    out = {}
    code = None
    for ins in c.dis(0x17EBE, 0xCA):
        if ins.mnemonic == "lsls" and ins.op_str.startswith("r1, r0, #"):
            bit = 31 - int(ins.op_str.split("#")[1], 0)
            code = bit
        elif ins.mnemonic == "movs" and ins.op_str.startswith("r4, #") and code is not None:
            out[code] = int(ins.op_str.split("#")[1], 0)
            code = None
    return out


def class_predicate(pkt1: int, mech_type: int) -> dict:
    """Emula 0x17f8c (reescritura de S+0x31 por tipo, 0x180e6/0x180f4/0x1808e) y el predicado 0x196a2."""
    s31 = pkt1
    if mech_type in (1, 2):
        s31 &= ~3
    elif mech_type == 3:
        s31 = ((s31 & ~3) + 1) & 0xFF
    elif mech_type == 4:
        s31 = (((s31 & ~3) + 2) & 0xFF) & ~0x40
    pred = 1 if (s31 & 3) == 0 or (s31 & 0x40) else 0
    return {"S31": s31, "0x196a2": pred}


def avcam_checks() -> dict | None:
    if not AVCAM.exists():
        return None
    d = AVCAM.read_bytes()
    u32 = lambda a: struct.unpack_from("<I", d, a - AV_BASE)[0]
    # `ldr.w rX,[pc,#imm]` en `a`, seguido de `add rX,pc` en `a+4` (PC = a+8): dirección = literal + a + 8
    rel = lambda a, imm: hex((u32(((a + 4) & ~3) + imm) + a + 8) & 0xFFFFFFFF)
    return {
        "variable_clase_0x43841360": rel(0x43841360, 0x59C),
        "byte_flag_0x4384136c": rel(0x4384136C, 0x594),
        "byte_flag_0x43841380": rel(0x43841380, 0x584),
        "byte_flag_0x43841350": rel(0x43841350, 0x5A8),
        "bytes_pkt1": d[0x43841342 - AV_BASE:0x43841398 - AV_BASE].hex(),
    }


def main() -> dict:
    c = Core()
    st = state_lists(c)
    res = {
        "descriptor": {"addr": hex(DESC), "tabla": hex(c.u32(DESC)), "n": c.u32(DESC + 4), "vars": [hex(c.u32(DESC + 8)), hex(c.u32(DESC + 12)), hex(c.u32(DESC + 16))],
                       "terminal": c.u32(DESC + 20), "refs_palabra": [hex(a) for a in c.word_refs(DESC)], "refs_ldr": [hex(a) for a in c.ldr_users(DESC)]},
        "listas": {hex(p): {"cuando": LIST_PTRS[p], "ids": [hex(i) for i in ids]} for p, ids in st.items()},
        "estados": {hex(k): hex(v) for k, v in states(c).items()},
        "mensajes": message_table(c),
        "bit_ocupacion": {str(k): hex(v) for k, v in busy_bit_decode(c).items()},
        "predicado_0x196a2": {f"tipo{t}/pkt1={p:#04x}": class_predicate(p, t) for t in range(5) for p in (0, 2, 0x40, 0x42)},
        "avcam": avcam_checks(),
    }
    out = ROOT / "analysis/e24-05a/capture-flow.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, ensure_ascii=False)[:6000])
