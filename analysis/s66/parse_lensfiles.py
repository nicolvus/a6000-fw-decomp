"""S62: parser de VX91xx_lensfile.bin.

Parseo por secciones: cabecera 'LF' con secciones encadenadas por magic u16
(no se descarta una lista de secciones al estilo TLV). Uso:
    parse_lensfiles.py [PATH...]        # por defecto los 18 de A6000 fw321
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LENSDIR = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0800_appli/lens"


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def entropy_chunk(b):
    if not b:
        return 0.0
    counts = [0] * 256
    for x in b:
        counts[x] += 1
    import math
    e = 0.0
    for c in counts:
        if c:
            p = c / len(b)
            e -= p * math.log2(p)
    return round(e, 2)


def parse(path):
    b = path.read_bytes()
    r = {"path": str(path.relative_to(ROOT)), "name": path.name, "size": len(b)}
    r["sha256"] = hashlib.sha256(b).hexdigest()
    # Cabecera dichiarada:
    hdr = {}
    hdr["magic"] = b[0:2].decode("latin1")             # 'LF'
    hdr["u2"] = u16(b, 2)                              # 0x0010
    hdr["file_size"] = u32(b, 6)
    hdr["u10"] = u16(b, 10)                            # 0x000b
    hdr["lens_id"] = u16(b, 12)                        # 0x9101...
    hdr["u14"] = u16(b, 14)
    hdr["u16_raw"] = b[0x10:0x20].hex()
    r["header"] = hdr
    sections = []
    off = 0x10
    while off + 8 <= len(b):
        sec_magic = b[off:off + 2].decode("latin1", "replace")
        sec_kind = u16(b, off + 2)
        sec_len = u32(b, off + 4) if off + 8 <= len(b) else 0
        # heuristica: magic printable, len plausible
        ok = sec_magic.isprintable() and sec_len <= len(b) and sec_len > 0
        sections.append({
            "off": off, "magic": sec_magic, "kind": sec_kind,
            "len_field": sec_len, "plausible": ok,
            "tail16": b[off:off + 16].hex(),
        })
        if ok:
            off = off + 8 + sec_len
        else:
            break
    r["sections_try"] = sections

    return r


def main():
    paths = [Path(a) for a in sys.argv[1:]] or sorted(LENSDIR.glob("VX*_lensfile.bin"))
    for p in paths:
        r = parse(p)
        print(f"== {r['name']} size={r['size']} lens_id=0x{r['header']['lens_id']:04x} "
              f"sha256={r['sha256'][:16]}")
        h = r["header"]
        print(f"   hdr: magic={h['magic']!r} u2={h['u2']:#x} fsize={h['file_size']} "
              f"u10={h['u10']:#x} u14={h['u14']:#x} b0x10={h['u16_raw']}")
        for s in r["sections_try"][:8]:
            print(f"   sec@{s['off']:#x} {s['magic']!r} kind={s['kind']:#06x} "
                  f"len={s['len_field']} ok={s['plausible']} {s['tail16']}")


if __name__ == "__main__":
    main()
