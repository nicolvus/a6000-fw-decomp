import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.inventory import inspect_file, inventory


class InventoryTests(unittest.TestCase):
    def test_unreadable_file_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'blocked').write_bytes(b'x')
            with patch('src.inventory.inspect_file', side_effect=PermissionError('denied')):
                rows = inventory(root)
            self.assertEqual(rows[0]['status'], 'error')
            self.assertEqual(rows[0]['path'], 'blocked')

    def test_hash_and_unknown_responsibility(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'shutter.bin'
            path.write_bytes(b'unknown')
            row = inspect_file(path, Path(directory))
            self.assertEqual(row['sha256'], hashlib.sha256(b'unknown').hexdigest())
            self.assertEqual(row['responsibility'], 'desconocida')

    def test_elf_machine_uses_header_not_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'not-arm.bin'
            data = bytearray(64)
            data[:6] = b'\x7fELF\x01\x01'
            data[18:20] = (40).to_bytes(2, 'little')
            path.write_bytes(data)
            self.assertEqual(inspect_file(path, Path(directory))['architecture'], 'ARM')

    def test_no_symlinks_and_deterministic_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'b').write_bytes(b'x')
            (root / 'a').write_bytes(b'x')
            (root / 'link').symlink_to(root / 'a')
            self.assertEqual([r['path'] for r in inventory(root)], ['a', 'b'])

    def test_truncated_elf_not_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad'
            path.write_bytes(b'\x7fELF')
            self.assertEqual(inspect_file(path, Path(directory))['format'], 'unknown')
