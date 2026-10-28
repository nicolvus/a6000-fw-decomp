#!/usr/bin/env python3
"""E25-19f P1 — emula EndExps (0x4354a678) con el código real sobre la instantánea física de RAM.

Caso LV: r0 = objeto vivo 0x43ee5184 (c38=1) → valida el emulador contra el valor físico `74e`.
Caso CAP: r0 = copia de `cap` en vuelo (bytes físicos 0..0xe00); se fuerza c38 sólo con --forzar-c38 (contrafactual, etiquetado).
Se registran sp+0x30c..0x31a (salida de 0x43af54d8/0x43af5504), el halfword enviado a `strh [r4,#0x74e]` y las llamadas sustituidas.
Uso: emular_endexps.py SNAPSHOT.bin {lv|cap} [CAP.json] [--forzar-c38]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from emu import Emu  # type: ignore[import-not-found]
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_SP

SNAP_BASE = 0x43D00000
LV = 0x43EE5184
FAKE_CAP = 0x43F80000  # hueco libre en la instantánea; se verifica que está a cero
STOPS = {  # dependencias de registro/log sustituidas por r0=0 (documentado en el informe)
    0x43728D28: 1, 0x43902718: 0, 0x4380FCAC: 0, 0x43901A8C: 0, 0x43561540: 0, 0x43560DC4: 0, 0x43AE7482: 0,
}


def correr(snap: Path, caso: str, cap_json: Path | None = None, forzar_c38: bool = False) -> dict:
    e = Emu({SNAP_BASE: snap.read_bytes()})
    e.stubs.update(STOPS)
    r4 = LV
    if caso == "cap":
        j = json.loads(cap_json.read_text())
        buf = bytes.fromhex(j["muestras"][0]["0x0"])
        assert not any(e.mu.mem_read(FAKE_CAP, 0xE00)), "hueco no vacío"
        e.wr(FAKE_CAP, buf)
        if forzar_c38:
            e.wr(FAKE_CAP + 0xC38, b"\x01")
        r4 = FAKE_CAP
    cap_ini = bytes(e.mu.mem_read(r4 + 0x73C, 0x20))
    vis = {}

    def sp_dump(emu, a):
        sp = emu.mu.reg_read(UC_ARM_REG_SP)
        vis[hex(a)] = bytes(emu.mu.mem_read(sp + 0x30C, 0x10)).hex()

    e.hooks_pc[0x4354B096] = sp_dump  # justo antes de cargar sp+0x312
    e.hooks_pc[0x4354AF78] = lambda emu, a: vis.setdefault("rama_bit2", "bloque1" if 0 else "visto")
    def salta(emu, a):  # omite el bloque de preparación 0x4354a78a..0x4354a9a2 (periféricos/ventanas); no produce sp+0x2c8/sp+0x44
        emu.mu.reg_write(UC_ARM_REG_PC, 0x4354A9A2 | 1)

    e.hooks_pc[0x4354A78A] = salta
    e.trazar = True
    try:
        e.call(0x4354A678, r4, count=5_000_000)
        fin = "ok"
    except Exception as exc:  # noqa: BLE001 - se conserva el motivo
        fin = f"excepcion {exc}"
    pcs = set(e.pcs)
    st74e = [(hex(a), s, hex(v)) for a, s, v in e.escrituras if r4 + 0x740 <= a < r4 + 0x758]
    return {
        "caso": caso, "forzar_c38": forzar_c38, "fin": fin, "instrucciones": len(e.pcs),
        "alcanza_aea4_prod": 0x4354AEA4 in pcs, "alcanza_b0ac": 0x4354B0AC in pcs, "alcanza_af88": 0x4354AF88 in pcs,
        "alcanza_b23a_rama_B": 0x4354B23A in pcs, "sp30c_31a": vis.get("0x4354b096"),
        "cap_73c_antes": cap_ini.hex(), "cap_73c_despues": bytes(e.mu.mem_read(r4 + 0x73C, 0x20)).hex(),
        "stores_740_758": st74e, "llamadas_sustituidas": [[hex(x) for x in c] for c in e.llamadas[:40]],
        "mem_no_mapeada": sorted({hex(a & ~0xFFF) for a in e.auto})[:20],
    }


if __name__ == "__main__":
    a = sys.argv[1:]
    res = correr(Path(a[0]), a[1], Path(a[2]) if len(a) > 2 and not a[2].startswith("--") else None, "--forzar-c38" in a)
    print(json.dumps(res, indent=1))
