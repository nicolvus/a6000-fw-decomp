#!/usr/bin/env python3
"""S382 v2: encontrar inicios de función reales recolectando targets de BL/BLX."""
import struct
from pathlib import Path
from capstone import *

PATH = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
            "firmware/extracted/fw321/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
data = PATH.read_bytes()

e_shoff = struct.unpack_from("<I", data, 0x20)[0]
e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
e_shnum = struct.unpack_from("<H", data, 0x30)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x32)[0]
sec_list = []
for i in range(e_shnum):
    off = e_shoff + i * e_shentsize
    st_name, stype, flags, addr, offset, size, link, info, align, entsize = \
        struct.unpack_from("<IIIIIIIIII", data, off)
    sec_list.append({"idx": i, "name": "", "st_name": st_name, "type": stype,
                     "flags": flags, "addr": addr, "off": offset, "size": size})
shstr_off = sec_list[e_shstrndx]["off"]
def sname(idx):
    s = sec_list[idx]
    end = data.index(b"\x00", shstr_off + s["st_name"])
    return data[shstr_off + s["st_name"]:end].decode()
for i in range(e_shnum):
    sec_list[i]["name"] = sname(i)
secs = {s["name"]: s for s in sec_list}

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True
text_va = secs[".text"]["addr"]
text_end = text_va + secs[".text"]["size"]

# --- Recolectar todos los targets de BL/BLX ---
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

bl_targets = set()
for off in range(text_va, text_end - 3, 2):
    tgt = decode_bl_blx(off)
    if tgt is not None and text_va <= tgt < text_end:
        bl_targets.add(tgt)

print(f"Targets únicos de BL/BLX en .text: {len(bl_targets)}")

# --- Buscar hacia atrás desde candidatos hasta encontrar un target de BL/BLX ---
CANDIDATES = [0x90de2e, 0x91634e]
for cand in CANDIDATES:
    print(f"\n=== 0x{cand:08x} ===")
    # Retroceder en pasos de 2 (Thumb/ARM). Buscar tanto la dirección par (ARM)
    # como la impar (Thumb bit0=1) ya que los targets de BL/BLX tienen bit0=1 para Thumb.
    found = None
    for variant in [cand, cand | 1]:
        v = variant
        while v >= text_va:
            if v in bl_targets:
                found = v
                break
            v -= 2
        if found:
            break
    if found:
        print(f"  Inicio de función probable: 0x{found:08x} (es target de BL/BLX)")
        # Desensamblar desde ahí
        i = found
        count = 0
        while i < min(found + 200, text_end) and count < 60:
            try:
                ins = list(md.disasm(data[i:i+4], i))
                if ins:
                    ins = ins[0]
                    mark = f"  <-- CANDIDATE 0x{cand:08x}" if i == cand else ""
                    print(f"    0x{i:08x}: {ins.mnemonic:<10} {ins.op_str}{mark}")
                    i = ins.address + ins.size
                    count += 1
                else:
                    i += 2
            except:
                i += 2
    else:
        print(f"  No se encontró target de BL/BLX hacia atrás (hasta inicio .text)")
    
    # También buscar hacia adelante para ver dónde termina la función
    print(f"  Contexto alrededor de 0x{cand:08x}:")
    i = cand - 16
    while i <= cand + 16:
        if i in bl_targets:
            print(f"    >>> 0x{i:08x} ES TARGET DE BL/BLX <<<")
        try:
            ins = list(md.disasm(data[i:i+4], i))
            if ins:
                ins = ins[0]
                mark = "  <-- CANDIDATE" if i == cand else ""
                print(f"    0x{i:08x}: {ins.mnemonic:<10} {ins.op_str}{mark}")
                i = ins.address + ins.size
            else:
                i += 2
        except:
            i += 2
