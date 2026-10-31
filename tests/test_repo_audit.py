"""Auditoría mecánica: enlaces rotos, estados válidos de PENDIENTES y recorte de listas."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repo_audit", ROOT / "scripts/audit/repo_audit.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def test_clip_keeps_total_and_truncates_sample():
    r = audit.clip(list(range(audit.CAP + 5)))
    assert r["total"] == audit.CAP + 5 and len(r["muestra"]) == audit.CAP


def test_md_links_reports_missing_target_and_ignores_urls(tmp_path, monkeypatch):
    (tmp_path / "a.md").write_text("[ok](b.md) [web](https://x.org/y.md) [rota](nada.md) [ancla](#x)\n")
    (tmp_path / "b.md").write_text("x")
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    r = audit.md_links(["a.md", "b.md"])
    assert [e["enlace"] for e in r["rotos"]["muestra"]] == ["nada.md"]


def test_estado_valido_accepts_qualifiers():
    assert audit.estado_valido("CERRADO CON LÍMITE")
    assert audit.estado_valido("ABIERTO (instalado en T024, en prueba)")
    assert audit.estado_valido("PARCIAL")
    assert not audit.estado_valido("CERRADO PERO")


def test_pendientes_have_valid_states_and_unique_ids():
    p = audit.pendientes()
    assert not p["estados_no_validos"] and not p["ids_duplicados"]
    assert {"E1", "R1", "R3"} <= set(p["ids_abiertos"])


def test_test_claims_ignores_historical_snapshots(tmp_path, monkeypatch):
    for f in ("docs/history/h.md", "knowledge/PROGRESS.md", "docs/vivo.md"):
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("3 pruebas en `tests/test_x.py`\n")
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    r = audit.test_claims(["docs/history/h.md", "knowledge/PROGRESS.md", "docs/vivo.md"], {"tests/test_x.py": 5})
    assert [e["en"] for e in r["muestra"]] == ["docs/vivo.md"]
