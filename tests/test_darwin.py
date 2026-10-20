import struct
import unittest

from src.darwin import decode_tbb, inspect_rom


class DarwinTableTests(unittest.TestCase):
    def test_thumb_pc_is_not_word_aligned_for_tbb(self) -> None:
        # TBB at base+2 uses PC=base+6, unlike an aligned literal load.
        image = bytearray(32)
        struct.pack_into('<HH', image, 2, 0xE8DF, 0xF001)
        image[6:10] = bytes([2, 3, 4, 5])
        self.assertEqual(decode_tbb(bytes(image), 0x4200, 0x4202, 4),
                         [0x420A, 0x420C, 0x420E, 0x4210])

    def test_truncated_table_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            decode_tbb(bytes.fromhex('dfe801f002'), 0x4200, 0x4200, 4)

    def test_non_tbb_instruction_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            decode_tbb(bytes(32), 0x4200, 0x4200, 4)

    def test_destination_outside_rom_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            decode_tbb(bytes.fromhex('dfe801f0ff'), 0x4200, 0x4200, 1)

    def test_invalid_address_and_count_are_rejected(self) -> None:
        for address, count in [(0x41FE, 4), (0x4201, 4), (0x4200, 0)]:
            with self.subTest(address=address, count=count), self.assertRaises(ValueError):
                decode_tbb(bytes(32), 0x4200, address, count)

    def test_unknown_or_modified_source_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            inspect_rom(bytes(32))
