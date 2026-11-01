"""3.25c (experimental): la evidencia versionada demuestra que se corrigió cada causa del bloqueo del 3.25.

En CI (sin firmware) se comprueba `analysis/e25-27/verify-325c.json`; con los artefactos locales se
vuelve a ejecutar el verificador completo y se exige el mismo resultado.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

EVIDENCE = ROOT / "analysis/e25-27/verify-325c.json"
DAT_SHA = "d64ad6e3d203dfafae020fc777ae8e9fe4a77c49f1f469cf5b907a1a6a477752"


def _check(report: dict) -> None:
    assert report["todo_ok"] is True
    assert all(report["comprobaciones"].values())
    assert report["dat_sha256"] == DAT_SHA
    emu = report["emulacion"]
    assert emu["corregida_3.25c"] == {"entradas": 369, "fallos": 0, "avisos_residuo": 0, "primer_fallo": None}
    assert emu["sony_3.21"]["fallos"] == 0
    assert emu["bloqueo_3.25"]["fallos"] == 361 and emu["bloqueo_3.25"]["primer_fallo"] == 0
    lay = report["disposicion"]
    assert lay["corregida"]["max_sectores_por_bloque"] <= lay["sony_3.21"]["max_sectores_por_bloque"] == 126
    assert lay["bloqueo_3.25"]["offsets_no_alineados_512"] == 359


def test_evidencia_versionada():
    _check(json.loads(EVIDENCE.read_text(encoding="utf-8")))


def test_verificador_completo_si_hay_artefactos():
    from e25_27 import verify_325c as V

    if not (V.DAT.is_file() and V.BRICK_DAT.is_file() and V.R39.BL.is_file()):
        pytest.skip("faltan el .dat 3.25c, el 3.25 que bloqueó o bootloader.bin (no versionados)")
    pytest.importorskip("unicorn")
    _check(V.run())
