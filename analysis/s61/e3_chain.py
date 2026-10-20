"""S61-E3: cadena obj+0x2be.. -> P0 (0x43861ed0) -> obj+0x314.. -> productor B (0x43aecbec) -> bloque obj+0xe20.
Código real en Unicorn; entradas SINTÉTICAS salvo la tabla del sexto par, que usa la entrada BK4 0x300ab real (valores por defecto del paquete).
Clasificación de resultado: PERMITIDO (supera las ramas de las funciones), no ALCANZABLE."""
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s58")); sys.path.insert(0, str(ROOT / "analysis/s55"))
from bk4 import BK4
from tdis import data
from wtrace import W

SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
BK = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0110_backup/SYSMUSASHI-DSLR/DM_UUD3/CX77500_UC2.bin"
OBJ = 0x45400000          # objeto de 0xf20 B (singleton devuelto por 0x437876dc)
STAGE = 0x45500000
TAB = 0x45600000
TVAR = 0x43EA5070         # variable global: puntero a la tabla del sexto par
IN = {0x2BE: 0x0410, 0x2C0: 0x0500, 0x2C2: 0x0420, 0x2C4: 0x0530, 0x2C6: 0x0440, 0x2C8: 0x0510,
      0x2CA: 0x0460, 0x2CC: 0x0900, 0x2CE: 0x0470, 0x2D0: 0x0000}
FIELDS = (0x314, 0x316, 0x318, 0x31A, 0x31C, 0x31E, 0x320, 0x322, 0x328, 0x32A)


def bk4_entry():
    b = BK4(BK)
    size, _ = b.entry(0x300AB)
    p = b.ptr(0x300AB)
    return b.d[p:p + size]


def scope():
    return [(0x43861ED0, 0x438621BC), (0x4355FD68, 0x43560000), (0x43AECBEC, 0x43AECC5E),
            (0x43AE8504, 0x43AE8510), (0x437A5A6C, 0x437A5B1E)]


def run(inputs=IN, stage3a=1, t_entry=None):
    assert hashlib.sha256(data("A6000")).hexdigest() == SHA
    w = W(ambito=scope(), stubfn={0x437876DC: lambda m: OBJ})
    w.u.mem_write(OBJ, bytes(0xF20))
    for off, v in inputs.items():
        w.w16(OBJ + off, v)
    w.call(0x43861ED0, OBJ)
    mid = {hex(o): w.r16(OBJ + o) for o in FIELDS}
    w.u.mem_write(OBJ + 0xE20, bytes(24))
    # obj8 = copia de obj+0x2cc (así lo construye 0x43aece72 con memcpy de 0x244 B)
    obj8 = OBJ + 0x2CC
    stage = bytearray(0x200); stage[0x3A] = stage3a; stage[0x17] = 0; stage[1] = 0
    w.u.mem_write(STAGE, bytes(stage))
    w.u.mem_write(STAGE + 0x400, bytes(0x400))       # [p1+4] -> bloque de tablas del sexto par
    w.w32(STAGE + 0x404, STAGE + 0x500)
    w.u.mem_write(OBJ + 0x2CC + 0x2, bytes([0x00, 0x0D]))        # obj8+2 = 0 ; obj8+3 = 0x0d
    p = 0x45700000
    w.u.mem_write(p, struct.pack("<IIII", STAGE, STAGE + 0x400, obj8, OBJ + 0x1000))
    entry = t_entry if t_entry is not None else bk4_entry()
    w.u.mem_write(TAB, entry + bytes(0x200))
    w.w32(TVAR, TAB)
    w.call(0x43AECBEC, p)
    block = w.rd(OBJ + 0xE20, 24)
    pairs = [struct.unpack_from("<HH", block, i * 4) for i in range(6)]
    return {"p0_output": mid, "pairs": pairs, "block_hex": block.hex(), "stubbed": {hex(k): v for k, v in w.stubbed.items()},
            "classification": "PERMITIDO (entradas sintéticas; sexto par con tabla BK4 real)"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
