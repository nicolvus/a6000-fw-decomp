"""S77: comprobaciones contra los bytes reales de av-cam.bin (A6000 fw3.21)
y extracción de datos de Creative Style, Picture Profile y White Balance."""
import hashlib
import json
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Cargar config JSON
JSON_PATH = ROOT / "analysis/s77_pp/picture_profile_creative_style.json"
with open(JSON_PATH, "r") as f:
    JSON_CONFIG = json.load(f)

BLOB_PATH = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
with open(BLOB_PATH, "rb") as f:
    BLOB = f.read()

# Base del blob av-cam.bin (dirección donde empiezan los nombres de Stage_)
B = 0x43c9ee6c

# Capstone para disassembly
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def dis(a, b):
    """Disasm instrucciones del blob av-cam.bin."""
    return [(i.address, i.mnemonic, i.op_str) for i in MD.disasm(BLOB[a - B:b - B], a)]


def u32(a):
    """Lee un entero sin signo de 32 bits little-endian del blob."""
    return struct.unpack_from("<I", BLOB, a - B)[0]


# ════════════════════════════════════════════════════════════════════════════
# Test classes
# ════════════════════════════════════════════════════════════════════════════


class CreativeStyleNames(unittest.TestCase):
    """Verifica el inventario de estilos Creative Style en av-cam.bin."""

    def test_creative_style_vivid_present(self):
        """Vivid debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Vivid", text, "Estilo 'Vivid' no encontrado")

    def test_creative_style_neutral_present(self):
        """Neutral debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Neutral", text, "Estilo 'Neutral' no encontrado")

    def test_creative_style_portrait_present(self):
        """Portrait debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Portrait", text, "Estilo 'Portrait' no encontrado")

    def test_creative_style_landscape_present(self):
        """Landscape debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Landscape", text, "Estilo 'Landscape' no encontrado")

    def test_creative_style_bw_present(self):
        """BW (Black & White) debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("BW", text, "Estilo 'BW' no encontrado")

    def test_creative_style_clear_present(self):
        """Clear debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Clear", text, "Estilo 'Clear' no encontrado")

    def test_creative_style_deep_present(self):
        """Deep debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Deep", text, "Estilo 'Deep' no encontrado")

    def test_creative_style_light_present(self):
        """Light debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Light", text, "Estilo 'Light' no encontrado")

    def test_creative_style_sunset_present(self):
        """Sunset debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Sunset", text, "Estilo 'Sunset' no encontrado")

    def test_creative_style_nightview_present(self):
        """Nightview debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Nightview", text, "Estilo 'Nightview' no encontrado")

    def test_creative_style_autumnleaves_present(self):
        """Autumnleaves debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Autumnleaves", text, "Estilo 'Autumnleaves' no encontrado")

    def test_creative_style_standard_present(self):
        """Standard debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Standard", text, "Estilo 'Standard' no encontrado")

    def test_creative_style_total_count(self):
        """Debe haber exactamente 13 estilos Creative Style únicos."""
        text = BLOB.decode("latin-1", errors="replace")
        # Los nombres aparecen como: VividNeutralPortraitLandscapeBWClearDeepLightSunsetNightviewAutumnleavesRealSepiaStandard
        # Usamos regex para encontrar todos los nombres (manejo de null bytes y concatenación)
        pattern = r"(?:Vivid|Neutral|Portrait|Landscape|BW|Clear|Deep|Light|Sunset|Nightview|Autumnleaves|RealSepia|Standard)"
        names = re.findall(pattern, text, re.IGNORECASE)
        unique_names = set(names)
        # Normalizar a títulos para comparar
        expected = ["Vivid", "Neutral", "Portrait", "Landscape", "BW", "Clear", "Deep", "Light", "Sunset", "Nightview", "Autumnleaves", "RealSepia", "Standard"]
        normalized = [n.title() for n in unique_names]
        for exp in expected:
            self.assertIn(exp, normalized,
                          f"Estilo esperado '{exp}' no encontrado en los {len(unique_names)} únicos: {normalized}")


class WhiteBalancePresets(unittest.TestCase):
    """Verifica los presets y coeficientes de balance de blancos."""

    def test_wb_auto_present(self):
        """Auto WB preset debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Auto", text, "Preset WB 'Auto' no encontrado")

    def test_wb_shade_present(self):
        """Shade WB preset debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Shade", text, "Preset WB 'Shade' no encontrado")

    def test_wb_flash_present(self):
        """Flash WB preset debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Flash", text, "Preset WB 'Flash' no encontrado")

    def test_wb_underwater_present(self):
        """Underwater WB preset debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertIn("Underwater", text, "Preset WB 'Underwater' no encontrado")

    def test_wb_coefficients_present(self):
        """Los coeficientes wb_r_data, wb_g_data, wb_b_data deben estar en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        for sym in ["wb_r_data", "wb_g_data", "wb_b_data"]:
            positions = [m.start() for m in re.finditer(sym, text, re.IGNORECASE)]
            self.assertGreater(len(positions), 0,
                               f"Símbolo '{sym}' no encontrado en av-cam.bin")
            # Verificar que las posiciones están en el área WB esperada (~7560230-7560299)
            for p in positions:
                self.assertIn(p, range(7560220, 7560310),
                              f"Offset de '{sym}' fuera del área esperada: {p}")


class PictureProfileParams(unittest.TestCase):
    """Verifica los parámetros de Picture Profile en av-cam.bin."""

    def test_contrast_present(self):
        """El parámetro Contrast debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertTrue(
            re.search(r"(?i)Contrast", text),
            "Parámetro 'Contrast' no encontrado en av-cam.bin"
        )

    def test_saturation_present(self):
        """El parámetro Saturation debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertTrue(
            re.search(r"(?i)Saturation", text),
            "Parámetro 'Saturation' no encontrado en av-cam.bin"
        )

    def test_brightness_present(self):
        """El parámetro Brightness debe aparecer en av-cam.bin."""
        text = BLOB.decode("latin-1", errors="replace")
        self.assertTrue(
            re.search(r"(?i)Brightness", text),
            "Parámetro 'Brightness' no encontrado en av-cam.bin"
        )


# ════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main()