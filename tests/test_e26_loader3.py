import struct

import pytest

from scripts.e26_recovery.inspect_loader3 import inspect


def test_inspects_chain_and_rejects_broken_next():
    data = bytearray(0x42800)
    data[0x18000:0x18004] = b'INFO'
    struct.pack_into('<I', data, 0x18008, 0x800)
    for index, fields in ((5, (0, 0, 2, 21, 43, 6)), (6, (0, 1, 2, 0, 21, 0))):
        pos = 0x18000 + 0x40 * index
        struct.pack_into('<6I', data, pos, *fields)
        data[pos + 0x28:pos + 0x34] = b'Loader3.bin\0'
    assert inspect(bytes(data))['candidate_length'] == 0x20000
    struct.pack_into('<I', data, 0x18154, 0)
    with pytest.raises(ValueError, match='cadena'):
        inspect(bytes(data))


def test_matching_length_does_not_validate_image_integrity():
    data = bytearray(0x42800)
    data[0x18000:0x18004] = b'INFO'
    struct.pack_into('<I', data, 0x18008, 0x800)
    for index, fields in ((5, (0, 0, 2, 21, 43, 6)), (6, (0, 1, 2, 0, 21, 0))):
        pos = 0x18000 + 0x40 * index
        struct.pack_into('<9I', data, pos, *fields, 1, 0, 0xc01f0000)
        data[pos + 0x28:pos + 0x34] = b'Loader3.bin\0'
    result = inspect(bytes(data))
    assert result['records'][0]['checksum'] == 1
    assert result['candidate_sum32'] == 0
    assert result['sum32_matches_info'] is False
    assert result['physical_mapping_verified'] is False
    # Agreement with a heuristic checksum also cannot prove physical mapping.
    for index in (5, 6):
        struct.pack_into('<I', data, 0x18000 + index * 0x40 + 0x18, 0)
    assert inspect(bytes(data))['sum32_matches_info'] is True
    assert inspect(bytes(data))['physical_mapping_verified'] is False
