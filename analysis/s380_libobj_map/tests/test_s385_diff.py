#!/usr/bin/env python3
"""Test S385: verifica métricas comparativas libObj.so A6000 vs A7S."""
import struct
from pathlib import Path

A6000 = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
             "firmware/extracted/fw321/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
A7S = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
           "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
           "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")

def read_elf_meta(path):
    data = path.read_bytes()
    e_shoff = struct.unpack_from("<I", data, 0x20)[0]
    e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
    e_shnum = struct.unpack_from("<H", data, 0x30)[0]
    sec_list = []
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        st_name, stype, flags, addr, offset, size = struct.unpack_from("<IIIIII", data, off)
        sec_list.append({"addr": addr, "off": offset, "size": size, "type": stype})
    # Encontrar índices por orden conocido (de readelf)
    # .text es típicamente después de .plt
    return data, sec_list

def test_sizes():
    a = A6000.stat().st_size
    b = A7S.stat().st_size
    assert a == 17436172, f"A6000 size {a}"
    assert b == 16184848, f"A7S size {b}"
    assert a > b, "A6000 debe ser más grande que A7S"

def test_entry_points():
    a = A6000.read_bytes()
    b = A7S.read_bytes()
    ea = struct.unpack_from("<I", a, 0x18)[0]
    eb = struct.unpack_from("<I", b, 0x18)[0]
    assert ea == 0x000e2b70, f"A6000 entry 0x{ea:08x}"
    assert eb == 0x000e5ff0, f"A7S entry 0x{eb:08x}"

def test_needed_libs_same():
    # Ambas tienen las mismas 17 NEEDED (verificado por readelf)
    needed = ["libInfraFsys.so", "libmprctrl.so", "libMWF.so", "libmpr.so",
              "libutil_date.so", "libcompassutil.so", "libsencore.so",
              "libBizFw.so", "libBizFw2.so", "libNetContUtil.so",
              "libUsbControl.so", "libNetCommon.so", "libGOConnectionManager.so",
              "libInfraMediaCommon.so", "libbackup.so", "libgcc_s.so.1",
              "libc.so.6"]
    for path in [A6000, A7S]:
        data = path.read_bytes()
        for lib in needed:
            # Buscar el nombre de la librería en .dynstr (aproximado)
            assert lib.encode() in data, f"{lib} no encontrado en {path}"

def test_key_exports_present():
    keys = ["ObjStillRecorder_Init", "ObjStillRecorder_Create",
            "InfraStillPool_Init", "StateMgr"]
    for path in [A6000, A7S]:
        data = path.read_bytes()
        for k in keys:
            assert k.encode() in data, f"{k} no en {path}"

if __name__ == "__main__":
    test_sizes(); print("PASS test_sizes")
    test_entry_points(); print("PASS test_entry_points")
    test_needed_libs_same(); print("PASS test_needed_libs_same")
    test_key_exports_present(); print("PASS test_key_exports_present")
    print("\nTodos los tests S385 PASS")
