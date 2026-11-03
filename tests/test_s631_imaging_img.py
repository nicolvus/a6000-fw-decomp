"""S631: trazas [IMAGING_IMG] y sus cargas PC-relativas (datos de verify_imaging_img.py)."""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).parent.parent / "analysis/s631_imaging_img/imaging_img.json").read_text())


def test_siete_trazas_con_prefijo():
    assert DATA["traces"] == len(DATA["strings"]) == 7
    assert all(t.startswith("[IMAGING_IMG]: ") for t in DATA["strings"].values())


def test_doce_cargas_repartidas_en_tres_funciones():
    assert DATA["pic_refs"] == len(DATA["refs"]) == 12
    funcs = [r["function"] for r in DATA["refs"]]
    assert sorted(set(funcs)) == sorted(DATA["functions"].values()) and all(funcs.count(f) == 4 for f in set(funcs))


def test_dos_rutas_de_log():
    assert DATA["logger_calls"] == ["0x4381b9d0", "0x43902718"]


def test_llamadores_directos():
    c = DATA["callers"]
    assert [len(c[k]) for k in ("Image::Clone", "Image::Branch", "Image::Create")] == [10, 26, 7]
    assert sum(r["function"] is None for rows in c.values() for r in rows) == 8
    assert len({r["function"] for rows in c.values() for r in rows} - {None}) == 30
