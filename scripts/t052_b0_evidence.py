#!/usr/bin/env python3
"""T052-B0 — genera la evidencia estática de VTS y predicado.

Solo lee el firmware, el volcado de reposo y los backups NVRAM del PC.
No toca la cámara. Salida:
  analysis/t052-b0/vts.json
  analysis/t052-b0/predicado.json
"""
from __future__ import annotations

import glob
import hashlib
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
DUMP = ROOT / "analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin"
OUT = ROOT / "analysis/t052-b0"

BASE = 0x43541000
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
RAM_OFF = 0x40000000
GOT = 0x4401EEE4
RECORD_A = 0x43EA5B4C
RECORD_B = 0x43EEE770
SETTINGS = 0x43F79F94
IMAGER = 0x43EA976C
GATE_B = 0x43F6E5C2
PREDICATE = 0x43DEB360
DESCRIPTOR = 0x43EA13DC
CTX = 0x43EAADD8
PREDICATE_GOT_OFF = 0x64E8
NVRAM_OFF = 0x74218


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u16(data: bytes, va: int) -> int:
    return struct.unpack_from("<H", data, va - BASE)[0]


def u32(data: bytes, va: int) -> int:
    return struct.unpack_from("<I", data, va - BASE)[0]


def hx(data: bytes, va: int, n: int) -> str:
    return data[va - BASE:va - BASE + n].hex()


def dump_read(path: Path, virt: int, n: int) -> bytes:
    with path.open("rb") as f:
        f.seek(virt + RAM_OFF - 0x80000000)
        return f.read(n)


