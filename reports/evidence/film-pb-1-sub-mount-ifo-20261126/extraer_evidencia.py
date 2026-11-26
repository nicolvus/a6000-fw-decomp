#!/usr/bin/env python3
"""Reproduce la evidencia de reports/film-pb-1-sub-mount-ifo-20261126.md.

Uso:
    .venv/bin/python3 extraer_evidencia.py            # regenera los .txt de este directorio
    .venv/bin/python3 extraer_evidencia.py --dump     # vuelca los literales del anillo (RAM)

Solo lectura: no ejecuta firmware ni toca la camara. Requiere capstone.
"""
from __future__ import annotations

import hashlib
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

RAIZ = Path(__file__).resolve().parents[3]
LIB = (
    RAIZ
    / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
    / "nflasha15_unpacked_unpacked/lib/libmpr.so"
)
DUMP = RAIZ / "analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin"
ANILLO_INI, ANILLO_FIN = 0x2DF9300, 0x2DFC400  # VA 0x82DF9300-0x82DFC400


class Elf:
    def __init__(self, path: Path) -> None:
        self.d = path.read_bytes()
        d = self.d
        self.segs: list[tuple[int, int, int]] = []
        e_phoff = struct.unpack_from("<I", d, 28)[0]
        e_phentsize = struct.unpack_from("<H", d, 42)[0]
        e_phnum = struct.unpack_from("<H", d, 44)[0]
        for i in range(e_phnum):
            o = e_phoff + i * e_phentsize
            t, off, va, _pa, fsz, _msz, _fl, _al = struct.unpack_from("<8I", d, o)
            if t == 1:
                self.segs.append((off, va, fsz))
        e_shoff = struct.unpack_from("<I", d, 32)[0]
        e_shentsize = struct.unpack_from("<H", d, 46)[0]
        e_shnum = struct.unpack_from("<H", d, 48)[0]
        e_shstrndx = struct.unpack_from("<H", d, 50)[0]
        secs = [
            struct.unpack_from("<10I", d, e_shoff + i * e_shentsize) for i in range(e_shnum)
        ]
        shstr = secs[e_shstrndx]
        self.sec: dict[str, tuple[int, int, int]] = {}
        for s in secs:
            o = shstr[4] + s[0]
            self.sec[d[o : d.index(b"\0", o)].decode()] = (s[3], s[4], s[5])

    def read(self, va: int, n: int) -> bytes:
        for po, base, fsz in self.segs:
            if base <= va < base + fsz:
                o = po + va - base
                return self.d[o : min(o + n, po + fsz)]
        return b""

    def va2off(self, va: int) -> int | None:
        for po, base, fsz in self.segs:
            if base <= va < base + fsz:
                return po + va - base
        return None

    def cstr(self, va: int, maxlen: int = 80) -> str:
        return self.read(va, maxlen).split(b"\0")[0].decode("latin1")


def _anotar(e: Elf, ins) -> str:
    if ins.mnemonic.startswith("ldr") and "[pc" in ins.op_str:
        m = re.search(r"#(0x[0-9a-f]+)", ins.op_str)
        if m:
            tgt = ((ins.address + 4) & ~3) + int(m.group(1), 16)
            v = e.read(tgt, 4)
            if len(v) == 4:
                p = struct.unpack("<I", v)[0]
                s = e.cstr(p, 64)
                nota = f' "{s}"' if s and all(32 <= c < 127 for c in s.encode("latin1")) and len(s) > 2 else ""
                return f"  ; [{tgt:08x}]={p:08x}{nota}"
    return ""


def listado(e: Elf, va: int, size: int) -> str:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    salida, cur, fin = [], va, va + size
    while cur < fin:
        ins = list(md.disasm(e.read(cur, 4), cur))
        if not ins:
            salida.append(f"{cur:08x}: {e.read(cur, 2).hex():<10} <dato>")
            cur += 2
            continue
        i = ins[0]
        salida.append(
            f"{i.address:08x}: {i.bytes.hex():<10} {i.mnemonic:<9} {i.op_str:<32}{_anotar(e, i)}"
        )
        cur += i.size
    return "\n".join(salida)


