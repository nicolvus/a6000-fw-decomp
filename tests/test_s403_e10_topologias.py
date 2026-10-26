"""E10: quién crea las filas de topología que llevan YC o STILL_DATA al ObjStillRecorder; contra e10_topologias.json."""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e10_topologias.json").read_text())
SHOOTING = {"ModelStillRec", "ModelBootEE", "ModelMovieRec", "ModelCamera", "ModelScalarCameraPatch"}


def classes_with(row_id: str) -> set[str | None]:
    return {e["clase"] for e in DATA["listas_estaticas_con_ids_de_interes"] if row_id in e["lista"]}


def test_row_2a_is_created_only_by_edit_models():
    assert classes_with("0x2a") == {"ModelBeautyEffect", "ModelFocusRevision", "ModelPaint", "ModelRedEye",
                                    "ModelRetouchArtFilter", "ModelTrimming"}
    assert not SHOOTING & classes_with("0x2a")


def test_still_recorder_lists_use_still_data_not_yc():
    lists = {tuple(e["lista"]) for e in DATA["listas_estaticas_con_ids_de_interes"] if e["clase"] == "ModelStillRec"}
    assert ("0xb0", "0xb1", "0x10", "0x0") in lists and ("0x8", "0x10", "0x0") in lists
    assert not any("0x2a" in x or "0xb4" in x for x in lists)


def test_census_coverage_is_declared():
    assert (DATA["sitios"], DATA["con_lista"]) == (300, 149)  # el resto: listas en heap o en otro marco (no resueltas)
    assert not [r for r in DATA["filas"] if r["lista"] and "0xb4" in r["lista"]]
