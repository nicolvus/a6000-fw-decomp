#!/usr/bin/env python3
"""Mapa de libObj.so (A6000 fw3.21): secciones, imports, exports, .plt->nombre."""
import struct, sys, json
from pathlib import Path

PATH = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/"
            "firmware/extracted/fw321/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
data = PATH.read_bytes()

assert data[:4] == b"\x7fELF"
e_shoff = struct.unpack_from("<I", data, 0x20)[0]
e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
e_shnum = struct.unpack_from("<H", data, 0x30)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x32)[0]

sec_list = []
secs_by_name = {}
for i in range(e_shnum):
    off = e_shoff + i * e_shentsize
    st_name, stype, flags, addr, offset, size, link, info, align, entsize = struct.unpack_from("<IIIIIIIIII", data, off)
    entry = {"idx": i, "st_name": st_name, "type": stype, "flags": flags, "addr": addr,
             "off": offset, "size": size, "link": link, "info": info, "align": align, "entsize": entsize}
    sec_list.append(entry)

# nombre de la sección por índice (leer del shstrtab, sección e_shstrndx)
shstr_off = sec_list[e_shstrndx]["off"]
def secname(idx):
    s = sec_list[idx]
    end = data.index(b"\x00", shstr_off + s["st_name"])
    return data[shstr_off + s["st_name"]:end].decode()

for i in range(e_shnum):
    sec_list[i]["name"] = secname(i)
    secs_by_name[sec_list[i]["name"]] = sec_list[i]

print("=== SECCIONES ===")
for i in range(e_shnum):
    s = sec_list[i]
    print(f"[{i:2d}] {s['name']:<20} type={s['type']} addr=0x{s['addr']:08x} off=0x{s['off']:06x} "
          f"size=0x{s['size']:06x} flags=0x{s['flags']:04x} link={s['link']} entsize={s['entsize']}")

# .dynstr
dynstr_off = secs_by_name[".dynstr"]["off"]
dynstr = data[dynstr_off: dynstr_off + secs_by_name[".dynstr"]["size"]]
def cstr(off):
    end = dynstr.index(b"\x00", off)
    return dynstr[off:end].decode("utf-8", "replace")

# .dynsym
ds_off = secs_by_name[".dynsym"]["off"]; ds_size = secs_by_name[".dynsym"]["size"]; ds_entsize = secs_by_name[".dynsym"]["entsize"]
ndsym = ds_size // ds_entsize
symbols = []
for k in range(ndsym):
    o = ds_off + k * ds_entsize
    st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack_from("<IIIBBH", data, o)
    bind = st_info >> 4; typ = st_info & 0xF
    name = cstr(st_name) if st_name < len(dynstr) else f"<bad:{st_name}>"
    symbols.append({"idx": k, "name": name, "value": st_value, "size": st_size,
                    "bind": bind, "type": typ, "shndx": st_shndx})

und = [s for s in symbols if s["shndx"] == 0]
defined = [s for s in symbols if s["shndx"] != 0]
funcs_und = [s for s in und if s["type"] == 2]   # STT_FUNC
objs_und = [s for s in und if s["type"] == 1]     # STT_OBJECT
funcs_def = [s for s in defined if s["type"] == 2]

print(f"\n=== SIMBOLOS .dynsym: total={ndsym} UND={len(und)} (func={len(funcs_und)}, obj={len(objs_und)}) "
      f"DEFINED={len(defined)} (func={len(funcs_def)})")

print("\n=== IMPORTS FUNC (UND, STT_FUNC) — primeros 60 ===")
for s in funcs_und[:60]:
    print(f"  UND FUNC {s['name']}")

print("\n=== EXPORTS FUNC (defined, STT_FUNC) — primeros 60 ===")
for s in funcs_def[:60]:
    print(f"  DEF FUNC 0x{s['value']:08x} size={s['size']} {s['name']}")

# .rel.plt -> mapear PLT offset a nombre
rplt_off = secs_by_name[".rel.plt"]["off"]; rplt_size = secs_by_name[".rel.plt"]["size"]; rplt_entsize = secs_by_name[".rel.plt"]["entsize"]
nrel = rplt_size // rplt_entsize
plt_map = {}   # va (plt slot) -> nombre sym
for k in range(nrel):
    o = rplt_off + k * rplt_entsize
    r_offset, r_info = struct.unpack_from("<II", data, o)
    sym_idx = r_info >> 8
    if sym_idx < len(symbols):
        plt_map[r_offset] = symbols[sym_idx]["name"]

print(f"\n=== .rel.plt: {nrel} entradas ===")
plt_base = secs_by_name[".plt"]["addr"]   # .plt addr = 0x0db3c4
plt_size = secs_by_name[".plt"]["size"]
# Cada entrada de .plt mide 16 B (Thumb-2 stub). r_offset apunta al GOT slot o a la entrada .plt.
# Listamos direcciones .plt con nombre resuelto.
resolved = 0
for k in range(plt_size // 16):
    va = plt_base + k * 16
    nom = plt_map.get(va)
    if nom:
        resolved += 1
print(f"Entradas .plt resueltas por .rel.plt (r_offset==va del .plt): {resolved} / {plt_size//16}")

# Guardar JSON
out = {
    "sections": {secname(i): sec_list[i] for i in range(e_shnum)},
    "n_dynsym": ndsym,
    "n_und_func": len(funcs_und),
    "n_und_obj": len(objs_und),
    "n_defined_func": len(funcs_def),
    "n_rel_plt": nrel,
    "plt_base": plt_base,
    "plt_size": plt_size,
    "imports_func": [{"name": s["name"]} for s in funcs_und],
    "exports_func": [{"name": s["name"], "value": s["value"], "size": s["size"]} for s in funcs_def],
    "plt_map": {hex(k): v for k, v in plt_map.items()},
}
Path("analysis/s380_libobj_map/map.json").write_text(json.dumps(out, indent=1))
print("\nGuardado analysis/s380_libobj_map/map.json")
