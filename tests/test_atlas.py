import unittest

from src.atlas import (
    classify,
    parse_readelf,
    resolve_needed,
    structural_role,
    subsystem_map,
)


class AtlasTests(unittest.TestCase):
    def test_metadata_keeps_declared_dependencies_and_symbol_direction(self) -> None:
        text = '''  Type: DYN (Shared object file)
  Machine: ARM
  [ 8] .modinfo PROGBITS
 0x00000001 (NEEDED) Shared library: [libcamera.so]
 0x0000000e (SONAME) Library soname: [libdemo.so]
 0x0000001d (RUNPATH) Library runpath: [$ORIGIN]
  1: 00000000 0 FUNC GLOBAL DEFAULT UND captureStart
  2: 00000100 8 FUNC GLOBAL DEFAULT 8 local_entry
'''
        result = parse_readelf(text)
        self.assertEqual(result['needed'], ['libcamera.so'])
        self.assertEqual(result['imports'], ['captureStart'])
        self.assertEqual(result['exports'], ['local_entry'])
        self.assertEqual(result['runpath'], ['$ORIGIN'])

    def test_unknown_without_semantic_evidence(self) -> None:
        self.assertEqual(classify({'imports': [], 'exports': [], 'needed': []}), [])

    def test_versioned_import_is_recognized_without_losing_evidence(self) -> None:
        result = classify({'imports': ['socket@GLIBC_2.4'], 'exports': [], 'needed': []})
        self.assertEqual(result[0]['subsystem'], 'network')
        self.assertEqual(result[0]['evidence'], ['socket@GLIBC_2.4'])

    def test_capture_label_carries_observed_evidence(self) -> None:
        result = classify({'imports': ['CameraHardwareDiadem_takePicture'],
                           'exports': [], 'needed': []})
        self.assertEqual(result[0]['subsystem'], 'capture')
        self.assertIn('CameraHardwareDiadem_takePicture', result[0]['evidence'])
        self.assertEqual(result[0]['status'], 'INFERENCIA')

    def test_senser_is_service_not_image_sensor(self) -> None:
        result = classify({'imports': [], 'exports': ['SenserIfStart'], 'needed': []})
        self.assertEqual([r['subsystem'] for r in result], ['service'])

    def test_ambiguous_dependency_is_not_arbitrarily_selected(self) -> None:
        candidates = [{'path': 'a/libx.so', 'sha256': '1'},
                      {'path': 'b/libx.so', 'sha256': '2'}]
        result = resolve_needed('c/app', 'libx.so', candidates)
        self.assertEqual(result['status'], 'ambiguous')
        self.assertEqual(len(result['candidates']), 2)

    def test_same_directory_is_only_a_search_candidate(self) -> None:
        result = resolve_needed('a/app', 'libx.so',
                                [{'path': 'a/libx.so', 'sha256': '1'}])
        self.assertEqual(result['status'], 'candidate')
        self.assertEqual(result['basis'], 'same_directory')

    def test_missing_dependency_explicit(self) -> None:
        self.assertEqual(resolve_needed('a/app', 'missing.so', [])['status'], 'missing')

    def test_dynamic_executable_is_not_called_a_shared_library(self) -> None:
        metadata = {'elf_type': 'DYN (Position-Independent Executable file)',
                    'interpreter': '/lib/ld-linux.so.3', 'kernel_module': False}
        self.assertEqual(structural_role(metadata), 'executable')

    def test_subsystem_map_preserves_ambiguity(self) -> None:
        rows = [{'path': 'app', 'associations': [{'subsystem': 'capture'}]},
                {'path': 'lib1', 'associations': [{'subsystem': 'ui'}]},
                {'path': 'lib2', 'associations': []}]
        edges = [{'source': 'app', 'needed': 'libx', 'status': 'ambiguous',
                  'candidates': ['lib1', 'lib2']}]
        result = subsystem_map(rows, edges)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(r['ambiguous_references'] == 1 for r in result))
