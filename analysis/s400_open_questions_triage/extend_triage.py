"""Añade a triage.json las filas de OPEN-QUESTIONS.md que aún no están triadas (regla automática de la ampliación)."""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "analysis" / "s400_open_questions_triage" / "triage.json"
ROW = re.compile(
    r"^\| \[([^\]]+)\]\([^)]*\) \| (\w+) \| (\w+) \| \[([^\]]+)\]\([^)]*\) \| (.*)\|\s*$"
)
CORR = re.compile(
    r"corrig|correcci|refut|sustitu|super[ao]|reemplaz|rectific|desmiente|invalida|deja sin efecto",
    re.IGNORECASE,
)


def main() -> None:
    triage = json.loads(P.read_text(encoding="utf-8"))
    seen = {(t["fuente"], t["destino"]) for t in triage}
    added = 0
    for line in (
        (ROOT / "docs" / "OPEN-QUESTIONS.md").read_text(encoding="utf-8").splitlines()
    ):
        m = ROW.match(line)
        if not m or (m[4], m[1]) in seen:
            continue
        dest, tipo, status, src, ev = m[1], m[2], m[3], m[4], m[5]
        sm = re.search(r"/s(\d{2,3})\b", dest)
        tok = f"S{sm.group(1)}" if sm else None
        if tok and re.search(tok + r"\b", ev) and CORR.search(ev):
            v, why = (
                "CORRECCION_APLICADA",
                f"auto: la cita nombra {tok} y declara su corrección",
            )
        else:
            v, why = (
                "FALSO_POSITIVO",
                "auto: índice/resumen o varios enlaces; la cita no declara una corrección de este destino",
            )
        triage.append(
            {
                "fuente": src,
                "destino": dest,
                "tipo": tipo,
                "status_grafo": status,
                "veredicto": v,
                "motivo": why,
            }
        )
        seen.add((src, dest))
        added += 1
    P.write_text(json.dumps(triage, ensure_ascii=False, indent=1), encoding="utf-8")
    print(added, len(triage), dict(Counter(t["veredicto"] for t in triage)))


if __name__ == "__main__":
    main()
