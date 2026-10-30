"""E26-R15 — c01f2282/c01f16b0 sobre las 55 copias BK4 y tabla modo -> archivos de RAMCFG.

c01f16b0 devuelve el u32 del elemento Backup 0xfa0033 (0 si falta). c01f2282 solo devuelve 1 (omitir
la entrada, «CFG:skip») si ese valor es 1 o 2, [0xc00e0004] != 6 y c01f5f18() ([0xc00e0060+0x24]) != 0.
Solo lee; la cámara no se toca.
"""

import importlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
r14 = importlib.import_module("r14-ramcfg-bos-fat")
B = importlib.import_module("r14_backup")

MODES = {
    0x1000000: "arranque normal por defecto / HotOFF",
    0x4000000: "arranque normal con modo de arranque 0xa/0xb / Normal load OFF",
    0x2000000: "modo 2",
    0x0100000: "Early load (bit 20)",
}


def sel_value(bk: "B.BK4") -> int:
    """u32 devuelto por c01f16b0 (0 si el elemento falta o es < 4 B)."""
    raw = bk.read(0xFA0033)
    return struct.unpack_from("<I", raw)[0] if raw is not None and len(raw) >= 4 else 0


def skip_possible(value: int) -> bool:
    return value in (1, 2)


def main() -> None:
    copies = {**r14.backup_copies(), **r14.package_backups()}
    values = Counter()
    for data in copies.values():
        values[f"{sel_value(B.BK4(data)):#x}"] += 1
    cfg = B.ramcfg(B.BK4(next(iter(copies.values()))))
    table = {
        f"{m:#x}": {"nombre": n, "archivos": [e.path for e in B.selected(cfg, m)]}
        for m, n in MODES.items()
    }
    json.dump(
        {
            "copias": len(copies),
            "valor_0xfa0033": dict(values),
            "omision_posible": any(skip_possible(int(v, 16)) for v in values),
            "tabla": table,
        },
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    main()
