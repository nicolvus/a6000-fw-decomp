"""El auditor de la tarjeta no puede reventar con varios ficheros en `AVF_INFO` (regresión 26-11-2026)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts")]
import filmpb1_audita_tarjeta as A


def test_varios_ficheros_en_avf_info(tmp_path):
    avf = tmp_path / "AVF_INFO"
    avf.mkdir()
    for nombre in ("AVIN0002.INP", "AVIN0001.INP", "AVIN0003.DAT"):
        (avf / nombre).write_bytes(b"x")
    r = A.audita(tmp_path)
    assert [x["fichero"] for x in r["avf_info"]] == ["AVIN0001.INP", "AVIN0002.INP", "AVIN0003.DAT"]
    assert all(x["bytes"] == 1 for x in r["avf_info"])
