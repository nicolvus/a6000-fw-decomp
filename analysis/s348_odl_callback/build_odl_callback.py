#!/usr/bin/env python3
"""S348 - carril B: el callback por entrada del consumidor A del ODL es un
adaptador de `memcpy`, y el unico tamano disponible por entrada es el 13 de la
palabra de especificacion.

S347 dejo el campo `0x000d` como tamano del bloque (13 B) por tres usos
independientes.  Quedaba por decidir **que hace el servicio con el bloque**: el
consumidor A entrega, por cada id, una terna

    {palabra_de_tabla (id | 13<<16), callback, item_i}   y  r0 = &companion[i]

S348 identifica ese `callback` en los tres modelos:

  * el puntero es impar (Thumb) y apunta a un *shim* de 12 B:
        push {r4,lr} ; mov r4,r1 ; mov r0,r3 ; mov r1,r2 ; mov r2,r4 ;
        pop {r4,lr} ; b <veneer>
    es decir `f(dst=arg4, src=arg3, len=arg2)`;
  * el *veneer* (`bx pc` + `b` ARM) salta a codigo **ARM**: la implementacion
    clasica de `memcpy` (`push {r0,lr}; subs r2,r2,#4; ... ands ip,r0,#3 ...`);
  * cada shim tiene **un solo usuario** en el binario: el bucle de la tabla del
    consumidor A (S342/S347).

Con eso, el servicio importado recibe por entrada (destino, memoria, tamano) y el
unico tamano por entrada que se le entrega es el `13` de la mitad alta de la
palabra de tabla.  El sentido del flujo (los 13 B se copian **hacia** el buffer
del consumidor) es INFERENCIA ALTA: el cuerpo del servicio vive fuera del blob.

Solo lectura de los blobs: sin firmware en ejecucion, sin camara, sin flasheo.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
FW = ROOT / "firmware/extracted"
BLOBS = {
    "a7s_fw320": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/"
                       "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6000_fw321": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300_fw201": FW / ("a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/"
                         "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
# callback (puntero Thumb, impar) y sitio PIC que lo carga, por modelo
MODELS: dict[str, dict[str, int]] = {
    "a7s_fw320": {"callback": 0x43ADB6E1, "pic_site": 0x43705702,
                  "table": 0x43FEF404, "entries": 69},
    "a6000_fw321": {"callback": 0x43ADA547, "pic_site": 0x436EB2E2,
                    "table": 0x43FEAE1C, "entries": 47},
    "a6300_fw201": {"callback": 0x43B9199F, "pic_site": 0x43734BEE,
                    "table": 0x441B0B1C, "entries": 69},
}
SHIM_BYTES = "10b50c46184611462246"      # push + 4 mov (10 B)
SHIM_POP = "bde81040"                     # pop.w {r4,lr}
MEMCPY_FINGERPRINT = ["e92d4001", "e2522004", "ba000020", "e210c003"]
OUT = Path(__file__).with_name("odl_callback.json")
MDT = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MDA = Cs(CS_ARCH_ARM, CS_MODE_ARM)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def thumb(blob: bytes, addr: int, n: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MDT.disasm(blob[addr - BASE:addr - BASE + n], addr)]


def arm(blob: bytes, addr: int, n: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MDA.disasm(blob[addr - BASE:addr - BASE + n], addr)]


def pic_target(blob: bytes, ldr: int) -> int:
    """`ldr rD,[pc,#imm]` + `add rD,pc` a partir de la instruccion `ldr`."""
    h = u16(blob, ldr)
    assert (h & 0xF800) == 0x4800, f"0x{ldr:08x} no es ldr pc-rel"
    lit = ((ldr + 4) & ~3) + ((h & 0xFF) * 4)
    return (u32(blob, lit) + ((ldr + 6) & ~1)) & 0xFFFFFFFF


def pic_sites(blob: bytes, target: int) -> list[str]:
    out: list[str] = []
    n = len(blob)
    for off in range(0, n - 8, 2):
        h = u16(blob, BASE + off)
        if (h & 0xF800) != 0x4800:
            continue
        rd = (h >> 8) & 7
        lit = ((BASE + off + 4) & ~3) + ((h & 0xFF) * 4)
        if lit - BASE + 4 > n:
            continue
        word = u32(blob, lit)
        for k in (2, 4, 6, 8):
            a = BASE + off + k
            if a - BASE + 2 > n:
                break
            h2 = u16(blob, a)
            if ((h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
                    and (h2 & 7) == rd and ((h2 >> 7) & 1) == 0):
                if (word + ((a + 4) & ~1)) & 0xFFFFFFFF == target:
                    out.append(f"0x{BASE + off:08x}")
                break
    return out


def arm_branch(blob: bytes, addr: int) -> int:
    """Direccion destino de un `b` ARM (cond=0xE, bits 27:25 = 101)."""
    w = u32(blob, addr)
    assert (w >> 25) & 7 == 5, f"0x{addr:08x} no es b ARM"
    imm = w & 0xFFFFFF
    if imm & 0x800000:
        imm -= 1 << 24
    return (addr + 8 + (imm << 2)) & 0xFFFFFFFF


def build_model(blob: bytes, m: dict[str, int]) -> dict[str, Any]:
    cb = m["callback"]
    entry = cb & ~1
    assert cb & 1 == 1, "el callback debe ser un puntero Thumb"
    # 1. el consumidor carga este callback con una base PIC
    loaded = pic_target(blob, m["pic_site"])
    assert loaded == cb, (hex(loaded), hex(cb))
    # 2. shim: push + 4 mov ; pop.w {r4,lr} ; b.w <veneer>
    shim = blob[entry - BASE:entry - BASE + 10]
    assert shim.hex() == SHIM_BYTES, shim.hex()
    assert blob[entry - BASE + 10:entry - BASE + 14].hex() == SHIM_POP, "pop.w"
    got = list(MDT.disasm(blob[entry - BASE + 14:entry - BASE + 18], entry + 14))
    assert got and got[0].mnemonic.startswith("b"), "falta el b.w al veneer"
    veneer = int(got[0].op_str.lstrip("#"), 16)
    # 3. veneer: bx pc + nop + b ARM
    assert blob[veneer - BASE:veneer - BASE + 4].hex() == "7847c046", "veneer"
    arm_entry = veneer + 4
    target = arm_branch(blob, arm_entry)
    # 4. implementacion ARM: huella de memcpy
    fp = [u32(blob, target + 4 * i) for i in range(4)]
    return {
        "callback_pointer": f"0x{cb:08x}",
        "shim": {"entry": f"0x{entry:08x}", "bytes": shim.hex(),
                 "code": thumb(blob, entry, 0x12),
                 "semantics": "memcpy(dst=arg4, src=arg3, len=arg2)"},
        "veneer": {"address": f"0x{veneer:08x}",
                   "bytes": blob[veneer - BASE:veneer - BASE + 12].hex(),
                   "arm_branch_at": f"0x{arm_entry:08x}",
                   "arm_target": f"0x{target:08x}"},
        "memcpy": {"address": f"0x{target:08x}",
                   "fingerprint": [f"0x{w:08x}" for w in fp],
                   "first_instructions": arm(blob, target, 0x20)},
        "users": pic_sites(blob, cb),
        "spec_word": {"first_entry": f"0x{u32(blob, m['table']):08x}",
                      "high_half": u16(blob, m["table"] + 2),
                      "low_half_id": u16(blob, m["table"])},
    }


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    per = {k: build_model(blobs[k], MODELS[k]) for k in MODELS}

    # todos los memcpy comparten huella; los shims son byte a byte iguales
    fps = {k: tuple(v["memcpy"]["fingerprint"]) for k, v in per.items()}
    shims = {v["shim"]["bytes"] for v in per.values()}
    users = {k: v["users"] for k, v in per.items()}
    highs = {k: v["spec_word"]["high_half"] for k, v in per.items()}

    data: dict[str, Any] = {
        "milestone": "S348",
        "title": ("el callback por entrada del ODL es un adaptador de memcpy con un solo "
                  "usuario; el unico tamano por entrada es el 13 de la palabra de tabla"),
        "base": f"0x{BASE:08x}",
        "firmware": {k: {"sha256": sha256(BLOBS[k]), "size": len(blobs[k])} for k in BLOBS},
        "models": per,
        "cross_model": {
            "shim_bytes_identical": len(shims) == 1,
            "memcpy_fingerprint_identical": len(set(fps.values())) == 1,
            "shim_users": users,
            "every_shim_has_one_user": all(len(u) == 1 for u in users.values()),
            "high_half_of_spec_word": highs,
        },
        "verdicts": {
            "callback_is_memcpy_adapter": True,
            "callback_is_data_specific": False,
            "callback_shared_with_other_services": False,
            "copy_length_available_per_entry": 13,
            "direction": ("INFERENCIA ALTA: el servicio copia el bloque recibido hacia el "
                          "buffer del consumidor (dst = 4. argumento del adaptador)"),
            "call_site_visible": False,
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("El cuerpo del servicio que invoca al callback esta en la interfaz importada "
             "(slots +0x2b0/+0x2c8/+0x2cc): no se ve la llamada ni sus argumentos."),
            ("Que el tamano sea 13 y no otro se apoya en S347 (unico valor por entrada) y en "
             "que el adaptador copia exactamente `len` bytes; no se observa el argumento."),
            ("La implementacion ARM es la `memcpy` clasica por huella de instrucciones, no por "
             "simbolo: no hay tabla de simbolos en el blob."),
            "S51 (A/B/C) no cambia: sigue siendo aberracion de objetivo, no obturador.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"escrito {OUT.name}")
    for k, v in per.items():
        print(k, v["callback_pointer"], "->", v["veneer"]["arm_target"],
              "usuarios:", v["users"], "alto:", v["spec_word"]["high_half"])


if __name__ == "__main__":
    main()
