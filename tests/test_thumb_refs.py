import struct
import unittest

from src.thumb_refs import find_candidates


class ThumbReferenceTests(unittest.TestCase):
    def fixture(self, register: int = 3) -> bytes:
        data = bytearray(24)
        struct.pack_into('<HH', data, 0, 0x4B03, 0x4478 | register)
        struct.pack_into('<i', data, 16, 0x1234 - 6)
        return bytes(data)

    def test_pc_relative_literal_candidate(self) -> None:
        result = find_candidates(self.fixture(), 0, 4, {0x1234})
        self.assertEqual(result, [{'add_file_offset': 2, 'load_file_offset': 0,
                                   'literal_file_offset': 16, 'target_file_offset': 0x1234}])

    def test_different_register_is_not_a_reference(self) -> None:
        self.assertEqual(find_candidates(self.fixture(2), 0, 4, {0x1234}), [])

    def test_truncated_literal_is_not_read(self) -> None:
        self.assertEqual(find_candidates(self.fixture()[:4], 0, 4, {0x1234}), [])

    def test_invalid_scan_bounds_rejected(self) -> None:
        with self.assertRaises(ValueError):
            find_candidates(self.fixture(), -1, 100, {0x1234})
