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


def test_pendientes_have_valid_states_and_unique_ids():
    p = audit.pendientes()
    assert not p["estados_no_validos"] and not p["ids_duplicados"]
    assert {"E1", "R1", "R3"} <= set(p["ids_abiertos"])
