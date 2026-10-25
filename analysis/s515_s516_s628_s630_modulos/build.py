#!/usr/bin/env python3
"""Evidencia de cadenas y referencias de pool para [BL], [PNL], [FILE_NUM], [FSYSMODE], [RING_DIAL].

Solo bytes de av-cam.bin (base 0x43541000); no ejecuta firmware. Una referencia de pool es una
palabra LE alineada igual a la dirección de la cadena: indica que algún código la carga, no que
la emita ni cuándo. Equivalencia funcional, logger dual y relación con el obturador quedan
NO_VERIFICADO (mismo criterio que la auditoría S605–S627).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s403_pendientes"))
import pic

OUT = Path(__file__).resolve().parent
BASE = 0x43541000
SUFFIX = "firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
FIRMWARE = {
    "a6000_fw321": ROOT / "firmware/extracted/fw321" / SUFFIX,
    "a7s_fw320": ROOT / "firmware/extracted/a7s-fw320/payload" / SUFFIX,
    "a6300_fw201": ROOT / "firmware/extracted/a6300-fw201/payload" / SUFFIX,
}
MODULES = {
    "S515": "[BL]", "S516": "[PNL]", "S628": "[FILE_NUM]", "S629": "[FSYSMODE]", "S630": "[RING_DIAL]",
}


def strings_with_tag(blob: bytes, tag: str) -> dict[int, str]:
    """Cadenas NUL-terminadas que contienen la etiqueta (puede ir tras un prefijo), por offset de inicio."""
    out = {}
    for m in re.finditer(re.escape(tag.encode()), blob):
        start = blob.rfind(b"\0", 0, m.start()) + 1
        out[start] = blob[start:blob.index(b"\0", m.start())].decode("ascii", "replace")
    return out


def pic_index(blob: bytes) -> dict[int, list[dict]]:
    idx: dict[int, list[dict]] = {}
    for r in pic.pic_refs(blob):
        idx.setdefault(r["target"], []).append(r)
    return idx


def refs_for(blob: bytes, idx: dict[int, list[dict]], offset: int, text: str) -> list[dict]:
    """Referencias PIC al inicio de la cadena o a un punto interior (p. ej. tras el prefijo), con su siguiente llamada."""
    out = []
    for k in range(len(text) + 1):
        for r in idx.get(BASE + offset + k, []):
            c = pic.next_call(blob, r["add"] + 2)
            out.append({"add": f"0x{r['add']:08x}", "interior": k,
                        "call": f"0x{c[1]:08x}" if c else None})
    return out


def main() -> None:
    blobs = {k: p.read_bytes() for k, p in FIRMWARE.items()}
    result = {
        "firmware": {k: {"sha256": hashlib.sha256(b).hexdigest(), "size": len(b)} for k, b in blobs.items()},
        "modules": {},
    }
    for sid, tag in MODULES.items():
        per_fw = {k: strings_with_tag(b, tag) for k, b in blobs.items()}
        a6 = per_fw["a6000_fw321"]
        idx = pic_index(blobs["a6000_fw321"])
        refs = {o: refs_for(blobs["a6000_fw321"], idx, o, t) for o, t in a6.items()}
        texts = {k: {t[t.index(tag):] for t in v.values()} for k, v in per_fw.items()}  # compara desde la etiqueta
        result["modules"][sid] = {
            "tag": tag,
            "counts": {k: len(v) for k, v in per_fw.items()},
            "only_a6000_vs_a7s": len(texts["a6000_fw321"] - texts["a7s_fw320"]),
            "only_a6000_vs_a6300": len(texts["a6000_fw321"] - texts["a6300_fw201"]),
            "a6000_strings": [
                {"vaddr": f"0x{BASE + o:08x}", "text": t, "pic_refs": refs[o]}
                for o, t in sorted(a6.items())
            ],
            "with_pic_ref": sum(1 for o in a6 if refs[o]),
        }
    (OUT / "modulos.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    for sid, m in result["modules"].items():
        print(sid, m["tag"], m["counts"], "solo A6000 vs A7S/A6300:", m["only_a6000_vs_a7s"], m["only_a6000_vs_a6300"],
              "con ref PIC:", m["with_pic_ref"])


if __name__ == "__main__":
    main()
