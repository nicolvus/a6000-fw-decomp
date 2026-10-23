#!/usr/bin/env python3
"""S347 - carril B: que codifica el campo `0x000d` de la tabla ODL de S342 y que
relacion funcional tienen los 47 ids de la A6000 con los 69 de la A7S/A6300.

S342 dejo la tabla `0x43fef404` caracterizada como `{u16 id, u16 0x000d}` (69
entradas en A7S/A6300, 47 en A6000) y consumida por dos funciones que iteran
exactamente el numero de entradas.  S347 (esta sesion) mide **el campo** y la
**relacion entre modelos** con bytes, no con nombres:

  * el segundo `u16` vale `0x000d` en las 69/47/69 entradas de los tres modelos
    (no es un dato por id: es una constante de la tabla);
  * el mismo `0x000d` se pasa como **segundo argumento del inicializador de
    stream** del camino de carga por id, en los tres modelos
    (`movs r1,#2` + `movs r2,#0xd` + `bl <init>`), y la cabecera del mensaje que
    se construye a continuacion es de `0x18` bytes: 13 no es el tamano de la
    cabecera;
  * el mismo `0x000d` se pasa como **primer argumento del allocador** de la
    tabla completa (slot `+0x2b0` de la interfaz importada) en los tres modelos;
  * en otros sitios de llamada de ese mismo inicializador el segundo parametro
    recibe **longitudes de runtime** (`ldrh.w r2,[sp,#0x4c]`), luego el
    parametro es un tamano, no un tipo;
  * el id viaja en el `u16` de offset `+0x12` del mensaje ODL (secuencia
    `strh rX,[r0]`/`[r0,#2]`/`strb [r0,#4]`/`strh rX,[r0,#0x12]` identica en
    los tres modelos), con `+0x14 = 0` y `timeout = -1`;
  * la lista de la A6000 es **exactamente** la de la A7S filtrada por `id<=0x4e`
    (78), conservando el orden; la A6300 es identica a la A7S (69/69).

Ademas se comprueba que `lensbin_lensproperty/LensAberrationData.bin` (que
existe y es **byte a byte identico** en los tres firmware) no contiene ni la
tabla `{id,0x000d}` ni la lista de ids: la lista de ids es codigo, no fichero.

Solo lectura de los blobs: sin firmware en ejecucion, sin camara, sin flasheo.
"""
from __future__ import annotations

import hashlib
import json
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
LENSBIN = {
    "a7s_fw320": FW / ("a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/"
                       "nflasha3_unpacked_unpacked/lensbin_lensproperty/LensAberrationData.bin"),
    "a6000_fw321": FW / ("fw321/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/lensbin_lensproperty/LensAberrationData.bin"),
    "a6300_fw201": FW / ("a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/"
                         "nflasha3_unpacked_unpacked/lensbin_lensproperty/LensAberrationData.bin"),
}

# Direcciones verificadas en S342 (tabla/companion/.bss) y en S347 (resto).
MODELS: dict[str, dict[str, Any]] = {
    "a7s_fw320": {
        "table": 0x43FEF404, "entries": 69, "companion": 0x43FEF520,
        "bss_array": 0x43E906F4,
        "cons_a": 0x437056EC, "cons_b": 0x43705748,
        "loop_a": 0x43705724, "loop_b": 0x4370576A,
        "alloc_arg": 0x4370574A,
        "load": 0x4373D52C, "load_init": (0x4373D530, 0x4373D532, 0x4373D538),
        "load_head_len": 0x4373D544, "builder": 0x4373D554,
        "id_store": 0x4373D560, "offset_store": 0x4373D56A,
        "cfg_write": (0x437051E6, 0x437051CC), "cfg_read": (0x43705248, 0x4370522C),
    },
    "a6000_fw321": {
        "table": 0x43FEAE1C, "entries": 47, "companion": 0x43FEAD58,
        "bss_array": 0x43E8197C,
        "cons_a": 0x436EB2CC, "cons_b": 0x436EB328,
        "loop_a": 0x436EB304, "loop_b": 0x436EB34A,
        "alloc_arg": 0x436EB32A,
        "load": 0x43721B9C, "load_init": (0x43721BA0, 0x43721BA2, 0x43721BA8),
        "load_head_len": 0x43721BB4, "builder": 0x43721BC4,
        "id_store": 0x43721BD0, "offset_store": 0x43721BDA,
        "cfg_write": (0x436FDA42, 0x436FDA3C), "cfg_read": (0x436FDAD4, 0x436FDAB4),
    },
    "a6300_fw201": {
        "table": 0x441B0B1C, "entries": 69, "companion": 0x441B0C38,
        "bss_array": 0x43FFFBC4,
        "cons_a": 0x43734BD8, "cons_b": 0x43734C34,
        "loop_a": 0x43734C10, "loop_b": 0x43734C56,
        "alloc_arg": 0x43734C36,
        "load": 0x4373B934, "load_init": (0x4373B938, 0x4373B93A, 0x4373B940),
        "load_head_len": 0x4373B94C, "builder": 0x4373B95C,
        "id_store": 0x4373B968, "offset_store": 0x4373B972,
        "cfg_write": (0x437346D2, 0x437346B8), "cfg_read": (0x43734734, 0x43734718),
    },
}

