#!/usr/bin/env python3
"""E25-19b (tramo final) — ciclo del evento en vuelo: motor Run(M), tabla de subestados y esperas alcanzables.

Todo por bytes de av-cam.bin (Capstone). Sin cámara. Escribe analysis/e25-19b/ciclo.json.
Hechos que decodifica (cada uno con su dirección):
 - Run(M)=0x43b047d0: invoca el functor M+8 con r1=M; el código devuelto (tbb 0x43b047ec) decide: 0 sub++ y re-post, 1 re-post,
   2 dly_tsk(50) y re-post, 3 retorno (espera externa), 4 fin(M), 5 callback M+0x24 y fin, 6 retorno.
 - Estado 0x43b1b024: despacha por [M+0x23] con tbh 0x43b1b030.
 - Esperas: wrappers µITRON/OSAL de 0x43560000..0x43564000 identificados por el desplazamiento en la tabla de liro.ko (+0x24).
"""

from __future__ import annotations

import json
import re
import struct
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from e25_19b_calls import calls
from e25_19b_dis import BASE, BIN

SHIFT = 0x24
NOMBRES = {
    0x38: "tslp_tsk",
    0x48: "dly_tsk",
    0x5C: "sig_sem",
    0x60: "twai_sem",
    0x78: "set_flg",
    0x7C: "clr_flg",
    0x80: "twai_flg",
    0x84: "ref_flg",
    0x9C: "trcv_mbx",
    0x1A0: "osal_wai_sem_tmo",
    0x1A4: "osal_sig_sem",
    0x1B0: "osal_snd_msg",
    0x1BC: "osal_rcv_msg_tmo",
    0xF8: "get_tim",
    0xFC: "CRE_CYC",
    0x10C: "sta_cyc",
    0x128: "sta_alm",
    0x12C: "stp_alm",
}
BLOQUEANTES = {
    "tslp_tsk",
    "dly_tsk",
    "twai_sem",
    "twai_flg",
    "trcv_mbx",
    "osal_wai_sem_tmo",
    "osal_rcv_msg_tmo",
}


def wrappers(data: bytes, lo: int = 0x43560000, hi: int = 0x43564000) -> dict[int, str]:
    """Dirección de cada wrapper de la tabla API -> primitiva (OFF - 0x24 = desplazamiento en la tabla de liro.ko)."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.skipdata = True
    ins = list(md.disasm(data[lo - BASE : hi - BASE], lo))
    out: dict[int, str] = {}
    for k, i in enumerate(ins):
        m = (
            re.fullmatch(r"r3, \[r3, #(0x[0-9a-f]+)\]", i.op_str)
            if i.mnemonic == "ldr.w"
            else None
        )
        if m and (int(m[1], 16) - SHIFT) in NOMBRES:
            start = next(
                p.address
                for p in reversed(ins[max(0, k - 6) : k])
                if p.mnemonic == "ldr" and "[pc" in p.op_str
            )
            out[start & ~1] = NOMBRES[int(m[1], 16) - SHIFT]
    return out


def tbh(data: bytes, base: int, n: int) -> list[int]:
    return [
        base + 2 * struct.unpack_from("<H", data, base - BASE + 2 * i)[0]
        for i in range(n)
    ]


def tbb(data: bytes, base: int, n: int) -> list[int]:
    return [base + 2 * data[base - BASE + i] for i in range(n)]


def alcanza(
    data: bytes, raiz: int, prof: int, wr: dict[int, str]
) -> dict[str, list[str]]:
    vistos = {raiz: [raiz]}
    cola = [raiz]
    res: dict[str, list[str]] = {}
    for _ in range(prof):
        sig = []
        for f in cola:
            for _s, _m, t in calls(data, f)[0]:
                nom = next((n for a, n in wr.items() if a - 8 <= t <= a + 0x14), None)
                if nom:
                    res.setdefault(nom, [hex(x) for x in vistos[f] + [t]])
                elif t not in vistos and BASE <= t < BASE + len(data):
                    vistos[t] = vistos[f] + [t]
                    sig.append(t)
        cola = sig
    return res


def main() -> int:
    d = BIN.read_bytes()
    wr = wrappers(d)
    subs = tbh(d, 0x43B1B034, 12)
    rc = tbb(d, 0x43B047F0, 7)
    raices = {f"sub{n}": s for n, s in enumerate(subs)}
    out: dict[str, Any] = {
        "schema": "e25-19b-ciclo/v1",
        "run": {
            "funcion": "0x43b047d0",
            "rc_destino": {str(i): hex(a) for i, a in enumerate(rc)},
        },
        "estado_0x43b1b024_sub_a_manejador": {
            str(i): hex(a) for i, a in enumerate(subs)
        },
        "wrappers": {hex(k): v for k, v in sorted(wr.items())},
        "espera_alcanzable_prof4": {k: alcanza(d, v, 4, wr) for k, v in raices.items()},
    }
    p = Path(__file__).resolve().parents[1] / "analysis/e25-19b/ciclo.json"
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(
        json.dumps(
            {k: out[k] for k in ("run", "estado_0x43b1b024_sub_a_manejador")}, indent=1
        )
    )
    print(sorted(out["wrappers"].items())[:40])
    for k, v in out["espera_alcanzable_prof4"].items():
        print(k, hex(raices[k]), {n: c[-3:] for n, c in v.items() if n in BLOQUEANTES})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
