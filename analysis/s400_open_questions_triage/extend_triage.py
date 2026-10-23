"""Registra preguntas nuevas sin sustituir la revisión manual por una heurística."""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "analysis" / "s400_open_questions_triage" / "triage.json"
ROW = re.compile(
    r"^\| \[([^\]]+)\]\([^)]*\) \| (\w+) \| (\w+) \| \[([^\]]+)\]\([^)]*\) \| (.*)\|\s*$"
)


def main() -> None:
    triage = json.loads(P.read_text(encoding="utf-8"))
    for row in triage:
        if row["motivo"].startswith("auto:"):
            row["veredicto"] = "VIGENTE"
            row["motivo"] = "Pendiente de revisión manual; veredicto automático anterior retirado."
    seen = {(t["fuente"], t["destino"]) for t in triage}
    added = 0
    for line in (
        (ROOT / "docs" / "OPEN-QUESTIONS.md").read_text(encoding="utf-8").splitlines()
    ):
        m = ROW.match(line)
        if not m or (m[4], m[1]) in seen:
            continue
        dest, tipo, status, src = m[1], m[2], m[3], m[4]
        triage.append(
            {
                "fuente": src,
                "destino": dest,
                "tipo": tipo,
                "status_grafo": status,
                "veredicto": "VIGENTE",
                "motivo": "Pendiente de revisión manual de fuente, destino y evidencia.",
            }
        )
        seen.add((src, dest))
        added += 1
    P.write_text(json.dumps(triage, ensure_ascii=False, indent=1), encoding="utf-8")
    print(added, len(triage), dict(Counter(t["veredicto"] for t in triage)))


if __name__ == "__main__":
    main()
