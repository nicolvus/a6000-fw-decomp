"""Test S601: [CAM_SCALAR] module exclusivity to A6000 fw3.21.

VERIFICADO: 34 trace strings with prefix [CAM_SCALAR] exist in A6000 fw3.21.
VERIFICADO: 0 such strings in A7S fw3.20.
VERIFICADO: 0 such strings in A6300 fw2.01.
CONCLUSION: Trace prefix is exclusive to A6000 fw3.21.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FIRMWARES = {
    "A6000_fw321": ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A7S_fw320": ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300_fw201": ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}

PATTERN = b"[CAM_SCALAR]"


def count_pattern(bin_path: Path) -> int:
    return bin_path.read_bytes().count(PATTERN)


def test_exclusivity():
    counts = {}
    for name, path in FIRMWARES.items():
        counts[name] = count_pattern(path)
        print(f"{name}: {counts[name]} occurrences of {PATTERN.decode()}")

    # VERIFICADO: A6000 has 34, others have 0
    assert counts["A6000_fw321"] >= 34, f"A6000 should have >=34, got {counts['A6000_fw321']}"
    assert counts["A7S_fw320"] == 0, f"A7S should have 0, got {counts['A7S_fw320']}"
    assert counts["A6300_fw201"] == 0, f"A6300 should have 0, got {counts['A6300_fw201']}"

    print("\n✓ VERIFICADO: [CAM_SCALAR] is exclusive to A6000 fw3.21")


if __name__ == "__main__":
    test_exclusivity()
