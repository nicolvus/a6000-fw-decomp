"""E18: registros DFE que lee `[LGA]` GetDfeDrvParam (0x4389b320); contra e18_dfe_param.json."""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e18_dfe_param.json").read_text())
STATIC = {r["id"]: r for r in DATA["ids"] if "suma" in r}


def test_fixed_id_0xb_sums_to_0xfc0():
    assert (STATIC[0xB]["registro"], STATIC[0xB]["campos"], STATIC[0xB]["suma"]) == ("0x43bb92b4", [4, 4, 4024], 0xFC0)


def test_static_record_coverage_is_declared():
    assert (len(DATA["ids"]), len(STATIC)) == (69, 13)  # los demás ids no pasan por los siete registros estáticos
    assert {r["suma"] for r in STATIC.values()} == {0x23E, 0x2C4, 0x326, 0x474, 0xEC, 0xFC0}