RANGOS = [
    ("01-avimmgr-mountcmd.txt", 0x626DB8, 0x1A0, "AviMMgrCmd::MountCmd"),
    ("02-avimmgr-mountcmd-driveletter.txt", 0x627020, 0x1F0, "AviMMgrCmd::MountCmd (variante driveLetter)"),
    ("03-avimmgr-flashmount.txt", 0x62684C, 0x170, "AviMMgrCmd::FlashMount"),
    ("04-avimmgr-getdeviceinfo.txt", 0x625C4C, 0x60, "AviMMgrCmd::GetDeviceInfo"),
    ("05-avimmgr-flashloadmp4.txt", 0x627BEC, 0x110, "AviMMgrCmd::FlashLoadMp4"),
    ("06-mmgr-createandload.txt", 0x67CA6C, 0xB0, "MMgrMp4IfoAcsr::CreateAndLoad"),
    ("07-mmgr-loadsub.txt", 0x67C8CC, 0xE8, "MMgrMp4IfoAcsr::LoadSub"),
    ("08-mmgr-load.txt", 0x67C9C0, 0x90, "MMgrMp4IfoAcsr::Load"),
    ("09-acsr-avchd-checksalvagestatus.txt", 0x671DAC, 0x110, "MMgrAvcHdIfoAcsr::CheckSalvageStatus"),
    ("10-mp4ifo-flashloadformsv.txt", 0x698EC8, 0x60, "mp4Ifo_General::FlashLoadForMsv"),
    ("11-mp4ifo-checksalvagestatus.txt", 0x698F18, 0x90, "mp4Ifo_General::CheckSalvageStatus"),
    ("12-mp4ifo-load.txt", 0x698FB8, 0x50, "mp4Ifo_General::Load"),
    ("13-msv-rcsbackuptbldata-caller.txt", 0x3AFA94, 0xB4, "llamante de RcsBackupTblData (0x35EA1C)"),
    ("14-gate-64c298.txt", 0x64C298, 0x50, "gate de estado AviMMgr (mask, state==mask)"),
    ("16-mapper-avi-1da818.txt", 0x1DA818, 0x80, "nombre de codigo AVI (0x32xxxxxx)"),
    ("17-enum-avi-state.txt", 0x1DA1EC, 0x50, "enum AVI_STATE*"),
    ("18-mp4ifo-traductor-a.txt", 0x6F0D4C, 0x60, "traductor mp4Ifo (cabecera)"),
    ("18-mp4ifo-traductor-b.txt", 0x6F0D8E, 0x60, "traductor mp4Ifo (grupos 0xXXnn0000)"),
    ("18-mp4ifo-traductor-c.txt", 0x6F0E40, 0x40, "traductor mp4Ifo (rama 0xX10000 -> 0xB0800001)"),
    ("19-mmgr-logger-prefijos.txt", 0x64E300, 0x90, "prefijo por cabecera del codigo en ## ERROR(...)"),
    ("20-mmgr-traductor-default.txt", 0x64ECDC, 0x20, "rama por defecto del traductor MMGR (0x31000006)"),
]

VAS_LITERALES = {
    "MountCmd : Flash Mount Error": [0x8EA305],
    "GetDeviceInfo : ER_SEQUENCE  DEVICE Unmounted": [0x8E9EAA],
    "FlashLoadMp4 : CreateAndLoad Error": [0x8EA6B8],
    "Err RcsBackupTblData": [0x823999],
    "CheckSalvageStatus": [0x90A075, 0x90B3C8],
    "tabla MMgrGlobal {nombre,codigo}": [0x8F6CA8],
    "enum AVI_STATE": [0x7AE476],
    "mmgrifoacsr/MMgrMp4IfoAcsr.cpp": [0x90D18C],
    "IF/mp4Ifo_General.cpp": [0x91443D],
    "mmgrifoacsr/MMgrAvcHdIfoAcsr.cpp": [0x8F6798],
    "avimmgr/AviMMgrCmd.cpp": [0x8E7F72],
}


def tabla_mmgrglobal(e: Elf) -> str:
    out = [
        "# Tabla {nombre, codigo} de errores MMgrGlobal (libmpr.so @ 0x8F6CA8..0x8F6E50)",
        "# Consumida por el traductor/impresor 0x64E300 (## ERROR(MMGR):0x%08X ...)",
    ]
    d = e.read(0x8F6CA8, 0x1A8)
    for i in range(0, 0x1A8, 8):
        p = struct.unpack_from("<I", d, i)[0]
        c = struct.unpack_from("<I", d, i + 4)[0]
        if not (0x800000 <= p <= 0x9FFFFF):
            continue
        out.append(f"{0x8F6CA8 + i:08x}  codigo=0x{c:08x}  {e.cstr(p, 48)}")
    return "\n".join(out)


def dump_anillo() -> None:
    b = DUMP.read_bytes()
    h = hashlib.sha256(b).hexdigest()
    print(f"dump: {len(b)} B  sha256={h}")
    reg = b[ANILLO_INI:ANILLO_FIN]
    for pat in (b"MountCmd", b"FlashMount", b"RcsBackup", b"GetDeviceInfo", b"LoadSub"):
        n = reg.count(pat)
        print(f"  {pat.decode():16s} {n} ocurrencia(s)")


def main() -> None:
    if not LIB.exists():
        raise SystemExit(f"no existe {LIB}")
    e = Elf(LIB)
    if "--dump" in sys.argv:
        dump_anillo()
        return
    base = Path(__file__).resolve().parent
    for nombre, va, size, _desc in RANGOS:
        (base / nombre).write_text(listado(e, va, size) + "\n", encoding="utf-8")
        print(f"{nombre}  {_desc}")
    (base / "15-tabla-mmgrglobal-errores.txt").write_text(
        tabla_mmgrglobal(e) + "\n", encoding="utf-8"
    )
    print("15-tabla-mmgrglobal-errores.txt")
    print("\nliterales (VA):")
    for txt, vas in VAS_LITERALES.items():
        print(f"  {', '.join(hex(v) for v in vas)}  {txt}")


if __name__ == "__main__":
    main()
