"""R36: invariantes TPZL que exige la ruta hardware (Loader3 → ARM7 → LDEC) y qué lecturas del arranque tocan los bloques anómalos del 3.25.

Dos comprobaciones independientes por imagen: un parser propio de registros (aquí) y
``scripts.e25_27.tpzl.hardware_violations``; deben coincidir.  La descompresión para el
mapa FAT usa ``fwtool``.  Solo lectura.  Salida: r36-ldec-records.json
"""

from __future__ import annotations

import json
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "references" / "fwtool")]

from scripts.e25_27 import tpzl

INSTALLED = ROOT / "analysis/e25-27/artifacts/nflasha3.integrated.bin"
OFFICIAL = (
    ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3"
)
LENGTHS = list(range(3, 17)) + [32, 64]
# RAMCFG (R14 §5): archivos de la partición 3 en el orden de carga del modo normal.
RAMCFG_P3 = [
    ("SABIN      ", "IDT_CAM BIN"),
    ("SABIN      ", "SA_DFDETBIN"),
    (None, "AV-CAM  BIN"),
    (None, "INITRD  IMG"),
    (None, "VMLINUX BIN"),
]


def records(block: bytes, target: int) -> list[tuple[str, int]]:
    """(tipo, salida) de cada registro hasta completar `target` bytes."""
    out: list[tuple[str, int]] = []
    p = 0
    while sum(n for _, n in out) < target:
        kind = block[p]
        p += 1
        if kind == 0x0F:
            n = struct.unpack_from("<H", block, p + 1)[0]
            out.append(("raw", n))
            p += 3 + n
            continue
        if kind != 0xF0:
            raise ValueError(f"tipo {kind:#x}")
        n = 0
        while True:
            flags = block[p]
            p += 1
            end = False
            for bit in range(8):
                if not flags >> bit & 1:
                    n += 1
                    p += 1
                    continue
                b0, b1 = block[p], block[p + 1]
                p += 2
                if (b0 & 0x0F) << 8 | b1 == 0:
                    end = True
                    break
                n += LENGTHS[b0 >> 4]
            if end:
                break
        out.append(("lz", n))
    return out


def audit(path: Path) -> dict:
    data = path.read_bytes()
    _, shift, toc, size = struct.unpack_from("<4sIII", data)
    entries = [struct.unpack_from("<II", data, toc + i) for i in range(0, size, 8)]
    residues: Counter[int] = Counter()
    shapes: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    for off, sz in entries:
        residues[off & 0x1FF] += 1
        recs = records(data[off : off + sz], 1 << shift)
        shapes[f"{len(recs)}x{sorted({n for _, n in recs})}"] += 1
        kinds.update(k for k, _ in recs)
    violations = tpzl.hardware_violations(tpzl.TpzlImage.parse(data))
    own_bad = (
        len(entries)
        - residues[0]
        + sum(v for k, v in shapes.items() if k != "16x[4096]")
    )
    tool_bad = sum("residuo" in v or "registros" in v for v in violations)
    return {
        "archivo": str(path.relative_to(ROOT)),
        "bloques": len(entries),
        "residuos": {str(k): v for k, v in sorted(residues.items())},
        "forma_bloques": dict(shapes),
        "registros": dict(kinds),
        "violaciones_hardware": len(violations),
        "coinciden_parsers": own_bad == tool_bad,
    }


def fat_reads(path: Path) -> list[dict]:
    """Bloques TPZL que tocan el montaje de la partición 3 y los 5 archivos RAMCFG."""
    from fwtool.archive import lzpt  # type: ignore[import-not-found]

    with path.open("rb") as f:
        vol = next(lzpt.readLzpt(f)).contents.read()
    data = path.read_bytes()
    _, shift, toc, size = struct.unpack_from("<4sIII", data)
    entries = [struct.unpack_from("<II", data, toc + i) for i in range(0, size, 8)]
    bps, spc, rsv, nfat, nroot, _t, _m, spf = struct.unpack_from("<HBHBHHBH", vol, 11)
    clus, fat_off = bps * spc, rsv * bps
    root_off = fat_off + nfat * spf * bps
    data_off = root_off + nroot * 32
    fat = vol[fat_off : fat_off + spf * bps]

    def chain(c: int) -> list[int]:
        out = []
        while 2 <= c < 0xFF8:
            out.append(c)
            v = struct.unpack_from("<H", fat, c * 3 // 2)[0]
            c = v >> 4 if c & 1 else v & 0xFFF
        return out

    def span(c: int) -> list[tuple[int, int]]:
        return [
            (data_off + (x - 2) * clus, data_off + (x - 1) * clus) for x in chain(c)
        ]

    def lookup(raw: bytes, name: str) -> int:
        for i in range(0, len(raw), 32):
            if raw[i : i + 11].decode("ascii", "replace") == name:
                return struct.unpack_from("<H", raw, i + 26)[0]
        raise KeyError(name)

    root = vol[root_off:data_off]
    sabin = lookup(root, "SABIN      ")
    sabin_raw = b"".join(vol[lo:hi] for lo, hi in span(sabin))
    reads = [("PBR/FAT/raíz", [(0, data_off)]), ("\\sabin", span(sabin))]
    for parent, name in RAMCFG_P3:
        reads.append((name, span(lookup(sabin_raw if parent else root, name))))
    bs, out = 1 << shift, []
    for label, rng in reads:
        blocks = sorted(
            {b for lo, hi in rng for b in range(lo // bs, (hi - 1) // bs + 1)}
        )
        one_record = [
            b
            for b in blocks
            if len(records(data[entries[b][0] : sum(entries[b])], bs)) != bs // 4096
        ]
        out.append(
            {
                "lectura": label.strip(),
                "bloques": len(blocks),
                "primer_bloque": blocks[0],
                "con_residuo": sum(1 for b in blocks if entries[b][0] & 0x1FF),
                "sin_16_registros": one_record,
            }
        )
    return out


def main() -> None:
    images = sorted(
        p
        for base in (ROOT / "firmware", ROOT / "analysis/camera-dumps")
        if base.is_dir()
        for p in base.rglob("*nflasha*")
        if p.is_file() and "_unpacked" not in p.name and p.open("rb").read(4) == b"TPZL"
    )
    result: dict[str, Any] = {"sony": [audit(p) for p in images]}
    if INSTALLED.is_file():
        result["instalado_325"] = audit(INSTALLED)
        result["lecturas_arranque_325"] = fat_reads(INSTALLED)
    if OFFICIAL.is_file():
        result["lecturas_arranque_321"] = fat_reads(OFFICIAL)
    sony = result["sony"]
    result["resumen_sony"] = {
        "imagenes": len(sony),
        "bloques": sum(a["bloques"] for a in sony),
        "registros": sum(sum(a["registros"].values()) for a in sony),
        "todas_16x4096_y_residuo_0": all(
            a["forma_bloques"] == {"16x[4096]": a["bloques"]}
            and a["residuos"] == {"0": a["bloques"]}
            for a in sony
        ),
        "coinciden_parsers": all(a["coinciden_parsers"] for a in sony),
    }
    out = Path(__file__).with_name("r36-ldec-records.json")
    out.write_text(
        json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["resumen_sony"], ensure_ascii=False))
    print(json.dumps(result.get("instalado_325"), ensure_ascii=False))
    for row in result.get("lecturas_arranque_325", []):
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
