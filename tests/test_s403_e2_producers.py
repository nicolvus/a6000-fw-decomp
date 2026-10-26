"""E2: productores de ObjMsg(grupo, 0x10000005) en libObj; contra e2_producers.json."""
import json
from pathlib import Path

SITES = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e2_producers.json").read_text())


def test_only_two_sites_publish_to_a_queue():
    ctor = [s for s in SITES if s["grupo"]]
    assert [s["ldr"] for s in ctor] == ["0x838e66", "0x90868a", "0x919f4a", "0x91c214"]
    assert [s["ldr"] for s in ctor if s["publica_en_cola"]] == ["0x838e66", "0x91c214"]
    assert {s["grupo"] for s in ctor} == {"r1, #0x3700", "r1, #0x3500", "r1, #0x3a48"}
