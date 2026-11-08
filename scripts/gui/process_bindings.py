#!/usr/bin/env python3
"""ProcessId → elemento de proceso y enlace con el negocio en `cmn_view_processDataMgr.so` de la A6000 fw3.21 (G13 §6). Solo lee.

`CmnViewProcessDataMgr::getElement(pid)` (`0x4ee6c`, `pid ≤ 0xe8`) indexa una tabla u32 con el caso de
`CmnViewElementFactory::factoryElement` (`tbh`, 145 casos → `…Element<Clase>::getInstance` por PLT).
`CmnViewProcessDataElementNormal::setProcessId` (`0x755c0`) guarda en `+0xc` el descriptor `D[pid]`: palabra 6 = puntero a los
modelos de datos (`+0` nombre `@Mxxx`), 7 = cuántos; palabra 8 = puntero a los ids de respaldo NVRAM, 9 = cuántos.
Uso: process_bindings.py [SALIDA.json]
"""
import json
import struct
import subprocess
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, str(Path(__file__).parent))
import elf_scan

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/cmn_view_processDataMgr.so"
FACTORY, GET_ELEMENT_LIT, GET_ELEMENT_ADD, SET_PID_LIT, SET_PID_ADD, NPID = 0x541AC, 0x4EE9C, 0x4EE7E, 0x755E4, 0x755D0, 0xE9


def _pc_table(raw: bytes, lit: int, add_pc: int) -> int:
    return (struct.unpack_from("<I", raw, lit)[0] + add_pc + 4) & 0xFFFFFFFF  # ldr rX,[pc] ; add rX,pc


def factory_cases(elf: elf_scan.Elf, raw: bytes) -> dict[int, str]:
    plt, md = elf.plt_map(), Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    ins = list(md.disasm(raw[FACTORY:FACTORY + 14], FACTORY))
    assert [i.mnemonic for i in ins[2:5]] == ["cmp", "bhi.w", "tbh"], ins
    n, base, out = int(ins[2].op_str.split("#")[1], 16), ins[4].address + 4, {}
    for case in range(n + 1):
        tgt = base + 2 * struct.unpack_from("<H", raw, base + 2 * case)[0]
        br = next(i for i in md.disasm(raw[tgt:tgt + 40], tgt) if i.mnemonic in ("b", "b.w", "bl", "blx"))
        stub = int(br.op_str.lstrip("#"), 16)
        sym = plt.get(stub + 4) or elf.name_of(stub, plt) or f"{stub:#x}"  # stub Thumb «bx pc» + entrada ARM del PLT
        out[case] = subprocess.run(["c++filt", sym], capture_output=True, text=True, check=True).stdout.strip() \
            .replace("::getInstance()", "").replace("CmnViewProcessDataElement", "")
    return out


def bindings() -> dict[int, dict]:
    elf, raw = elf_scan.Elf(LIB), LIB.read_bytes()
    cases = factory_cases(elf, raw)
    elem = struct.unpack(f"<{NPID}I", elf.read_vaddr(_pc_table(raw, GET_ELEMENT_LIT, GET_ELEMENT_ADD), 4 * NPID))
    desc = struct.unpack(f"<{NPID}I", elf.read_vaddr(_pc_table(raw, SET_PID_LIT, SET_PID_ADD), 4 * NPID))
    out = {}
    for pid in range(NPID):
        w = struct.unpack("<16I", elf.read_vaddr(desc[pid], 64))
        models = [raw[m:m + 8].split(b"\0")[0].decode() for m in
                  (struct.unpack_from("<I", elf.read_vaddr(w[6] + 0x24 * i, 4))[0] for i in range(w[7]))] if w[6] else []
        backups = [f"{struct.unpack_from('<I', elf.read_vaddr(w[8] + 0x18 * i, 4))[0]:#x}" for i in range(w[9])] if w[8] else []
        out[pid] = {"elemento": cases[elem[pid]], "modelos": models, "respaldos": backups}
    return out


if __name__ == "__main__":
    b = bindings()
    assert b[0x46]["elemento"] == "Normal" and b[0x46]["modelos"] == ["@M00F"], b[0x46]  # EFCS (funciona en cámara)
    assert b[0xC0]["respaldos"] == b[0xE4]["respaldos"] == ["0x107090f"], (b[0xC0], b[0xE4])  # Dial/Wheel Lock y Wheel Lock
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps({f"{k:#x}": v for k, v in b.items()}, indent=1))
    print(sum(v["elemento"] != "Normal" for v in b.values()), "Custom;", sum(bool(v["modelos"] or v["respaldos"]) for v in b.values()),
          "con modelo/respaldo de", len(b))
