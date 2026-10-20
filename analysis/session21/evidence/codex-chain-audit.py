"""Auditoría reproducible de aristas/ABI; no ejecuta firmware ni escribe archivos."""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from rtti_vtables import Elf, recover, self_check

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib"
EXPECTED = {
    "libmpr.so": "9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30",
    "libObj.so": "8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a",
}


def branch(elf, va):
    """Decodifica BL/B.W Thumb-2; sitios aceptados contrastados además con LLVM."""
    offset = elf.off(va)
    assert offset is not None
    a, b = struct.unpack_from("<HH", elf.d, offset)
    assert a & 0xf800 == 0xf000 and b & 0xd000 in (0xd000, 0x9000)
    sign = (a >> 10) & 1
    delta = ((sign << 24) | ((1 ^ ((b >> 13) & 1) ^ sign) << 23)
             | ((1 ^ ((b >> 11) & 1) ^ sign) << 22)
             | ((a & 1023) << 12) | ((b & 2047) << 1))
    return (va + 4 + delta - ((1 << 25) if sign else 0)) & 0xffffffff


def main():
    checks = []
    elves = {name: Elf(str(LIB / name)) for name in EXPECTED}

    def check(name, passed):
        assert passed, name
        checks.append({"check": name, "result": "PASS"})

    for name, elf in elves.items():
        check("SHA256 " + name, hashlib.sha256(elf.d).hexdigest() == EXPECTED[name])
    mpr, obj = elves["libmpr.so"], elves["libObj.so"]
    rtti = recover(mpr)
    self_check(mpr, rtti)
    slots = {0x81c0e0: 0x34cfa1, 0x81c0e8: 0x34b2e5,
             0x81c0ec: 0x34b349, 0x882e34: 0x5144e5, 0x81bb50: 0x34b139}
    for slot, expected in slots.items():
        check(f"relocated table {slot:#x} -> {expected:#x}", mpr.rel[slot][0] == expected)
    edges = {
        "libObj.so": {0x90ba24: 0x908084, 0x90817a: 0x90fcd4,
                      0x90fd60: 0x91bbd0, 0x90fdc8: 0x91bbd0,
                      0x91bbdc: 0x8fd2fc, 0x8fd37e: 0x900124,
                      0x90bb86: 0x90f698, 0x90bbdc: 0x908afc,
                      0x908d9c: 0x8fe0a0, 0x90a172: 0x8fe0a0,
                      0x91bb64: 0x8fd38e, 0x8fd3b0: 0x8fc538,
                      0x939df2: 0x932a44},
        "libmpr.so": {0x34a93a: 0x2d7d20, 0x32d5ea: 0x32ed34,
                      0x34ac20: 0x34b5c8, 0x34b5b6: 0x513268,
                      0x34b78c: 0x34b5a6, 0x34bd66: 0x32ee30,
                      0x34cfde: 0x34cc34, 0x514530: 0x5144b0,
                      0x5144d8: 0x5141ec, 0x514366: 0x3a2e74,
                      0x397116: 0x1d6c76, 0x39746e: 0x1d6cb6,
                      0x1d6cc2: 0x22d1cc, 0x397494: 0x1d6cc6,
                      0x34c848: 0x2d7dd0, 0x51458c: 0x455b08,
                      0x38be60: 0x38b064, 0x38be9a: 0x381a18,
                      0x38b7e4: 0x3816bc, 0x38225e: 0x3816bc,
                      0x381958: 0x381594, 0x3815c8: 0x3bd3bc,
                      0x3bd3ec: 0x3bcfbc, 0x3810b4: 0x353428,
                      0x38166a: 0x3bc1e4},
    }
    for name, pairs in edges.items():
        for site, target in pairs.items():
            check(f"{name} {site:#x} -> {target:#x}", branch(elves[name], site) == target)
    # Las tablas TBB son bytes de datos, no las instrucciones ficticias que imprime LLVM.
    off = mpr.off(0x34b2f0)
    assert off is not None
    command9 = 0x34b2f0 + 2 * mpr.d[off + 9]
    check("command9 TBB -> flag +0x956 setter", command9 == 0x34b310)
    off = mpr.off(0x34cfb0)
    assert off is not None
    state7 = 0x34cfb0 + 2 * mpr.d[off + 6]
    check("state7 TBB -> 34cfda -> 34cc34", state7 == 0x34cfda)
    check("RAW callee name, despite MPO error label", mpr.cstr(mpr.u32(0x22d3c8)) == "RegisterRawContent")
    check("RecStill ctor vptr", mpr.u32(0x34b7fc) == 0x81c0b8)
    check("StillWriterFilter ctor vptr", mpr.u32(0x513340) == 0x882e28)
    # Una marca Pool no se identifica por el código externo del sobre.
    check("PoolWrap 8fc538 includes selector 3001=1", obj.d[obj.off(0x8fc57e):obj.off(0x8fc580)] == bytes.fromhex("0121"))
    check("PoolWrap 8fc62e includes selector 3001=2", obj.d[obj.off(0x8fc674):obj.off(0x8fc676)] == bytes.fromhex("0221"))
    sensor = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
    sensor_data = sensor.read_bytes()
    check("SHA256 av-cam.bin", hashlib.sha256(sensor_data).hexdigest() ==
          "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")
    notify_lines = []
    with Path("/tmp/s20work/avcam-thumb.disasm").open() as listing:
        for line in listing:
            match = re.match(r"\s*([0-9a-f]+):\s+((?:[0-9a-f]{4} )*[0-9a-f]{4})\s+", line)
            if not match or not 0x437efe78 <= int(match[1], 16) < 0x437f000c:
                continue
            va = int(match[1], 16)
            raw = b"".join(struct.pack("<H", int(w, 16)) for w in match[2].split())
            check(f"cached Stage_Notify bytes {va:#x}", sensor_data[va - 0x43541000:va - 0x43541000 + len(raw)] == raw)
            notify_lines.append(line.rstrip())
    check("nonempty Stage_Notify verification", len(notify_lines) > 20)
    for name, elf in elves.items():
        check("original unchanged " + name, hashlib.sha256((LIB / name).read_bytes()).hexdigest() == EXPECTED[name])
    print(json.dumps({"result": "PASS", "checks": checks,
                      "recstill_vtable": rtti["classes"]["0x81c0a0"] if "0x81c0a0" in rtti["classes"] else
                      next(c for c in rtti["classes"].values() if c["name"] == "RecStill"),
                      "stage_notify_reused_listing": notify_lines,
                      "limits": ["aristas estáticas, no ejecución", "no certifica persistencia SD ni reproducción"]}, indent=2))


if __name__ == "__main__":
    main()
