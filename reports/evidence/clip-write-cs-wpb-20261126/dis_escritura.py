#!/usr/bin/env python3
"""Desensamblado (capstone) de todo lo que sostiene la medición del camino de ESCRITURA del clip.

    python3 dis_escritura.py > dis-escritura.txt

Rutinas y por qué:
  0x5C9F48  m2psIfo_Backup.cpp «SECTOR CHANGE»: `movs r0,#4` (0x5C9F7C) + `ldr r1,[r4,#0xC]` +
            `bl 0x2B41B4` (0x5C9F7E) → fija que ChangeSector se llama con (userID=4, mediaID).
  0x5CA134  m2psIfo_Backup.cpp: `bl 0x2B3D24` (0x5CA164) con r0=4, r1=[this+0xC], r2=dataID,
            r3=longitud par, [sp]=&pack, [sp+4]=0, [sp+8]=0; después 0x2B3C64 y 0x2B3B94.
  0x2B3D24  WritePackBegin: firma real y guardas (0x10100001 en 0x2B3D90 si el handle es 0).
  0x2B3EF8  WriteSectorManagerInfo, el otro llamante (userID 0x80): enseña el reparto de los 3
            argumentos de pila ([sp]=&pack, [sp+4]=arg6 sin leer, [sp+8]=operationMode).
  0x2B41B4  ChangeSector(userID,mediaID): 0x2B3094 → si el handle es 0, 0x10100006 en 0x2B41F4;
            si hay handle, 0x2B2BCC + 0x2B1DCC y luego 0x2B4030 WriteBaseData(OM,mediaID).
  0x2B3094  userID/mediaID → índice (0x2B2F48) → handle = [0xA3699C + 0x14*idx + 4].
  0x2B2F48  GetSectorManagerInfoIdxFromUserID: recorre 0xA3699C comparando el u32 de la entrada.
  0x2B2B18  GetFileType: userID+mediaID → fileType por la tabla estática 0x9D23FC.
  0x2B2BCC  GetOperationModeFromUserFuncTable: userID → operationMode (misma tabla).
  0x2B1DCC  (OM-7 <= 1) → 1: el atajo OM_INI/OM_DCF de ChangeSector.
  0x2B3000  GetSectorHandleFromOperatioModeAndMediaID: la GUARDA `cbz r2` de 0x2B301A salta las
            filas de 0x9D23FC con fn == 0 y termina en 0x10800010 (0x2B2FF8).
  0x2B4030  BackupMgr::WriteBaseData: 0x2B3000 → CreateSector32 → alta en 0xA3699C → 0x2B3F7C.
  0x2B3B94  WritePackEnd: si 0x2B3B94 acaba bien llama a 0x2B25D0 (escritura real).
  0x2B25D0  la escritura: GetSectorInfo (0x2B2480) → compara «seek» → ChangeSeekPoint (PLT
            0x11E8D0 = GOT 0x9C3ABC) → WriteSector (PLT 0x11E810 = GOT 0x9C3A7C) → 0x2B242C.
  0x2B2480  GetSectorInfo del backup: handle 0 → 0x10100009; si no, FlashLib::GetSectorInfo.
  0x2B242C  traduce el código FBS: 0 → 0, 0x57 → 0x10100009, 0x0A → 0x10100003, resto → 0x10800020.
Además: tabla de cadenas de error FBS (0x7E9488, índice = código-1) para nombrar el 0x11, y la tabla
estática 0x9D23FC tal cual está en el fichero (fn = 0 en las 38 filas).
"""
from __future__ import annotations

import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../.."))
LIB = os.path.join(REPO, "analysis/camera-extract/usr/lib/libmpr.so")
# la sección RW va en el fichero 0x8000 por debajo de su VA (PT_LOAD: Off 0x9BB1C8 / VA 0x9C31C8)
DELTA_RW = 0x8000

