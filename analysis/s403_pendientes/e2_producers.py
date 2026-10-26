"""E2: sitios de libObj.so que construyen `MWF::ObjMsg(grupo, 0x10000005)` y si lo publican en una cola (`[obj]->vtable[+0xc](msg)`).
Solo bytes originales (Capstone Thumb sobre .text). Salida: e2_producers.json."""
import json
import re
import struct
import subprocess
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so")
OUT = Path(__file__).with_name("e2_producers.json")
MSG_ID = 0x10000005
CS = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def text_range() -> tuple[int, int]:
    out = subprocess.run(["readelf", "-SW", str(LIB)], capture_output=True, text=True, check=True).stdout
    m = re.search(r"\] \.text\s+PROGBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)", out)
    assert m
    return int(m.group(1), 16), int(m.group(2), 16)


def main() -> None:
    blob = LIB.read_bytes()
    lo, size = text_range()
    sites = []
    for a in range(lo, lo + size - 2, 2):
        h = struct.unpack_from("<H", blob, a)[0]
        if h & 0xF800 != 0x4800 or (h >> 8) & 7 != 2:
            continue
        p = ((a + 4) & ~3) + (h & 0xFF) * 4
        if struct.unpack_from("<I", blob, p)[0] != MSG_ID:
            continue
        ins = list(CS.disasm(blob[a - 12:a + 80], a - 12))
        ctor = next((i for i in ins if i.address > a and i.mnemonic in ("blx", "bl")), None)
        group = next((i.op_str for i in reversed(ins) if i.address < a and i.op_str.startswith("r1,") and i.mnemonic in ("mov.w", "movw", "movs")), None)
        post = any(i.mnemonic == "ldr" and i.op_str.endswith("[r3, #0xc]") for i in ins if i.address > a)
        sites.append({"ldr": hex(a), "grupo": group, "llamada": f"{ctor.mnemonic} {ctor.op_str}" if ctor else None, "publica_en_cola": post})
    OUT.write_text(json.dumps(sites, indent=1) + "\n")
    for s in sites:
        print(s)


if __name__ == "__main__":
    main()
