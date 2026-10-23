#!/usr/bin/env python3
"""S338 - carril B: identificacion del bloque MMIO 0xfc02a000 (DFE/CISIF).

S335 midio que las mascaras del carril B acaban en `0xfc02a00c` y en
`0xf292b000..8`.  Esta sesion identifica el primer bloque con evidencia del
propio repo y de los bytes:

* El bloque `0xfc02a000` aparece como literal en ambos firmwares (A7S
  `0x436f2034`/`0x436f2044`; A6000 `0x436d2cbc`/`0x436d2d78`).
* En el A7S, `0x436f2014` devuelve `base+8` (`0xfc02a008`) y `0x436f202c`
  escribe `base` (`0xfc02a000`).
* El mapa Ghidra del repo (`analysis/ghidra/efcs-dfe-base-map.json`,
  `FUN_436d1c98`, cadena `DFE_INIT_Start`) hace `_DAT_fc02a008 |= 8`: el bloque
  es el **DFE**.
* `S56-B` documento que el mismo par de tablas (`0x43bc20dc`/`0x43bc2248`) y el
  mismo colapso de 12 pares (carril, bit) → mascara u16 alimentan el **CISIF**
  (`SIF SetSyncCode`, `SIFSyncCode`).

Conclusion: la cadena del carril B modula un registro del bloque DFE/CISIF, no
la RAM del formateador P2S (`0xfc088300`, S56).  `0xf292b000` sigue sin
identificar.

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
OUT = Path(__file__).with_name("block_identity.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

DFE_BASE = 0xFC02A000
DFE_REG = 0xFC02A00C
UNKNOWN_BLOCK = 0xF292B000
STRINGS = [b"DFE_INIT_Start", b"DFECore", b"SIFSyncCode", b"SIF SetSyncCode",
           b"CISIF", b"Synccode"]
A7_DFE_CODE = {"getter_base_plus_8": 0x436F2014, "writer_base": 0x436F202C}
A6_DFE_CODE = {"getter_base_plus_8": 0x436D2C9C, "writer_base": 0x436D2CB4}
GHIDRA_MAP = ROOT / "analysis/ghidra/efcs-dfe-base-map.json"
S56_DOC = ROOT / "docs/capture/s56-cisif-dfe-controller.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def raw(blob: bytes, addr: int, size: int) -> bytes:
    return blob[addr - BASE:addr - BASE + size]


def dis(blob: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw(blob, start, size), start)]


def literal_sites(blob: bytes, value: int) -> list[str]:
    pat = struct.pack("<I", value)
    hits, i = [], blob.find(pat)
    while i >= 0:
        hits.append(f"0x{BASE + i:08x}")
        i = blob.find(pat, i + 1)
    return hits


def string_sites(blob: bytes, needle: bytes) -> list[str]:
    hits, i = [], blob.find(needle)
    while i >= 0:
        hits.append(f"0x{BASE + i:08x}")
        i = blob.find(needle, i + 1)
    return hits


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()

    # citas de los documentos del repo (evidencia secundaria)
    ghidra_hit = None
    if GHIDRA_MAP.exists():
        text = GHIDRA_MAP.read_text(encoding="utf-8", errors="ignore")
        idx = text.find("fc02a008")
        if idx >= 0:
            ghidra_hit = text[max(0, idx - 160):idx + 40]
    s56_text = S56_DOC.read_text(encoding="utf-8") if S56_DOC.exists() else ""
    s56_lines = [line for line in s56_text.splitlines()
                 if "0x43bc20dc" in line or "SIFSyncCode" in line]

    data: dict[str, Any] = {
        "milestone": "S338",
        "title": "Las mascaras del carril B acaban en el bloque DFE/CISIF "
                 "(0xfc02a000); 0xf292b000 sigue sin identificar",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)}},
        "dfe_block": {
            "base": f"0x{DFE_BASE:08x}", "register": f"0x{DFE_REG:08x}",
            "literal_sites": {"a7s": literal_sites(a7, DFE_BASE),
                              "a6000": literal_sites(a6, DFE_BASE)},
            "a7s_code": {name: {"address": f"0x{addr:08x}",
                                "disasm": dis(a7, addr, 0x1C)}
                         for name, addr in A7_DFE_CODE.items()},
            "a6000_code": {name: {"address": f"0x{addr:08x}",
                                  "disasm": dis(a6, addr, 0x1C)}
                           for name, addr in A6_DFE_CODE.items()},
        },
        "strings": {needle.decode("latin-1"): {
            "a7s": string_sites(a7, needle),
            "a6000": string_sites(a6, needle)} for needle in STRINGS},
        "repo_evidence": {
            "ghidra_map": str(GHIDRA_MAP.relative_to(ROOT)),
            "ghidra_snippet": ghidra_hit,
            "s56_doc": str(S56_DOC.relative_to(ROOT)),
            "s56_lines": s56_lines[:4],
        },
        "unknown_block": {"base": f"0x{UNKNOWN_BLOCK:08x}",
                          "status": "NO_VERIFICADO",
                          "note": "unico vecino documentado en 0xf292xxxx: DSP de "
                                  "lente 0xf292d000 (S66)"},
        "verdicts": {
            "dfe_register": f"0x{DFE_REG:08x} pertenece al bloque 0x{DFE_BASE:08x}",
            "dfe_block_identification": "INFERENCIA ALTA (mapa Ghidra + S56-B + "
                                        "cadenas CISIF en ambos firmwares)",
            "block_is_cisif_receiver": True,
            "p2s_transport_affected": False,
            "unknown_block_identified": False,
        },
        "corrections": [
            ("S334 dejo como INFERENCIA que las mascaras acabaran en una trama P2S; "
             "se descarta: el destino es un registro del bloque DFE/CISIF."),
            ("El par de tablas 0x43bc20dc/0x43bc2248 de S332 es el mismo que S56-B "
             "documento como CISIF (sync codes / carriles), no una tabla de "
             "exposicion."),
        ],
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("La identificacion DFE/CISIF se apoya en el mapa Ghidra del repo y en "
             "S56-B (evidencia derivada), ademas de las cadenas presentes en ambos "
             "blobs; no hay datasheet del bloque 0xfc02a000."),
            "0xf292b000 no se ha identificado.",
            "No se asigna significado fisico a los bits del registro.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("sitios 0xfc02a000:", data["dfe_block"]["literal_sites"])
    print("cadenas:", {k: (len(v["a7s"]), len(v["a6000"]))
                       for k, v in data["strings"].items()})
    print("ghidra:", (ghidra_hit or "")[:120].replace("\n", " "))


if __name__ == "__main__":
    main()
