#!/usr/bin/env python3
"""S331 - carril B: correccion de la firma de `0x436f618c` (indice = posicion de modo).

S317 etiqueto la entrada como `0x436f618c(obj, idx, modo)` y S327/S330 trataron
`obj+0x2b4` como el **indice de fila** de T1/T2/T3.  Los bytes de los dos unicos
llamadores dicen otra cosa:

* En `0x436f3bcc..0x436f3be2` (setter de modo, slot 8):
  ``r0`` devuelto por 0x43ada284 (busqueda lineal del codigo en el `u32[34]`) se
  guarda en `obj+0x1b8` y se pasa como **r1**; ``r2`` es `obj+0x2b4`.
* En `0x436f4472..0x436f4480` (segundo llamador): igual, ``r1 = r6 = indice`` y
  ``r2 = [obj+0x2b4]``.
* En el consumidor, `r5 = r1` y `muls r5, r2, r5` con `r2 = 0x1c` → la fila es
  **r1 = posicion del modo**; `r2` solo se compara con 1 para decidir una llamada
  de log (`0x438f7114`) antes de reutilizarse como stride.

Conclusiones que se publican aqui:

1. **La fila de T1/T2/T3 es la posicion del modo** en `0x43fee370` (0..33), no
   `obj+0x2b4`: la correspondencia fila<->modo queda **VERIFICADA** (corrige
   S327 y S330).
2. `obj+0x2b4` es un **flag de log** (0 en el singleton de S330).
3. Los otros dos aplicadores (`0x436f61f8`, `0x436f60ac`) comparten la misma
   firma `(obj, posicion, flag)`.
4. Con las bases de S329, la diferencia T de `0x4e`/`0x4f` frente a `0x4c`/`0x4d`
   es la **mascara de T2** (`0x3ff` -> 0); T1 y T3 son identicas.

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
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("consumer_signature.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

CONSUMER = 0x436F618C
SIBLINGS = {"fill_6c": 0x436F61F8, "fill_68": 0x436F60AC}
CALLSITE_SETTER = (0x436F3BC0, 0x436F3BE6)   # (busqueda lineal, tras el bl)
CALLSITE_SECOND = (0x436F4472, 0x436F4484)
SEARCH = 0x43ADA284
MODE_LIST = 0x43FEE370
TABLES = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30}
T_STRIDE = 0x1C
CODES = [0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51, 0x0B]
FIELD_ROWS = ("w0", "w4", "descriptor_index", "mask")


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


def raw(blob: bytes, addr: int, size: int) -> bytes:
    return blob[addr - BASE:addr - BASE + size]


def dis(blob: bytes, start: int, size: int) -> list[dict[str, str]]:
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw(blob, start, size), start)]


def bl_callers(blob: bytes, target: int) -> list[str]:
    out = []
    for i in range(0, len(blob) - 4, 2):
        h1 = struct.unpack_from("<H", blob, i)[0]
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", blob, i + 2)[0]
        if (h2 & 0xD000) not in (0xD000, 0xC000):
            continue
        s = (h1 >> 10) & 1
        imm10 = h1 & 0x03FF
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        addr = BASE + i
        if ((addr + 4 + imm) & 0xFFFFFFFF) == target:
            out.append(f"0x{addr:08x}")
    return out


def row(blob: bytes, base: int, index: int) -> dict[str, Any]:
    addr = base + T_STRIDE * index
    return {"w0": u32(blob, addr),
            "w4": f"0x{u32(blob, addr + 4):08x}",
            "descriptor_index": u32(blob, addr + 0x14),
            "mask": u16(blob, addr + 0x18),
            "hex": raw(blob, addr, T_STRIDE).hex()}


def main() -> None:
    blob = A7S.read_bytes()
    codes = [u32(blob, MODE_LIST + 4 * i) for i in range(34)]
    pos = {c: i for i, c in enumerate(codes)}

    consumer = dis(blob, CONSUMER, 0x20)
    # pruebas de registro en el consumidor
    check_muls = [i for i in consumer if i["insn"].startswith("muls")]
    check_mov = [i for i in consumer if i["insn"] == "mov r5, r1"]
    flag_cmp = [i for i in consumer if i["insn"] == "cmp r2, #1"]

    setter = dis(blob, CALLSITE_SETTER[0], CALLSITE_SETTER[1] - CALLSITE_SETTER[0])
    second = dis(blob, CALLSITE_SECOND[0], CALLSITE_SECOND[1] - CALLSITE_SECOND[0])
    search = dis(blob, SEARCH, 0x1C)

    tables = {name: [row(blob, base, i) for i in range(34)]
              for name, base in TABLES.items()}
    per_code = {f"0x{c:02x}": {"position": pos[c],
                               "rows": {name: tables[name][pos[c]] for name in TABLES}}
                for c in CODES}
    diffs = {}
    for name in TABLES:
        same = {}
        for a, b in ((0x4E, 0x4C), (0x4F, 0x4D), (0x4E, 0x51), (0x4F, 0x50),
                     (0x4C, 0x4D)):
            ra = tables[name][pos[a]]
            rb = tables[name][pos[b]]
            same[f"0x{a:02x}/0x{b:02x}"] = {
                "identical": all(ra[k] == rb[k] for k in FIELD_ROWS),
                "fields_equal": [k for k in FIELD_ROWS if ra[k] == rb[k]],
                "fields_diff": {k: [ra[k], rb[k]] for k in FIELD_ROWS
                                if ra[k] != rb[k]},
            }
        diffs[name] = same

    data: dict[str, Any] = {
        "milestone": "S331",
        "title": "La fila de T1/T2/T3 es la posicion del modo; obj+0x2b4 es un "
                 "flag de log (corrige S317/S327/S330)",
        "base": f"0x{BASE:08x}",
        "firmware": {"a7s_fw320": {"sha256": sha256(A7S), "size": len(blob)}},
        "consumer": {"address": f"0x{CONSUMER:08x}", "disasm": consumer,
                     "row_index_source": "r1",
                     "mov_r5_r1": bool(check_mov),
                     "stride_muls": check_muls[0]["insn"] if check_muls else None,
                     "flag_cmp": flag_cmp[0]["insn"] if flag_cmp else None,
                     "flag_effect": "si flag==1 llama a 0x438f7114 (log)",
                     "signature": "0x436f618c(obj, posicion_modo, flag)"},
        "siblings": {name: {"address": f"0x{addr:08x}",
                            "disasm": dis(blob, addr, 0x48),
                            "signature": "(obj, posicion_modo, flag)"}
                     for name, addr in SIBLINGS.items()},
        "search": {"address": f"0x{SEARCH:08x}", "disasm": search,
                   "returns": "indice 0..count-1 o 0xff",
                   "callers": bl_callers(blob, SEARCH)},
        "call_sites": {"setter": {"range": [f"0x{CALLSITE_SETTER[0]:08x}",
                                            f"0x{CALLSITE_SETTER[1]:08x}"],
                                  "disasm": setter,
                                  "r1": "[obj+0x1b8] (indice de la busqueda)",
                                  "r2": "[obj+0x2b4] (flag)"},
                       "second": {"range": [f"0x{CALLSITE_SECOND[0]:08x}",
                                            f"0x{CALLSITE_SECOND[1]:08x}"],
                                  "disasm": second,
                                  "r1": "r6 (indice de la busqueda)",
                                  "r2": "[obj+0x2b4] (flag)"}},
        "consumer_callers": bl_callers(blob, CONSUMER),
        "tables": {"bases": {k: f"0x{v:08x}" for k, v in TABLES.items()},
                   "per_code": per_code},
        "pair_diffs": diffs,
        "verdicts": {
            "row_index_is_mode_position": True,
            "obj_2b4_is_row_index": False,
            "obj_2b4_is_log_flag": True,
            "s326_row_to_mode_mapping": "VERIFICADA (via indice de la busqueda)",
            "s327_row_index_writer": "REFUTADO (escribe el flag)",
            "s330_singleton_row0_only": "REFUTADO (la fila la elige la posicion)",
            "silent_T_difference": "T2: mask 0x3ff (0x4c/0x4d) -> 0 (0x4e/0x4f)",
        },
        "corrections": [
            ("S317 etiqueto el tercer argumento como 'modo'; es un flag de log "
             "comparado con #1 antes de reutilizar r2 como stride."),
            ("S327 y S330 trataron obj+0x2b4 como indice de fila; los llamadores "
             "pasan como r1 la posicion del modo y obj+0x2b4 como r2."),
            ("Con la fila correcta, la diferencia de T2 entre 0x4c/0x4d y "
             "0x4e/0x4f es la mascara (0x3ff -> 0), no el indice de descriptor."),
        ],
        "limits": [
            "Solo lectura estatica; sin runtime, camara ni flasheo.",
            ("Que la mascara de 12 bits seleccione campos de un mensaje P2S es "
             "INFERENCIA: los descriptores B solo dan offsets dentro del objeto "
             "0x43dc02e0."),
            "No se asigna semantica fisica a los registros ni a los bloques.",
            "S51 (A/B/C) no cambia.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"escrito {OUT.name}")
    print("firma:", data["consumer"]["signature"], "| muls:", check_muls[0]["insn"])
    print("callers consumidor:", data["consumer_callers"])
    print("T2 4e/4c:", diffs["T2"]["0x4e/0x4c"])
    print("T1 4e/4c:", diffs["T1"]["0x4e/0x4c"]["identical"],
          "T3 4e/4c:", diffs["T3"]["0x4e/0x4c"]["identical"])


if __name__ == "__main__":
    main()
