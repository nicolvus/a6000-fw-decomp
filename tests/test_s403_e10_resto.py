"""E10 (resto): escritores de EffectInternalMode=1, StsId de las filas YC y liberación en StillConverter; contra e10_resto.json."""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e10_resto.json").read_text())


def test_fader_end_writer_is_created_only_by_movie_rec_factory():
    callers = DATA["escritores"]["0x154990"]["clases_llamadoras"]
    assert callers["0x153fb4"] == ["OBJEFFECT::ExecCmdFactoryComponentMovieRec"]


def test_deliver_base_writer_is_reached_only_through_playback_edit_subclasses():
    callers = set(DATA["escritores"]["0x1e069c"]["clases_llamadoras"]["0x1e0340"])
    assert callers == {f"OBJEFFECT::SequencePinDeliver{n}" for n in ("BigImageOpen", "SplitResizeImage", "StillEditBase", "VgaCache")}


def test_yc_rows_are_the_only_stsid_6_and_no_shooting_model_uses_it():
    sts = DATA["StsId"]
    assert sts["filas_con_StsId_6"] == ["0x2a", "0xb4"]
    assert all(6 not in v for v in sts["StsId_por_modelo_de_disparo"].values())


def test_still_converter_frees_its_own_work_memory():
    assert len(DATA["StillConverter_libera"]) >= 8
