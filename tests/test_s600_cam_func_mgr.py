"""Test S600: [CAM_FUNC_MGR] module exclusivity to A6000 fw3.21.

VERIFICADO: 36 trace strings with prefix [CAM_FUNC_MGR] exist in A6000 fw3.21.
VERIFICADO: 0 such strings in A7S fw3.20.
VERIFICADO: 0 such strings in A6300 fw2.01.
CONCLUSION: Module is exclusive to A6000 fw3.21.
"""

import subprocess

FIRMWARES = {
    "A6000_fw321": "/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A7S_fw320": "/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300_fw201": "/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}

PATTERN = b"[CAM_FUNC_MGR]"


def count_pattern(bin_path: str) -> int:
    result = subprocess.run(["strings", "-a", bin_path], check=False, capture_output=True)
    return result.stdout.count(PATTERN)


def test_exclusivity():
    counts = {}
    for name, path in FIRMWARES.items():
        counts[name] = count_pattern(path)
        print(f"{name}: {counts[name]} occurrences of {PATTERN.decode()}")

    # VERIFICADO: A6000 has 36 unique (REA) / 43 total (strings), others have 0
    assert counts["A6000_fw321"] >= 36, f"A6000 should have >=36, got {counts['A6000_fw321']}"
    assert counts["A7S_fw320"] == 0, f"A7S should have 0, got {counts['A7S_fw320']}"
    assert counts["A6300_fw201"] == 0, f"A6300 should have 0, got {counts['A6300_fw201']}"

    print("\n✓ VERIFICADO: [CAM_FUNC_MGR] is exclusive to A6000 fw3.21")


if __name__ == "__main__":
    test_exclusivity()