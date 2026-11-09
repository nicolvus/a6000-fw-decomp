"""Emula el despachador LIRO real de `av-cam.bin` (0x438052d8) y sus manejadores (`+0x238` Silent, `+0x210` EFCS)."""

from __future__ import annotations

from pathlib import Path

from .armlib import Machine

B = 0x43541000
G = 0x43EDF684


class AvCam:
    def __init__(self, binpath: Path) -> None:
        self.m = Machine()
        m = self.m
        m.automap = True
        data = binpath.read_bytes()
        m.uc.mem_map(B, (len(data) + 0xFFF) & ~0xFFF)
        m.uc.mem_write(B, data)
        m.overrides[0x4375DCD4 & ~1] = lambda mm: (
            0
        )  # post-proceso (aviso) tras el manejador

    def state(self, off: int) -> int:
        return self.m.u32(G + off)

    def deliver(self, pkt: bytes) -> None:
        buf = self.m.alloc(16)
        self.m.uc.mem_write(buf, pkt.ljust(16, b"\0"))
        self.m.call(0x438052D8, buf, 0)
