#!/usr/bin/env python3
"""S311: the A6000's own +0x00/+0x02 writers and their presence in the A7S."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("config.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

WRITERS = [
    (0x43833FF8, "state+0x02", ["0x4383415a", "0x4383418a"]),
    (0x4383ACE0, "state+0x02", ["0x4383afd0"]),
    (0x4383B2DC, "state+0x02", ["0x4383b316"]),
    (0x4383ABEC, "state+0x00", ["0x4383ac90"]),
]


def direct_callers(blob, target):
    out = []
    for a in range(0x43541000, 0x43D00000, 2):
        off = a - BASE
        if off + 4 > len(blob):
            break
        hw = blob[off] | (blob[off + 1] << 8)
        if (hw & 0xF800) != 0xF000:
            continue
        i = next(MD.disasm(blob[off:off + 4], a), None)
        if i and i.mnemonic in ("bl", "blx", "b", "b.w") and i.op_str == f"#0x{target:x}":
            out.append(f"0x{a:08x}")
    return out


def main():
    a6, a7 = A6.read_bytes(), A7.read_bytes()
    rows = []
    for f, field, sites in WRITERS:
        head = a6[f - BASE:f - BASE + 24]
        rows.append({
            "function": f"0x{f:08x}", "field": field,
            "head_hex": head.hex(),
            "a7s_head_hits": a7.count(head),
            "write_sites": sites,
            "callers": direct_callers(a6, f),
        })
    data = {
        "milestone": "S311",
        "title": "ruta de configuración propia de la A6000 (writers de +0x00/+0x02)",
        "firmware": {"a6000": hashlib.sha256(a6).hexdigest(),
                     "a7s": hashlib.sha256(a7).hexdigest()},
        "base": f"0x{BASE:08x}",
        "writers": rows,
        "scope_limit": "Presencia por 24 B de prólogo y callers directos; no prueba "
                       "equivalencia funcional entre las rutas de las dos cámaras.",
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    for r in rows:
        print(r["function"], r["field"], "A7S hits:", r["a7s_head_hits"],
              "callers:", len(r["callers"]))


if __name__ == "__main__":
    main()
