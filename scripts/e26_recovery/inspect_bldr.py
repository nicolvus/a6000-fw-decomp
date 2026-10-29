"""Describe the historical E26 BLDR dump without inventing lost USB frame identities."""

import argparse
import hashlib
import json
import struct
from pathlib import Path


def inspect_bldr(data: bytes) -> dict:
    # shortcut: this is the historical 480 KiB layout hypothesis, not a generic NAND parser.
    if (len(data) != 0x78000 or data[:4] != b'EXBL'
            or data[0x18000:0x18004] != b'INFO'
            or struct.unpack_from('<I', data, 0x18008)[0] != 0x800):
        raise ValueError('formato distinto del respaldo histórico E26')
    chunks = []
    for number, (offset, size) in enumerate(((0, 0x18000), (0x18000, 0x20000),
                                           (0x38000, 0x20000), (0x58000, 0x20000))):
        chunks.append({'ordinal_surviving': number, 'offset': offset, 'length': size,
                       'sha256': hashlib.sha256(data[offset:offset + size]).hexdigest(),
                       'physical_block': None,
                       'status': 'conditional boundary; original frame headers not retained'})
    fragments = []
    runtime = 0xc01f0000
    for index in (5, 6):
        die, plane, block, page, pages, next_record = struct.unpack_from(
            '<6I', data, 0x18000 + index * 0x40)
        length = pages * 0x800
        fragments.append({'info_index': index, 'die': die, 'plane': plane, 'block': block,
                          'page': page, 'pages': pages, 'next': next_record,
                          'runtime_start': runtime, 'length': length,
                          'source_offset': 0x22800 if index == 5 else None,
                          'status': ('prefix located by INFO; physical identity inferred'
                                     if index == 5 else 'plane 1 not explicitly acquired by BLDR')})
        runtime += length
    return {'backup_sha256': hashlib.sha256(data).hexdigest(), 'backup_length': len(data),
            'assumptions': ['64 pages/block, 2048 normal bytes/page, 1536 safe bytes/page',
                            'safe block succeeded and observed INFO begins first surviving normal block'],
            'requested_frames': 5, 'conditional_surviving_normal_frames': 3,
            'conditional_missing_normal_frames': 1, 'lost_frame_ordinal': None,
            'physical_mapping_verified': False, 'chunks': chunks,
            'loader3_fragments': fragments,
            'scope': 'No raw image, no OOB/ECC, no saved block IDs or failed-frame sizes. '
                     'A corrected-ECC warning can be discarded as an error by this payload.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    print(json.dumps(inspect_bldr(parser.parse_args().backup.read_bytes()), indent=2))


if __name__ == '__main__':
    main()
