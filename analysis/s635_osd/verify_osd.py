#!/usr/bin/env python3
"""S635: la etiqueta `[OSD]` (una sola cadena, `[VDF][OSD] VDF_EVF_OUT_MODE_ON_LR_THROUGH`) en A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "analysis/camera_closure"), str(ROOT / "analysis"), str(ROOT / "analysis/s106_imaging_cap")]
import labels as L, closure as C, closure2 as K, verify_s6xx as V


def build():
    d = L.evaluate("[OSD]")
    d["vdf_osd_a7s"] = C.tokens(V.FIRMWARE["a7s_fw320"], "[VDF][OSD]")
    d["vdf_osd_a6300"] = C.tokens(V.FIRMWARE["a6300_fw201"], "[VDF][OSD]")
    d["vdf_osd_a6000"] = C.tokens(V.FIRMWARE["a6000_fw321"], "[VDF][OSD]")
    d["vdf_evf_out_mode"] = {m: C.tokens(p, "VDF_EVF_OUT_MODE") for m, p in V.FIRMWARE.items()}
    f = int(d["funciones"][0]["func"], 16)
    d["referencias_funcion"] = K.refs(f)
    return d


if __name__ == "__main__":
    d = build()
    (ROOT / "analysis/s635_osd/osd.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
    print(json.dumps(d, ensure_ascii=False)[:900])
