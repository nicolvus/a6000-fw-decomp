#!/usr/bin/env python3
"""S180 - RTTI de AccyUmDeviceRemote en los tres firmware (type_info + vtable)."""
import struct, sys

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
CLASSES = [b"AccyUmDeviceRemote", b"AccyUmDeviceBase", b"AccyUmKeyStatusMgr",
           b"AccyUmDeviceHello", b"AccyMiDeviceBase", b"AccyMiDeviceLight"]


def u32(d, a):
    o = a - BASE
    if o < 0 or o + 4 > len(d):
        return None
    return struct.unpack_from("<I", d, o)[0]


def cstr(d, a):
    o = a - BASE
    if o < 0 or o >= len(d):
        return None
    e = o
    while e < len(d) and 32 <= d[e] < 127:
        e += 1
    return d[o:e].decode("latin1")


for k, p in BINS.items():
    d = open(p, "rb").read()
    print("=" * 72)
    print(k)
    for cn in CLASSES:
        i = d.find(cn)
        if i < 0:
            print(f"  {cn.decode()}: NO")
            continue
        # el nombre completo empieza en el prefijo de longitud ASCII (2 digitos)
        s = i
        while s > 0 and 32 <= d[s - 1] < 127 and not (48 <= d[s - 1] <= 57 and s - 1 >= 2 and
                                                      not (32 <= d[s - 2] < 127)):
            break
        # retroceder hasta el inicio real de la cadena
        st = i
        while st > 0 and 32 <= d[st - 1] < 127:
            st -= 1
        name_ptr = st + BASE
        cands = []
        for off in range(0, len(d) - 4, 4):
            if struct.unpack_from("<I", d, off)[0] == name_ptr:
                cands.append(off + BASE)
        print(f"  {cn.decode()}: cadena en 0x{name_ptr:08x} {d[st:i+len(cn)].decode('latin1')!r}"
              f"  type_info candidatos={[hex(c) for c in cands]}")
        for ti in cands:
            vt = u32(d, ti)
            nm = u32(d, ti + 4)
            base_ti = u32(d, ti + 8)
            bn = cstr(d, base_ti + 4) if base_ti else None
            print(f"     type_info 0x{ti:08x}: vtable=0x{vt:08x} name=0x{nm:08x} base=0x{base_ti:08x} ({bn!r})")
            vtbase = ti - 8
            print(f"       vtable 0x{vtbase:08x}: " +
                  " ".join(f"[{j}]0x{u32(d, vtbase+4*j):08x}" for j in range(6)))
