import struct

from scripts.e25_27.tpzl import encode_literal
from scripts.e26_recovery.compare_tpzl import compare


def test_repack_preserves_data_and_reports_offsets():
    block = encode_literal(b'A' * 4096)
    start = 512
    size = (len(block) + 255) // 256 * 256
    header = struct.pack('<4sIII', b'TPZL', 12, 24, 16)
    image = bytearray(header + bytes(8) + struct.pack('<IIII', start, size, start + size, size))
    image.extend(bytes(start - len(image)))
    image.extend((block + bytes(size - len(block))) * 2)
    result = compare(bytes(image), bytes(image))
    assert result['changed_decompressed_blocks'] == []
    assert result['residues']['aligned'] == {0: 2}
