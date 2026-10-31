#!/usr/bin/env python3
"""E26-R11 — Reconstrucción del pinout del BootROM UART desde el esquema del manual de servicio Sony A6000.

Extrae y valida las conexiones documentadas en el texto extraído del esquema
(página 38, SY-1028 BOARD):
  * CN4001 = conector Multi Terminal externo
  * CN4906 = huella de servicio interna (SIDE A)
  * R4002 / R4003 = resistencias de 0 Ω candidatas, ambas marcadas XX (no montadas)
  * BOOT_SERIAL_IN = señal de recepción del BootROM (BIONZ IC6000 pin H21)

OFFLINE ONLY.  No abre, envía ni comunica con hardware real.
"""

import re
from dataclasses import dataclass, field

# ── Esquemas conocidos (extraídos del manual de servicio) ───────────────────

# CN4001 — Multi Terminal, PDF página 37 del manual (corregido en E26-R29: la
# versión anterior desplazaba el pin 1 y omitía el pin 3; ver docs/capture/
# e26-r29-pinout-cn4001-cn4906-completo.md §1).
CN4001_PINS: dict[int, str] = {
    1: "USB_VBUS",
    2: "USB_D-",
    3: "USB_D+",
    4: "USB_ID",
    5: "GND",
    6: "D_3.1V/LANC_DC",
    7: "XRESET_REQ",
    8: "UART_TX/LANC_SIG",
    9: "UART_RX/BOOT_IN",
    10: "AD_JACK_IN",
    11: "ROUT/XAELOCK",
    12: "LOUT/XSHUT",
    13: "VIDEO",
    14: "AV_GND",
    15: "XPWR_ON",
    16: "REG_GND",  # 16-19: masa/blindaje vía D4001 (XX, no montado)
    17: "REG_GND",
    18: "REG_GND",
    19: "REG_GND",
}

# CN4906 — huella de servicio SIDE A, PDF página 38 del manual (corregido en
# E26-R29: es un conector de 18 pines; los antiguos «31/32» pertenecían a OTRO
# conector de la misma hoja —el flex del panel superior, XS_1/XS_2 del botón
# disparador, ver s21-claude-button-to-shutter-order.md— no a CN4906).
CN4906_PINS: dict[int, str] = {
    1: "REG_GND",
    2: "BOOT_MODE_1",
    3: "EVER_3.15V",
    4: "UART_RXD_MSS",
    5: "UART_TXD_MSS",
    6: "UART_RXD_DWN",
    7: "UART_TXD_DWN",
    8: "NSRST",
    9: "TDO",
    10: "RTCK",
    11: "TCK(SWCLK)",
    12: "TMS(SWDIO)",
    13: "TDI",
    14: "NTRST",
    15: "DEBUG_MODE",
    16: "REG_GND",
    17: "REG_GND",  # sin etiqueta propia en el esquema; une al bus de masa
    18: "REG_GND",
}

# CN4906 — origen interno de cada pin, trazado por coordenadas de píxel sobre
# el esquema vectorial (E26-R29; ver informe para el método). Confirma que
# CN4906 es un conector combinado BIONZ+Darwin: los pines 11/12/15 unen (con
# un punto de conexión visible en el esquema) la vía de servicio de BIONZ
# (SWCLK/SWDIO/VIO_FLD, resistencias R4911/12/13 XX) con el bus de depuración
# "DWN" de Darwin (IC5700). El pin 10 (RTCK) no tiene red externa.
CN4906_SOURCES: dict[int, tuple[str, str]] = {
    2: ("FIQ (R4910, XX)", "ALTA"),
    3: ("EVER_3.15V (vía CL4910/CL4911)", "ALTA"),
    4: ("DEBUG_UART0_RXD", "ALTA"),
    5: ("DEBUG_UART0_TXD", "ALTA"),
    6: ("DWN_UART_RXD", "ALTA"),
    7: ("DWN_UART_TXD", "ALTA"),
    8: ("MD0_DWN", "MEDIA"),
    9: ("TDO_DWN", "ALTA"),
    10: ("(sin red externa)", "ALTA"),
    11: ("SWCLK (R4911, XX) + TCK_DWN (unidos)", "ALTA"),
    12: ("SWDIO (R4912, XX) + TMS_DWN (unidos)", "ALTA"),
    13: ("TDI_DWN", "ALTA"),
    14: ("TRST_DWN", "ALTA"),
    15: ("VIO_FLD (R4913, XX) + XDWN_RESET (unidos)", "ALTA"),
}

# Resistencias candidatas en la ruta BOOT_SERIAL_IN (ambas XX = no montadas)
RESISTORS_XX = {"R4002", "R4003", "R4004", "R6004"}

# Conexiones documentadas en el esquema (origen → [intermedios] → destino)
BOOT_SERIAL_IN_ROUTE = {
    "origin": "BIONZ IC6000 pin H21 (BOOT_SERIAL_IN)",
    "intermediates": ["R4003 (XX)", "R4002 (XX)"],
    "destinations": ["DEBUG_UART0_RXD → CN4001 pin 9", "CN4906 pin 4 (UART_RXD_MSS)"],
}

