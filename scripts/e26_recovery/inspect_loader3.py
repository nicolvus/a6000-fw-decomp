"""Inspect the backed-up INFO records and the contiguous Loader3 candidate."""

import argparse
import hashlib
import json
import struct
from pathlib import Path


def inspect(data: bytes) -> dict:
    base = 0x18000
    if data[base:base + 4] != b'INFO' or len(data) < 0x42800:
        raise ValueError('respaldo incompatible o truncado')
    page_size = struct.unpack_from('<I', data, base + 8)[0]
    records = []
    for index in (5, 6):
        offset = base + index * 0x40
        fields = struct.unpack_from('<6I', data, offset)
        name = data[offset + 0x28:offset + 0x40].split(b'\0', 1)[0]
        if name != b'Loader3.bin':
            raise ValueError('INFO no identifica Loader3')
        records.append({'index': index, 'location': fields[:4], 'pages': fields[4], 'next': fields[5]})
    if page_size != 0x800 or records[0]['next'] != 6 or records[1]['next'] != 0:
        raise ValueError('geometría o cadena INFO inesperada')
    candidate = data[0x22800:0x42800]
    if len(candidate) != sum(int(record['pages']) for record in records) * page_size:
        raise ValueError('el tamaño del candidato no coincide con INFO')
    return {'page_size': page_size, 'records': records, 'candidate_offset': 0x22800,
            'candidate_length': len(candidate), 'candidate_sha256': hashlib.sha256(candidate).hexdigest(),
            'scope': 'The physical mapping and integrity remain unverified.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    print(json.dumps(inspect(parser.parse_args().backup.read_bytes()), indent=2))


if __name__ == '__main__':
    main()
