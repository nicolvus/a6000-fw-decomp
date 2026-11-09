"""G22: simulación de la cadena completa de «Silent Shooting» con el código real emulado (unicorn): elemento `Normal` →
`libObj` → paquete LIRO → `av-cam`. Solo las fronteras (ParamList/PrmNumber, ObjMsg/ObjIf, contenedores) son modelos Python."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
pytest.importorskip("unicorn")
from g22.sim.camera import Camera

G = ROOT / "analysis/gui/g22"
OBJ59, CMN59 = (
    G / "files-359/lib/libObj.so",
    G / "files-359/lib/cmn_view_processDataMgr.so",
)
OBJ_SONY = (
    ROOT
    / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
)
CMN58 = G / "files-358/lib/cmn_view_processDataMgr.so"
AV = ROOT / "analysis/rea-independent/input/av-cam.bin"
needs = pytest.mark.skipif(
    not all(p.is_file() for p in (OBJ59, CMN59, OBJ_SONY, CMN58, AV)),
    reason="faltan binarios",
)


@needs
def test_3_59_elegir_on_off_llega_a_av_cam_y_se_refleja_en_el_menu():
    c = Camera(OBJ59, CMN59, AV)
    assert (
        c.cmn.get_value() is None
    )  # contenedor a 0: el menú no sabe el valor actual hasta el primer SET
    for idx, byte in ((1, 1), (0, 0), (1, 1)):
        c.cmn.set_value(idx)
        assert c.requests[-1] == ("@M00F", 0x5B, {0x291: idx + 1})
        assert c.packets[-1] == bytes.fromhex("0500e34000000000") + bytes([byte])
        assert c.av.state(0x238) == byte and c.av.state(0x210) == 0
        assert c.cmn.get_value() == idx


@needs
def test_3_58_la_escritura_llega_pero_el_menu_no_lo_refleja():
    c = Camera(OBJ_SONY, CMN58, AV)
    c.cmn.set_value(1)
    assert (
        c.av.state(0x238) == 1 and c.cmn.get_value() is None
    )  # síntoma observado con el 3.58 (fijo en Off)


@needs
def test_contenedor_inicial_off_da_valor_valido_desde_el_arranque():
    c = Camera(OBJ59, CMN59, AV, init_elems=(1, 1))
    assert c.cmn.get_value() == 0


@needs
def test_control_efcs_pid_0x46_mueve_0x210_no_0x238():
    c = Camera(OBJ59, CMN59, AV, pid=0x46)
    c.cmn.set_value(1)
    assert (
        c.requests[-1] == ("@M00F", 0x54, {0x246: 2})
        and c.av.state(0x210) == 1
        and c.av.state(0x238) == 0
    )
