#!/usr/bin/env python3
"""S382 completo: encontrar funciones contenedoras de 0x90de2e y 0x91634e,
quién las llama, y qué hacen."""
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
insns = []
i = text_va
while i < text_end:
    try:
        inslist = list(md.disasm(data[i:i+4], i))
        if inslist:
            ins = inslist[0]
            insns.append((ins.address, ins.mnemonic, ins.op_str, ins.size))
            i = ins.address + ins.size
        else:
            i += 2
    except Exception:
        i += 2
ins_by_va = {v: (m, o, s) for v, m, o, s in insns}

THUMB_PROLOGUES = [b"\x2d\xe9", b"\xb0\xf0", b"\xb0\xf8", b"\x4f\xf0", b"\x46\xaf"]
ARM_PROLOGUES = [b"\xe9\x2d", b"\xe5\x2d", b"\xe1\x2d"]

def is_prologue(va):
    if va & 1:
        b2 = data[va:va+2]; b4 = data[va:va+4]
        for p in THUMB_PROLOGUES:
            if b4.startswith(p) or b2.startswith(p):
                return True, va, "thumb"
    va_a = va & ~1
    b4 = data[va_a:va_a+4]
    for p in ARM_PROLOGUES:
        if b4.startswith(p):
            return True, va_a, "arm"
    return False, None, None

def find_function_start(addr):
    best = None
    start_scan = max(text_va, addr - 0x5000)
    v = start_scan
    while v <= addr:
        is_p, pva, mode = is_prologue(v)
        if is_p:
            best = (pva, mode)
        v += 2
    return best

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
        return "BL", va + 4 + (imm24 << 1)
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
        return "BLX", va + 4 + imm32
    return None

# --- Encontrar inicios de función para los candidatos ---
CANDIDATES = [0x90de2e, 0x91634e]
print("=== S382: Funciones contenedoras ===\n")
container_funcs = {}
for cand in CANDIDATES:
    start = find_function_start(cand)
    if start:
        pva, mode = start
        container_funcs[cand] = (pva, mode)
        print(f"0x{cand:08x}: dentro de función 0x{pva:08x} ({mode})")
    else:
        print(f"0x{cand:08x}: NO se encontró prólogo (hasta -0x5000)")
print()

# --- Quién llama a las funciones contenedoras ---
print("=== Quién llama a las funciones contenedoras ===\n")
for cand, (pva, mode) in container_funcs.items():
    callers = []
    # Buscar BL/BLX a pva (Thumb: pva|1, ARM: pva)
    targets = [pva]
    if mode == "thumb":
        targets.append(pva | 1)
    for off in range(0, len(data) - 3, 2):
        res = decode_bl_blx(off)
        if res and res[1] in targets:
            callers.append((off, res[0], res[1]))
    print(f"Llamadores a 0x{pva:08x} ({mode}): {len(callers)}")
    for va, mnem, tgt in callers[:20]:
        cs, cstart, cmode = find_function_start(va)
        cfn = f"0x{cstart:08x} ({cmode})" if cstart else "desconocida"
        print(f"  {mnem} en 0x{va:08x} -> 0x{tgt:08x} (función: {cfn})")
    print()

# --- Cuerpo completo de las funciones contenedoras ---
print("=== Cuerpo de funciones contenedoras ===\n")
for cand, (pva, mode) in container_funcs.items():
    print(f"--- Función 0x{pva:08x} ({mode}) [contiene 0x{cand:08x}] ---")
    i = pva
    count = 0
    end = min(pva + 400, text_end)
    while i < end and count < 80:
        if i in ins_by_va:
            m, o, s = ins_by_va[i]
            marker = f"  <-- 0x{cand:08x}" if i == cand else ""
            print(f"    0x{i:08x}: {m:<10} {o}{marker}")
            i += s
            count += 1
        else:
            i += 2
    print()
