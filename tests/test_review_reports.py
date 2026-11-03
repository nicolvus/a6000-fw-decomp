"""El revisor paralelo debe dar el mismo resultado que el secuencial y producir el resumen."""
from scripts.review_reports import files, review


def test_revision_de_un_informe():
    r = review("docs/capture/s631-imaging_img.md")
    assert r["open"] and r["done"] and not [e for e in r["errors"] if e["kind"] == "enlace roto"]


def test_cubre_los_informes_de_captura():
    found = files()
    assert "docs/capture/s631-imaging_img.md" in found
    assert not any(f.startswith("analysis/review_reports") for f in found)
