#!/usr/bin/env python3
"""Resumen estructurado del hito S110 (motor de imagen YC, `[CAMERA_MAIN_YC]`).

Reúne: cadenas por bloque, sub-módulo (la etiqueta tras `[CAMERA_MAIN_YC]:`), API
`api_YC_*` y jobs `job_YC_*` con la función que los referencia, y el diferencial
A6000 vs A7S fw3.20.
"""
import json
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 0x43541000
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


def submod(text):
    m = re.match(r"\[CAMERA_MAIN_YC\]:\s*([A-Za-z][A-Za-z0-9_]{1,19})[:\s]", text)
    return m.group(1) if m else None


def main():
    strings = json.load(open(os.path.join(HERE, "strings_raw.json")))["strings"]
    blocks = json.load(open(os.path.join(HERE, "blocks.json")))["blocks"]
    fmap = json.load(open(os.path.join(HERE, "func_map.json")))

    # sub-módulos
    sub = defaultdict(list)
    for s in strings:
        t = submod(s["text"])
        if t:
            sub[t].append(s)
    subs = []
    for t, ss in sorted(sub.items(), key=lambda kv: -len(kv[1])):
        funcs = sorted({f["func"] for f in fmap["functions"]
                        for x in f["strings"] if x["vaddr"] in {y["vaddr"] for y in ss}})
        subs.append({"submodule": t, "n": len(ss), "n_functions": len(funcs),
                     "lo": min(x["vaddr"] for x in ss), "hi": max(x["vaddr"] for x in ss),
                     "sample": [x["text"][:110] for x in ss[:3]]})

    # API y jobs: función que referencia el nombre
    api, jobs = defaultdict(set), defaultdict(set)
    for f in fmap["functions"]:
        for s in f["strings"]:
            for m in re.finditer(r"\b(api_YC_[A-Za-z0-9_]+)", s["text"]):
                api[m.group(1)].add(f["func"])
            for m in re.finditer(r"\b(job_YC_[A-Za-z0-9_]+)", s["text"]):
                jobs[m.group(1)].add(f["func"])

    def pick(d):
        out = {}
        for k, v in sorted(d.items()):
            out[k] = sorted(v)
        return out

    # diferencial A7S
    a7s = open(os.path.join(os.path.dirname(HERE), "..", A7S), "rb").read()
    diff = {"A7S_prefix_count": a7s.count(b"[CAMERA_MAIN_YC]")}
    for probe in (b"YAP:\tjob_YC_RawDevMakerNote_Yap_apc_init",
                  b"MARBLE: MOV\t<MBL_MOV_Image_Mod> ul_rc_zo",
                  b"job_YC_RawDevMakerNote_Yap_apc_lpf"):
        i = a7s.find(probe)
        diff.setdefault("probes", {})[probe.decode("latin1")[:40]] = (
            f"0x{BASE + i:x}" if i >= 0 else None)

    out = {
        "milestone": "S110",
        "module": "CAMERA_MAIN_YC",
        "counts": {
            "strings": len(strings),
            "blocks": len(blocks),
            "functions": fmap["n_functions"],
            "submodules": len(subs),
            "api_yc": len(api),
            "job_yc": len(jobs),
        },
        "blocks": [{"lo": b["lo"], "hi": b["hi"], "n": b["n"]} for b in blocks],
        "submodules": subs,
        "api_yc": pick(api),
        "job_yc": pick(jobs),
        "a7s": diff,
    }
    dest = os.path.join(HERE, "yc_summary.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["counts"], indent=1))
    print("api_yc:", json.dumps(out["api_yc"], indent=1))
    print("job_yc:", json.dumps(out["job_yc"], indent=1))
    print("escrito", dest)


if __name__ == "__main__":
    main()
