"""Comprueba evidencia del firmware y coherencia de los resultados persistidos."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_s6xx", ROOT / "analysis/verify_s6xx.py")
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class S6xxFirmwareVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blobs = {model: path.read_bytes() for model, path in VERIFY.FIRMWARE.items()}
        cls.modules = {p: json.loads(p.read_text()) for p in VERIFY.module_files()}

    def test_inventory_is_complete(self):
        self.assertEqual({int(p.parent.name[1:4]) for p in self.modules}, set(range(605, 628)))
        self.assertEqual(len(self.modules), 23)

    def test_persisted_evidence_is_reproducible(self):
        for path, data in self.modules.items():
            with self.subTest(path=path):
                self.assertEqual(data["verification_status"], VERIFY.verify_module(data, self.blobs))

    def test_saved_results_match_firmware_and_statuses(self):
        saved = json.loads((ROOT / "analysis/s6xx_verification_results.json").read_text())
        self.assertEqual(saved, VERIFY.audit())

    def test_exact_traces_twins_cores_and_metadata(self):
        for path, data in self.modules.items():
            status = VERIFY.verify_module(data, self.blobs)
            for category in ("trace_strings", "twin_strings", "core_strings"):
                evidence = status[category]
                with self.subTest(path=path, category=category):
                    self.assertEqual(evidence["verified"], evidence["count_total"] > 0)
            self.assertTrue(status["metadata"]["verified"])

    def test_claims_without_control_flow_remain_pending(self):
        for data in self.modules.values():
            for category in (
                "logger_dual", "equivalencia_funcional", "equivalencia_codigo",
                "linea_obturador", "differential", "other_claims",
            ):
                evidence = data["verification_status"][category]
                if category == "logger_dual" and data["module"] in {"CAM_CMD", "IMAGING_RSRC"}:
                    self.assertEqual(evidence["status"], "VERIFICADO_ESTATICO")
                    self.assertTrue(evidence["verified"])
                else:
                    self.assertEqual(evidence["status"], "NO_VERIFICADO")
                    self.assertFalse(evidence["verified"])

    def test_whitespace_corruption_is_rejected(self):
        data = copy.deepcopy(next(d for p, d in self.modules.items() if p.parent.name.startswith("s607")))
        trace = next(t for t in data["trace_strings"] if t["text"].endswith("\n"))
        trace["text"] = trace["text"].rstrip()
        self.assertFalse(VERIFY.verify_module(data, self.blobs)["trace_strings"]["verified"])

    def test_wrong_twin_address_is_rejected(self):
        data = copy.deepcopy(next(d for p, d in self.modules.items() if p.parent.name.startswith("s606")))
        data["trace_strings"][0]["twin_vaddr"] = "0x43cfdb9c"
        self.assertFalse(VERIFY.verify_module(data, self.blobs)["twin_strings"]["verified"])

    def test_wrong_delta_is_rejected(self):
        data = copy.deepcopy(next(d for p, d in self.modules.items() if p.parent.name.startswith("s606")))
        data["trace_strings"][0]["delta"] += 1
        self.assertFalse(VERIFY.verify_module(data, self.blobs)["twin_strings"]["verified"])

    def test_wrong_core_text_is_rejected(self):
        data = copy.deepcopy(next(d for p, d in self.modules.items() if p.parent.name.startswith("s608")))
        data["trace_strings"][0]["core_text"] += "corrupt"
        self.assertFalse(VERIFY.verify_module(data, self.blobs)["core_strings"]["verified"])

    def test_trace_annotations_match_firmware(self):
        for session, field, value in ((613, "sub_prefix", "[WRONG]"), (619, "level", "DEBUG")):
            data = copy.deepcopy(next(
                d for p, d in self.modules.items() if p.parent.name.startswith(f"s{session}")
            ))
            data["trace_strings"][0][field] = value
            status = VERIFY.verify_module(data, self.blobs)
            self.assertFalse(status["trace_annotations"]["verified"])

    def test_unknown_trace_fields_are_pending(self):
        data = copy.deepcopy(next(iter(self.modules.values())))
        data["trace_strings"][0]["emitter"] = "0x43902718"
        status = VERIFY.verify_module(data, self.blobs)
        self.assertEqual(status["other_claims"]["trace_fields"], [
            {"vaddr": data["trace_strings"][0]["vaddr"], "fields": ["emitter"]}
        ])

    def test_wrong_prefix_with_same_length_is_rejected(self):
        data = copy.deepcopy(next(iter(self.modules.values())))
        data["prefix"] = "X" * len(data["prefix"])
        self.assertFalse(VERIFY.verify_module(data, self.blobs)["metadata"]["verified"])

    def test_incomplete_twin_schema_is_rejected(self):
        data = copy.deepcopy(next(
            d for p, d in self.modules.items() if p.parent.name.startswith("s606")
        ))
        del data["trace_strings"][0]["twin_vaddr"]
        self.assertFalse(VERIFY.verify_module(data, self.blobs)["metadata"]["verified"])

    def test_positive_logger_flag_is_rejected(self):
        data = copy.deepcopy(next(iter(self.modules.values())))
        data["logger_dual"] = True
        self.assertFalse(VERIFY.verify_module(data, self.blobs)["metadata"]["verified"])

    def test_s611_dual_logger_paths_are_verified_from_instructions(self):
        data = next(d for p, d in self.modules.items() if p.parent.name.startswith("s611"))
        self.assertTrue(VERIFY.verify_module(data, self.blobs)["logger_dual"]["verified"])
        corrupted = copy.deepcopy(data)
        corrupted["logger_paths"][0]["local_call"] = "0x4379a364"
        self.assertFalse(VERIFY.verify_module(corrupted, self.blobs)["logger_dual"]["verified"])

    def test_s607_dual_logger_paths_are_verified_from_instructions(self):
        data = next(d for p, d in self.modules.items() if p.parent.name.startswith("s607"))
        self.assertTrue(VERIFY.verify_module(data, self.blobs)["logger_dual"]["verified"])
        corrupted = copy.deepcopy(data)
        corrupted["logger_paths"][0]["global_call"] = "0x437fc380"
        self.assertFalse(VERIFY.verify_module(corrupted, self.blobs)["logger_dual"]["verified"])

    def test_cli_rejects_saved_positive_claims_without_evidence(self):
        data = copy.deepcopy(next(iter(self.modules.values())))
        result = {"module": data["module"], "json": "unused.json",
                  "verification_status": VERIFY.verify_module(data, self.blobs)}
        for category in ("logger_dual", "equivalencia_funcional", "equivalencia_codigo"):
            with self.subTest(category=category):
                changed = copy.deepcopy(data)
                changed["verification_status"][category] = {
                    "verified": True, "status": "VERIFICADO"
                }
                with patch.object(VERIFY, "audit", return_value=[result]), \
                        patch.object(Path, "read_text", return_value=json.dumps(changed)), \
                        patch("sys.argv", ["verify_s6xx"]):
                    self.assertTrue(VERIFY.main())

    def test_data_bytes_do_not_prove_logger_code(self):
        data = copy.deepcopy(next(iter(self.modules.values())))
        data["global_logger"] = data["trace_strings"][0]["vaddr"]
        status = VERIFY.verify_module(data, self.blobs)["logger_dual"]
        self.assertIsNotNone(status["bytes_hex"])
        self.assertFalse(status["global_logger_verified"])
        self.assertFalse(status["verified"])

    def test_empty_evidence_does_not_verify_absence(self):
        data = next(d for p, d in self.modules.items() if p.parent.name.startswith("s618"))
        status = VERIFY.verify_module(data, self.blobs)
        self.assertFalse(status["trace_strings"]["verified"])
        self.assertFalse(status["linea_obturador"]["verified"])

    def test_out_of_range_and_missing_terminator_are_rejected(self):
        self.assertFalse(VERIFY.check_string(b"abc", hex(VERIFY.BASE), "abc"))
        self.assertFalse(VERIFY.check_string(b"abc\0", hex(VERIFY.BASE - 1), "abc"))
        self.assertFalse(VERIFY.check_string(b"abc\0", hex(VERIFY.BASE + 4), ""))


if __name__ == "__main__":
    unittest.main()
