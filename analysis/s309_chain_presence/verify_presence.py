#!/usr/bin/env python3
"""S309: re-check every chain signature against both blobs."""
import hashlib
import json
from pathlib import Path

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = Path(__file__).with_name("presence.json")


def main():
    a6, a7 = A6.read_bytes(), A7.read_bytes()
    d = json.loads(DATA.read_text())
    assert d["firmware"]["a6000"] == hashlib.sha256(a6).hexdigest()
    assert d["firmware"]["a7s"] == hashlib.sha256(a7).hexdigest()
    for row in d["chain"]:
        addr = int(row["entry"], 16)
        raw = a7[addr - BASE:addr - BASE + 24]
        assert raw.hex() == row["head_hex"], row["label"]
        assert a6.count(raw) == row["a6000_hits"] == 0, row["label"]
    assert len(d["chain"]) == 7
    print(f"OK: {len(d['chain'])} funciones de la cadena con 0 coincidencias en A6000")


if __name__ == "__main__":
    main()