TROZOS = [
    ("m2psIfo_Backup: SECTOR CHANGE 0x5C9F48 (ChangeSector(4,[this+0xC]) en 0x5C9F7E)", 0x5C9F48, 0x50),
    ("m2psIfo_Backup: escritura 0x5CA134 (WritePackBegin en 0x5CA164, Add 0x2B3C64, End 0x2B3B94)", 0x5CA134, 0x80),
    ("ChangeSector 0x2B41B4 (userID, mediaID): 0x10100006 en 0x2B41F4", 0x2B41B4, 0xA0),
    ("WritePackBegin 0x2B3D24 (firma real; 0x10100001 en 0x2B3D90)", 0x2B3D24, 0x100),
    ("WriteSectorManagerInfo 0x2B3EF8 (otro llamante: userID 0x80, [sp]=&pack, [sp+8]=operationMode)", 0x2B3EF8, 0x60),
    ("0x2B3094 userID/mediaID -> handle ([0xA3699C+0x14*idx+4], 0 si no hay fila)", 0x2B3094, 0x30),
    ("0x2B2F48 GetSectorManagerInfoIdxFromUserID (recorre 0xA3699C)", 0x2B2F48, 0x50),
    ("0x2B2B18 GetFileType (userID+mediaID -> fileType por 0x9D23FC)", 0x2B2B18, 0x40),
    ("0x2B2BCC GetOperationModeFromUserFuncTable (userID -> OM)", 0x2B2BCC, 0x40),
    ("0x2B1DCC (OM-7 <= 1)", 0x2B1DCC, 0x10),
    ("0x2B3000 GetSectorHandleFromOperatioModeAndMediaID (guarda fn != 0 en 0x2B301A -> 0x10800010)", 0x2B3000, 0x80),
    ("BackupMgr::WriteBaseData 0x2B4030", 0x2B4030, 0xB0),
    ("WritePackEnd 0x2B3B94 (llama a 0x2B25D0 en 0x2B3C18)", 0x2B3B94, 0xB0),
    ("0x2B25D0 escritura real: GetSectorInfo -> ChangeSeekPoint -> WriteSector -> 0x2B242C", 0x2B25D0, 0xA0),
    ("0x2B2480 GetSectorInfo (handle 0 -> 0x10100009; lit 0x10800020 en 0x2B2478)", 0x2B2480, 0x50),
    ("0x2B242C traduce el código FBS (0x11 -> 0x10800020)", 0x2B242C, 0x30),
]


def main() -> int:
    ruta = sys.argv[1] if len(sys.argv) > 1 else LIB
    dato = open(ruta, "rb").read()
    u32 = lambda a: struct.unpack_from("<I", dato, a)[0]   # noqa: E731
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    print("binario: %s (%d B)" % (ruta, len(dato)))
    print("literales pc-relativos resueltos y, si son punteros a rodata, la cadena.\n")
    for titulo, va, n in TROZOS:
        print("==== %s" % titulo)
        for i in md.disasm(dato[va:va + n], va):
            extra = ""
            if i.mnemonic in ("ldr", "add") and "[pc," in i.op_str:
                d = i.op_str.split("#", 1)[1].split("]")[0]
                try:
                    v = u32(((i.address + 4) & ~3) + int(d, 0))
                except ValueError:
                    v = None
                if v is not None:
                    txt = ""
                    if v < len(dato):
                        e = dato.find(b"\0", v)
                        s = dato[v:e]
                        if s and all(32 <= c < 127 for c in s):
                            txt = ' "%s"' % s.decode("latin1")[:48]
                    extra = "   ; = %#x%s" % (v, txt)
            print("  %08x: %-12s %-8s %-40s%s" % (i.address, i.bytes.hex(), i.mnemonic, i.op_str, extra))

    print("\n==== tabla estática 0x9D23FC (38 filas de 0x18: userID, mediaID, fileType, OM, fn, arg)")
    off = 0x9D23FC - DELTA_RW
    for i in range(38):
        u, m, ft, om, fn, arg = struct.unpack_from("<IIIIII", dato, off + i * 0x18)
        print("  [%02d] u%02x/m%d/ft%03x/om%x/fn%x/arg%x" % (i, u, m, ft, om, fn, arg))

    print("\n==== cadenas de error FBS (tabla en 0x7E9488; GetErrorString(c) = tabla[c-1] para 1..0x55)")
    for c in list(range(1, 0x13)) + [0x49, 0x57]:
        p = u32(0x7E9488 + (c - 1) * 4)
        e = dato.find(b"\0", p)
        print("  %#04x -> %s" % (c, dato[p:e].decode("latin1") if p < len(dato) else "?"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
