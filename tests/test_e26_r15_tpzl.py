"""E26-R15 — pruebas offline del validador TPZL de Loader3 y de c01f2282. Solo leen imágenes existentes."""

import importlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))

T = importlib.import_module("r15_tpzl_loader3")
M = importlib.import_module("r15-mode-table")


def _img(
    entries: list[tuple[int, int]],
    shift: int = 16,
    toc: int = 0x18,
    magic: bytes = b"TPZL",
) -> bytes:
    body = struct.pack("<4sIII", magic, shift, toc, len(entries) * 8) + bytes(8)
    body += b"".join(struct.pack("<II", o, s) for o, s in entries)
    return body.ljust(max(o + s for o, s in entries) + 512, b"\xff")


def test_aligned_and_residue_images_are_accepted():
    ok = T.audit(_img([(1024, 512), (1536, 700)]))
    assert ok["ok"] and ok["residues"] == {0: 2} and not ok["warnings"]
    res = T.audit(_img([(1024, 512), (1536 + 256, 700)]))
    assert res["ok"] and res["residues"] == {0: 1, 256: 1} and res["max_sectors"] == 2
    assert res["warnings"]


def test_header_rejections_match_c01fe4ec():
    assert not T.audit(_img([(512, 512)], magic=b"LZPT"))["ok"]
    assert not T.audit(_img([(512, 512)], shift=0x12))["ok"]
    assert T.audit(_img([(512, 512)], shift=0x11))["ok"]
    assert not T.audit(_img([(512, 512)], toc=0x1A))["ok"]
    assert not T.audit(b"TPZL" + bytes(8))["ok"]


def test_read_past_device_is_rejected():
    assert not T.audit(_img([(1024, 4096)]), partition_bytes=4096)["ok"]


def test_real_images_pass_loader3_checks():
    for name, path in {
        "oficial": ROOT
        / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3",
        "integrada": ROOT / "analysis/e25-27/artifacts/nflasha3.integrated.bin",
    }.items():
        if not path.exists():
            continue
        r = T.audit(path.read_bytes(), partition_bytes=30 << 20)
        assert (
            r["ok"] and r["entries"] == 369 and r["decompressed_bytes"] == 24182784
        ), name
    if (ROOT / "analysis/e25-27/artifacts/nflasha3.integrated.bin").exists():
        assert r["residues"] == {0: 10, 256: 359}


def test_c01f2282_never_skips_with_known_backups():
    assert M.skip_possible(1) and M.skip_possible(2)
    assert not M.skip_possible(0x80021048)
