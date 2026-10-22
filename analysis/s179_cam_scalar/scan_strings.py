#!/usr/bin/env python3
"""S179 - localizar las cadenas del token [CAM_SCALAR] en los tres firmware."""
import json, os, sys

BASE = 0x43541000
BINS = {
 "A6000": "analysis/rea-independent/input/av-cam.bin",
 "A7S":   "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
 "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
TOKEN = b"[CAM_SCALAR]"

def strings_with_token(data):
    out = []
    i = 0
    n = len(data)
    while True:
        j = data.find(TOKEN, i)
        if j < 0: break
        # inicio de cadena
        s = j
        while s > 0 and 32 <= data[s-1] < 127:
            s -= 1
        e = j
        while e < n and 32 <= data[e] < 127:
            e += 1
        out.append((s, e, data[s:e]))
        i = j + 1
    return out

res = {}
for k, p in BINS.items():
    if not os.path.exists(p):
        print("FALTA", k, p); continue
    d = open(p, "rb").read()
    st = strings_with_token(d)
    print(f"{k}: {len(d)} B, ocurrencias token={d.count(TOKEN)}, cadenas={len(st)}")
    res[k] = [{"off": s, "vaddr": s + BASE, "text": t.decode("latin1")} for s, e, t in st]

json.dump(res, open("analysis/s179_cam_scalar/strings_raw.json", "w"), indent=1)
