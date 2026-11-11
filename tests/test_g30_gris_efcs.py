"""G30: EFCS (pid 0x46) en gris con Silent On — `CmnViewProcessDataMgr::isGrayedOut` de la copia de viewUnified2 pasa por un tramo nuevo (código real emulado con unicorn;
solo se simula `CmnViewProcessDataMgr::getValue(pid, int&)`)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "tests"))
pytest.importorskip("unicorn")
pytest.importorskip("keystone")
import pid_space as S
from test_g28_pid_space import AJ, BASE, LIB, _cargar, _llamar, needs
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_LR


@pytest.fixture(scope="module")
def img():
    if not LIB.is_file():
        pytest.skip("viewUnified2.so de Sony ausente")
    return S.patch(LIB.read_bytes(), AJ, gris_efcs=True)


def _correr(img, pid, silent_idx):
    uc = _cargar(img)
    llamadas = []

    def hook(u, addr, size, _):
        if addr == BASE + S.GET_VALUE_VU2:                          # getValue(mgr, pid, &out): out = índice de la opción de Silent
            llamadas.append((u.reg_read(UC_ARM_REG_R0), u.reg_read(UC_ARM_REG_R1)))
            u.mem_write(u.reg_read(UC_ARM_REG_R2), struct.pack("<I", silent_idx))
            u.reg_write(UC_ARM_REG_R0, 1)
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR) | 1)
        if addr == BASE + S.SITIO_GRIS[0] + 4:                      # llegó al resto del isGrayedOut original
            llamadas.append("original")
            u.reg_write(UC_ARM_REG_R0, 0x77)
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR) | 1)

    r = _llamar(uc, S.SITIO_GRIS[0], 0x20000100, pid, hooks=hook)
    return r, llamadas


@needs
def test_efcs_en_gris_solo_con_silent_on(img):
    assert _correr(img, 0x46, 1)[0] == 1 and _correr(img, 0x46, 0)[0] == 0
    assert _correr(img, 0x46, 1)[1] == [(0x20000100, 0x12)]          # consulta el pid de Silent sobre el mismo gestor


@needs
def test_los_demas_pids_siguen_el_camino_original(img):
    for pid in (0x12, 0x10, 0xE0):
        r, ll = _correr(img, pid, 1)
        assert ll == ["original"] and r == 0x77


@needs
def test_sin_la_opcion_el_gestor_queda_intacto():
    d = LIB.read_bytes()
    assert S.patch(d, AJ)[S.SITIO_GRIS[0]:S.SITIO_GRIS[0] + 4] == S.SITIO_GRIS[1]
