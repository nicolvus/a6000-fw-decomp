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
