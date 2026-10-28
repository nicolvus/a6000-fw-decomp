#!/usr/bin/env python3
"""T052-A — lector y auditoría offline de los parámetros reales de exposición.

Este script NO habla con la cámara y NO escribe nada: solo lee el firmware
`av-cam.bin` (3.21) y, si existe, un volcado de RAM real ya capturado en el PC.
Con esos datos:

1. verifica la identidad del binario y el mapa virtual→físico;
2. lee una lista blanca de objetos (record, settings, imager, compuerta);
3. ejecuta el productor nativo `0x4383fa40` en Unicorn con los valores
   observados y con las dos hipótesis de VTS (4219 / 4266);
4. escribe `analysis/t052-a/lecturas.json`.

El volcado de referencia es `ram-servicio-20261020/ram_0x80000000.bin`
(1 GiB, cámara en marcha, reposo, fw 3.21). No se versiona. Si no está, el
script sigue y marca las lecturas físicas como no disponibles.

Modo `--protocol`: imprime el protocolo de lectura de T052-B (solo lectura)
para ejecutarlo a mano cuando la cámara esté accesible. No abre sockets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
DUMP = ROOT / "analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin"
OUT = ROOT / "analysis/t052-a/lecturas.json"

BASE = 0x43541000
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
RAM_OFF = 0x40000000          # virtual = físico − 0x40000000 (código y datos de av-cam)
DUMP_BASE = 0x80000000

# GOT de av-cam (base 0x4401eee4) y objetos confirmados en el volcado real.
GOT = 0x4401EEE4
GOT_RECORD_A = GOT + 0x3764          # 0x44022648 -> 0x43ea5b4c
GOT_RECORD_B = GOT + 0x6F18          # 0x44025dfc -> 0x43eee770
GOT_SETTINGS = GOT + 0x1904          # 0x440207e8 -> 0x43f79f94
GOT_IMAGER = GOT + 0x2CC4            # 0x44021ba8 -> 0x43ea976c
GOT_GATE_B = GOT + 0x5F74            # 0x44024e58 -> 0x43f6e5c2
GOT_PREDICATE = GOT + 0x64E8         # 0x440253cc -> 0x43deb360

RECORD_A = 0x43EA5B4C
RECORD_B = 0x43EEE770
SETTINGS = 0x43F79F94
IMAGER = 0x43EA976C
GATE_B = 0x43F6E5C2
PREDICATE = 0x43DEB360

TV_TO_R5 = 0x4383FA40
GATE_WRITER = 0x437B3B08

LINE_US = 15.2
LINE_Q8 = round(LINE_US * 256)        # 3891
VTS_HYP = (4219, 4266)

# Direcciones (virtuales) de la lista blanca. Se traducen a físico con RAM_OFF.
WHITELIST = {
    "record_a": (RECORD_A, 0x158),
    "record_b": (RECORD_B, 0x158),
    "settings": (SETTINGS, 0x4c0),
    "imager": (IMAGER, 0x520),
    "gate_b": (GATE_B, 0x100),
    "predicate": (PREDICATE, 0x40),
    "got_record_a": (GOT_RECORD_A, 4),
    "got_record_b": (GOT_RECORD_B, 4),
    "got_settings": (GOT_SETTINGS, 4),
    "got_imager": (GOT_IMAGER, 4),
    "got_gate_b": (GOT_GATE_B, 4),
    "got_predicate": (GOT_PREDICATE, 4),
}

SPEEDS = {
    "1/4000": (0x1BF7, 0.00025),
    "1/250": (0x17F7, 0.004),
    "1/60": (0x15E8, 0.016674),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Dump:
    """Lectura acotada y verificada de un volcado de RAM ya capturado."""

    def __init__(self, path: Path):
        self.path = path
        self.f = path.open("rb")
        self.size = path.stat().st_size

    def read(self, virt: int, n: int) -> bytes:
        phys = virt + RAM_OFF
        off = phys - DUMP_BASE
        if off < 0 or off + n > self.size:
            raise ValueError(f"fuera del volcado: {virt:#x} (+{n:#x})")
        self.f.seek(off)
        data = self.f.read(n)
        if len(data) != n:
            raise ValueError(f"lectura corta en {virt:#x}: {len(data)} != {n}")
        return data

    def u8(self, virt: int) -> int:
        return self.read(virt, 1)[0]

    def u16(self, virt: int) -> int:
        return struct.unpack("<H", self.read(virt, 2))[0]

    def u32(self, virt: int) -> int:
        return struct.unpack("<I", self.read(virt, 4))[0]

    def hex(self, virt: int, n: int) -> str:
        return self.read(virt, n).hex()


def read_whitelist(dump: Dump) -> dict:
    out = {}
    for name, (addr, n) in WHITELIST.items():
        # Solo un prefijo corto: el JSON no debe convertirse en un volcado de RAM.
        out[name] = {
            "virtual": f"0x{addr:08x}",
            "physical": f"0x{addr + RAM_OFF:08x}",
            "prefijo_hex": dump.hex(addr, min(n, 0x20)),
        }
    return out


def objects(dump: Dump) -> dict:
    """Valores puntuales de los objetos que usa la cadena de exposición."""
    return {
        "record_a": {
            "tv_f6": dump.u16(RECORD_A + 0xF6),
            "periodo_c": dump.u32(RECORD_A + 0xC),
            "suelo_1c": dump.u16(RECORD_A + 0x1C),
            "vts_20": dump.u16(RECORD_A + 0x20),
            "r5_64": dump.u32(RECORD_A + 0x64),
            "frames_68": dump.u16(RECORD_A + 0x68),
            "shutmode_6d": dump.u8(RECORD_A + 0x6D),
            "lineas_f0": dump.u32(RECORD_A + 0xF0),
            "d8_dc": [dump.u16(RECORD_A + 0xD8), dump.u16(RECORD_A + 0xDA), dump.u16(RECORD_A + 0xDC)],
        },
        "record_b": {
            "tv_f6": dump.u16(RECORD_B + 0xF6),
            "periodo_c": dump.u32(RECORD_B + 0xC),
            "suelo_1c": dump.u16(RECORD_B + 0x1C),
            "vts_20": dump.u16(RECORD_B + 0x20),
            "r5_64": dump.u32(RECORD_B + 0x64),
            "frames_68": dump.u16(RECORD_B + 0x68),
            "shutmode_6d": dump.u8(RECORD_B + 0x6D),
            "lineas_f0": dump.u32(RECORD_B + 0xF0),
        },
        "settings": {
            "tv_162": dump.u16(SETTINGS + 0x162),
            "modo_15e": dump.u16(SETTINGS + 0x15E),
            "cuadro_164": dump.u16(SETTINGS + 0x164),
        },
        "imager": {
            "factor_4b8": dump.u8(IMAGER + 0x4B8),
            "modo_504": dump.u8(IMAGER + 0x504),
            "tv_118": dump.u16(IMAGER + 0x118),
            "tv_11a": dump.u16(IMAGER + 0x11A),
            "tv_11c": dump.u16(IMAGER + 0x11C),
            "tv_11e": dump.u16(IMAGER + 0x11E),
        },
        "gate": {
            "b_8c": dump.u8(GATE_B + 0x8C),
            "gate_esperada": int(dump.u8(IMAGER + 0x504) == 3)
            if dump.u8(GATE_B + 0x8C) not in (1, 2)
            else (1 if dump.u8(GATE_B + 0x8C) == 1 else 0),
        },
        "predicate": {
            "byte_10": dump.u8(PREDICATE + 0x10),
            # 0x43a12ca8 devuelve 1 si el byte es 0 o 1; 0 si es >= 2.
            "extra_frame": int(dump.u8(PREDICATE + 0x10) < 2),
        },
        "got": {
            "record_a": f"0x{dump.u32(GOT_RECORD_A):08x}",
            "record_b": f"0x{dump.u32(GOT_RECORD_B):08x}",
            "settings": f"0x{dump.u32(GOT_SETTINGS):08x}",
            "imager": f"0x{dump.u32(GOT_IMAGER):08x}",
            "gate_b": f"0x{dump.u32(GOT_GATE_B):08x}",
            "predicate": f"0x{dump.u32(GOT_PREDICATE):08x}",
        },
    }


def emulation() -> dict:
    """Ejecuta 0x4383fa40 (función del firmware) con las combinaciones clave."""
    sys.path.insert(0, str(ROOT / "scripts/e25_16"))
    from emu_core import thumb_stub_ret
    from emular_r5 import NATIVE_RECORD, NATIVE_SETTINGS, Harness

    rows = {}
    for name, (tv, nominal_s) in SPEEDS.items():
        rows[name] = {"tv": f"0x{tv:04x}", "nominal_ms": round(nominal_s * 1000, 3)}
        for vts in VTS_HYP:
            for extra in (0, 1):
                # Unicorn no invalida de forma fiable el stub reescrito entre
                # llamadas: se usa un emulador nuevo por combinación.
                h = Harness()
                h.mu.mem_write(0x43A12CA8, thumb_stub_ret(extra))
                h.mu.mem_write(NATIVE_RECORD, b"\x00" * 0x200)
                h.mu.mem_write(NATIVE_SETTINGS, b"\x00" * 0x600)
                h.mu.mem_write(NATIVE_RECORD + 0xC, struct.pack("<I", LINE_Q8))
                h.mu.mem_write(NATIVE_RECORD + 0x1C, struct.pack("<H", 1))
                h.mu.mem_write(NATIVE_RECORD + 0x20, struct.pack("<H", vts))
                h.mu.mem_write(NATIVE_RECORD + 0xF6, struct.pack("<H", tv))
                h.mu.mem_write(NATIVE_SETTINGS + 0x4B8, b"\x01")
                h.call(TV_TO_R5, NATIVE_RECORD, NATIVE_SETTINGS)
                r5 = struct.unpack("<I", h.read(NATIVE_RECORD + 0x64, 4))[0]
                frames = struct.unpack("<H", h.read(NATIVE_RECORD + 0x68, 2))[0]
                lines = struct.unpack("<I", h.read(NATIVE_RECORD + 0xF0, 4))[0]
                key = f"vts{vts}_extra{extra}"
                t_ley = (4219 - r5) * LINE_US / 1000
                rows[name][key] = {
                    "r5": r5,
                    "frames": frames,
                    "lineas": lines,
                    # tiempo según la ley medida T046/T047: (4219 − r5)·15.2 µs
                    "tiempo_ley_4219_ms": round(t_ley, 3),
                    "representable": int(2 <= r5 <= 4219),
                    "r5_valido_en_su_vts": int(2 <= r5 < vts),
                    "error_pct_vs_nominal": (
                        round((t_ley - nominal_s * 1000) / (nominal_s * 1000) * 100, 1)
                        if 2 <= r5 <= 4219 else None
                    ),
                }
    return {
        "funcion": f"0x{TV_TO_R5:08x}",
        "line_us": LINE_US,
        "line_q8": LINE_Q8,
        "factor": 1,
        "suelo": 1,
        "stub_predicado": "0x43a12ca8 se sustituye por 0/1; en el firmware real lee [0x43deb360+0x10]",
        "velocidades": rows,
    }


def protocol() -> str:
    """Protocolo T052-B0, solo lectura, para ejecutar a mano con la cámara."""
    return """T052-B0 — lectura de los parámetros reales de una foto (SOLO LECTURA)
