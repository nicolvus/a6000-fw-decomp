"""S632: sufijos [MODE_*] de «CamCore acquire Error» y [MODEFLG] (A6000 fw3.21)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis/s632_mode"))
import verify_mode as V

D = V.build()
SUF = {"MODE_CAP_DRP": 14, "MODE_CAP_PREREVIEW": 15, "MODE_CAP": 17, "MODE_CAP_SNR": 3, "MODE_SNR_BUS_THROUGH": 12,
       "MODE_CAP_SNR_PREREVIEW": 11, "MODE_SNR_BUS_THROUGH_PREREVIEW": 13}


def test_siete_sufijos_en_una_funcion():
    assert {r["sufijo"]: r["ramas"][0]["consts"]["acquire"]["r1"] for r in D["strings"]} == SUF
    assert D["funciones"] == ["0x437f5a04"] and sum(len(r["sitios"]) for r in D["strings"]) == 11
    assert all("0x43ae82e4" in [x[1] for x in r["ramas"][0]["bls"]] and r["ramas"][0]["bls"][-1][1] == "0x437f5414" for r in D["strings"])


def test_sin_obturador_y_modeflg():
    assert D["alcance_obturador"] == {"0x437f5a04": []}
    assert D["mode_flg"]["funcion"] == "0x439012d0" and D["mode_flg"]["a7s"] == 0 and D["mode_flg"]["a6300"] == 0


def test_json_versionado_coincide():
    assert json.loads((ROOT / "analysis/s632_mode/mode.json").read_text()) == json.loads(json.dumps(D))
