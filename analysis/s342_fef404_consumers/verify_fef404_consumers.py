#!/usr/bin/env python3
"""S342 - verificacion independiente: re-decoda TODO desde los blobs.

No importa el build: repite la decodificacion (tabla, arrays, pares PIC, slots
GOT, bucles, callers, cadenas) y compara con `fef404_consumers.json`.

Uso: ``.venv/bin/python analysis/s342_fef404_consumers/verify_fef404_consumers.py``
"""
from __future__ import annotations

import hashlib
import json
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
JSON = Path(__file__).with_name("fef404_consumers.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

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


def ids_of(b: bytes, t: int) -> list[int]:
    out, i = [], 0
    while u16(b, t + 4 * i + 2) == 0x000D:
        out.append(u16(b, t + 4 * i))
        i += 1
    return out


def pic(b: bytes, ldr: int, add: int) -> tuple[int, int, int]:
    h = u16(b, ldr)
    assert (h & 0xF800) == 0x4800
    lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    word = u32(b, lit)
    h2 = u16(b, add)
    assert (h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
    assert (h2 & 7) == (h >> 8) & 7 and ((h2 >> 7) & 1) == 0
    return lit, word, (word + ((add + 4) & ~1)) & 0xFFFFFFFF


def pics_to(b: bytes, target: int) -> list[int]:
    out = []
    n = len(b)
    for off in range(0, n - 8, 2):
        h = u16(b, BASE + off)
        if (h & 0xF800) != 0x4800:
            continue
        rd = (h >> 8) & 7
        lit = ((BASE + off + 4) & ~3) + ((h & 0xFF) * 4)
        if lit - BASE + 4 > n:
            continue
        word = u32(b, lit)
        for k in (2, 4, 6, 8):
            add = BASE + off + k
            h2 = u16(b, add)
            if ((h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
                    and (h2 & 7) == rd and ((h2 >> 7) & 1) == 0):
                if (word + ((add + 4) & ~1)) & 0xFFFFFFFF == target:
                    out.append(BASE + off)
                break
    return out


def bl_to(b: bytes, target: int) -> list[int]:
    out = []
    for off in range(0, len(b) - 4, 2):
        h = struct.unpack_from("<H", b, off)[0]
        if (h & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", b, off + 2)[0]
        if (h2 & 0xD000) != 0xD000:
            continue
        s = (h >> 10) & 1
        j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
        val = ((s << 24) | ((1 - (j1 ^ s)) << 23) | ((1 - (j2 ^ s)) << 22)
               | ((h & 0x3FF) << 12) | ((h2 & 0x7FF) << 1))
        if s:
            val -= 1 << 25
        if (BASE + off + 4 + val) & 0xFFFFFFFF == target:
            out.append(BASE + off)
    return out


def insns(b: bytes, start: int, size: int) -> list[tuple[int, str]]:
    return [(i.address, f"{i.mnemonic} {i.op_str}".strip())
            for i in MD.disasm(b[start - BASE:start - BASE + size], start)]


def zero_run(b: bytes, addr: int) -> tuple[int, int]:
    i = addr - BASE
    lo = i
    while lo > 0 and b[lo - 1] == 0:
        lo -= 1
    hi = i
    while hi < len(b) and b[hi] == 0:
        hi += 1
    return BASE + lo, BASE + hi


def has_insn(b: bytes, start: int, size: int, text: str) -> bool:
    return any(t == text for _, t in insns(b, start, size))


def main() -> int:
    d = json.loads(JSON.read_text())
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    a7, a6, a63 = blobs["a7s"], blobs["a6000"], blobs["a6300"]

    # 0. blobs
    for k, key in (("a7s", "a7s_fw320"), ("a6000", "a6000_fw321"),
                   ("a6300", "a6300_fw201")):
        h = hashlib.sha256(blobs[k]).hexdigest()
        check(f"sha256 {k}", h == d["firmware"][key]["sha256"])
        check(f"size {k}", len(blobs[k]) == d["firmware"][key]["size"])

    # 1. tabla A7S
    t7 = d["a7s"]["table"]
    ids7 = ids_of(a7, 0x43FEF404)
    check("a7s ids recomputados", ids7 == t7["ids"])
    check("a7s 69 entradas", len(ids7) == 69)
    check("a7s fin tabla", t7["end"] == f"0x{0x43FEF404 + 4 * 69:08x}")
    check("a7s segundo campo 0x0d",
          all(u16(a7, 0x43FEF404 + 4 * i + 2) == 0x0D for i in range(69)))
    check("a7s ids unicos", len(set(ids7)) == 69)

    # 2. array de 256 punteros que termina en la tabla
    pre = [u32(a7, 0x43FEF004 + 4 * i) for i in range(256)]
    run = 0
    back = 0x43FEF404 - 4
    while u32(a7, back) == 0x43F9C622:
        run += 1
        back -= 4
    check("a7s prefijo 256 entradas", len(pre) == 256)
    check("a7s run contiguo 169", run == d["a7s"]["prefix_array"]["contiguous_43f9c622_before_table"])
    check("a7s total 0x43f9c622", pre.count(0x43F9C622) == d["a7s"]["prefix_array"]["count_43f9c622"])
    lo, hi = zero_run(a7, 0x43F9C622)
    check("a7s zero run", (f"0x{lo:08x}", f"0x{hi:08x}") ==
          (d["a7s"]["zero_run"]["start"], d["a7s"]["zero_run"]["end"]))
    check("a7s prefijo en bss", all(lo <= p < hi for p in pre))

    # 3. hueco de 8 B y array companero
    gap = [u32(a7, 0x43FEF518 + 4 * i) for i in range(2)]
    check("a7s gap", [f"0x{v:08x}" for v in gap] == d["a7s"]["gap"]["words"])
    comp = u32(a7, 0x44028C78)
    check("a7s slot companero", comp == 0x43FEF520)
    ptrs = [u32(a7, comp + 4 * i) for i in range(69)]
    check("a7s 69 punteros", len(ptrs) == 69)
    check("a7s punteros en bss", all(lo <= p < hi for p in ptrs))
    check("a7s sin base PIC al array", pics_to(a7, comp) == [])

    # 4. sitios PIC hacia la tabla
    sites7 = pics_to(a7, 0x43FEF404)
    check("a7s 2 sitios PIC", sites7 == [0x437056F8, 0x43705754])
    lit, word, base = pic(a7, 0x437056F8, 0x437056FC)
    check("a7s literal A", (lit, word, base) == (0x43705738, 0x008E9D04, 0x43FEF404))
    lit, word, base = pic(a7, 0x43705754, 0x43705756)
    check("a7s literal B", (lit, word, base) == (0x4370577C, 0x008E9CAA, 0x43FEF404))
    # ambos sitios van seguidos de una lectura, no de una escritura
    for ldr, add in ((0x437056F8, 0x437056FC), (0x43705754, 0x43705756)):
        nxt = insns(a7, add + 2, 4)
        check(f"a7s lectura tras {add:08x}", bool(nxt) and nxt[0][1].startswith("ldr"))

    # 5. consumidor A
    ca = d["a7s"]["consumers"]["A"]
    check("A prologo", has_insn(a7, 0x437056EC, 4, "push.w {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}"))
    check("A bucle 69", has_insn(a7, 0x43705724, 2, "cmp r7, #0x45"))
    check("A paso 1", has_insn(a7, 0x43705712, 2, "adds r4, #4"))
    check("A slot companero", ca["slots"][0]["slot"] == "0x44028c78"
          and ca["slots"][0]["value"] == "0x43fef520")
    check("A slot otro", ca["slots"][1]["slot"] == "0x44026240"
          and ca["slots"][1]["value"] == "0x43e906f4")
    check("A llamadas", [c for c in ca["calls"]] == ["#0x4355f790", "#0x4355f6a8"])
    check("A caller", bl_to(a7, 0x437056EC) == [0x4373D0B4])

    # 6. consumidor B
    cb = d["a7s"]["consumers"]["B"]
    check("B inmediato 0xd", has_insn(a7, 0x43705748, 4, "movs r0, #0xd"))
    check("B bucle 0x114", has_insn(a7, 0x4370576A, 4, "cmp.w r5, #0x114"))
    check("B paso 4", has_insn(a7, 0x43705764, 2, "adds r5, #4"))
    check("B iteraciones", cb["loop_count"] == 69)
    check("B slots", [s["value"] for s in cb["slots"]] == ["0x43fef520", "0x43e906f4"])
    check("B caller", bl_to(a7, 0x43705748) == [0x4373D2F2])

    # 7. array de 256 con limite 0x100
    pf = d["a7s"]["prefix_array_consumer"]
    check("prefijo slot", pf["slot"]["slot"] == "0x440253ac"
          and pf["slot"]["value"] == "0x43fef004")
    check("prefijo limite", has_insn(a7, 0x4373F1DC, 4, "cmp.w r3, #0x100"))
    check("prefijo indice", has_insn(a7, 0x4373F1EC, 2, "cmp r5, #0xff"))

    # 8. modulo del init
    strs = " ".join(d["a7s"]["module_strings"])
    check("modulo ODL", "Camera::Lens::ODL" in strs)
    check("init ODL", "Camera::Lens::Initialize(UPM_BOOT_FACTOR*)" in strs)

    # 9. A6000
    t6 = d["a6000"]["table"]
    ids6 = ids_of(a6, 0x43FEAE1C)
    check("a6000 ids", ids6 == t6["ids"] and len(ids6) == 47)
    check("a6000 sitios", pics_to(a6, 0x43FEAE1C) == [0x436EB2D8, 0x436EB334])
    check("a6000 bucle A", has_insn(a6, 0x436EB304, 2, "cmp r7, #0x2f"))
    check("a6000 bucle B", has_insn(a6, 0x436EB34A, 4, "cmp r5, #0xbc"))
    check("a6000 slot companero", u32(a6, 0x44022AB0) == 0x43FEAE1C - 0xC4)
    check("a6000 callers", bl_to(a6, 0x436EB2CC) == [0x4372162A]
          and bl_to(a6, 0x436EB328) == [0x4372187A])

    # 10. A6300 (base corroborada por la cadena de S168)
    s = b"position num in rolling is strange"
    i = a63.find(s)
    check("a6300 base", (0x43D9FE03 - i) & 0xFFFFFFFF == BASE)
    ids63 = ids_of(a63, 0x441B0B1C)
    check("a6300 ids == a7s", ids63 == ids7)
    check("a6300 sitios", pics_to(a63, 0x441B0B1C) == [0x43734BE4, 0x43734C40])
    check("a6300 bucle A", has_insn(a63, 0x43734C10, 2, "cmp r7, #0x45"))
    check("a6300 slot companero", u32(a63, 0x441FCB9C) == 0x441B0C38)

    # 11. relaciones entre modelos
    check("a6000 subconjunto", set(ids6) < set(ids7))
    check("faltan 22", [f"0x{x:02x}" for x in sorted(set(ids7) - set(ids6))]
          == [f"0x{x:02x}" for x in range(0x4F, 0x65)])
    check("bucles = entradas", d["cross_model"]["loop_bounds"]
          == {"a7s": 69, "a6000": 47, "a6300": 69})

    # 12. negativos
    check("0 literales absolutos", d["negatives"]["absolute_literal_refs"] == 0)
    regs = {u16(a7, u32(a7, 0x43FEE598 + 0x14 * k) - 4) for k in range(69)}
    check("ids != registros matriz", regs == {0x81, 0x83} and set(ids7) != regs)

    total = ok + len(fails)
    print(f"{total} comprobaciones, {len(fails)} fallos")
    for f in fails:
        print("  FALLO:", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
