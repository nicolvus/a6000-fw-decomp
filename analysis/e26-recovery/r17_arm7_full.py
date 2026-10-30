"""R17: recorrido recursivo completo del BossFirm ARM7 (bootloader.bin[0x18800:+0x3800], base 0). Solo lectura.

Salida: r17-arm7-full.json (funciones, aristas, accesos LDEC, lectores de trabajo+off).
Convención: arista 'directa' = bl/b a destino inmediato; 'puntero' = literal de pool que apunta a código alcanzable.
"""

from __future__ import annotations

import json
import struct
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs
from capstone.arm import ARM_OP_IMM, ARM_OP_MEM, ARM_REG_PC
from r16_arm7 import IMG

MD = Cs(CS_ARCH_ARM, CS_MODE_ARM)
MD.detail = True
N = len(IMG)
LDEC = 0xF2903000


def word(a: int) -> int:
    return struct.unpack_from("<I", IMG, a)[0]


def ins_at(a: int):
    return next(MD.disasm(IMG[a : a + 4], a), None)


def explore() -> dict:
    seeds = {0: "reset"}
    # vectores: ldr pc,[pc,#imm] -> destino en el pool
    for v in range(0, 0x20, 4):
        i = ins_at(v)
        if i and i.mnemonic == "ldr" and i.op_str.startswith("pc, [pc"):
            m = i.operands[1].mem
            t = word(v + 8 + m.disp)
            if t < N:
                seeds[t] = f"vec{v:02x}"
    for k in range(18):  # tabla de despacho 0x379c (18 punteros, §4 del informe R17)
        seeds[word(0x379C + 4 * k)] = f"op{k}"
    for a in (0x2B8, 0x2BC, 0x2C0):  # punteros de pool de vectores IRQ/FIQ
        seeds[word(a)] = f"vecptr{a:03x}"
    funcs: dict[int, str] = dict(seeds)
    edges: list[tuple[int, int, str, int]] = []  # (origen_ins, destino, tipo, func)
    seen: set[int] = set()
    todo = list(funcs)
    owner: dict[int, int] = {}
    pool_ptrs: dict[int, int] = {}
    while todo:
        f = todo.pop()
        stack = [f]
        while stack:
            a = stack.pop()
            while 0 <= a < N and a not in seen:
                seen.add(a)
                owner[a] = f
                i = ins_at(a)
                if i is None:
                    break
                mn = i.mnemonic
                if (
                    mn.startswith("bl")
                    and not mn.startswith("bic")
                    and i.operands
                    and i.operands[0].type == ARM_OP_IMM
                ):
                    t = i.operands[0].imm
                    if (
                        mn.startswith("bl")
                        and mn in ("bl",)
                        or mn.startswith("bl")
                        and len(mn) == 4
                        and mn[2:]
                        in (
                            "eq",
                            "ne",
                            "hs",
                            "lo",
                            "mi",
                            "pl",
                            "vs",
                            "vc",
                            "hi",
                            "ls",
                            "ge",
                            "lt",
                            "gt",
                            "le",
                        )
                    ):
                        if 0 <= t < N:
                            edges.append((a, t, "call", f))
                            if t not in funcs:
                                funcs[t] = f"sub_{t:04x}"
                                todo.append(t)
                        a += 4
                        continue
                if (
                    mn.startswith("b")
                    and mn not in ("bic", "bics", "bfc", "bfi", "bkpt", "blx", "bx")
                    and not mn.startswith("bic")
                    and i.operands
                    and i.operands[0].type == ARM_OP_IMM
                ):
                    t = i.operands[0].imm
                    edges.append((a, t, "branch", f))
                    if 0 <= t < N:
                        stack.append(t)
                    if mn == "b":
                        break
                    a += 4
                    continue
                is_ret = (
                    (mn == "bx" and i.op_str == "lr")
                    or (mn == "pop" and "pc" in i.op_str)
                    or (mn.startswith("ldm") and "pc" in i.op_str)
                )
                if is_ret and i.cc in (0, 14):
                    break
                if (
                    mn.startswith("ldr")
                    and i.operands[0].reg == ARM_REG_PC
                    and i.operands[1].type == ARM_OP_MEM
                ):
                    break  # salto por tabla / ldr pc: no seguimos linealmente
                if mn in ("mov", "movs") and i.op_str.startswith("pc"):
                    break
                a += 4
    # punteros de pool a código (literales que apuntan a funciones/entradas)
    for a in range(0, N - 3, 4):
        v = word(a)
        if v in funcs and a not in owner:
            pool_ptrs[a] = v
    return {
        "funcs": funcs,
        "edges": edges,
        "seen": seen,
        "owner": owner,
        "pool_ptrs": pool_ptrs,
    }


def literal_loads() -> dict[int, int]:
    """dirección de ldr rX,[pc,#d] -> valor del literal"""
    out = {}
    for a in range(0, N, 4):
        i = ins_at(a)
        if (
            i
            and i.mnemonic == "ldr"
            and i.operands[1].type == ARM_OP_MEM
            and i.operands[1].mem.base == ARM_REG_PC
            and i.operands[1].mem.index == 0
        ):
            ea = a + 8 + i.operands[1].mem.disp
            if 0 <= ea < N - 3:
                out[a] = word(ea)
    return out


if __name__ == "__main__":
    r = explore()
    seen = r["seen"]
    funcs = r["funcs"]
    lits = literal_loads()
    ldec_users = sorted(a for a, v in lits.items() if v == LDEC)
    sram_users = sorted(a for a, v in lits.items() if v == 0x3F50)
    out = {
        "bytes": N,
        "code_words_reached": len(seen),
        "coverage_pct": round(4 * len(seen) / N * 100, 1),
        "functions": {hex(k): v for k, v in sorted(funcs.items())},
        "n_functions": len(funcs),
        "ldec_literal_loads": [hex(a) for a in ldec_users],
        "sram_3f50_literal_loads": [hex(a) for a in sram_users],
        "owners_ldec": sorted({hex(r["owner"].get(a, -1)) for a in ldec_users}),
        "owners_sram": sorted({hex(r["owner"].get(a, -1)) for a in sram_users}),
    }
    callers: dict[int, list[str]] = defaultdict(list)
    for o, t, k, f in r["edges"]:
        if k == "call":
            callers[t].append(hex(o))
    out["callers"] = {hex(k): v for k, v in sorted(callers.items())}
    Path(__file__).with_name("r17-arm7-full.json").write_text(json.dumps(out, indent=1))
    print(
        json.dumps(
            {k: v for k, v in out.items() if k not in ("callers", "functions")},
            indent=1,
        )
    )
    print(len(funcs), "funciones")
