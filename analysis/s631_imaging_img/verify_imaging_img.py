"""S631: verifica contra av-cam.bin las 7 trazas [IMAGING_IMG] y sus 12 cargas PC-relativas."""
import collections
import json
import re
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


def bl_target(h1: int, h2: int, addr: int) -> int | None:
    """Destino de un BL Thumb-2 (T1 0xF000/0xD000)."""
    if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000:
        return None
    s, j1, j2 = (h1 >> 10) & 1, (h2 >> 13) & 1, (h2 >> 11) & 1
    imm = (s << 24) | ((~(j1 ^ s) & 1) << 23) | ((~(j2 ^ s) & 1) << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
    return (addr + 4 + imm - (1 << 25 if s else 0)) & 0xFFFFFFFF


def func_start(blob: bytes, addr: int) -> int | None:
    for p in range((addr - BASE) & ~1, addr - BASE - 6000, -2):
        h = struct.unpack_from("<H", blob, p)[0]
        if (h & 0xFF00) == 0xB500 or (h == 0xE92D and struct.unpack_from("<H", blob, p + 2)[0] & 0x4000):
            return BASE + p
    return None


def module_tags(blob: bytes, start: int, end: int) -> dict:
    """Etiquetas [X] de las cadenas cargadas por pares ldr pc-relativo + add pc dentro de [start,end)."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.skipdata = True
    ins = list(md.disasm(blob[start - BASE:end - BASE], start))
    out = collections.Counter()
    for n, i in enumerate(ins):
        if i.mnemonic.startswith("ldr") and "pc," in i.op_str and "#" in i.op_str:
            reg, imm = i.op_str.split(",")[0], int(i.op_str.split("#")[1].rstrip("]"), 16)
            value = struct.unpack_from("<I", blob, ((i.address + 4) & ~3) + imm - BASE)[0]
            add = next((j for j in ins[n + 1:n + 6] if j.mnemonic == "add" and j.op_str == f"{reg}, pc"), None)
            target = (value + add.address + 4) & 0xFFFFFFFF if add else 0
            if add and BASE <= target < BASE + len(blob):
                m = re.match(rb"(\[[A-Z0-9_]+\])", blob[target - BASE:target - BASE + 60])
                if m:
                    out[m.group(1).decode()] += 1
    return dict(out)


def callers(blob: bytes) -> dict:
    found = {name: [] for name in FUNCS}
    by_addr = {v: k for k, v in FUNCS.items()}
    for o in range(0, len(blob) - 4, 2):
        t = bl_target(*struct.unpack_from("<HH", blob, o), BASE + o)
        if t in by_addr:
            found[by_addr[t]].append(BASE + o)
    out = {}
    for name, sites in found.items():
        rows = []
        for a in sites:
            f = func_start(blob, a)
            rows.append({"site": hex(a), "function": hex(f) if f else None,
                         "tags": module_tags(blob, f, min(f + 1500, a + 400)) if f else {}})
        out[name] = rows
    return out


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
            "strings": {hex(a): t for a, t in sorted(strings.items())}, "refs": refs, "logger_calls": calls, "callers": callers(blob)}
    assert len(strings) == 7 and len(refs) == 12, data
    assert [len(v) for v in data["callers"].values()] == [10, 26, 7], data["callers"]
    assert all(r["function"] for r in refs) and all(i < END for i in [int(r["load"], 16) for r in refs])
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    print(json.dumps({k: v for k, v in main().items() if k in ("traces", "pic_refs", "logger_calls")}))
