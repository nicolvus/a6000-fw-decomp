"""S631: verifica contra av-cam.bin las 7 trazas [IMAGING_IMG] y sus 12 cargas PC-relativas."""
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
OUT = Path(__file__).with_name("imaging_img.json")
BASE = 0x43541000
LO, HI = 0x4381B9D0, 0x4381C200
FUNCS = {"Image::Clone": 0x4381BA9C, "Image::Branch": 0x4381BBF0, "Image::Create": 0x4381BD4C}
END = 0x4381BEC4  # siguiente push tras Image::Create
LOGGERS = (0x4381B9D0, 0x43902718)


def main() -> dict:
    blob = BIN.read_bytes()
    strings = {}
    pos = 0
    while (pos := blob.find(b"[IMAGING_IMG]", pos)) >= 0:
        end = blob.index(b"\0", pos)
        strings[BASE + pos] = blob[pos:end].decode("latin1")
        pos = end
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.skipdata = True
    ins = list(md.disasm(blob[LO - BASE:HI - BASE], LO))
    refs = []
    for n, i in enumerate(ins):
        if i.mnemonic != "ldr" or "pc," not in i.op_str:
            continue
        reg, imm = i.op_str.split(",")[0], int(i.op_str.split("#")[1].rstrip("]"), 16)
        value = struct.unpack_from("<I", blob, ((i.address + 4) & ~3) + imm - BASE)[0]
        add = next((j for j in ins[n + 1:n + 6] if j.mnemonic == "add" and j.op_str == f"{reg}, pc"), None)
        target = (value + add.address + 4) & 0xFFFFFFFF if add else None
        if target in strings:
            owner = max((a for a in FUNCS.values() if a <= i.address), default=None)
            refs.append({"string": hex(target), "load": hex(i.address), "pic_add": hex(add.address),
                         "function": hex(owner) if owner else None})
    calls = sorted({hex(int(i.op_str[1:], 16)) for i in ins if i.mnemonic == "bl"
                    and int(i.op_str[1:], 16) in LOGGERS})
    data = {"traces": len(strings), "pic_refs": len(refs), "functions": {k: hex(v) for k, v in FUNCS.items()},
            "strings": {hex(a): t for a, t in sorted(strings.items())}, "refs": refs, "logger_calls": calls}
    assert len(strings) == 7 and len(refs) == 12, data
    assert all(r["function"] for r in refs) and all(i < END for i in [int(r["load"], 16) for r in refs])
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    print(json.dumps({k: v for k, v in main().items() if k in ("traces", "pic_refs", "logger_calls")}))
