#!/usr/bin/env python3
"""Auditoría de Picture Profile por capas en A6000 fw3.21, A7S fw3.20 y A6300 fw2.01 (G15). Solo lee.

Capas: 1) menú (nodos `PictureProfile*`/`SLogDispAssist*` de `CautionConfig.so`, ProcessId y opciones); 2) clase de elemento
de la A6300 (`analysis/gui/g14/f6300.json`); 3) `libObj.so` (tabla de nombres `PARAMID_*`: índice de cada `PARAMID_PP_*`);
4) `av-cam.bin` (marcadores del cálculo de gamma de captura y tipos `Camera::PP_*`).
shortcut: la capa 4 cuenta cadenas, no sigue el manejador del mensaje; la prueba final es el código o la cámara.
Uso: picture_profile_audit.py [SALIDA.json]
"""
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import setting_nodes
import uxc_strings

ROOT = Path(__file__).resolve().parents[2]
FW = {"a6000": "fw321", "a7s": "a7s-fw320/payload", "a6300": "a6300-fw201/payload"}
PART = "firmware.tar_unpacked/0700_part_image/dev/{}_unpacked_unpacked"
AVCAM_MARKS = ("job_EC_CalcCaptureGamma", "PIN_YC_CAPTURE_GAMMA", "Camera::PP_MODE", "Camera::PP_COLOR_MODE",
               "Gamma/EC_Gamma.cpp", "CheckSetPictureProfile", "PP_GammaType", "GammaReg=")


def part(model: str, n: str) -> Path:
    return ROOT / "firmware/extracted" / FW[model] / PART.format(n)


def menu(usr: Path) -> dict[str, dict]:
    _, _, texts = uxc_strings.parse((usr / "share/app/string_english.uxc").read_bytes())
    lists = {n: {p: v for p, _, v in props} for n, props in
             setting_nodes.property_lists(usr / "lib/CautionConfig.so", r"^(PictureProfile|SLogDispAssist)")}
    out = {}
    for name, p in lists.items():
        if 0xE not in p:
            continue
        base = re.sub(r"(Root|Page\d+)$", "", name)
        opts = {texts.get(q[0] & 0xFFFF, "?"): q[0xF] for n, q in lists.items()
                if n.startswith(base) and n != name and 0xF in q and 0 in q and q.get(0xC) == 1}
        out[name] = {"pid": p[0xE], "texto": texts.get(p[0] & 0xFFFF, ""), "visible": p.get(0xB) == 2,
                     "opciones": dict(sorted(opts.items(), key=lambda kv: kv[1]))}
    return out


def paramid_pp(lib: Path) -> dict[str, int]:
    """Índice de cada `PARAMID_PP_*` en la tabla de punteros a nombres `PARAMID_*` de libObj.so."""
    d = lib.read_bytes()
    is_name = lambda v: 0 < v < len(d) and d[v:v + 8] == b"PARAMID_"
    h = d.find(struct.pack("<I", d.find(b"PARAMID_PP_GAMMA_TYPE\0")))
    s = h
    while is_name(struct.unpack_from("<I", d, s - 4)[0]):
        s -= 4
    out, i = {}, s
    while is_name(v := struct.unpack_from("<I", d, i)[0]):
        n = d[v:v + 64].split(b"\0")[0].decode()
        if n.startswith("PARAMID_PP_") and not n.endswith(("_SET", "_ACT")):
            out[n] = (i - s) // 4
        i += 4
    return out


def avcam(model: str) -> dict[str, int]:
    s = subprocess.run(["strings", "-n5", str(part(model, "nflasha3") / "av-cam.bin")], capture_output=True, text=True,
                       check=True).stdout
    return {m: s.count(m) for m in AVCAM_MARKS}


def main(dest: Path | None) -> dict:
    f6300 = json.loads((ROOT / "analysis/gui/g14/f6300.json").read_text())
    m = menu(part("a6300", "nflasha15"))
    for r in m.values():
        r["clase_a6300"] = f6300["cases"][str(f6300["pid2case"][r["pid"]])]
    res = {"menu_a6300": m, "menu_a6000": menu(part("a6000", "nflasha15")),
           "paramid_pp": {k: paramid_pp(part(k, "nflasha15") / "lib/libObj.so") for k in FW},
           "avcam": {k: avcam(k) for k in FW}}
    p = res["paramid_pp"]
    assert res["menu_a6000"] == {} and len(m) == 29, (len(res["menu_a6000"]), len(m))
    assert m["PictureProfileGammaRoot"]["pid"] == 0x101 and m["PictureProfileGammaRoot"]["opciones"]["S-Log2"] == 8
    assert all(p["a6000"][k] == v for k, v in p["a7s"].items() if k in p["a6000"]), "índices PARAMID_PP distintos"
    assert "PARAMID_PP_MODE" not in p["a6000"] and "PARAMID_PP_MODE" in p["a7s"]
    assert res["avcam"]["a6000"]["job_EC_CalcCaptureGamma"] == 0 < res["avcam"]["a7s"]["job_EC_CalcCaptureGamma"]
    if dest:
        dest.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    return res


if __name__ == "__main__":
    r = main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    print("menú A6300:", len(r["menu_a6300"]), "ajustes con ProcessId; A6000:", len(r["menu_a6000"]))
    for k, v in r["paramid_pp"].items():
        print(k, "PARAMID_PP_*:", len(v))
    for k, v in r["avcam"].items():
        print(k, v)
