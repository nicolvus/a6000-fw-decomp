#!/usr/bin/env python3
"""Sondas reproducibles, sin REA, para los bytes de TASK2.

Uso: python3 work/codex/scripts/task2_probe.py
Imprime hashes, tablas de modos y las secuencias de datos que se citan en
crosscheck.md. No modifica los binarios de entrada.
"""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 0x43541000
A7S = ROOT / "work/claude/input/a7s-av-cam.bin"
A6000 = ROOT / "work/claude/input/a6000-av-cam.bin"
DFE = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/dfe/dfe.bin"


def words(path: Path, address: int, count: int) -> list[int]:
    data = path.read_bytes()
    return list(struct.unpack_from(f"<{count}I", data, address - BASE))


def main() -> None:
    for label, path in (("a7s", A7S), ("a6000", A6000), ("dfe", DFE)):
        print(f"{label}.sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
    modes = words(A7S, 0x43FEE370, 34)
    print("imx235_modes=" + ",".join(f"{value:#x}" for value in modes))
    print("imx235_special_indices=" + repr([(i, v) for i, v in enumerate(modes) if v in {0x4E, 0x4F, 0x50, 0x51}]))
    print("silent_converter_table=" + repr(words(A7S, 0x43BC1658, 2)))
    print("dfe_vectors=" + repr(list(struct.unpack_from("<8I", DFE.read_bytes(), 0))))


if __name__ == "__main__":
    main()
