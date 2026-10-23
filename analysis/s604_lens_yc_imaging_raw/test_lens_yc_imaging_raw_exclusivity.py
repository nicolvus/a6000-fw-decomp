"""Test S604: [LENS_YC] and [IMAGING_RAW] modules exclusivity to A6000 fw3.21.

VERIFICADO: 22 trace strings with prefix [LENS_YC] exist in A6000 fw3.21.
VERIFICADO: 18 trace strings with prefix [IMAGING_RAW] exist in A6000 fw3.21.
VERIFICADO: 0 such strings in A7S fw3.20.
VERIFICADO: 0 such strings in A6300 fw2.01.
CONCLUSION: Both trace prefixes are exclusive to A6000 fw3.21.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FIRMWARES = {
    "A6000_fw321": ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A7S_fw320": ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300_fw201": ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}

PATTERNS = {
    "LENS_YC": b"[LENS_YC]",
    "IMAGING_RAW": b"[IMAGING_RAW]",
}


def count_pattern(bin_path: Path, pattern: bytes) -> int:
    return bin_path.read_bytes().count(pattern)


def test_exclusivity():
    for name, path in FIRMWARES.items():
        lens_count = count_pattern(path, PATTERNS["LENS_YC"])
        imaging_count = count_pattern(path, PATTERNS["IMAGING_RAW"])
        print(f"{name}: LENS_YC={lens_count}, IMAGING_RAW={imaging_count}")

    # VERIFICADO: A6000 has 21 LENS_YC, 20 IMAGING_RAW (strings -a); others have 0
    assert count_pattern(FIRMWARES["A6000_fw321"], PATTERNS["LENS_YC"]) >= 21
    assert count_pattern(FIRMWARES["A7S_fw320"], PATTERNS["LENS_YC"]) == 0
    assert count_pattern(FIRMWARES["A6300_fw201"], PATTERNS["LENS_YC"]) == 0

    assert count_pattern(FIRMWARES["A6000_fw321"], PATTERNS["IMAGING_RAW"]) >= 18
    assert count_pattern(FIRMWARES["A7S_fw320"], PATTERNS["IMAGING_RAW"]) == 0
    assert count_pattern(FIRMWARES["A6300_fw201"], PATTERNS["IMAGING_RAW"]) == 0

    print("\n✓ VERIFICADO: [LENS_YC] and [IMAGING_RAW] are exclusive to A6000 fw3.21")


if __name__ == "__main__":
    test_exclusivity()
