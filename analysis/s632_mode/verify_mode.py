#!/usr/bin/env python3
"""S632: sufijos [MODE_*] de los diagnósticos «CamCore acquire Error» de [IMAGING_CAP] y [MODEFLG] de [CAM_UTIL_SENS].

Lee av-cam.bin (A6000 fw3.21, base 0x43541000) y los de A7S fw3.20 / A6300 fw2.01. Sin ejecutar firmware.
shortcut: la rama de cada sitio se acota con los 0x40 B previos; las constantes son `movs rN,#imm` de 16 bits.
"""
import bisect, json, re, struct, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "analysis"), str(ROOT / "analysis/camera_closure"), str(ROOT / "analysis/s106_imaging_cap")]
import closure as C, closure2 as K, verify_s6xx as V

B, BASE = K.B, K.BASE
SHUTTER = C.SHUTTER
LOGGER = 0x437f5414
ACQUIRE = 0x43ae82e4


def modes():
    return [(BASE + m.start(), m.group().decode()) for m in re.finditer(rb"\[IMAGING_CAP\]: CamCore [Aa]c?qu?ire Error!: %02x\[MODE_[A-Z_]+\]", B)]


def branch(site):
    """bl previos al sitio (posición, destino) y constantes `movs rN,#imm` entre el último bl previo y el sitio."""
    pairs = sorted((a, t) for t, aa in K.bl_callers().items() for a in aa if site - 0x40 <= a < site + 8)
    acq = next(a for a, t in pairs if t == ACQUIRE)
    consts = {"acquire": {}, "log": {}}
    for a in range(acq - 0x14, site + 2, 2):
        h = struct.unpack_from("<H", B, a - BASE)[0]
        if (h & 0xF800) == 0x2000 and ((h >> 8) & 7) <= 3:
            consts["acquire" if a < acq else "log"][f"r{(h >> 8) & 7}"] = h & 0xFF
    return [(hex(a), hex(t)) for a, t in pairs], consts


def build():
    refs = K.S.scan(BASE, BASE + K.N)
    out = {"strings": [], "mode_flg": None, "tokens": {}}
    for a, text in modes():
        site = next(iter(refs.get(a, [])), None)
        sites = refs.get(a, [])
        row = {"vaddr": hex(a), "text": text, "sufijo": re.search(r"\[(MODE_[A-Z_]+)\]", text).group(1), "sitios": [hex(s) for s in sites],
               "funcion": hex(C.func_start(sites[0])) if sites else None}
        row["ramas"] = [dict(zip(("bls", "consts"), branch(s))) for s in sites]
        row["a7s"] = C.tokens(V.FIRMWARE["a7s_fw320"], re.search(r"\[MODE_[A-Z_]+\]", text).group()); row["a6300"] = C.tokens(V.FIRMWARE["a6300_fw201"], re.search(r"\[MODE_[A-Z_]+\]", text).group())
        out["strings"].append(row)
    funcs = sorted({r["funcion"] for r in out["strings"]})
    out["funciones"] = funcs
    out["alcance_obturador"] = {f: sorted(SHUTTER[x] for x in C.reach(int(f, 16), 3) if x in SHUTTER) for f in funcs}
    m = re.search(rb"\[CAM_UTIL_SENS\]: +\[MODEFLG\]:%x", B)
    a = BASE + m.start()
    s = refs.get(a, [])
    out["mode_flg"] = {"vaddr": hex(a), "sitios": [hex(x) for x in s], "funcion": hex(C.func_start(s[0])) if s else None,
                       "a7s": C.tokens(V.FIRMWARE["a7s_fw320"], "[MODEFLG]"), "a6300": C.tokens(V.FIRMWARE["a6300_fw201"], "[MODEFLG]")}
    out["tokens"] = {"[MODE_": {k: C.tokens(p, "[MODE_") for k, p in V.FIRMWARE.items()}}
    return out


if __name__ == "__main__":
    d = build()
    (ROOT / "analysis/s632_mode/mode.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
    for r in d["strings"]:
        print(r["sufijo"], r["vaddr"], r["sitios"], r["funcion"], r["a7s"], r["a6300"], [(x["bls"][-2:], x["consts"]) for x in r["ramas"]][:1])
    print(d["funciones"], d["alcance_obturador"], d["mode_flg"], d["tokens"])
