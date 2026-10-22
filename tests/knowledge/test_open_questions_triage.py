"""Cada fila de docs/OPEN-QUESTIONS.md debe estar triada en analysis/s400_open_questions_triage/."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRIAGE = ROOT / "analysis" / "s400_open_questions_triage" / "triage.json"
ROW = re.compile(r"^\| \[([^\]]+)\]\([^)]*\) \| \w+ \| \w+ \| \[([^\]]+)\]")


def _open_keys() -> set[tuple[str, str]]:
    text = (ROOT / "docs" / "OPEN-QUESTIONS.md").read_text(encoding="utf-8")
    return {(m[2], m[1]) for line in text.splitlines() if (m := ROW.match(line))}


def test_every_open_question_is_triaged() -> None:
    triaged = {(t["fuente"], t["destino"]) for t in json.loads(TRIAGE.read_text(encoding="utf-8"))}
    assert _open_keys() - triaged == set()


def test_verdicts_are_known() -> None:
    verdicts = {t["veredicto"] for t in json.loads(TRIAGE.read_text(encoding="utf-8"))}
    assert verdicts <= {"CORRECCION_APLICADA", "FALSO_POSITIVO", "VIGENTE"}