=====================================================================
Requisitos: cámara en 3.23 (B1a), modo M, ISO fijo, RAW+JPEG, trípode,
escena fija. Ningún parche RAM activo. Comprobar los dos sitios de T050:

  dd if=/dev/mem bs=1 skip=0x836d6fb6 count=4  -> 91f80990
  dd if=/dev/mem bs=1 skip=0x836d7000 count=6  -> 28125ffa85fe

Para cada velocidad (1/4000, 1/250, 1/60):
  1. Fijar la velocidad y esperar a que se estabilice.
  2. Disparar una foto normal (sin parche).
  3. Leer, con dd if=/dev/mem (nunca of=/dev/mem), los dos registros:
       record A: 0x83ea5b4c + 0xf6/+0xc/+0x1c/+0x20/+0x64/+0x68/+0x6d/+0xf0/+0xd8
       record B: 0x83eee770 + los mismos campos
     y los objetos:
       settings 0x83f79f94 + 0x162 (Tv)
       imager   0x83ea976c + 0x4b8 (factor), +0x504 (modo)
       gate B   0x83f6e5c2 + 0x8c
       pred     0x83deb360 + 0x10
  4. Repetir la lectura inmediatamente: los valores deben coincidir
     (o documentar la transición de estado).
  5. Guardar los bytes en el PC; borrar el archivo temporal de la cámara.

