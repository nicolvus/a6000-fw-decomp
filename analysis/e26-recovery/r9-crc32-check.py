#!/usr/bin/env python3
"""Offline check of the BootROM reflected CRC routine; no hardware access."""
import argparse
import hashlib
import struct
import zlib
from pathlib import Path

EXPECTED = '81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026'
POLY = 0xEDB88320


def rom_crc(data: bytes) -> int:
    state = 0xFFFFFFFF
    for byte in data:
        value = (state ^ byte) & 0xFF
        for _ in range(8):
            value = (value >> 1) ^ (POLY if value & 1 else 0)
        state = value ^ (state >> 8)
    return state ^ 0xFFFFFFFF


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('bootrom', type=Path)
    args = parser.parse_args()
    binary = args.bootrom.read_bytes()
    assert hashlib.sha256(binary).hexdigest() == EXPECTED
    assert struct.unpack_from('<I', binary, 0xC94)[0] == POLY
    for data in (b'', b'123456789', bytes(range(256)), bytes(range(255, -1, -1))):
        assert rom_crc(data) == zlib.crc32(data)
    assert rom_crc(b'123456789') == 0xCBF43926
    print('SHA-256, literal y CRC-32 reflejado: OK (4 vectores sintéticos)')


if __name__ == '__main__':
    main()
