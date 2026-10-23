#!/usr/bin/env python3
"""S381c: llamadas indirectas (bx/blx rN tras ldr rN,[pc) y xrefs a RecordStill::Execute."""
import struct, json, re
from pathlib import Path
from capstone import *
from collections import Counter

BASE = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter")
PATH = BASE / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
data = PATH.read_bytes()
TVA = 0  # PIE: file offset == VA for LOAD segment 0

# --- secciones ---
e_shoff = struct.unpack_from("<I", data, 0x20)[0]
e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
e_shnum = struct.unpack_from("<H", data, 0x30)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x32)[0]
sec_list = []
for i in range(e_shnum):
    off = e_shoff + i * e_shentsize
    st_name, stype, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from("<IIIIIIIIII", data, off)
    sec_list.append({"idx": i, "st_name": st_name, "type": stype, "flags": flags, "addr": addr,
                     "off": offset, "size": size})
shstr_off = sec_list[e_shstrndx]["off"]
def sname(idx):
    s = sec_list[idx]
    end = data.index(b"\x00", shstr_off + s["st_name"])
    return data[shstr_off + s["st_name"]:end].decode()
for i in range(e_shnum):
    sec_list[i]["name"] = sname(i)
secs = {s["name"]: s for s in sec_list}

# --- .dynsym + .rel.plt para GOT->nombre ---
dynstr = data[secs[".dynstr"]["off"]: secs[".dynstr"]["off"] + secs[".dynstr"]["size"]]
def cstr(off):
    end = dynstr.index(b"\x00", off)
    return dynstr[off:end].decode("utf-8", "replace")
ds = secs[".dynsym"]; nd = ds["size"] // 16
symbols = []
for k in range(nd):
    o = ds["off"] + k * 16
    st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack_from("<IIIBBH", data, o)
    symbols.append({"idx": k, "name": cstr(st_name), "value": st_value})
rplt = secs[".rel.plt"]; nrel = rplt["size"] // 8
got_to_name = {}
for k in range(nrel):
    o = rplt["off"] + k * 8
    r_offset, r_info = struct.unpack_from("<II", data, o)
    sym_idx = r_info >> 8
    if sym_idx < len(symbols):
        got_to_name[r_offset] = symbols[sym_idx]["name"]
got_base = secs[".got"]["addr"]; got_size = secs[".got"]["size"]
got_func = {off: nom for off, nom in got_to_name.items() if got_base <= off < got_base + got_size}

# --- desensamblar .text ---
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

print(f"Total instrucciones .text: {len(insns)}")

# REGISTER alias map
REG_ALIASES = {"r0":0,"r1":1,"r2":2,"r3":3,"r4":4,"r5":5,"r6":6,"r7":7,"r8":8,"r9":9,"r10":10,"r11":11,"ip":12,"r12":12,"sp":13,"r13":13,"lr":14,"r14":14,"pc":15,"r15":15}
def reg_of(mnem, op):
    if mnem in ("bx", "blx"):
        op = op.strip()
        return REG_ALIASES.get(op)
    return None

indirect_calls = []
n_bxreg = 0
for idx, (va, mnem, op, size) in enumerate(insns):
    reg = reg_of(mnem, op)
    if reg is None:
        continue
    n_bxreg += 1
    # buscar hasta 16 instrucciones atrás un ldr rN,[pc con el mismo registro
    regname = f"r{reg}" if reg <= 11 else ("ip" if reg == 12 else ("sp" if reg == 13 else ("lr" if reg == 14 else "pc")))
    for j in range(idx - 1, max(0, idx - 16), -1):
        p_va, p_mnem, p_op, p_size = insns[j]
        if p_va >= va:
            continue
        if p_va < va - 64:  # solo 64 bytes atrás
            break
        if p_mnem == "ldr" and f"{regname}," in p_op and "[pc" in p_op:
            # obtener imm12 del operando
            mm = re.search(r'#0x([0-9a-fA-F]+)', p_op)
            if mm:
                imm12 = int(mm.group(1), 16)
                lit_addr = (p_va + 4) & ~3 + imm12
                if 0 <= lit_addr - text_va < len(data) - (lit_addr - text_va):
                    lit_val = int.from_bytes(data[lit_addr:lit_addr+4], "little")
                    if lit_val in got_func:
                        indirect_calls.append((p_va, va, lit_val, got_func[lit_val], regname))
                        break

print(f"Instrucciones bx/blx registro: {n_bxreg}")
print(f"Llamadas indirectas confirmadas (ldr GOT + bx/blx): {len(indirect_calls)}")
by_name = Counter(c[3] for c in indirect_calls)
for nom, cnt in by_name.most_common(40):
    print(f"  {nom}: {cnt}")

print("\nLlamadas indirectas a osal_*:")
for caller, target, got, nom, reg in indirect_calls:
    if "osal_" in nom:
        print(f"  0x{caller:08x} -> 0x{target:08x} GOT=0x{got:08x} {nom} via {reg}")

Path("analysis/s380_libobj_map/indirect_calls_c.json").write_text(json.dumps([
    {"caller": hex(c), "target": hex(t), "got": hex(g), "name": n, "reg": r} for c, t, g, n, r in indirect_calls
], indent=1))

# --- xrefs a RecordStill::Execute (0x90b248) ---
print("\n--- Xrefs a RecordStill::Execute 0x90b248 ---")
TARGET = 0x90b248
# literal en .rodata/.data/.data.rel.ro/.got
import struct as st
pat = st.pack("<I", TARGET)
for secname in [".rodata", ".data", ".data.rel.ro", ".got"]:
    s = secs[secname]
    offs = []
    pos = 0
    while True:
        pos = data.find(pat, s["off"] + pos, s["off"] + s["size"])
        if pos < 0:
            break
        offs.append(pos - s["off"])
        pos += 1
    print(f"Literal 0x90b248 en {secname}: {len(offs)} sitios")
    for o in offs[:10]:
        print(f"   off 0x{o:06x} (VA 0x{o+s['addr']:08x})")

print("\nGuardado indirect_calls_c.json")
