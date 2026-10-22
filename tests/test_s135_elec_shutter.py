"""Tests for S135 — el subsistema `ElecShutter` del A6300 como control positivo."""

import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300 = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)


def _data(path):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=160):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


class TestControlPositivoEnElA6300:
    def test_el_a6300_tiene_el_modulo_elecshutter(self):
        a6300 = _data(A6300)
        assert a6300.count(b"ElecShutter") == 4
        assert _cstr(a6300, 0x43DCFA41) == "ElecShutter/EC_ElecShutter_Main.cpp"
        assert _cstr(a6300, 0x43DCFA65) == (
            "ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp")

    def test_los_ajustes_de_obturador_electronico_del_a6300(self):
        a6300 = _data(A6300)
        assert _cstr(a6300, 0x43DC4F43) == "SET Silent Shutter Type: %d"
        assert "SilentShutterMode" in _cstr(a6300, 0x43DC9A14)
        assert _cstr(a6300, 0x43DCA61F).endswith("[shutterType] cur:%d req:%d")
        assert _cstr(a6300, 0x43DC821D).endswith("[front_eshutter] cur:%d req:%d")
        assert _cstr(a6300, 0x43DCA9AD) == "CheckSetSilentShutterMode"
        assert _cstr(a6300, 0x43DCB09C) == "CheckSetShutterType"

    def test_la_tabla_de_velocidades_no_lineales(self):
        a6300 = _data(A6300)
        # justo detras del nombre del fichero: tabla de codigos de velocidad
        off = 0x43DCFA9E - BASE_VADDR
        tabla = a6300[off:off + 28]
        assert tabla == bytes([0x00, 0x01, 0x03, 0x04, 0x05, 0x06, 0x08, 0x09,
                               0x0A, 0x0B, 0x0D, 0x0E, 0x0F, 0x10, 0x12, 0x13,
                               0x14, 0x16, 0x17, 0x18, 0x19, 0x1B, 0x1C, 0x1D,
                               0x1E, 0x1F, 0x21, 0x22])


class TestAusenciaEnA6000YA7S:
    @pytest.mark.parametrize("termino", [
        b"ElecShutter", b"EC_ElecShutter", b"EC_NonlinearElecShutter",
        b"ElecShutter_Main", b"MechShutterTable", b"SilentShutterMode",
        b"CheckSetSilentShutterMode", b"front_eshutter", b"CheckSetFrontEshutter",
        b"shutterType", b"CheckSetShutterType", b"efcs", b"EFCS",
        b"electronic", b"curtain", b"mechanical", b"flicker", b"silent",
    ])
    def test_termino_ausente(self, termino):
        assert _data(A6000).count(termino) == 0, termino
        assert _data(A7S).count(termino) == 0, termino

    def test_la_unica_coincidencia_de_la_a7s_es_el_diagnostico_conocido(self):
        a7s = _data(A7S)
        assert a7s.count(b"SET Silent Shutter Type") == 1
        assert _cstr(a7s, 0x43CA4B6B) == "SET Silent Shutter Type: %d"
        # y es un diagnostico del convertidor, no un modulo
        assert b"ElecShutter" not in a7s

    def test_la_a6000_no_tiene_el_ajuste_ni_su_diagnostico(self):
        assert _data(A6000).count(b"SET Silent Shutter Type") == 0


class TestLaA6000SiTieneElMotorEC:
    def test_el_motor_de_exposicion_esta_presente(self):
        a6000 = _data(A6000)
        assert _cstr(a6000, 0x43CA91CE) == "EC::EcTagData"
        assert _cstr(a6000, 0x43CA9227) == "EC::EcEncryptedTagData"
        assert b"api_EC_GetApolloLapNum" in a6000

    def test_las_apariciones_de_shutter_de_la_a6000_son_del_obturador_mecanico(self):
        a6000 = _data(A6000)
        assert a6000.count(b"shutter") == 7
        assert a6000.count(b"Shutter") == 8
        assert b"ShutterMuteOffExecutor" in a6000
        assert b"[SFRS][PINSEND] shutter mute thru" in a6000
        assert b"[VPH_API]<shutter_mute_param>" in a6000
