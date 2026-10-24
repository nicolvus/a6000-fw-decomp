"""S384: candidatos Thumb por bytes; la alineación no demuestra flujo ejecutable.

Uso: .venv/bin/python analysis/s380_libobj_map/queue_40193_flow.py
Emite JSON; solo lee ELF originales. Las VA se convierten mediante PT_LOAD.
"""

import json
import struct
from collections.abc import Iterator

from recordimage_audit import LIBRARIES, Elf32


def literal_loads(data: bytes, base: int) -> Iterator[tuple[int, int, int]]:
    """LDR literal T1/T2 a cada halfword; incluye PC alineado y signo U."""
    for offset in range(0, len(data) - 1, 2):
        first = struct.unpack_from("<H", data, offset)[0]
        address = base + offset
        pc = (address + 4) & ~3
        if first & 0xF800 == 0x4800:
            yield address, (first >> 8) & 7, pc + (first & 255) * 4
        elif first in (0xF8DF, 0xF85F) and offset + 4 <= len(data):
            second = struct.unpack_from("<H", data, offset + 2)[0]
            sign = 1 if first == 0xF8DF else -1
            yield address, second >> 12, pc + sign * (second & 4095)


def mov_halves(data: bytes, base: int) -> Iterator[tuple[int, str, int, int]]:
    """MOVW/MOVT Thumb: imm4:i:imm3:imm8, Rd separado, bit15 segundo=0."""
    for offset in range(0, len(data) - 3, 2):
        first, second = struct.unpack_from("<HH", data, offset)
        opcode = first & 0xFBF0
        if opcode not in (0xF240, 0xF2C0) or second & 0x8000:
            continue
        immediate = ((first & 15) << 12 | ((first >> 10) & 1) << 11
                     | ((second >> 12) & 7) << 8 | second & 255)
        yield base + offset, "movw" if opcode == 0xF240 else "movt", (second >> 8) & 15, immediate


def survey(elf: Elf32) -> dict[str, object]:
    section = elf.sections[".text"]
    text = elf.read(section[3], section[5])
    hits = set(elf.word_hits(0x40193))
    references = []
    for address, reg, pool in literal_loads(text, section[3]):
        if pool in hits:
            ins = elf.instruction(address)
            references.append({
                "load": hex(address), "bytes": ins.bytes.hex(), "register": reg,
                "pool": hex(pool), "value": hex(elf.u32(pool)),
                "unwind_interval": [hex(v) for v in elf.unwind_span(address)],
            })
    return {
        "word_hits": [hex(v) for v in sorted(hits)],
        "literal_load_candidates": references,
        "movw_0193_candidates": [hex(a) for a, op, _, imm in mov_halves(text, section[3])
                                 if op == "movw" and imm == 0x193],
        "limits": "Thumb halfword candidates; no CFG, ARM coverage or interprocedural proof. "
                  "PT_LOAD file-backed words include sections other than .text.",
    }


if __name__ == "__main__":
    print(json.dumps({model: survey(Elf32(path)) for model, path in LIBRARIES.items()}, indent=2))
