"""Firma de pines (tipo, índice, dirección) declarada por cada función de un ELF ARM32, vía constructores MWF.

Uso: python3 -I scripts/pin_signatures.py lib.so desensamblado.txt rtti.json salida.json
Tipos de pin: m_pinTbl de libSysDef.so (analysis/topology-table-libobj.json). Dirección 0=in, 1=out.
shortcut: solo resuelve inmediatos (movs/mov.w/movw/mov rN,rM, str rN,[sp]) en las 14 instrucciones previas;
argumentos calculados quedan None — revisar a mano cuando aparezcan."""
import bisect
import collections
import importlib.util
import json
import re
import sys

KINDS = {  # símbolo mangled del constructor -> registros con (tipo, índice, dirección)
    "_ZN3MWF6ObjPinC1EN9DefObjPin7PinTypeEiNS1_6PinDirEPNS_11EventSenderE": ("r1", "r2", "r3"),
    "_ZN17OBJAVBBCBASECLASS9BizObjPinC1EtN9DefObjPin7PinTypeEiNS1_6PinDirEPN3MWF11EventSenderE": ("r2", "r3", "sp0"),
    "_ZN5AVBIZ8UNIVERSE7UObjPinC1ERNS0_2UcEN9DefObjPin7PinTypeEiNS4_6PinDirEPN3MWF11EventSenderE": ("r2", "r3", "sp0"),
}
INS = re.compile(r"^\s*([0-9a-f]+):\s+(\S+)\s*(.*)$")


def signatures(lib: str, dis: str, rtti: str) -> dict:
    spec = importlib.util.spec_from_file_location("fo", "scripts/func_owner.py")
    fo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fo)
    _, _, _, ordered, _ = fo.load(dis, rtti, lib)
    pt = {p["type"]: p["name"] for p in json.load(open("analysis/topology-table-libobj.json"))["pin_tbl"]}
    lines = open(dis).read().splitlines()
    pins = collections.defaultdict(set)
    for i, line in enumerate(lines):
        kind = next((k for k in KINDS if k in line and "bl" in line), None)
        if not kind:
            continue
        regs = {}
        for prev in lines[max(0, i - 14):i]:
            m = INS.match(prev)
            if not m:
                continue
            op, args = m[2], m[3]
            if op in ("movs", "mov.w", "mov", "movw") and (mi := re.match(r"(r\d), #(0x[0-9a-f]+|\d+)$", args)):
                regs[mi[1]] = int(mi[2], 0)
            elif op == "mov" and (mr := re.match(r"(r\d), (r\d)$", args)):
                regs[mr[1]] = regs.get(mr[2])
            elif op == "str" and (ms := re.match(r"(r\d), \[sp\]$", args)):
                regs["sp0"] = regs.get(ms[1])
        t, n, d = (regs.get(r) for r in KINDS[kind])
        addr = int(line.split(":")[0], 16)
        fn = ordered[bisect.bisect_right(ordered, addr) - 1]
        pins[hex(fn)].add((pt.get(t, t), n, {0: "in", 1: "out"}.get(d, d)))
    return {f: sorted(v, key=str) for f, v in pins.items()}


if __name__ == "__main__":
    lib, dis, rtti, out = sys.argv[1:5]
    res = signatures(lib, dis, rtti)
    json.dump(res, open(out, "w"), indent=1)
    print(f"funciones con pines: {len(res)}")
