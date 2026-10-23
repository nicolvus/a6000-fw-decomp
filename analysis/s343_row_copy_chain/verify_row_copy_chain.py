#!/usr/bin/env python3
"""S343 - verificacion independiente: re-decoda la cadena desde los blobs.

Uso: ``.venv/bin/python analysis/s343_row_copy_chain/verify_row_copy_chain.py``
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
FW = ROOT / "firmware/extracted"
BLOBS = {
    "a7s": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/"
                 "nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6000": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                   "nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300": FW / ("a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/"
                   "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
JSON = Path(__file__).with_name("row_copy_chain.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
BLOCKS = [0xF3122300, 0xF3122200, 0xF3123300, 0xF3123200, 0xFC0A3100, 0xFC0A4100]

ok = 0
fails: list[str] = []


def check(name: str, cond: bool) -> None:
    global ok
    if cond:
        ok += 1
    else:
        fails.append(name)


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def code(b: bytes, start: int, size: int) -> list[tuple[int, str, str]]:
    return [(i.address, f"{i.mnemonic} {i.op_str}".strip(), i.bytes.hex())
            for i in MD.disasm(b[start - BASE:start - BASE + size], start)]


def texts(b: bytes, start: int, size: int) -> list[str]:
    return [t for _, t, _ in code(b, start, size)]


def has(b: bytes, start: int, size: int, text: str) -> bool:
    return text in texts(b, start, size)


def writer(b: bytes, func: int) -> dict[str, int | str] | None:
    ins = code(b, func, 14)
    if len(ins) < 5:
        return None
    t = [x[1] for x in ins]
    if (not t[0].startswith("ldr r3, [pc") or not t[1].startswith("ldr r2, [r3")
            or "bfi r2, r0" not in t[2] or not t[3].startswith("str r2, [r3")
            or t[4] != "bx lr"):
        return None
    m0 = re.search(r"#(0x[0-9a-f]+|\d+)", t[0])
    assert m0 is not None
    lit = ((func + 4) & ~3) + int(m0.group(1), 0)
    m = re.search(r"\[r3(?:, #(0x[0-9a-f]+|\d+))?\]", t[1])
    off = int(m.group(1), 0) if m and m.group(1) else 0
    m3 = re.search(r"#(0x[0-9a-f]+|\d+), #(0x[0-9a-f]+|\d+)$", t[2])
    assert m3 is not None
    return {"function": f"0x{func:08x}", "block": u32(b, lit), "offset": off,
            "lsb": int(m3.group(1), 0), "width": int(m3.group(2), 0)}


def library(b: bytes) -> dict[tuple[int, int, int, int], str]:
    out: dict[tuple[int, int, int, int], str] = {}
    for blk in BLOCKS:
        pat = struct.pack("<I", blk)
        i = b.find(pat)
        while i >= 0:
            w = writer(b, BASE + i - 0xC)
            if w and w["block"] == blk:
                out[(int(w["block"]), int(w["offset"]), int(w["lsb"]), int(w["width"]))] = str(w["function"])
            i = b.find(pat, i + 1)
    return out


def main() -> int:
    d = json.loads(JSON.read_text())
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    a7, a6, a63 = blobs["a7s"], blobs["a6000"], blobs["a6300"]

    for k, key in (("a7s", "a7s_fw320"), ("a6000", "a6000_fw321"),
                   ("a6300", "a6300_fw201")):
        check(f"sha256 {k}", hashlib.sha256(blobs[k]).hexdigest() == d["firmware"][key]["sha256"])
        check(f"size {k}", len(blobs[k]) == d["firmware"][key]["size"])

    # 1. copia de 20 B en 0x436f5f7c
    check("copia ldm/stm 16 B", has(a7, 0x436F5FA6, 8, "ldm.w lr!, {r0, r1, r2, r3}"))
    check("copia 4 B extra", has(a7, 0x436F5FAC, 6, "ldr.w r3, [lr]"))
    check("parche bit 0 del estado", has(a7, 0x436F5FBA, 4, "tst.w r3, #1"))
    check("llamada a 0x43ada310", has(a7, 0x436F5FD2, 4, "bl #0x43ada310"))

    # 2. constructor del bloque de 44 B
    check("0x43ada310 copia 20 B", has(a7, 0x43ADA318, 8, "ldm r7!, {r0, r1, r2, r3}"))
    check("0x43ada310 bucle 12 pares", has(a7, 0x43ADA344, 2, "cmp r6, #0x18"))
    check("0x43ada310 stride 2", has(a7, 0x43ADA342, 2, "adds r6, #2"))
    check("0x43ada310 padding 0xb", has(a7, 0x43ADA35A, 2, "adds r2, #0xb"))
    check("0x43ada310 llama 0x43ada480", has(a7, 0x43ADA368, 4, "bl #0x43ada480"))

    # 3. despachador
    check("0x43ada480 copia bloque[0]", has(a7, 0x43ADA48A, 2, "str r3, [r0]"))
    check("0x43ada480 umbral 12", has(a7, 0x43ADA4A4, 2, "cmp r3, #0xc"))
    calls = [t.split()[1] for t in texts(a7, 0x43ADA4A8, 0x2C) if t.startswith("bl ")]
    check("0x43ada480 4 bl + tail", calls == ["#0x436f6710", "#0x436f68ec",
                                             "#0x43544270", "#0x436f6b9c"]
          and has(a7, 0x43ADA4D2, 4, "b.w #0x436f7480"))

    # 4. descompresor tbh: 6 casos y 12 campos en el caso 0
    tbl = 0x436F6720
    tgts = [f"0x{tbl + 2 * u16(a7, tbl + 2 * k):08x}" for k in range(6)]
    check("tbh 6 casos", tgts == d["handlers"]["0x436f6710"]["tbh"])
    case0 = [t for t in texts(a7, 0x436F672C, 0x4C)]
    row_bytes = [int(t.split("#")[1].rstrip("]"), 16) for t in case0 if t.startswith("ldrb r0, [r4, #")]
    check("caso 0 usa 12 bytes impares", row_bytes == list(range(1, 0x19, 2)))
    first = writer(a7, 0x436F7578)
    check("escritor nibble lsb0", first is not None and first["offset"] == 0
          and first["lsb"] == 0 and first["width"] == 4 and first["block"] == 0xF3122300)

    # 5. bit unico por caso
    singles = [(s["case"], s["block"], s["offset"], s["lsb"], s["width"])
               for s in d["single_bit_writers"]]
    check("6 bits unicos", singles == [(0, "0xf3122300", 0x28, 0, 1),
                                       (1, "0xf3122200", 0x20, 0, 1),
                                       (2, "0xf3123300", 0x28, 0, 1),
                                       (3, "0xf3123200", 0x20, 0, 1),
                                       (4, "0xfc0a3100", 0x28, 0, 1),
                                       (5, "0xfc0a4100", 0x28, 0, 1)])
    for s in d["single_bit_writers"]:
        w = writer(a7, int(s["function"], 16))
        check(f"bit {s['case']}", w is not None and w["block"] == int(s["block"], 16)
              and w["offset"] == s["offset"])

    # 6. biblioteca de escritores
    lib7, lib6, lib63 = library(a7), library(a6), library(a63)
    check("178 escritores A7S", len(lib7) == 178 == d["writer_library"]["total"])
    check("177 escritores A6000", len(lib6) == 177)
    check("178 escritores A6300", len(lib63) == 178)
    per: dict[str, int] = {}
    for (blk, *_rest) in lib7:
        per[f"0x{blk:08x}"] = per.get(f"0x{blk:08x}", 0) + 1
    check("reparto por bloque", per == d["writer_library"]["per_block"])
    check("campos A7S", {f"0x{b:08x}" for b in BLOCKS} == set(per))

    # 7. getters de S340
    getters = [(g["function"], g["block"], g["offset"]) for g in d["getters"]["list"]]
    check("6 getters", getters == [("0x436f7734", "0xf3122300", 0x30),
                                   ("0x436f78e8", "0xf3122200", 0x24),
                                   ("0x436f7b20", "0xf3123300", 0x30),
                                   ("0x436f7cd4", "0xf3123200", 0x24),
                                   ("0x436f7f1c", "0xfc0a3100", 0x30),
                                   ("0x436f8164", "0xfc0a4100", 0x30)])
    s340 = json.loads((ROOT / "analysis/s340_w0_selector/w0_selector.json").read_text())
    check("bloques = S340", sorted(s340["verdicts"]["selector_bases"])
          == [f"0x{b:08x}" for b in sorted(BLOCKS)])

    # 8. diferencial A7S/A6000
    only7 = sorted(set(lib7) - set(lib6))
    only6 = sorted(set(lib6) - set(lib7))
    check("un solo campo exclusivo A7S", only7 == [(0xFC0A3100, 0xC, 24, 1)])
    check("ninguno exclusivo A6000", only6 == [])
    check("json coincide", d["cross_model"]["a7s_only_fields"] ==
          [{"block": "0xfc0a3100", "offset": 12, "lsb": 24, "width": 1}])

    # 9. negativos: la cadena no toca la mascara DFE ni P2S
    check("sin escritores 0xfc02a00c", 0xFC02A00C not in {b for (b, *_r) in lib7})
    check("sin escritores 0xfc088300", 0xFC088300 not in {b for (b, *_r) in lib7})
    check("mascara DFE documentada", d["negatives"]["mask_path_register"] == "0xfc02a00c (S335/S338)")

    # 10. evidencias de los otros manejadores
    check("0x436f68ec mascara de flags", has(a7, 0x436F6904, 4, "ands r5, r3, #0xa"))
    check("0x436f68ec lee flags", has(a7, 0x436F691E, 4, "ldrb.w r5, [r1, #0x2a]"))
    check("0x43544270 lee byte 5", has(a7, 0x43544276, 2, "ldrb r4, [r1, #5]"))
    check("0x436f6b9c tabla 0x78", has(a7, 0x436F6BCC, 4, "mov.w r8, #0x78"))

    total = ok + len(fails)
    print(f"{total} comprobaciones, {len(fails)} fallos")
    for f in fails:
        print("  FALLO:", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
