"""S68 — Gestión de batería, alimentación y carga (NP-FW50) en la A6000: anclas verificadas.

Análisis estático de bytes del av-cam.bin (fw3.21). Nada se ejecuta del firmware.
Informe: analysis/s68_power/battery_power.md · Hito: docs/capture/s68-battery-power.md

Nota: la dirección de la cadena "Wait E-MountLens ReduceVoltage" la corrigió el revisor
de este test: 0x43cc7aa4 (no 0x43cc2ca6, que apuntaba a otra cadena de SHD).
"""
import re
import sys
import unittest
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False
MD.skipdata = True

STR_RE = re.compile(rb"[\x20-\x7e]{5,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 128)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def addresses_of(text, model="A6000"):
    d = data(model)
    needle = text.encode()
    return [B + m.start() for m in STR_RE.finditer(d) if needle in m.group()]


class BatteryAnchors(unittest.TestCase):
    def test_battery_level_log_and_info(self):
        self.assertEqual(cstr(0x43CA2DFD),
                         "[CAMERA_MAIN_SYNC]: Set UPM Battery Level [state] %d [Error] %d")
        self.assertEqual(cstr(0x43CA6A3C), "[CAMERA_MAIN_FC]: OSAL_ERROR: BatteryInfo")
        self.assertEqual(cstr(0x43CA6A5A), "BatteryInfo")
        self.assertEqual(cstr(0x43CA7E2E), "[IRLight] Battery Info : %d")
        self.assertEqual(cstr(0x43CA7F1D), "[VideoLight] Battery Info : %d")

    def test_battery_state_messages_to_mcu(self):
        self.assertEqual(cstr(0x43C8F83B), "ACV Error Voltage")
        self.assertEqual(cstr(0x43C8F95E), "ACV_BATT_Snd")
        self.assertEqual(cstr(0x43C8F96B), "BATT_AUTH_Snd")
        self.assertEqual(len(addresses_of("BATT_STATE1_Snd")), 1)
        self.assertEqual(len(addresses_of("BATT_TYPE1_Snd")), 1)
        self.assertEqual(len(addresses_of("Box_Temperature_Snd")), 1)

    def test_flash_charge_block_is_not_battery(self):
        """El bloque de 'carga' es del flash (SB), no de la batería principal."""
        self.assertEqual(cstr(0x43CB4C23), "SB_CHARGE")
        self.assertEqual(cstr(0x43CCD8C2), "uc_ChargeCommand")
        self.assertEqual(cstr(0x43CCD8EF), "uc_ChargeStatus")
        self.assertEqual(cstr(0x43CCD939), "uc_ChargeEnable")
        self.assertEqual(cstr(0x43CCD96C), "uc_ChargeForceOff")
        self.assertEqual(cstr(0x43CCDC63), "b_GpflLogicPowerOn")
        self.assertEqual(cstr(0x43CCDC76), "b_SBChargeReq")

    def test_reduce_voltage_address(self):
        """Corrección de dirección: la cadena de reducción de voltaje está en 0x43cc7aa4."""
        self.assertEqual(cstr(0x43CC7AA4),
                         "[IMAGING_CAP]: Warning! Wait E-MountLens ReduceVoltage Wait(%d ms)")
        self.assertNotEqual(cstr(0x43CC2CA6),
                            "[IMAGING_CAP]: Warning! Wait E-MountLens ReduceVoltage Wait(%d ms)")

    def test_power_off_detect(self):
        self.assertEqual(cstr(0x43CA9D85),
                         "[IMAGING_CAP]: CapMgr)CaptureCancel_PowerOffDetect() offFactor=%d")

    def test_no_np_fw50_model_in_avcam(self):
        """Resultado NEGATIVO verificado: no hay modelo del pack NP-FW50 en av-cam.bin."""
        d = data("A6000")
        for needle in (b"NP-FW", b"NPFW", b"FW50"):
            self.assertEqual(d.find(needle), -1, needle)

    def test_a7s_comparison(self):
        """A7S (fw3.20): conserva el bloque de estado de batería y la carga de flash, pero no
        tiene 'BatteryInfo' ni los 'Battery Info' de las luces.

        Corrección de la revisión: la A7S **sí** tiene `ACV Error Voltage` (0x43c982d3) y
        `ACV_BATT_Snd` (0x43c983f6); la afirmación inicial de que faltaban era incorrecta.
        """
        def txt(model):
            d = data(model)
            return "\n".join(m.group().decode("ascii", "replace") for m in STR_RE.finditer(d))
        a7s = txt("A7S")
        self.assertIn("Set UPM Battery Level", a7s)
        self.assertIn("SB_CHARGE", a7s)
        self.assertIn("ACV Error Voltage", a7s)
        self.assertIn("ACV_BATT_Snd", a7s)
        self.assertIn("BATT_STATE1_Snd", a7s)
        self.assertNotIn("BatteryInfo", a7s)
        self.assertNotIn("[IRLight] Battery Info", a7s)
        self.assertNotIn("[VideoLight] Battery Info", a7s)
        self.assertEqual(cstr(0x43C982D3, "A7S"), "ACV Error Voltage")
        self.assertEqual(cstr(0x43C983F6, "A7S"), "ACV_BATT_Snd")


if __name__ == "__main__":
    unittest.main()
