"""R16: estadísticas por bloque de TODAS las imágenes TPZL del repo (sectores por petición, tipo de bloque, residuo).

Sectores = (residuo + tamaño + 0x1ff) >> 9 (c01fdd8e). Solo lectura. Salida: r16-tpzl-corpus.json
"""

from __future__ import annotations

import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN = [
    ROOT / "firmware",
    ROOT / "analysis" / "camera-dumps",
    ROOT / "analysis" / "e25-27" / "artifacts",
]
SKIP = {".tar", ".dat", ".fdat", ".jpg", ".png"}


def stats(path: Path) -> dict | None:
    try:
        with path.open("rb") as f:
            head = f.read(0x18)
            if len(head) < 0x18 or head[:4] != b"TPZL":
                return None
            _, shift, toc, tsize = struct.unpack("<4sIII", head[:16])
            f.seek(toc)
            raw = f.read(tsize)
            data = path.read_bytes()
    except OSError:
        return None
    n = tsize // 8
    ents = [struct.unpack_from("<II", raw, 8 * i) for i in range(n)]
    sect: list[int] = []
    kinds: Counter[int] = Counter()
    res: Counter[int] = Counter()
    for off, sz in ents:
        r = off & 0x1FF
        res[r] += 1
        sect.append((r + sz + 0x1FF) >> 9)
        kinds[data[off] if off < len(data) else -1] += 1
    over = [i for i, s in enumerate(sect) if s > 128]
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "shift": shift,
        "entries": n,
        "max_sectors": max(sect),
        "max_comp_bytes": max(s for _, s in ents),
        "blocks_gt128_sectors": over,
        "kind_byte_counts": {hex(k): v for k, v in kinds.items()},
        "residues": dict(res),
    }


def main() -> list[dict]:
    out, seen = [], set()
    for base in SCAN:
        for p in base.rglob("*"):
            if (
                p.is_file()
                and p.suffix not in SKIP
                and p.stat().st_size > 0x1000
                and not p.is_symlink()
            ):
                s = stats(p)
                if s and s["sha256"] not in seen:
                    seen.add(s["sha256"])
                    out.append(s)
    return out


if __name__ == "__main__":
    rows = main()
    (Path(__file__).parent / "r16-tpzl-corpus.json").write_text(
        json.dumps(rows, indent=1)
    )
    for r in rows:
        print(
            r["path"][-70:],
            r["entries"],
            "maxsec",
            r["max_sectors"],
            "maxcomp",
            r["max_comp_bytes"],
            ">128:",
            len(r["blocks_gt128_sectors"]),
            "kinds",
            r["kind_byte_counts"],
            "res",
            r["residues"],
        )
