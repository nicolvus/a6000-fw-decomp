"""Sondeo solo lectura: reutiliza ventanas S20 y verifica bytes con LLVM."""
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from rtti_vtables import Elf, recover, self_check

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib"


def main():
    name, *specs = sys.argv[1:]
    elf = Elf(str(LIB / name))
    before = hashlib.sha256(elf.d).hexdigest()
    rtti = recover(elf)
    self_check(elf, rtti)
    windows = {}
    reused = []
    for path in (ROOT / "analysis/session20/evidence").glob("codex-dcf-*.json"):
        data = json.loads(path.read_text())
        if Path(data.get("library", "")).name == name:
            windows.update(data.get("windows", {}))
    out = {"library": name, "sha256_before": before, "windows": {}, "reused": reused,
           "rtti": {c["name"]: {"bases": c["bases"], "vtables": [
               {"addr_point": v["addr_point"], "methods": v["methods"][:8]}
               for v in c["vtables"]]} for c in rtti["classes"].values()
                    if c["name"] in ("Recorder", "StillRecorder", "StillWriterFilter", "dcf_AVISequence", "dcf_Sequence")}}
    targets = {int(s[1:], 16) & ~1 for s in specs if s.startswith("@")}
    if targets:
        out["target_virtuals"] = {hex(t): rtti["methods_by_entry"].get(hex(t), []) for t in targets}
        out["target_relocations"] = {hex(t): [hex(a) for a, (v, _) in elf.rel.items()
                                              if v is not None and v & ~1 == t] for t in targets}
        out["branch_candidates"] = []
        sec = elf.text
        for off in range(sec["off"], sec["off"] + sec["size"] - 3, 2):
            a, b = struct.unpack_from("<HH", elf.d, off)
            if a & 0xf800 != 0xf000 or b & 0xd000 not in (0xd000, 0x9000, 0xc000):
                continue
            sign = (a >> 10) & 1
            i1 = 1 ^ ((b >> 13) & 1) ^ sign
            i2 = 1 ^ ((b >> 11) & 1) ^ sign
            delta = (sign << 24) | (i1 << 23) | (i2 << 22) | ((a & 1023) << 12) | ((b & 2047) << 1)
            if sign:
                delta -= 1 << 25
            va = sec["addr"] + off - sec["off"]
            base = (va + 4) & (~3 if b & 0xd000 == 0xc000 else ~0)
            dest = (base + delta) & 0xffffffff
            if dest in targets:
                out["branch_candidates"].append({"va": hex(va), "target": hex(dest)})
    for spec in (s for s in specs if not s.startswith("@")):
        lo, hi = (int(a, 16) for a in spec.split(":"))
        old = []
        for key, text in windows.items():
            a, b = (int(v, 16) for v in key.split(":"))
            if a <= lo and b >= hi:
                old = [line for line in text.splitlines()
                       if (m := re.match(r"\s*([0-9a-f]+):", line))
                       and lo <= int(m[1], 16) < hi]
                reused.append({"requested": spec, "source_window": key})
                break
        fresh = subprocess.run(["llvm-objdump", "-d", "--triple=thumbv7-linux-gnueabi",
                                f"--start-address={lo}", f"--stop-address={hi}", str(LIB / name)],
                               capture_output=True, text=True, check=True).stdout
        # Preserve fresh bytes for independent verification; older labels are not ownership.
        offset = elf.off(lo)
        assert offset is not None
        out["windows"][spec] = {"existing_listing": "\n".join(old) if old else None,
                                "binary_verification": fresh,
                                "bytes_sha256": hashlib.sha256(elf.d[offset:offset + hi - lo]).hexdigest()}
        literals = []
        for line in fresh.splitlines():
            match = re.search(r"ldr(?:\.w)?\s+r\d+, \[pc,.*@ 0x([0-9a-f]+)", line)
            if match and elf.off(int(match[1], 16)) is not None:
                value = elf.u32(int(match[1], 16))
                try:
                    string = elf.cstr(value)
                except (ValueError, TypeError):
                    continue
                if 3 < len(string) < 300 and all(32 <= ord(c) < 127 or c in "\n\r\t" for c in string):
                    literals.append({"pool": match[1], "target": hex(value), "string": string})
        out["windows"][spec]["literal_strings"] = literals
    out["sha256_after"] = hashlib.sha256((LIB / name).read_bytes()).hexdigest()
    assert out["sha256_after"] == before
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
