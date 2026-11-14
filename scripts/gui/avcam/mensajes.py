#!/usr/bin/env python3
"""Mensajes de CamMgr (cola 0x30001, im.elf → av-cam) y de av-cam hacia ObjCamera (cola 0x20002), tal como se ven en avcam.jsonl (14-11-2026).

Formato observado (INFERENCIA, 17 mensajes del arranque por defecto; ver docs/gui/g22-avcam-puente.md §5.17):
    {u8 tipo, u8 0, u16 id (LE), u32 seq | 0x80000000 (LE), carga…}
  tipo 5 = orden de ajuste de ObjCamera a CamMgr; tipo 0 = petición con respuesta; tipo 1 = respuesta de av-cam (carga {estado u8 = 0, 0xf0, 0, 0, datos…});
  tipo 4 = notificación espontánea de av-cam (única vista: id 0x1016, carga {0,0,0,0,1}).
`seq` empieza en 2 y sube de uno en uno por orden; la respuesta repite id y seq.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

TIPO_AJUSTE, TIPO_PETICION, TIPO_RESPUESTA, TIPO_NOTIF = 5, 0, 1, 4
# ids vistos en el arranque por defecto → ¿contesta av-cam? (medido: respuesta en 0x20002 con el mismo id y seq)
ORDENES = {
    0x40EC: ("ajuste", False), 0x40EB: ("ajuste", False), 0x40F5: ("ajuste", False), 0x4074: ("ajuste múltiple (3 pares id/seq)", False),
    0x405C: ("ajuste", False), 0x4050: ("ajuste", False), 0x408D: ("ajuste", False), 0x4036: ("ajuste con respuesta {0, 0xf0, 0, 0, 0, 2, 1, 0}", True),
    0x3024: ("petición", False), 0x302A: ("petición con respuesta", True), 0x401B: ("ajuste con respuesta", True), 0x4049: ("ajuste con respuesta (CAMLIRO)", True),
}


@dataclass(frozen=True)
class Mensaje:
    tipo: int
    id: int
    seq: int
    carga: bytes = b""


def codifica(m: Mensaje) -> bytes:
    return struct.pack("<BBHI", m.tipo, 0, m.id, (m.seq | 0x80000000) & 0xFFFFFFFF) + m.carga


def decodifica(b: bytes) -> Mensaje:
    if len(b) < 8:
        raise ValueError("mensaje de CamMgr/av-cam de menos de 8 bytes")
    tipo, _, id_, seq = struct.unpack_from("<BBHI", b)
    return Mensaje(tipo, id_, seq & 0x7FFFFFFF, bytes(b[8:]))


def respuesta(orden: Mensaje, datos: bytes = b"") -> Mensaje:
    """Respuesta de av-cam a una orden (estado 0, 0xf0 y los datos, como las vistas para 0x4049/0x4036/0x302a/0x401b)."""
    return Mensaje(TIPO_RESPUESTA, orden.id, orden.seq, b"\x00\xf0\x00\x00" + datos)
