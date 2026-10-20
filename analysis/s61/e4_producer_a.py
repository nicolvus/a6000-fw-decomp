"""S61-E4: fragmento real del productor A (0x437ab502..0x437ab540) con G = 0x43e964a4 sintético.
Pregunta: ¿A se ejecuta solo si bit6 de G[0xd]==0 y publica 6 copias de (G[0x168],G[0x16a])?"""
import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s58")); sys.path.insert(0, str(ROOT / "analysis/s55"))
from tdis import data
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R4, UC_ARM_REG_SP
from wtrace import W

SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
G = 0x43E964A4
OBJ = 0x45400000
GOT = 0x4401EEE4


def run(g0d, g168, g16a):
    assert hashlib.sha256(data("A6000")).hexdigest() == SHA
    w = W(ambito=[(0x43AEB0CC, 0x43AEB0D4), (0x43AE8504, 0x43AE8510), (0x437AB502, 0x437AB540)],
          stubfn={0x437876DC: lambda m: OBJ})
    w.u.mem_write(OBJ, bytes(0xF20))
    w.u.mem_write(G, bytes(0x200))
    w.u.mem_write(G + 0xD, bytes([g0d]))
    w.w16(G + 0x168, g168); w.w16(G + 0x16A, g16a)
    w.u.reg_write(UC_ARM_REG_R4, GOT)
    w.u.reg_write(UC_ARM_REG_SP, 0x44500000 - 0x200)
    w.u.reg_write(UC_ARM_REG_LR, 0x44F00001)
    w.u.emu_start(0x437AB502 | 1, 0x437AB540, count=2000)
    block = w.rd(OBJ + 0xE20, 24)
    return [struct.unpack_from("<HH", block, i * 4) for i in range(6)] if any(block) else None


if __name__ == "__main__":
    for g0d in (0x00, 0x40, 0xBF, 0xFF):
        print(hex(g0d), run(g0d, 0x1234, 0x5678))
