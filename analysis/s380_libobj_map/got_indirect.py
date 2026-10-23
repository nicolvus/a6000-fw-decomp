#!/usr/bin/env python3
"""S381: mapear slots del GOT a nombres de import (.rel.plt) y buscar llamadas indirectas (ldr GOT + bx/blx)."""
import struct, json
from pathlib import Path
from capstone import *

BASE = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter")
PATH = BASE / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
data = PATH.read_bytes()

# --- Leer secciones ---
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

# --- Leer .dynsym ---
dynstr = data[secs[".dynstr"]["off"]: secs[".dynstr"]["off"] + secs[".dynstr"]["size"]]
def cstr(off):
    end = dynstr.index(b"\x00", off)
    return dynstr[off:end].decode("utf-8", "replace")
ds = secs[".dynsym"]; nd = ds["size"] // 16
symbols = []
for k in range(nd):
    o = ds["off"] + k * 16
    st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack_from("<IIIBBH", data, o)
    symbols.append({"idx": k, "name": cstr(st_name), "value": st_value, "shndx": st_shndx})

# --- .rel.plt: slot GOT (r_offset) -> nombre de funcion importada ---
rplt = secs[".rel.plt"]; nrel = rplt["size"] // 8
got_to_name = {}
for k in range(nrel):
    o = rplt["off"] + k * 8
    r_offset, r_info = struct.unpack_from("<II", data, o)
    sym_idx = r_info >> 8
    if sym_idx < len(symbols):
        got_to_name[r_offset] = symbols[sym_idx]["name"]

# Slots del GOT en rango .got (0x0102cbd0 - 0x01035320)
got_base = secs[".got"]["addr"]; got_size = secs[".got"]["size"]
got_slots_in_range = {off: nom for off, nom in got_to_name.items() if got_base <= off < got_base + got_size}
print(f".rel.plt entradas={nrel}, slots GOT mapeados en rango .got: {len(got_slots_in_range)}")

# --- Guardar mapeo ---
out_got = {hex(k): v for k, v in got_slots_in_range.items()}
Path("analysis/s380_libobj_map/got_to_name.json").write_text(json.dumps(out_got, indent=1))

# --- Buscar llamadas indirectas: ldr rX,[pc,#imm] + add rX,pc + ldr rX,[rX,#imm] + bx/blx rX ---
# Patrón: ldr desde literal pool que apunta al GOT, luego bx/blx
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True

# Primero: recolectar todos los slots del GOT que son importaciones de funciones
got_func_slots = set(got_slots_in_range.keys())

# Buscar instrucciones ldr rX,[pc,#imm] donde el target sea un slot del GOT
# ldr (literal): 11111001 01 imm12 1111 Rt -> 0xF8DF 0xF000|imm12... 
# Encoding Thumb-2 ldr literal: 1111 1000 1 0 imm12 1111 Rt = 0xF8 0xDF hi, 0xF0|Rt lo ... 
# Formato: 0xF8DF0000 | (imm12 << ?)... mejor usar capstone para detectar 'ldr' con 'pc' en op_str y ']'

indirect_calls = []  # (caller_va, got_slot, target_name)
a = secs[".text"]["addr"]
text_end = a + secs[".text"]["size"]
i = a
while i < text_end:
    try:
        insns = list(md.disasm(data[i:i+4], i))
        if not insns:
            i += 2; continue
        insn = insns[0]
        mnem = insn.mnemonic; op = insn.op_str
        # ldr rX,[pc,#imm] -> luego add rX,pc (PIC) -> ldr rX,[rX,#imm] -> bx/blx rX
        # Patrón simple: ldr ... [pc ...] donde el valor cargado (literal) sea un slot GOT
        if mnem == "ldr" and "pc" in op and "]" in op:
            # calcular dirección del literal pool
            # ldr literal Thumb-2: imm12 en el opcode
            hw1 = data[i] | (data[i+1] << 8)
            hw2 = data[i+2] | (data[i+3] << 8)
            if (hw1 & 0xF800) == 0xF800 and (hw1 & 0x0800) == 0x0800:  # ldr literal
                imm12 = ((hw1 & 0x0700) >> 4) | (hw2 & 0xFF)  # aproximado
                lit_addr = (i + 4) & ~0x2  # alineado a 4
                # leer el literal
                lit_val = int.from_bytes(data[lit_addr:lit_addr+4], "little")
                if lit_val in got_func_slots:
                    # buscar bx/blx al registro en las próximas instrucciones
                    for j in range(i+4, min(i+40, text_end), 2):
                        try:
                            ins2s = list(md.disasm(data[j:j+4], j))
                            if ins2s:
                                ins2 = ins2s[0]
                                if ins2.mnemonic in ("bx", "blx") and ins2.op_str.strip().startswith("r"):
                                    reg = ins2.op_str.strip()[1:]
                                    indirect_calls.append((i, lit_val, got_slots_in_range[lit_val], reg))
                                    break
                        except Exception:
                            pass
        i = insn.address + insn.size
    except Exception:
        i += 2

print(f"\nLlamadas indirectas (ldr literal->GOT+bx/blx) encontradas: {len(indirect_calls)}")
# Agrupar por nombre de función
from collections import Counter
by_name = Counter(c[2] for c in indirect_calls)
print("Por función importada:")
for nom, cnt in by_name.most_common(40):
    print(f"  {nom}: {cnt} llamadas")

# Llamadas a osal_* específicamente
print("\nLlamadas indirectas a osal_*:")
osal_calls = [c for c in indirect_calls if "osal_" in c[2]]
for caller, got, nom, reg in osal_calls:
    print(f"  caller=0x{caller:08x} GOT=0x{got:08x} -> {nom} via {reg}")

Path("analysis/s380_libobj_map/indirect_calls.json").write_text(json.dumps([
    {"caller": hex(c), "got": hex(g), "name": n, "reg": r} for c, g, n, r in indirect_calls
], indent=1))
print("\nGuardado indirect_calls.json y got_to_name.json")
