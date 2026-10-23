"""Lectura acotada ELF32/ARM para reproducir la auditoría RecordImage/RecordStill."""

import struct
from itertools import pairwise
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs, CsInsn

ROOT = Path(__file__).resolve().parents[2]
LIBRARIES = {
    model: ROOT / "firmware/extracted" / version
    / "firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
    for model, version in {"A6000": "fw321", "A7S": "a7s-fw320/payload"}.items()
}


class Elf32:
    """Solo ELF32 ARM little endian; las direcciones públicas son VA del ELF."""

    def __init__(self, path: Path):
        self.data = path.read_bytes()
        if self.data[:6] != b"\x7fELF\x01\x01" or self.data[18:20] != b"\x28\x00":
            raise ValueError("Se requiere ELF32 ARM little endian")
        ph, sh = struct.unpack_from("<II", self.data, 28)
        pe, pn, se, sn, si = struct.unpack_from("<5H", self.data, 42)
        self.loads = [
            entry for i in range(pn)
            if (entry := struct.unpack_from("<8I", self.data, ph + i * pe))[0] == 1
        ]
        sections = [struct.unpack_from("<10I", self.data, sh + i * se) for i in range(sn)]
        strings = sections[si]
        names = self.data[strings[4]:strings[4] + strings[5]]
        self.sections = {
            names[s[0]:].split(b"\0", 1)[0].decode(): s for s in sections
        }
        self.decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        self.decoder.detail = True

    def offset(self, va: int, size: int = 1) -> int:
        for segment in self.loads:
            if segment[2] <= va and va + size <= segment[2] + segment[4]:
                return segment[1] + va - segment[2]
        raise ValueError(f"VA no respaldada por archivo: {va:#x}+{size:#x}")

    def read(self, va: int, size: int) -> bytes:
        offset = self.offset(va, size)
        return self.data[offset:offset + size]

    def u32(self, va: int) -> int:
        return struct.unpack("<I", self.read(va, 4))[0]

    def instruction(self, va: int) -> CsInsn:
        return next(self.decoder.disasm(self.read(va, 4), va, count=1))

    def pc_string(self, load: int, add: int) -> tuple[int, str]:
        """Resuelve LDR literal + ADD reg,PC; no confunde pool con instrucciones."""
        ins = self.instruction(load)
        reg = ins.reg_name(ins.operands[0].reg)
        assert ins.mnemonic in {"ldr", "ldr.w"} and "[pc," in ins.op_str
        addition = self.instruction(add)
        assert addition.mnemonic == "add" and addition.op_str == f"{reg}, pc"
        literal = ((load + 4) & ~3) + ins.operands[1].mem.disp
        address = (self.u32(literal) + add + 4) & 0xFFFFFFFF
        offset = self.offset(address)
        end = self.data.index(b"\0", offset)
        return address, self.data[offset:end].decode()

    def unwind_span(self, va: int) -> tuple[int, int]:
        """Intervalo entre entradas PREL31; no garantiza un único cuerpo de código."""
        section = self.sections[".ARM.exidx"]
        entries = []
        for delta in range(0, section[5], 8):
            place = section[3] + delta
            relative = self.u32(place) & 0x7FFFFFFF
            if relative & 0x40000000:
                relative -= 0x80000000
            entries.append((place + relative) & ~1)
        for start, end in pairwise(entries):
            if start <= va < end:
                return start, end
        raise ValueError(f"Sin intervalo unwind: {va:#x}")

    def word_hits(self, value: int) -> list[int]:
        """Palabras exactas, incluso desalineadas, solo en PT_LOAD con bytes."""
        pattern = struct.pack("<I", value)
        hits = set()
        for segment in self.loads:
            start, end = segment[1], segment[1] + segment[4]
            position = self.data.find(pattern, start, end)
            while position >= 0:
                hits.add(segment[2] + position - start)
                position = self.data.find(pattern, position + 1, end)
        return sorted(hits)
