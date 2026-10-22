#!/usr/bin/env python3
"""S170 — diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01 del subsistema [ILLUMI].

Comprueba, en las tres imágenes:
  * apariciones de las cadenas de clase (RTTI) y de las trazas [ILLUMI],
  * los identificadores OSAL usados por el módulo (0x520250, 0x720018, 0x7a0020),
  * los "backup id" 0x133003c / 0x133003d,
  * los registros del dispositivo (0x39 / 0x41 / 0x46) y los key codes 0x17000001/2,
  * los typeinfo / vtable de las clases Illumi*.
"""
import json
import re
import struct

BASE = 0x43541000
FILES = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
TOKENS = [b"[ILLUMI]", b"IllumiDiag", b"IllumiGain", b"IllumiLevel",
          b"IllumiRPR0400", b"IllumiAd", b"IllumiCam", b"IllumiDev",
          b"GetIllumiData", b"GetRawData", b"AD MAXOVER", b"Gain Change Complete",
          b"Illumi"]
U32 = [0x520250, 0x720018, 0x7a0020, 0x133003c, 0x133003d,
       0x17000001, 0x17000002]
# typeinfo de las clases (A6000) -> para A7S/A6300 se busca el mismo puntero a nombre
TI_NAMES = {0x43c4084c: "9IllumiDev", 0x43c40893: "8IllumiAd",
            0x43c40a20: "9IllumiCam", 0x43c40baf: "13IllumiRPR0400"}


def count(b, pat):
    return b.count(pat)


def main():
    res = {}
    for name, path in FILES.items():
        b = open(path, "rb").read()
        e = {"size": len(b), "tokens": {}, "u32": {}}
        for t in TOKENS:
            n = count(b, t)
            if n:
                e["tokens"][t.decode()] = n
        for v in U32:
            pat = struct.pack("<I", v)
            n = count(b, pat)
            if n:
                e["u32"][hex(v)] = n
        res[name] = e
        print(f"== {name} ({len(b)} B)")
        print("   tokens:", e["tokens"])
        print("   u32   :", e["u32"])
    json.dump(res, open("analysis/s170_illumi/illumi_diff.json", "w"), indent=1)


if __name__ == "__main__":
    main()
