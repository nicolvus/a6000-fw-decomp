#!/usr/bin/env python3
"""Comparativa A6000 / A7S fw3.20 / A6300 del módulo de trazas [IMAGING_CAP].

Extrae las cadenas con el prefijo `[IMAGING_CAP]` de cada blob, cuenta, delimita
el rango, comprueba la presencia de los 16 nombres `*_Selector.cpp` y de la
tabla de 17 secciones, y calcula el diferencial de cadenas.
"""
import json
import re
import struct
import sys

BASE = 0x43541000
BLOBS = {
    "A6000-fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S-fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300-fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
PREFIX = b"[IMAGING_CAP]"
SELECTORS = [
    "CaptureAfterEffect", "CaptureAfterEnc", "CaptureAfterRead", "CaptureCorrectRaw",
    "CaptureDevEntry", "CaptureDevExit", "CaptureDevelop", "CaptureEncode",
    "CaptureExposure", "CaptureFeatureEffect", "CaptureMarble", "CaptureOpdBeforeNR",
    "CapturePrelight", "CaptureRead", "CaptureSortJpeg", "SequenceFilter",
]
TABLE = 0x43FF8FB4


def extract(path):
    data = open(path, "rb").read()
    out = []
    for m in re.finditer(re.escape(PREFIX), data):
        s = m.start()
        e = s
        while e < len(data) and 32 <= data[e] < 127:
            e += 1
        out.append((BASE + s, data[s:e].decode("latin1")))
    return data, out


def main():
    res = {}
    for name, path in BLOBS.items():
        try:
            data, strings = extract(path)
        except FileNotFoundError:
            print(f"{name}: no encontrado ({path})")
            continue
        texts = {t for _, t in strings}
        res[name] = {
            "n_strings": len(strings),
            "min": f"0x{strings[0][0]:x}" if strings else None,
            "max": f"0x{strings[-1][0]:x}" if strings else None,
            "selectors_present": [s for s in SELECTORS
                                  if f"{s}_Selector.cpp".encode() in data],
            "selectors_absent": [s for s in SELECTORS
                                 if f"{s}_Selector.cpp".encode() not in data],
            "table_17_entries": None,
            "strings": {f"0x{a:x}": t for a, t in strings},
        }
        if name == "A6000-fw321":
            ents = []
            for i in range(17):
                off = TABLE - BASE + i * 8
                sid, fn = struct.unpack("<II", data[off:off + 8])
                ents.append((sid, fn & ~1))
            res[name]["table_17_entries"] = [[s, f"0x{f:x}"] for s, f in ents]
        print(f"{name}: {len(strings)} cadenas, "
              f"{res[name]['min']}-{res[name]['max']}, "
              f"selectors presentes={len(res[name]['selectors_present'])}/16")

    if "A6000-fw321" in res and "A7S-fw320" in res:
        a = set(res["A6000-fw321"]["strings"].values())
        b = set(res["A7S-fw320"]["strings"].values())
        res["diff_a6000_only"] = sorted(a - b)
        res["diff_a7s_only"] = sorted(b - a)
        print(f"solo A6000: {len(res['diff_a6000_only'])}, solo A7S: {len(res['diff_a7s_only'])}")

    out = "analysis/s104_imaging_cap/imaging_cap_a7s_diff.json"
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    print("escrito", out)


if __name__ == "__main__":
    sys.exit(main())
