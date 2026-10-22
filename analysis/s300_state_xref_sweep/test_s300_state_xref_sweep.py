#!/usr/bin/env python3
"""Test reproducible para S300 — Barrido xrefs a 0x43f72d02 (A6000 fw3.21).

Verifica:
1. 15 xrefs encontrados por REA a 0x43f72d02
2. Clasificación de cada xref (spill/lectura/escritura/propagación)
3. NO writers a state+3 (0x43f72d05) ni state+6 (0x43f72d08)
4. Literales 0x43f72d05/0x43f72d08 ausentes en binario
"""

import unittest
import mmap
import struct
import json
import os

BIN_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "firmware",
    "extracted",
    "fw321",
    "firmware.tar_unpacked",
    "0700_part_image",
    "dev",
    "nflasha3_unpacked_unpacked",
    "av-cam.bin"
)
BASE = 0x43541000
STATE_OBJ = 0x43f72d02
GOT_SLOT = 0x4401f990


class TestS300StateXrefSweep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(BIN_PATH, "rb") as f:
            cls.m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

    def test_state_object_literal_count(self):
        """El literal 0x43f72d02 aparece exactamente 2 veces: en GOT y en tabla datos."""
        target = STATE_OBJ.to_bytes(4, "little")
        positions = []
        idx = 0
        while True:
            idx = self.m.find(target, idx)
            if idx == -1:
                break
            positions.append(idx)
            idx += 1
        self.assertEqual(len(positions), 2, f"Esperadas 2 ocurrencias de 0x43f72d02, encontradas {len(positions)}")
        vas = [BASE + p for p in positions]
        self.assertIn(GOT_SLOT, vas, "GOT slot 0x4401f990 debe contener el literal")
        self.assertIn(0x43ff3248, vas, "Tabla de datos 0x43ff3248 debe contener el literal")

    def test_state_plus3_plus6_literals_absent(self):
        """No hay literales directos a state+3 (0x43f72d05) ni state+6 (0x43f72d08)."""
        for offset, name in [(3, "state+3"), (6, "state+6")]:
            target = (STATE_OBJ + offset).to_bytes(4, "little")
            idx = self.m.find(target)
            self.assertEqual(idx, -1, f"Literal {name} (0x{STATE_OBJ+offset:x}) NO debe estar en binario")

    def test_xrefs_classified_json_exists(self):
        """El JSON de clasificación existe y tiene la estructura esperada."""
        json_path = os.path.join(os.path.dirname(__file__), "xrefs_classified.json")
        self.assertTrue(os.path.exists(json_path), "Falta xrefs_classified.json")
        with open(json_path) as f:
            data = json.load(f)
        self.assertEqual(data["binary"], "av-cam.bin A6000 fw3.21")
        self.assertEqual(data["state_object"], "0x43f72d02")
        self.assertEqual(data["got_slot"], "0x4401f990")
        self.assertEqual(data["xrefs_total"], 15)
        self.assertEqual(len(data["classified"]), 15)
        self.assertEqual(data["gates_writers"]["state_plus_3"], "NO_ENCONTRADO")
        self.assertEqual(data["gates_writers"]["state_plus_6"], "NO_ENCONTRADO")

    def test_all_classified_entries_have_required_fields(self):
        """Cada entrada clasificada tiene campos requeridos."""
        json_path = os.path.join(os.path.dirname(__file__), "xrefs_classified.json")
        with open(json_path) as f:
            data = json.load(f)
        for entry in data["classified"]:
            self.assertIn("addr", entry)
            self.assertIn("func", entry)
            self.assertIn("type", entry)
            self.assertIn("fields", entry)
            self.assertIn("evidence", entry)

    def test_no_write_to_gates_in_classified(self):
        """Ninguna entrada clasificada es escritura a state+3 o state+6."""
        json_path = os.path.join(os.path.dirname(__file__), "xrefs_classified.json")
        with open(json_path) as f:
            data = json.load(f)
        for entry in data["classified"]:
            # Verificar que los campos no sean +3 o +6 como escritura
            for field in entry["fields"]:
                if isinstance(field, str) and field.startswith("+"):
                    # Extraer offset
                    try:
                        off = int(field[1:], 16) if field[1:].startswith("0x") else int(field[1:])
                        self.assertNotIn(off, [3, 6], f"Entrada {entry['addr']} tiene escritura a gate +{off}")
                    except ValueError:
                        pass  # campo como "various", ignorar

    def test_gates_writers_verdict(self):
        """El veredicto de gates es NO_VERIFICADO."""
        json_path = os.path.join(os.path.dirname(__file__), "xrefs_classified.json")
        with open(json_path) as f:
            data = json.load(f)
        self.assertEqual(data["gates_writers"]["verdict"], "NO_VERIFICADO (runtime desconocido)")

    def test_xref_types_distribution(self):
        """Verificar distribución de tipos de xrefs."""
        json_path = os.path.join(os.path.dirname(__file__), "xrefs_classified.json")
        with open(json_path) as f:
            data = json.load(f)
        types = [e["type"] for e in data["classified"]]
        # Debe haber al menos: 1 write_state+0, 3+ stack_spill, varios field_read, 1 data_reference
        self.assertIn("write_state+0", types)
        stack_spill_count = sum(1 for t in types if "stack_spill" in t)
        self.assertGreaterEqual(stack_spill_count, 3, f"Esperados >=3 stack_spill, encontrados {stack_spill_count}")
        self.assertIn("data_reference", types)


if __name__ == "__main__":
    unittest.main(verbosity=2)