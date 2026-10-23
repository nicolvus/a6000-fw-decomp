#!/usr/bin/env python3
"""S334 - carril B: que pasa con los 12 pares que escribe `0x436f618c`.

S331 dejo tres bloques de 12 pares `(flag, byte)` en `obj+0x16`, `obj+0x2e` y
`obj+0xa5`.  Esta sesion sigue el dataflow:

1. `0x43ada370(obj, pares)` y `0x43ada402(obj, pares, dst, op)` recorren los
   24 B de un bloque y, por cada par con flag != 0, hacen `1 << byte` y lo
   acumulan en un **u16**; luego lo guardan (`obj+0x68` / `dst`) y llaman a
   `0x436f822c(obj+1, mascara, op)`.
   => el segundo byte del par **no es un offset**, es un **indice de bit**.
2. `0x436f61f8` colapsa `obj+0x16` en `obj+0x68`; `0x436f60ac` aplica la mascara
   de `obj+0x68` con `op=0`; `0x436f61f8` colapsa `obj+0xa5` en `obj+0xf8` con
   `op=1`.
3. `0x436f5eac(obj, posicion, flag)` lee el **primer u32 de la fila** (`w0`) de
   T1 y de T2 y lo usa como **codigo de operacion** para `0x436f6660`.
4. `0x436f822c(obj, mascara, op)` aplica la mascara con `op` 0 o 1 (lectura,
   `~valor ^ mascara`, escritura) y registra; `op` 2/otros solo traza.

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
OUT = Path(__file__).with_name("pair_dataflow.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

COLLAPSE_68 = 0x43ADA370
COLLAPSE_DST = 0x43ADA402
FILL_T1T2T3 = 0x436F618C
APPLY_68 = 0x436F60AC
COLLAPSE_ALL = 0x436F61F8
OP_SELECT = 0x436F5EAC
APPLY = 0x436F822C
OP_CALL = 0x436F6660

TABLES = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30}
MODE_LIST = 0x43FEE370
CODES = [0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51, 0x0B]


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


def row(blob: bytes, base: int, index: int) -> dict[str, Any]:
    addr = base + 0x1C * index
    return {"w0": u32(blob, addr), "w4": f"0x{u32(blob, addr + 4):08x}",
            "descriptor_index": u32(blob, addr + 0x14),
            "mask": u16(blob, addr + 0x18)}


def main() -> None:
    blob = A7S.read_bytes()
    codes = [u32(blob, MODE_LIST + 4 * i) for i in range(34)]
    pos = {c: i for i, c in enumerate(codes)}

    tables = {name: [row(blob, base, i) for i in range(34)]
              for name, base in TABLES.items()}
    per_code: dict[str, dict[str, Any]] = {
        f"0x{c:02x}": {"position": pos[c],
                               "T1": tables["T1"][pos[c]],
                               "T2": tables["T2"][pos[c]],
                               "T3": tables["T3"][pos[c]]}
        for c in CODES}

    data: dict[str, Any] = {
        "milestone": "S334",
        "title": "Los 12 pares son (flag, indice de bit) y se colapsan en una "
                 "mascara u16; el w0 de T1/T2 es un codigo de operacion",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(blob)}},
        "collapse": {
            "obj_68": {"address": f"0x{COLLAPSE_68:08x}",
                       "disasm": dis(blob, COLLAPSE_68, 0x34),
                       "input": "obj+0x16 (12 pares)",
                       "output": "u16 en obj+0x68",
                       "loop": "r2 = 0,2,...,0x16; cmp r2,#0x18",
                       "bit_op": "lsls.w r4, r5(=1), r4(byte del par)",
                       "tail": f"0x{APPLY:08x}"},
            "dst": {"address": f"0x{COLLAPSE_DST:08x}",
                    "disasm": dis(blob, COLLAPSE_DST, 0x30),
                    "input": "pares en r1",
                    "output": "u16 en [r2]",
                    "callers": {"0x436f61f8": "obj+0xa5 -> obj+0xf8, op=1"}},
            "callers": {"0x436f61f8": {"address": f"0x{COLLAPSE_ALL:08x}",
                                       "disasm": dis(blob, COLLAPSE_ALL, 0x44)},
                        "0x436f60ac": {"address": f"0x{APPLY_68:08x}",
                                       "disasm": dis(blob, APPLY_68, 0x4C)},
                        "0x436f618c": {"address": f"0x{FILL_T1T2T3:08x}",
                                       "note": "escribe los pares (S331)"}},
        },
        "op_select": {
            "address": f"0x{OP_SELECT:08x}",
            "disasm": dis(blob, OP_SELECT, 0x6C),
            "reads": "w0 de T1 (0/1) y de T2 (2/3) indexado por posicion",
            "target": f"0x{OP_CALL:08x}",
            "per_code": {f"0x{c:02x}": {"T1_w0": tables["T1"][pos[c]]["w0"],
                                        "T2_w0": tables["T2"][pos[c]]["w0"],
                                        "T3_w0": tables["T3"][pos[c]]["w0"]}
                         for c in CODES},
        },
        "apply": {"address": f"0x{APPLY:08x}", "disasm": dis(blob, APPLY, 0x60),
                  "ops": {"0": "0x436f82b0 + ~valor^mascara + 0x436f82a0 + "
                               "0x436f8290 + 0x436f82d0",
                          "1": "0x436f8314 + ~valor^mascara + 0x436f8300 + "
                               "0x436f82e8",
                          "2/otros": "solo traza (0x438f7114)"}},
        "per_code": per_code,
        "verdicts": {
            "pair_second_byte_is_bit_index": True,
            "pair_second_byte_is_state_offset": False,
            "blocks_collapse_to_u16_masks": True,
            "mask_destinations": ["obj+0x68", "obj+0xf8"],
            "w0_is_op_code": True,
            "silent_op_codes": {"0x4c": [0, 2], "0x4d": [0, 2],
                                "0x4e": [0, 2], "0x4f": [0, 2],
                                "0x50": [1, 3], "0x51": [1, 3]},
            "accessor_layer_semantics": "NO_VERIFICADO",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("La capa 0x436f8290/0x436f82a0/0x436f82d0/0x436f82e8/0x436f8300/"
             "0x436f8314/0x436f8324 no se ha resuelto: no se afirma que escriba "
             "MMIO ni que llegue al sensor."),
            ("El indice de bit se toma del objeto 0x43dc02e0 (runtime): el mapeo "
             "campo->bit no esta verificado."),
            "Que las mascaras acaben en una trama P2S es INFERENCIA, no medido.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("op por modo:", data["op_select"]["per_code"])
    print("mascaras:", {k: (v["T1"]["mask"], v["T2"]["mask"], v["T3"]["mask"])
                        for k, v in per_code.items()})


if __name__ == "__main__":
    main()
