"""S75 — ZPD (Zone Plate Detection): calibracion del sensor con datos de la lente.

Anclas verificadas contra los bytes del av-cam.bin A6000 (fw3.21).
Ver analysis/s75_zpd/zpd_subsystem.md.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

STR_RE = re.compile(rb"[\x20-\x7e]{5,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 160)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def strings_with(prefix, model="A6000"):
    d = data(model)
    return sorted(B + m.start() for m in STR_RE.finditer(d) if m.group().startswith(prefix.encode()))


class ZpdNamespace(unittest.TestCase):
    def test_zpd_class_names(self):
        names = [cstr(a) for a in strings_with("N6Camera3ZPD")]
        self.assertEqual(len(names), 14)
        self.assertIn("N6Camera3ZPD4Lens18LensInterpretChunkE", names)
        self.assertIn("N6Camera3ZPD4Lens20LensInterpretChunkEdE", names)
        self.assertIn("N6Camera3ZPD7Control6DetectE", names)
        self.assertIn("N6Camera3ZPD13MemUnitBackupE", names)

    def test_zpd_data_sources(self):
        """Los datos de ZPD vienen de la lente, del cuerpo y de 'dra data'."""
        self.assertEqual(cstr(0x43CCF27F), "[ZPD]: lens attach sequence end.")
        self.assertEqual(cstr(0x43CCF2A0), "[ZPD]: load dra data.")
        self.assertEqual(cstr(0x43CCF2C7), "[ZPD]: load lens data from lens.")
        self.assertEqual(cstr(0x43CCF2E8), "[ZPD]: load lens data from body.")

    def test_dfe_zpd_interrupts(self):
        """El DFE tiene dos canales de interrupcion ZPD0/ZPD1 con factor configurable."""
        for addr, text in {
            0x43C91781: "[DFECore]: [Err][SetZPD0IntFactor] wrong int bit %08X",
            0x43C917F8: "[DFECore]: [Err][ClearZPD0IntFactor] wrong int bit %08X",
            0x43C91875: "[DFECore]: [Err][SetZPD1IntFactor] wrong int bit %08X",
            0x43C918EC: "[DFECore]: [Err][ClearZPD1IntFactor] wrong int bit %08X",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_defect_positions_to_sensor_sram(self):
        self.assertIn("ImgDdcSetter::loadDefectPos ZPD_SRAM shortage",
                      cstr(0x43CF75EE))

    def test_apb_and_aif_traces(self):
        for addr, text in {
            0x43FA9798: "Detected IRQ : ZPD CH1",
            0x43FA9A4C: "CPU IRQ : ZPD0",
            0x43FA9A60: "CPU IRQ : ZPD1",
            0x43FA9F24: "CPU APB : ZPD_APB1 Value write (Min addr)",
            0x43FAA120: "CPU APB : ZPD_APB0 Value write (Min addr)",
            0x43FAABB0: "CPU AIF : ZPD W-ch0 Start",
            0x43FAABF0: "CPU AIF : ZPD R-ch1 Start",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_coordination_with_mount_and_af(self):
        """ZPD se coordina con el bus de la lente (EclipseDataComState) y con el AF hibrido."""
        self.assertEqual(cstr(0x43C976B5),
                         "[MOUNT_DEBUG]: [BL]ZPD change EclipseDataComState from STANDBY to START")
        self.assertIn("NOT_DETECT from ZPD MODULE in spite of ZpdPreEnable", cstr(0x43C9D07E))
        self.assertIn("time is zero Main/LC/ZPD/zpd_mario_afa.cpp", cstr(0x43C9DB6A))
        self.assertIn("LC_GetZpdResultInfo:Error", cstr(0x43CA78B6))
        # el protocolo de montura lleva un contador de timeout del canal LC (calibracion)
        self.assertEqual(cstr(0x43C96C1E), "[MOUNT_ERROR]: [BL]LC T.O. Cnt         %04X")

    def test_a7s_has_dfe_zpd_but_not_the_app_namespace(self):
        """Diferencial A7S (fw3.20): existen los factores de interrupcion ZPD en el DFE, pero NO
        el namespace de aplicacion `Camera::ZPD` (0 hits de 'N6Camera3ZPD')."""
        a7s_names = [cstr(a, "A7S") for a in strings_with("N6Camera3ZPD", "A7S")]
        self.assertEqual(a7s_names, [])
        # el DFE de la A7S si tiene SetZPD0IntFactor / ClearZPD1IntFactor (sin el prefijo [DFECore])
        self.assertEqual(cstr(0x43C9A689, "A7S"), "[Err][SetZPD0IntFactor] wrong int bit %08X")
        self.assertEqual(cstr(0x43C9A7B2, "A7S"), "[Err][ClearZPD1IntFactor] wrong int bit %08X")
        # y no tiene los logs de origen de datos de la fw3.21
        a7s_logs = [cstr(a, "A7S") for a in strings_with("[ZPD]:", "A7S")]
        self.assertEqual(a7s_logs, [])


if __name__ == "__main__":
    unittest.main()
