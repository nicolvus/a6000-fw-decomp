#!/usr/bin/env python3
"""S164 — detalles del modulo [CAMERA_IS]: envoltorio de traza por sub-capa (y su
categoria log r1), verificacion manual de los pares PIC y contexto del llamador.

Lee analysis/s164_camera_is/camera_is.json y lo enriquece in situ.
"""
import bisect
import json
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False
PAT = re.compile(rb"[\x20-\x7e]{4,}")
STR = {}
for m in PAT.finditer(DATA):
    STR[BASE + m.start()] = m.group().decode("latin1")
PROL = json.loads((HERE / "prologues.json").read_text())

# envoltorio de traza por sub-capa, deducido del `bl` inmediatamente posterior al `add rX,pc`
WRAPPERS = {
    "MOUNT": ["0x436ea224", "0x43705cb8"],
    "DIST": ["0x436ea3c4"],
    "AS": ["0x436febc4", "0x4371e39c"],
    "EIS": ["0x437026ac", "0x437041dc"],
}


def pic_check(ldr, add):
    """Verificacion manual: ldr rX,[pc,#imm] + add rX,pc -> destino."""
    h = struct.unpack_from("<H", DATA, ldr - BASE)[0]
    if (h & 0xF800) == 0x4800:
        imm = h & 0xFF
        lit = ((ldr + 4) & ~3) + imm * 4
        kind = "ldr16"
    else:
        h2 = struct.unpack_from("<H", DATA, ldr - BASE + 2)[0]
        imm = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
        lit = ((ldr + 4) & ~3) + imm
        kind = "ldr.w"
    w = struct.unpack_from("<I", DATA, lit - BASE)[0]
    tgt = (w + (add + 4)) & 0xFFFFFFFF
    return {
        "ldr": hex(ldr), "kind": kind, "literal": hex(lit), "pool_w": hex(w),
        "add": hex(add), "destino": hex(tgt),
        "texto": STR.get(tgt),
    }


def wrapper_after(add):
    """Primer `bl` despues del `add rX,pc` del sitio de emision."""
    for ins in MD.disasm(DATA[add - BASE:add - BASE + 16], add):
        if ins.mnemonic == "bl":
            return hex(int(ins.op_str[1:], 16)) if ins.op_str.startswith("#0x") else ins.op_str
    return None


def category_id(add):
    """Valor inmediato cargado en r1 justo antes del `add rX,pc`.

    Se buscan directamente los halfwords `movs r1,#imm` (0x21xx) en los 32 B previos.
    """
    for back in range(2, 34, 2):
        a = add - back
        h = struct.unpack_from("<H", DATA, a - BASE)[0]
        if (h & 0xFF00) == 0x2100:
            return h & 0xFF
    return None


def main():
    js = json.loads((HERE / "camera_is.json").read_text())

    # 1) envoltorio + categoria por sitio
    for s in js["strings"]:
        for site in s["sites"]:
            w = wrapper_after(site)
            s.setdefault("log_wrapper", {})
            s["log_wrapper"][hex(site)] = {"wrapper": w,
                                           "categoria_r1": category_id(site),
                                           "r0_nivel": 0xf}

    # 2) verificacion manual de un par PIC por sub-capa (regla metodologica S106)
    checks = []
    for s in js["strings"]:
        site = s["sites"][0]
        # el `ldr` que precede al `add` del sitio
        best = None
        for back in range(2, 44, 2):
            a = site - back
            h = struct.unpack_from("<H", DATA, a - BASE)[0]
            ok = (h & 0xF800) == 0x4800
            if not ok:
                ok = (h & 0xFF7F) == 0xF85F
            if ok:
                best = a
                break
        c = pic_check(best, site)
        c["subcapa"] = s["sublayer"]
        c["ok"] = c["destino"] == hex(s["vaddr"])
        checks.append(c)
    js["verificacion_manual_pic"] = checks

    # 3) contexto del llamador: funcion contenedora + etiqueta de modulo mas cercana
    refs = {int(k, 16): v for k, v in
            json.loads((ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json").read_text()).items()}
    bysite = []
    for dest, sites in refs.items():
        for st in sites:
            bysite.append((st, STR.get(dest, "")))
    bysite.sort()
    sites_only = [s for s, _ in bysite]
    for f in js["functions"]:
        ctx = []
        for c in f["bl_callers"]:
            k = bisect.bisect_left(sites_only, c) - 1
            near = []
            j = k
            while j >= 0 and len(near) < 3:
                if c - sites_only[j] <= 0x400:
                    t = bysite[j][1]
                    if t:
                        near.append((hex(sites_only[j]), t[:90]))
                j -= 1
            fn = None
            kk = bisect.bisect_left(PROL, c) - 1
            if kk >= 0:
                fn = hex(PROL[kk])
            ctx.append({"caller": hex(c), "caller_func": fn, "cadenas_cercanas": near})
        f["llamadores_contexto"] = ctx

    (HERE / "camera_is.json").write_text(json.dumps(js, indent=1, ensure_ascii=False) + "\n")
    print("manual PIC checks:", sum(1 for c in checks if c["ok"]), "/", len(checks))
    for c in checks:
        if not c["ok"]:
            print("  FALLO", c)
    print("escrito camera_is.json")


if __name__ == "__main__":
    main()
