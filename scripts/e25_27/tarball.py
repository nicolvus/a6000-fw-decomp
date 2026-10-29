"""Tar de `firmware.tar`: reescritura conservadora con miembros de tamaño distinto.

`firmware.tar` es un ustar con 105 miembros regulares.  Para el firmware integrado
solo cambian `0700_part_image/dev/nflasha3` (la partición TPZL recompuesta), su
suma `0701_part_image_sum/part_image.sum`, `0640_darwin/darwin_core.bin` y
`0641_darwin_sum/darwin.sum`.  Este módulo conserva el orden, las cabeceras y los
campos de cada miembro; solo reescribe tamaño y checksum de los reemplazados.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

BLOCK = 512


class TarError(ValueError):
    """Tar inválido o miembro no soportado."""


def _parse_number(field: bytes) -> int:
    if field and field[0] & 0x80:  # base-256 (GNU)
        value = int.from_bytes(field, "big", signed=True)
        return value & ((1 << (len(field) * 8 - 1)) - 1)
    text = field.split(b"\0", 1)[0].strip()
    if not text:
        return 0
    try:
        return int(text, 8)
    except ValueError as exc:
        raise TarError(f"campo numérico inválido: {field!r}") from exc


def _set_number(field: bytes, value: int) -> bytes:
    if value < 0:
        raise TarError("valor negativo")
    width = len(field) - 1
    text = f"{value:0{width}o}".encode("ascii")
    if len(text) > width:
        raise TarError(f"valor {value} no cabe en {len(field)} B")
    return text + b"\0"


def _checksum(header: bytes) -> int:
    raw = bytearray(header)
    raw[148:156] = b" " * 8
    return sum(raw)


@dataclass(frozen=True)
class TarEntry:
    name: str
    header: bytes
    data: bytes
    offset: int
    typeflag: bytes

    @property
    def size(self) -> int:
        return len(self.data)


def parse(data: bytes) -> tuple[list[TarEntry], bytes]:
    entries: list[TarEntry] = []
    pos = 0
    while pos + BLOCK <= len(data):
        header = data[pos:pos + BLOCK]
        if header == b"\0" * BLOCK:
            break
        name = header[:100].split(b"\0", 1)[0].decode("utf-8", "replace")
        size = _parse_number(header[124:136])
        typeflag = header[156:157]
        if typeflag not in (b"0", b"\0", b"5", b"7"):
            raise TarError(f"tipo de miembro no soportado {typeflag!r}: {name}")
        if typeflag == b"5" and size != 0:
            raise TarError(f"directorio con datos: {name}")
        body = data[pos + BLOCK:pos + BLOCK + size]
        if len(body) != size:
            raise TarError(f"miembro truncado: {name}")
        entries.append(TarEntry(name, header, body, pos, typeflag))
        pos += BLOCK + ((size + BLOCK - 1) // BLOCK) * BLOCK
    if not entries:
        raise TarError("tar sin miembros")
    return entries, data[pos:]


def _rebuild_header(header: bytes, size: int) -> bytes:
    out = bytearray(header)
    out[124:136] = _set_number(bytes(out[124:136]), size)
    out[148:156] = b" " * 8
    value = _checksum(bytes(out))
    text = f"{value:06o}".encode("ascii")
    if len(text) != 6:
        raise TarError("checksum fuera de rango")
    out[148:156] = text + b"\0 "
    return bytes(out)


def rebuild(data: bytes, replacements: dict[str, bytes]) -> tuple[bytes, list[dict]]:
    """Reemplaza miembros por nombre conservando cabeceras y orden."""
    entries, trailing = parse(data)
    names = {entry.name for entry in entries}
    missing = set(replacements) - names
    if missing:
        raise TarError(f"miembros no encontrados: {sorted(missing)}")
    out = bytearray()
    info: list[dict] = []
    for entry in entries:
        if entry.name in replacements:
            body = replacements[entry.name]
            out += _rebuild_header(entry.header, len(body))
            out += body
            out += b"\0" * ((-len(body)) % BLOCK)
            info.append({
                "name": entry.name,
                "offset_old": entry.offset,
                "size_old": entry.size,
                "size_new": len(body),
                "sha256_old": hashlib.sha256(entry.data).hexdigest(),
                "sha256_new": hashlib.sha256(body).hexdigest(),
            })
        else:
            out += entry.header
            out += entry.data
            out += b"\0" * ((-len(entry.data)) % BLOCK)
    out += trailing
    result = bytes(out)
    # Comprobación estructural: mismos nombres, mismo orden, mismos bytes no tocados.
    check, trailing_check = parse(result)
    if [e.name for e in check] != [e.name for e in entries]:
        raise TarError("el tar reconstruido cambia el orden de miembros")
    if trailing_check != trailing:
        raise TarError("el tar reconstruido cambia el relleno final")
    for old, new in zip(entries, check):
        if old.name in replacements:
            if new.data != replacements[old.name]:
                raise TarError(f"miembro {old.name} no coincide")
        elif old.header != new.header or old.data != new.data:
            raise TarError(f"miembro no previsto alterado: {old.name}")
    return result, info
