#!/usr/bin/env python3
"""S180 - localizar las cadenas del token [REMOTE] en los tres firmware.

Convencion: vaddr = 0x43541000 + file_offset (valida para A6000 fw3.21,
A7S fw3.20 y A6300 fw2.01).
"""
import json, os, sys

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
TOKEN = b"[REMOTE]"


def strings_with_token(data, tok=TOKEN):
    out = []
    i = 0
    n = len(data)
    while True:
        j = data.find(tok, i)
        if j < 0:
            break
        s = j
        while s > 0 and 32 <= data[s - 1] < 127:
            s -= 1
        e = j
        while e < n and 32 <= data[e] < 127:
            e += 1
        out.append((s, e, data[s:e]))
        i = j + 1
    return out


def main():
    res = {}
    for k, p in BINS.items():
        if not os.path.exists(p):
            print("FALTA", k, p)
            continue
        d = open(p, "rb").read()
        st = strings_with_token(d)
        print(f"{k}: {len(d)} B, ocurrencias token={d.count(TOKEN)}, cadenas={len(st)}")
        res[k] = [
            {"off": s, "vaddr": s + BASE, "text": t.decode("latin1")}
            for s, e, t in st
        ]
    out = "analysis/s180_remote/strings_raw.json"
    json.dump(res, open(out, "w"), indent=1)
    print("->", out)


if __name__ == "__main__":
    main()
