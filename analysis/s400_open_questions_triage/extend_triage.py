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


def citation(source: str, fallback: str) -> dict[str, str]:
    """Conserva el marcador completo y su contexto, no los 160 caracteres del índice."""
    path, _, number = source.rpartition(":")
    if number.isdigit() and (ROOT / path).is_file():
        lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
        index = int(number) - 1
        if 0 <= index < len(lines):
            return {
                "cita": lines[index],
                "contexto": "\n".join(lines[max(0, index - 2):index + 3]).strip(),
            }
    return {"cita": fallback.strip(), "contexto": fallback.strip()}


def identity(row: dict) -> tuple:
    if "cita" in row:
        return (row["fuente"].rsplit(":", 1)[0], row["destino"], row.get("tipo"),
                row["cita"], row["contexto"])
    return (row["fuente"], row["destino"], row.get("tipo"))


def main() -> None:
    triage = json.loads(P.read_text(encoding="utf-8"))
    for row in triage:
        if row["motivo"].startswith("auto:"):
            row["veredicto"] = "VIGENTE"
            row["motivo"] = "Pendiente de revisión manual; veredicto automático anterior retirado."
    seen: dict[tuple, list[dict]] = {}
    for row in triage:
        if "cita" in row:
            row.pop("fuente_actual", None)
        seen.setdefault(identity(row), []).append(row)
    added = 0
    for line in (
        (ROOT / "docs" / "OPEN-QUESTIONS.md").read_text(encoding="utf-8").splitlines()
    ):
        m = ROW.match(line)
        if not m:
            continue
        dest, tipo, status, src = m[1], m[2], m[3], m[4]
        candidate = {
            "fuente": src,
            "fuente_actual": src,
            "destino": dest,
            "tipo": tipo,
            "status_grafo": status,
            "veredicto": "VIGENTE",
            "motivo": "Pendiente de revisión manual de fuente, destino y evidencia.",
            **citation(src, m[5]),
        }
        key = identity(candidate)
        if key in seen:
            for row in seen[key]:
                row["fuente_actual"] = src
            continue
        triage.append(candidate)
        seen[key] = [candidate]
        added += 1
    P.write_text(json.dumps(triage, ensure_ascii=False, indent=1), encoding="utf-8")
    print(added, len(triage), dict(Counter(t["veredicto"] for t in triage)))


if __name__ == "__main__":
    main()
