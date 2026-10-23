#!/usr/bin/env python3
"""S348 - verificador independiente de `odl_callback.json` (solo bytes).

No usa `build_odl_callback.py` ni capstone: decodifica a mano el `ldr`+`add pc`,
el `b.w` T4 del shim, el veneer (`bx pc` + `b` ARM) y la huella de `memcpy`, y
re-cuenta los usuarios del shim con un barrido PIC propio.

Uso: .venv/bin/python analysis/s348_odl_callback/verify_odl_callback.py
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FW = ROOT / "firmware/extracted"
BLOBS = {
    "a7s_fw320": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/"
                       "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6000_fw321": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300_fw201": FW / ("a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/"
                         "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
DATA = json.loads((HERE / "odl_callback.json").read_text(encoding="utf-8"))
CHECKS = 0


def check(cond: bool, msg: str) -> None:
    global CHECKS
    CHECKS += 1
    if not cond:
        raise SystemExit(f"FALLO #{CHECKS}: {msg}")


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def raw(blob: bytes, addr: int, n: int) -> bytes:
    off = addr - BASE
    check(0 <= off and off + n <= len(blob), f"0x{addr:08x} fuera del blob")
    return blob[off:off + n]


def b_w_target(blob: bytes, addr: int) -> int:
    """`b.w` T4 incondicional (2 halfwords) -> destino."""
    h1 = u16(blob, addr)
    h2 = u16(blob, addr + 2)
    check((h1 & 0xF800) == 0xF000, f"0x{addr:08x}: h1 no es b.w")
    check((h2 & 0xD000) == 0x9000, f"0x{addr:08x}: h2 no es b.w")
    s = (h1 >> 10) & 1
    imm10 = h1 & 0x3FF
    j1 = (h2 >> 13) & 1
    j2 = (h2 >> 11) & 1
    imm11 = h2 & 0x7FF
    i1 = 1 - (j1 ^ s)
    i2 = 1 - (j2 ^ s)
    imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if s:
        imm -= 1 << 25
    return (addr + 4 + imm) & 0xFFFFFFFF


def arm_b_target(blob: bytes, addr: int) -> int:
    w = u32(blob, addr)
    check((w >> 28) == 0xE, f"0x{addr:08x}: no es b ARM incondicional")
    check(((w >> 25) & 7) == 5, f"0x{addr:08x}: no es b ARM")
    imm = w & 0xFFFFFF
    if imm & 0x800000:
        imm -= 1 << 24
    return (addr + 8 + (imm << 2)) & 0xFFFFFFFF


def pic_sites(blob: bytes, target: int) -> list[str]:
    out: list[str] = []
    for off in range(0, len(blob) - 8, 2):
        h = struct.unpack_from("<H", blob, off)[0]
        if (h & 0xF800) != 0x4800:
            continue
        rd = (h >> 8) & 7
        lit = ((BASE + off + 4) & ~3) + ((h & 0xFF) * 4)
        if lit - BASE + 4 > len(blob):
            continue
        word = struct.unpack_from("<I", blob, lit - BASE)[0]
        for k in (2, 4, 6, 8):
            a = BASE + off + k
            if a - BASE + 2 > len(blob):
                break
            h2 = struct.unpack_from("<H", blob, a - BASE)[0]
            if ((h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
                    and (h2 & 7) == rd and ((h2 >> 7) & 1) == 0):
                if (word + ((a + 4) & ~1)) & 0xFFFFFFFF == target:
                    out.append(f"0x{BASE + off:08x}")
                break
    return out


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    # 1. hashes
    for k in BLOBS:
        check(DATA["firmware"][k]["sha256"] == hashlib.sha256(blobs[k]).hexdigest(),
              f"sha256 de {k}")
        check(DATA["firmware"][k]["size"] == len(blobs[k]), f"tamano de {k}")

    shims: set[str] = set()
    fps: set[tuple[str, ...]] = set()
    for k, m in DATA["models"].items():
        blob = blobs[k]
        cb = int(m["callback_pointer"], 16)
        check(cb & 1 == 1, f"{k}: el callback no es puntero Thumb")
        entry = cb & ~1
        # 2. el sitio PIC carga exactamente ese callback
        pic = pic_sites(blob, cb)
        check(pic == m["users"], f"{k}: usuarios del shim {pic}")
        check(len(pic) == 1, f"{k}: el shim debe tener un solo usuario")
        # 3. shim: push + 4 mov + pop.w + b.w
        check(raw(blob, entry, 10).hex() == "10b50c46184611462246", f"{k}: shim")
        check(raw(blob, entry + 10, 4).hex() == "bde81040", f"{k}: pop.w del shim")
        veneer = b_w_target(blob, entry + 14)
        check(f"0x{veneer:08x}" == m["veneer"]["address"], f"{k}: veneer")
        check(m["shim"]["bytes"] == "10b50c46184611462246", f"{k}: shim registrado")
        shims.add(m["shim"]["bytes"])
        # 4. veneer: bx pc + nop + b ARM
        check(raw(blob, veneer, 4).hex() == "7847c046", f"{k}: bx pc del veneer")
        target = arm_b_target(blob, veneer + 4)
        check(f"0x{target:08x}" == m["memcpy"]["address"], f"{k}: destino ARM")
        check(f"0x{target:08x}" == m["veneer"]["arm_target"], f"{k}: target registrado")
        # 5. huella de memcpy ARM (4 palabras exactas)
        fp = [f"0x{u32(blob, target + 4 * i):08x}" for i in range(4)]
        check(fp == ["0xe92d4001", "0xe2522004", "0xba000020", "0xe210c003"],
              f"{k}: huella de memcpy {fp}")
        check(tuple(fp) == tuple(m["memcpy"]["fingerprint"]), f"{k}: huella registrada")
        fps.add(tuple(fp))
        # 6. palabra de especificacion: id bajo, 13 alto
        check(m["spec_word"]["high_half"] == 13, f"{k}: alto de la palabra != 13")
        check(m["spec_word"]["high_half"] == 0x000D, f"{k}: 13 != 0x000d")
        table = {"a7s_fw320": 0x43FEF404, "a6000_fw321": 0x43FEAE1C,
                 "a6300_fw201": 0x441B0B1C}[k]
        check(u16(blob, table + 2) == 13, f"{k}: la tabla no lleva 13")
        check(m["spec_word"]["low_half_id"] == u16(blob, table), f"{k}: id bajo")

    # 7. cross-model
    check(len(shims) == 1, "los shims difieren entre modelos")
    check(len(fps) == 1, "las implementaciones de memcpy difieren")
    check(DATA["cross_model"]["shim_bytes_identical"] is True, "cross: shims")
    check(DATA["cross_model"]["memcpy_fingerprint_identical"] is True, "cross: memcpy")
    check(DATA["cross_model"]["every_shim_has_one_user"] is True, "cross: usuarios")
    check(set(DATA["cross_model"]["high_half_of_spec_word"].values()) == {13},
          "cross: alto != 13 en algun modelo")

    # 8. veredictos
    v = DATA["verdicts"]
    check(v["callback_is_memcpy_adapter"] is True, "veredicto: adaptador")
    check(v["callback_is_data_specific"] is False, "veredicto: no especifico")
    check(v["callback_shared_with_other_services"] is False, "veredicto: un usuario")
    check(v["copy_length_available_per_entry"] == 13, "veredicto: 13")
    check(v["direction"].startswith("INFERENCIA"), "veredicto: direccion es inferencia")
    check(v["call_site_visible"] is False, "veredicto: call site no visible")

    print(f"{CHECKS} comprobaciones OK")


if __name__ == "__main__":
    main()
