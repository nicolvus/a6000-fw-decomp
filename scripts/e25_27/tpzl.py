"""TPZL (LZPT) de `nflasha3`: lectura, descompresión y reconstrucción determinista.

El formato está documentado en `references/fwtool/fwtool/archive/lzpt.py` y el
descompresor en `references/fwtool/fwtool/lz77/__init__.py`.  Aquí se reimplementa
solo lo necesario para reconstruir la partición sin depender de `fwtool` en tiempo
de ejecución; el resultado se contrasta con `fwtool` en la verificación del
contenedor.

Estructura:

    cabecera 16 B: "TPZL", blockSize=16, tocOffset=0x18, tocSize
    TOC: N pares (offset, size) little-endian
    datos: N bloques comprimidos; cada bloque produce 65536 B (2**blockSize)

Un bloque puede contener varios segmentos LZ77 terminados en `bd == 0`; el
descompresor los concatena hasta completar 65536 B.  Para recompresar se emite un
único segmento de literales, válido para cualquier contenido y determinista.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

MAGIC = b"TPZL"
HEADER_SIZE = 16
TOC_OFFSET = 0x18
DEFAULT_BLOCK_LOG2 = 16
ALIGN = 256
_LENGTHS = list(range(3, 17)) + [32, 64]


class TpzlError(ValueError):
    """Cabecera, TOC o bloque TPZL inválido."""


def _inflate_segment(block: bytes, pos: int) -> tuple[bytes, int]:
    """Descomprime un segmento LZ77 y devuelve (salida, posición siguiente)."""
    if pos >= len(block):
        raise TpzlError("segmento LZ77 truncado")
    kind = block[pos]
    pos += 1
    if kind == 0x0F:
        if pos + 3 > len(block):
            raise TpzlError("bloque sin comprimir truncado")
        size = struct.unpack_from("<H", block, pos + 1)[0]
        pos += 3
        if pos + size > len(block):
            raise TpzlError("bloque sin comprimir truncado")
        return block[pos:pos + size], pos + size
    if kind != 0xF0:
        raise TpzlError(f"tipo LZ77 desconocido: {kind:#x}")

    out = bytearray()
    while True:
        if pos >= len(block):
            raise TpzlError("flujo LZ77 sin terminador")
        flags = block[pos]
        pos += 1
        if flags == 0:
            if pos + 8 > len(block):
                raise TpzlError("grupo de 8 literales truncado")
            out += block[pos:pos + 8]
            pos += 8
            continue
        for bit in range(8):
            if not (flags >> bit) & 1:
                if pos >= len(block):
                    raise TpzlError("literal truncado")
                out.append(block[pos])
                pos += 1
                continue
            if pos + 2 > len(block):
                raise TpzlError("token de longitud/distancia truncado")
            b0, b1 = block[pos], block[pos + 1]
            pos += 2
            length = _LENGTHS[b0 >> 4]
            distance = ((b0 & 0x0F) << 8) | b1
            if distance == 0:
                return bytes(out), pos
            if distance > len(out):
                raise TpzlError(f"distancia {distance} mayor que la salida {len(out)}")
            start = len(out) - distance
            for i in range(length):
                out.append(out[start + i])
    return bytes(out), pos


def decode_block(block: bytes, target: int) -> bytes:
    """Descomprime un bloque completo hasta `target` bytes."""
    out = bytearray()
    pos = 0
    while len(out) < target:
        start = pos
        chunk, pos = _inflate_segment(block, pos)
        if pos <= start:
            raise TpzlError("segmento sin avance")
        out += chunk
    if len(out) != target:
        raise TpzlError(f"bloque de {len(out)} B, esperado {target} B")
    return bytes(out)


def encode_literal(data: bytes) -> bytes:
    """Segmento LZ77 de literales (sin coincidencias), terminado en `bd=0`."""
    out = bytearray([0xF0])
    i = 0
    while i + 8 <= len(data):
        out.append(0)                       # flags = 0: ocho literales
        out += data[i:i + 8]
        i += 8
    remaining = len(data) - i
    if remaining:
        out.append(1 << remaining)          # bits 0..remaining-1 = literal
        out += data[i:]
        out += b"\x00\x00"                  # token longitud 3 / distancia 0
    else:
        out += b"\x01\x00\x00"              # grupo vacío + terminador
    return bytes(out)


@dataclass(frozen=True)
class TpzlImage:
    """Vista inmutable de una partición TPZL."""

    data: bytes
    block_log2: int
    toc_offset: int
    entries: tuple[tuple[int, int], ...]

    @property
    def block_size(self) -> int:
        return 1 << self.block_log2

    @property
    def data_offset(self) -> int:
        return _align(self.toc_offset + len(self.entries) * 8)

    @classmethod
    def parse(cls, data: bytes) -> TpzlImage:
        if len(data) < HEADER_SIZE:
            raise TpzlError("archivo menor que la cabecera TPZL")
        magic, block_log2, toc_offset, toc_size = struct.unpack_from("<4sIII", data, 0)
        if magic != MAGIC:
            raise TpzlError(f"magia TPZL inesperada: {magic!r}")
        if not 12 <= block_log2 <= 20:
            raise TpzlError(f"blockSize fuera de rango: {block_log2}")
        if toc_size % 8:
            raise TpzlError("TOC de tamaño no múltiplo de 8")
        if toc_offset < HEADER_SIZE or toc_offset + toc_size > len(data):
            raise TpzlError("TOC fuera del archivo")
        entries = tuple(
            struct.unpack_from("<II", data, toc_offset + i)
            for i in range(0, toc_size, 8)
        )
        last = 0
        for index, (offset, size) in enumerate(entries):
            if offset < toc_offset + toc_size or offset >= len(data):
                raise TpzlError(f"bloque fuera del archivo: {offset:#x}+{size:#x}")
            if offset + size > len(data) and index != len(entries) - 1:
                raise TpzlError(f"bloque fuera del archivo: {offset:#x}+{size:#x}")
            if offset < last:
                raise TpzlError("bloques TPZL solapados o desordenados")
            last = offset + size
        return cls(data, block_log2, toc_offset, entries)

    def block(self, index: int) -> bytes:
        offset, size = self.entries[index]
        return self.data[offset:offset + size]

    def target_size(self, index: int) -> int:
        """Tamaño descomprimido del bloque (el último puede ser menor)."""
        return self.block_size

    def decompressed(self) -> bytes:
        out = bytearray()
        for index in range(len(self.entries)):
            out += decode_block(self.block(index), self.target_size(index))
        return bytes(out)

    def block_index(self, offset: int) -> int:
        index, _rem = divmod(offset, self.block_size)
        if index >= len(self.entries):
            raise TpzlError(f"offset {offset:#x} fuera de la partición")
        return index


def _align(value: int, align: int = ALIGN) -> int:
    return (value + align - 1) // align * align


def rebuild(image: TpzlImage, replacements: dict[int, bytes]) -> tuple[bytes, list[dict]]:
    """Reconstruye la partición cambiando solo los bloques indicados.

    `replacements` asocia índice de bloque con sus 65536 B descomprimidos.  El
    resto de bloques se copia byte a byte, sin recomprimir.  Los bloques nuevos se
    recompresan como literales y se alinean a 256 B.
    """
    blocks: list[bytes] = []
    info: list[dict] = []
    for index, (old_offset, old_size) in enumerate(image.entries):
        target = image.target_size(index)
        if index in replacements:
            raw = replacements[index]
            if len(raw) != target:
                raise TpzlError(
                    f"bloque {index}: {len(raw)} B, esperado {target} B"
                )
            compressed = encode_literal(raw)
            image.block(index)
            if decode_block(compressed, target) != raw:
                raise TpzlError(f"bloque {index}: la recompresión no reproduce el contenido")
            info.append({
                "block": index,
                "offset_old": old_offset,
                "size_old": old_size,
                "size_new": len(compressed),
                "recompressed": True,
            })
        else:
            compressed = image.block(index)
            info.append({
                "block": index,
                "offset_old": old_offset,
                "size_old": old_size,
                "size_new": old_size,
                "recompressed": False,
            })
        blocks.append(compressed)

    data_start = image.data_offset
    toc = bytearray()
    body = bytearray()
    cursor = data_start
    for compressed in blocks:
        padded_size = _align(len(compressed))
        toc += struct.pack("<II", cursor, padded_size)
        body += compressed
        body += b"\xFF" * (padded_size - len(compressed))
        cursor += padded_size

    header = struct.pack(
        "<4sIII", MAGIC, image.block_log2, image.toc_offset, len(toc)
    )
    prefix = bytearray(header)
    prefix += b"\x00" * (image.toc_offset - len(prefix))
    prefix += toc
    prefix += b"\x00" * (data_start - len(prefix))
    out = bytes(prefix) + bytes(body)
    rebuilt = TpzlImage.parse(out)
    if rebuilt.decompressed() != _apply(image, replacements):
        raise TpzlError("la partición reconstruida no reproduce el contenido previsto")
    for item in info:
        item["offset_new"] = rebuilt.entries[item["block"]][0]
    return out, info


def _apply(image: TpzlImage, replacements: dict[int, bytes]) -> bytes:
    out = bytearray()
    for index in range(len(image.entries)):
        if index in replacements:
            out += replacements[index]
        else:
            out += decode_block(image.block(index), image.target_size(index))
    return bytes(out)


def patch_decompressed(image: TpzlImage, patched: bytes) -> tuple[bytes, list[dict]]:
    """Sustituye el contenido descomprimido completo y recompone los bloques tocados."""
    original = image.decompressed()
    if len(patched) != len(original):
        raise TpzlError(f"tamaño distinto: {len(patched)} != {len(original)}")
    replacements: dict[int, bytes] = {}
    for index in range(len(image.entries)):
        lo = index * image.block_size
        hi = lo + image.block_size
        if patched[lo:hi] != original[lo:hi]:
            replacements[index] = patched[lo:hi]
    if not replacements:
        raise TpzlError("no hay ningún bloque distinto")
    return rebuild(image, replacements)
