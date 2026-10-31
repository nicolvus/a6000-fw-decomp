"""E26-R39 — emulación (Unicorn) de la petición de bloques TPZL de Loader3 y de la programación del LDEC por el ARM7.

Ejecuta el código real de `bootloader.bin`:

* Loader3 (Thumb, base `0xc01f0000`): `c01fe4ec` (registro TPZL: cabecera y TOC) y `c01fdd8e`
  (petición por bloque) hasta la llamada a `c01fce8c`, donde se captura el trabajo de 0x18 B.
* ARM7 (ARM, base 0): `0x3f4`, que escribe los registros del LDEC (`0xf2903000`).

Se sustituyen por Python solo funciones ausentes del volcado (`c020xxxx`: printf, división) y los
servicios de E/S (`c01fd9d4` lectura cruda, `c01f9d10` malloc, `c01fdbe0` lista de sectores).
El LDEC es silicio: se modela como R36 (`MODELO`): entra el flujo de sectores enteros desde
`offset >> 9`; produce `registros` registros de 4096 B cada uno, en el formato que usa Sony.
Solo lee; nunca escribe imágenes.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_CODE,
    UC_HOOK_MEM_WRITE,
    UC_MODE_ARM,
    UC_MODE_THUMB,
    Uc,
)
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_27 import tpzl  # type: ignore[import-not-found]

BL = ROOT / "analysis/camera-dumps/updater-20261020-175427/bootloader.bin"
SONY = (
    ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3"
)
INSTALLED_325 = ROOT / "analysis/e25-27/artifacts/nflasha3.integrated.bin"
OUT = ROOT / "analysis/e26-recovery/r39-tpzl-emu.json"

L3, L3_LEN = 0xC01F0000, 0x15800
RAM, RAM_LEN = 0xC0000000, 0x300000
HEAP, STACK = 0xC0100000, 0xC02F0000
DEV, CACHE, CTX = 0xC0120000, 0xC0121000, 0xC0122000
SL = 0xC00E1764  # caché de bloques de c01fdd8e
LDEC = 0xF2903000
REGS = ("REG_00", "REG_04", None, "RECORDS_0C", "DEST_10")
STOP = 0xC01F0001  # dirección de retorno centinela (Thumb)


class Loader3:
    """Unicorn con Loader3 cargado y los servicios mínimos sustituidos."""

    def __init__(self, image: bytes, code: bytes) -> None:
        self.image, self.heap = image, HEAP
        self.prints: list[tuple[int, int]] = []
        self.request: dict | None = None
        uc = self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(RAM, RAM_LEN)
        uc.mem_write(L3, code)
        uc.hook_add(UC_HOOK_CODE, self._hook)
        self.stubs = {
            0xC01F9D10: self._malloc,
            0xC01F9D36: lambda: 0,
            0xC020BD24: self._printf,
            # división de libgcc ausente del volcado; su resultado solo llega a c01fdbe0 (sustituida)
            0xC020D7D8: lambda: self.r(0) // self.r(1) if self.r(1) else 0,
            0xC01FD9D4: self._read,
            0xC01FDBE0: self._list,
            0xC01FCE8C: self._send,
        }

    def r(self, n: int) -> int:
        return self.uc.reg_read(UC_ARM_REG_R0 + n)

    def w32(self, addr: int, value: int) -> None:
        self.uc.mem_write(addr, struct.pack("<I", value & 0xFFFFFFFF))

    def r32(self, addr: int) -> int:
        return struct.unpack("<I", self.uc.mem_read(addr, 4))[0]

    def _malloc(self) -> int:
        ptr, self.heap = self.heap, (self.heap + self.r(0) + 0xFFF) & ~0xFFF
        return ptr

    def _printf(self) -> int:
        self.prints.append((self.r(0), self.r(1)))
        return 0

    def _read(self) -> int:  # c01fd9d4(dev, buf, offset, len)
        buf, off, n = self.r(1), self.r(2), self.r(3)
        self.uc.mem_write(buf, self.image[off : off + n])
        return 0

    def _list(self) -> int:  # c01fdbe0(ctx, ?, sector, n, [sp]=capacidad)
        self.list_args = (self.r(2), self.r(3))
        return CTX

    def _send(self) -> int:  # c01fce8c(&trabajo): se captura y se detiene
        raw = bytes(self.uc.mem_read(self.r(0), 0x18))
        self.request = dict(
            zip(
                ("list", "ctx", "residue", "records", "dest", "size"),
                struct.unpack("<6I", raw),
            ),
            raw=raw,
            sector=self.list_args[0],
            nsect=self.list_args[1],
        )
        self.uc.emu_stop()
        return 0

    def _hook(self, uc: Uc, addr: int, _size: int, _data: object) -> None:
        stub = self.stubs.get(addr)
        if stub is None:
            if not L3 <= addr < L3 + L3_LEN:
                raise RuntimeError(
                    f"ejecución fuera de Loader3 sin sustituir: {addr:#x}"
                )
            return
        uc.reg_write(UC_ARM_REG_R0, stub() & 0xFFFFFFFF)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def call(self, fn: int, *args: int) -> int:
        for i, a in enumerate(args):
            self.uc.reg_write(UC_ARM_REG_R0 + i, a)
        self.uc.reg_write(UC_ARM_REG_SP, STACK)
        self.uc.reg_write(UC_ARM_REG_LR, STOP)
        self.uc.emu_start(fn | 1, STOP & ~1, count=200_000)
        return self.r(0)

    def setup(self) -> None:
        self.w32(DEV + 0x00, 3)  # identificador del dispositivo
        self.w32(DEV + 0x0C, CTX)
        self.w32(DEV + 0x14, 0)  # sector base: relativo a la partición
        self.w32(DEV + 0x28, 0x800)
        self.w32(DEV + 0x2C, 0x10000)
        self.w32(SL, 1)  # una entrada de caché
        self.w32(SL + 4, CACHE)
        self.w32(CACHE + 0, 0xC0200000)  # búfer destino
        self.w32(CACHE + 8, 0xFFFFFFFF)  # sin acierto de caché

    def register(self) -> int:
        self.setup()
        return self.call(0xC01FE4EC, DEV)

    def block(self, index: int) -> dict:
        self.request = None
        self.w32(SL + 8, 0)
        self.call(0xC01FDD8E, DEV, index)
        if self.request is None:
            raise RuntimeError(f"bloque {index}: no se llegó a c01fce8c")
        return self.request


def arm7_program(arm7: bytes, work: bytes) -> dict[int, int]:
    """Ejecuta ARM7 `0x3f4` con el trabajo copiado y devuelve las escrituras en el LDEC."""
    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    uc.mem_map(0, 0x10000)
    uc.mem_write(0, arm7)
    uc.mem_map(LDEC, 0x1000)
    uc.mem_write(0x8000, work)
    writes: dict[int, int] = {}
    uc.hook_add(
        UC_HOOK_MEM_WRITE,
        lambda _uc, _acc, addr, _size, value, _d: writes.__setitem__(
            addr - LDEC, value
        ),
        begin=LDEC,
        end=LDEC + 0xFFF,
    )
    uc.reg_write(UC_ARM_REG_R0, 0x8000)
    uc.reg_write(UC_ARM_REG_SP, 0xF000)
    uc.reg_write(UC_ARM_REG_LR, 0xFFFC)
    uc.emu_start(0x3F4, 0xFFFC)
    return writes


def ldec_model(stream: bytes, records: int, expected: bytes) -> dict:
    """MODELO R36: `records` registros de 4096 B leídos en orden desde el primer byte del flujo."""
    out, pos = bytearray(), 0
    for k in range(records):
        try:
            chunk, pos = tpzl._inflate_segment(stream, pos)
        except tpzl.TpzlError as exc:
            return {
                "ok": False,
                "registro": k,
                "motivo": str(exc),
                "primer_byte": stream[0],
            }
        if len(chunk) != tpzl.RECORD:
            return {
                "ok": False,
                "registro": k,
                "motivo": f"registro de {len(chunk)} B",
                "primer_byte": stream[0],
            }
        out += chunk
    if bytes(out) != expected:
        return {
            "ok": False,
            "registro": None,
            "motivo": "contenido distinto",
            "primer_byte": stream[0],
        }
    return {"ok": True}


def run(
    image: bytes, code: bytes, arm7: bytes, blocks: list[int] | None = None
) -> dict:
    parsed = tpzl.TpzlImage.parse(image)
    emu = Loader3(image, code)
    if emu.register() != 0:
        return {"registro": "rechazado"}
    entries = emu.r32(DEV + 8)
    result: dict = {
        "entradas": entries,
        "bloques": {},
        "avisos_residuo": 0,
        "fallos": [],
    }
    for i in range(entries) if blocks is None else blocks:
        req = emu.block(i)
        regs = arm7_program(arm7, req["raw"])
        start = req["sector"] * 512
        stream = image[start : start + req["nsect"] * 512]
        expected = tpzl.decode_block(parsed.block(i), parsed.block_size)
        verdict = ldec_model(stream, regs[0xC], expected)
        result["avisos_residuo"] += bool(req["residue"])
        if not verdict["ok"]:
            result["fallos"].append(i)
        if blocks is not None or not verdict["ok"] or i < 2:
            result["bloques"][i] = {
                "sector": req["sector"],
                "sectores": req["nsect"],
                "residuo_trabajo+8": req["residue"],
                "ldec_registros": regs[0xC],
                "ldec_destino": hex(regs[0x10]),
                "ldec_escrituras": sorted(regs),
                "ldec": verdict,
            }
    result["primer_fallo"] = result["fallos"][0] if result["fallos"] else None
    return result


def images() -> dict[str, bytes]:
    sony = SONY.read_bytes()
    inst = INSTALLED_325.read_bytes()
    s, i = tpzl.TpzlImage.parse(sony), tpzl.TpzlImage.parse(inst)
    content = i.decompressed()
    bs = s.block_size
    repl = {
        k: content[k * bs : (k + 1) * bs]
        for k in range(len(s.entries))
        if content[k * bs : (k + 1) * bs] != tpzl.decode_block(s.block(k), bs)
    }
    fixed, _ = tpzl.rebuild(s, repl)
    return {"sony_3.21": sony, "instalada_3.25": inst, "corregida_R36": fixed}


def main() -> None:
    bl = BL.read_bytes()
    code, arm7 = bl[0x22800 : 0x22800 + L3_LEN], bl[0x18800 : 0x18800 + 0x3800]
    report: dict[str, Any] = {
        "bootloader_sha256": hashlib.sha256(bl).hexdigest(),
        "imagenes": {},
    }
    for name, img in images().items():
        res = run(img, code, arm7)
        res["sha256"] = hashlib.sha256(img).hexdigest()
        res["n_fallos"] = len(res["fallos"])
        report["imagenes"][name] = res
    OUT.write_text(
        json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    for name, res in report["imagenes"].items():
        print(
            name,
            res["entradas"],
            "fallos",
            res["n_fallos"],
            "avisos",
            res["avisos_residuo"],
            "primero",
            res["primer_fallo"],
        )


if __name__ == "__main__":
    main()
