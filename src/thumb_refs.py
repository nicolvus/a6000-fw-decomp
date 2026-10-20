"""Candidatos Thumb LDR literal + ADD PC; no demuestra flujo ni uso en ejecución."""

import argparse
import hashlib
import json
import struct
from pathlib import Path


def find_candidates(data: bytes, start: int, end: int,
                    targets: set[int]) -> list[dict[str, int]]:
    if start < 0 or end > len(data) or start > end or start % 2 or end % 2:
        raise ValueError('límites de exploración inválidos')
    result = []
    for offset in range(start, end - 1, 2):
        word = struct.unpack_from('<H', data, offset)[0]
        if word & 0xFFF8 != 0x4478:
            continue
        register = word & 7
        for load in range(max(start, offset - 96), offset, 2):
            instruction = struct.unpack_from('<H', data, load)[0]
            if instruction & 0xF800 != 0x4800 or (instruction >> 8) & 7 != register:
                continue
            literal = ((load + 4) & ~3) + (instruction & 255) * 4
            if literal + 4 > len(data):
                continue
            target = (offset + 4 + struct.unpack_from('<i', data, literal)[0]) & 0xFFFFFFFF
            if target in targets:
                result.append({'add_file_offset': offset, 'load_file_offset': load,
                               'literal_file_offset': literal, 'target_file_offset': target})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--start', type=lambda v: int(v, 0), required=True)
    parser.add_argument('--end', type=lambda v: int(v, 0), required=True)
    parser.add_argument('--target', type=lambda v: int(v, 0), action='append', required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.binary.resolve():
        parser.error('la salida no puede sobrescribir el binario')
    data = args.binary.read_bytes()
    result = {'binary': str(args.binary), 'sha256': hashlib.sha256(data).hexdigest(),
              'method': 'Thumb16 LDR literal + ADD PC, candidate-only',
              'limitations': ['Only applicable where file offsets equal ELF virtual addresses',
                              'No control-flow or intervening register-clobber analysis',
                              'May match embedded data; validate decoded instructions independently'],
              'range': [args.start, args.end],
              'references': find_candidates(data, args.start, args.end, set(args.target))}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(f'{len(result["references"])} candidatos; validar mediante desensamblado')


if __name__ == '__main__':
    main()
