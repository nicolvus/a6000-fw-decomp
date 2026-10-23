"""Resolver el PLT ARM observado en libObj.so, con veneers Thumb opcionales."""

import struct


def _immediate(word: int) -> int:
    rotate = ((word >> 8) & 15) * 2
    value = word & 255
    return ((value >> rotate) | (value << (32 - rotate))) & 0xffffffff


def resolve_plt(data: bytes, base: int, offset: int, size: int,
                got: dict[int, str]) -> dict[int, str]:
    entries = {}
    for position in range(offset, offset + size - 11, 4):
        first, second, third = struct.unpack_from("<III", data, position)
        if (first & 0xfffff000, second & 0xfffff000, third & 0xfffff000) != (
            0xe28fc000, 0xe28cc000, 0xe5bcf000,
        ):
            continue
        address = base + position - offset
        slot = (address + 8 + _immediate(first) + _immediate(second) + (third & 0xfff)) & 0xffffffff
        if slot in got:
            entries[address] = got[slot]
            if position >= offset + 4 and data[position - 4:position] == bytes.fromhex("78 47 c0 46"):
                entries[address - 4] = got[slot]
    return entries
