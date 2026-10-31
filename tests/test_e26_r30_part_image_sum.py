"""E26-R30 — part_image.sum lista nodos de dispositivo y su CRC32 cubre los primeros `tamaño` bytes.

Usa archivos locales no publicados; se omite si faltan. No prueba el contenido físico de la NAND.
"""

import tarfile
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FW321 = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked"
ART = ROOT / "analysis/e25-27/artifacts"
DUMP = ROOT / "analysis/camera-dumps/nand-20261020/dev_nflasha3.bin"
NEEDED = [FW321 / "0701_part_image_sum/part_image.sum", FW321 / "0700_part_image/dev/nflasha3",
          ART / "firmware.integrated.tar", ART / "nflasha3.integrated.bin", DUMP]
pytestmark = pytest.mark.skipif(not all(p.is_file() for p in NEEDED), reason="artefactos locales ausentes")


def _entries(text: str) -> dict[str, tuple[int, int]]:
    rows = (line.split(",") for line in text.splitlines() if line.startswith("0,"))
    return {r[10]: (int(r[1], 16), int(r[2], 16)) for r in rows}


def _crc(path: Path, size: int) -> int:
    with path.open("rb") as f:
        return zlib.crc32(f.read(size))


def _sum_325() -> str:
    with tarfile.open(ART / "firmware.integrated.tar") as t:
        member = t.extractfile("0701_part_image_sum/part_image.sum")
        assert member is not None
        return member.read().decode()


def test_paths_are_device_nodes_relative_to_root():
    for text in (NEEDED[0].read_text(), _sum_325()):
        assert {p for p in _entries(text)} == {f"dev/nflasha{n}" for n in (3, 5, 7, 15, 16)}


def test_crc_matches_images_and_real_device_dump():
    crc321, size321 = _entries(NEEDED[0].read_text())["dev/nflasha3"]
    crc325, size325 = _entries(_sum_325())["dev/nflasha3"]
    assert (crc321, size321) == (0x0C047870, 0x00AF4F10)
    assert (crc325, size325) == (0xF5E75C34, 0x00B09500)
    assert _crc(NEEDED[1], size321) == crc321
    assert _crc(NEEDED[3], size325) == crc325
    assert DUMP.stat().st_size > size321 and _crc(DUMP, size321) == crc321


def test_only_nflasha3_changed():
    old, new = _entries(NEEDED[0].read_text()), _entries(_sum_325())
    assert {k for k in old if old[k] != new[k]} == {"dev/nflasha3"}
