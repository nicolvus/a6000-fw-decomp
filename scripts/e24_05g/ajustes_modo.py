"""E24-05g: origen de 0x11/0x14 (FSM de ajustes), de 0x17 (cambio de modo) y byte 0 del 0x0b (solo lectura de bytes).

Reproducible: `python scripts/e24_05g/ajustes_modo.py` guarda analysis/e24-05g/ajustes_modo.json.
Reutiliza el grafo de llamadas de E24-05f; las direcciones raíz son las del informe, el resto se deriva de instrucciones/tablas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[0] / "e24_05f"), str(HERE.parents[0] / "e24_05"), str(HERE.parents[0] / "e24_05d")]

import emisores as E
from bz import Bz
from dwn import ROOT, Core

CURTAIN = {0x20CB2, 0x20CD4, 0x20D00, 0x20D26, 0x20C90, 0x20C4A}  # primitivas de bobina/cortina (S21/S54)
BAD = E.GATE | E.MOTOR | set(E.OUTER_STARTERS) | CURTAIN
ROWS, HOOKS = 0x29514, 0x282FC  # tabla {manejador,flags} de 8 B (44 filas) y lista de ganchos tras cada trama 0x31
T2 = 0x28198  # bloques de la trama BIONZ→Darwin: {len, ptr}
ROOTS = {
    "starter_evento": [0x1C04C, 0x1C02C, 0x1C0B6, 0x1AA28, 0x1AAD8],
    "starter_disparo": [0x17C26, 0x1A3EC, 0x1A004],
    "estado27_modo0": [0x175A0, 0x1F02A, 0x1B290],
    "estado28_espera": [0x175BC, 0x1F030, 0x1B2AA, 0x12240],
    "modo0": [0xE64A, 0xCB2A, 0xE572, 0x11BDC, 0x11DE8, 0x11EF6, 0x11F22, 0x122B0, 0x12260, 0x12302, 0xCEA2],
    "modo1": [0xE5CC, 0xCB2A, 0x11BDC, 0x11DE8, 0x11EF6, 0x11F22, 0x122B0, 0x12260, 0xE572, 0xD044, 0xE64A],
    "modo2": [0x1CB0E, 0x1CEBE, 0xD044, 0xE5CC, 0xCB2A],
    "esperas_estado31": [0x18FA0, 0x18D6E, 0xD34E, 0xD35A],
}


def pin(off: int, bank: str) -> str:
    """Offset de bit-band (r0 de 0x51c0/0x51c6) -> pin FM3: puerto = off//0x80, bit = (off%0x80)//4."""
    return f"P{off // 0x80}{(off % 0x80) // 4:X}"


def u8_list(c: Core, p: int, term: int) -> list[int]:
    out = []
    while True:
        out.append(c.u8(p))
        p += 1
        if out[-1] == term:
            return out


def main() -> dict:
    c = Core()
    g = E.G(c)
    res: dict = {"sha256": c.sha256()}

    rows = {k: (c.u32(ROWS + 8 * k), c.u16(ROWS + 8 * k + 4)) for k in range(44)}
    res["tabla_filas"] = {
        "base": hex(ROWS),
        "fila22": [hex(x) for x in rows[22]], "fila23": [hex(x) for x in rows[23]], "fila24": [hex(x) for x in rows[24]],
    }
    res["ganchos"] = [hex(c.u32(HOOKS + 4 * k)) for k in range(12)]
    res["bloque10"] = [hex(c.u32(T2 + 80)), hex(c.u32(T2 + 84))]
    res["gpio_espera_estado31"] = pin(0x124, "PDIR")
    res["cierres"] = {}
    for name, roots in ROOTS.items():
        cl: set[int] = set()
        for r in roots:
            cl |= g.closure(r)
        res["cierres"][name] = {"funciones": len(cl), "golpes": sorted(hex(x) for x in BAD & cl)}

    res["tabla_modos"] = [{"key": c.u8(0x294A0 + 8 * k), "seq": u8_list(c, c.u32(0x294A0 + 8 * k + 4), 0x17)} for k in range(11)]
    res["bionz"] = bionz()
    out = ROOT / "analysis/e24-05g/ajustes_modo.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1))
    return res


def bionz() -> dict:
    b = Bz()
    mask = [b.u8(0x43B1C6E6 + i) for i in range(8)]
    waits = {0x438D050C: "0x11", 0x438D060C: "0x14"}
    sites = {}
    for w, n in waits.items():
        sites[n] = [a for a in range(0x438C0000, 0x438D0000, 2) if _bl_target(b, a) == w]
    return {"tbb_tipos": mask, "esperas": {k: [hex(x) for x in v] for k, v in sites.items()},
            "byte0_rama": [hex(0x438C25B4), hex(0x438C2682), hex(0x438C277C)], "reintentos_max": 0x13}


def _bl_target(b: Bz, a: int) -> int | None:
    h1, h2 = b.u16(a), b.u16(a + 2)
    if h1 & 0xF800 != 0xF000 or not h2 & 0x8000:
        return None
    s, j1, j2 = (h1 >> 10) & 1, (h2 >> 13) & 1, (h2 >> 11) & 1
    imm = (s << 24) | ((~(j1 ^ s) & 1) << 23) | ((~(j2 ^ s) & 1) << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
    return a + 4 + (imm - (1 << 25) if s else imm)


if __name__ == "__main__":
    print(json.dumps(main(), indent=1)[:3500])
