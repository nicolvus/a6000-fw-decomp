#!/usr/bin/env python3
"""S346 - carril B: productor del array `.bss` `0x43e906f4` (consumidor B de S342).

El consumidor B de S342 recorre 69 dwords en `0x43e906f4` (un puntero de la GOT).
Ese array esta en `.bss` (cero en la imagen).  Buscando quien lo escribe:

  * el valor `0x43e906f4` solo aparece **una** vez en el blob: el slot GOT
    `0x44026240`;
  * el slot solo se referencia desde **dos** sitios, ambos de los consumidores
    de S342 (`0x43705716` y `0x4370575e`, offset `0x1d00` sobre `0x44024540`);
  * esos dos sitios **pasan la direccion** a *thunks* que despachan por la
    vtable `[global+0x14] + 0x2c8 / +0x2cc`.

Conclusion: no hay escritor estatico; el array lo rellena el servicio invocado
por esos *thunks*.  La A6000 repite el patron (slot `0x44020730` -> `0x43e8197c`,
offset `0x184c`, dos referencias en los mismos consumidores).

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
OUT = Path(__file__).with_name("array_producer.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def code(b: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(b[start - BASE:start - BASE + size], start)]


def literal_refs(b: bytes, value: int) -> list[dict[str, str]]:
    """Sitios `ldr rX,[pc,#imm]` cuyo literal vale `value`."""
    out = []
    pat = struct.pack("<I", value)
    i = b.find(pat)
    while i >= 0:
        lit = BASE + i
        for back in range(2, 0x400, 2):
            a = lit - back
            if a < BASE:
                break
            h = u16(b, a)
            if (h & 0xF800) == 0x4800 and ((a + 4) & ~3) + (h & 0xFF) * 4 == lit:
                out.append({"ldr": f"0x{a:08x}", "literal_addr": f"0x{lit:08x}",
                            "value": f"0x{u32(b, lit):08x}"})
                break
        i = b.find(pat, i + 1)
    return out


def pic_bases_to(b: bytes, target: int) -> list[str]:
    out = []
    n = len(b)
    for off in range(0, n - 8, 2):
        h = u16(b, BASE + off)
        if (h & 0xF800) != 0x4800:
            continue
        rd = (h >> 8) & 7
        lit = ((BASE + off + 4) & ~3) + ((h & 0xFF) * 4)
        if lit - BASE + 4 > n:
            continue
        word = u32(b, lit)
        for k in (2, 4, 6, 8):
            add = BASE + off + k
            h2 = u16(b, add)
            if ((h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
                    and (h2 & 7) == rd and ((h2 >> 7) & 1) == 0):
                if (word + ((add + 4) & ~1)) & 0xFFFFFFFF == target:
                    out.append(f"0x{BASE + off:08x}")
                break
    return out


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    a7, a6 = blobs["a7s_fw320"], blobs["a6000_fw321"]
    slot7, array7 = 0x44026240, 0x43E906F4
    slot6, array6 = 0x44020730, 0x43E8197C

    data: dict[str, Any] = {
        "milestone": "S346",
        "title": ("el array .bss 0x43e906f4 no tiene escritor estatico: se rellena por "
                  "la vtable del servicio ([global+0x14]+0x2c8/+0x2cc)"),
        "base": f"0x{BASE:08x}",
        "firmware": {k: {"sha256": sha256(BLOBS[k]), "size": len(blobs[k])}
                     for k in BLOBS},
        "a7s": {
            "array": f"0x{array7:08x}",
            "array_is_zero_in_image": all(a7[array7 - BASE + i] == 0 for i in range(0x114)),
            "occurrences_of_array_literal": len(_find_all(a7, struct.pack("<I", array7))),
            "slot": f"0x{slot7:08x}",
            "slot_value": f"0x{u32(a7, slot7):08x}",
            "slot_offset_from_got": f"0x{slot7 - 0x44024540:08x}",
            "slot_refs": [r["ldr"] for r in literal_refs(a7, slot7 - 0x44024540)],
            "pic_bases_to_array": pic_bases_to(a7, array7),
            "thunks": {
                "0x4355f790": code(a7, 0x4355F790, 0x10),
                "0x4355f7ac": code(a7, 0x4355F7AC, 0x10),
            },
            "vtable_slots": {"0x4355f790": "0x2c8", "0x4355f7ac": "0x2cc"},
        },
        "a6000": {
            "array": f"0x{array6:08x}",
            "slot": f"0x{slot6:08x}",
            "slot_value": f"0x{u32(a6, slot6):08x}",
            "slot_offset_from_got": f"0x{slot6 - 0x4401EEE4:08x}",
            "slot_refs": [r["ldr"] for r in literal_refs(a6, slot6 - 0x4401EEE4)],
        },
        "verdicts": {
            "static_writer": False,
            "slot_reference_count_a7s": 2,
            "references_are_s342_consumers": True,
            "producer": "servicio invocado por los thunks (vtable +0x2c8/+0x2cc)",
            "producer_identity": "NO_VERIFICADO",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Un array en `.bss` puede llenarse en runtime sin dejar rastro estatico: "
             "el negativo es sobre escritores con literal/slot, no sobre el hardware."),
            ("Los thunks 0x4355f790/0x4355f7ac son envoltorios: el cuerpo real esta en "
             "la vtable de runtime, que no es estatica."),
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("A7S slot refs:", data["a7s"]["slot_refs"], "PIC:", data["a7s"]["pic_bases_to_array"])
    print("A6000 slot refs:", data["a6000"]["slot_refs"])


def _find_all(b: bytes, pat: bytes) -> list[int]:
    out, i = [], b.find(pat)
    while i >= 0:
        out.append(BASE + i)
        i = b.find(pat, i + 1)
    return out


if __name__ == "__main__":
    main()
