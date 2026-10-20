"""Read-only recovery of the verified Darwin phase tables; no device access."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

ROM_BASE = 0x4200
PROFILES = {
    '5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4':
        ('A6000 3.21', 0x2089C, 0x208E0, 0x209A2, 0x20734),
    '6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac':
        ('A6300 2.01', 0x23E16, 0x23E58, 0x23F2A, 0x23AF4),
}


def decode_tbb(image: bytes, base: int, address: int, count: int) -> list[int]:
    """Decode PC-relative Thumb TBB; PC is instruction address+4, unaligned."""
    offset = address - base
    if address % 2 or offset < 0 or count <= 0 or offset + 4 + count > len(image):
        raise ValueError('Invalid TBB bounds')
    first, second = struct.unpack_from('<HH', image, offset)
    if first != 0xE8DF or second & 0xFFF0 != 0xF000:
        raise ValueError('Expected TBB [PC, Rm]')
    targets = [address + 4 + 2 * value for value in image[offset + 4:offset + 4 + count]]
    if any(target < base or target >= base + len(image) for target in targets):
        raise ValueError('TBB destination outside ROM')
    return targets


def inspect_rom(image: bytes) -> dict[str, object]:
    """Accept only unchanged sources and preserve bytes alongside derived addresses."""
    sha = hashlib.sha256(image).hexdigest()
    if sha not in PROFILES:
        raise ValueError('Unknown or modified Darwin image')
    model, entry, instruction, end, initializer = PROFILES[sha]
    targets = decode_tbb(image, ROM_BASE, instruction, 4)
    references = []
    for offset in range(0, len(image) - 3, 2):
        value = struct.unpack_from('<I', image, offset)[0]
        if value in (entry | 1, initializer | 1):
            references.append({'rom_address': hex(ROM_BASE + offset), 'value': hex(value)})
    return {
        'status': 'VERIFICADO', 'model': model, 'source_sha256': sha,
        'rom_base': hex(ROM_BASE), 'function': hex(entry),
        'tbb_instruction': hex(instruction), 'table': hex(instruction + 4),
        'table_hex': image[instruction + 4 - ROM_BASE:instruction + 8 - ROM_BASE].hex(),
        'phase_destinations': dict(enumerate(map(hex, targets))),
        'callback_pointer_occurrences': references,
        'instruction_window_hex': image[entry - ROM_BASE:end - ROM_BASE].hex(),
        'method': 'Original ROM bytes; TBB PC+2*unsigned-byte; no hardware execution',
        'limitations': 'Pointer occurrences alone do not prove callback execution or curtain semantics',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_rom(args.rom.read_bytes()), indent=2))


if __name__ == '__main__':
    main()
