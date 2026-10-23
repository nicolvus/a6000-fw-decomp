#!/usr/bin/env python3
"""S328 - carril B: la segunda matriz (slot 0x44026088) no tiene productor estatico.

S321/S324 documentaron un segundo bucle en el accesor de la matriz, abierto por la puerta
`sub != 0` (`obj+0x2b0` A7S / `+0x266` A6000) y alimentado por un segundo slot. Esta sesion
comprueba quien llena ese slot/tabla y que ocurre con el blob tal cual.

Resultado (A7S y A6000, simetrico):

* El slot `0x44026088` (A7S) contiene `0x43e8de00`; el slot `0x44026694` (A6000) contiene
  `0x43e80160`. Son los **unicos** literales con esos valores: nadie reescribe el slot.
* El offset `0x1b48` (A7S) / `0x77b0` (A6000) que resuelve el slot aparece en **un solo**
  sitio por firmware: el propio bucle del accesor (`0x436f394e` / `0x436d65a0`). No hay
  otros usuarios.
* Ambas tablas estan **a cero** en el blob y su primera palabra es la cabecera-destino del
  bucle: con el blob tal cual, el bucle termina en la primera iteracion → **no escribe nada**.

Conclusion: la segunda matriz solo podria activarse con un productor en runtime (otro
modulo, DMA o inicializacion no visible). Su efecto para `sub != 0` (p. ej. `0x4f`) queda
**NO_VERIFICADO**.

No ejecuta firmware ni toca la camara: solo lectura de los blobs.
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
OUT = Path(__file__).with_name("second_matrix.json")

CASES = {
    "a7s_fw320": {"slot": 0x44026088, "base": 0x44024540, "offset": 0x1B48,
                  "site": 0x436F394E},
    "a6000_fw321": {"slot": 0x44026694, "base": 0x4401EEE4, "offset": 0x77B0,
                    "site": 0x436D65A0},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(blob: bytes, a: int) -> int:
    return struct.unpack_from("<H", blob, a - BASE)[0]


def u32(blob: bytes, a: int) -> int:
    return struct.unpack_from("<I", blob, a - BASE)[0]


def literal_sites(blob: bytes, value: int) -> list[str]:
    out: list[str] = []
    n = len(blob)
    for off in range(0, n - 3, 2):
        addr = BASE + off
        h = u16(blob, addr)
        if (h & 0xF800) != 0x4800:
            continue
        lit = ((addr + 4) & ~3) + (h & 0xFF) * 4
        if not (0 <= lit - BASE < n - 3):
            continue
        if u32(blob, lit) == value:
            out.append(f"0x{addr:08x}")
    return out


def abs_refs(blob: bytes, value: int) -> list[str]:
    pat = struct.pack("<I", value)
    out: list[str] = []
    i = 0
    while True:
        j = blob.find(pat, i)
        if j < 0:
            return out
        out.append(f"0x{BASE + j:08x}")
        i = j + 1


def main() -> None:
    blobs = {"a7s_fw320": A7S.read_bytes(), "a6000_fw321": A6000.read_bytes()}
    result: dict[str, Any] = {
        "milestone": "S328",
        "title": "La segunda matriz no tiene productor estatico y su bucle no ejecuta con "
                 "el blob tal cual",
        "base": f"0x{BASE:08x}",
        "firmware": {
            "a7s_fw320": {"sha256": sha256(A7S), "size": len(blobs["a7s_fw320"])},
            "a6000_fw321": {"sha256": sha256(A6000), "size": len(blobs["a6000_fw321"])},
        },
        "cases": {},
        "verdict": {
            "static_producer": False,
            "loop_executes_on_blob": False,
            "gate": "sub != 0 (S324)",
            "sub_effect": "NO_VERIFICADO",
            "s51": "sin cambios (A=NO, B=NO, C=NO)",
        },
        "scope_limit": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("La tabla podria llenarse en runtime desde otro modulo, por DMA o por una "
             "inicializacion no visible en av-cam: no se descarta."),
            ("No se interpreta el contenido futuro de la segunda matriz ni su efecto sobre "
             "los modos con sub != 0."),
        ],
    }
    for name, c in CASES.items():
        blob = blobs[name]
        slot_value = u32(blob, c["slot"])
        table = blob[slot_value - BASE:slot_value - BASE + 0x40]
        entry: dict[str, Any] = {
            "slot": f"0x{c['slot']:08x}",
            "slot_base": f"0x{c['base']:08x}",
            "offset_le": f"0x{c['offset']:x}",
            "slot_value": f"0x{slot_value:08x}",
            "offset_sites": literal_sites(blob, c["offset"]),
            "expected_site": f"0x{c['site']:08x}",
            "slot_value_refs": abs_refs(blob, slot_value),
            "table_nonzero_bytes_64": sum(1 for b in table if b),
            "table_first_word": f"0x{u32(blob, slot_value):08x}",
        }
        result["cases"][name] = entry
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, e in result["cases"].items():
        print(f"{name}: slot {e['slot']} -> {e['slot_value']}, "
              f"offset en {e['offset_sites']}, ceros={e['table_nonzero_bytes_64']}")


if __name__ == "__main__":
    main()
