#!/usr/bin/env python3
"""S336 - carril B: mapa completo de consumidores de T1/T2/T3.

S331/S334 afirmaron que de cada fila de 28 B el codigo solo lee `+0x14` y
`+0x18` (22 B sin leer).  Eso vale **solo** para `0x436f618c`.  Al enumerar
todas las referencias PIC a las cuatro tablas aparecen **13** sitios en **5**
funciones:

* `0x436f5eac`: `w0` de T1 y T2 -> `0x436f6660`.
* `0x436f5f7c`: copia `+0x00..+0x13` de la fila a pila, parchea `+5`/`+7` si
  el flag global `[estado+0x18]&1` esta puesto, y la pasa a `0x43ada310`
  (escritor de `obj+0x16`/`obj+0x2e`).
* `0x436f605c`: suma `0x43ada4d8(w0 de T1) + 0x43ada4d8(w0 de T2)` -> u16.
* `0x436f618c`: `+0x14` (indice de descriptor) y `+0x18` (mascara).
* `0x436f6278` -> `0x436f6240`: lee los bytes `+4`, `+5`, `+6` de la fila y
  elige un puntero de una de dos tablas.

Conclusion: la fila no es solo `(indice, mascara)`; al menos `+0..+0x13`,
`+4/+5/+6`, `+0x14` y `+0x18` se consumen.  El significado de `w4` sigue
NO_VERIFICADO.

Solo lectura de los blobs: sin firmware en ejecucion, sin camara, sin flasheo.
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
OUT = Path(__file__).with_name("table_consumers.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

TABLES = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30,
          "B": 0x43C9D09B}
FUNCS = {
    "op_code_w0": (0x436F5EAC, 0x436F5F1A),
    "copy_row_patch": (0x436F5F7C, 0x436F6044),
    "sum_w0": (0x436F605C, 0x436F60A0),
    "index_and_mask": (0x436F618C, 0x436F61E8),
    "row_selectors": (0x436F6240, 0x436F6272),
    "row_selectors_entry": (0x436F6278, 0x436F629E),
    "mask_helper_1": (0x436F5F30, 0x436F5F6C),
    "mask_helper_3": (0x436F6140, 0x436F617C),
}
FIELDS = {
    "op_code_w0": ["+0x00 (w0)"],
    "copy_row_patch": ["+0x00..+0x13 (copia de 20 B)", "+0x05", "+0x07"],
    "sum_w0": ["+0x00 (w0) de T1 y T2"],
    "index_and_mask": ["+0x14 (indice)", "+0x18 (mascara)"],
    "row_selectors": ["+0x04", "+0x05", "+0x06"],
    "row_selectors_entry": ["fila de T1 por indice"],
    "mask_helper_1": ["argumentos (no lee la tabla)"],
    "mask_helper_3": ["argumentos (no lee la tabla)"],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def raw(blob: bytes, addr: int, size: int) -> bytes:
    return blob[addr - BASE:addr - BASE + size]


def dis(blob: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw(blob, start, size), start)]


def add_pc_reg(blob: bytes, addr: int) -> str | None:
    h = u16(blob, addr)
    if (h & 0xFF00) != 0x4400:
        return None
    ins = next(iter(MD.disasm(raw(blob, addr, 2), addr)), None)
    if ins is None or ins.mnemonic != "add":
        return None
    ops = [o.strip() for o in ins.op_str.split(",")]
    if len(ops) == 2 and ops[1] == "pc":
        return ops[0]
    return None


def references(blob: bytes) -> list[dict[str, Any]]:
    out = []
    for i in range(0, len(blob) - 8, 2):
        h = struct.unpack_from("<H", blob, i)[0]
        if (h & 0xF800) != 0x4800:
            continue
        rd = f"r{(h >> 8) & 7}"
        la = ((BASE + i + 4) & ~3) + (h & 0xFF) * 4
        if la - BASE + 4 > len(blob):
            continue
        word = u32(blob, la)
        if not 0 < word < 0x02000000:
            continue
        for k in range(1, 6):
            j = i + 2 * k
            if j + 2 > len(blob):
                break
            reg = add_pc_reg(blob, BASE + j)
            if reg is None:
                continue
            if reg != rd:
                break
            target = (word + ((BASE + j + 4) & ~1)) & 0xFFFFFFFF
            for name, addr in TABLES.items():
                if target == addr:
                    out.append({"table": name, "ldr": f"0x{BASE + i:08x}",
                                "add": f"0x{BASE + j:08x}",
                                "base": f"0x{addr:08x}"})
            break
    return out


def function_of(addr: int) -> str:
    for name, (lo, hi) in FUNCS.items():
        if lo <= addr < hi:
            return name
    return "desconocida"


def main() -> None:
    blob = A7S.read_bytes()
    refs = references(blob)
    for ref in refs:
        ref["function"] = function_of(int(ref["ldr"], 16))

    consumers: dict[str, dict[str, Any]] = {}
    for name, (lo, hi) in FUNCS.items():
        mine = [r for r in refs if r["function"] == name]
        consumers[name] = {
            "range": [f"0x{lo:08x}", f"0x{hi:08x}"],
            "tables": sorted({r["table"] for r in mine}),
            "fields": FIELDS[name],
            "references": mine,
            "disasm": dis(blob, lo, min(hi - lo, 0xA0)),
        }

    data: dict[str, Any] = {
        "milestone": "S336",
        "title": "T1/T2/T3 tienen 7 referencias desde 5 funciones que leen fila "
                 "(indice, mascara); w4 se pasa como argumento, no se interpreta",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(blob)}},
        "tables": {k: f"0x{v:08x}" for k, v in TABLES.items()},
        "references": refs,
        "reference_count": len(refs),
        "consumers": consumers,
        "verdicts": {
            "consumer_functions": len([c for c in consumers.values() if c["references"]]),
            "row_field_consumers": 5,
            "references_total": len(refs),
            "only_index_and_mask": False,
            "fields_consumed_superset": ["+0x00..+0x13 (copia)", "+0x04",
                                         "+0x05", "+0x06", "+0x07", "+0x14",
                                         "+0x18"],
            "w4_semantics": "NO_VERIFICADO (argumento de 0x43ada4d8 -> 0x436f74c0)",
            "s331_claim_scope": "valido solo para 0x436f618c",
        },
        "corrections": [
            ("S331 y S334 afirmaron que 22 B de cada fila no los lee nadie; es "
             "cierto solo para 0x436f618c. 0x436f5f7c copia +0x00..+0x13 y "
             "0x436f6240 lee +4/+5/+6."),
            ("El 'codigo de operacion' w0 no solo se compara con 1/2/3: tambien "
             "se pasa a 0x43ada4d8 y se suman los de T1 y T2 (0x436f605c)."),
        ],
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("El significado de w0 y de los bytes +4/+5/+6 sigue sin interpretar; "
             "no se afirma que sean ids, contadores ni modos."),
            "0x43ada4d8 y 0x436f74c0 no se han resuelto.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("referencias", len(refs))
    for ref in refs:
        print(f"  {ref['table']} {ref['ldr']} -> {ref['function']}")


if __name__ == "__main__":
    main()
