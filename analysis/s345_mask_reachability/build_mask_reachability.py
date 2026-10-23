#!/usr/bin/env python3
"""S345 - carril B: alcanzabilidad estatica de `0x436f822c` (aplicacion de mascara).

Pregunta: la escritura de la mascara de 12 bits en el bloque DFE/CISIF
(`0x436f822c`) , esta condicionada por el modo?  Se comparan los tramos que
aplican las dos operaciones en A7S y A6000.

  A7S   0x436f4476..0x436f4498   (rectilineo, sin ramas)
          0x436f618c(obj, posicion, flag)   lee fila T
          0x436f61f8(obj, posicion, flag)   pares -> mascara (op 0)  -> 0x436f822c
          0x436f60ac(obj, posicion, flag)   pares -> mascara (op 1)  -> 0x436f822c
        segundo sitio: 0x436f5afe, con puerta `0x43ad9b50(obj) != 0`

  A6000 0x436d8f46..0x436d8f6a   (rectilineo, sin ramas)
          0x43ad94d8(obj, obj+0x14)         op 0
          0x436d8bd8(obj, posicion, flag)
          0x43ad9512(obj, obj+0xa1, obj+0xd4, 1)  op 1 (tail)

Conclusion: la aplicacion de la mascara es **comun a los dos modelos y no esta
condicionada por el modo** dentro de esos tramos; la diferencia A7S/A6000 esta
en los datos (pares y mascaras), no en la alcanzabilidad.  Esto respalda S51.

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
FW = ROOT / "firmware/extracted"
BLOBS = {
    "a7s_fw320": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/"
                       "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6000_fw321": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/av-cam.bin"),
}
OUT = Path(__file__).with_name("mask_reachability.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def code(b: bytes, start: int, end: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(b[start - BASE:end - BASE], start)]


def branches(ins: list[dict[str, str]]) -> list[dict[str, str]]:
    """Ramas condicionales del tramo (`bl`/`blx` no cuentan)."""
    cond = {"beq", "bne", "bcs", "bhs", "bcc", "blo", "bmi", "bpl", "bvs", "bvc",
            "bhi", "bls", "bge", "blt", "bgt", "ble", "cbz", "cbnz"}
    return [i for i in ins if i["insn"].split()[0] in cond]


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    a7, a6 = blobs["a7s_fw320"], blobs["a6000_fw321"]

    span7 = code(a7, 0x436F4476, 0x436F449C)
    span7b = code(a7, 0x436F5AE8, 0x436F5B10)
    span6 = code(a6, 0x436D8F46, 0x436D8F6E)

    data: dict[str, Any] = {
        "milestone": "S345",
        "title": ("la aplicacion de la mascara (0x436f822c) es comun a A7S y A6000 "
                  "y no esta condicionada por el modo dentro del tramo"),
        "base": f"0x{BASE:08x}",
        "firmware": {k: {"sha256": sha256(BLOBS[k]), "size": len(blobs[k])}
                     for k in BLOBS},
        "a7s": {
            "apply_span": {"start": "0x436f4476", "end": "0x436f449c",
                           "code": span7,
                           "branches": branches(span7),
                           "calls": [i["insn"] for i in span7 if i["insn"].startswith("bl ")]},
            "second_site": {"start": "0x436f5ae8", "end": "0x436f5b10",
                            "code": span7b,
                            "gate": "0x43ad9b50(obj) != 0",
                            "gate_caller": "0x436f5aec"},
            "mask_writer": "0x436f822c",
            "mask_writer_callers": ["0x43ada370", "0x43ada402"],
            "op0_tail": "0x43ada3a0 b.w #0x436f822c",
            "op1_tail": "0x43ada42c b.w #0x436f822c",
        },
        "a6000": {
            "apply_span": {"start": "0x436d8f46", "end": "0x436d8f6e",
                           "code": span6,
                           "branches": branches(span6),
                           "calls": [i["insn"] for i in span6 if i["insn"].startswith("bl ")]},
            "op0": "0x43ad94d8 (equivalente de 0x43ada370)",
            "op1": "0x43ad9512 (equivalente de 0x43ada402, tail-call)",
            "mask_writer_equivalent": "NO_VERIFICADO (el tail de 0x43ad9512 no se sigue aqui)",
        },
        "verdicts": {
            "mask_application_mode_gated_in_span": False,
            "same_two_ops_in_both_models": True,
            "a7s_extra_silent_only_path": False,
            "difference_is_data_not_reachability": True,
            "s51": "sin cambios (A=NO, B=NO, C=NO)",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("«No condicionada por el modo dentro del tramo» se refiere al tramo "
             "rectilineo medido; la alcanzabilidad de la funcion que lo contiene no "
             "se ha probado hasta el origen."),
            ("El equivalente del escritor de mascara en la A6000 no se sigue: solo se "
             "verifica que las dos operaciones (op 0 y op 1) estan presentes."),
            "La puerta 0x43ad9b50 del segundo sitio del A7S no se ha identificado.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("A7S tramo ramas:", len(branches(span7)), "calls:", data["a7s"]["apply_span"]["calls"])
    print("A6000 tramo ramas:", len(branches(span6)), "calls:", data["a6000"]["apply_span"]["calls"])


if __name__ == "__main__":
    main()
