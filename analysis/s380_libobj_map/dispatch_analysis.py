"""S380/S381: RecordStill::Execute cuerpo + xrefs; .plt osal_* y sus llamadores."""
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs, CsError
from elf_plt import resolve_plt

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "scripts"))
from elf_thumb_callers import callers as thumb_callers

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
        except CsError:
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
xrefs = [address for address, _ in thumb_callers(data, {TARGET})]
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
got_map = {}
for k in range(nrel):
    r_offset, r_info = struct.unpack_from("<II", data, rplt["off"] + k * 8)
    got_map[r_offset] = symbols[r_info >> 8]["name"]
plt = secs[".plt"]
plt_map = resolve_plt(data, plt["addr"], plt["off"], plt["size"], got_map)

osal_plt = {va: nom for va, nom in plt_map.items() if "osal_" in nom}
print(f"Entradas .plt con 'osal_': {len(osal_plt)}")
for va, nom in sorted(osal_plt.items()):
    print(f"  0x{va:08x} -> {nom}")

# Buscar llamadores de cada entrada osal_ plt
print("\n=== Llamadores (BL/BLX) a cada entrada .plt osal_* ===")
call_sites = {}
for address, target in thumb_callers(data, set(osal_plt)):
    call_sites.setdefault(target, []).append(address)
for plt_va, nom in sorted(osal_plt.items()):
    callers = call_sites.get(plt_va, [])
    if callers:
        print(f"  .plt 0x{plt_va:08x} ({nom}): {len(callers)} llamadores")
        for c in callers[:10]:
            print(f"    0x{c:08x}")
