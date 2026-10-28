#!/usr/bin/env python3
"""E25-19b — ¿alcanza un manejador una primitiva OSAL de espera? Búsqueda por llamadas directas en av-cam.bin.

Los wrappers OSAL de av-cam son `ldr r3,[API]; ldr r3,[r3,#0x14]; ldr.w r3,[r3,#OFF]`; OFF = desplazamiento en la
tabla de `liro.ko` (.data: wai_sem_tmo 0x1a0, sig_sem 0x1a4, snd_msg 0x1b0, rcv_msg_tmo 0x1bc) + 0x24 (rcv_msg_tmo
confirmado: wrapper 0x43561260 con 0x1e0). Las llamadas indirectas (`blx rX`) no se siguen: se cuentan.
Uso: ADDR [ADDR...] [--depth N]; escribe analysis/e25-19b/esperas.json.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from e25_19b_calls import calls
from e25_19b_dis import BASE, BIN

SHIFT = 0x24
PRIMITIVAS = {"osal_wai_sem_tmo": 0x1A0, "osal_sig_sem": 0x1A4, "osal_snd_msg": 0x1B0, "osal_rcv_msg_tmo": 0x1BC}


def wrappers(data: bytes, lo: int = 0x43561000, hi: int = 0x43564000) -> dict[int, str]:
    """Dirección de cada wrapper OSAL de la tabla API -> nombre de la primitiva."""
    by_off = {off + SHIFT: n for n, off in PRIMITIVAS.items()}
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.skipdata = True
    ins = list(md.disasm(data[lo - BASE : hi - BASE], lo))
    out: dict[int, str] = {}
    for k, i in enumerate(ins):
        m = re.fullmatch(r"r3, \[r3, #(0x[0-9a-f]+)\]", i.op_str) if i.mnemonic == "ldr.w" else None
        if m and int(m[1], 16) in by_off:
            start = next(p.address for p in reversed(ins[max(0, k - 6) : k]) if p.mnemonic == "ldr" and "[pc" in p.op_str)
            out[start] = by_off[int(m[1], 16)]
    return out


def buscar(data: bytes, raiz: int, prof: int, wr: dict[int, str]) -> dict:
    """BFS por llamadas directas; devuelve cadena hasta cada primitiva y nº de llamadas indirectas no seguidas."""
    vistos = {raiz: [raiz]}
    cola: list[int] = [raiz]
    hallazgos: dict[str, list[str]] = {}
    for _ in range(prof):
        sig = []
        for f in cola:
            for _site, _m, t in calls(data, f)[0]:
                nombre = next((n for a, n in wr.items() if a - 8 <= t <= a + 0x14), None)
                if nombre:
                    hallazgos.setdefault(nombre, [hex(x) for x in vistos[f] + [t]])
                elif t not in vistos and BASE <= t < BASE + len(data):
                    vistos[t] = vistos[f] + [t]
                    sig.append(t)
        cola = sig
    return {"funciones_alcanzadas": len(vistos), "primitivas": hallazgos}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("addr", nargs="+")
    ap.add_argument("--depth", type=int, default=4)
    a = ap.parse_args()
    d = BIN.read_bytes()
    wr = wrappers(d)
    res = {"wrappers": {hex(k): v for k, v in wr.items()},
           "raices": {x: buscar(d, int(x, 16), a.depth, wr) for x in a.addr}}
    out = Path(__file__).resolve().parents[1] / "analysis/e25-19b/esperas.json"
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
