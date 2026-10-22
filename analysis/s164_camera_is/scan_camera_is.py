#!/usr/bin/env python3
"""S164 — modulo `[CAMERA_IS]` de la A6000 fw3.21: cadenas, referencias PIC (regla
estricta), funcion contenedora, llamadores y diferencial con A7S fw3.20 / A6300 fw2.01.

  vaddr = 0x43541000 + file_offset

Regla de referencias: estricta (canonica del repo), mapa global ya calculado en
analysis/s106_imaging_cap/pic_refs_strict_global.json
(ver analysis/s106_imaging_cap/pic_xref_methodology.md).

Salida: analysis/s164_camera_is/camera_is.json
"""
import bisect
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 0x43541000

A6000 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7S = (ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = (ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
               "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
REFS = ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json"
PROL = HERE / "prologues.json"

DATA = A6000.read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False
PAT = re.compile(rb"[\x20-\x7e]{4,}")
TOKEN = "[CAMERA_IS]"

# sub-capas declaradas por las propias cadenas
SUBLAYER = {
    "MOUNT": "interfaz IS <-> montura de objetivo (CAIF/LENS_MOUNT)",
    "DIST": "correccion de distorsion (parametros y conversion de posiciones)",
    "AS": "estabilizador activo (STABILIZER) y su cola de mensajes OSAL",
    "EIS": "estabilizacion electronica (EIS): alimentacion, rejilla y giroscopio",
}


def strings_with(data, token):
    """Cadenas C (hasta el NUL) que contienen el token; devuelve (vaddr, texto exacto)."""
    out = []
    for m in PAT.finditer(data):
        t = m.group().decode("latin1")
        if token not in t:
            continue
        off = m.start()
        end = off
        while end < len(data) and data[end] != 0:
            end += 1
        out.append((BASE + off, data[off:end].decode("latin1")))
    return out


def sublayer(text):
    m = re.match(r"\[CAMERA_IS\]\[([A-Z]+)\]", text)
    return m.group(1) if m else "?"


def inner(text):
    """Texto sin la etiqueta [CAMERA_IS][X]:."""
    return re.sub(r"^\[CAMERA_IS\]\[[A-Z]+\]:\s*", "", text)


def container(site, prol):
    """Proximo prologo `push {...,lr}` por detras (mismo metodo que S133)."""
    k = bisect.bisect_left(prol, site) - 1
    for p in reversed(prol[max(0, k - 80):k + 1]):
        if site - p > 0x3000:
            break
        last = None
        ok = True
        for ins in MD.disasm(DATA[p - BASE:site - BASE], p):
            if ins.address >= site:
                break
            m, o = ins.mnemonic, ins.op_str
            if (m.startswith("pop") and "pc" in o) or (m == "bx" and o == "lr"):
                ok = False
                break
            last = ins
        if ok and last is not None and last.address + last.size == site:
            return p, False
    for p in reversed(prol[max(0, k - 80):k + 1]):
        if site - p > 0x3000:
            break
        return p, True
    return None, True


def sweep_calls():
    calls = defaultdict(list)
    off = 0
    n = len(DATA)
    while off < n:
        got = False
        for ins in MD.disasm(DATA[off:off + 16], BASE + off):
            got = True
            if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#0x"):
                calls[int(ins.op_str[1:], 16)].append(ins.address)
            off += ins.size
        if not got:
            off += 2
    return calls


def main():
    refs = {int(k, 16): v for k, v in json.loads(REFS.read_text()).items()}
    prol = json.loads(PROL.read_text())
    calls = sweep_calls()

    strs = strings_with(DATA, TOKEN)
    rows = []
    for a, t in strs:
        for site in refs.get(a, []):
            f, approx = container(site, prol)
            rows.append({"str": a, "text": t, "site": site, "func": f, "approx": approx})

    by_func = defaultdict(list)
    for r in rows:
        by_func[r["func"]].append(r)

    funcs = []
    for f, rs in sorted(by_func.items(), key=lambda kv: (kv[0] is None, kv[0])):
        funcs.append({
            "vaddr": f,
            "vaddr_hex": hex(f) if f else None,
            "n_sites": len(rs),
            "sites": sorted({r["site"] for r in rs}),
            "sites_hex": [hex(x) for x in sorted({r["site"] for r in rs})],
            "strings": sorted({r["str"] for r in rs}),
            "strings_hex": [hex(x) for x in sorted({r["str"] for r in rs})],
            "texts": [r["text"] for r in sorted(rs, key=lambda x: x["site"])],
            "approx_function": any(r["approx"] for r in rs),
            "bl_callers": sorted(calls.get(f, [])) if f else [],
            "bl_callers_hex": [hex(c) for c in sorted(calls.get(f, []))] if f else [],
        })

    per_string = defaultdict(list)
    for r in rows:
        per_string[r["str"]].append(r)

    a7s = A7S.read_bytes()
    a6300 = A6300.read_bytes()

    str_json = []
    for a, t in strs:
        rr = per_string.get(a, [])
        str_json.append({
            "vaddr": a,
            "vaddr_hex": hex(a),
            "text": t,
            "inner_text": inner(t),
            "sublayer": sublayer(t),
            "sites": sorted({r["site"] for r in rr}),
            "sites_hex": [hex(x) for x in sorted({r["site"] for r in rr})],
            "functions": sorted({r["func"] for r in rr if r["func"] is not None}),
            "functions_hex": [hex(x) for x in sorted({r["func"] for r in rr if r["func"] is not None})],
            "n_refs": len(rr),
            "a7s_inner_present": inner(t).encode("latin1") in a7s,
            "a6300_inner_present": inner(t).encode("latin1") in a6300,
        })

    # diferencial: terminos estructurales del subsistema IS en los tres firmwares
    terms = ["[CAMERA_IS]", "GyroAD", "FILE_IS_%04x.dat", "SetStblzPower", "SetStblzGridH",
             "SetStblzParamV", "SetStblzVectorH", "IS_LensMountExpStartCB",
             "IS_LensMountPanoramaGyro", "MakeDistCorPrm", "CnvPosInvDistCorr",
             "MakeDistRawAppliTag", "upm_get_hcrn_ura", "osal_reg_sync_msg_queue_cb",
             "osal_unreg_sync_msg_queue_cb", "[STABILIZER]", "LENS_MOUNT",
             "EIS_RC1V_SetPower", "rcct_SetStblz", "src/api_rc.cpp",
             "WrapRcctSetStblzPower.cpp", "WrapRcctSetStblzGridH.cpp",
             "WrapRcctSetStblzParamV.cpp", "WrapRcctSetStblzVectorH.cpp",
             "ModuleDistBase.cpp", "rolling", "readout",
             "position num in rolling is strange %d",
             "GetImagerStabilizationTime"]
    diff = {}
    for t in terms:
        tb = t.encode("latin1")
        diff[t] = {"A6000": DATA.count(tb), "A7S": a7s.count(tb), "A6300": a6300.count(tb)}

    out = {
        "milestone": "S164",
        "modulo": "[CAMERA_IS]",
        "binary": str(A6000.relative_to(ROOT)),
        "vaddr_rule": "vaddr = 0x43541000 + file_offset",
        "xref_rule": "estricta (analysis/s106_imaging_cap/pic_refs_strict_global.json); "
                     "ver analysis/s106_imaging_cap/pic_xref_methodology.md",
        "counts": {
            "cadenas": len(strs),
            "sitios_pic": len(rows),
            "referenciadas": sum(1 for a, _ in strs if a in per_string),
            "sin_referencia": sum(1 for a, _ in strs if a not in per_string),
            "funciones": len(funcs),
        },
        "subcapas": SUBLAYER,
        "contadores_por_subcapa": dict(Counter(sublayer(t) for _, t in strs)),
        "contadores_por_subcapa_sitios": dict(Counter(
            sublayer(r["text"]) for r in rows)),
        "strings": str_json,
        "functions": funcs,
        "diferencial": diff,
        "diferencial_nota": "A7S fw3.20 y A6300 fw2.01: 0 apariciones del token [CAMERA_IS] "
                            "y 0 textos interiores coincidentes; la capa RC de estabilizacion "
                            "(rcct_SetStblz*, WrapRcctSetStblz*.cpp) y el fichero "
                            "/mnt/FILE_IS_%04x.dat SI existen en los tres. Lo propio de la "
                            "A6000 fw3.21 es la capa de aplicacion (giroscopio, matematica de "
                            "distorsion, callbacks de montura, cola AS). El concepto de "
                            "rolling shutter y la API GetImagerStabilizationTime solo existen "
                            "en el A6300 fw2.01, y tampoco pertenecen a [CAMERA_IS].",
    }
    (HERE / "camera_is.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(out["counts"]))
    print("subcapas:", out["contadores_por_subcapa"], out["contadores_por_subcapa_sitios"])
    for s in str_json:
        print("  %s %-9s %-58s %s" % (s["vaddr_hex"], s["sublayer"], s["text"][:58],
                                      s["functions_hex"]))
    for f in funcs:
        print("  func %s n=%d callers=%s" % (f["vaddr_hex"], f["n_sites"], f["bl_callers_hex"]))
    print("escrito", HERE / "camera_is.json")


if __name__ == "__main__":
    main()
