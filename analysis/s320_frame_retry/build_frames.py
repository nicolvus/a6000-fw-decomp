#!/usr/bin/env python3
"""S320 - modo 2 vs modo 0 en el aplicador de listas: misma trama, reintento.

`0x436f25f0` (modo 2) y `0x43ad968a` (modo !=2) son el mismo formateador:
fijan obj[3]=arg1, llaman a 0x43ad931c y a 0x43ad9666. La unica diferencia es
que el de modo 2, si el formateador devuelve 2 (ocupado), llama a 0x43ad92e6 y
reintenta una vez; si vuelve a fallar, registra un log.

Solo bytes. Sin firmware ni camara.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
OUT = Path(__file__).with_name("frames.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

RETRY = (0x436F25F0, 0x30)
PLAIN = (0x43AD968A, 0x1E)
FORMATTER = (0x43AD9666, 0x20)
BUSY = (0x43AD92E6, 0x18)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def insns(blob: bytes, addr: int, size: int) -> list[dict]:
    raw = blob[addr - BASE:addr - BASE + size]
    return [{"address": f"0x{i.address:08x}", "bytes": i.bytes.hex(),
             "insn": f"{i.mnemonic} {i.op_str}".strip()}
            for i in MD.disasm(raw, addr)]


def main() -> None:
    a7 = A7S.read_bytes()
    a6 = A6000.read_bytes()
    retry = insns(a7, *RETRY)
    plain = insns(a7, *PLAIN)
    # prefijo comun: instrucciones identicas byte a byte hasta el primer desvio
    common = 0
    for x, y in zip(retry, plain):
        if x["bytes"] != y["bytes"]:
            break
        common += 1
    presence = {}
    for name, (addr, size) in [("retry", RETRY), ("plain", PLAIN),
                               ("formatter", FORMATTER), ("busy", BUSY)]:
        sig = a7[addr - BASE:addr - BASE + size]
        presence[name] = {"address": f"0x{addr:08x}", "bytes": size,
                          "signature": sig.hex(), "a6000_hits": a6.count(sig)}
    data: dict = {
        "milestone": "S320",
        "title": "Modo 2 no cambia la trama: reintenta el mismo formateador",
        "firmware": {"a7s": {"sha256": sha256(A7S), "size": len(a7)},
                     "a6000": {"sha256": sha256(A6000), "size": len(a6)}},
        "retry_path": {"entry": f"0x{RETRY[0]:08x}", "insn": retry},
        "plain_path": {"entry": f"0x{PLAIN[0]:08x}", "insn": plain},
        "common_insn": common,
        "extra_block": insns(a7, 0x436F260C, 0x1E),
        "formatter": {"entry": f"0x{FORMATTER[0]:08x}", "insn": insns(a7, *FORMATTER)},
        "busy": {"entry": f"0x{BUSY[0]:08x}", "insn": insns(a7, *BUSY)},
        "presence": presence,
        "conclusion": "modo 2 == misma trama + un reintento tras 0x43ad92e6",
        "limits": [
            "Estatico: sin firmware ejecutado, sin camara, sin flasheo.",
            "No se decodifica el contenido de la trama (0x43ad9666 delega en 0x43ad9628/0x436f2554).",
            "El enlace de 'modo 2' con el silent shutter sigue NO_VERIFICADO.",
            "S51 sin cambios.",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print("common_insn", common)
    print("presence", {k: v["a6000_hits"] for k, v in presence.items()})
    print("retry block", [i["insn"] for i in data["extra_block"]])


if __name__ == "__main__":
    main()
