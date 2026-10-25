#!/usr/bin/env python3
"""Revisión individual, reproducible y solo léxico-estructural de las etiquetas pendientes del censo S178.

Entrada: pendientes_auditados.json (S178) y los tres av-cam.bin. Salida: d1_census_review.json.
No cambia ningún veredicto del censo: clasifica la forma en que cada etiqueta aparece (módulo propio, subetiqueta, campo de
formato), su presencia en A7S/A6300 y su léxico de captura. La función real exige leer instrucciones (ver ACEPTO/NO_VERIFICADO).
"""
import json
import re
from collections import Counter
from pathlib import Path

import pic

ROOT = Path(__file__).resolve().parents[2]
CENSUS = ROOT / "analysis/s178_census/pendientes_auditados.json"
OUT = Path(__file__).with_name("d1_census_review.json")
LEXICON = re.compile(r"shut|expos|curtain|efcs|silent|readout|sensor|imager|\bSHR\b|\bVD\b|capture|\bCAP\b", re.IGNORECASE)


def classify(occ: list[dict], tag: str) -> tuple[str, float]:
    own = sum(1 for o in occ if o["cadena_vaddr"] == o["token_vaddr"]) / len(occ)
    field = sum(1 for o in occ if re.search(re.escape(tag) + r"\s*[%\d:=]", o["texto_hasta_nul_latin1"])
                and ">>" in o["texto_hasta_nul_latin1"].split(tag)[0]) / len(occ)
    if field >= 0.5:
        return "campo_de_formato", own
    if own >= 0.5:
        return "modulo_propio", own
    if own == 0:
        return "subetiqueta", own
    return "mixto", own


def main() -> None:
    census = json.loads(CENSUS.read_text())
    blobs = {m: pic.load(m) for m in ("a6000", "a7s", "a6300")}
    rows = []
    for e in census["etiquetas"]:
        if e["estado_censo"] != "pendiente":
            continue
        tag, occ = e["etiqueta"], e["ocurrencias"]
        kind, own = classify(occ, tag)
        texts = [o["texto_hasta_nul_latin1"] for o in occ]
        lex = sorted({m.lower() for t in texts for m in LEXICON.findall(t)})
        rows.append({
            "etiqueta": tag, "prioridad": e["prioridad"], "veredicto_censo": e["veredicto"],
            "ocurrencias": len(occ), "clase": kind, "fraccion_inicio_propio": round(own, 2),
            "con_ref_pic": sum(1 for o in occ if o["referencias_pic_candidatas"]),
            "recuento_bytes": {m: b.count(tag.encode()) for m, b in blobs.items()},
            "lexico_captura": lex,
            "ejemplos": [t[:90] for t in texts[:3]],
        })
    rows.sort(key=lambda r: (r["prioridad"], -r["ocurrencias"], r["etiqueta"]))
    summary = {
        "total": len(rows),
        "por_clase": dict(Counter(r["clase"] for r in rows)),
        "solo_a6000": sum(1 for r in rows if r["recuento_bytes"]["a7s"] == 0 and r["recuento_bytes"]["a6300"] == 0),
        "con_lexico_captura": [r["etiqueta"] for r in rows if r["lexico_captura"]],
    }
    OUT.write_text(json.dumps({"resumen": summary, "etiquetas": rows}, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