# Parálisis crítica: CN4906 pin 9 ≠ CN4001 pin 9
CN4906_PIN_9 = "TDO (SWD/JTAG)"
CN4001_PIN_9 = "UART_RX/BOOT_IN (MULTI)"


@dataclass
class PinConnection:
    reference: str
    pin: int
    signal: str
    intermediate: str | None
    mounting_status: str  # "montado", "no_montado_XX", "desconocido"
    destination: str
    evidence: str
    certainty: str  # "ALTA", "MEDIA", "BAJA"


@dataclass
class ReconstructionResult:
    connections: list[PinConnection] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def reconstruct_from_schematic_text(schematic_text: str) -> ReconstructionResult:
    """
    Valida que el texto extraído del esquema contenga las conexiones
    documentadas clave para el BootROM UART.
    """
    result = ReconstructionResult()

    # 1. Verificar marca XX (no montado) en resistencias clave
    for resistor in ("R4002", "R4003"):
        pattern = rf"{resistor}\s+XX"
        if not re.search(pattern, schematic_text):
            result.errors.append(f"{resistor} no encontrada con marca XX en el esquema")
        else:
            result.warnings.append(
                f"{resistor} está marcada XX (no montada) — ruta BOOT_SERIAL_IN interrumpida"
            )

    # 2. Verificar CN4001 pin 9 = UART_RX/BOOT_IN
    if (
        "9    UART_RX/BOOT_IN" not in schematic_text
        and "9   UART_RX/BOOT_IN" not in schematic_text
    ):
        result.warnings.append(
            "CN4001 pin 9 = UART_RX/BOOT_IN no confirmada en el texto extraído"
        )

    # 3. Verificar CN4906 pin 9 = TDO (no UART_RX/BOOT_IN)
    if "9     TDO" not in schematic_text and "9    TDO" not in schematic_text:
        result.warnings.append("CN4906 pin 9 = TDO no confirmada en el texto extraído")

    # 4. Verificar CN4906 pin 4 = UART_RXD_MSS
    if (
        "4     UART_RXD_MSS" not in schematic_text
        and "4    UART_RXD_MSS" not in schematic_text
    ):
        result.warnings.append(
            "CN4906 pin 4 = UART_RXD_MSS no confirmada en el texto extraído"
        )

    # 5. Verificar advertencia XX = NO MOUNT
    if "XX MARK: NO MOUNT" not in schematic_text and "XX" not in schematic_text:
        result.errors.append(
            "No se encontró la advertencia XX = NO MOUNT en el esquema"
        )

    # 6. Verificar que CN4906 pin 9 ≠ CN4001 pin 9
    if CN4906_PIN_9 == CN4001_PIN_9:
        result.errors.append(
            "ERROR: CN4906 pin 9 y CN4001 pin 9 mapeadas a la misma señal"
        )

    return result


def build_connection_map() -> list[PinConnection]:
    """Construye el mapa de conexiones conocido desde el esquema del manual."""
    connections = [
        PinConnection(
            reference="BIONZ IC6000",
            pin=0x21,  # H21
            signal="BOOT_SERIAL_IN",
            intermediate="—",
            mounting_status="desconocido",
            destination="R4003 (XX), R6004 (XX)",
            evidence="Esquema manual pág. 38, línea 3264",
            certainty="ALTA",
        ),
        PinConnection(
            reference="R4003",
            pin=0,
            signal="0 Ω candidato BOOT_SERIAL_IN → DEBUG_UART0_RXD",
            intermediate="R4003",
            mounting_status="no_montado_XX",
            destination="DEBUG_UART0_RXD → CN4001 pin 9",
            evidence="Esquema manual pág. 38, línea 6110",
            certainty="ALTA",
        ),
        PinConnection(
            reference="R4002",
            pin=0,
            signal="0 Ω candidato DEBUG_UART0_RXD → CN4001 pin 9",
            intermediate="R4002",
            mounting_status="no_montado_XX",
            destination="CN4001 pin 9 (UART_RX/BOOT_IN)",
            evidence="Esquema manual pág. 38, línea 6108",
            certainty="ALTA",
        ),
        PinConnection(
            reference="CN4001 (Multi Terminal)",
            pin=9,
            signal="UART_RX/BOOT_IN",
            intermediate="R4002 (XX) / R4003 (XX)",
            mounting_status="desconocido",
            destination="BootROM UART RX (si estuviera poblado)",
            evidence="Esquema manual pág. 38, línea 6109",
            certainty="MEDIA",
        ),
        PinConnection(
            reference="CN4001 (Multi Terminal)",
            pin=8,
            signal="UART_TX/LANC_SIG",
            intermediate="CM4008",
            mounting_status="desconocido",
            destination="DEBUG_UART0_TXD → BIONZ UART0_TXD",
            evidence="Esquema manual pág. 38, línea 6107",
            certainty="MEDIA",
        ),
        PinConnection(
            reference="CN4906 (servicio SIDE A)",
            pin=4,
            signal="UART_RXD_MSS",
            intermediate="DEBUG_UART0_RXD",
            mounting_status="desconocido",
            destination="BootROM UART RX",
            evidence="Esquema manual pág. 38, línea 6310",
            certainty="BAJA",
        ),
        PinConnection(
            reference="CN4906 (servicio SIDE A)",
            pin=5,
            signal="UART_TXD_MSS",
            intermediate="DEBUG_UART0_TXD",
            mounting_status="desconocido",
            destination="BootROM UART TX",
            evidence="Esquema manual pág. 38, línea 6314",
            certainty="BAJA",
        ),
        PinConnection(
            reference="CN4906 (servicio SIDE A)",
            pin=9,
            signal="TDO (SWD/JTAG)",
            intermediate="R4911 (XX)",
            mounting_status="no_montado_XX",
            destination="JTAG TDO (no BootROM UART)",
            evidence="Esquema manual pág. 38, línea 6324",
            certainty="ALTA",
        ),
        PinConnection(
            reference="R6004",
            pin=0,
            signal="0.1u cerca BOOT_SERIAL_IN",
            intermediate="R6004",
            mounting_status="no_montado_XX",
            destination="—",
            evidence="Esquema manual pág. 38, línea 3270",
            certainty="ALTA",
        ),
    ]
    return connections