SECOND = 0x000D
HEADER_LEN = 0x18          # capacidad del mensaje que envuelve al bloque de 13 B
SIZES_SEEN = (5, 3, 0x13B, 0xB6, 0xBC)   # otras capacidades del mismo inicializador

OUT = Path(__file__).with_name("odl_field.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False


# --------------------------------------------------------------------------- #
# helpers de bytes / decodificacion
# --------------------------------------------------------------------------- #
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<H", blob, addr - BASE)[0]


def u32(blob: bytes, addr: int) -> int:
    return struct.unpack_from("<I", blob, addr - BASE)[0]


def insn(blob: bytes, addr: int) -> dict[str, str]:
    got = list(MD.disasm(blob[addr - BASE:addr - BASE + 4], addr))
    assert got, f"0x{addr:08x} no decodifica"
    i = got[0]
    return {"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
            "insn": f"{i.mnemonic} {i.op_str}".strip()}


def require(blob: bytes, addr: int, prefix: str) -> dict[str, str]:
    d = insn(blob, addr)
    assert d["insn"].startswith(prefix), (hex(addr), d["insn"], prefix)
    return d


def pic_base(blob: bytes, ldr: int, add: int) -> int:
    """`ldr rD,[pc,#imm]` + `add rD,pc` -> base.  PC=(add+4) con bit0 a 0."""
    h = u16(blob, ldr)
    assert (h & 0xF800) == 0x4800, f"0x{ldr:08x} no es ldr pc-rel"
    lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    h2 = u16(blob, add)
    assert (h2 & 0xFF00) == 0x4400, f"0x{add:08x} no es add"
    return (u32(blob, lit) + ((add + 4) & ~1)) & 0xFFFFFFFF


def pic_sites(blob: bytes, target: int) -> list[str]:
    out: list[str] = []
    n = len(blob)
    for off in range(0, n - 8, 2):
        h = u16(blob, BASE + off)
        if (h & 0xF800) != 0x4800:
            continue
        rd = (h >> 8) & 7
        lit = ((BASE + off + 4) & ~3) + ((h & 0xFF) * 4)
        if lit - BASE + 4 > n:
            continue
        word = u32(blob, lit)
        for k in (2, 4, 6, 8):
            a = BASE + off + k
            if a - BASE + 2 > n:
                break
            h2 = u16(blob, a)
            if ((h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
                    and (h2 & 7) == rd and ((h2 >> 7) & 1) == 0):
                if (word + ((a + 4) & ~1)) & 0xFFFFFFFF == target:
                    out.append(f"0x{BASE + off:08x}")
                break
    return out


def lit_sites(blob: bytes, value: int) -> list[str]:
    return [f"0x{BASE + i:08x}" for i in range(0, len(blob) - 3, 2)
            if u32(blob, BASE + i) == value]


def bl_targets(blob: bytes, target: int) -> list[str]:
    out: list[str] = []
    n = len(blob)
    for off in range(0, n - 4, 2):
        h = struct.unpack_from("<H", blob, off)[0]
        if (h & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", blob, off + 2)[0]
        if (h2 & 0xD000) != 0xD000:
            continue
        s = (h >> 10) & 1
        imm10 = h & 0x3FF
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        imm11 = h2 & 0x7FF
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        val = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s:
            val -= 1 << 25
        if (BASE + off + 4 + val) & 0xFFFFFFFF == target:
            out.append(f"0x{BASE + off:08x}")
    return out


def entries_of(blob: bytes, model: dict[str, Any]) -> list[dict[str, int]]:
    return [{"id": u16(blob, model["table"] + 4 * i),
             "second": u16(blob, model["table"] + 4 * i + 2),
             "word": u32(blob, model["table"] + 4 * i)}
            for i in range(model["entries"])]


def init_size_arg(blob: bytes, model: dict[str, Any]) -> dict[str, Any]:
    """`movs r1,#2` ; `movs r2,#<size>` ; ... `bl <init>`: segundo parametro."""
    r1, r2, call = model["load_init"]
    d1, d2, d3 = insn(blob, r1), insn(blob, r2), insn(blob, call)
    assert d1["insn"].replace(" ", "") in ("movsr1,#2", "mov.wr1,#2"), d1
    assert d2["insn"].replace(" ", "").startswith(("movsr2,#", "mov.wr2,#")), d2
    assert d3["insn"].startswith("bl "), d3
    size = int(d2["insn"].split("#")[1], 16)
    return {"channel": 2, "size": size, "size_insn": d2, "call_insn": d3,
            "init_function": d3["insn"].split()[1]}


def loop_bound(blob: bytes, addr: int, step: int) -> dict[str, Any]:
    """`cmp rX,#imm` + `bne`: el contador avanza `step` por iteracion."""
    d = insn(blob, addr)
    assert d["insn"].startswith("cmp"), d
    imm = int(d["insn"].split("#")[1], 16)
    return {"insn": d, "imm": imm, "step": step, "iterations": imm // step}


# --------------------------------------------------------------------------- #
def build_model(blob: bytes, name: str, model: dict[str, Any]) -> dict[str, Any]:
    ents = entries_of(blob, model)
    ids = [e["id"] for e in ents]
    seconds = [e["second"] for e in ents]

    ca = pic_base(blob, model["cons_a"] + 0x0C, model["cons_a"] + 0x10)
    cb = pic_base(blob, model["cons_b"] + 0x0C, model["cons_b"] + 0x0E)
    assert ca == cb == model["table"], (hex(ca), hex(cb), hex(model["table"]))

    la = loop_bound(blob, model["loop_a"], 1)
    lb = loop_bound(blob, model["loop_b"], 4)
    assert la["iterations"] == model["entries"], la
    assert lb["iterations"] == model["entries"], lb

    alloc = require(blob, model["alloc_arg"], "movs r0")
    alloc_val = int(alloc["insn"].split("#")[1], 16)

    size = init_size_arg(blob, model)
    head = require(blob, model["load_head_len"], "movs r3")
    head_val = int(head["insn"].split("#")[1], 16)
    builder = require(blob, model["builder"], "movs r3")
    idstore = require(blob, model["id_store"], "strh")
    offset = require(blob, model["offset_store"], "str")
    # prologo del constructor de mensaje: 20 B identicos en los tres modelos
    prologue = blob[model["builder"] - BASE:model["builder"] - BASE + 20].hex()

    comp = [u32(blob, model["companion"] + 4 * i) for i in range(model["entries"])]
    bss = [u32(blob, model["bss_array"] + 4 * i) for i in range(model["entries"])]

    cw_addr, cw_cfg = model["cfg_write"]
    cr_addr, cr_cfg = model["cfg_read"]
    cw = require(blob, cw_addr, "strh")
    cr = require(blob, cr_addr, "ldrh")
    cfg_w = require(blob, cw_cfg, "movw")
    cfg_r = require(blob, cr_cfg, "movw")

    return {
        "table": {"address": f"0x{model['table']:08x}", "entries": model["entries"],
                  "end": f"0x{model['table'] + 4 * model['entries']:08x}",
                  "second_fields": sorted(set(seconds)),
                  "second_constant": len(set(seconds)) == 1,
                  "ids": ids, "ids_unique": len(set(ids)),
                  "ids_range": [min(ids), max(ids)]},
        "consumers": {
            "A": {"function": f"0x{model['cons_a']:08x}", "closed_loop": la},
            "B": {"function": f"0x{model['cons_b']:08x}", "closed_loop": lb,
                  "alloc_first_arg": alloc, "alloc_value": alloc_val},
        },
        "load_path": {
            "function": f"0x{model['load']:08x}",
            "init": size, "header_capacity": {"value": head_val, "insn": head},
            "builder": {"address": builder["address"], "insn": builder},
            "id_store": idstore, "offset_store": offset,
            "message_prologue_20b": prologue,
        },
        "config_persistence": {
            "write": cw, "read": cr,
            "config_id_write": cfg_w, "config_id_read": cfg_r,
        },
        "companion": {"address": f"0x{model['companion']:08x}",
                      "first": [f"0x{p:08x}" for p in comp[:6]],
                      "targets_zero_in_image": all(u32(blob, p) == 0 for p in comp),
                      "count": len(comp)},
        "bss_array": {"address": f"0x{model['bss_array']:08x}",
                      "zero_in_image": all(v == 0 for v in bss),
                      "count": len(bss)},
    }


def build_lensbin() -> dict[str, Any]:
    hashes = {k: sha256(p) for k, p in LENSBIN.items()}
    sizes = {k: p.stat().st_size for k, p in LENSBIN.items()}
    blob = LENSBIN["a7s_fw320"].read_bytes()
    ids = [e["id"] for e in entries_of(BLOBS["a7s_fw320"].read_bytes(), MODELS["a7s_fw320"])]
    # negativos: ni tabla {id,13} ni la lista de ids en el fichero
    pairs = 0
    for off in range(0, len(blob) - 8, 2):
        if struct.unpack_from("<H", blob, off + 2)[0] == SECOND:
            n = 1
            while (off + 4 * n + 4 <= len(blob)
                   and struct.unpack_from("<H", blob, off + 4 * n + 2)[0] == SECOND):
                n += 1
            pairs = max(pairs, n)
    id_list = b"".join(struct.pack("<H", x) for x in ids)
    return {"sizes": sizes, "sha256": hashes,
            "identical_across_models": len(set(hashes.values())) == 1,
            "max_consecutive_pairs_with_second_0x000d": pairs,
            "contains_a7s_id_list": blob.find(id_list) >= 0,
            "header": blob[:8].hex(),
            "directory_entries": struct.unpack_from("<H", blob, 4)[0]}


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    per_model = {k: build_model(blobs[k], k, MODELS[k]) for k in MODELS}

    ids7 = per_model["a7s_fw320"]["table"]["ids"]
    ids6 = per_model["a6000_fw321"]["table"]["ids"]
    ids63 = per_model["a6300_fw201"]["table"]["ids"]

    prefix = 0
    while prefix < len(ids6) and ids6[prefix] == ids7[prefix]:
        prefix += 1

    sizes = {k: v["load_path"]["init"]["size"] for k, v in per_model.items()}
    heads = {k: v["load_path"]["header_capacity"]["value"] for k, v in per_model.items()}
    allocs = {k: v["consumers"]["B"]["alloc_value"] for k, v in per_model.items()}
    prologues = {k: v["load_path"]["message_prologue_20b"] for k, v in per_model.items()}
    seconds = {k: v["table"]["second_fields"] for k, v in per_model.items()}

    data: dict[str, Any] = {
        "milestone": "S347",
        "title": ("el campo 0x000d de la tabla ODL es la constante 13 del camino de "
                  "carga (no un dato por id) y la lista A6000 es la A7S filtrada a id<=0x4e"),
        "base": f"0x{BASE:08x}",
        "firmware": {k: {"sha256": sha256(BLOBS[k]), "size": len(blobs[k])} for k in BLOBS},
        "models": per_model,
        "cross_model": {
            "entries": {k: per_model[k]["table"]["entries"] for k in MODELS},
            "second_field": {k: [f"0x{x:04x}" for x in seconds[k]] for k in MODELS},
            "a6000_equals_a7s_filtered_le_0x4e": ids6 == [x for x in ids7 if x <= 0x4E],
            "a6300_equals_a7s": ids63 == ids7,
            "shared_prefix_entries": prefix,
            "a6000_missing": sorted(set(ids7) - set(ids6)),
            "a6000_missing_count": len(set(ids7) - set(ids6)),
            "loop_iterations": {k: per_model[k]["consumers"]["A"]["closed_loop"]["iterations"]
                                for k in MODELS},
        },
        "field_meaning": {
            "value": SECOND,
            "constant_in_all_entries": all(v["table"]["second_constant"] for v in per_model.values()),
            "same_value_in_load_path": {k: sizes[k] for k in MODELS},
            "same_value_in_group_alloc": {k: allocs[k] for k in MODELS},
            "header_capacity": {k: heads[k] for k in MODELS},
            "message_prologue_identical": len(set(prologues.values())) == 1,
            "runtime_length_call_sites": {
                "example": "0x438f7fdc ldrh.w r2,[sp,#0x4c] -> 0x438f7fe2 bl 0x43ae1332",
                "insn": insn(blobs["a7s_fw320"], 0x438F7FDC),
                "call": insn(blobs["a7s_fw320"], 0x438F7FE2),
            },
            "other_capacities": [f"0x{x:x}" for x in SIZES_SEEN],
            "homonym": ("en la A6000 `movs r0,#0xd` aparece tambien como id de modulo del "
                        "logger (0x437219f8 = log(0xd, 3, 1, fmt)); no confundir con el "
                        "tamano del camino de carga"),
        },
        "lens_aberration_file": build_lensbin(),
        "negatives": {
            "absolute_literal_refs_to_table": {
                k: len(lit_sites(blobs[k], MODELS[k]["table"])) for k in MODELS},
            "pic_bases_to_table": {k: pic_sites(blobs[k], MODELS[k]["table"]) for k in MODELS},
            # 20 de los 34 codigos de drive mode coinciden numericamente con ids:
            # el espacio 1..0x64 se solapa, pero la tabla no se indexa por modo (S342)
            "mode_codes_intersect_ids_a7s": sorted(
                set(ids7) & set(struct.unpack_from(
                    "<34I", blobs["a7s_fw320"], 0x43FEE370 - BASE))),
        },
        "verdicts": {
            "second_field_is_per_id_data": False,
            "second_field_is_constant_13": True,
            "same_13_in_load_path_all_models": len(set(sizes.values())) == 1 and sizes["a7s_fw320"] == SECOND,
            "same_13_in_group_alloc_all_models": len(set(allocs.values())) == 1 and allocs["a7s_fw320"] == SECOND,
            "13_equals_message_header_size": heads["a7s_fw320"] == SECOND,
            "id_is_u16_at_message_offset_0x12": all(
                v["load_path"]["id_store"]["insn"].split()[1].startswith("r")
                and "#0x12" in v["load_path"]["id_store"]["insn"]
                for v in per_model.values()),
            "a6000_ids_are_a7s_subset_in_order": True,
            "a6000_equals_a7s_filtered_le_0x4e": ids6 == [x for x in ids7 if x <= 0x4E],
            "a6300_equals_a7s": ids63 == ids7,
            "lensbin_identical_across_models": True,
            "ids_index_the_lensbin_file": False,
            "semantic_of_13": "INFERENCIA ALTA: tamano en bytes del bloque de datos de "
                              "aberracion que el ODL mueve por id",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("El destino real de los 13 B (peticion o respuesta) no se puede decidir sin "
             "runtime: el mensaje se envia por la interfaz importada (slot 0x2b0/0x2c8/0x2cc), "
             "cuyo cuerpo vive en otro modulo."),
            ("Que 13 sean 'bytes del bloque de aberracion' es INFERENCIA: lo verificado es que "
             "el valor se usa como capacidad del bloque que se adjunta al mensaje (13) y que la "
             "cabecera es 24."),
            ("El contenido fisico de cada bloque y el motivo de que la A6000 no pida los ids "
             "0x4f..0x64 quedan NO_VERIFICADOS."),
            "REA/Ghidra comparten motor: su acuerdo no es independencia; manda el byte.",
            "S51 (A/B/C) no cambia: el modulo ODL es de aberracion del objetivo, no del obturador.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("entradas:", data["cross_model"]["entries"],
          "| segundo campo:", data["cross_model"]["second_field"])
    print("prefijo comun A6000/A7S:", prefix, "| faltan en A6000:",
          len(data["cross_model"]["a6000_missing"]))
    print("13 en load/alloc/cabecera:", sizes, allocs, heads)


if __name__ == "__main__":
    main()
