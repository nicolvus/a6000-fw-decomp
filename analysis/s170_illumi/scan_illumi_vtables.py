#!/usr/bin/env python3
"""S170 — vtables de las clases Illumi* + tabla de IDs OSAL 0x10600xx."""
import json
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
N = len(B)


def r32(a):
    return struct.unpack_from("<I", B, a - BASE)[0]


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    return B[o:e].decode("ascii", "replace")


TI = {
    "IllumiDev": 0x43fdaa74,
    "IllumiAd": 0x43fdaa7c,
    "IllumiCam": 0x43fdaa8c,
    "IllumiRPR0400": 0x43fdaa98,
}


def ptr_refs(value):
    pat = struct.pack("<I", value)
    out = []
    i = 0
    while True:
        j = B.find(pat, i)
        if j < 0:
            break
        out.append(BASE + j)
        i = j + 1
    return out


def main():
    res = {}
    for nm, ti in TI.items():
        refs = ptr_refs(ti)
        vts = [r + 8 for r in refs]     # el typeinfo está en vtable-8
        print(f"== {nm} typeinfo={ti:#x} refs={len(refs)} vtables={[hex(v) for v in vts]}")
        info = []
        for vt in vts:
            slots = [r32(vt + 4 * k) for k in range(8)]
            # cortar en el 0
            n = 0
            while n < 8 and slots[n] != 0:
                n += 1
            slots = slots[:n + 1]
            print(f"   vt={vt:#x}")
            for k, s in enumerate(slots):
                print(f"      [{k}] {s:#x}")
            info.append({"addr": hex(vt), "slots": [hex(s) for s in slots]})
        res[nm] = {"typeinfo": hex(ti), "vtables": info}

    # tabla de IDs 0x10600xx alrededor de 0x43fdaaa4
    tab = []
    for a in range(0x43fdaa9c, 0x43fdaac0, 4):
        v = r32(a)
        tab.append((hex(a), hex(v)))
    print("\nIDs 0x10600xx alrededor de los typeinfo:")
    for a, v in tab:
        print("  ", a, v)
    res["_ids_0x10600xx"] = tab
    json.dump(res, open("analysis/s170_illumi/illumi_vtables.json", "w"), indent=1)


if __name__ == "__main__":
    main()
