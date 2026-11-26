"""Análisis ELF independiente de libmpr 3.97 frente al de fábrica (3.21/3.94, mismo sha256)."""
import hashlib
import json
import struct
import sys
from pathlib import Path

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

W = Path("build/aud397/work")
NEW = W / "libmpr-397.so"
OLD = W / "libmpr-321.so"
HOOK = 0x7126E6
CAVE = 0x93B000
s = lambda b: hashlib.sha256(b).hexdigest()

nb, ob = NEW.read_bytes(), OLD.read_bytes()
print("sha256 nuevo", s(nb))
print("sha256 fabrica", s(ob))
print("tamano", len(nb), len(ob), "iguales", nb == ob)


def elf(buf):
    import io
    return ELFFile(io.BytesIO(buf))


en, eo = elf(nb), elf(ob)

# --- cabecera
print("\n== ELF header ==")
for k in ("e_ident", "e_type", "e_machine", "e_version", "e_entry", "e_phoff", "e_shoff",
          "e_flags", "e_ehsize", "e_phentsize", "e_phnum", "e_shentsize", "e_shnum", "e_shstrndx"):
    vn, vo = getattr(en.header, k), getattr(eo.header, k)
    print(f"{k:12} {vn!r} == {vo!r} -> {vn == vo}")

# --- program headers
print("\n== Program headers ==")
pn = [(p["p_type"], p["p_offset"], p["p_vaddr"], p["p_paddr"], p["p_filesz"], p["p_memsz"], p["p_flags"], p["p_align"]) for p in en.iter_segments()]
po = [(p["p_type"], p["p_offset"], p["p_vaddr"], p["p_paddr"], p["p_filesz"], p["p_memsz"], p["p_flags"], p["p_align"]) for p in eo.iter_segments()]
for x, y in zip(pn, po):
    print(x, "==", y, "->", x == y)
print("num_ph", len(pn), len(po))

# --- secciones
print("\n== Secciones ==")
sn = [(x.name, x["sh_type"], x["sh_addr"], x["sh_offset"], x["sh_size"], x["sh_flags"], x["sh_addralign"], x["sh_entsize"]) for x in en.iter_sections()]
so = [(x.name, x["sh_type"], x["sh_addr"], x["sh_offset"], x["sh_size"], x["sh_flags"], x["sh_addralign"], x["sh_entsize"]) for x in eo.iter_sections()]
print("num_sh", len(sn), len(so), "metadatos_iguales", sn == so)
if sn != so:
    for x, y in zip(sn, so):
        if x != y:
            print("DIFIERE", x, y)
for x in en.iter_sections():
    print(f"[{x.name:16}] addr 0x{x['sh_addr']:08x} off 0x{x['sh_offset']:08x} size 0x{x['sh_size']:08x} flags 0x{x['sh_flags']:x}", end="")
    print("   <-- contiene 0x93B000" if x["sh_addr"] <= CAVE < x["sh_addr"] + x["sh_size"] and x["sh_type"] != "SHT_NOBITS" else "")

# --- bytes del gancho
print("\n== Gancho ==")
off_hook = HOOK  # primer PT_LOAD: vaddr == offset
print("0x%X fabrica:" % HOOK, ob[off_hook:off_hook + 8].hex(" "))
print("0x%X nuevo  :" % HOOK, nb[off_hook:off_hook + 8].hex(" "))
print("0x7126EA intacto:", nb[HOOK + 4:HOOK + 8] == ob[HOOK + 4:HOOK + 8])

# --- cueva
print("\n== Cueva ==")
seed = ob[CAVE:CAVE + 0x60]
print("fabrica 0x93B000..0x93B060:", seed.hex(" "))
print("fabrica todo cero hasta siguiente seccion:",
      not any(ob[CAVE:CAVE + 0x100]))
print("nuevo   0x93B000..0x93B060:", nb[CAVE:CAVE + 0x60].hex(" "))
print("alineada a 4:", CAVE % 4 == 0, "a 8:", CAVE % 8 == 0, "a 16:", CAVE % 16 == 0, "a 32:", CAVE % 32 == 0)

# --- relocaciones
print("\n== Relocaciones ==")
for buf, tag in ((nb, "nuevo"), (ob, "fabrica")):
    e = elf(buf)
    tot = 0
    for sec in e.iter_sections():
        if sec["sh_type"] not in ("SHT_REL", "SHT_RELA"):
            continue
        sym = e.get_section(sec["sh_link"]) if sec["sh_link"] else None
        hits = []
        n = 0
        for r in sec.iter_relocations():
            n += 1
            o = r["r_offset"]
            if CAVE - 0x100 <= o < CAVE + 0x100 or HOOK <= o < HOOK + 8:
                hits.append((hex(o), r["r_info_sym"], r["r_info_type"]))
        tot += n
        print(f"{tag:7} {sec.name:10} entradas {n}  cerca_gancho_o_cueva {hits}")
    print(tag, "total_relocs", tot)

# --- literales que apunten a la cueva (4 bytes LE) en todo el fichero
print("\n== Referencias literales a 0x93B000..0x93B052 ==")
lo, hi = CAVE, CAVE + 0x52
for buf, tag in ((nb, "nuevo"), (ob, "fabrica")):
    found = []
    for v in range(lo, hi, 2):  # Thumb: direcciones impares (|1) y pares
        for cand in (v, v | 1):
            pat = struct.pack("<I", cand)
            start = 0
            while True:
                i = buf.find(pat, start)
                if i < 0:
                    break
                found.append((hex(cand), hex(i)))
                start = i + 1
    # limita ruido
    print(tag, "ocurrencias", len(found), found[:20])

# --- symbolos cercanos
print("\n== Simbolos .dynsym en 0x930000..0x940000 ==")
for sec in en.iter_sections():
    if isinstance(sec, SymbolTableSection):
        for sym in sec.iter_symbols():
            v = sym["st_value"]
            if 0x930000 <= v < 0x940000:
                print(sec.name, sym.name, hex(v), sym["st_size"], sym["st_info"]["type"])

print("\n== Simbolos .dynsym en 0x712000..0x713000 ==")
for sec in en.iter_sections():
    if isinstance(sec, SymbolTableSection):
        for sym in sec.iter_symbols():
            v = sym["st_value"]
            if 0x712000 <= v < 0x713000:
                print(sec.name, sym.name, hex(v), sym["st_size"], sym["st_info"]["type"])
