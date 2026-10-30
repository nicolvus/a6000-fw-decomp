"""E26-R11 — pruebas automáticas de reconstrucción del pinout BootROM UART.

Pruebas offline y sintéticas. Validan la reconstrucción del pinout desde el
esquema del manual de servicio. No tocan la cámara, no transmiten paquetes,
no realizan operaciones físicas.

Informe: docs/capture/e26-r11-bootrom-uart-physical-access.md
"""

import sys

import pytest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))

r11 = __import__("r11-pinout-reconstruction")


# ------------------------------------------------------------------ pin map

def test_cn4001_pin9_is_uart_rx_boot_in():
    assert r11.CN4001_PINS[9] == "UART_RX/BOOT_IN"


def test_cn4001_pin8_is_uart_tx():
    assert r11.CN4001_PINS[8] == "UART_TX/LANC_SIG"


def test_cn4906_pin9_is_tdo_not_uart():
    """Advertencia crítica: CN4906 pin 9 = TDO, no UART_RX/BOOT_IN."""
    assert r11.CN4906_PINS[9] == "TDO"
    assert r11.CN4906_PIN_9 != r11.CN4001_PIN_9


def test_cn4906_pin4_is_uart_rxd_mss():
    assert r11.CN4906_PINS[4] == "UART_RXD_MSS"


def test_cn4906_pin5_is_uart_txd_mss():
    assert r11.CN4906_PINS[5] == "UART_TXD_MSS"


# ------------------------------------------------------------ resistors XX

def test_r4002_and_r4003_are_xx():
    assert "R4002" in r11.RESISTORS_XX
    assert "R4003" in r11.RESISTORS_XX


def test_r6004_is_xx():
    assert "R6004" in r11.RESISTORS_XX


# ----------------------------------------------------- connection map

def test_connection_map_has_expected_references():
    conns = r11.build_connection_map()
    refs = {c.reference for c in conns}
    assert "R4003" in refs
    assert "R4002" in refs
    assert "CN4001 (Multi Terminal)" in refs
    assert "CN4906 (servicio SIDE A)" in refs
    assert "BIONZ IC6000" in refs


def test_connection_map_certainty_levels():
    conns = r11.build_connection_map()
    for c in conns:
        assert c.certainty in ("ALTA", "MEDIA", "BAJA")
        assert c.mounting_status in ("montado", "no_montado_XX", "desconocido")


def test_r4003_is_no_mount():
    conns = r11.build_connection_map()
    r4003 = [c for c in conns if c.reference == "R4003"]
    assert len(r4003) == 1
    assert r4003[0].mounting_status == "no_montado_XX"


def test_r4002_is_no_mount():
    conns = r11.build_connection_map()
    r4002 = [c for c in conns if c.reference == "R4002"]
    assert len(r4002) == 1
    assert r4002[0].mounting_status == "no_montado_XX"


# ---------------------------------------------------- route interruption

def test_route_boot_serial_in_to_cn4001_pin9_is_interrupted():
    conns = r11.build_connection_map()
    assert r11.is_route_interrupted(conns) is True


# ---------------------------------------------------- schematic validation

def test_reconstruct_synthetic_schematic_no_errors():
    synthetic = """
    DEBUG_UART0_TXD   CM4008    8    UART_TX/LANC_SIG    MULTI
    R4002   XX
    DEBUG_UART0_RXD   9    UART_RX/BOOT_IN
             R4003        XX
    BOOT_SERIAL_IN    CM4002    10     AD_JACK_IN
    XX MARK: NO MOUNT
    """
    result = r11.reconstruct_from_schematic_text(synthetic)
    assert len(result.errors) == 0
    assert len(result.warnings) >= 1


def test_reconstruct_missing_xx_warning():
    schematic = """
    DEBUG_UART0_TXD   CM4008    8    UART_TX/LANC_SIG    MULTI
    DEBUG_UART0_RXD   9    UART_RX/BOOT_IN
    """
    result = r11.reconstruct_from_schematic_text(schematic)
    assert any("XX" in w for w in result.warnings) or any("XX" in e for e in result.errors)


# ---------------------------------------------------- return codes

if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))