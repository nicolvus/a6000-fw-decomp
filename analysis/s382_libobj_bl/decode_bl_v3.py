#!/usr/bin/env python3
"""S382 v3: quién llama a las funciones contenedoras 0x90de2c y 0x91631e."""
import struct
from pathlib import Path
from capstone import *

PATH = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
            "firmware/extracted/fw321/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
data = PATH.read_bytes()

# Secciones
e_shoff = struct.unpack_from("<I", data, 0x20)[0]
e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
e_shnum = struct.unpack_from("<H", data, 0x30)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x32)[0]
sec_list = []
for i in range(e_shnum):
    off = e_shoff + i * e_shentsize
    st_name, stype, flags, addr, offset, size, link, info, align, entsize = \
        struct.unpack_from("<IIIIIIIIII", data, off)
    sec_list.append({"name": "", "st_name": st_name, "addr": addr,
                     "off": offset, "size": size})
shstr_off = sec_list[e_shstrndx]["off"]
def sname(idx):
    s = sec_list[idx]
    end = data.index(b"\x00", shstr_off + s["st_name"])
    return data[shstr_off + s["st_name"]:end].decode()
for i in range(e_shnum):
    sec_list[i]["name"] = sname(i)
secs = {s["name"]: s for s in sec_list}

text_va = secs[".text"]["addr"]
text_end = text_va + secs[".text"]["size"]

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True

def decode_bl_blx(off):
    va = off
    hw1 = data[off] | (data[off+1] << 8)
    hw2 = data[off+2] | (data[off+3] << 8)
    if (hw2 & 0xFE00) == 0xF800:
        s = (hw2 >> 8) & 1
        imm10 = hw2 & 0xFF
        imm11 = hw1 & 0x7FF
        imm24 = (s << 23) | (imm10 << 13) | imm11
        if imm24 & 0x800000:
            imm24 |= ~0xFFFFFF
        return va + 4 + (imm24 << 1)
    elif (hw2 & 0xFE00) == 0xFA00:
        s = (hw2 >> 8) & 1
        imm10 = hw2 & 0xFF
        imm11 = hw1 & 0x7FF
        h = (imm10 >> 9) & 1
        j1 = (imm11 >> 12) & 1
        j2 = (imm11 >> 11) & 1
        i1 = (imm11 >> 10) & 1
        i2 = imm11 & 0x3FF
        imm32 = (s << 24) | (h << 23) | ((~j1 & 1) << 22) | ((~j2 & 1) << 21) | (imm10 << 12) | (i1 << 11) | i2
        if imm32 & 0x800000:
            imm32 |= ~0xFFFFFFFF
        return va + 4 + imm32
    return None

CONTAINERS = [0x0090de2c, 0x0091631e]
print("=== Quién llama a las funciones contenedoras ===\n")
for cont in CONTAINERS:
    targets = [cont | 1, cont]  # Thumb target (bit0=1) y ARM target (bit0=0)
    callers = []
    for off in range(text_va, text_end - 3, 2):
        tgt = decode_bl_blx(off)
        if tgt is not None and tgt in targets:
            callers.append((off, tgt))
    print(f"Llamadores a 0x{cont:08x}: {len(callers)}")
    for va, tgt in callers[:30]:
        print(f"  BL/BLX en 0x{va:08x} -> 0x{tgt:08x}")
    print()
