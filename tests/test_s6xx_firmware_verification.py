#!/usr/bin/env python3
"""Tests de verificación S605–S627 contra el firmware av-cam.bin.

Verifica SOLO lo demostrable por instrucciones/bytes del firmware:
1. Existencia de cada cadena de traza en su vaddr declarado
2. Existencia del logger global 0x43902718 como código (no relleno/ceros)
3. Ausencia de palabras clave del obturador en las cadenas de traza del módulo

NO verifica: logger dual (requiere xrefs/REA), equivalencia A7S/A6300,
equivalencia de código (requieren REA y los otros firmwares).
"""
import json
import struct
import unittest
from pathlib import Path

FW_A6000 = Path(
    "firmware/extracted/fw321/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
BASE = 0x43541000
LOGGER_GLOBAL = 0x43902718

fw_data = FW_A6000.read_bytes()
fw_size = len(fw_data)


def vaddr_to_offset(vaddr: int):
    off = vaddr - BASE
    if off < 0 or off >= fw_size:
        return None
    return off


def read_cstring(off: int):
    if off is None:
        return None
    try:
        end = fw_data.index(b"\x00", off)
        return fw_data[off:end].decode("ascii", errors="replace")
    except ValueError:
        return None


def norm(s: str):
    if s is None:
        return None
    return s.rstrip()


import re
SHUTTER_PATTERNS = [
    r"\bshutter\b", r"\bsilent\b", r"\bcurtain\b", r"\belectro\b", r"\bmech\b",
    r"\bobtur\b", r"\bsensor\b", r"\breadout\b", r"\bimager\b", r"\biso\b",
    r"\bapert\b", r"\bexpos\b", r"\bbrack\b", r"\bdrive\b", r"\brelease\b",
    r"\bflash\b", r"\bvsync\b", r"\bcapture\b", r"\bstill\b", r"\bmovie\b",
    r"\bfocus\b", r"\bsvd\b", r"\bshd\b", r"\bspl\b", r"\bframe\b",
]
# "shot" y "sync" excluidos: falsos positivos conocidos
#   - "shot" en "Shot Timing Transform" (S611) = contexto GOLFSHOT, no obturador
#   - "sync" en "osal_reg_sync_msg_queue_cb" (S620) = registro sincrónico, no vsync


def list_module_dirs():
    return sorted(
        d for d in Path("analysis").glob("s6[0-2][0-9]_*")
        if 605 <= int(d.name[1:4]) <= 627
    )


def load_module_json(module_dir):
    json_files = list(module_dir.glob("*.json"))
    assert json_files, f"No JSON in {module_dir}"
    with open(json_files[0]) as f:
        return json.load(f)


class S6xxFirmwareVerification(unittest.TestCase):
    """Tests compartidos para todos los módulos S605–S627."""

    @classmethod
    def setUpClass(cls):
        cls.results = {}
        for d in list_module_dirs():
            jdata = load_module_json(d)
            cls.results[d.name] = jdata

    def test_logger_global_exists_as_code(self):
        """0x43902718 debe ser código válido (no cerros/relleno) en av-cam.bin."""
        off = vaddr_to_offset(LOGGER_GLOBAL)
        self.assertIsNotNone(off, f"Logger 0x{LOGGER_GLOBAL:08x} fuera de rango")
        b = fw_data[off:off + 4]
        self.assertNotEqual(b, b"\x00\x00\x00\x00", "Logger global son ceros")
        self.assertNotEqual(b, b"\xff\xff\xff\xff", "Logger global es relleno 0xFF")

    def test_all_trace_strings_exist_in_firmware(self):
        """Cada cadena de traza debe existir en su vaddr declarado en av-cam.bin."""
        for module_name, jdata in self.results.items():
            for ts in jdata.get("trace_strings", []):
                vaddr = int(ts["vaddr"], 16) if isinstance(ts["vaddr"], str) else ts["vaddr"]
                expected = ts["text"]
                off = vaddr_to_offset(vaddr)
                found = read_cstring(off)
                self.assertIsNotNone(
                    found,
                    f"{module_name}: cadena en 0x{vaddr:08x} no encontrada en firmware"
                )
                self.assertTrue(
                    norm(found) == norm(expected),
                    f"{module_name}: 0x{vaddr:08x} esperado='{norm(expected)[:60]}' encontrado='{norm(found)[:60]}'"
                )

    def test_no_shutter_keywords_in_trace_strings(self):
        """Las cadenas de traza del módulo no deben contener palabras clave del obturador."""
        for module_name, jdata in self.results.items():
            for ts in jdata.get("trace_strings", []):
                text = ts["text"].lower()
                for pat in SHUTTER_PATTERNS:
                    self.assertNotRegex(
                        text, pat,
                        f"{module_name}: 0x{int(ts['vaddr'],16):08x} coincide con '{pat}' (línea del obturador)"
                    )

    def test_verification_status_present(self):
        """Cada JSON debe tener verification_status."""
        for module_name, jdata in self.results.items():
            self.assertIn(
                "verification_status", jdata,
                f"{module_name}: falta verification_status en JSON"
            )
            vs = jdata["verification_status"]
            self.assertIn("trace_strings", vs)
            self.assertIn("logger_dual", vs)
            self.assertIn("equivalencia_funcional", vs)
            self.assertIn("equivalencia_codigo", vs)
            self.assertIn("linea_obturador", vs)

    def test_logger_dual_is_no_verificado(self):
        """logger_dual debe estar marcado NO_VERIFICADO (no demostrado por strings)."""
        for module_name, jdata in self.results.items():
            vs = jdata.get("verification_status", {})
            ld = vs.get("logger_dual", {})
            self.assertEqual(
                ld.get("status"), "NO_VERIFICADO",
                f"{module_name}: logger_dual no es NO_VERIFICADO"
            )

    def test_equivalencia_funcional_is_no_verificado(self):
        """equivalencia_funcional debe estar marcado NO_VERIFICADO."""
        for module_name, jdata in self.results.items():
            vs = jdata.get("verification_status", {})
            ef = vs.get("equivalencia_funcional", {})
            self.assertEqual(
                ef.get("status"), "NO_VERIFICADO",
                f"{module_name}: equivalencia_funcional no es NO_VERIFICADO"
            )

    def test_equivalencia_codigo_is_no_verificado(self):
        """equivalencia_codigo debe estar marcado NO_VERIFICADO."""
        for module_name, jdata in self.results.items():
            vs = jdata.get("verification_status", {})
            ec = vs.get("equivalencia_codigo", {})
            self.assertEqual(
                ec.get("status"), "NO_VERIFICADO",
                f"{module_name}: equivalencia_codigo no es NO_VERIFICADO"
            )

    def test_linea_obturador_verified(self):
        """linea_obturador debe estar VERIFICADO (0 keywords en trazas)."""
        for module_name, jdata in self.results.items():
            vs = jdata.get("verification_status", {})
            lo = vs.get("linea_obturador", {})
            self.assertEqual(
                lo.get("status"), "VERIFICADO",
                f"{module_name}: linea_obturador no es VERIFICADO: {lo}"
            )


if __name__ == "__main__":
    unittest.main()