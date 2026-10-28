"""Utilidades de solo lectura sobre av-cam.bin (fw 3.21): desensamblado Thumb-2 y búsqueda de referencias."""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
FW = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"

_data = FW.read_bytes()
assert hashlib.sha256(_data).hexdigest() == SHA, "av-cam.bin no coincide con fw 3.21"
_md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
_md.detail = False


def rd(addr: int, n: int) -> bytes:
    return _data[addr - BASE:addr - BASE + n]


def u32(addr: int) -> int:
    return struct.unpack("<I", rd(addr, 4))[0]


def u16(addr: int) -> int:
    return struct.unpack("<H", rd(addr, 2))[0]


def dis(start: int, end: int):
    out = []
    for i in _md.disasm(rd(start, end - start), start):
        out.append((i.address, i.bytes.hex(), i.mnemonic, i.op_str))
    return out


def cstr(addr: int, n: int = 80) -> str | None:
    if not (BASE <= addr < BASE + len(_data)):
        return None
    s = rd(addr, n).split(b"\0")[0]
    if len(s) >= 4 and all(32 <= c < 127 for c in s):
        return s.decode()
    return None


def show(start: int, end: int) -> None:
    lit: dict[str, int] = {}
    for a, b, m, o in dis(start, end):
        c = ""
        if m.startswith("ldr") and "[pc" in o:
            try:
                off = int(o.split("#")[1].rstrip("]"), 16)
                v = u32(((a + 4) & ~3) + off)
                c = f"  ; =0x{v:08x}"
                lit[o.split(",")[0]] = v
            except (ValueError, IndexError):
                pass  # literal no resoluble: se omite el comentario
        elif m == "add" and o.endswith(", pc") and o.split(",")[0] in lit:
            t = (lit[o.split(",")[0]] + a + 4) & 0xFFFFFFFF
            c = f"  ; ->0x{t:08x}"
            sv = cstr(t)
            if sv:
                c += f" \"{sv}\""
        print(f"{a:08x}  {b:<10} {m:<8} {o}{c}")


_CALLS: dict[int, list[int]] | None = None


def calls() -> dict[int, list[int]]:
    """Índice destino -> llamadores (bl/blx/b.w con destino inmediato) de todo el código; desensamblado lineal con resincronización."""
    global _CALLS
    if _CALLS is None:
        import os
        import pickle
        cache = "/tmp/e25_17_calls.pkl"
        if os.path.exists(cache):
            with open(cache, "rb") as fh:
                _CALLS = pickle.load(fh)
            return _CALLS
        idx: dict[int, list[int]] = {}
        a, hi = 0x43541000, 0x43b40000
        while a < hi:
            got = False
            for i in _md.disasm(_data[a - BASE:min(a - BASE + 0x4000, hi - BASE)], a):
                got = True
                a = i.address + i.size
                if i.mnemonic in ("bl", "blx", "b.w") and i.op_str.startswith("#"):
                    idx.setdefault(int(i.op_str[1:], 16), []).append(i.address)
            if not got:
                a += 2
        with open(cache, "wb") as fh:
            pickle.dump(idx, fh)
        _CALLS = idx
    return _CALLS


def bl_callers(target: int):
    return calls().get(target, [])


if __name__ == "__main__":
    a = int(sys.argv[1], 16)
    b = int(sys.argv[2], 16)
    show(a, b)
