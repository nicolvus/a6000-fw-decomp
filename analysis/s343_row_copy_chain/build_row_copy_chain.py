#!/usr/bin/env python3
"""S343 - carril B: a donde va el copiado de 20 B de la fila T.

S336 dejo abierto el unico camino de datos de las filas T sin seguir: `0x436f5f7c`
copia 20 B de la fila, parchea `+5`/`+7` si `[estado+0x18]&1` y llama a
`0x43ada310`.  Siguiendo la cadena completa:

  0x436f5f7c  copia 20 B de la fila T1 y parchea
      -> 0x43ada310  anade los 12 pares (flag, bit) y forma un bloque de 44 B
          -> 0x43ada480  guarda el id de canal (`[obj+4]` = 0..5), cuenta los
             flags no nulos (`obj+8`) y despacha a 5 manejadores
               -> 0x436f6710  tbh de 6 casos: descompone los bytes impares de la
                  fila en nibbles de los seis bloques de canal
               -> 0x436f7480  tbb de 6 casos: escribe 1 bit por bloque de canal
               -> 0x436f68ec / 0x43544270 / 0x436f6b9c  mascaras y tablas

Los seis bloques son **exactamente** los que lee el selector `w0` de S340:
`0xf3122300`, `0xf3122200`, `0xf3123300`, `0xf3123200`, `0xfc0a3100`,
`0xfc0a4100`.  La capa tiene **178** escritores de campo en A7S/A6300 y **177**
en A6000: el unico campo ausente en la A6000 es `0xfc0a3100+0xc` bit 24.

Solo lectura de los blobs: sin firmware en ejecucion, sin camara, sin flasheo.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
FW = ROOT / "firmware/extracted"
BLOBS = {
    "a7s_fw320": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/"
                       "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6000_fw321": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300_fw201": FW / ("a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/"
                         "dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
BLOCKS = [0xF3122300, 0xF3122200, 0xF3123300, 0xF3123200, 0xFC0A3100, 0xFC0A4100]
OUT = Path(__file__).with_name("row_copy_chain.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(b: bytes, a: int) -> int:
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b: bytes, a: int) -> int:
    return struct.unpack_from("<I", b, a - BASE)[0]


def code(b: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(b[start - BASE:start - BASE + size], start)]


def function_end(b: bytes, start: int, limit: int = 0x1000) -> int:
    """Primer `pop`/`bx lr` seguido de un prologo `push` a <= 8 B."""
    ins = code(b, start, limit)
    for i, cur in enumerate(ins[:-1]):
        if not (cur["insn"].startswith(("pop", "bx lr"))):
            continue
        nxt = ins[i + 1]
        gap = int(nxt["address"], 16) - (int(cur["address"], 16) + len(cur["bytes"]) // 2)
        if gap <= 8 and nxt["insn"].startswith("push"):
            return int(nxt["address"], 16)
    return start + limit


def bl_calls(b: bytes, start: int, size: int) -> list[str]:
    return [i["insn"].split()[1] for i in code(b, start, size)
            if i["insn"].startswith("bl ")]


def parse_writer(b: bytes, func: int) -> dict[str, Any] | None:
    """Reconoce `ldr r3,[pc]; ldr r2,[r3,#off]; bfi r2,r0,#lsb,#w; str; bx lr`."""
    ins = code(b, func, 14)
    if len(ins) < 5:
        return None
    t = [i["insn"] for i in ins]
    if (not t[0].startswith("ldr r3, [pc") or not t[1].startswith("ldr r2, [r3")
            or "bfi r2, r0" not in t[2] or not t[3].startswith("str r2, [r3")
            or t[4] != "bx lr"):
        return None
    m = re.search(r"\[pc, #(0x[0-9a-f]+|\d+)\]", t[0])
    assert m
    lit = ((func + 4) & ~3) + int(m.group(1), 0)
    m2 = re.search(r"\[r3(?:, #(0x[0-9a-f]+|\d+))?\]", t[1])
    off = int(m2.group(1), 0) if m2 and m2.group(1) else 0
    m3 = re.search(r"bfi r2, r0, #(0x[0-9a-f]+|\d+), #(0x[0-9a-f]+|\d+)", t[2])
    assert m3
    return {"function": f"0x{func:08x}", "literal_addr": f"0x{lit:08x}",
            "block": f"0x{u32(b, lit):08x}", "block_int": u32(b, lit),
            "offset": off, "lsb": int(m3.group(1), 0), "width": int(m3.group(2), 0)}


def writer_library(b: bytes) -> list[dict[str, Any]]:
    """Todos los escritores de campo de los seis bloques (por literal + patron)."""
    out: dict[str, Any] = {}
    for blk in BLOCKS:
        pat = struct.pack("<I", blk)
        i = b.find(pat)
        while i >= 0:
            lit = BASE + i
            func = lit - 0xC
            if func >= BASE:
                w = parse_writer(b, func)
                if w and w["block_int"] == blk:
                    out[w["function"]] = w
            i = b.find(pat, i + 1)
    return [out[k] for k in sorted(out)]


def read_getters(b: bytes) -> list[dict[str, Any]]:
    """Getters `ldr r3,[pc]; ldr r0,[r3,#off]; bx lr` de los seis bloques (S340)."""
    out = []
    for blk in BLOCKS:
        pat = struct.pack("<I", blk)
        i = b.find(pat)
        while i >= 0:
            lit = BASE + i
            func = lit - 0x8
            ins = code(b, func, 8)
            t = [x["insn"] for x in ins]
            if (len(t) >= 3 and t[0].startswith("ldr r3, [pc")
                    and t[1].startswith("ldr r0, [r3") and t[2] == "bx lr"):
                m = re.search(r"\[r3(?:, #(0x[0-9a-f]+|\d+))?\]", t[1])
                off = int(m.group(1), 0) if m and m.group(1) else 0
                out.append({"function": f"0x{func:08x}", "block": f"0x{blk:08x}",
                            "offset": off})
            i = b.find(pat, i + 1)
    return out


def tbh_targets(b: bytes, table: int, count: int = 6) -> list[int]:
    return [table + 2 * u16(b, table + 2 * k) for k in range(count)]


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    a7, a6, a63 = blobs["a7s_fw320"], blobs["a6000_fw321"], blobs["a6300_fw201"]

    # --- cadena de la copia de la fila -------------------------------------
    copy_span = code(a7, 0x436F5F7C, 0x5C)
    ada310 = code(a7, 0x43ADA310, 0x60)
    ada480 = code(a7, 0x43ADA480, 0x58)
    handlers = {
        "0x436f6710": {"calls": bl_calls(a7, 0x436F672C, 0x4C),
                       "tbh": [f"0x{x:08x}" for x in tbh_targets(a7, 0x436F6720)]},
        "0x436f68ec": {"evidence": code(a7, 0x436F68EC, 0x48)},
        "0x43544270": {"evidence": code(a7, 0x43544270, 0x2C)},
        "0x436f6b9c": {"evidence": code(a7, 0x436F6B9C, 0x2C),
                       "tbh": [f"0x{x:08x}" for x in tbh_targets(a7, 0x436F6BB8)]},
        "0x436f7480": {"tbb_stubs": [f"0x{0x436F748A + 2 * a7[0x436F748A - BASE + k]:08x}"
                                     for k in range(6)]},
    }
    # caso 0 del descompresor: 12 bytes impares de la fila -> 12 escritores
    case0 = []
    for ins in code(a7, 0x436F672C, 0x4C):
        if "ldrb r0, [r4, #" in ins["insn"]:
            case0.append({"row_byte": int(ins["insn"].split("#")[1].rstrip("]"), 16),
                          "at": ins["address"]})
        elif (ins["insn"].startswith(("bl ", "b.w #0x436f75"))
              and case0 and "writer" not in case0[-1]):
            case0[-1]["writer"] = ins["insn"].split()[1]

    lib = writer_library(a7)
    lib6 = writer_library(a6)
    lib63 = writer_library(a63)
    key = lambda w: (w["block_int"], w["offset"], w["lsb"], w["width"])
    keys7 = {key(w) for w in lib}
    keys6 = {key(w) for w in lib6}

    def counts(items: list[dict[str, Any]]) -> dict[str, int]:
        out: dict[str, int] = {}
        for w in items:
            out[w["block"]] = out.get(w["block"], 0) + 1
        return dict(sorted(out.items()))

    # bit unico por caso de 0x436f7480 (el stub hace `b.w` al escritor)
    singles = []
    for k in range(6):
        stub = 0x436F748A + 2 * a7[0x436F748A - BASE + k]
        target = stub
        for ins in code(a7, stub, 8):
            if ins["insn"].startswith("b.w #0x"):
                target = int(ins["insn"].split("#")[1], 16)
        w = parse_writer(a7, target)
        if w:
            singles.append({"case": k, "stub": f"0x{stub:08x}",
                            **{kk: w[kk] for kk in
                               ("function", "block", "offset", "lsb", "width")}})

    s340 = json.loads((ROOT / "analysis/s340_w0_selector/w0_selector.json").read_text())
    data: dict[str, Any] = {
        "milestone": "S343",
        "title": ("la copia de 20 B de la fila T configura los seis bloques MMIO "
                  "de canal (0xf3122xxx/0xfc0a3xxx/4xxx) con 178 escritores de campo"),
        "base": f"0x{BASE:08x}",
        "firmware": {k: {"sha256": sha256(BLOBS[k]), "size": len(blobs[k])}
                     for k in BLOBS},
        "chain": {
            "copy_function": "0x436f5f7c",
            "copy_code": copy_span,
            "block_builder": "0x43ada310",
            "block_code": ada310,
            "block_layout": {"row_bytes": 20, "pairs": 12, "pair_size": 2,
                             "total": 44, "padding_pair": [0, 0x0B]},
            "dispatch": {"function": "0x43ada480", "code": ada480,
                         "channel_id_source": "[obj+4] = bloque[0..3]",
                         "flag_count": "obj+8 = nº de pares con flag != 0",
                         "max_flags": 12},
        },
        "handlers": handlers,
        "decompress_case0": case0,
        "single_bit_writers": singles,
        "writer_library": {
            "total": len(lib),
            "per_block": counts(lib),
            "fields": [{"function": w["function"], "block": w["block"],
                        "offset": w["offset"], "lsb": w["lsb"],
                        "width": w["width"]} for w in lib],
        },
        "getters": {"total": len(read_getters(a7)), "list": read_getters(a7)},
        "s340_cross_check": {
            "blocks_equal": sorted(s340["verdicts"]["selector_bases"]) ==
                            [f"0x{b:08x}" for b in sorted(BLOCKS)],
            "selector_offsets": s340["verdicts"]["selector_offsets"],
        },
        "cross_model": {
            "writers": {"a7s": len(lib), "a6000": len(lib6), "a6300": len(lib63)},
            "getters": {"a7s": len(read_getters(a7)), "a6000": len(read_getters(a6)),
                        "a6300": len(read_getters(a63))},
            "per_block": {"a7s": counts(lib), "a6000": counts(lib6),
                          "a6300": counts(lib63)},
            "a7s_only_fields": [
                {"block": f"0x{k[0]:08x}", "offset": k[1], "lsb": k[2], "width": k[3]}
                for k in sorted(keys7 - keys6)],
            "a6000_only_fields": [
                {"block": f"0x{k[0]:08x}", "offset": k[1], "lsb": k[2], "width": k[3]}
                for k in sorted(keys6 - keys7)],
        },
        "negatives": {
            "writes_to_dfe_mask_register": 0,
            "writes_to_p2s_ram": 0,
            "mask_path_register": "0xfc02a00c (S335/S338)",
        },
        "verdicts": {
            "row_copy_destination": "campos de bit de los seis bloques de canal MMIO",
            "ends_in_log": False,
            "ends_in_p2s": False,
            "same_blocks_as_w0": True,
            "writer_count_a7s": len(lib),
            "a6000_missing_field": "0xfc0a3100+0xc bit 24",
            "channel_semantics": "NO_VERIFICADO",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Que los seis bloques sean «canales» es una etiqueta de trabajo: el "
             "numero de casos (6) y su uso por w0 lo sostienen, la funcion fisica no."),
            ("Los 5 manejadores se describen por su efecto sobre el bloque de 44 B; "
             "0x436f68ec/0x43544270/0x436f6b9c no se han descompuesto linea a linea."),
            ("La ausencia del campo 0xfc0a3100+0xc bit 24 en la A6000 es estatica: no "
             "prueba que el hardware no lo escriba por otra ruta."),
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("escritores", len(lib), counts(lib))
    print("A6000", len(lib6), "solo A7S:", data["cross_model"]["a7s_only_fields"])
    print("bits unicos:", [(s["case"], s["block"], hex(s["offset"]), s["lsb"]) for s in singles])


if __name__ == "__main__":
    main()
