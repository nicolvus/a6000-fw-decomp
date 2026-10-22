#!/usr/bin/env python3
"""S125 — localizadores de los llamadores (`bl`) de las funciones clave de los dos módulos.

Recorre `0x43541000`–`0x43a00000` con Capstone (Thumb) y anota quién llama a cada función
interesante.  Salida: analysis/s125_imaging_rel/bl_callers.json

Uso:  scan_callers.py
"""
import json
import os

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.join(REPO, "analysis/s125_imaging_rel")
BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"

OBJETIVOS = {
    0x437E6B3C: "PanoramaSweepStart",
    0x437E6E78: "PanoramaSweepEnd",
    0x437E751C: "UpdateSweepCanvas",
    0x437E9068: "seq_brcEncode",
    0x437E643A: "cmp_fill",
    0x43780EB4: "seq_panoramaClippingDecode",
    0x43781424: "seq_panoramaParallelStitch",
    0x438BCEF8: "PanoramaStitch",
    0x438BC0A8: "ddls_srotate_sa_start_cb",
    0x438BC720: "ddls_stitch_sa_start_cb",
    0x4379D114: "RelKey",
    0x4379D37A: "IsNeedForceS1ON",
    0x4379D3F8: "RelMgr notifica a CamUser",
    0x4379D83A: "despachador REL_EVT",
    0x4379E354: "RelMgr CLEAR_INNER_RP_CAPID_IDX",
    0x4379E500: "RelMgr Invalid RelLock Factor",
    0x43792A0C: "SyncTask VD_Pre/HS3",
    0x4381C30C: "CapIdTblMgr Initialize",
    0x4381C6CC: "CapIdTblMgr GetCaptureID",
    0x4381CC7C: "CapIdTblMgrIf",
    0x4381D088: "RelLock LOCK",
    0x4381D114: "NoMprCap InnerRp Clear",
    0x43807488: "ExecModeHandler NotifyEEStartEnable",
    0x437F0838: "Stage_InitializeSweepAndSpoolBranch",
    0x43549020: "Stage_Panorama",
}


def main():
    with open(os.path.join(REPO, BIN), "rb") as fh:
        data = fh.read()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    md.skipdata = True
    lo, hi = BASE, BASE + 0x4BF000
    res = {t: [] for t in OBJETIVOS}
    for ins in md.disasm(data[lo - BASE:hi - BASE], lo):
        if ins.mnemonic in ("bl", "blx") and ins.operands and ins.operands[0].type == 2:
            t = ins.operands[0].imm
            if t in res:
                res[t].append(ins.address)
    out = {f"0x{t:x}": {"nombre": OBJETIVOS[t], "llamadores": [hex(x) for x in v]}
           for t, v in sorted(res.items())}
    dest = os.path.join(HERE, "bl_callers.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    for k, v in out.items():
        print(f"{k} {v['nombre']}: {len(v['llamadores'])} -> {v['llamadores'][:6]}")
    print("->", dest)


if __name__ == "__main__":
    main()
