"""Cada fila de docs/OPEN-QUESTIONS.md debe estar triada en analysis/s400_open_questions_triage/."""

import hashlib
import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path

from analysis.s400_open_questions_triage import extend_triage

ROOT = Path(__file__).resolve().parents[2]
TRIAGE = ROOT / "analysis" / "s400_open_questions_triage" / "triage.json"
ROW = re.compile(r"^\| \[([^\]]+)\]\([^)]*\) \| \w+ \| \w+ \| \[([^\]]+)\]")


def _open_keys() -> set[tuple[str, str]]:
    text = (ROOT / "docs" / "OPEN-QUESTIONS.md").read_text(encoding="utf-8")
    return {(m[2], m[1]) for line in text.splitlines() if (m := ROW.match(line))}


def test_every_open_question_is_triaged() -> None:
    triaged = {(t.get("fuente_actual", t["fuente"]), t["destino"])
               for t in json.loads(TRIAGE.read_text(encoding="utf-8"))}
    assert _open_keys() - triaged == set()


def test_verdicts_are_known() -> None:
    verdicts = {t["veredicto"] for t in json.loads(TRIAGE.read_text(encoding="utf-8"))}
    assert verdicts <= {"CORRECCION_APLICADA", "FALSO_POSITIVO", "VIGENTE"}


def test_current_index_matches_full_citations_contexts_and_relation_types() -> None:
    rows = json.loads(TRIAGE.read_text(encoding="utf-8"))
    seen = {extend_triage.identity(row) for row in rows}
    for line in (ROOT / "docs/OPEN-QUESTIONS.md").read_text(encoding="utf-8").splitlines():
        if match := extend_triage.ROW.match(line):
            candidate = {"fuente": match[4], "destino": match[1], "tipo": match[2],
                         **extend_triage.citation(match[4], match[5])}
            assert extend_triage.identity(candidate) in seen


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


def test_line_movement_preserves_review_but_changed_quote_does_not(tmp_path, monkeypatch) -> None:
    """Archivo:línea se recicla; una decisión pertenece a su cita y contexto."""
    (tmp_path / "docs").mkdir()
    source = tmp_path / "source.md"
    source.write_text("\n\nCorrige una premisa de destino.\n", encoding="utf-8")
    old = {
        "fuente": "source.md:1", "destino": "destino.md", "tipo": "CORRECTS",
        "status_grafo": "NO_VERIFICADO", "veredicto": "FALSO_POSITIVO",
        "motivo": "revisión documentada", "cita": "Corrige una premisa de destino.",
        "contexto": "Corrige una premisa de destino.", "revision_manual": "caso-1",
    }
    index = tmp_path / "docs/OPEN-QUESTIONS.md"
    index.write_text(
        "| [destino.md](x) | CORRECTS | NO_VERIFICADO | [source.md:3](x) | truncado |\n",
        encoding="utf-8",
    )
    path = tmp_path / "triage.json"
    path.write_text(json.dumps([old]), encoding="utf-8")
    monkeypatch.setattr(extend_triage, "ROOT", tmp_path)
    monkeypatch.setattr(extend_triage, "P", path)
    extend_triage.main()
    rows = json.loads(path.read_text())
    assert len(rows) == 1
    assert rows[0]["fuente_actual"] == "source.md:3"
    assert rows[0]["revision_manual"] == "caso-1"
    source.write_text("\n\nCorrige una afirmación diferente.\n", encoding="utf-8")
    extend_triage.main()
    rows = json.loads(path.read_text())
    assert len(rows) == 2
    assert rows[1]["veredicto"] == "VIGENTE"
    assert "revision_manual" not in rows[1]
    assert rows[1]["cita"] == "Corrige una afirmación diferente."
    extend_triage.main()
    assert json.loads(path.read_text()) == rows


def test_different_relation_types_do_not_share_a_verdict(tmp_path, monkeypatch) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/OPEN-QUESTIONS.md").write_text(
        "| [b](x) | CORRECTS | NO_VERIFICADO | [a](x) | cita |\n"
        "| [b](x) | SUPERSEDES | NO_VERIFICADO | [a](x) | cita |\n",
        encoding="utf-8",
    )
    path = tmp_path / "triage.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(extend_triage, "ROOT", tmp_path)
    monkeypatch.setattr(extend_triage, "P", path)
    extend_triage.main()
    assert len(json.loads(path.read_text())) == 2


