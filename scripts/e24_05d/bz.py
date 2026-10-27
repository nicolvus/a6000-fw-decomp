"""Utilidades de solo lectura sobre av-cam.bin (BIONZ, Thumb-2, base 0x43541000) con Capstone."""
from __future__ import annotations

import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000


class Bz:
    def __init__(self, path: Path = AVCAM):
        self.d = path.read_bytes()
        self.cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        self.cs.detail = False
        self.cs.skipdata = True

    def off(self, a: int) -> int:
        return a - BASE

    def u32(self, a: int) -> int:
        return struct.unpack_from("<I", self.d, a - BASE)[0]

    def u16(self, a: int) -> int:
        return struct.unpack_from("<H", self.d, a - BASE)[0]

    def u8(self, a: int) -> int:
        return self.d[a - BASE]

    def cstr(self, a: int) -> str:
        o = a - BASE
        e = self.d.index(b"\0", o)
        return self.d[o:e].decode("latin1")

    def dis(self, a: int, n: int = 0x80):
        return list(self.cs.disasm(self.d[a - BASE : a - BASE + n], a))

    def text(self, a: int, n: int = 0x80) -> str:
        """Desensamblado con los literales `ldr rX,[pc,#k]` resueltos."""
        out = []
        for i in self.dis(a, n):
            s = f"{i.address:#x}: {i.mnemonic} {i.op_str}"
            if i.mnemonic.startswith("ldr") and "[pc" in i.op_str:
                imm = int(i.op_str.split("#")[-1].rstrip("]"), 0) if "#" in i.op_str else 0
                la = ((i.address + 4) & ~3) + imm
                try:
                    s += f"   ; ={self.u32(la):#x}"
                except Exception:
                    pass
            out.append(s)
        return "\n".join(out)

    def lit_refs(self, value: int, lo: int = 0, hi: int | None = None) -> list[int]:
        """Direcciones de palabras alineadas == value y las instrucciones ldr pc-relativas que las cargan."""
        hi = hi or BASE + len(self.d)
        words = {a for a in range(max(lo, BASE), hi - 3, 4) if self.u32(a) == value}
        refs = []
        for a in range(max(lo, BASE), hi - 4, 2):
            h = self.u16(a)
            if h & 0xF800 == 0x4800:  # ldr rX,[pc,#imm8*4] (T1)
                la = ((a + 4) & ~3) + (h & 0xFF) * 4
                if la in words:
                    refs.append(a)
            elif h == 0xF8DF or (h & 0xFFF0) == 0xF8D0 and False:
                pass
        return refs

    def bl_callers(self, target: int, lo: int = 0, hi: int | None = None) -> list[int]:
        hi = hi or BASE + len(self.d)
        out = []
        for a in range(max(lo, BASE), hi - 4, 2):
            h1, h2 = self.u16(a), self.u16(a + 2)
            if h1 & 0xF800 == 0xF000 and h2 & 0xD000 in (0xD000, 0xC000) and h2 & 0xC000 == 0xC000:
                s = (h1 >> 10) & 1
                j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
                i1, i2 = (~(j1 ^ s)) & 1, (~(j2 ^ s)) & 1
                imm = ((s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1))
                if s:
                    imm -= 1 << 25
                t = a + 4 + imm
                if h2 & 0x1000 and t == target:
                    out.append(a)
        return out


def pcrel_index(bz: Bz) -> dict[int, list[int]]:
    """{dirección destino: [direcciones de la instrucción `add rX,pc`]} para el patrón PIC `ldr rX,[pc,#k]; add rX,pc`.

    shortcut: solo T1/T2 con el `add` en las 6 instrucciones siguientes, no sigue valores copiados a otros registros.
    """
    n = len(bz.d) // 2
    hw = struct.unpack_from(f"<{n}H", bz.d)
    idx: dict[int, list[int]] = {}
    for i in range(n - 2):
        h = hw[i]
        a = BASE + 2 * i
        reg = lit = None
        if h & 0xF800 == 0x4800:
            reg, lit = (h >> 8) & 7, ((a + 4) & ~3) + (h & 0xFF) * 4
        elif h == 0xF8DF or h == 0xF85F:
            h2 = hw[i + 1]
            reg, off = (h2 >> 12) & 15, h2 & 0xFFF
            lit = ((a + 4) & ~3) + (off if h == 0xF8DF else -off)
        if reg is None or not (BASE <= lit < BASE + len(bz.d) - 3):
            continue
        for j in range(i + 1, min(i + 8, n)):
            hj = hw[j]
            if hj & 0xFF78 == 0x4478 and ((hj & 7) | ((hj >> 4) & 8)) == reg:
                aj = BASE + 2 * j
                t = (bz.u32(lit) + aj + 4) & 0xFFFFFFFF
                idx.setdefault(t, []).append(aj)
                break
    return idx
