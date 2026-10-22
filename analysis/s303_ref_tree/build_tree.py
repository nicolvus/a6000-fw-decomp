#!/usr/bin/env python3
"""S303: reference tree of table 0x43ff3200 and callers of the gate dumper.

All call edges are found by an exhaustive scan of Thumb BL/BLX/B/B.W encodings in
the code range (0x43541000..0x43d00000), so every edge is byte-verifiable.
"""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
OUT = Path(__file__).with_name("ref_tree.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

DUMPER = 0x43858338
CALLER = 0x43859710
TABLE = 0x43FF3200
GOT_SLOT = 0x4401F080


def read(blob, addr, size=4):
    return blob[addr - BASE:addr - BASE + size]


def disasm(blob, addr):
    ins = next(MD.disasm(read(blob, addr), addr), None)
    return f"{ins.mnemonic} {ins.op_str}" if ins else None


def callers(blob, targets):
    """Exhaustive direct-branch scan; returns {target: [(site, mnemonic)]}."""
    hits = {t: [] for t in targets}
    for a in range(0x43541000, 0x43D00000, 2):
        off = a - BASE
        if off + 4 > len(blob):
            break
        hw1 = blob[off] | (blob[off + 1] << 8)
        if (hw1 & 0xF800) != 0xF000:
            continue
        ins = next(MD.disasm(blob[off:off + 4], a), None)
        if ins and ins.mnemonic in ("bl", "blx", "b", "b.w") and ins.op_str.startswith("#"):
            try:
                t = int(ins.op_str[1:], 16)
            except ValueError:
                continue
            if t in targets:
                hits[t].append((a, ins.mnemonic))
    return hits


def prologue(blob, addr, limit=0x600):
    """Nearest preceding push {..., lr} — heuristic container (INFERENCE)."""
    best = None
    for p in range(max(BASE, addr - limit), addr, 2):
        off = p - BASE
        if off + 4 > len(blob):
            break
        hw = blob[off] | (blob[off + 1] << 8)
        if not (hw == 0xE92D or (hw & 0xFE00) == 0xB400):
            continue
        ins = next(MD.disasm(blob[off:off + 4], p), None)
        if ins and ins.mnemonic.startswith("push") and ("lr" in ins.op_str or "pc" in ins.op_str):
            best = p
    return best


def edge(blob, site, mnemonic, target):
    ins = disasm(blob, site)
    return {"site": f"0x{site:08x}", "bytes_hex": read(blob, site).hex(),
            "insn": ins, "kind": mnemonic, "target": f"0x{target:08x}",
            "container": (f"0x{prologue(blob, site):08x}" if prologue(blob, site) else None)}


def main():
    blob = BIN.read_bytes()
    vals = []
    for k in range(400):
        v = int.from_bytes(read(blob, TABLE + 4 * k), "little")
        if not (0x43540000 <= v < 0x44100000):
            break
        vals.append(v)
    level1 = callers(blob, {DUMPER})
    level2 = callers(blob, {CALLER})
    level2_edges = [edge(blob, s, m, CALLER) for s, m in level2[CALLER]]
    containers = {e["container"] for e in level2_edges if e["container"]}
    level3 = callers(blob, {int(c, 16) for c in containers})

    data = {
        "milestone": "S303",
        "title": "árbol de referencias de la tabla 0x43ff3200 y callers del dumper de gates",
        "firmware": {"name": "av-cam.bin (A6000 fw3.21)",
                     "sha256": hashlib.sha256(blob).hexdigest()},
        "base": f"0x{BASE:08x}",
        "table": {
            "base": f"0x{TABLE:08x}",
            "entries": len(vals),
            "terminator": f"0x{TABLE + 4 * len(vals):08x}",
            "unique": len(set(vals)) == len(vals),
            "min": f"0x{min(vals):08x}", "max": f"0x{max(vals):08x}",
            "state_index": vals.index(0x43F72D02),
            "state_entry": f"0x{TABLE + 4 * vals.index(0x43F72D02):08x}",
            "all_entries_are_bss_objects": all(v >= 0x43E00000 for v in vals),
            "got_slot": {"address": f"0x{GOT_SLOT:08x}",
                         "value": f"0x{int.from_bytes(read(blob, GOT_SLOT), 'little'):08x}"},
        },
        "dumper": {
            "entry": f"0x{DUMPER:08x}", "prologue_hex": read(blob, DUMPER).hex(),
            "prologue_insn": disasm(blob, DUMPER),
            "direct_callers": [edge(blob, s, m, DUMPER) for s, m in level1[DUMPER]],
        },
        "caller_function": {
            "entry": f"0x{CALLER:08x}", "prologue_hex": read(blob, CALLER).hex(),
            "prologue_insn": disasm(blob, CALLER),
            "callers": level2_edges,
        },
        "level3": {f"0x{t:08x}": [edge(blob, s, m, t) for s, m in v]
                   for t, v in level3.items()},
        "corrections": {
            "0x438581e8": {"bytes_hex": read(blob, 0x438581E8).hex(),
                           "insn": disasm(blob, 0x438581E8),
                           "why": "no es entrada de función: cae dentro de FUN_43858190"},
            "0x43858390": {"bytes_hex": read(blob, 0x43858390).hex(),
                           "insn": disasm(blob, 0x43858390),
                           "why": "no es entrada de función: es el byte +0x58 de FUN_43858338"},
        },
        "scope_limit": "Solo llamadas directas BL/BLX/B/B.W en 0x43541000..0x43d00000; "
                       "no cubre llamadas indirectas ni alcanzabilidad runtime.",
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"table={len(vals)} state_idx={data['table']['state_index']} "
          f"dumper_callers={len(level1[DUMPER])} caller_callers={len(level2[CALLER])}")


if __name__ == "__main__":
    main()
