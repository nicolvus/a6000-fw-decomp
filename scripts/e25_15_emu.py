#!/usr/bin/env python3
"""E25-15 — emulación diferencial offline de `SetExposure` (IMX210) y del método `+0x30`.

Compara los escenarios A (ShutMode 3, r5=1), B (ShutMode 0, r5=1) y C
(ShutMode 0, r5 calculado) al nivel de **escrituras de software**: bloque de
comandos del imager (`obj+0xfc`), campos de configuración `0x4401c...` y
contadores del objeto. No se conecta la cámara ni se escribe nada fuera de la
copia del firmware en la memoria del emulador.

La emulación reproduce instrucciones; **no** demuestra el comportamiento
eléctrico del sensor ni el instante físico de integración.

Funciones emuladas (fw 3.21, `av-cam.bin`, SHA-256 b60c845c…):
  SetExposure 0x436d6f6c  (vtable +0x28)
  SetRead     0x436d7e08  (vtable +0x30)
  Conversión  0x436d8a90  (código de posición -> posición 0..4095; único llamador +0x30)
  Tiempo Tv   0x4382fac8  (código Tv -> µs; verificado en E25-11)

Llamadas externas sustituidas por stubs (qué representan y qué NO permiten
afirmar):
  0x436d9f70 -> 0   comprobación de driver pendiente (se fuerza "sin cambio")
  0x436d6738 -> 0   log de error
  0x43901a8c -> 0   envío de mensaje al sistema (no se modela la cola)
  0x436d6450 -> 0   consulta auxiliar de estado (su retorno no se usa en esta ruta)
  0x436d6020 -> 0   log interno
  0x436d60e4 -> 0   log interno
  0x436d6118 -> ptr objeto imager sintético (singleton)
Los stubs no cambian los destinos de escritura comparados; impiden afirmar
nada sobre colas, temporización real ni respuesta del sensor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_MEM_WRITE,
    UC_MODE_THUMB,
    UC_PROT_ALL,
    Uc,
    UcError,
)
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"

SETEXPOSURE = 0x436D6F6C
SETREAD = 0x436D7E08
CONV = 0x436D8A90
TV_US = 0x4382FAC8

SENT = 0x20000000
STACK = 0x10000000
OBJ = 0x30000000
PARAM_SE = 0x30010000
PARAM_SR = 0x30010100
PARAM_CONV = 0x30010200
CFG = 0x30030000

LINE_US = 15.2
VTS = 4219.0

# código Tv: 0x1000 + 256*log2(1/t)  (0x1000 = 1 s)
SPEEDS = {
    "1/8000": 0x1CF7,
    "1/4000": 0x1BF7,
    "1/1000": 0x19F7,
    "1/250": 0x17F7,
    "1/60": 0x15E8,
    "1/15": 0x13E8,
    "1/8": 0x12F8,
    "1s": 0x1000,
    "30s": 0x0B17,
}

# códigos de posición (entrada de +0x30): 0x1000 = posición más larga.
# El valor real por velocidad lo calcula 0x437b061c a partir del código Tv; no se
# emula aquí (requiere el objeto de ajustes completo). Para el diferencial A/B/C se
# usa el MISMO código en los tres escenarios: +0x30 no recibe ShutMode ni r5.
POSITION_CODES = (0x0A00, 0x0B00, 0x0C00, 0x0D00, 0x0E00, 0x0F00, 0x0FE0, 0x0FF0, 0x0FFF, 0x1000)
SR_CODE = 0x0F00


def thumb_stub_ret(value: int) -> bytes:
    return struct.pack("<HH", 0x2000 | (value & 0xFF), 0x4770)


def thumb_stub_ptr(addr: int) -> bytes:
    return struct.pack("<HHH", 0x4800, 0x4770, 0x0000) + struct.pack("<I", addr)


class Emu:
    def __init__(self):
        data = FW.read_bytes()
        self.mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        size = ((len(data) + 0xFFF) & ~0xFFF) + 0x200000
        self.mu.mem_map(BASE, size, UC_PROT_ALL)
        self.mu.mem_write(BASE, data)
        self.mu.mem_map(STACK, 0x20000, UC_PROT_ALL)
        self.mu.mem_map(SENT, 0x1000, UC_PROT_ALL)
        self.mu.mem_write(SENT, b"\x00\xbe")  # bkpt
        self.mu.mem_map(OBJ, 0x20000, UC_PROT_ALL)
        self.mu.mem_map(CFG, 0x20000, UC_PROT_ALL)
        self.writes: list[tuple[int, int, int]] = []
        self.mu.hook_add(UC_HOOK_MEM_WRITE, self._on_write)
        self._patch_stubs()
        self.setup_object()

    def _patch_stubs(self):
        for addr, val in (
            (0x436D9F70, 0),
            (0x436D6738, 0),
            (0x43901A8C, 0),
            (0x436D6450, 0),
            (0x436D6020, 0),
            (0x436D60E4, 0),
        ):
            self.mu.mem_write(addr, thumb_stub_ret(val))
        self.mu.mem_write(0x436D6118, thumb_stub_ptr(OBJ))

    def _on_write(self, uc, access, address, size, value, user_data):
        self.writes.append((address, size, value))

    def setup_object(self, drv: int = 0x0B):
        """Objeto imager sintético con descriptor de modo en obj+0x294."""
        mu = self.mu
        mu.mem_write(OBJ, b"\x00" * 0x1C0)
        mu.mem_write(CFG, b"\x00" * 0x20000)
        desc = CFG + 0x1000
        mu.mem_write(OBJ + 0x294, struct.pack("<I", desc))
        mu.mem_write(desc, struct.pack("<IIII", 0x11, 30, 0, 0))
        mu.mem_write(desc + 4, struct.pack("<I", 30))
        mu.mem_write(desc + 0x18, struct.pack("<I", CFG + 0x3000))
        mu.mem_write(desc + 0x1C, struct.pack("<I", CFG + 0x2000))
        base = [14539, 14756, 14974, 15192, 15411, 15630]
        blob = b"".join(struct.pack("<III", v << 8, v << 8, v << 8) for v in base)
        mu.mem_write(CFG + 0x2000, blob + b"\x00" * (30 * 12 - len(blob)))
        r = bytearray(48)
        struct.pack_into("<H", r, 0x1A, 0x0600)
        struct.pack_into("<H", r, 0x1C, 0x1000)
        mu.mem_write(CFG + 0x3000, bytes(r) * 30)
        mu.mem_write(OBJ + 0x170, struct.pack("<I", drv))
        mu.mem_write(OBJ + 0x17C, b"\x00")
        mu.mem_write(OBJ + 0x18, b"\x00" * 0x40)

    def call(self, addr: int, r0: int, r1: int, r2: int = 0) -> int:
        mu = self.mu
        mu.reg_write(UC_ARM_REG_R0, r0)
        mu.reg_write(UC_ARM_REG_R1, r1)
        mu.reg_write(UC_ARM_REG_R2, r2)
        mu.reg_write(UC_ARM_REG_SP, STACK + 0x18000)
        mu.reg_write(UC_ARM_REG_LR, SENT | 1)
        self.writes = []
        try:
            mu.emu_start(addr | 1, SENT, count=200000)
        except UcError as e:  # pragma: no cover - diagnóstico
            raise RuntimeError(f"Unicorn: {e}") from e
        return mu.reg_read(UC_ARM_REG_R0)

    def cmd_writes(self) -> dict[str, int]:
        """Campos del bloque de comandos, relativos a obj+0xfc (blk+0x50..)."""
        out: dict[str, int] = {}
        for a, s, v in self.writes:
            if OBJ + 0xFC <= a < OBJ + 0x1C0:
                out[f"blk+0x{a - OBJ - 0xFC:02x}"] = v
        return out

    def cfg_writes(self) -> list[tuple[str, int]]:
        return [(f"0x{a:08x}", v) for a, s, v in self.writes if 0x4401C000 <= a < 0x4401D000]

    def obj_writes(self) -> list[tuple[str, int]]:
        return [(f"obj+0x{a - OBJ:03x}", v) for a, s, v in self.writes if OBJ <= a < OBJ + 0x100]


def param_se(r5: int, shutmode: int, p4: int = 0, p6: int = 0) -> bytes:
    return struct.pack("<HHHHBBBB", r5 & 0xFFFF, p4, p6, 0, 0, shutmode, 0, 0)


def param_sr(code: int) -> bytes:
    return struct.pack("<HHH", code, 0x0FFF, 0x0100) + b"\x00" * 10


def scenario(emu: Emu, r5: int, shutmode: int, code: int) -> dict:
    emu.mu.mem_write(PARAM_SE, param_se(r5, shutmode))
    emu.call(SETEXPOSURE, OBJ, PARAM_SE)
    se = {"cmd": emu.cmd_writes(), "cfg": emu.cfg_writes(), "obj": emu.obj_writes()}
    emu.mu.mem_write(PARAM_SR, param_sr(code))
    emu.call(SETREAD, OBJ, PARAM_SR)
    sr = {"cmd": emu.cmd_writes(), "cfg": emu.cfg_writes()}
    return {"setexposure": se, "setread": sr}


def conv(emu: Emu, code: int, minv: int = 0x0600, maxv: int = 0x0FFF) -> int:
    """Emula 0x436d8a90 con los valores por defecto de +0x30 (0x0600/0x0fff/0x0fff)."""
    blob = struct.pack("<HHHHHH", code & 0xFFFF, minv, maxv, 0x0600, 0x0FFF, 0x0FFF)
    emu.mu.mem_write(PARAM_CONV, blob)
    return emu.call(CONV, OBJ + 0x18, PARAM_CONV) & 0xFFFF


def tv_us(emu: Emu, code: int) -> int:
    return emu.call(TV_US, code, 0) & 0xFFFFFFFF


def r5_from_us(us: float, vts: float = VTS, line_us: float = LINE_US) -> int:
    return round(vts - us / line_us)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, help="escribe la evidencia JSON")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if not FW.exists():
        print("firmware no disponible; se omite (no cuenta como verificación)", file=sys.stderr)
        return 2
    h = hashlib.sha256()
    with FW.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    if h.hexdigest() != SHA:
        print(f"SHA-256 inesperado: {h.hexdigest()}", file=sys.stderr)
        return 2

    emu = Emu()
    out: dict = {
        "firmware_sha256": SHA,
        "line_us": LINE_US,
        "vts": VTS,
        "nota": "escrituras de software; no comportamiento del sensor",
        "velocidades": {},
        "conversion_posicion": {},
        "escenarios": {},
    }

    for name, code in SPEEDS.items():
        us = tv_us(emu, code)
        out["velocidades"][name] = {
            "code": code,
            "us": us,
            "lines": round(us / LINE_US, 3),
            "r5": r5_from_us(us),
        }
    for code in POSITION_CODES:
        out["conversion_posicion"][f"0x{code:04x}"] = conv(emu, code)

    for name, code in SPEEDS.items():
        us = out["velocidades"][name]["us"]
        r5c = r5_from_us(us)
        out["escenarios"][name] = {
            "sr_code": SR_CODE,
            "A_shutmode3_r5_1": scenario(emu, 1, 3, SR_CODE),
            "B_shutmode0_r5_1": scenario(emu, 1, 0, SR_CODE),
            "C_shutmode0_r5_calc": scenario(emu, max(0, r5c), 0, SR_CODE),
        }

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")

    if not args.quiet:
        print(f"{'vel':>7} {'µs':>10} {'líneas':>9} {'r5c':>6}")
        for name in SPEEDS:
            c = out["velocidades"][name]
            print(f"{name:>7} {c['us']:>10} {c['lines']:>9.2f} {c['r5']:>6}")
        print("\nconversión 0x436d8a90 (posición -> posición 0..4095):")
        for k, v in out["conversion_posicion"].items():
            print(f"  {k} -> {v}")
        print()
        for name in ("1/8000", "1/250", "1/60"):
            print(f"== {name}")
            for sc in ("A_shutmode3_r5_1", "B_shutmode0_r5_1", "C_shutmode0_r5_calc"):
                se = out["escenarios"][name][sc]["setexposure"]["cmd"]
                sr = out["escenarios"][name][sc]["setread"]["cmd"]
                keep = ("blk+0x50", "blk+0x52", "blk+0x54", "blk+0x56", "blk+0x57")
                print(f"  {sc:>22}: SE {[se.get(k) for k in keep]} | +0x30 "
                      f"{[sr.get('blk+0x66'), sr.get('blk+0x68'), sr.get('blk+0x6a'), sr.get('blk+0x6c')]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
