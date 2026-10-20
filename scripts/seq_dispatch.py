"""Tabla de secuencias del selector 0x4380e43c: caso (cfg+0x264>>15) -> modo IMX210 -> función de secuencia.
Los punteros viven en la GOT PIC (base = literal + pc, entrada = base + offset). Uso: python3 -I scripts/seq_dispatch.py"""
import json
import struct
import sys

BASE, OFF = 0x43541000, 0x1F0
GOT_LIT, GOT_ADD_PC = 0x4354C94C, 0x4354C6E2 + 4  # ldr r6,[pc]; add r6,pc en 0x4354c6e0
# caso -> (entrada GOT, modo IMX210 escrito en DAT_43eea2e4); sale de analysis/ghidra/mode-pick-4380e43c.json
CASES = {7: (0x44020064, None), 8: (0x44020064, "5/0x32"), 9: (0x4401F6BC, 0x08), 10: (0x44022478, 0x11),
         0xB: (0x44023DA0, 0x11), 0xC: (0x4401F058, 0x11), 0xD: (0x44023840, 0x11), 0xE: (0x44022D28, 0x11),
         0xF: (0x44025204, 0x11), 0x10: (0x44021A2C, "0x21..0x2c"), 0x11: (0x44021A2C, "0x28..0x2e"),
         0x12: (0x4401FFA8, 0x01)}


def word(d: bytes, a: int) -> int:
    return struct.unpack_from("<I", d, OFF + a - BASE)[0]


def table(d: bytes) -> dict:
    got = (word(d, GOT_LIT) + GOT_ADD_PC) & 0xFFFFFFFF
    rows = {hex(c): {"got_entry": hex(e), "got_offset": hex(e - got), "func": hex(word(d, e) & ~1), "imx210_mode": m}
            for c, (e, m) in CASES.items()}
    return {"got_base": hex(got), "cases": rows}


if __name__ == "__main__":
    with open("analysis/av-cam-analysis-view.elf", "rb") as f:
        json.dump(table(f.read()), sys.stdout, indent=1)
