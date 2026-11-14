import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "gui" / "harness"))
import live  # noqa: E402


def variables(env: str) -> dict[str, str]:
    return dict(t.split("=", 1) for t in env.split() if "=" in t)


def test_shimenv_por_defecto_trae_la_sd_emulada():
    v = variables(live.construye_shimenv(True, ""))
    for k in ("SDIMG", "SDSECT", "FRONTRM", "BKMULTIPTR", "INSHORT", "NULLMWF", "TABLE0"):
        assert k in v, k
    assert v["SDSECT"] == "8388608"  # 4 GB / 512 B
    assert v["SKIPFN"].startswith("7fa3d4=0,") and "829da0=0" in v["SKIPFN"]  # el SKIPFN base se amplía, no se duplica
    assert live.construye_shimenv(True, "").count("SKIPFN=") == 1


def test_shimenv_sin_sd_es_el_anterior():
    v = variables(live.construye_shimenv(False, ""))
    assert "SDIMG" not in v and "FRONTRM" not in v and "TABLE0" not in v
    assert v["SKIPFN"] == "7fa3d4=0"


def test_shimextra_manda_sobre_el_conjunto():
    assert variables(live.construye_shimenv(True, "FRONTRM=9"))["FRONTRM"] == "9"
