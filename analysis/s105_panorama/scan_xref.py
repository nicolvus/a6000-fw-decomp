#!/usr/bin/env python3
"""S105 — xrefs a direcciones del blob mediante el idioma Thumb
   `ldr rX, [pc, #imm]` (pool con palabra W) seguido de `add rX, pc`
   -> direccion efectiva = W + (direccion del `add`) + 4.

Convención: vaddr = 0x43541000 + off.
Uso: scan_xref.py A6000 0xADDR1,0xADDR2,...
"""
import struct, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
BLOBS = {
    "A6000": ROOT / "analysis/rea-independent/input/av-cam.bin",
    "A7S": ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}

def build(data, targets):
    n = len(data)
    tset = set(targets)
    hits = []
    u16 = struct.unpack_from
    for off in range(0, n - 4, 2):
        hw = u16("<H", data, off)[0]
        # --- ADD (register) T1 con Rn = PC : 0x4478 + Rd
        if 0x4478 <= hw <= 0x447F:
            rd = hw & 7
            pc_add = off + 4
            for back in range(1, 13):
                lo = off - 2 * back
                if lo < 0:
                    break
                lh = u16("<H", data, lo)[0]
                if (lh & 0xF800) == 0x4800 and ((lh >> 8) & 7) == rd:
                    pool = ((lo + 4) & ~3) + (lh & 0xFF) * 4
                    if pool + 4 <= n:
                        W = u16("<I", data, pool)[0]
                        eff = (W + pc_add + BASE) & 0xFFFFFFFF
                        if eff in tset:
                            hits.append((lo + BASE, off + BASE, pool + BASE, rd, eff))
        # --- ADD (register) T2 (32 bits) con Rn = PC
        elif (hw & 0xFFF0) == 0xE08F:
            hw2 = u16("<H", data, off + 2)[0]
            rd = (hw2 >> 8) & 0xF
            pc_add = off + 4
            for back in range(1, 13):
                lo = off - 2 * back
                if lo < 0:
                    break
                lh = u16("<H", data, lo)[0]
                if (lh & 0xF800) == 0x4800 and ((lh >> 8) & 7) == rd:
                    pool = ((lo + 4) & ~3) + (lh & 0xFF) * 4
                    if pool + 4 <= n:
                        W = u16("<I", data, pool)[0]
                        eff = (W + pc_add + BASE) & 0xFFFFFFFF
                        if eff in tset:
                            hits.append((lo + BASE, off + BASE, pool + BASE, rd, eff))
                elif (lh & 0xFF7F) == 0xF8DF:
                    hw2b = u16("<H", data, lo + 2)[0]
                    if ((hw2b >> 12) & 0xF) == rd:
                        pool = ((lo + 4) & ~3) + (hw2b & 0xFFF)
                        if pool + 4 <= n:
                            W = u16("<I", data, pool)[0]
                            eff = (W + pc_add + BASE) & 0xFFFFFFFF
                            if eff in tset:
                                hits.append((lo + BASE, off + BASE, pool + BASE, rd, eff))
    return hits

def main():
    which = sys.argv[1]
    targets = [int(x, 0) for x in sys.argv[2].split(",")]
    data = BLOBS[which].read_bytes()
    for ldr, add, pool, rt, eff in sorted(set(build(data, targets))):
        print(f"ldr@0x{ldr:08x} add@0x{add:08x} pool@0x{pool:08x} r{rt} -> 0x{eff:08x}")

if __name__ == "__main__":
    main()
