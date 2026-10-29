"""Actualización de los `.sum` de Sony (`tipo,crc32,tamaño,modo,...,ruta,`)."""
from __future__ import annotations

import zlib


class SumError(ValueError):
    """Línea de suma inválida o ruta no encontrada."""


def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def _fields(line: str) -> list[str]:
    return line.split(",")


def update(text: str, path: str, data: bytes) -> tuple[str, dict]:
    """Reescribe CRC-32 y tamaño de `path` conservando el resto de campos."""
    wanted = path
    out_lines: list[str] = []
    found = False
    detail: dict = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            out_lines.append(line)
            continue
        fields = _fields(line)
        if len(fields) < 11:
            raise SumError(f"línea de suma inválida: {line!r}")
        if fields[10] != wanted:
            out_lines.append(line)
            continue
        if found:
            raise SumError(f"ruta duplicada en el sum: {wanted}")
        found = True
        detail = {
            "path": wanted,
            "line_before": line,
            "crc32_before": fields[1],
            "size_before": fields[2],
        }
        fields[1] = f"{crc32(data):08x}"
        fields[2] = f"{len(data):08x}"
        new_line = ",".join(fields)
        if len(new_line) != len(line):
            raise SumError("la línea cambiaría de longitud")
        out_lines.append(new_line)
        detail.update({
            "line_after": new_line,
            "crc32_after": fields[1],
            "size_after": fields[2],
        })
    if not found:
        raise SumError(f"ruta no encontrada en el sum: {wanted}")
    result = "\n".join(out_lines)
    if text.endswith("\n"):
        result += "\n"
    return result, detail


def verify(text: str, path: str, data: bytes) -> bool:
    for line in text.splitlines():
        fields = _fields(line)
        if len(fields) >= 11 and fields[10] == path:
            return fields[1] == f"{crc32(data):08x}" and fields[2] == f"{len(data):08x}"
    raise SumError(f"ruta no encontrada en el sum: {path}")
