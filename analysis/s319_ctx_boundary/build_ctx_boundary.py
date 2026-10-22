#!/usr/bin/env python3
"""S319 - frontera estatica del ctx 0x43ea70a0 (carril B).

Objetivo: decidir si el escritor de `[ctx]` y `[ctx+8]` esta en av-cam.bin o en un
modulo hermano. Se documenta el resultado NEGATIVO con su alcance:

* 40 sitios en av-cam calculan `ctx` (formas ldr/add pc de 16 y 32 bits); se
  clasifican como lectura de campo, escritura a otro offset o paso de `ctx` como
  argumento. Ninguno escribe `[ctx]` ni `[ctx+8]`.
* 0 palabras absolutas `0x43ea70a0`/`0x43ea70a8` en av-cam.
* 0 palabras absolutas en `kmod/*` y `lib/*` del firmware A7S.

Una ausencia de literal no prueba ausencia de escritura cross-module (puede ir por
memoria compartida/OSAL o por un mapeo del kernel); por eso el veredicto es
NO_VERIFICADO, no "imposible".

Solo bytes. Sin firmware ni camara.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm import ARM_OP_MEM, ARM_OP_REG

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
FW = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha15_unpacked_unpacked")
OUT = Path(__file__).with_name("ctx_boundary.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = True
CTX = 0x43EA70A0
CTX8 = 0x43EA70A8


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sites(blob: bytes, target: int) -> list[dict]:
    out = []
    for off in range(2, len(blob) - 4, 2):
        a = BASE + off
        h1 = struct.unpack_from("<H", blob, off - 2)[0]
        h2 = struct.unpack_from("<H", blob, off)[0]
        if (h2 & 0xFFF8) != 0x4478:
            continue
        rd = h2 & 7
        if (h1 & 0xF800) != 0x4800 or ((h1 >> 8) & 7) != rd:
            continue
        pc0 = (a + 4) & ~1
        lit = ((a + 4) & ~3) + (h1 & 0xFF) * 4
        if not (0 <= lit - BASE < len(blob) - 3):
            continue
        tgt = (struct.unpack_from("<I", blob, lit - BASE)[0] + pc0) & 0xFFFFFFFF
        if tgt == target:
            out.append({"add": f"0x{a:08x}", "reg": rd, "form": 16})
    for off in range(0, len(blob) - 8, 2):
        a = BASE + off
        h1, h2 = struct.unpack_from("<HH", blob, off)
        if h1 != 0xF8DF:
            continue
        rt = (h2 >> 12) & 0xF
        if rt >= 13:
            continue
        lit = ((a + 4) & ~3) + (h2 & 0xFFF)
        if not (0 <= lit - BASE < len(blob) - 3):
            continue
        h3 = struct.unpack_from("<H", blob, off + 4)[0]
        if (h3 & 0xFFF8) == 0x4478 and (h3 & 7) == rt:
            tgt = (struct.unpack_from("<I", blob, lit - BASE)[0] + ((a + 8) & ~1)) & 0xFFFFFFFF
            if tgt == target:
                out.append({"add": f"0x{a:08x}", "reg": rt, "form": 32})
    return out


def classify(blob: bytes, s: dict) -> tuple[str, int | None]:
    """Primera operacion con el registro base: (clase, offset)."""
    a = int(s["add"], 16)
    reg = s["reg"]
    rname = f"r{reg}"
    raw = blob[a + 2 - BASE:a + 2 - BASE + 24]
    for ins in MD.disasm(raw, a + 2):
        ops = ins.operands
        mem = [o for o in ops if o.type == ARM_OP_MEM]
        if mem and MD.reg_name(mem[0].mem.base) == rname:
            off = mem[0].mem.disp
            if ins.mnemonic.startswith("str"):
                return ("store", off)
            if ins.mnemonic.startswith("ldr"):
                return ("load", off)
            return ("otro", off)
        if ins.mnemonic.startswith("b") or ins.mnemonic in ("pop",):
            break
        if ins.mnemonic.startswith("mov") and ops and ops[0].type == ARM_OP_REG \
                and MD.reg_name(ops[0].reg) in ("r0", "r1", "r2", "r3"):
            return ("arg", None)
    return ("indirecto", None)


def scan_words(path: Path, targets: dict[int, str]) -> dict:
    b = path.read_bytes()
    hits = []
    for t, name in targets.items():
        pat = struct.pack("<I", t)
        off = b.find(pat)
        while off >= 0:
            hits.append({"target": name, "offset": f"0x{off:x}"})
            off = b.find(pat, off + 1)
    return {"path": str(path.relative_to(ROOT)), "size": len(b), "hits": hits}


def main() -> None:
    a7 = A7S.read_bytes()
    s_ctx = sites(a7, CTX)
    s_ctx8 = sites(a7, CTX8)
    ctx_class = [classify(a7, s) for s in s_ctx]
    kinds = [c[0] for c in ctx_class]
    stores_zero = [s["add"] for s, (k, off) in zip(s_ctx, ctx_class)
                   if k == "store" and off in (0, 8)]
    modules = []
    for d in ("kmod", "lib"):
        for p in sorted((FW / d).glob("*")):
            if p.is_file():
                modules.append(scan_words(p, {CTX: "ctx", CTX8: "ctx+8"}))
    data: dict = {
        "milestone": "S319",
        "title": "Frontera estatica del ctx 0x43ea70a0: sin escritor visible en av-cam ni literales en modulos",
        "firmware": {"a7s": {"sha256": sha256(A7S), "size": len(a7)}},
        "ctx": {"address": f"0x{CTX:08x}",
                "ctx_plus_8": f"0x{CTX8:08x}",
                "sites": s_ctx,
                "sites_ctx8": s_ctx8,
                "classification": {k: kinds.count(k) for k in sorted(set(kinds))},
                "stores_at_offset_0_or_8": stores_zero,
                "classification_detail": [{"add": s["add"], "class": c[0], "offset": c[1]}
                                          for s, c in zip(s_ctx, ctx_class)]},
        "absolute_words_av_cam": {
            "ctx": a7.count(struct.pack("<I", CTX)),
            "ctx8": a7.count(struct.pack("<I", CTX8))},
        "sibling_modules": modules,
        "verdict": "NO_VERIFICADO",
        "limits": [
            "Estatico: sin firmware ejecutado, sin camara, sin flasheo.",
            ("La ausencia de literales absolutos en los modulos no prueba ausencia de escritura: "
             "puede ir por memoria compartida, OSAL o un mapeo del kernel."),
            ("Los 40 sitios de av-cam se clasifican por su primera operacion; un escritor podria "
             "estar en una funcion que recibe ctx como argumento (no cubierto por el barrido)."),
            "S51 sin cambios.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print("sites ctx", len(s_ctx), "ctx+8", len(s_ctx8), "class", data["ctx"]["classification"])
    print("absolute av-cam", data["absolute_words_av_cam"])
    print("modules with hits", [(m["path"], len(m["hits"])) for m in modules if m["hits"]])


if __name__ == "__main__":
    main()
