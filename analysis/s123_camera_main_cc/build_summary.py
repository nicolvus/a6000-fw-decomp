#!/usr/bin/env python3
"""S123 — consolida los artefactos del hito `[CAMERA_MAIN_CC]` en `camera_main_cc.json`.

Entradas (generadas por los demás scripts de esta carpeta):
  cc_strings.json     cadenas con vaddr/texto/bloque
  func_map.json       mapa función→traza (regla PIC estricta)
  source_files.json   ficheros `.cpp`/`.h` referenciados y sus funciones
  callgraph.json      llamadas de cada función CC
  stage_states.json   función de etapa y byte de estado de cada método
  param_ids.json      ids de parámetro (`movw`) del módulo
  a7s_diff.json       diferencial A7S/A6300

Uso:  build_summary.py [SALIDA]
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 0x43541000

# sub-bloques del módulo (partición exacta de las 49 trazas)
SUBBLOCKS = {
    "capture-control": "métodos del control de captura (identidad de la captura)",
    "lut": "LUT 2D/3D (corrección de color, LUT de efecto)",
    "ie": "IE = image effect (LightNum/MapNum)",
    "miniraw": "miniRaw (tamaño de la imagen raw reducida)",
    "makernote-playraw": "MakerNote de reproducción raw",
    "camcore-3dlut": " CamCore: escritura de la tabla 3D-LUT",
}


# métodos del control de captura (los nombres tal cual aparecen en las trazas)
METHODS = [
    "ExtractCaptureData", "CaptureInit", "SetReadImageParam", "SetNRParam",
    "SetOPDParam", "AfterOPDAfterNR", "SetDevelopParam",
    "SetDevDetectDevelopParam", "DetectYC", "SetDualRecParam", "SetDAEParam",
    "SetBdroIdtData", "SetSACCParam", "SetSACCSaEndParam", "WriteExifMakernote",
    "GetKDZMode", "SetPlayRawDevDetectDevelop", "SetPlayRawDevelopParam",
    "SetMovDevelopParam", "SetReviewDevelopParam", "WriteSACCMakerNote",
]
# trazas del bloque LUT que no llevan "Lut"/"LUT" en el texto
LUT_EXTRA = {"IsSplit Change [%02X] -> [%02X]"}


def method_of(text):
    if not text.startswith("[CAMERA_MAIN_CC]: "):
        return None
    body = text[len("[CAMERA_MAIN_CC]: "):]
    for m in METHODS:
        if body.startswith(m):
            return m
    return None


def block_of(text):
    if method_of(text):
        return "capture-control"
    core = text[len("[CAMERA_MAIN_CC]: "):] if text.startswith("[CAMERA_MAIN_CC]: ") else text
    if "CamCore" in core:
        return "camcore-3dlut"
    if core in LUT_EXTRA or "Lut" in core or "LUT" in core or "DLUT" in core \
            or "uc_sync" in core:
        return "lut"
    if re.match(r"IE\s", core):
        return "ie"
    if "miniRaw" in core:
        return "miniraw"
    if "MakerNote" in core:
        return "makernote-playraw"
    return None


def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "camera_main_cc.json")
    strings = json.load(open(os.path.join(HERE, "cc_strings.json")))["strings"]
    fmap = json.load(open(os.path.join(HERE, "func_map.json")))
    srcs = json.load(open(os.path.join(HERE, "source_files.json")))
    cg = json.load(open(os.path.join(HERE, "callgraph.json")))
    stages = json.load(open(os.path.join(HERE, "stage_states.json")))
    pids = json.load(open(os.path.join(HERE, "param_ids.json")))
    diff = json.load(open(os.path.join(HERE, "a7s_diff.json")))

    site_of = {}
    for r in fmap["xrefs"]:
        site_of[r["string"]] = r
    fn_of = {}
    for fn in fmap["functions"]:
        for s in fn["strings"]:
            fn_of[s["vaddr"]] = fn

    rows = []
    for s in strings:
        r = site_of.get(s["vaddr"])
        fn = fn_of.get(s["vaddr"])
        rows.append({
            "vaddr": s["vaddr"],
            "text": s["text"],
            "block": block_of(s["text"]),
            "method": method_of(s["text"]),
            "referenced": r is not None,
            "xref_site": r["site"] if r else None,
            "func": fn["func"] if fn else None,
            "func_end": fn["func_end"] if fn else None,
        })

    sub = {}
    for r in rows:
        sub.setdefault(r["block"], []).append(r)

    # tramos contiguos de .rodata: una cadena sigue a la anterior si el NUL
    # terminador de la anterior cae justo antes de ella
    tramos = []
    prev = None
    for r in rows:
        contiguo = prev is not None and prev["fin"] + 1 == int(r["vaddr"], 16)
        if not contiguo:
            tramos.append({"ini": r["vaddr"], "n": 0})
        tramos[-1]["n"] += 1
        prev = {"fin": int(r["vaddr"], 16) + len(r["text"]), "text": r["text"]}
    for t, r in zip(tramos, rows):
        pass
    #fin de cada tramo
    fines = []
    for i, r in enumerate(rows):
        fin = int(r["vaddr"], 16) + len(r["text"])
        if i + 1 < len(rows) and fin + 1 == int(rows[i + 1]["vaddr"], 16):
            continue
        fines.append(fin)
    for t, fin in zip(tramos, fines):
        t["fin"] = f"0x{fin:x}"
        t["n"] = sum(1 for r in rows
                     if int(t["ini"], 16) <= int(r["vaddr"], 16) <= fin)

    out = {
        "milestone": "S123",
        "module": "CAMERA_MAIN_CC",
        "base": f"0x{BASE:x}",
        "rule": "estricta (analysis/s106_imaging_cap/scan_pic_refs_strict.py)",
        "counts": {
            "strings": len(rows),
            "referenced": sum(1 for r in rows if r["referenced"]),
            "unreferenced": sum(1 for r in rows if not r["referenced"]),
            "xref_sites": len(fmap["xrefs"]),
            "functions": fmap["n_functions"],
            "subblocks": len(sub),
            "capture_methods": sum(1 for r in rows if r["block"] == "capture-control"),
            "capture_methods_live": sum(1 for r in rows
                                        if r["block"] == "capture-control" and r["referenced"]),
            "a7s_prefixed": diff["a7s"]["n_cadenas_cc"],
            "a7s_common_messages": diff["comunes_a7s"],
            "a6300_prefixed": diff["a6300"]["n_cadenas_cc"],
            "a6300_common_messages": diff["comunes_a6300"],
        },
        "subblocks": [
            {"name": k, "n": len(v), "desc": SUBBLOCKS.get(k, ""),
             "lo": min(x["vaddr"] for x in v), "hi": max(x["vaddr"] for x in v),
             "strings": [{"vaddr": x["vaddr"], "text": x["text"], "referenced": x["referenced"],
                          "func": x["func"], "xref_site": x["xref_site"]} for x in v]}
            for k, v in sorted(sub.items(), key=lambda kv: -len(kv[1]))
        ],
        "rodata_runs": tramos,
        "strings": rows,
        "functions": fmap["functions"],
        "capture_identity_layout": {
            "estructura_grande": {
                "CapMode": "0x1c0 (32 bits)",
                "ExposureID": "0x1b8 (32 bits)",
                "ContID": "0x1bc (32 bits)",
                "BDROSeq": "0x6ec (32 bits)",
                "BDRObase": "0x6f4 (32 bits)",
                "FrameID": "0x701 (8 bits)",
            },
            "estructura_pequena_ExtractCaptureData": {
                "ExposureID": "0x00 (32 bits)",
                "ContID": "0x04 (32 bits)",
                "CapMode": "0x08 (32 bits)",
                "FrameID": "0x0c (32 bits)",
            },
            "metodo": "lectura literal verificada desensamblando CaptureInit "
                      "(0x4379ed34), SetReadImageParam (0x4379ee04), "
                      "SetDevelopParam (0x4379f150) y WriteSACCMakerNote (0x4379fb48)",
        },
        "stage_functions": stages["stages"],
        "param_ids": sorted({r["imm"] for r in pids["movw"] if 0x9000 <= r["imm"] <= 0x96ff}),
        "source_files": [
            {"name": r["name"], "vaddr": r["vaddr"], "n_refs": r["n_refs"],
             "funcs": [x["func"] for x in r["elsewhere"]]}
            for r in srcs["files"]
            if any(x.get("region") for x in r["in_cc_regions"]) or r["name"] in (
                "CaptureUtilityCommon.cpp", "CaptureUtilityCamCore.cpp",
                "CaptureUtilityExifMkNote.cpp", "CaptureUtilityImager.cpp",
                "CaptureUtilitySDF.cpp", "CaptureUtilityStdYc.cpp",
                "ImageParamCapture.cpp", "CaptureManager.cpp",
                "CaptureManager_FunctionIF.cpp", "CaptureManager_ModeInfo.cpp",
                "CaptureManager_ReleaseIF.cpp", "NotifyController.cpp",
                "Stage_SACC.cpp", "Sequence_Common.cpp")
        ],
        "callgraph": cg["functions"],
        "callers": json.load(open(os.path.join(HERE, "callers.json")))["callers"],
        "class_registry": json.load(open(os.path.join(HERE, "class_registry.json"))),
        "a7s_diff": {k: v for k, v in diff.items() if k != "tabla"},
        "a7s_diff_tabla": diff["tabla"],
    }
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("sub-bloques:", [(b["name"], b["n"]) for b in out["subblocks"]])


if __name__ == "__main__":
    import sys
    main()
