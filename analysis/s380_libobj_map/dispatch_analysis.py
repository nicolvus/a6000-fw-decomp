#!/usr/bin/env python3
"""S380/S381: RecordStill::Execute cuerpo + xrefs; .plt osal_* y sus llamadores."""
import struct
from capstone import *
from pathlib import Path

BASE = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter")
PATH = BASE / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
data = PATH.read_bytes()
BASE_VA = 0  # PIE, offset de archivo == VA para el primer segmento LOAD

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True

def disasm_range(start, end):
    """Desensambla [start, end) siguiendo flujo lineal simple."""
    a = start
    out = []
    while a < end:
        try:
            insns = list(md.disasm(data[a:a + 4], a))
            if insns:
                insn = insns[0]
                out.append((insn.address, insn.mnemonic, insn.op_str, insn.size))
                a = insn.address + insn.size
            else:
                a += 2
        except Exception:
            a += 2
    return out

# --- 1. Cuerpo de RecordStill::Execute en 0x90b248 ---
print("=" * 70)
print("RecordStill::Execute @ 0x90b248 (cuerpo, 0x90b248..0x90b400)")
print("=" * 70)
for addr, mnem, op, size in disasm_range(0x90b248, 0x90b400):
    print(f"0x{addr:08x}: {mnem:<10} {op}")

# --- 2. Buscar xrefs (BL/BLX) a 0x90b248 en todo libObj.so ---
print("\n" + "=" * 70)
print("Xrefs BL/BLX a 0x90b248 (RecordStill::Execute) en libObj.so")
print("=" * 70)
TARGET = 0x90b248
xrefs = []
for off in range(0, len(data) - 3, 2):
    from_va = BASE_VA + off
    hw1 = data[off] | (data[off + 1] << 8)
    hw2 = data[off + 2] | (data[off + 3] << 8)
    # BL (Thumb-2)
    if (hw1 & 0xF800) == 0xF000 and (hw2 & 0xF800) == 0xF800:
        s = (hw1 >> 10) & 1
        imm10 = hw1 & 0x3FF
        imm11 = hw2 & 0x7FF
        imm24 = (s << 23) | (imm10 << 13) | imm11
        if imm24 & 0x800000:
            imm24 |= ~0xFFFFFF
        target = from_va + 4 + (imm24 << 1)
        if target == TARGET:
            xrefs.append(from_va)
    # BLX immediate
    elif (hw1 & 0xF800) == 0xF000 and (hw2 & 0xF800) == 0xF800:
        s = (hw1 >> 10) & 1
        imm10 = hw1 & 0x3FF
        imm11 = hw2 & 0x7FF
        h = (imm10 >> 9) & 1
        j1 = (imm11 >> 12) & 1
        j2 = (imm11 >> 11) & 1
        i1 = (imm11 >> 10) & 1
        i2 = imm11 & 0x3FF
        imm32 = (s << 24) | (h << 23) | ((~j1 & 1) << 22) | ((~j2 & 1) << 21) | (imm10 << 12) | (i1 << 11) | i2
        if imm32 & 0x800000:
            imm32 |= ~0xFFFFFFFF
        target = from_va + 4 + imm32
        if target == TARGET:
            xrefs.append(from_va)
print(f"Xrefs directos a 0x90b248: {len(xrefs)}")
for x in xrefs[:30]:
    print(f"  0x{x:08x}")

# --- 3. Entradas .plt de osal_* y sus llamadores ---
print("\n" + "=" * 70)
print("Entradas .plt de osal_* (registro/recibo/envío de colas)")
print("=" * 70)

# Reconstruir plt_map (orden de .rel.plt)
e_shoff = struct.unpack_from("<I", data, 0x20)[0]
e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
e_shnum = struct.unpack_from("<H", data, 0x30)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x32)[0]
sec_list = []
for i in range(e_shnum):
    off = e_shoff + i * e_shentsize
    st_name, stype, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from("<IIIIIIIIII", data, off)
    sec_list.append({"idx": i, "st_name": st_name, "type": stype, "flags": flags, "addr": addr,
                     "off": offset, "size": size, "link": link, "info": info, "align": align, "entsize": entsize})
shstr_off = sec_list[e_shstrndx]["off"]
def sname(idx):
    s = sec_list[idx]
    end = data.index(b"\x00", shstr_off + s["st_name"])
    return data[shstr_off + s["st_name"]:end].decode()
for i in range(e_shnum):
    sec_list[i]["name"] = sname(i)
secs = {s["name"]: s for s in sec_list}

dynstr = data[secs[".dynstr"]["off"]: secs[".dynstr"]["off"] + secs[".dynstr"]["size"]]
def cstr(off):
    end = dynstr.index(b"\x00", off)
    return dynstr[off:end].decode("utf-8", "replace")
ds = secs[".dynsym"]; nd = ds["size"] // 16
symbols = []
for k in range(nd):
    o = ds["off"] + k * 16
    st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack_from("<IIIBBH", data, o)
    symbols.append({"idx": k, "name": cstr(st_name)})

rplt = secs[".rel.plt"]; nrel = rplt["size"] // 8
plt_base = secs[".plt"]["addr"]; plt_size = secs[".plt"]["size"]; nplt = plt_size // 16
plt_map = {}
for k in range(min(nrel, nplt)):
    o = rplt["off"] + k * 8
    r_offset, r_info = struct.unpack_from("<II", data, o)
    sym_idx = r_info >> 8
    nom = symbols[sym_idx]["name"] if sym_idx < len(symbols) else f"<sym{sym_idx}>"
    plt_map[plt_base + k * 16] = nom

osal_plt = {va: nom for va, nom in plt_map.items() if "osal_" in nom}
print(f"Entradas .plt con 'osal_': {len(osal_plt)}")
for va, nom in sorted(osal_plt.items()):
    print(f"  0x{va:08x} -> {nom}")

# Buscar llamadores de cada entrada osal_ plt
print("\n=== Llamadores (BL/BLX) a cada entrada .plt osal_* ===")
for plt_va, nom in sorted(osal_plt.items()):
    callers = []
    for off in range(0, len(data) - 3, 2):
        from_va = off
        hw1 = data[off] | (data[off + 1] << 8)
        hw2 = data[off + 2] | (data[off + 3] << 8)
        if (hw1 & 0xF800) == 0xF000 and (hw2 & 0xF800) == 0xF800:
            s = (hw1 >> 10) & 1
            imm10 = hw1 & 0x3FF
            imm11 = hw2 & 0x7FF
            imm24 = (s << 23) | (imm10 << 13) | imm11
            if imm24 & 0x800000:
                imm24 |= ~0xFFFFFF
            target = from_va + 4 + (imm24 << 1)
            if target == plt_va:
                callers.append(from_va)
    if callers:
        print(f"  .plt 0x{plt_va:08x} ({nom}): {len(callers)} llamadores")
        for c in callers[:10]:
            print(f"    0x{c:08x}")
