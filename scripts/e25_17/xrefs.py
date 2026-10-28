"""Referencias a direcciones (cadenas/datos) vía `ldr rX,[pc,#]` + `add rX,pc` y literales absolutos.
Desensamblado lineal con resincronización; cachea el índice en /tmp. Uso: xrefs.py 0xADDR [0xADDR...]"""
import os
import pickle
import sys

from fw import BASE, _data, _md, u32

CACHE = "/tmp/e25_17_xref_index.pkl"
LO, HI = 0x43541000, 0x43b40000


def build():
    idx = {}   # destino -> [direcciones del add]
    a = LO
    lit = {}
    while a < HI:
        got = False
        for i in _md.disasm(_data[a - BASE:min(a - BASE + 0x4000, HI - BASE)], a):
            got = True
            a = i.address + i.size
            m, o = i.mnemonic, i.op_str
            if m.startswith("ldr") and "[pc" in o:
                try:
                    off = int(o.split("#")[1].rstrip("]"), 16)
                    lit[o.split(",")[0]] = (u32(((i.address + 4) & ~3) + off), i.address)
                except (ValueError, IndexError):
                    pass  # literal no resoluble
            elif m == "add" and o.endswith(", pc"):
                r = o.split(",")[0]
                if r in lit and i.address - lit[r][1] < 0x40:
                    idx.setdefault((lit[r][0] + i.address + 4) & 0xFFFFFFFF, []).append(i.address)
        if not got:
            a += 2
        else:
            pass
    return idx


def get():
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as fh:
            return pickle.load(fh)
    idx = build()
    with open(CACHE, "wb") as fh:
        pickle.dump(idx, fh)
    return idx


if __name__ == "__main__":
    idx = get()
    for arg in sys.argv[1:]:
        t = int(arg, 16)
        print(f"{t:08x}: " + " ".join(f"{x:08x}" for x in idx.get(t, [])))
