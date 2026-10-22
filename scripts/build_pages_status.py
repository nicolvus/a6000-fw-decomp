"""Build the public, documentation-only milestone index for GitHub Pages."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "site" / "status.json"
PROGRESS = ROOT / "analysis" / "s178_census" / "census.md"
REPO = "https://github.com/nicolvus/a6000-fw-decomp/blob/main/"
SESSION = re.compile(r"(?:^|/)s(\d{1,3})(?:[-_/]|\.md$)", re.IGNORECASE)
HEADING = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def title(path: Path) -> str:
    match = HEADING.search(path.read_text(encoding="utf-8", errors="replace")[:3000])
    return match.group(1).strip() if match else path.stem.replace("-", " ")


def main() -> None:
    # The catalogue points to a representative document, not to a claim of completion.
    candidates: dict[int, tuple[int, Path]] = {}
    for folder, priority in (("docs/capture", 0), ("analysis", 1)):
        for path in sorted((ROOT / folder).rglob("*.md")):
            relative = path.relative_to(ROOT)
            match = SESSION.search(relative.as_posix())
            if not match:
                continue
            number = int(match.group(1))
            if not 1 <= number <= 999:
                continue
            score = priority + (2 if "conclusion" not in path.stem and "report" not in path.stem else 0)
            if number not in candidates or (score, len(relative.parts)) < (
                candidates[number][0], len(candidates[number][1].parts)
            ):
                candidates[number] = (score, relative)

    # S73/S74 share a report; S67 was cancelled in the general RE catalogue.
    candidates[74] = candidates[73]

    sessions = [
        {
            "id": f"S{number}",
            "title": "S74 — ADJ_CMD (informe conjunto S73/S74)" if number == 74 else title(ROOT / path),
            "source": REPO + path.as_posix(),
        }
        for number, (_, path) in sorted(candidates.items(), reverse=True)
    ]
    census = PROGRESS.read_text(encoding="utf-8")
    coverage = re.search(r"\*\*(\d+)/(\d+)\*\* = \*\*([\d.,]+) %\*\*", census)
    pending = re.search(r"\| \*\*pendientes reales\*\* \| \*\*(\d+)\*\*", census)
    if not coverage or not pending:
        raise ValueError("No se pudo leer la cobertura de S178")
    covered, total, percent = coverage.groups()
    if int(covered) + int(pending.group(1)) != int(total):
        raise ValueError("El censo S178 no suma cobertura y pendientes")

    data = {
        "generated_from": "Documentos versionados en docs/capture/ y analysis/",
        "latest": sessions[0]["id"] if sessions else None,
        "documented_count": len(sessions),
        "sessions": sessions,
        "module_coverage": {
            "covered": int(covered), "total": int(total),
            "pending": int(pending.group(1)), "percent": percent,
            "source": REPO + "analysis/s178_census/census.md",
        },
        "exceptions": {
            "S67": {
                "label": "Cancelada; el tema de AF se asignó a S63.",
                "source": REPO + "docs/capture/linea-general-re.md",
            }
        },
        "physical_tests": {"done": 0, "total": 8, "source": REPO + "docs/capture/physical-test-plan.md"},
        "decision": {"label": "No parchear: evidencia insuficiente", "source": REPO + "docs/capture/s51-decision.md"},
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "site" / "progress").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "docs" / "progress" / "index.html", ROOT / "site" / "progress" / "index.html")
    print(f"{len(sessions)} sesiones documentadas; última {data['latest']}; salida {OUTPUT}")


if __name__ == "__main__":
    main()
