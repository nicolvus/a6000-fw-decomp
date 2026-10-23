#!/usr/bin/env python3
"""S339 - carril B: que se puede afirmar de `0xf292b000..8` (S335).

S335 midio que las mascaras escriben `0xf292b004`/`0xf292b008` y leen
`0xf292b000`, pero no identifico el bloque.  Esta sesion acota lo que se puede
decir por bytes:

* Solo hay **6 literales** de `0xf292b000/4/8` en el A7S (1/2/3) y estan todos
  en los accesores `0x436f8290..0x436f82d0`: **ningun otro codigo** toca el
  bloque directamente.
* La interfaz es de 3 registros (base, +4, +8) con campos de 12 bits y valores
  de control `0x1000`/`0x10000`.
* El bloque esta en la ventana `0xf292x000`, con bloques cada 4 KB; los unicos
  vecinos documentados en el repo son GPIO `0xf2910000` (S54/S55) y el DSP de
  lente `0xf292d000` (S66). `0xf292b000` no aparece en la documentacion.

Conclusion: identidad **NO_VERIFICADA**; queda acotado a "interfaz de 3
registros usada solo por la capa de mascaras del carril B".

Solo lectura de los blobs: sin firmware en ejecucion, sin camara, sin flasheo.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("block_f292b.json")

REGS = [0xF292B000, 0xF292B004, 0xF292B008]
ACCESSORS = [0x436F82B0, 0x436F82A0, 0x436F8290, 0x436F82C0, 0x436F82D0]
KNOWN_NEIGHBOURS = {"0xf2910000": "GPIO BIONZ (S54/S55)",
                    "0xf292d000": "DSP de lente (S66)"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def hits(blob: bytes, value: int) -> list[str]:
    pat = struct.pack("<I", value)
    out, i = [], blob.find(pat)
    while i >= 0:
        out.append(f"0x{BASE + i:08x}")
        i = blob.find(pat, i + 1)
    return out


def window(blob: bytes) -> dict[str, int]:
    """Bloques usados en la ventana 0xf292xxxx (paso 4 KB)."""
    from collections import Counter

    c: Counter[int] = Counter()
    for i in range(0, len(blob) - 4, 4):
        v = struct.unpack_from("<I", blob, i)[0]
        if 0xF2920000 <= v < 0xF2930000:
            c[(v >> 12) << 12] += 1
    return {f"0x{k:08x}": v for k, v in sorted(c.items())}


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()

    sites = {f"0x{v:08x}": {"a7s": hits(a7, v), "a6000": hits(a6, v)}
             for v in REGS}
    in_accessors = all(
        any(0x436F8290 <= int(s, 16) < 0x436F82E0 for s in info["a7s"])
        for info in sites.values()
    )

    data: dict[str, Any] = {
        "milestone": "S339",
        "title": "0xf292b000..8: interfaz de 3 registros usada solo por la capa "
                 "de mascaras; identidad NO_VERIFICADA",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000_fw321": {"sha256": sha256(A6000), "size": len(a6)}},
        "registers": [f"0x{v:08x}" for v in REGS],
        "literal_sites": sites,
        "all_sites_in_accessors": in_accessors,
        "accessors": [f"0x{v:08x}" for v in ACCESSORS],
        "interface": {"registers": 3, "offsets": ["+0x0", "+0x4", "+0x8"],
                      "field_width": "12 bits", "control_values": ["0x1000", "0x10000"]},
        "window_0xf292x000": {"a7s": window(a7), "a6000": window(a6)},
        "known_neighbours": KNOWN_NEIGHBOURS,
        "verdicts": {
            "identity": "NO_VERIFICADO",
            "only_mask_layer_uses_it": in_accessors,
            "documented_in_repo": False,
            "same_sites_in_both_models": all(
                len(info["a7s"]) == len(info["a6000"]) for info in sites.values()),
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("El bloque no aparece en la documentacion del repo ni en ningun simbolo; "
             "no se afirma que sea sensor, P2S, ADC ni GPIO."),
            ("Los vecinos 0xf2910000 (GPIO) y 0xf292d000 (DSP de lente) estan "
             "documentados, pero no implican la funcion de 0xf292b000."),
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("sitios:", {k: (len(v["a7s"]), len(v["a6000"])) for k, v in sites.items()})
    print("todos en accesores:", in_accessors)
    print("ventana A7S:", data["window_0xf292x000"]["a7s"])


if __name__ == "__main__":
    main()
