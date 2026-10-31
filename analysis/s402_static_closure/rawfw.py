"""Variante de fw.Lib para imágenes crudas av-cam (base 0x43541000, Thumb): sin ELF, PLT ni GOT con nombres."""

import struct
from pathlib import Path

import s402_fw as fw

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
IMAGES = {"A6000": ROOT / "analysis/rea-independent/input/av-cam.bin",
          "A7S": ROOT / "analysis/rea-independent/input/av-cam-a7s.bin"}


class RawElf:
    def __init__(self, path: Path):
        self.data = path.read_bytes()
        self.sections = {".got": (0, 0, 0, 0, 0, 0), ".text": (BASE, BASE, len(self.data), BASE, 0, len(self.data))}

    def read(self, va: int, size: int) -> bytes:
        return self.data[va - BASE:va - BASE + size]

    def u32(self, va: int) -> int:
        return struct.unpack_from("<I", self.data, va - BASE)[0]

    def offset(self, va: int) -> int:
        return va - BASE


class RawLib(fw.Lib):
    def __init__(self, model: str, limit: int = 0x4000):
        self.model = model
        self.e = RawElf(IMAGES[model])  # type: ignore[assignment]
        self.plt, self.syms, self.gotmap, self.gotbase, self.limit = {}, {}, {}, 0, limit
        self.starts = []

    def fstart(self, va: int) -> int:
        return va

    def fend(self, va: int) -> int:
        return va + self.limit

    def section_of(self, va: int):
        return ".text" if BASE <= va < BASE + len(self.e.data) else None
