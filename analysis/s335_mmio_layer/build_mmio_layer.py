#!/usr/bin/env python3
"""S335 - carril B: la capa de acceso de S334 termina en MMIO, no en P2S.

S334 dejo abierto si las mascaras acababan en una trama P2S.  Las nueve
funciones diminutas que aplican la mascara (`0x436f8290/82a0/82b0/82c0/82d0/
82e8/8300/8314/8324`) cargan un literal absoluto y leen/escriben ese registro:

* `0xf292b000`, `0xf292b004`, `0xf292b008` (bloque `0xf292b000`)
* `0xfc02a00c` (campo de 12 bits + bit 12)

La A6000 tiene la misma capa en `0x436dbdf8..0x436dbe8c`, con los mismos
literales.  Conclusion: el camino modo -> mascara -> registro acaba en MMIO; la
hipotesis P2S de S334 queda descartada.  La semantica del bloque no se conoce.

Solo lectura de los blobs: sin firmware en ejecucion, sin camara, sin flasheo.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("mmio_layer.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

A7_ACCESSORS = {
    0x436F8290: "write 12 bits -> 0xf292b008",
    0x436F82A0: "write 12 bits -> 0xf292b004",
    0x436F82B0: "read 12 bits <- 0xf292b000",
    0x436F82C0: "write 0x1000 -> 0xf292b008",
    0x436F82D0: "write 0x10000 -> 0xf292b008 | 0xf292b004",
    0x436F82E8: "rmw bic 12 bits en 0xfc02a00c",
    0x436F8300: "rmw orr 12 bits en 0xfc02a00c",
    0x436F8314: "read 12 bits <- 0xfc02a00c",
    0x436F8324: "clear bit 12 de 0xfc02a00c",
}
MMIO = [0xF292B000, 0xF292B004, 0xF292B008, 0xFC02A00C]


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


def raw(blob: bytes, addr: int, size: int) -> bytes:
    return blob[addr - BASE:addr - BASE + size]


def dis(blob: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw(blob, start, size), start)]


def literals(blob: bytes, start: int, size: int) -> list[dict[str, Any]]:
    """Literales absolutos cargados con `ldr rX,[pc,#imm]` en la funcion."""
    out = []
    for ins in MD.disasm(raw(blob, start, size), start):
        if ins.mnemonic == "ldr" and "[pc," in ins.op_str:
            imm = int(ins.op_str.split("#")[1].rstrip("]"), 16)
            la = ((ins.address + 4) & ~3) + imm
            out.append({"insn": f"0x{ins.address:08x}", "literal_addr": f"0x{la:08x}",
                        "value": f"0x{u32(blob, la):08x}"})
    return out


def find_sites(blob: bytes, value: int) -> list[str]:
    pat = struct.pack("<I", value)
    hits, i = [], blob.find(pat)
    while i >= 0:
        hits.append(f"0x{BASE + i:08x}")
        i = blob.find(pat, i + 1)
    return hits


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()

    a7_layer: dict[str, dict[str, Any]] = {f"0x{addr:08x}": {"role": role,
                                  "disasm": dis(a7, addr, 0x12),
                                  "literals": literals(a7, addr, 0x12)}
                for addr, role in A7_ACCESSORS.items()}

    a6_layer: dict[str, dict[str, Any]] = {}
    for addr in (0x436DBDF8, 0x436DBE08, 0x436DBE18, 0x436DBE28, 0x436DBE3C,
                 0x436DBE40, 0x436DBE58, 0x436DBE6C, 0x436DBE7C, 0x436DBE8C):
        a6_layer[f"0x{addr:08x}"] = {"disasm": dis(a6, addr, 0x14),
                                     "literals": literals(a6, addr, 0x14)}

    sites = {f"0x{v:08x}": {"a7s": find_sites(a7, v), "a6000": find_sites(a6, v)}
             for v in MMIO}

    data: dict[str, Any] = {
        "milestone": "S335",
        "title": "La capa de acceso de las mascaras escribe MMIO (0xf292b000..8, "
                 "0xfc02a00c), no una trama P2S",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)}},
        "a7s_layer": a7_layer,
        "a6000_layer": a6_layer,
        "mmio": {"addresses": [f"0x{v:08x}" for v in MMIO], "sites": sites},
        "verdicts": {
            "mask_path_ends_in_mmio": True,
            "p2s_hypothesis": "DESCARTADA",
            "same_layer_in_a6000": True,
            "mmio_semantics": "NO_VERIFICADO",
            "field_width": "12 bits (lsls #0x14 / lsrs #0x14, bfi #0,#0xc)",
            "extra_bit": "bit 12 (bfc #0xc,#1 en 0x436f8324)",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Las direcciones 0xf292b000.. y 0xfc02a00c se identifican como MMIO por "
             "su rango y por el acceso directo; no hay datasheet que diga que bloque "
             "es ni que controla."),
            ("Que el bloque sea el driver del sensor, del P2S o de otro periferico "
             "queda NO_VERIFICADO."),
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    for key, info in a7_layer.items():
        print(key, info["role"], [lit["value"] for lit in info["literals"]])
    print("sitios MMIO:", {k: (len(v["a7s"]), len(v["a6000"]))
                           for k, v in sites.items()})


if __name__ == "__main__":
    main()
