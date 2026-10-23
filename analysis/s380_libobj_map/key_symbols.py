"""Resuelve imports/exports y enlaza las instrucciones PLT con relocaciones GOT."""
import json
import struct
from pathlib import Path

from elf_plt import resolve_plt

BASE = Path("/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter")
PATH = BASE / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
data = PATH.read_bytes()

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
    bind = st_info >> 4; typ = st_info & 0xF
    symbols.append({"idx": k, "name": cstr(st_name), "value": st_value, "size": st_size,
                    "bind": bind, "type": typ, "shndx": st_shndx})

und_func = [s for s in symbols if s["shndx"] == 0 and s["type"] == 2]
def_func = [s for s in symbols if s["shndx"] != 0 and s["type"] == 2]

KEYS = ["SendAndRecv", "queueMsg", "RcvMsg", "msg_queue_cb", "queue_cb", "PinSend",
        "PinYc", "PinEPN", "osal_rcv", "osal_snd", "osal_reg", "ObjMsg", "RecordStill",
        "GetFileImage", "Still", "MprIf", "DataflowInfra", "Sender", "INFRA", "ENQUEUE",
        "DEQUEUE", "GetMsgNum", "SendCmd", "SendId", "SendEvent"]
print("=== IMPORTS que contienen claves ===")
for s in und_func:
    n = s["name"]
    if any(k in n for k in KEYS):
        print(f"  UND  {n}")

print("\n=== EXPORTS que contienen claves ===")
for s in def_func:
    n = s["name"]
    if any(k in n for k in KEYS):
        print(f"  DEF  0x{s['value']:08x} size={s['size']:5d}  {n}")

# .rel.plt -> .plt por orden de entrada
rplt = secs[".rel.plt"]
nrel = rplt["size"] // 8
plt_base = secs[".plt"]["addr"]; plt_size = secs[".plt"]["size"]
got_map = {}
for k in range(nrel):
    r_offset, r_info = struct.unpack_from("<II", data, rplt["off"] + k * 8)
    got_map[r_offset] = symbols[r_info >> 8]["name"]
plt_map = resolve_plt(data, plt_base, secs[".plt"]["off"], plt_size, got_map)
print(f"Relocaciones GOT={nrel}; entradas PLT ARM/Thumb={len(plt_map)}")

# Ver funciones clave en .plt
print("\n=== Entradas .plt para funciones clave ===")
for va, nom in plt_map.items():
    if any(k in nom for k in ["SendAndRecv", "queueMsg", "RcvMsg", "queue_cb", "msg_queue_cb", "PinSend", "PinYc", "PinEPN", "ObjMsg"]):
        print(f"  0x{va:08x} -> {nom}")

out = {
    "n_imports_func": len(und_func),
    "n_exports_func": len(def_func),
    "imports_key": [s["name"] for s in und_func if any(k in s["name"] for k in KEYS)],
    "exports_key": [{"name": s["name"], "value": s["value"], "size": s["size"]}
                    for s in def_func if any(k in s["name"] for k in KEYS)],
    "plt_map_count": len(plt_map),
    "plt_map": {hex(k): v for k, v in plt_map.items()},
}
Path("analysis/s380_libobj_map/key_symbols.json").write_text(json.dumps(out, indent=1))
print("\nGuardado key_symbols.json")
