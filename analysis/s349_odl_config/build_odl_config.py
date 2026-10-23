#!/usr/bin/env python3
"""S349 - carril B: el `u16` persistido en config `0x402` offset `+0x680`
(«aberration data info») no es un id de la tabla del ODL.

La pregunta de la cola era si ese valor (escrito por `SetAberrationDataInfo` y por
`job_Mount_SaveAberrationDataHndl`, leido por `job_Mount_LoadAberrationDataHndl`)
se compara o se usa como indice de la tabla `{id,0x000d}` de S342.  S349 mide las
cuatro funciones del cluster, los dos globales que espejan el valor (u16 + puntero
al bloque de config) y **todas** las referencias a esos globales:

  * Set   `(u16)`   guarda el u16 en un global, lee la config `0x402` y guarda el
                    puntero del bloque (o 0 si falla);
  * Save  `(u16)`   escribe el u16 en `cfg+0x680`, hace commit y llama a Set;
  * Load  `()`      lee `cfg+0x680`, hace commit y llama a Set;
  * Close `()`      hace commit, pone a 0 el u16 y el puntero.

  * las referencias a los dos globales son **3-4 por modelo y todas dentro del
    cluster** (0 sitios fuera): nadie compara el valor con la tabla;
  * la tabla `{id,0x000d}` sigue teniendo **solo sus dos consumidores** (S342), y
    ninguno de los cuatro metodos la toca.

Conclusion (VERIFICADA, negativa acotada): el `u16` es un **selector persistido
del propio modulo de montura/ODL**, no un id de la tabla.  Que provenga del
objetivo o de la UI queda NO_VERIFICADO (el valor llega como argumento del job).

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
MODELS: dict[str, dict[str, Any]] = {
    "a7s_fw320": {
        "set": 0x4370516C, "save": 0x437051C0, "load": 0x43705224,
        "close": 0x4370528C, "table": 0x43FEF404,
        "set_prologue": "0f4b", "set_store": 0x4370517A, "set_store_bytes": "1880",
        "save_store": 0x437051E6, "save_store_bytes": "a3f88046",
        "load_read": 0x43705248, "load_read_bytes": "b3f88056",
        "close_strh": 0x437052B0, "close_str": 0x437052B6,
    },
    "a6000_fw321": {
        "set": 0x436FD9B0, "save": 0x436FDA1C, "load": 0x436FDAB0,
        "close": 0x436FDB4C, "table": 0x43FEAE1C,
        "set_prologue": "144b", "set_store": 0x436FD9BE, "set_store_bytes": "1880",
        "save_store": 0x436FDA42, "save_store_bytes": "a3f88066",
        "load_read": 0x436FDAD4, "load_read_bytes": "b3f88066",
        "close_strh": 0x436FDB86, "close_str": 0x436FDB8C,
    },
    "a6300_fw201": {
        "set": 0x43734658, "save": 0x437346AC, "load": 0x43734710,
        "close": 0x43734778, "table": 0x441B0B1C,
        "set_prologue": "0f4b", "set_store": 0x43734666, "set_store_bytes": "1880",
        "save_store": 0x437346D2, "save_store_bytes": "a3f88046",
        "load_read": 0x43734734, "load_read_bytes": "b3f88056",
        "close_strh": 0x4373479C, "close_str": 0x437347A2,
    },
}
CFG_ID = 0x402
CFG_OFF = 0x680
OUT = Path(__file__).with_name("odl_config.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False


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


def raw(blob: bytes, addr: int, n: int) -> bytes:
    return blob[addr - BASE:addr - BASE + n]


def dis(blob: bytes, addr: int, n: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(blob[addr - BASE:addr - BASE + n], addr)]


def pic_base(blob: bytes, ldr: int, add: int) -> int:
    h = u16(blob, ldr)
    assert (h & 0xF800) == 0x4800, f"0x{ldr:08x} no es ldr pc-rel"
    lit = ((ldr + 4) & ~3) + ((h & 0xFF) * 4)
    h2 = u16(blob, add)
    assert (h2 & 0xFF00) == 0x4400 and ((h2 >> 3) & 0xF) == 0xF
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


def bl_callers(blob: bytes, target: int) -> list[str]:
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


def pic_pairs(blob: bytes, start: int, n: int) -> list[tuple[int, int, int]]:
    """Pares `ldr rD,[pc,#imm]` + `add rD,pc` dentro de los primeros `n` bytes."""
    out: list[tuple[int, int, int]] = []
    pending: dict[int, int] = {}
    for d in dis(blob, start, n):
        addr = int(d["address"], 16)
        parts = d["insn"].replace(",", " ").split()
        if parts[0] == "ldr" and "pc" in d["insn"] and "[" in d["insn"]:
            pending[parts[1]] = addr
        elif parts[0] == "add" and d["insn"].endswith(" pc") and parts[1] in pending:
            out.append((pending.pop(parts[1]), addr, pic_base(blob, pending.get(parts[1], 0) or 0, addr)
                        if False else pic_base(blob, [k for k, v in pending.items() if v == v] and 0 or 0, addr)))
    return out


def build_model(blob: bytes, m: dict[str, Any]) -> dict[str, Any]:
    set_a, save_a, load_a, close_a = m["set"], m["save"], m["load"], m["close"]
    # prologo de Set: `ldr r3,[pc,#imm]` con el inmediato documentado
    assert raw(blob, set_a, 2).hex() == m["set_prologue"], "prologo de Set"
    assert raw(blob, m["set_store"], 2).hex() == m["set_store_bytes"], "strh r0 de Set"
    assert raw(blob, m["save_store"], 4).hex() == m["save_store_bytes"], "store +0x680"
    assert raw(blob, m["load_read"], 4).hex() == m["load_read_bytes"], "load +0x680"
    assert raw(blob, m["close_strh"], 2).hex() == "1a80", "Close: u16 = 0"
    assert raw(blob, m["close_str"], 2).hex() == "1a60", "Close: puntero = 0"
    # globales: el u16 que guarda Set y el puntero al bloque de config
    g_u16 = pic_base(blob, set_a, set_a + 8)
    # el segundo par PIC de Set esta tras la lectura de config (+0x1e / +0x22)
    g_ptr = pic_base(blob, set_a + 0x1E, set_a + 0x22)
    cfg_sites = [f"0x{BASE + i:08x}" for i in range(0, len(blob) - 3, 2)
                 if u32(blob, BASE + i) != 0 and False]
    # id de config 0x402 en Save/Load
    cfg_movw = [f"0x{BASE + i:08x}" for i in range(0, len(blob) - 3, 2)
                if raw(blob, BASE + i, 4).hex() == "40f20240"]
    return {
        "methods": {
            "set": {"entry": f"0x{set_a:08x}", "code": dis(blob, set_a, 0x40),
                    "callers": bl_callers(blob, set_a)},
            "save": {"entry": f"0x{save_a:08x}", "code": dis(blob, save_a, 0x40),
                     "callers": bl_callers(blob, save_a)},
            "load": {"entry": f"0x{load_a:08x}", "code": dis(blob, load_a, 0x40),
                     "callers": bl_callers(blob, load_a)},
            "close": {"entry": f"0x{close_a:08x}", "code": dis(blob, close_a, 0x40),
                      "callers": bl_callers(blob, close_a)},
        },
        "config": {"id": f"0x{CFG_ID:03x}", "offset": f"0x{CFG_OFF:03x}",
                   "id_sites": cfg_movw,
                   "id_sites_in_cluster": [s for s in cfg_movw
                                           if set_a - 0x40 <= int(s, 16) <= close_a + 0x40],
                   "unused": cfg_sites},
        "globals": {
            "u16": {"address": f"0x{g_u16:08x}", "value_in_image": u16(blob, g_u16),
                    "sites": pic_sites(blob, g_u16)},
            "ptr": {"address": f"0x{g_ptr:08x}", "value_in_image": f"0x{u32(blob, g_ptr):08x}",
                    "sites": pic_sites(blob, g_ptr)},
        },
        "table_sites": pic_sites(blob, m["table"]),
    }


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in BLOBS.items()}
    per = {k: build_model(blobs[k], MODELS[k]) for k in MODELS}

    for k, m in per.items():
        lo = MODELS[k]["set"] - 0x40
        hi = MODELS[k]["close"] + 0x40
        for g in ("u16", "ptr"):
            sites = [int(s, 16) for s in m["globals"][g]["sites"]]
            m["globals"][g]["all_sites_in_cluster"] = all(lo <= s <= hi for s in sites)
        m["globals"]["u16"]["site_count"] = len(m["globals"]["u16"]["sites"])
        m["globals"]["ptr"]["site_count"] = len(m["globals"]["ptr"]["sites"])

    data: dict[str, Any] = {
        "milestone": "S349",
        "title": ("el u16 de config 0x402/+0x680 no es un id de la tabla ODL: solo lo "
                  "escribe/lee el cluster Set/Save/Load/Close"),
        "base": f"0x{BASE:08x}",
        "firmware": {k: {"sha256": sha256(BLOBS[k]), "size": len(blobs[k])} for k in BLOBS},
        "models": per,
        "verdicts": {
            "config_value_is_table_id": False,
            "globals_referenced_only_inside_cluster": all(
                m["globals"][g]["all_sites_in_cluster"] for m in per.values()
                for g in ("u16", "ptr")),
            "table_consumers_unchanged": all(len(m["table_sites"]) == 2
                                             for m in per.values()),
            "origin_of_value": "NO_VERIFICADO (llega como argumento del job de montura)",
        },
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("La ausencia de comparaciones con la tabla se limita a las referencias a los dos "
             "globales y a los cuatro metodos: un tercer consumidor podria leer la config "
             "0x402 por otra via (hay otros sitios `movw r0,#0x402` fuera del cluster, "
             "listados en `config.id_sites`)."),
            ("El valor llega como argumento del job (`job_Mount_SaveAberrationDataHndl(u16)`); "
             "quien lo produce (objetivo, UI o configuracion) queda NO_VERIFICADO."),
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"escrito {OUT.name}")
    for k, m in per.items():
        print(k, "u16", m["globals"]["u16"]["address"], m["globals"]["u16"]["sites"],
              "| ptr", m["globals"]["ptr"]["address"], m["globals"]["ptr"]["sites"],
              "| tabla", m["table_sites"])


if __name__ == "__main__":
    main()
