"""E26-R20 — tabla de decisiones del selector del BootROM (`FUN_ffff1062`), por emulación con auxiliares sustituidas."""

import importlib
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))
pytest.importorskip("unicorn")
R20 = importlib.import_module("r20_bootrom_selector")
pytestmark = pytest.mark.skipif(not R20.ROM.exists(), reason="bootrom.bin ausente")


def fin(**kw):
    return R20.run(**kw)[1]


def test_literales_del_selector():
    rom = R20.ROM.read_bytes()
    assert (
        struct.unpack_from("<I", rom, 0x12C0)[0] == 0xF2915000
    )  # MODEREG base (+0x10)
    assert struct.unpack_from("<I", rom, 0x12C4)[0] == 0xF2910410  # GPIO(4,RDATA)


def test_bit0_cero_arranque_normal():
    assert fin(modereg_bit0=0) == "jump_loader2"
    assert fin(modereg_bit0=0, storage_init=0x1003) == "error_led"


def test_bit0_uno_siempre_acaba_en_ruta_de_servicio():
    assert fin(modereg_bit0=1, gpio_bit22=1) == "serial_boot"
    for fallo in ({"storage_init": 0x1003}, {"load_header": 0x1006}, {"find_key": 1}):
        assert fin(modereg_bit0=1, **fallo) == "serial_boot"


def test_clave():
    base = {"modereg_bit0": 1, "find_key": 0, "rx_packet": 0}
    assert fin(**base, clave=0x1234, recibida=0x1234) == "serial_boot"
    assert fin(**base, clave=0x1234, recibida=0x4321) == "error_led"
    assert fin(**base, crc_key=0, clave=0x1234, recibida=0x1234) == "error_led"
    assert fin(modereg_bit0=1, find_key=0, rx_packet=0x3001) == "jump_ram"
