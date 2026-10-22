#!/usr/bin/env python3
"""S309: presence of the A7S silent/config chain in the A6000 by 24-byte prologue signature."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("presence.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

CHAIN = [
    ("selector_caller", 0x43548C70, "configura y llama al selector silent"),
    ("selector", 0x43826D58, "tipo==2 -> 0x4e/0x4f"),
    ("message_builder", 0x43AD96FA, "recibe el codigo de modo"),
    ("config_caller", 0x43861A58, "construye el buffer y llama al bloque de tiempos"),
    ("timing_block", 0x438645BC, "lee +0xae, escribe +0xde/+0xe6..+0xea"),
    ("trio_writer", 0x438642F0, "escribe +0xe6/+0xe8/+0xea"),
    ("de_writer", 0x43865100, "escribe +0xde"),
]


def main():
    a6, a7 = A6.read_bytes(), A7.read_bytes()

    def head(blob, addr, n=24):
        return blob[addr - BASE:addr - BASE + n]

    rows = []
    for label, addr, role in CHAIN:
        h = head(a7, addr)
        ins = next(MD.disasm(h[:4], addr), None)
        rows.append({"label": label, "entry": f"0x{addr:08x}", "role": role,
                     "head_hex": h.hex(),
                     "insn": f"{ins.mnemonic} {ins.op_str}" if ins else None,
                     "a6000_hits": a6.count(h)})
    data = {
        "milestone": "S309",
        "title": "la cadena silent/config de la A7S no aparece en la A6000",
        "firmware": {"a6000": hashlib.sha256(a6).hexdigest(),
                     "a7s": hashlib.sha256(a7).hexdigest()},
        "base": f"0x{BASE:08x}",
        "chain": rows,
        "scope_limit": "Coincidencia exacta de 24 B de prólogo; no prueba ausencia de "
                       "funcionalidad equivalente reescrita en la A6000.",
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    for r in rows:
        print(r["label"], r["entry"], "A6000 hits:", r["a6000_hits"])


if __name__ == "__main__":
    main()
