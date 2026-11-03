"""El registro de verificación debe coincidir con las marcas reales de docs/capture."""
from scripts.build_pending_claims import OUT, ROOT, claims, labels, render


def test_registro_actualizado():
    assert OUT.read_text(encoding="utf-8") == render()


def test_cubre_todas_las_marcas_y_etiquetas():
    text = OUT.read_text(encoding="utf-8")
    assert text.count("- **V-") == len(claims()) > 1000
    assert len(labels()) == text.split("## A.")[1].split("## B.")[0].count("\n- `")
    assert (ROOT / "docs/capture/s631-imaging_img.md").exists()


def test_secciones_d_y_e_coinciden_con_la_revision():
    from scripts.build_pending_claims import review, unmarked

    text = OUT.read_text(encoding="utf-8")
    rev = review()
    extra, _ = unmarked(rev, {(r[0], r[1]) for r in claims()})
    assert text.count("- **W-") == len(extra)
    assert text.count("- **E-") == sum(e["kind"] == "VERIFICADO sin evidencia" for e in rev["errors"])
