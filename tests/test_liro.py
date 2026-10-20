import struct
import unittest

from src.liro import parse_dispatch, parse_header


class LiroTests(unittest.TestCase):
    def header(self) -> bytes:
        data = bytearray(256)
        struct.pack_into('<3I', data, 0, 0xEA00000A, 0x4C49524F, 4)
        struct.pack_into('<9I', data, 12, *(0x1000 + x for x in
                         (0x44, 0x58, 0xB4, 0x68, 0x78, 0x88, 0x98, 0x9C, 0xA0)))
        return bytes(data)

    def test_header_keeps_declared_coordinates(self) -> None:
        header = parse_header(self.header(), 0x1000)
        self.assertEqual(header['version'], 4)
        self.assertEqual(header['entry_main'], 0x1058)
        self.assertEqual(header['descriptor_file_offset'], 0xB4)

    def test_invalid_magic_rejected(self) -> None:
        data = bytearray(self.header())
        data[4:8] = b'ELF!'
        with self.assertRaises(ValueError):
            parse_header(bytes(data), 0x1000)

    def test_short_header_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_header(b'LIRO', 0x1000)

    def test_unmapped_entry_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_header(self.header(), 0x2000)

    def test_dispatch_preserves_thumb_and_unknown_flag(self) -> None:
        data = bytearray(128)
        struct.pack_into('<3I', data, 0, 0x40E3, 0x1041, 0)
        result = parse_dispatch(bytes(data), 0, 1, 0x1000)
        self.assertEqual(result, [{'command_id': 0x40E3, 'handler_address': 0x1041,
                                  'handler_file_offset': 64, 'thumb': 1, 'flag': 0}])

    def test_truncated_dispatch_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_dispatch(b'\0' * 12, 0, 2, 0)

    def test_duplicate_commands_rejected(self) -> None:
        data = bytearray(128)
        struct.pack_into('<6I', data, 0, 0x40E3, 0x1041, 0, 0x40E3, 0x1045, 1)
        with self.assertRaises(ValueError):
            parse_dispatch(bytes(data), 0, 2, 0x1000)
