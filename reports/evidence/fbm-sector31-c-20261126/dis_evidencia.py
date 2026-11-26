#!/usr/bin/env python3
"""Desensamblado (capstone) de las rutinas en las que se apoya el parche C, para la evidencia.

    python3 dis_evidencia.py > dis-funciones-c.txt

Rutinas y por qué:
  0x2B1DEC  EntryWriteBaseDataFunction(userID r0, fn r1, arg r2, mediaID r3) — el que la consola
            expone como `EWBDFD` (handler 0x2B5198, que pasa r1 = literal 0x2B5185 y r2 = 3.er arg).
  0x2B3000  GetSectorHandleFromOperatioModeAndMediaID: la GUARDA `cbz r2` de 0x2B301A salta las filas
            de 0x9D23FC con fn == 0; sin fn no hay handle y WriteBaseData devuelve 0x10800010.
  0x2B2F48  0x2B2B18 (userID→fileType) + 0x2B2E54/0x2B2DF4: NO llaman a fn; sólo resuelven el índice.
  0x2B3F7C  SÍ llama a fn: `ldr r3,[r4,#0x10]; cbz; ldr r0,[r4,#0x14]; blx r3` (0x2B3FC2..0x2B3FC8)
            y trata r0 != 0 como error (0x2B3FD4).  De aquí sale el stub propio del parche C.
  0x2B43F0  BackupMgr::InitBackupData(OM, mediaID): mutex → InvalidateSync → WriteBaseData →
            ValidateSync → Sync (lo que hace persistente el sector).
  0x2B4030  WriteBaseData: 0x2B3000 → CreateSector32 (0x2B40C8) → alta en 0xA3699C (0x2B40DA..) →
            0x2B3F7C → ChangeSectorToValid / ChangeSectorRelocateComp → TermSectorData 0x2B4164.
  0x2A8750  DvdFlashBackupLib::CreateSector: los rechazos que se citan en el informe de riesgo
            (0x9E598C y el error 0x4F).
"""
from __future__ import annotations

import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

LIB = "analysis/camera-extract/usr/lib/libmpr.so"

TROZOS = [
    ("EntryWriteBaseDataFunction 0x2B1DEC  (userID, fn, arg, mediaID)", 0x2B1DEC, 0x4A),
    ("EWBDFD handler 0x2B5198", 0x2B5198, 0x3E),
    ("dummy de fabrica 0x2B5184 (el que usa EWBDFD)", 0x2B5184, 0x12),
    ("GetSectorHandleFromOperatioModeAndMediaID 0x2B3000 (guarda fn!=0 en 0x2B301A)", 0x2B3000, 0x70),
    ("GetSectorManagerInfoIdx 0x2B2F48 (NO llama a fn)", 0x2B2F48, 0x50),
    ("0x2B2B18 (userID+mediaID -> fileType; NO llama a fn)", 0x2B2B18, 0x50),
    ("0x2B3F7C (SI llama a fn: blx r3 en 0x2B3FC8, r0 = arg)", 0x2B3F7C, 0x60),
    ("BackupMgr::InitBackupData 0x2B43F0 (OM, mediaID)", 0x2B43F0, 0xC0),
    ("BackupMgr::WriteBaseData 0x2B4030", 0x2B4030, 0xB0),
    ("WriteBaseData: cola TermSectorData 0x2B4164", 0x2B4150, 0x18),
    ("DvdFlashBackupLib::CreateSector 0x2A8750 (rechazos)", 0x2A8750, 0x90),
]


def main() -> int:
    dato = open(sys.argv[1] if len(sys.argv) > 1 else LIB, "rb").read()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    print("binario: %s (%d B)" % (sys.argv[1] if len(sys.argv) > 1 else LIB, len(dato)))
    for titulo, va, n in TROZOS:
        print("\n==== %s" % titulo)
        for i in md.disasm(dato[va:va + n], va):
            print("  %08x: %-10s %-8s %s" % (i.address, i.bytes.hex(), i.mnemonic, i.op_str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
