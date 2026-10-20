"""S37: validate preserved inputs and exact exported DMM instructions."""

import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
EXPECTED = "514e14116caa1d15d75bd56641dabfe815f620b6208008929c44d8d70386011d"
ORIGINAL = ROOT / (
    "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
    "nflasha15_unpacked_unpacked/lib/libmprctrl.so"
)


def elf_bytes(data: bytes, address: int, size: int = 4) -> bytes:
    """Translate an ELF VA through PT_LOAD, independently of Ghidra."""
    header = struct.unpack_from("<16sHHIIIIIHHHHHH", data)
    for index in range(header[10]):
        segment = struct.unpack_from("<IIIIIIII", data, header[5] + index * header[9])
        kind, offset, base, _, length, _, _, _ = segment
        if kind == 1 and base <= address and address + size <= base + length:
            return data[offset + address - base:offset + address - base + size]
    raise AssertionError(f"Unmapped ELF address {address:#x}")


def main() -> None:
    """Check artifacts without executing any firmware code."""
    for path in (ORIGINAL, OUT / "s37-input/libmprctrl.so"):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED, path
    assert (OUT / "s37-input/libmprctrl.so").stat().st_mode & 0o222 == 0
    for manifest in ("s37-avcam-before.sha256", "s37-avcam-rep-before.sha256"):
        for line in (OUT / manifest).read_text().splitlines():
            digest, name = line.split(maxsplit=1)
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    data = json.loads((OUT / "s37-library.json").read_text())
    assert data["executable_sha256"] == EXPECTED
    assert data["image_base"] == "00010000"
    functions = {f["entry"]: f for f in data["functions"]}
    for entry in ("0002bc9c", "0002bf54", "0002b628", "0002b028", "0002b58c", "0002b5e4",
                  "0002b3fc", "0002afe8", "0002ada8", "0002c620", "0002c638"):
        function = functions[entry]
        assert function["completed"] and not function["thunk"]
        assert function["listing"] and function.get("pseudo_code"), entry
    for entry, offset in (("0002c620", "0x10"), ("0002c638", "0x14")):
        function = functions[entry]
        assert "DmmAccessPLA::" in function["name"]
        assert offset in function["pseudo_code"]
        assert any("ldr" in ins and offset in ins for ins in function["listing"])
    code = functions["0002b028"]["pseudo_code"]
    assert "osal_valloc_msg_wait" in code and "0x18" in code
    assert "*psVar3 = 2;" in code and "psVar3[1] = param_2;" in code
    assert "memcpy(__dest,psVar3,__size)" in code
    assert "param_1 + -4" in functions["0002a9c2"]["pseudo_code"]
    assert "param_1,4,2" in functions["0002afe8"]["pseudo_code"]
    binary = ORIGINAL.read_bytes()
    for address in (0x1B310, 0x1B8B0, 0x1AF84):
        assert struct.unpack("<I", elf_bytes(binary, address))[0] == 0x61003C
    displacement = struct.unpack("<i", elf_bytes(binary, 0x1AC14))[0]
    assert displacement + 0x1AB9C == 0x3DA5C
    assert struct.unpack("<IIHH", elf_bytes(binary, 0x3DA5C, 12)) == (0x8125B, 3, 0, 0)
    assert elf_bytes(binary, 0x3DA5C + 22, 2) == b"\xff\xff"
    libobj = ORIGINAL.with_name("libObj.so")
    assert hashlib.sha256(libobj.read_bytes()).hexdigest() == (
        "8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a"
    )
    relocations = subprocess.check_output(["readelf", "-rW", str(libobj)], text=True)
    assert any("0102d024" in line and "_ZN9DmmAccess15DmmCloseAndFreeEt" in line
               for line in relocations.splitlines())
    dependencies = subprocess.check_output(["readelf", "-d", str(libobj)], text=True)
    assert "[libmprctrl.so]" in dependencies
    findings = json.loads((OUT / "s37-findings.json").read_text())
    assert findings["physical_yc"] == "NO_VERIFICADO"
    assert findings["byte_identical_s33"] is False
    print("PASS: SHA original/copy, read-only copy, av-cam intact, complete exports,")
    print("      extent loads, OSAL layout, close/free and bounded conclusions.")


if __name__ == "__main__":
    main()
