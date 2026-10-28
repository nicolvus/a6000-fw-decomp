"""E25-19b (tramo final): motor Run(M), argumento del thunk y cap en vuelo, por bytes de av-cam.bin y evidencia física."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_19b_ciclo import tbb, tbh, wrappers
from e25_19b_dis import BIN, dis

pytestmark = pytest.mark.skipif(not BIN.exists(), reason="falta av-cam.bin")


def first(addr: int) -> str:
    return dis(BIN.read_bytes(), addr, 4)[0].split(": ", 1)[1]


def test_run_pasa_m_como_r1_al_thunk():
    d = "\n".join(dis(BIN.read_bytes(), 0x43B047D0, 0x1C))
    assert (
        "add.w r0, r0, #8" in d and "mov r1, r4" in d and "bl #0x43b047aa" in d
    )  # functor=M+8, r1=M
    assert first(0x43AFB3BC) == "ldr r3, [r0, #8]"  # thunk: handler=[functor+8]
    assert tbb(BIN.read_bytes(), 0x43B047F0, 7) == [
        0x43B047F8,
        0x43B0480A,
        0x43B04804,
        0x43B04840,
        0x43B0483A,
        0x43B04816,
        0x43B04840,
    ]


def test_cap_es_el_primer_campo_de_m_y_lo_fija_la_creacion():
    assert first(0x43AE75DC) == "ldr r0, [r0]"
    assert (
        first(0x4381BB12) == "str.w r8, [r0]"
    )  # 0x4381ba9c(plantilla, copia_de_cap): [M] = 2.º argumento


def test_subestado_9_y_espera_infinita():
    sub = tbh(BIN.read_bytes(), 0x43B1B034, 12)
    assert sub[9] == 0x43B1B0A6 and sub[2] == 0x43B1B060
    assert first(0x43B1B0A6 + 6) == "b.w #0x438c289c"
    assert "bl #0x438d08e8" in "\n".join(dis(BIN.read_bytes(), 0x438C289C, 0x20))
    d = "\n".join(dis(BIN.read_bytes(), 0x437DBA2E, 0x10))
    assert "mov.w r2, #-1" in d and "bl #0x43561260" in d  # osal_rcv_msg_tmo sin límite
    assert wrappers(BIN.read_bytes())[0x43560E04] == "ref_flg"


def test_complete_solo_desde_avance_y_fin():
    from e25_19b_callers import callers

    c = callers(BIN.read_bytes(), {0x437E611C, 0x437E56EC})
    assert c[0x437E611C] == [0x437E5638, 0x437E577A] and c[0x437E56EC] == [
        0x437E5822,
        0x437E5934,
    ]


def test_evidencia_cap_en_vuelo():
    f = ROOT / "analysis/e25-19b/cap-4s.json"
    if not f.exists():
        pytest.skip("sin evidencia física")
    d = json.loads(f.read_text())
    vivo = [m for m in d["muestras"] if "cap" in m]
    assert vivo and d["originales_ok_final"]
    assert {m["cap"]["phys"] for m in vivo} == {"0x952db580"}
    c = vivo[0]["cap"]["campos"]
    assert (
        c["shd_svd_modo@0x64c"][:8] == "01000000"
        and c["shd_svd_modo@0x64c"][8:16] == "00000000"
    )  # shd=1, svd=0
    assert c["shd_svd_modo@0x64c"][18:20] == "03"  # ShutMode=3 en cap+0x655
    assert c["tim56c_570@0x56c"] == "6003000050100000"  # 864 y 4176
