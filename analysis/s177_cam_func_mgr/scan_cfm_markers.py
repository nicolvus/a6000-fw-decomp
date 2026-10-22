#!/usr/bin/env python3
"""S177 — busca marcadores del subsistema Camera::Function en los tres firmwares.

Marcadores:
  * nombres de clase RTTI mangled `N6Camera8Function<len><Name>E`
  * rutas de fichero `Function/...`, `api/capcon_api_*.cpp`, `wrapper/*.cpp`, `tsk/tsk_*.cpp`
  * el token `[CAM_FUNC_MGR]`
  * la palabra `Capcon` / `CAPCON`
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
FILES = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
RE_RTTI = re.compile(rb"N6Camera8Function\d+[A-Za-z_0-9]+E")
RE_PATH = re.compile(rb"(?:Function|wrapper|tsk|api)/[A-Za-z_0-9]+\.cpp")
RE_CAPCON = re.compile(rb"[Cc][Aa][Pp][Cc][Oo][Nn][A-Za-z_0-9]*")

out = {}
for name, path in FILES.items():
    b = open(os.path.join(ROOT, path), "rb").read()
    rtti = []
    for m in RE_RTTI.finditer(b):
        s = m.group().decode("ascii")
        if s not in [x["texto"] for x in rtti]:
            rtti.append({"texto": s, "vaddr": hex(m.start() + BASE)})
    paths = []
    for m in RE_PATH.finditer(b):
        s = m.group().decode("ascii")
        paths.append({"texto": s, "vaddr": hex(m.start() + BASE)})
    capcon = []
    for m in RE_CAPCON.finditer(b):
        s = m.group().decode("ascii")
        capcon.append({"texto": s, "vaddr": hex(m.start() + BASE)})
    out[name] = {"rtti": rtti, "paths": paths, "capcon": capcon,
                 "n_capcon": len(capcon)}
    print(f"== {name}: rtti={len(rtti)} paths={len(paths)} capcon_ocurrencias={len(capcon)}")

json.dump(out, open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_markers.json"), "w"),
          indent=1)

for name in FILES:
    print(f"\n--- {name} RTTI Camera::Function ---")
    for x in out[name]["rtti"]:
        print("   ", x["vaddr"], x["texto"])
    print(f"--- {name} paths ---")
    for x in out[name]["paths"]:
        print("   ", x["vaddr"], x["texto"])
