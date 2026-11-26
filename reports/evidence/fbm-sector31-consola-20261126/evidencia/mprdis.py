#!/usr/bin/env python3
"""Desensambla libmpr.so por VA del ELF (base 0) con capstone: anota nombres del .dynsym,
stubs de .plt (imports), cadenas del pool de literales y destinos de `bl`."""
import sys
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_ARM

LIB = "analysis/camera-extract/usr/lib/libmpr.so"
e = ELFFile(open(LIB, "rb"))
SEG = [(s["p_vaddr"], s["p_vaddr"] + s["p_filesz"], s["p_offset"]) for s in e.iter_segments() if s["p_type"] == "PT_LOAD"]
ROD = e.get_section_by_name(".rodata"); RO = (ROD["sh_addr"], ROD["sh_addr"] + ROD["sh_size"])

def sec(name):
    s = e.get_section_by_name(name); return (s["sh_addr"], s["sh_addr"] + s["sh_size"])

def rd(va, n):
    with open(LIB, "rb") as f:
        for a, b, o in SEG:
            if a <= va < b:
                f.seek(o + va - a); return f.read(min(n, b - va))
    return None

def rd32(va):
    b = rd(va, 4); return None if not b or len(b) < 4 else int.from_bytes(b, "little")

def cstr(va, maxn=100):
    b = rd(va, maxn)
    if not b: return None
    z = b.find(b"\x00")
    if z < 0: return None
    try: s = b[:z].decode()
    except UnicodeDecodeError: return None
    return s if s and all(32 <= ord(c) < 127 or c in "\n\t" for c in s) else None

def dynsyms():
    d = {}
    for s in e.get_section_by_name(".dynsym").iter_symbols():
        v = s["st_value"] & ~1
        if v and s["st_info"]["type"] in ("STT_FUNC", "STT_OBJECT"):
            d.setdefault(v, s.name)
    return d

def dem(n):
    return n

def rot(v, r):
    r &= 31
    return ((v >> r) | (v << (32 - r))) & 0xffffffff if r else v

import re as _re
def imms(txt):
    return [int(x, 0) for x in _re.findall(r"#(0x[0-9a-fA-F]+|\d+)", txt)]

def plt_map():
    """stub de .plt (ARM, 12 B) -> símbolo importado. Patrón:
         add ip, pc, #imm8, #rot   (o add ip, pc, #imm12)
         add ip, ip, #0xa5000
         ldr pc, [ip, #imm]!
       GOT = addr+8 + rot(imm8,rot) + 0xa5000 + imm."""
    rel = {}
    for r in e.get_section_by_name(".rel.plt").iter_relocations():
        ds = e.get_section_by_name(".dynsym").get_symbol(r["r_info_sym"])
        rel[r["r_offset"]] = ds.name
    out = {}
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    lo, hi = sec(".plt")
    code = rd(lo, hi - lo)
    ins = list(md.disasm(code, lo))
    for k in range(len(ins) - 2):
        a, b, c = ins[k], ins[k + 1], ins[k + 2]
        if a.mnemonic == "add" and b.mnemonic == "add" and c.mnemonic == "ldr" \
           and "ip, pc," in a.op_str and "ip, ip," in b.op_str and "[ip," in c.op_str:
            ia = imms(a.op_str); ib = imms(b.op_str); ic = imms(c.op_str)
            va = rot(ia[0], ia[1]) if len(ia) > 1 else ia[0]
            vb = rot(ib[0], ib[1]) if len(ib) > 1 else ib[0]
            v = va + vb + ic[0]
            g = a.address + 8 + v
            if g in rel:
                out[a.address] = rel[g]
            out.setdefault(a.address, rel.get(g, f"?got{g:#x}"))
    return out

SYM = dynsyms()
PLT = plt_map()

def literal(i):
    """ldr rX, [pc, #imm] -> valor en el pool (y cadena si cae en .rodata)."""
    if i.mnemonic != "ldr" or "[pc," not in i.op_str: return ""
    try: imm = int(i.op_str.split("#")[-1].rstrip("]"), 0)
    except ValueError: return ""
    a = (i.address + 4) & ~3
    v = rd32(a + imm)
    if v is None: return ""
    s = cstr(v) if RO[0] <= v < RO[1] else None
    if s: return f'   ; ={v:#x} "{s}"'
    t = (v & ~1) if SYM.get(v & ~1) else None
    if t: return f"   ; ={v:#x} {SYM[t]}"
    return f"   ; ={v:#x}"

def dis(va, n):
    code = rd(va, n)
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    for i in md.disasm(code, va):
        extra = literal(i)
        if i.mnemonic in ("bl", "blx", "b", "cbz", "cbnz") and i.op_str.startswith("#"):
            t = int(i.op_str[1:], 0) & ~1
            if t in SYM: extra = f"   ; {SYM[t]}"
            elif i.address in PLT: extra = ""
        if i.mnemonic in ("bl", "blx"):
            t = int(i.op_str[1:], 0) & ~1
            if t in PLT: extra += f"   ; PLT:{PLT[t]}"
            elif t in SYM: extra += f"   ; {SYM[t]}"
        print(f"{i.address:08x}: {i.bytes.hex():<10} {i.mnemonic:<8} {i.op_str}{extra}")

if __name__ == "__main__":
    print(f"# {LIB}: syms={len(SYM)} plt={len(PLT)}  rodata={RO[0]:#x}..{RO[1]:#x}")
    for a in sys.argv[1:]:
        if ":" in a: v, n = a.split(":"); v = int(v, 0); n = int(n, 0)
        else: v = int(a, 0); n = 0x60
        print(f"\n===== {v:#x} .. {v+n:#x} =====")
        dis(v, n)
