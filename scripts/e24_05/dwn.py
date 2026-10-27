"""Utilidades estáticas de solo lectura para `darwin_core.bin` (A6000 3.21), base ROM 0x4200.

E24-05. No ejecuta nada ni toca la cámara. Uso: `python -m scripts.e24_05.dwn dis 0x4bca 0x120`.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from functools import cached_property
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
SHA256 = "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
BASE = 0x4200


class Core:
    def __init__(self, path: Path = DARWIN):
        self.data = path.read_bytes()
        self.end = BASE + len(self.data)
        self.md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
        self.md.detail = True

    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()

    def u32(self, addr: int) -> int:
        return struct.unpack_from("<I", self.data, addr - BASE)[0]

    def u16(self, addr: int) -> int:
        return struct.unpack_from("<H", self.data, addr - BASE)[0]

    def u8(self, addr: int) -> int:
        return self.data[addr - BASE]

    def dis(self, addr: int, size: int):
        """Instrucciones de [addr, addr+size); las medias palabras indecodificables se omiten (1 insn = .hword)."""
        out, a, end = [], addr, addr + size
        while a < end:
            got = next(self.md.disasm(self.data[a - BASE:a - BASE + 4], a, 1), None)
            if got is None:
                a += 2
                continue
            out.append(got)
            a += got.size
        return out

    @cached_property
    def all_insns(self) -> list:
        """Barrido lineal de todo el core (los pools literales producen basura aislada)."""
        out = []
        a = BASE
        while a < self.end - 2:
            got = list(self.md.disasm(self.data[a - BASE:a - BASE + 4], a, 1))
            if got:
                out.append(got[0])
                a += got[0].size
            else:
                a += 2
        return out

    def lit_of(self, i) -> int | None:
        """Valor cargado por `ldr rX,[pc,#imm]` (o None)."""
        if i.mnemonic.startswith("ldr") and "[pc" in i.op_str:
            op = i.operands[1]
            tgt = ((i.address + 4) & ~3) + op.mem.disp
            if BASE <= tgt < self.end - 3:
                return self.u32(tgt)
        return None

    def render(self, addr: int, size: int) -> str:
        lines = []
        for i in self.dis(addr, size):
            lit = self.lit_of(i)
            extra = f"   ; =0x{lit:x}" if lit is not None else ""
            lines.append(f"{i.address:#x}: {i.bytes.hex():<9} {i.mnemonic} {i.op_str}{extra}")
        return "\n".join(lines)

    def bl_callers(self, target: int) -> list[int]:
        res = []
        for i in self.all_insns:
            if i.mnemonic in ("bl", "b.w", "blx") and i.operands and i.operands[0].type == capstone.arm.ARM_OP_IMM \
                    and i.operands[0].imm == target:
                res.append(i.address)
        return res

    def word_refs(self, value: int) -> list[int]:
        """Direcciones alineadas a 4 donde aparece `value` como palabra (pools literales y tablas)."""
        pat = struct.pack("<I", value)
        out, p = [], self.data.find(pat)
        while p >= 0:
            if p % 4 == 0:
                out.append(BASE + p)
            p = self.data.find(pat, p + 1)
        return out

    def ldr_users(self, value: int) -> list[int]:
        """Instrucciones `ldr pc-relativo` cuyo literal vale `value`."""
        return [i.address for i in self.all_insns if self.lit_of(i) == value]


def main(argv: list[str]) -> None:
    c = Core()
    cmd = argv[0]
    if cmd == "dis":
        print(c.render(int(argv[1], 0), int(argv[2], 0)))
    elif cmd == "callers":
        print(" ".join(hex(a) for a in c.bl_callers(int(argv[1], 0))))
    elif cmd == "words":
        print(" ".join(hex(a) for a in c.word_refs(int(argv[1], 0))))
    elif cmd == "lit":
        print(" ".join(hex(a) for a in c.ldr_users(int(argv[1], 0))))
    elif cmd == "u32":
        n = int(argv[2], 0) if len(argv) > 2 else 1
        for k in range(n):
            print(f"{int(argv[1], 0) + 4 * k:#x}: {c.u32(int(argv[1], 0) + 4 * k):#x}")


if __name__ == "__main__":
    main(sys.argv[1:])
