"""Cada fila de docs/OPEN-QUESTIONS.md debe estar triada en analysis/s400_open_questions_triage/."""

import json
import re
from pathlib import Path

from analysis.s400_open_questions_triage import extend_triage

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


def test_automatic_triage_requires_manual_review(tmp_path, monkeypatch) -> None:
    """Una cita aislada no permite cerrar una corrección ni descartarla."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/OPEN-QUESTIONS.md").write_text(
        "| [docs/capture/s385-diff.md](x) | CORRECTS | NO_VERIFICADO | "
        "[README.md](x) | corrige S385 |\n"
        "| [docs/capture/s382-callers.md](x) | CORRECTS | NO_VERIFICADO | "
        "[README.md](x) | resumen sin destino explícito |\n",
        encoding="utf-8",
    )
    triage_path = tmp_path / "triage.json"
    triage_path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(extend_triage, "ROOT", tmp_path)
    monkeypatch.setattr(extend_triage, "P", triage_path)
    extend_triage.main()
    result = json.loads(triage_path.read_text(encoding="utf-8"))
    assert len(result) == 2
    assert {row["veredicto"] for row in result} == {"VIGENTE"}
    extend_triage.main()
    assert json.loads(triage_path.read_text(encoding="utf-8")) == result


def test_reopen_automatic_verdicts_preserves_manual_review(tmp_path, monkeypatch) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/OPEN-QUESTIONS.md").write_text("", encoding="utf-8")
    manual = {"fuente": "a", "destino": "b", "veredicto": "FALSO_POSITIVO", "motivo": "revisión manual"}
    automatic = {"fuente": "c", "destino": "d", "veredicto": "FALSO_POSITIVO", "motivo": "auto: sin sesión"}
    triage_path = tmp_path / "triage.json"
    triage_path.write_text(json.dumps([manual, automatic]), encoding="utf-8")
    monkeypatch.setattr(extend_triage, "ROOT", tmp_path)
    monkeypatch.setattr(extend_triage, "P", triage_path)
    extend_triage.main()
    result = json.loads(triage_path.read_text(encoding="utf-8"))
    assert result[0] == manual
    assert result[1]["veredicto"] == "VIGENTE"
