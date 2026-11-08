#!/usr/bin/env python3
"""Núcleo `av-cam.bin`: soporte de las gammas de Picture Profile en A6000 fw3.21 frente a A7S fw3.20 (G16). Solo lee.

Comprueba con bytes: 1) tabla de curvas de gamma (punteros por `número_gamma*2 + modo`, modo 1 = vídeo); 2) curvas de vídeo
comunes iguales salvo el campo `+0x1012`; 3) tabla «selector PP (byte 0x1a del mensaje LIRO 0x4066) → número de gamma»;
4) formato del mensaje 0x4066 (42 campos); 5) límites de los `switch` por número de gamma.
Uso: pp_core_audit.py [SALIDA.json]
"""
import json
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BASE, CURVE = 0x43541000, 0x101A
FW = {  # tabla de curvas, tabla selector→gamma, desempaquetador de 0x4066, switch de gamma (cmp #máx)
    "a6000": ("av-cam.bin", 0x44001404, 0x43CB56E6, 0x43802A28, 0x4384764C),
    "a7s": ("av-cam-a7s.bin", 0x43FFA290, 0x43CAB54D, 0x437A9404, 0x437CDF62),
}
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def load(k: str) -> bytes:
    return (ROOT / "analysis/rea-independent/input" / FW[k][0]).read_bytes()


def unpacker(d: bytes, start: int) -> dict[int, int]:
    """Byte del mensaje → campo de la configuración (`ldrb r2,[r0,#i]` / `str* r2,[r3,#o]`)."""
    out, cur = {}, None
    for i in MD.disasm(d[start - BASE:start - BASE + 0x400], start):
        if i.mnemonic == "bx":
            break
        if (m := re.match(r"r2, \[r0, #(0x[0-9a-f]+)\]", i.op_str)) and i.mnemonic.startswith("ldr"):
            cur = int(m.group(1), 16)
        elif (m := re.match(r"r2, \[r3, #(0x[0-9a-f]+)\]", i.op_str)) and i.mnemonic.startswith("str") and cur is not None:
            out[cur], cur = int(m.group(1), 16), None
    return out


def audit() -> dict:
    res, raw = {}, {}
    for k, (_, curves, sel, unp, sw) in FW.items():
        d = raw[k] = load(k)
        ptr = struct.unpack_from("<64I", d, curves - BASE)
        cmp = next(MD.disasm(d[sw - BASE:sw - BASE + 2], sw))
        res[k] = {"curvas_video": [g for g in range(32) if ptr[2 * g + 1]], "curvas_foto": [g for g in range(32) if ptr[2 * g]],
                  "selector_a_gamma": [list(d[sel - BASE + 2 * i:sel - BASE + 2 * i + 2]) for i in range(12)],
                  "msg_4066": unpacker(d, unp), "switch_max": int(cmp.op_str.split("#")[1], 16), "_ptr": ptr}
    a, s = res["a6000"], res["a7s"]
    nuevas = sorted(set(s["curvas_video"]) - set(a["curvas_video"]))
    iguales = []
    for g in (g for g in a["curvas_video"] if g < 0x1F):  # 0x1f: curva especial, distinta por modelo
        ca = raw["a6000"][a["_ptr"][2 * g + 1] - BASE:][:CURVE]
        cb = raw["a7s"][s["_ptr"][2 * g + 1] - BASE:][:CURVE]
        iguales.append(sum(x != y for x, y in zip(ca, cb)) == 1 and ca[0x1012] == 4 and cb[0x1012] == 7)
    out = {"nuevas_curvas_video_a7s": nuevas, "curvas_video_comunes_iguales_salvo_0x1012": all(iguales),
           "bytes_curvas_nuevas": len(nuevas) * CURVE,
           **{k: {kk: vv for kk, vv in v.items() if kk != "_ptr" and kk != "msg_4066"} | {"msg_4066_campos": len(v["msg_4066"])}
              for k, v in res.items()},
           "msg_4066_mismo_orden": list(a["msg_4066"]) == list(s["msg_4066"]),
           "gamma_byte_0x1a": {"a6000": hex(a["msg_4066"][0x1A]), "a7s": hex(s["msg_4066"][0x1A])}}
    return out


if __name__ == "__main__":
    r = audit()
    assert r["nuevas_curvas_video_a7s"] == [0x16, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D], r["nuevas_curvas_video_a7s"]
    assert r["curvas_video_comunes_iguales_salvo_0x1012"] and r["msg_4066_mismo_orden"]
    assert r["gamma_byte_0x1a"] == {"a6000": "0x153", "a7s": "0x165"}
    assert r["a6000"]["switch_max"] == 0x1B and r["a7s"]["switch_max"] == 0x1D
    assert all(0x16 not in p and 0x18 not in p for p in r["a6000"]["selector_a_gamma"])
    assert r["a7s"]["selector_a_gamma"][6] == [0x18, 0x18] and r["a7s"]["selector_a_gamma"][11] == [0x1D, 0x1D]
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(r, indent=1))
    print(json.dumps({k: r[k] for k in ("nuevas_curvas_video_a7s", "bytes_curvas_nuevas", "gamma_byte_0x1a")}))
    for k in ("a6000", "a7s"):
        print(k, "selector→gamma", r[k]["selector_a_gamma"], "switch ≤", hex(r[k]["switch_max"]))
