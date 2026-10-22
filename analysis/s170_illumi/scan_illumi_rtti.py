#!/usr/bin/env python3
"""S170 — RTTI de las clases Illumi* (A6000 fw3.21) y vtables asociadas.

Busca los typeinfo Itanium (`__class_type_info` / `__si_class_type_info`) cuyo
nombre sea `NIllumi...`, y extrae: typeinfo, clase base, vtable (address point).
"""
import json
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

NAMES = ["9IllumiDev", "8IllumiAd", "9IllumiCam", "13IllumiRPR0400"]


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    return B[o:e].decode("ascii", "replace")


def r32(a):
    return U32(B, a - BASE)[0]


def find_occurrences(needle):
    out = []
    pat = needle.encode()
    start = 0
    while True:
        i = B.find(pat, start)
        if i < 0:
            break
        out.append(BASE + i)
        start = i + 1
    return out


def main():
    res = {}
    for nm in NAMES:
        occ = find_occurrences(nm)
        print(f"== {nm}: {len(occ)} apariciones {[hex(x) for x in occ]}")
        for o in occ:
            # el typeinfo tiene: [vptr][nameptr][...]; el nameptr apunta al nombre
            # buscamos punteros absolutos a 'o' en la imagen (4 bytes LE)
            pat = struct.pack("<I", o)
            refs = []
            i = 0
            while True:
                j = B.find(pat, i)
                if j < 0:
                    break
                refs.append(BASE + j)
                i = j + 1
            print(f"   nombre@{o:#x} refs_4B={len(refs)}")
            for r in refs:
                # comprobar si es un typeinfo: vptr debe apuntar a _ZTVN10__cxxabiv117__class_type_infoE etc
                vptr = r32(r)
                nameptr = r32(r + 4)
                nm2 = cstr(nameptr) if nameptr else None
                print(f"      ptr@{r:#x}: vptr={vptr:#x} nameptr={nameptr:#x} name={nm2!r}")
                if nm2 and nm2.endswith(nm):
                    # vtable address point: buscar en la .rodata un puntero a (r - 8)
                    ti = r
                    pat2 = struct.pack("<I", ti - 8)
                    vts = []
                    i = 0
                    while True:
                        j = B.find(pat2, i)
                        if j < 0:
                            break
                        vts.append(BASE + j + 8)
                        i = j + 1
                    print(f"      typeinfo={ti:#x} vtables_candidatas={[hex(v) for v in vts]}")
                    for vt in vts:
                        slots = []
                        for k in range(8):
                            slots.append(hex(r32(vt + 4 * k)))
                        print(f"        vt={vt:#x} slots={slots}")
                    res[nm] = {"name_addr": hex(o), "typeinfo": hex(ti),
                               "vptr": hex(vptr), "base_ptr": hex(nameptr),
                               "vtables": [{"addr": hex(v),
                                            "slots": [hex(r32(v + 4 * k)) for k in range(8)]}
                                           for v in vts]}
    json.dump(res, open("analysis/s170_illumi/illumi_rtti.json", "w"), indent=1)


if __name__ == "__main__":
    main()