def literal_refs(data: bytes, target_literal: int) -> list[int]:
    """Direcciones de instrucciones LDR que cargan `target_literal`."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    refs = []
    pat = struct.pack("<I", target_literal)
    pos = []
    i = 0
    while True:
        j = data.find(pat, i)
        if j < 0:
            break
        pos.append(BASE + j)
        i = j + 1
    for lit in pos:
        for back in range(2, 0x400, 2):
            va = lit - back
            if va < BASE:
                break
            ins = list(md.disasm(data[va - BASE:va - BASE + 4], va))
            if not ins:
                continue
            ins = ins[0]
            if ins.mnemonic == "ldr" and "pc" in ins.op_str:
                mem = ins.operands[1].mem
                if ins.reg_name(mem.base) == "pc":
                    addr = ((ins.address + 4) & ~3) + mem.disp
                    if addr == lit:
                        refs.append(ins.address)
                        break
    return sorted(set(refs))


def main() -> int:
    fw = FW.read_bytes()
    assert sha256(fw) == SHA
    OUT.mkdir(parents=True, exist_ok=True)

    # --- VTS -----------------------------------------------------------------
    chain = {
        "record_0x20": {
            "virtual": f"0x{RECORD_A + 0x20:08x}",
            "source": "cap+0x5e0",
            "instruction": "0x43846e12 a4f8e035",
            "bytes_ok": hx(fw, 0x43846E12, 4) == "a4f8e035",
        },
        "cap_0x5e0": {
            "source": "[descriptor+6]",
            "instruction": "0x43846e08 db88 ; 0x43846e12 a4f8e035",
            "descriptor_rest_u16_6": struct.unpack_from("<H", dump_read(DUMP, DESCRIPTOR, 0x200), 6)[0],
        },
        "descriptor": {
            "virtual": f"0x{DESCRIPTOR:08x}",
            "source": "[ctx+0x3c]",
            "instruction": "0x43846d9c ldr r2,[r5,#0x3c]",
            "ctx": f"0x{CTX:08x}",
            "ctx_0x3c": f"0x{struct.unpack('<I', dump_read(DUMP, CTX + 0x3C, 4))[0]:08x}",
        },
        "ctx": {
            "dispatcher": "0x437b4eb4",
            "init": "0x437b4df0",
            "builder": "0x437b5b14",
            "constructor": "0x43844e80",
            "note": "ctx+0x3c se copia de la tabla de componentes; el descriptor es un objeto de modo en DRAM",
        },
    }
    vts = {
        "firmware_sha256": SHA,
        "base": f"0x{BASE:08x}",
        "ram_offset": f"0x{RAM_OFF:08x}",
        "chain": chain,
        "descriptor_rest_header_hex": dump_read(DUMP, DESCRIPTOR, 0x30).hex(),
        "vts_candidates": {
            "4219": "referencia efectiva medida en T046/T047; ley E=(4219-r5)*15.2 us",
            "4266": "0x4385de94(600,1,0): 0x271000/600 = 4266 (foto no la llama; solo vista en directo)",
        },
        "grep_4219_const_in_photo_path": {
            "result": "no aparece como constante del productor; el productor lee record+0x20",
            "byte_check": hx(fw, 0x4383FA66, 2) == "268c",
        },
        "static_conclusion": "VTS de fotografia NO determinado estaticamente: [descriptor+6] es 0 en reposo y su escritor/selector de foto no se localizo. Falta la lectura fisica de record+0x20 (o descriptor+6) tras un disparo.",
    }
    (OUT / "vts.json").write_text(json.dumps(vts, indent=1, ensure_ascii=False) + "\n")

    # --- Predicado -----------------------------------------------------------
    nv_files = sorted(glob.glob(str(ROOT / "analysis/camera-dumps/**/backup_mem.bin"), recursive=True))
    nv_rows: list[dict[str, int | str]] = []
    for p in nv_files:
        data = Path(p).read_bytes()
        i = data.find(bytes.fromhex("ffffff01020202"))
        if i < 0:
            continue
        block = data[i:i + 0x100]
        nv_rows.append({
            "path": str(Path(p).relative_to(ROOT)),
            "offset": i,
            "byte_10": block[0x10],
            "sha256_100": sha256(block),
        })
    ram_block = dump_read(DUMP, PREDICATE, 0x100)
    nv_block = None
    if nv_rows:
        first = nv_rows[0]
        data = Path(ROOT / str(first["path"])).read_bytes()
        off = int(first["offset"])
        nv_block = data[off:off + 0x100]

    refs = literal_refs(fw, PREDICATE_GOT_OFF)
    # Clasificación simple: un escritor a +0x10 tendría un str/strb con #0x10
    writes = []
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    for ref in refs:
        window = fw[ref - BASE:ref - BASE + 0x80]
        for ins in md.disasm(window, ref):
            if ins.mnemonic.startswith("str") and "#0x10]" in ins.op_str:
                writes.append({"at": f"0x{ins.address:08x}", "insn": f"{ins.mnemonic} {ins.op_str}"})

    pred = {
        "firmware_sha256": SHA,
        "object": f"0x{PREDICATE:08x}",
        "block_index": 5,
        "block_id": "0xbc0005",
        "block_size": 0x100,
        "ram_block_sha256_100": sha256(ram_block),
        "ram_byte_10": ram_block[0x10],
        "nvram_rows": nv_rows,
        "nvram_unique_sha256_100": sorted({r["sha256_100"] for r in nv_rows}),
        "ram_equals_nvram_first_100": bool(nv_block is not None and ram_block == nv_block),
        "got_slot": f"0x{GOT + PREDICATE_GOT_OFF:08x}",
        "got_slot_value": f"0x{struct.unpack('<I', dump_read(DUMP, GOT + PREDICATE_GOT_OFF, 4))[0]:08x}"
        if DUMP.exists() else None,
        "code_refs_to_got_offset": [f"0x{x:08x}" for x in refs],
        "raw_str_10_matches_in_windows": writes,
        "raw_str_10_interpretation": "Ninguno escribe en el objeto del predicado: 0x43a12ac4 pertenece a 0x43a12a84 y 0x43a12d12 a 0x43a12d9c; usan otras bases (r4/r2), no el puntero cargado desde GOT+0x64e8. El getter 0x43a12ca8 solo lee +0x10.",
        "callers_of_43a12ca8": ["0x4383fa9a", "0x438c7416", "0x43a1415a"],
        "caller_effects": {
            "0x4383fa9a": "0x4383fa40: si devuelve 1, r8 += frame (cuadro extra); r5 = 2*frame - lineas",
            "0x438c7416": "0x438c73f8: elige 0x19 (predicado 1) frente a 0x11 (predicado 0) en el flags de captura",
            "0x43a1415a": "0x43a14154: elige la tabla 0x4401ae4e (predicado 1) frente a 0x4401ad6c (predicado 0)",
        },
        "static_conclusion": "El bloque de 0x100 B es una copia literal del Backup/NVRAM (offset 0x74218 en los 12 backups); +0x10 = 0 en todos. No se encontró escritor directo de +0x10 en av-cam. El predicado devuelve 1 (cuadro extra activo). La lectura fisica tras un disparo sigue siendo necesaria para descartar un escritor externo, pero no hay evidencia de que exista.",
    }
    (OUT / "predicado.json").write_text(json.dumps(pred, indent=1, ensure_ascii=False) + "\n")
    print(f"escrito {OUT/'vts.json'}")
    print(f"escrito {OUT/'predicado.json'}")
    print(f"predicado: byte_10={ram_block[0x10]} refs={len(refs)} writes={len(writes)} nv_rows={len(nv_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