def is_route_interrupted(connections: list[PinConnection]) -> bool:
    """Retorna True si la ruta BOOT_SERIAL_IN → CN4001 pin 9 está interrumpida."""
    xx_resistors = {
        c.reference
        for c in connections
        if c.mounting_status == "no_montado_XX" and c.reference in ("R4002", "R4003")
    }
    return "R4002" in xx_resistors and "R4003" in xx_resistors


def cn4906_pin9_equals_cn4001_pin9() -> bool:
    """Advertencia crítica: CN4906 pin 9 y CN4001 pin 9 NO son el mismo contacto."""
    return CN4906_PIN_9 != CN4001_PIN_9


# ── Self-test ───────────────────────────────────────────────────────────────


def self_test() -> bool:
    print("=== E26-R11 Pinout Reconstruction Self-Test ===")
    ok = True

    # T1: CN4001 pin 9 is UART_RX/BOOT_IN
    assert CN4001_PINS[9] == "UART_RX/BOOT_IN", "CN4001 pin 9 debe ser UART_RX/BOOT_IN"
    print("  [PASS] CN4001 pin 9 = UART_RX/BOOT_IN")

    # T2: CN4906 pin 9 is TDO (NOT UART_RX/BOOT_IN)
    assert CN4906_PINS[9] == "TDO", "CN4906 pin 9 debe ser TDO"
    assert CN4906_PIN_9 != CN4001_PIN_9, "CN4906 pin 9 ≠ CN4001 pin 9"
    print("  [PASS] CN4906 pin 9 = TDO (≠ CN4001 pin 9)")

    # T3: CN4906 pin 4 is UART_RXD_MSS
    assert CN4906_PINS[4] == "UART_RXD_MSS", "CN4906 pin 4 debe ser UART_RXD_MSS"
    print("  [PASS] CN4906 pin 4 = UART_RXD_MSS")

    # T4: R4002 and R4003 are XX
    assert "R4002" in RESISTORS_XX and "R4003" in RESISTORS_XX
    print("  [PASS] R4002 y R4003 marcadas XX")

    # T5: Route is interrupted
    conns = build_connection_map()
    assert is_route_interrupted(conns), (
        "Ruta BOOT_SERIAL_IN → CN4001 pin 9 interrumpida"
    )
    print(
        "  [PASS] Ruta BOOT_SERIAL_IN → CN4001 pin 9 está interrumpida (R4002/R4003 XX)"
    )

    # T6: Connection map has expected entries
    refs = {c.reference for c in conns}
    assert "R4003" in refs
    assert "R4002" in refs
    assert "CN4001 (Multi Terminal)" in refs
    assert "CN4906 (servicio SIDE A)" in refs
    print("  [PASS] Mapa de conexiones contiene todas las entradas esperadas")

    # T7: Certainty levels
    for c in conns:
        assert c.certainty in ("ALTA", "MEDIA", "BAJA"), (
            f"Nivel de certeza inválido: {c.certainty}"
        )
    print("  [PASS] Todos los niveles de certeza son válidos")

    # T8: Schematic text validation (synthetic)
    synthetic_schematic = """
    DEBUG_UART0_TXD   CM4008    8    UART_TX/LANC_SIG    MULTI
    R4002   XX
    DEBUG_UART0_RXD   9    UART_RX/BOOT_IN
             R4003        XX
    BOOT_SERIAL_IN    CM4002    10     AD_JACK_IN
    XX MARK: NO MOUNT
    """
    result = reconstruct_from_schematic_text(synthetic_schematic)
    assert len(result.errors) == 0, f"Errores inesperados: {result.errors}"
    assert len(result.warnings) >= 1, (
        "Se esperaba al menos una advertencia sobre resistencias XX"
    )
    print("  [PASS] Validación de texto esquemático sintético")

    print(f"\n  {'Todos los tests pasaron.' if ok else 'ALGUNOS TESTS FALLARON.'}")
    return ok


def main() -> int:
    ok = self_test()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
