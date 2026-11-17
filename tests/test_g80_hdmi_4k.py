"""G80 — Salida HDMI 4K: la A6000 3.21 trae de fábrica la reproducción de fotos en 4K por HDMI (QFHD); no hay vídeo 4K que sacar."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
USR = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked"
pytestmark = pytest.mark.skipif(not USR.exists(), reason="extracción no disponible")


def test_reproduccion_4k_de_fabrica():
    assert b"cmnViewSettingNodeRootOutput4kMode" in (USR / "lib/CautionConfig.so").read_bytes()
    assert b"handle_set_resolution : hd:0x%x sd:0x%x qfhd:0x%x" in (USR / "lib/libInfraHdmi.so").read_bytes()
    lo = (USR / "lib/libObj.so").read_bytes()
    assert b"PRM_APP_HDMI_RESO_QFHD" in lo and b"MID_RENDERER_SET_PATH_QFHD_THROUGH_RESIZE" in lo
    assert b"4K Still Image PB" in (USR / "share/app/string_english.uxc").read_bytes()
