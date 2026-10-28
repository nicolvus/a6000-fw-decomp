#!/usr/bin/env python3
"""E25-19b — cadena estática hacia `cap` (av-cam.bin) y comprobación en RAM, solo lectura.

Cadena derivada de los bytes: GOT 0x440267bc → matriz de 17 gestores (0x43ff8f70) → gestor E
(objeto estático, cola con centinela en E+0x14) → nodo → carga útil (nodo+8) cuyo primer campo es el
mensaje M → `cap = [M]` (`ldr r0,[r0]`, 0x43ae75dc). Con `--live` lee la matriz y los centinelas
(Telnet de E25-19; nunca escribe). Un centinela autoapuntado = cola vacía.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e25_19_readonly import OUTDIR, Telnet, verify_originals

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE, GOT_BASE = 0x43541000, 0x4401EEE4
RAM_OFF = 0x40000000


def word(data: bytes, va: int) -> int:
    return struct.unpack_from("<I", data, va - BASE)[0]


def pc_literal(data: bytes, ldr_va: int, disp: int, add_va: int) -> int:
    """`ldr rX,[pc,#disp]` seguido de `add rX,pc` (PIC de Thumb)."""
    return (word(data, ((ldr_va + 4) & ~3) + disp) + add_va + 4) & 0xFFFFFFFF


def static_chain(data: bytes) -> dict:
    """Dirección de la matriz de gestores a partir de 0x437e50d8 y de la tabla de selectores (0x437e5374)."""
    got = pc_literal(data, 0x437E50D8, 0x38, 0x437E50DE)
    slot = (got + word(data, ((0x437E50E2 + 4) & ~3) + 0x34)) & 0xFFFFFFFF
    arr = word(data, slot)
    sel = pc_literal(data, 0x437E5374, 0xCC, 0x437E537A)
    return {
        "got_base": got, "slot_matriz": slot, "matriz": arr,
        "gestores": [word(data, arr + 4 * i) for i in range(17)],
        "tabla_selectores": sel,
        "selectores": {word(data, sel + 4 + 8 * i + 4): word(data, sel + 4 + 8 * i) for i in range(16)},
    }


def live(tr: Telnet, chain: dict) -> dict:
    """Matriz y centinelas de cola de cada gestor (E+0x14 → [centinela] == centinela ⇒ vacía)."""
    arr = struct.unpack("<17I", tr.read(chain["matriz"] + RAM_OFF, 68))
    out: dict = {"matriz": arr, "gestores": {}}
    for e in sorted(set(arr) - {0}):
        nxt, prv = struct.unpack("<II", tr.read(e + RAM_OFF + 0x14, 8))
        out["gestores"][f"{e:#x}"] = {"next": f"{nxt:#x}", "prev": f"{prv:#x}", "vacia": nxt == prv == e + 0x14}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--confirm-readonly", action="store_true", required=True)
    a = ap.parse_args()
    ch = static_chain(BIN.read_bytes())
    res: dict = {"schema": "e25-19b/v1", "estatico": {k: (f"{v:#x}" if isinstance(v, int) else v) for k, v in ch.items()
                                                      if k not in ("gestores", "selectores")},
                 "gestores": [f"{g:#x}" for g in ch["gestores"]],
                 "selectores": {str(k): f"{v:#x}" for k, v in ch["selectores"].items()}}
    if a.live:
        tr = Telnet()
        try:
            assert verify_originals(tr)["ok"], "originales T050 alterados"
            res["vivo"] = live(tr, ch)
        finally:
            tr.close()
    out = OUTDIR.parent / "e25-19b" / ("cadena-vivo.json" if a.live else "cadena-estatica.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
