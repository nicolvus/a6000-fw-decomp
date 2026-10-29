"""E25-26 — C3-B: parche, emulación end-to-end y tabla de velocidades (offline)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in ("scripts", "scripts/e25_18", "scripts/e25_16", "scripts/e25_17"):
    sys.path.insert(0, str(ROOT / p))

pytest.importorskip("unicorn")
pytest.importorskip("capstone")

from e25_24 import patch_bionz as PB
from e25_26 import emu
from e25_26 import patch_c3b as PC

AV_CAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
EVID26 = ROOT / "analysis/e25-26/evidence.json"
RAPIDAS = {"1/8000": 1 / 8000, "1/4000": 1 / 4000, "1/1000": 1 / 1000,
           "1/250": 1 / 250, "1/125": 1 / 125, "1/60": 1 / 60, "1/30": 1 / 30}


@pytest.fixture(scope="module")
def image() -> PB.BionzImage:
    if not AV_CAM.is_file():
        pytest.skip("falta av-cam.bin")
    return PB.BionzImage.load(AV_CAM)


@pytest.fixture(scope="module")
def selector(image) -> bytes:
    return PB.apply_bytes(image.data)[0]


@pytest.fixture(scope="module")
def combined(selector) -> bytes:
    return PC.apply_bytes(selector)[0]


# --------------------------------------------------------------------- parche


def test_hook_y_cueva_bytes(image, selector, combined):
    assert image.data[PC.HOOK - PB.BASE:PC.HOOK - PB.BASE + 4] == PC.HOOK_OLD
    out, diff = PC.apply_bytes(selector)
    assert out == combined and diff
    assert all(d["address"] in PC.allowed_addresses() for d in diff)
    assert combined[PC.HOOK - PB.BASE:PC.HOOK - PB.BASE + 4] == PC.hook_bytes()


def test_reversion_exacta(image, selector, combined):
    back = PC.restore_bytes(combined)
    assert back == selector
    back = PB.restore_bytes(back)
    assert back == image.data
    assert hashlib.sha256(back).hexdigest() == PC.SHA256_ORIGINAL


def test_no_escribe_fuera_de_cap(selector):
    _, diff = PC.apply_bytes(selector)
    allowed = PC.allowed_addresses()
    assert {d["address"] for d in diff} <= allowed
    assert all(PC.CAVE <= d["address"] < PC.CAVE + PC.CAVE_LEN or
               PC.HOOK <= d["address"] < PC.HOOK + 4 for d in diff)


# --------------------------------------------------------------------- emulación


def test_matriz_completa(combined):
    m = emu.matrix(combined)
    assert m["efcs_identical"] is True
    assert m["errors_identical"] is True
    assert m["electronic_normalized"] is True
    assert m["electronic_pred1"]["combined"]["shd_a_SetExposure"] == 4203
    assert m["electronic_pred1"]["combined"]["svd_a_SetExposure"] == 0
    assert m["electronic_pred1"]["combined"]["shutmode_a_SetExposure"] == 0
    assert m["electronic_pred1"]["original"]["shd_a_SetExposure"] == 8422
    assert m["electronic_long"]["combined"]["svd_a_SetExposure"] == 2
    assert m["electronic_long"]["combined"]["shutmode_a_SetExposure"] == 3
    assert m["alternation"] == [
        {"flag": 0, "shd": 8422, "svd": 1, "shutmode": 3},
        {"flag": 1, "shd": 4203, "svd": 0, "shutmode": 0},
        {"flag": 0, "shd": 8422, "svd": 1, "shutmode": 3},
        {"flag": 1, "shd": 4203, "svd": 0, "shutmode": 0},
    ]


def test_efcs_conserva_el_plan_nativo(combined):
    for cap504 in (0, 1):
        orig = emu.baseline(flag=0, shd=8422, svd=1, shutmode=3, cap504=cap504)
        comb = emu.run(combined, flag=0, shd=8422, svd=1, shutmode=3, cap504=cap504)
        assert emu.equivalent(orig, comb)
        assert comb["shd_a_SetExposure"] == 8422
        assert comb["shutmode_a_SetExposure"] == 3
        assert comb["cap_650_final"] == 1


def test_errores_no_cambian_nada(combined):
    for kw in ({"flag": 2, "shd": 8422, "svd": 1, "shutmode": 3},
               {"flag": 1, "shd": 8422, "svd": 1, "shutmode": 3, "vts": 0},
               {"flag": 1, "shd": 100, "svd": 1, "shutmode": 3, "vts": 4219}):
        assert emu.equivalent(emu.baseline(**kw), emu.run(combined, **kw))


def test_tabla_de_velocidades(combined):
    import silent_plan as P
    for name, t in RAPIDAS.items():
        tv = P.tv_code(t)
        nat = P.productor(tv, P.PERIODO_Q8, P.VTS_MEDIDO, 1, 1, 1)
        r = emu.run(combined, flag=1, shd=nat["shd"], svd=nat["svd"], shutmode=3)
        expected = nat["shd"] - P.VTS_MEDIDO if nat["svd"] == 1 else nat["shd"]
        assert r["shd_a_SetExposure"] == expected, name
        assert r["svd_a_SetExposure"] == 0 and r["shutmode_a_SetExposure"] == 0
        exp_us = (P.VTS_MEDIDO - expected) * P.PERIODO_Q8 / 256
        assert abs(exp_us / (t * 1e6) - 1) < 0.05, name


def test_evidencia_e25_26(combined):
    if not EVID26.is_file():
        pytest.skip("falta analysis/e25-26/evidence.json")
    ev = json.loads(EVID26.read_text())
    assert ev["phase"] == "E25-26" and ev["installable"] is False
    assert ev["restore_ok"] is True
    assert ev["cave"]["address"] == hex(PC.CAVE)
    assert ev["combined_sha256"] == PC.sha256(combined)
    assert ev["emulation"]["efcs_identical"] is True
    assert ev["speeds"]["1/4000"]["pred1"]["c3b_shd"] == 4203
    assert ev["speeds"]["1/8000"]["pred1"]["c3b_shd"] == 4211


def test_origen_de_vts_y_modalidad_en_cap(image):
    """cap+0x5e0 = descriptor+6 (VTS) y cap+0x41c = global+0x210 (modalidad)."""
    import capstone

    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    data = image.data
    vts = [(i.mnemonic, i.op_str) for i in md.disasm(data[0x43846E00 - PB.BASE:0x43846E16 - PB.BASE], 0x43846E00)]
    assert ("ldrh", "r3, [r3, #6]") in vts
    assert ("strh.w", "r3, [r4, #0x5e0]") in vts
    mod = [(i.mnemonic, i.op_str) for i in md.disasm(data[0x43845F2E - PB.BASE:0x43845F38 - PB.BASE], 0x43845F2E)]
    assert ("ldr.w", "r2, [r3, #0x210]") in mod
    assert ("str.w", "r2, [r4, #0x41c]") in mod
