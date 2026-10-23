#!/usr/bin/env python3
"""S381b: buscar llamadas indirectas (bx/blx rX) tras carga desde GOT, y rastrear RecordStill::Execute."""
import struct, json
from pathlib import Path
from capstone import *
from collections import Counter

BASE = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter")
PATH = BASE / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
data = PATH.read_bytes()

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

# --- desensamblar todo .text una vez, guardar instrucciones ---
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True
text_va = secs[".text"]["addr"]
text_end = text_va + secs[".text"]["size"]

insns = []  # (va, mnemonic, op_str, size, bytes_hex)
i = text_va
while i < text_end:
    try:
        inslist = list(md.disasm(data[i:text_va + len(data) - i if False else i - text_va + 0:i - text_va + 4], i))
        if inslist:
            ins = inslist[0]
            insns.append((ins.address, ins.mnemonic, ins.op_str, ins.size, data[ins.address-text_va:ins.address-text_va+ins.size].hex()))
            i = ins.address + ins.size
        else:
            i += 2
    except Exception:
        i += 2

# índice por VA
ins_by_va = {v: (m, o, s, b) for v, m, o, s, b in insns}

# --- buscar bx rX / blx rX y rastrear 6 instrucciones atrás para ldr desde GOT ---
def reg_of(op):
    """devuelve el registro de 'bx rN' o 'blx rN'"""
    parts = op.strip().split()
    if parts and parts[0] in ("bx", "blx") and len(parts) > 1:
        r = parts[1]
        if r.startswith("r") and r[1:].isdigit():
            return int(r[1:])
    return None

indirect_calls = []
for va, mnem, op, size, _ in insns:
    reg = reg_of(op)
    if reg is None:
        continue
    # mirar hasta 8 instrucciones atrás
    start = va - 8 * 4
    for j in range(len(insns) - 1, -1, -1):
        p_va, p_mnem, p_op, p_size, _ = insns[j]
        if p_va >= va:
            continue
        if p_va < start:
            break
        # buscar ldr que use este registro y [pc]
        if p_mnem == "ldr" and f"r{reg}," in p_op and "[pc" in p_op:
            # calcular literal pool address
            # ldr literal: imm12 en operando
            # intentar leer el literal
            try:
                hw1 = data[p_va - text_va] | (data[p_va - text_va + 1] << 8)
                hw2 = data[p_va - text_va + 2] | (data[p_va - text_va + 3] << 8)
                # ldr literal encoding: 1111 100x 1 imm12 1111 Rt
                # imm12 = bits: [8:11] de hw1 (3 bits) + [0:7] de hw2 (8 bits) -> 11 bits? No, es 12 bits
                # Thumb-2 ldr literal: imm12 se distribuye: imm12[11:8] en hw1[3:0], imm12[7:0] en hw2[7:0]
                # Pero hay un bit P, U, W... para ldr literal P=1, U=1, W=0
                # encoding: 1 1 1 1 1 0 0 P U 0 W imm12 1 1 1 1 Rt
                # hw1 bits: 15:13=111, 12:10=100, 9=P, 8=U, 7=0(W), 6:2=imm12[11:7]?? 
                # Esto es demasiado complejo. En su lugar, usar capstone para obtener el imm.
                pass
            except Exception:
                pass
            # salto: leer el literal pool directamente asumiendo que está alineado
            # El literal pool está en (pc_aligned + imm12). Necesitamos imm12.
            # Usamos operando de capstone: buscar '#' en p_op
            # p_op como "r0, [pc, #0xXXX]"
            import re
            m = re.search(r'#0x([0-9a-fA-F]+)', p_op)
            if m:
                imm12 = int(m.group(1), 16)
                lit_addr = (p_va + 4) & ~0x3  # alineado abajo a 4
                # pero imm12 es relativo a pc+4 (aligned)
                lit_addr = (p_va + 4) + imm12
                if lit_addr >= text_va and lit_addr < text_va + len(data):
                    lit_val = int.from_bytes(data[lit_addr - text_va:lit_addr - text_va + 4], "little")
                    if lit_val in got_func:
                        indirect_calls.append((va, lit_val, got_func[lit_val], reg))
                        break
            # tambien probar sin alineacion (literal directo)
            lit_addr = (p_va + 4) + imm12 if 'm' in dir() else 0

print(f"Llamadas indirectas (bx/blx tras ldr GOT): {len(indirect_calls)}")
by_name = Counter(c[2] for c in indirect_calls)
for nom, cnt in by_name.most_common(40):
    print(f"  {nom}: {cnt}")

print("\nLlamadas indirectas a osal_*:")
for caller, got, nom, reg in indirect_calls:
    if "osal_" in nom:
        print(f"  caller=0x{caller:08x} GOT=0x{got:08x} -> {nom} via r{reg}")

Path("analysis/s380_libobj_map/indirect_calls_b.json").write_text(json.dumps([
    {"caller": hex(c), "got": hex(g), "name": n, "reg": r} for c, g, n, r in indirect_calls
], indent=1))

# --- 2. Buscar xrefs a RecordStill::Execute (0x90b248) via puntero de funcion ---
# Buscar literales 0x0090b248 en .rodata, .data, .data.rel.ro, .got
import struct as st
target = 0x0090b248
pat = st.pack("<I", target)
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
    print(f"\nLiteral 0x90b248 en {secname}: {len(offs)} sitios")
    for o in offs[:20]:
        print(f"  off 0x{o:06x} (VA 0x{o+s['addr']:08x})")

print("\n=== FIN ===")
