"""R16: características del flujo LZ77 por bloque TPZL (qué construcciones usa cada imagen). Solo lectura.

Recorre los tokens como `scripts.e25_27.tpzl._inflate_segment` y cuenta: grupos con flags==0 (8 literales),
grupos mixtos, tokens de copia, terminadores (distancia 0), segmentos, tipo de segmento (0xF0/0x0F).
"""

from __future__ import annotations

import json
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIG = (
    ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3"
)
INTEG = ROOT / "analysis/e25-27/artifacts/nflasha3.integrated.bin"


def walk(block: bytes) -> Counter:
    c: Counter = Counter()
    pos, out = 0, 0
    while out < 65536 and pos < len(block):
        kind = block[pos]
        pos += 1
        c["seg"] += 1
        if kind == 0x0F:
            size = struct.unpack_from("<H", block, pos + 1)[0]
            pos += 3 + size
            out += size
            c["raw_seg"] += 1
            continue
        if kind != 0xF0:
            c["unknown_kind"] += 1
            break
        while True:
            flags = block[pos]
            pos += 1
            if flags == 0:
                c["flags0_groups"] += 1
                pos += 8
                out += 8
                continue
            c["mixed_groups"] += 1
            end = False
            for bit in range(8):
                if not (flags >> bit) & 1:
                    pos += 1
                    out += 1
                    continue
                b0, b1 = block[pos], block[pos + 1]
                pos += 2
                dist = ((b0 & 0xF) << 8) | b1
                if dist == 0:
                    c["terminators"] += 1
                    end = True
                    break
                c["copies"] += 1
                out += [*range(3, 17), 32, 64][b0 >> 4]
            if end:
                break
    c["bytes_consumed"] = pos
    c["bytes_out"] = out
    return c


def seg_sizes(block: bytes) -> list[tuple[str, int]]:
    """Tamaño de salida de cada segmento del bloque: ('lz'|'raw', bytes)."""
    sizes, pos, out = [], 0, 0
    while out < 65536 and pos < len(block):
        kind = block[pos]
        pos += 1
        if kind == 0x0F:
            size = struct.unpack_from("<H", block, pos + 1)[0]
            pos += 3 + size
            out += size
            sizes.append(("raw", size))
            continue
        if kind != 0xF0:
            sizes.append(("bad", kind))
            break
        cur = 0
        while True:
            flags = block[pos]
            pos += 1
            if flags == 0:
                pos += 8
                cur += 8
                continue
            end = False
            for bit in range(8):
                if not (flags >> bit) & 1:
                    pos += 1
                    cur += 1
                    continue
                b0, b1 = block[pos], block[pos + 1]
                pos += 2
                if (((b0 & 0xF) << 8) | b1) == 0:
                    end = True
                    break
                cur += [*range(3, 17), 32, 64][b0 >> 4]
            if end:
                break
        out += cur
        sizes.append(("lz", cur))
    return sizes


def segment_structure(path: Path) -> dict:
    """Segmentos por bloque y tamaños de segmento de una imagen TPZL."""
    d = path.read_bytes()
    _, _, toc, tsize = struct.unpack_from("<4sIII", d, 0)
    per: Counter = Counter()
    sizes: Counter = Counter()
    for i in range(tsize // 8):
        off, sz = struct.unpack_from("<II", d, toc + 8 * i)
        segs = seg_sizes(d[off : off + sz])
        per[len(segs)] += 1
        sizes.update(f"{t}:{n}" for t, n in segs)
    return {"segmentos_por_bloque": dict(per), "tamanos_segmento": dict(sizes)}


CORPUS = {
    "orig321": ORIG,
    "a7s320": ROOT
    / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3",
    "a6300": ROOT
    / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3",
    "cam_nflasha7": ROOT / "analysis/camera-dumps/nand-20261020/dev_nflasha7.bin",
    "cam_nflasha15": ROOT / "analysis/camera-dumps/nand-20261020/dev_nflasha15.bin",
    "integ325": INTEG,
}


def image_stats(path: Path) -> list[Counter]:
    d = path.read_bytes()
    _, _, toc, tsize = struct.unpack_from("<4sIII", d, 0)
    rows = []
    for i in range(tsize // 8):
        off, sz = struct.unpack_from("<II", d, toc + 8 * i)
        rows.append(walk(d[off : off + sz]))
    return rows


if __name__ == "__main__":
    o, n = image_stats(ORIG), image_stats(INTEG)
    tot: Counter[str] = Counter()
    for r in o:
        tot.update(
            {k: v for k, v in r.items() if k not in ("bytes_consumed", "bytes_out")}
        )
    diff = [i for i, (a, b) in enumerate(zip(o, n)) if a != b]
    res = {
        "orig_totales": dict(tot),
        "bloques_distintos": diff,
        "orig_bloques_0_48_57": {str(i): dict(o[i]) for i in (0, 48, 57)},
        "integ_bloques_0_48_57": {str(i): dict(n[i]) for i in (0, 48, 57)},
        "orig_bloques_con_flags0": sum(1 for r in o if r["flags0_groups"]),
        "orig_max_flags0_en_bloque": max(r["flags0_groups"] for r in o),
        "orig_bloques_con_terminadores_multiples": sum(
            1 for r in o if r["terminators"] > 1
        ),
    }
    (Path(__file__).parent / "r16-lz-features.json").write_text(
        json.dumps(res, indent=1)
    )
    print(json.dumps(res, indent=1))
    seg = {k: segment_structure(p) for k, p in CORPUS.items() if p.is_file()}
    (Path(__file__).parent / "r16-segment-structure.json").write_text(
        json.dumps(seg, indent=1)
    )
    print(json.dumps(seg, indent=1))
