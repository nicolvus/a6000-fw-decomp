#!/usr/bin/env python3
"""S327 - carril B: quien escribe `obj+0x2b4` (indice de fila de T1/T2/T3).

S326 dejo como **INFERENCIA** que la fila de T1/T2/T3 fuese la posicion del modo en
`0x43fee370`. Esta sesion localiza los escritores del campo y los consumidores.

Resultado:

* Solo hay **dos** escritores de `obj+0x2b4` en el rango de la clase:
  - `0x436f2d74` en el constructor base: `str.w r3,[r4,#0x2b4]` con `r3 = 0`
    (inicializacion).
  - `0x436f40fe` en el **constructor parametrico** `0x436f3fc0(obj, idx)`:
    `mov r6, r1` al entrar y `str.w r6,[r4,#0x2b4]` al final → guarda el
    **parametro de construccion**, no una posicion de modo.
* El unico llamador estatico (`0x436f2a8a`) hace `movs r1,#0` → **idx = 0**.
* Hay 9 lectores de `+0x2b4`, todos `ldr`; ninguno lo deriva de un codigo de modo.

Consecuencia: en la unica instancia visible `obj+0x2b4 = 0`, de modo que T1/T2/T3 se leen
en la **fila 0**. La correspondencia fila↔modo de S326 (y las filas 29/30 = `0x4e`/`0x4f`)
queda **NO_VERIFICADA**.

No ejecuta firmware ni toca la camara: solo lectura de los blobs.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("row_index_writer.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u32(blob: bytes, a: int) -> int:
    return struct.unpack_from("<I", blob, a - BASE)[0]


def dis(blob: bytes, start: int, size: int) -> list[dict]:
    raw = blob[start - BASE:start - BASE + size]
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw, start)]


def scan_stores(blob: bytes, lo: int, hi: int) -> list[dict]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.skipdata = True
    out: list[dict] = []
    raw = blob[lo - BASE:hi - BASE]
    for i in md.disasm(raw, lo):
        if i.mnemonic.startswith("str") and "#0x2b4]" in i.op_str:
            out.append({"address": f"0x{i.address:08x}", "insn": f"{i.mnemonic} {i.op_str}"})
    return out


def scan_loads(blob: bytes, lo: int, hi: int) -> list[dict]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.skipdata = True
    out: list[dict] = []
    raw = blob[lo - BASE:hi - BASE]
    for i in md.disasm(raw, lo):
        if (i.mnemonic.startswith("ldr") and "#0x2b4]" in i.op_str
                and "[pc" not in i.op_str):
            out.append({"address": f"0x{i.address:08x}", "insn": f"{i.mnemonic} {i.op_str}"})
    return out


def main() -> None:
    a7s = A7S.read_bytes()
    a6 = A6000.read_bytes()

    stores = scan_stores(a7s, 0x436F2000, 0x436F7000)
    loads = scan_loads(a7s, 0x436F2000, 0x436F7000)
    ctor = dis(a7s, 0x436F3FC0, 0x14)          # entrada: push, sub sp, mov r4/r6
    ctor_tail = dis(a7s, 0x436F40F8, 0x0C)     # str.w r6,[r4,#0x2b4]
    base_ctor = dis(a7s, 0x436F2D62, 0x16)     # zero-init
    caller = dis(a7s, 0x436F2A7C, 0x14)        # movs r1,#0 ; bl ctor

    data: dict[str, Any] = {
        "milestone": "S327",
        "title": "obj+0x2b4 guarda el indice del constructor parametrico (0), no una "
                 "posicion de modo",
        "base": f"0x{BASE:08x}",
        "firmware": {
            "a7s_fw320": {"sha256": sha256(A7S), "size": len(a7s)},
            "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)},
        },
        "stores": stores,
        "loads": loads,
        "store_count": len(stores),
        "load_count": len(loads),
        "parametric_ctor": {
            "function": "0x436f3fc0",
            "signature": "(obj, idx)",
            "entry": ctor,
            "tail": ctor_tail,
            "idx_register": "r6 = r1",
            "field": "+0x2b4",
        },
        "base_ctor_zero_init": {"function": "0x436f2d44", "instructions": base_ctor},
        "caller": {"function": "0x436f2a7c", "instructions": caller,
                   "idx_value": 0,
                   "site": "0x436f2a8a"},
        "verdict": {
            "field_semantics": "indice de construccion (parametro idx)",
            "visible_instance_idx": 0,
            "rows_reached": [0],
            "s326_row_mode_mapping": "NO_VERIFICADO / sin soporte en este escritor",
            "silent_rows_29_30_reachable": False,
        },
        "scope_limit": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("El constructor parametrico podria invocarse de forma dinamica con otro idx "
             "(tabla de punteros o modulo externo): no se descarta, solo consta un llamador "
             "estatico con idx=0."),
            ("No se interpreta el indice de construccion: no se afirma que seleccione un "
             "modo, un canal ni una variante de lectura."),
            ("S326 conserva sus mediciones de T2; solo su emparejamiento fila<->modo queda "
             "sin soporte."),
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"escrito {OUT.name}: {len(stores)} escritores, {len(loads)} lectores, "
          f"idx del llamador = 0")


if __name__ == "__main__":
    main()
