"""E25-18 — emula código REAL del firmware 3.21: `SetExposure` (0x436d6f70) y el tramo `StartExposure` 0x438c828c..0x438c83e8.

Solo software (Unicorn). Las funciones externas se sustituyen por stubs que registran sus argumentos. Demuestra qué
valores de shd/svd/spl/ShutMode alcanzan los registros sombra ID3–ID8 y cómo `cap+0x504`, `cap+0x740` y el
punto de enganche 0x438c82fe alteran `cap+0x650`. No prueba comportamiento del IMX210.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/e25_16"))
sys.path.insert(0, str(ROOT / "scripts/e25_17"))
from emu_core import BASE, FW, SCRATCH, Emu  # type: ignore[import-not-found]

SETEXP = 0x436D6F70
STARTEXP = 0x438C828C
GOT = 0x4401EEE4
# sombra de registro = [GOT+off]+2 ; (nombre, offset GOT, máscara de bits útiles)
SOMBRAS = {"ID3_svd_lo": (0x6A34, 0xFF), "ID4_svd_hi": (0x584, 0x0F), "ID5_shd_lo": (0x77A4, 0xFF),
           "ID6_shd_hi": (0x3DE8, 0x3F), "ID7_spl_lo": (0x48F8, 0xFF), "ID8_spl_hi": (0x70D0, 0x0F)}
CAP, IMG, TBL, ENT = SCRATCH + 0x1000, SCRATCH + 0x8000, SCRATCH + 0x9000, SCRATCH + 0x9100
MOD = 0x4355FD4C


def nuevo() -> Emu:
    e = Emu()
    # restaura el módulo/división real que Emu sustituye por un stub
    e.mu.mem_write(MOD, FW.read_bytes()[MOD - BASE:MOD - BASE + 0x40])
    return e


def _tabla(e: Emu) -> None:
    mu = e.mu
    mu.mem_write(IMG + 0x170, struct.pack("<I", 1))           # != 0x11: SetExposure válido
    mu.mem_write(IMG + 0x294, struct.pack("<I", TBL))
    mu.mem_write(TBL + 4, struct.pack("<I", 8))
    for off in (0x14, 0x18, 0x1C):
        mu.mem_write(TBL + off, struct.pack("<I", ENT))
    mu.mem_write(ENT, bytes(range(1, 0x100)) * 4)


def _sombras(e: Emu) -> dict[str, int]:
    out = {}
    for n, (off, m) in SOMBRAS.items():
        p = struct.unpack("<I", e.read(GOT + off, 4))[0]
        out[n] = e.read(p + 2, 1)[0] & m
    return out


def _movw_bx(v: int) -> bytes:
    """`movw r0,#v16; bx lr` (Thumb-2)."""
    v &= 0xFFFF
    hw1 = 0xF240 | ((v >> 11) & 1) << 10 | (v >> 12)
    hw2 = ((v >> 8) & 7) << 12 | (v & 0xFF)
    return struct.pack("<HHH", hw1, hw2, 0x4770)


def _stub_externos(e: Emu, reales: list[tuple[int, int]], logs: list, ret: dict[int, int] | None = None) -> None:
    """Parchea todo destino de bl/blx/b.w ajeno a `reales` con `movw r0,#v; bx lr` (ARM para blx) y registra sus argumentos."""
    import fw  # type: ignore[import-not-found]
    ret = ret or {}
    objetivos: dict[int, bool] = {}
    for lo, hi in reales:
        for _a, _b, m, o in fw.dis(lo, hi):
            if m in ("bl", "blx", "b.w") and o.startswith("#"):
                t = int(o[1:], 16)
                if not any(l <= t < h for l, h in reales) and not 0x4355FA00 <= t < 0x43560000:
                    objetivos[t] = objetivos.get(t, False) or m == "blx"
    for t, arm in objetivos.items():
        v = ret.get(t, 0)
        e.mu.mem_write(t, struct.pack("<II", 0xE3A00000 | (v & 0xFF), 0xE12FFF1E) if arm else _movw_bx(v))

        def hook(uc, addr, size, _):
            r1 = uc.reg_read(UC_ARM_REG_R1)
            try:
                blk = bytes(uc.mem_read(r1, 16))
            except Exception:  # noqa: BLE001 - r1 no es un puntero
                blk = b""
            logs.append((addr, uc.reg_read(UC_ARM_REG_R0), r1, uc.reg_read(UC_ARM_REG_R2), blk))
        e.mu.hook_add(UC_HOOK_CODE, hook, begin=t, end=t)


def setexposure(shd: int, svd: int, spl: int = 0, sint: int = 0, shutmode: int = 0) -> dict:
    """Ejecuta el cuerpo real de SetExposure con un bloque de parámetros `cap+0x64c` y devuelve los registros sombra."""
    e = nuevo()
    _tabla(e)
    prm = SCRATCH + 0x2000
    e.mu.mem_write(prm, struct.pack("<HxxHHBB", shd, svd, spl, sint, shutmode) if False else
                   struct.pack("<I", shd) + struct.pack("<HH", svd, spl) + bytes([sint, shutmode]) + b"\0\0")
    logs: list = []
    _stub_externos(e, [(0x436D6F00, 0x436D7400)], logs)
    e.mu.mem_write(prm, struct.pack("<H", shd & 0xFFFF) + b"\0\0" + struct.pack("<H", svd) + struct.pack("<H", spl)
                   + bytes([sint, shutmode]))
    antes = _sombras(e)
    e.call(SETEXP, IMG, prm)
    desp = _sombras(e)
    return {"entrada": {"shd": shd, "svd": svd, "spl": spl, "shutmode": shutmode}, "sombras": desp, "antes": antes,
            "obj_3a8_svd": struct.unpack("<I", e.read(IMG + 0x3A8, 4))[0],
            "decod": {"svd": desp["ID3_svd_lo"] | (desp["ID4_svd_hi"] << 8),
                      "shd": desp["ID5_shd_lo"] | (desp["ID6_shd_hi"] << 8),
                      "spl": desp["ID7_spl_lo"] | (desp["ID8_spl_hi"] << 8)},
            "llamadas_externas": [hex(l[0]) for l in logs]}


REALES_START = [(0x438C828C, 0x438C8470), (0x43B1E520, 0x43B1E570)]
NOMBRES = {0x437F8A50: "0x437f8a50", 0x43A12C64: "forzado", 0x436D6320: "SetExposure", 0x436D6398: "SetRead",
           0x43AD9116: "SSB", 0x43AD911C: "Execute", 0x43AD9132: "Execute_pre", 0x43901A8C: "msg_0x107",
           0x43AD90C2: "cfg_u16", 0x436D6118: "imager"}


def start_exposure(cap: dict, forzado: int = 0, cfg_u16: int = 0xFFFF, hook=None, hasta: int = 0x438C83E8) -> dict:
    """Ejecuta StartExposure (0x438c828c) hasta `hasta`. `cap`: offsets -> (valor, bytes). `hook(emu)` escribe memoria justo antes de `hook_pc`."""
    e = nuevo()
    logs: list = []
    _stub_externos(e, REALES_START, logs, {0x43A12C64: forzado, 0x43AD90C2: cfg_u16, 0x437F8A50: 0, 0x436C28D0: 1, 0x43AD90B6: 1})
    e.mu.mem_write(CAP, b"\0" * 0x5000)
    for off, (n, v) in cap.items():
        e.mu.mem_write(CAP + off, v.to_bytes(n, "little"))
    if hook:
        pc, fn = hook
        e.mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: fn(uc), begin=pc, end=pc)
    e.call(STARTEXP, CAP, 0, 0, sent=hasta)
    rd = lambda off, n: int.from_bytes(e.read(CAP + off, n), "little")
    sx = [l for l in logs if l[0] == 0x436D6320]
    prm = sx[0][4] if sx else b""
    return {"svd_a_SetExposure": int.from_bytes(prm[4:6], "little") if prm else None,
            "shd_a_SetExposure": int.from_bytes(prm[0:4], "little") if prm else None,
            "shutmode_a_SetExposure": prm[9] if prm else None,
            "param_bytes": prm.hex(), "mem": e.read(CAP, 0x5000), "cap650_final": rd(0x650, 2), "cap655_final": rd(0x655, 1), "cap73b": rd(0x73B, 1),
            "llamadas": [NOMBRES.get(l[0], hex(l[0])) for l in logs]}


if __name__ == "__main__":
    import json
    for s in [(1, 14, 0, 0, 0), (1, 472, 0, 0, 0), (2025, 0, 0, 0, 0)]:
        print(json.dumps(setexposure(*s))[:700])
    base = {0x64C: (4, 1), 0x650: (2, 14), 0x655: (1, 0), 0x504: (4, 0), 0x740: (4, 1), 0x4B9C: (4, 0)}
    r = start_exposure(base)
    r.pop("mem")
    print(json.dumps(r))
