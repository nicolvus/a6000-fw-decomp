"""E26-R15 — validador offline de TPZL con las condiciones de Loader3 (bootloader.bin, 0xc01f0000).

Reproduce solo lo que el binario comprueba (no usa ``scripts.e25_27.tpzl``):

* registro, ``c01fe4ec``: magic ``TPZL`` (``c01fe500``), ``u32@4`` (shift) <= 0x11 (``c01fe518``),
  ``u32@8`` (TOC) y ``u32@0xc`` (tamaño del TOC) distintos de 0 y ``(a|b) & 3 == 0`` (``c01fe510``);
  entradas = tamaño/8 (``c01fe55a``).
* petición, ``c01fe006``/``c01fdd8e``: índice de bloque < entradas (``c01fe03a``); residuo = offset & 0x1ff,
  distinto de 0 solo emite un aviso (``c01fde00``–``c01fde06``, ``c01fdf70``–``c01fdf78``); sectores =
  (residuo + tamaño + 0x1ff) >> 9 desde ``offset >> 9`` (``c01fde1c``–``c01fde28``).

Solo lee; nunca escribe imágenes.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

MAGIC = b"TPZL"
MAX_SHIFT = 0x11
SECTOR = 512


@dataclass
class Check:
    ok: bool = True
    rejects: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def reject(self, why: str) -> None:
        self.ok = False
        self.rejects.append(why)


def audit(data: bytes, partition_bytes: int | None = None) -> dict:
    """Aplica las comprobaciones de Loader3; ``partition_bytes`` modela el límite del dispositivo."""
    c = Check()
    if len(data) < 0x18:
        c.reject("cabecera < 0x18 B (c01fe4fa lee 0x18)")
        return {"ok": False, "rejects": c.rejects}
    magic, shift, toc, toc_size = struct.unpack_from("<4sIII", data, 0)
    if magic != MAGIC:
        c.reject("magic != TPZL (c01fe504)")
    if shift > MAX_SHIFT:
        c.reject(f"shift {shift} > 0x11 (c01fe518)")
    if toc == 0 or toc_size == 0:
        c.reject("TOC u32@8 o tamaño u32@0xc a cero (c01fe508/c01fe50e)")
    if (toc | toc_size) & 3:
        c.reject("TOC o tamaño no múltiplo de 4 (c01fe510)")
    n = toc_size >> 3
    entries = []
    if c.ok:
        if toc + toc_size > len(data):
            c.reject("TOC fuera de la imagen (lectura c01fe538)")
        else:
            entries = [struct.unpack_from("<II", data, toc + 8 * i) for i in range(n)]
    residues: dict[int, int] = {}
    last_end = 0
    max_sectors = 0
    beyond = 0
    for off, size in entries:
        r = off & (SECTOR - 1)
        residues[r] = residues.get(r, 0) + 1
        sectors = (r + size + SECTOR - 1) >> 9
        max_sectors = max(max_sectors, sectors)
        end = ((off >> 9) + sectors) * SECTOR
        last_end = max(last_end, end)
        if partition_bytes is not None and end > partition_bytes:
            c.reject(
                f"lectura fuera del dispositivo: bloque con fin {end} > {partition_bytes}"
            )
        if size == 0:
            c.warnings.append("entrada de tamaño 0")
        if off + size > len(data):
            beyond += 1
    if residues.keys() - {0}:
        c.warnings.append("residuos != 0: Loader3 solo avisa (c01fdf72-c01fdf78)")
    return {
        "ok": c.ok,
        "rejects": c.rejects,
        "warnings": sorted(set(c.warnings)),
        "shift": shift,
        "entries": n,
        "residues": dict(sorted(residues.items())),
        "max_sectors": max_sectors,
        "last_read_end": last_end,
        "image_len": len(data),
        "blocks_ending_past_eof": beyond,
        "decompressed_bytes": n << shift,
    }


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    files = {
        "camara-3.21": root / "analysis/camera-dumps/nand-20261020/dev_nflasha3.bin",
        "oficial-3.21": root
        / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3",
        "integrada-3.25": root / "analysis/e25-27/artifacts/nflasha3.integrated.bin",
    }
    out = {}
    for name, path in files.items():
        raw = path.read_bytes()
        out[name] = {
            "sha256": hashlib.sha256(raw).hexdigest(),
            **audit(raw, partition_bytes=30 * 1024 * 1024),
        }
    json.dump(out, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
