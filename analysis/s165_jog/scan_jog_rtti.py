#!/usr/bin/env python3
"""S165 — RTTI: typeinfo -> nombre, clase base y vtable -> ranuras virtuales."""
import json
import struct
import sys

sys.path.insert(0, "analysis/s165_jog")
from common import BASE, B, N, U32, cstr  # noqa: E402

TI_VTABLE = {"__class_type_info": 0x43fd04f8, "__si_class_type_info": 0x43fd03d8}
VTAB_ZONE = (0x43fb0000, 0x43fe0000)   # zona donde vive la tabla de vtables


def find_all(v):
    pat = struct.pack("<I", v)
    out = []
    i = B.find(pat)
    while i >= 0:
        out.append(BASE + i)
        i = B.find(pat, i + 1)
    return out


def typeinfo_entries():
    """[(addr, name, base_addr)] para cada typeinfo(__si_class_type_info)."""
    out = []
    for a in range(0x43fd0000, 0x43fe0000, 4):
        vptr = U32(B, a - BASE)[0]
        if vptr not in TI_VTABLE.values():
            continue
        name_addr = U32(B, a + 4 - BASE)[0]
        nm = cstr(name_addr)
        if not nm or not nm[0].isdigit():
            continue
        base = None
        if vptr == TI_VTABLE["__si_class_type_info"]:
            base = U32(B, a + 8 - BASE)[0]
        out.append((a, nm, base))
    return out


def vtables_for(ti_addr):
    """Direcciones donde el puntero al typeinfo aparece (ranura typeinfo de una vtable)."""
    res = []
    for p in find_all(ti_addr):
        if VTAB_ZONE[0] <= p < VTAB_ZONE[1]:
            res.append(p)
    return res


def main():
    tis = typeinfo_entries()
    names = {a: (nm, base) for a, nm, base in tis}
    by_name = {nm: a for a, nm, _ in tis}
    want = sys.argv[1:] or ["Jog", "Illumi", "McAssert"]
    for a, nm, base in tis:
        if not any(w.lower() in nm.lower() for w in want):
            continue
        bn = names.get(base, (None, None))[0]
        print(f"\n== {nm}  typeinfo@{a:#x}  base={base and hex(base)} ({bn})")
        for p in vtables_for(a):
            addr_point = p + 4
            slots = []
            q = addr_point
            while True:
                v = U32(B, q - BASE)[0]
                slots.append((q, v))
                q += 4
                if len(slots) > 12:
                    break
                if not (BASE <= v < BASE + N):
                    break
            print(f"   vtable typeinfo-slot@{p:#x}  address-point={addr_point:#x}")
            for q, v in slots:
                lbl = ""
                if BASE <= v < BASE + N:
                    nmv = cstr(v)
                    if nmv and nmv[0].isdigit() and len(nmv) < 40:
                        lbl = "  <- " + nmv
                print(f"      slot@{q:#x}: {v:#x}{lbl}")


if __name__ == "__main__":
    main()
