#!/usr/bin/env python3
"""S180 - vtables de las clases AccyUm* en los tres firmware (y sus funciones)."""
import struct, json

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
TI = {
    "A6000": {"AccyUmDeviceBase": 0x43fd7c8c, "AccyUmDeviceRemote": 0x43fd7dbc,
              "AccyUmKeyStatusMgr": 0x43fd7d78, "AccyUmDeviceHello": 0x43fd7d98},
    "A7S": {"AccyUmDeviceBase": 0x43fd99f4, "AccyUmDeviceRemote": 0x43fd9b24,
            "AccyUmKeyStatusMgr": 0x43fd9ae0, "AccyUmDeviceHello": 0x43fd9b00},
    "A6300": {"AccyUmDeviceBase": 0x441992ec, "AccyUmDeviceRemote": 0x4419941c,
              "AccyUmKeyStatusMgr": 0x441993d8, "AccyUmDeviceHello": 0x441993f8},
}


def u32(d, a):
    o = a - BASE
    if o < 0 or o + 4 > len(d):
        return None
    return struct.unpack_from("<I", d, o)[0]


out = {}
for k, p in BINS.items():
    d = open(p, "rb").read()
    print("=" * 72)
    print(k)
    out[k] = {}
    for cls, ti in TI[k].items():
        # buscar punteros al type_info (vtable-8)
        cands = [off + BASE for off in range(0, len(d) - 4, 4)
                 if struct.unpack_from("<I", d, off)[0] == ti]
        print(f"  {cls}: type_info=0x{ti:08x}  punteros={[hex(c) for c in cands]}")
        for c in cands:
            vt = c + 8
            ent = [u32(d, vt + 4 * j) for j in range(8)]
            print(f"      vtable 0x{vt:08x}: " + " ".join(f"0x{e:08x}" for e in ent))
            out[k].setdefault(cls, {})[f"0x{vt:x}"] = [f"0x{e:x}" for e in ent]
json.dump(out, open("analysis/s180_remote/vtables.json", "w"), indent=1)
