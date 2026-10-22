#!/usr/bin/env python3
"""S133 — inventario de las trazas `[MOUNT_DEBUG]` del av-cam.bin de A6000 fw3.21.

Solo bytes. No usa REA/Ghidra.

* Cadenas: `[MOUNT_DEBUG]` (y, como contexto, `[MOUNT_ERROR]`/`[MOUNT_INFO]`/`[MOUNT_WARNING]`).
* Referencias: mapa **estricto** ya calculado del repo
  (`analysis/s106_imaging_cap/pic_refs_strict_global.json`, dest -> [direcciones del `add rX,pc`]).
  Regla canónica: ver `analysis/s106_imaging_cap/pic_xref_methodology.md`.
* Función contenedora de cada sitio: el prólogo `push {…,lr}` más cercano por detrás desde el
  que el desensamblado lineal llega **exactamente** al sitio sin cruzarse con un epílogo
  (`pop {…,pc}` / `bx lr`). Si ese test falla (piscinas de literales mixtas), se cae al
  prólogo más cercano y se marca `approx: true`. Los sitios del bucle principal
  `0x436e5e3c`–`0x436e7bf0` (hito S66) se asignan a `0x436e5e3c` por rango verificado.
* Llamadores: barrido lineal del blob recogiendo `bl #0x…`.

Uso:  .venv/bin/python analysis/s133_mount_debug/scan_mount_debug.py [SALIDA]
"""
import bisect
import json
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
REFS = ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json"
BASE = 0x43541000
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("mount_debug_raw.json")

# rango del bucle principal de la tarea BL verificado en S66
MAIN_LO, MAIN_HI = 0x436e5e3c, 0x436e7bf0

DATA = BIN.read_bytes()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False


def sweep():
    """Barrido lineal Thumb: prólogos, epílogos y llamadas."""
    prologues, calls = [], {}
    off, n = 0, len(DATA)
    while off < n:
        got = False
        for ins in MD.disasm(DATA[off:off + 16], BASE + off):
            got = True
            m, o = ins.mnemonic, ins.op_str
            if m.startswith("push") and "lr" in o:
                prologues.append(ins.address)
            if m in ("bl", "blx") and o.startswith("#0x"):
                calls.setdefault(int(o[1:], 16), []).append(ins.address)
            off += ins.size
        if not got:
            off += 2
    prologues.sort()
    return prologues, calls


def reaches_without_epilogue(start, site):
    last = None
    for ins in MD.disasm(DATA[start - BASE:site - BASE], start):
        if ins.address >= site:
            break
        m, o = ins.mnemonic, ins.op_str
        if (m.startswith("pop") and "pc" in o) or (m == "bx" and o == "lr"):
            return False
        last = ins
    return last is not None and last.address + last.size == site


def container(site, prologues):
    k = bisect.bisect_left(prologues, site) - 1
    for p in reversed(prologues[max(0, k - 60):k + 1]):
        if site - p > 0x3000:
            break
        if reaches_without_epilogue(p, site):
            return p, False
    for p in reversed(prologues[max(0, k - 60):k + 1]):
        if site - p > 0x3000:
            break
        return p, True
    return None, True


def strings(prefixes):
    out = []
    for m in re.finditer(rb"\[MOUNT_[A-Z]+\][^\x00]*", DATA):
        text = m.group().decode("latin1")
        tag = text[1:text.index("]")]
        if tag in prefixes:
            out.append((BASE + m.start(), text))
    return out


def main():
    refs = {int(k, 16): v for k, v in json.loads(REFS.read_text()).items()}
    prologues, calls = sweep()
    rows, byfunc = [], {}
    for addr, text in strings({"MOUNT_DEBUG", "MOUNT_ERROR", "MOUNT_INFO", "MOUNT_WARNING"}):
        sites = refs.get(addr, [])
        for site in sites:
            if MAIN_LO <= site < MAIN_HI:
                func, approx = MAIN_LO, False
            else:
                func, approx = container(site, prologues)
            rows.append({"str": addr, "site": site, "func": func, "approx": approx})
            if func is not None:
                byfunc.setdefault(func, set()).add(addr)
    funcs = []
    for f in sorted(byfunc):
        fsites = [r for r in rows if r["func"] == f]
        funcs.append({
            "vaddr": f,
            "site_count": len(fsites),
            "sites": sorted({r["site"] for r in fsites}),
            "string_vaddrs": sorted(byfunc[f]),
            "approx_function": any(r["approx"] for r in fsites),
            "bl_callers": calls.get(f, []),
        })
    per_string = {}
    for r in rows:
        per_string.setdefault(r["str"], []).append(r)
    out = {
        "milestone": "S133",
        "binary": str(BIN.relative_to(ROOT)),
        "vaddr_rule": "vaddr = 0x43541000 + file_offset",
        "xref_rule": "estricta (analysis/s106_imaging_cap/pic_refs_strict_global.json)",
        "counts": {
            "strings": len(per_string),
            "sites": len(rows),
            "functions": len(funcs),
            "unreferenced": sum(1 for a in per_string.values() if not a),
        },
        "strings": [
            {
                "vaddr": a,
                "text": t,
                "sites": sorted({r["site"] for r in per_string.get(a, [])}),
                "functions": sorted({r["func"] for r in per_string.get(a, []) if r["func"] is not None}),
            }
            for a, t in strings({"MOUNT_DEBUG", "MOUNT_ERROR", "MOUNT_INFO", "MOUNT_WARNING"})
        ],
        "functions": funcs,
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"{OUT}: {out['counts']}")


if __name__ == "__main__":
    main()
