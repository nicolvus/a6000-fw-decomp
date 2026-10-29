"""Compare TPZL tables and an in-memory 512-byte repack; never writes firmware."""

import argparse
import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.e25_27.tpzl import TpzlImage, decode_block


def repack(image: TpzlImage) -> bytes:
    start = (image.toc_offset + len(image.entries) * 8 + 511) // 512 * 512
    result = bytearray(image.data[:image.toc_offset])
    result.extend(bytes(start - len(result)))
    cursor = start
    for index, (_, size) in enumerate(image.entries):
        block = image.block(index)
        padded = (size + 511) // 512 * 512
        struct.pack_into('<II', result, image.toc_offset + index * 8, cursor, padded)
        result.extend(block)
        result.extend(b'\xff' * (padded - len(block)))
        cursor += padded
    return bytes(result)


def compare(original: bytes, modified: bytes) -> dict:
    old, new = TpzlImage.parse(original), TpzlImage.parse(modified)
    aligned = TpzlImage.parse(repack(new))
    if len(old.entries) != len(new.entries) or old.block_size != new.block_size:
        raise ValueError('Las imágenes no tienen geometría comparable')
    changed = []
    for i in range(len(new.entries)):
        before = decode_block(old.block(i), old.block_size)
        after = decode_block(new.block(i), new.block_size)
        if after != decode_block(aligned.block(i), aligned.block_size):
            raise ValueError(f'El repack altera el bloque {i}')
        if before != after:
            changed.append(i)
    sample = sorted({0, 1, 48, 49, 57, 58, len(new.entries) - 1} & set(range(len(new.entries))))
    def entry(image: TpzlImage, index: int) -> dict:
        offset, size = image.entries[index]
        return {'offset': offset, 'size': size, 'residue': offset % 512,
                'mapped_sectors': (size + (offset % 512) + 511) // 512}
    return {
        'blocks': len(new.entries), 'changed_decompressed_blocks': changed,
        'residues': {name: dict(collections.Counter(off % 512 for off, _ in image.entries))
                     for name, image in [('original', old), ('modified', new), ('aligned', aligned)]},
        'sizes': {'original': len(original), 'modified': len(modified), 'aligned': len(aligned.data)},
        'aligned_sha256': hashlib.sha256(aligned.data).hexdigest(),
        'samples': [{'block': i, **{name: entry(image, i) for name, image in
                    [('original', old), ('modified', new), ('aligned', aligned)]}} for i in sample],
        'scope': 'Sector count models muminlzp_request; it does not emulate LDEC or hardware.',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('modified', type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.original.read_bytes(), args.modified.read_bytes()), indent=2))


if __name__ == '__main__':
    main()
