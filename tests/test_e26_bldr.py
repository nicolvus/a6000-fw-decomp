import struct

import pytest

from scripts.e26_recovery.inspect_bldr import inspect_bldr


def test_bldr_does_not_invent_the_lost_frame_or_plane_one():
    data = bytearray(0x78000)
    data[:4] = b'EXBL'
    data[0x18000:0x18004] = b'INFO'
    struct.pack_into('<I', data, 0x18008, 0x800)
    struct.pack_into('<6I', data, 0x18140, 0, 0, 2, 21, 43, 6)
    struct.pack_into('<6I', data, 0x18180, 0, 1, 2, 0, 21, 0)
    result = inspect_bldr(bytes(data))
    assert result['conditional_missing_normal_frames'] == 1
    assert result['physical_mapping_verified'] is False
    assert result['loader3_fragments'][1]['source_offset'] is None
    assert result['loader3_fragments'][1]['runtime_start'] == 0xc0205800
    assert result['loader3_fragments'][1]['length'] == 0xa800
    assert result['chunks'][2]['physical_block'] is None
    with pytest.raises(ValueError, match='formato'):
        inspect_bldr(bytes(data[:-1]))
