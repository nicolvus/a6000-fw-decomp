"""El revisor paralelo debe dar el mismo resultado que el secuencial y producir el resumen."""
from pathlib import Path

from scripts.review_reports import ROOT, files, review


def test_revision_de_un_informe():
    r = review("docs/capture/s631-imaging_img.md")
    assert r["done"] and not [e for e in r["errors"] if e["kind"] == "enlace roto"]


def test_revision_de_un_informe_con_afirmaciones_abiertas():
    """El informe de prueba no se fija: cualquier documento con NO_VERIFICADO sirve, así el test no caduca."""
    abierto = next(f for f in files() if "NO_VERIFICADO" in (ROOT / f).read_text(errors="ignore"))
    r = review(abierto)
    assert r["open"] and not [e for e in r["errors"] if e["kind"] == "enlace roto"]


def test_cubre_los_informes_de_captura():
    found = files()
    assert "docs/capture/s631-imaging_img.md" in found
    assert not any(f.startswith("analysis/review_reports") for f in found)
    assert Path(ROOT, "docs/capture").is_dir()
