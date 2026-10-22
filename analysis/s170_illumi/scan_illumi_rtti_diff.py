#!/usr/bin/env python3
"""S170 — comprueba si el *código* de las clases Illumi* existe en A7S fw3.20 / A6300 fw2.01.

Para cada imagen: localiza el typeinfo de `IllumiRPR0400` / `IllumiAd` / `IllumiCam`
a partir del puntero al nombre RTTI, extrae la vtable y sus ranuras, y comprueba si
alguna ranura apunta a código que reference el token `[ILLUMI]` (no en A7S/A6300) o
a código equivalente (patrón ReadDevice 0x39/0x46).
"""
import json
import struct

BASE = 0x43541000
FILES = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
U32 = struct.Struct("<I").unpack_from


def r32(b, a):
    return U32(b, a - BASE)[0]


def find_all(b, pat):
    out = []
    i = 0
    while True:
        j = b.find(pat, i)
        if j < 0:
            break
        out.append(BASE + j)
        i = j + 1
    return out


def main():
    res = {}
    for name, path in FILES.items():
        b = open(path, "rb").read()
        e = {}
        for cls in ("13IllumiRPR0400", "8IllumiAd", "9IllumiCam", "9IllumiDev"):
            name_addr = find_all(b, cls.encode())
            info = []
            for na in name_addr:
                # typeinfo: el puntero al nombre está en typeinfo+4 (layout Itanium)
                for ti in find_all(b, struct.pack("<I", na)):
                    # candidate typeinfo = ti-4 ; comprobar vptr razonable
                    if ti < 4:
                        continue
                    base = ti - 4
                    vptr = r32(b, base)
                    if not (BASE <= vptr < BASE + len(b)):
                        continue
                    # vtable: buscar punteros a (base) ; address point = ref+4
                    vts = [x + 4 for x in find_all(b, struct.pack("<I", base))]
                    slots = []
                    for vt in vts:
                        s = [r32(b, vt + 4 * k) for k in range(6)]
                        slots.append({"vt": hex(vt), "slots": [hex(x) for x in s]})
                    info.append({"name_addr": hex(na), "typeinfo": hex(base),
                                 "vptr": hex(vptr), "vtables": slots})
            e[cls] = {"nombres": [hex(x) for x in name_addr], "typeinfos": info}
            print(f"{name} {cls}: nombres={[hex(x) for x in name_addr]}")
            for i in info:
                print("   typeinfo", i["typeinfo"], "vptr", i["vptr"])
                for s in i["vtables"]:
                    print("      vt", s["vt"], s["slots"])
        res[name] = e
    json.dump(res, open("analysis/s170_illumi/illumi_rtti_diff.json", "w"), indent=1)


if __name__ == "__main__":
    main()