Criterio de parada:
  - si record+0x20 no es 4219 ni 4266, o el período no es 3891, detener;
  - si el predicado [0x83deb360+0x10] < 2 (extra frame), detener C3;
  - si record+0xf6 no coincide con settings+0x162, repetir la lectura.
No escribir RAM, NVRAM ni NAND. No ejecutar 0x4383fa40 en la cámara.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dump", type=Path, default=DUMP)
    ap.add_argument("--json", type=Path, default=OUT)
    ap.add_argument("--protocol", action="store_true", help="imprime el protocolo T052-B0 y sale")
    args = ap.parse_args()

    if args.protocol:
        print(protocol())
        return 0

    if not FW.exists():
        print(f"falta el firmware: {FW}", file=sys.stderr)
        return 2
    got_sha = sha256(FW)
    if got_sha != SHA:
        print(f"SHA inesperado: {got_sha}", file=sys.stderr)
        return 2

    out = {
        "firmware": str(FW.relative_to(ROOT)),
        "sha256": got_sha,
        "base": f"0x{BASE:08x}",
        "ram_offset": f"0x{RAM_OFF:08x}",
        "dump": None,
        "lecturas": None,
        "emulacion": emulation(),
    }

    if args.dump.exists():
        d = Dump(args.dump)
        out["dump"] = {
            "path": str(args.dump.relative_to(ROOT)),
            "bytes": d.size,
            "base": f"0x{DUMP_BASE:08x}",
            "sha256": sha256(args.dump),
        }
        out["lecturas"] = {
            "whitelist": read_whitelist(d),
            "objetos": objects(d),
        }
    else:
        out["dump"] = {"path": str(args.dump), "disponible": False}

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"escrito {args.json}")
    if out["lecturas"]:
        o = out["lecturas"]["objetos"]
        print(f"record A: tv={o['record_a']['tv_f6']:#06x} vts={o['record_a']['vts_20']} "
              f"r5={o['record_a']['r5_64']} sm={o['record_a']['shutmode_6d']}")
        print(f"settings: tv={o['settings']['tv_162']:#06x}  "
              f"imager factor={o['imager']['factor_4b8']} modo={o['imager']['modo_504']}  "
              f"gate={o['gate']['gate_esperada']}  extra_frame={o['predicate']['extra_frame']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