def test_identical_marker_with_changed_context_requires_new_review(tmp_path, monkeypatch) -> None:
    (tmp_path / "docs").mkdir()
    source = tmp_path / "source.md"
    source.write_text("Objeto A\nCorrige el resultado.\n", encoding="utf-8")
    (tmp_path / "docs/OPEN-QUESTIONS.md").write_text(
        "| [b](x) | CORRECTS | NO_VERIFICADO | [source.md:2](x) | cita |\n",
        encoding="utf-8",
    )
    path = tmp_path / "triage.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(extend_triage, "ROOT", tmp_path)
    monkeypatch.setattr(extend_triage, "P", path)
    extend_triage.main()
    source.write_text("Objeto B\nCorrige el resultado.\n", encoding="utf-8")
    extend_triage.main()
    rows = json.loads(path.read_text())
    assert len(rows) == 2
    assert {r["veredicto"] for r in rows} == {"VIGENTE"}


@lru_cache(None)
def _snapshot(revision: str, path: str) -> list[str]:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{path}"], cwd=ROOT, text=True,
    ).splitlines()


def test_manual_review_preserves_original_sources_and_decisions() -> None:
    rows = json.loads(TRIAGE.read_text(encoding="utf-8"))
    audit = json.loads(TRIAGE.with_name("manual_review.json").read_text(encoding="utf-8"))
    original = json.loads("\n".join(_snapshot(
        audit["revision_destinos"], TRIAGE.relative_to(ROOT).as_posix(),
    )))
    assert len(original) == 392  # 132 anteriores + 207 del encargo + 53 posteriores
    for i, previous in enumerate(original):
        row = rows[i]
        assert (row["fuente"], row["destino"], row["tipo"]) == (
            previous["fuente"], previous["destino"], previous["tipo"],
        )
        assert row["veredicto_anterior"] == previous["veredicto"]
        assert row["motivo_anterior"] == previous["motivo"]
        assert row["revision_manual"] in audit["casos"]
    for row in rows:
        if "revision_manual" not in row:
            assert row["veredicto"] == "VIGENTE"
            continue
        case = audit["casos"][row["revision_manual"]]
        assert row["veredicto"] == case["veredicto"]
        assert row["motivo"] == case["razon"]
        path, number = row["fuente"].rsplit(":", 1)
        lines = _snapshot(row["revision_fuente"], path)
        index = int(number) - 1
        assert lines[index] == row["cita"]
        assert "\n".join(lines[max(0, index - 2):index + 3]).strip() == row["contexto"]
        assert row["destino_cita"] == "\n".join(
            _snapshot(audit["revision_destinos"], row["destino"])[:12],
        )
        if row["veredicto"] == "CORRECCION_APLICADA":
            assert case["evidencias"], row["fuente"]


def test_review_evidence_is_exact_and_has_not_changed() -> None:
    audit = json.loads(TRIAGE.with_name("manual_review.json").read_text(encoding="utf-8"))
    for case in audit["casos"].values():
        for entry in case["evidencias"]:
            raw = (ROOT / entry["archivo"]).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
            if entry["archivo"].endswith(".json"):
                quote = json.dumps(json.loads(raw)[entry["localizador"]], ensure_ascii=False)
            else:
                start, end = map(int, entry["localizador"].split(":"))
                quote = "\n".join(raw.decode().splitlines()[start - 1:end])
            assert quote == entry["cita"]


def test_review_does_not_repeat_previous_misclassifications() -> None:
    rows = json.loads(TRIAGE.read_text(encoding="utf-8"))
    by_key = {(r["fuente"], r["destino"]): r for r in rows}
    expected = [
        ("analysis/s50/shared/inbox-for-claude.md:5", "s49-capture-config-producer.md", "CORRECCION_APLICADA"),
        ("docs/capture/s50-codex-exposure-curtains.md:17", "s49-capture-config-producer.md", "CORRECCION_APLICADA"),
        ("docs/history/CONTEXT-full-2026-10-18.md:89", "s23-yc-pin-dataflow-boundary.md", "CORRECCION_APLICADA"),
        ("docs/capture/s59-sol.md:28", "s58-ae-timing-producers.md", "VIGENTE"),
        ("docs/capture/s135-elec-shutter.md:57", "s172-elec-shutter-a6300.md", "FALSO_POSITIVO"),
    ]
    for source, target, verdict in expected:
        assert by_key[source, f"docs/capture/{target}"]["veredicto"] == verdict
