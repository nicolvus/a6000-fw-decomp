#!/usr/bin/env python3
"""S135 — barrido de términos de obturador electrónico en los tres `av-cam.bin`.

Compara A6000 fw3.21, A7S fw3.20 y A6300 fw2.01 y vuelca el recuento de cada término
y el contexto de cada coincidencia.

Salida: analysis/s135_elec_shutter/elec_shutter_scan.json
"""
import json
import os
import re

BASE = 0x43541000
BLOBS = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
TERMINOS = [
    "ElecShutter", "EC_ElecShutter", "EC_NonlinearElecShutter", "ElecShutter_Main",
    "MechShutterTable", "SilentShutterMode", "CheckSetSilentShutterMode",
    "front_eshutter", "CheckSetFrontEshutter", "shutterType", "CheckSetShutterType",
    "SET Silent Shutter Type", "efcs", "EFCS", "electronic", "Electronic", "curtain",
    "rolling", "mechanical", "Mechanical", "flicker", "silent", "Silent", "SILENT",
    "shutter", "Shutter",
]
HERE = os.path.dirname(os.path.abspath(__file__))


def contexto(data, i, antes=80, despues=80):
    ini = data.rfind(b"\x00", 0, i) + 1
    fin = data.find(b"\x00", i)
    if fin < 0:
        fin = i + despues
    return data[ini:fin].decode("latin1")


def main():
    datos = {k: open(v, "rb").read() for k, v in BLOBS.items()}
    out = {"milestone": "S135", "base": BASE, "counts": {}, "hits": {}}
    for t in TERMINOS:
        tb = t.encode()
        out["counts"][t] = {k: d.count(tb) for k, d in datos.items()}
    for t in TERMINOS:
        tb = t.encode()
        for k, d in datos.items():
            hits = []
            for m in re.finditer(re.escape(tb), d):
                hits.append({"vaddr": f"0x{BASE + m.start():x}",
                             "contexto": contexto(d, m.start())[:200]})
            if hits:
                out["hits"].setdefault(t, {})[k] = hits
    dest = os.path.join(HERE, "elec_shutter_scan.json")
    json.dump(out, open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"{'término':30s} {'A6000':>6s} {'A7S':>6s} {'A6300':>6s}")
    for t in TERMINOS:
        c = out["counts"][t]
        print(f"{t:30s} {c['A6000_fw321']:6d} {c['A7S_fw320']:6d} {c['A6300_fw201']:6d}")
    print("escrito", dest)


if __name__ == "__main__":
    main()
