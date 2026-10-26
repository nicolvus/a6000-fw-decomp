"""build_pages_status: agrupación de etiquetas por familia (sin tocar site/)."""
import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("bps", Path(__file__).resolve().parents[1] / "scripts/build_pages_status.py")
bps = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bps)


def test_families_groups_three_or_more_and_sends_the_rest_to_otros():
    detail = {f"[CAM_{n}]": {"estado": "hito", "hitos": []} for n in "ABC"} | {"[X_1]": {"estado": "hito", "hitos": []}}
    fams = dict(bps.families(detail))
    assert [lab for lab, _ in fams["CAM"]] == ["[CAM_A]", "[CAM_B]", "[CAM_C]"]
    assert [lab for lab, _ in fams["OTROS"]] == ["[X_1]"]


def test_tip_lists_sessions_and_names():
    info = {"estado": "hito", "hitos": ["12"]}
    assert bps.tip("[A]", info, {"12": "Tema"}) == "[A]: hito S12 — Tema"
