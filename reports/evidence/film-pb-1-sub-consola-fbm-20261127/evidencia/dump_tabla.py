#!/usr/bin/env python3
"""Vuelca la tabla de comandos de consola del módulo FBM de libmpr.so 3.21.

    python3 dump_tabla.py [libmpr.so]

Tabla en `.data` 0x7E7FAC..0x7E8108: 29 registros de 12 B {char *name; int (*fn)(long,char**); char *desc}
+ terminador {0,0,0}. El handler del módulo es 0x2B50D8 y el despachador genérico 0x6822F8.
Escribe el mismo texto que evidencia/tabla-comandos-fbm.txt.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, "/tmp")
from elfhelper import Elf  # noqa: E402

LIB = sys.argv[1] if len(sys.argv) > 1 else (
    Path(__file__).resolve().parents[4] / "analysis/camera-extract/usr/lib/libmpr.so")
BASE, N = 0x7E7FAC, 29

SYN = {
    "Destroy": "Destroy <1|2|3|4> … (tipo 1 void; 2 [mediaID(HEX)]; 3 [mediaID(HEX)] [operationMode(HEX)]; 4 [userID(HEX)] [mediaID(HEX)])",
    "Close": "Close [index]", "Delete": "Delete [index]", "DeleteAll": "(sin argumentos)",
    "ReadAllPD": "ReadAllPD [Sec name]", "ReadPD": "ReadPD [UserID(Hex)] [MediaID(Hex)]",
    "WritePack": "WritePack [USER_ID] [MEDIA_ID] [DATA_ID] [Data length]",
    "InitB": "InitB [Operation Mode] [MediaID]   (los dos DECIMALES)",
    "ChgSec": "ChgSec [userID(Hex)] [mediaID(Hex)]",
    "SetOM": "SetOM <OM> <x>   (imprime por error la ayuda de InitB)",
    "SetSMI": "SetSMI [index] [SectorName(Hex)] [handle] [status] [OM]",
    "View": "(sin argumentos)", "ASV": "(sin argumentos)", "GASI": "(sin argumentos)",
    "WDS": "(sin argumentos)", "Flush": "(sin argumentos)", "SSS": "SSS [SectorNo] [Status]",
    "GSS": "GSS  |  GSS [UserID(Hex)] [MediaID(Hex)]", "ARB": "(sin argumentos)",
    "Quit": "(sin argumentos)", "GetAlignSize": "GetAlignSize [Original Data Size]",
    "INRFB": "(sin argumentos)", "CRFB": "(sin argumentos)", "DFT": "(sin argumentos)",
    "DRWBI": "(sin argumentos)", "LTC": "fbm ltc [module number] [parameter1]....",
    "EWBDFD": "EWBDFD [UserID(Hex)][MediaID(Hex)][FunctionDataAdrs(Hex)]",
    "CWBDF": "CWBDF [UserID(Hex)][MediaID(Hex)]", "WBI": "(sin argumentos)",
}


def main() -> None:
    e = Elf(str(LIB))

    def s(va: int, n: int = 120) -> str:
        return e.read(va, n).split(b"\0")[0].decode("latin1")

    print('TABLA DE COMANDOS DE CONSOLA DEL MODULO "FBM" (libmpr.so 3.21, VA del ELF)')
    print(f"tabla = {BASE:#x} .. {BASE + N * 12:#x}, {N} registros de 12 B "
          "{char*name; int(*fn)(long,char**); char*desc}, terminador {0,0,0}")
    print("handler del modulo = 0x2B50D8 (literal 0x2B4E60 = 0x2B50D9); alta en el monitor: "
          '0x2B4D7E -> 0x684940("FBM")')
    print("despacho: 0x2B50D8 -> 0x6847EC -> 0x6822F8(tabla, argc-1, argv+1) -> 0x682230 strcmp + blx [+4]")
    print()
    print("%-3s %-13s %-10s %s" % ("#", "nombre", "handler", "sintaxis / descripcion"))
    for i in range(N):
        off = BASE + i * 12
        name = s(struct.unpack("<I", e.read(off, 4))[0])
        fn = struct.unpack("<I", e.read(off + 4, 4))[0] & ~1
        desc = s(struct.unpack("<I", e.read(off + 8, 4))[0])
        print("%02d  %-13s 0x%08x %s   [%s]" % (i, name, fn, SYN.get(name, desc), desc))
    print()
    print("No hay CreateSector, ni Format, ni Repair. Crea `InitB` (0x2B5B34 -> 0x2B43F0 -> 0x2B4030 "
          "-> FlashLib::CreateSector32 + alta en 0xA3699C en 0x2B40DA).")


if __name__ == "__main__":
    main()
