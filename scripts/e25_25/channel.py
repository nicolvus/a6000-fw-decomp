"""E25-25 — canal de modalidad por captura (modelo offline).

Transporte implementado por E25-24 y verificado aquí:

    selector +0x210 -> cap+0x41c -> pkt[0x0e] (mensaje 0x0c, 22 B)
                    -> Darwin S+0x30+0x0e = S+0x3e (0x20003716)

El byte se congela en la copia de `cap` que hace el constructor (0x43844e80,
`str.w r2,[r4,#0x41c]` desde la configuración global +0x210) y en el paquete
`0x0c` de esa captura.  Cambiar el menú después no altera la captura en curso.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

PACKET_LEN = 22
PACKET_MODALITY = 0x0E
CAP_FIELD = 0x41C
DARWIN_S = 0x200036D8
DARWIN_PACKET = 0x30
DARWIN_MODALITY = PACKET_MODALITY  # offset dentro de la copia S+0x30 -> 0x20003716
FLAG_EFCS = 0
FLAG_ELECTRONIC = 1


class ChannelError(ValueError):
    """Paquete o estado de modalidad inválido."""


def flag_from_field(value: int) -> int:
    """Campo EFCS +0x210 (0/1) al byte de modalidad de Darwin."""
    if value == 0:
        return FLAG_EFCS
    if value == 1:
        return FLAG_ELECTRONIC
    raise ChannelError(f"valor de modalidad no soportado: {value:#x}")


def flag_from_packet(packet: bytes) -> int:
    if len(packet) != PACKET_LEN:
        raise ChannelError(f"paquete de {len(packet)} B, esperado {PACKET_LEN}")
    value = packet[PACKET_MODALITY]
    if value not in (FLAG_EFCS, FLAG_ELECTRONIC):
        raise ChannelError(f"pkt[0x0e] no soportado: {value:#x}")
    return value


def build_packet(field_value: int, *, template: bytes | None = None) -> bytes:
    """Construye el `0x0c` de 22 B con el byte de modalidad en +0x0e.

    El resto de campos se conservan de `template` (paquete nativo) o a cero: el
    parche solo rellena +0x0e y replica `pkt[0]=0`; no reordena el paquete.
    """
    if template is None:
        packet = bytearray(PACKET_LEN)
    else:
        if len(template) != PACKET_LEN:
            raise ChannelError("plantilla de tamaño incorrecto")
        packet = bytearray(template)
    packet[PACKET_MODALITY] = flag_from_field(field_value)
    return bytes(packet)


def darwin_copy(packet: bytes) -> bytes:
    """Copia que hace Darwin en `0x17f8c` (S+0x30..S+0x45) desde el paquete.

    El analizador no copia byte a byte en orden: reproduce los destinos
    verificados en el desensamblado (S+0x30..0x3e y S+0xa0..0xa3).
    """
    if len(packet) != PACKET_LEN:
        raise ChannelError("paquete de tamaño incorrecto")
    s = bytearray(0xB0)  # copia relativa a S+0x30
    s[0x00] = packet[0x00]
    s[0x01] = packet[0x01]
    s[0x02:0x04] = packet[0x02:0x04]
    s[0x04:0x06] = packet[0x04:0x06]
    s[0x06] = packet[0x06]
    s[0x07] = packet[0x07]
    s[0x08:0x0A] = packet[0x08:0x0A]
    s[0x0A:0x0C] = packet[0x0A:0x0C]
    s[0x0D] = packet[0x0D]
    s[0x0E] = packet[0x0E]
    s[0x0F] = packet[0x0F]
    s[0x10] = packet[0x10]
    s[0x11] = packet[0x11]
    s[0x12] = packet[0x12]
    s[0x13] = packet[0x13]
    s[0x14] = packet[0x14]
    s[0x15] = packet[0x15]
    # Campos con bits insertados (0x18014-0x18052).
    s[0x16] = (s[0x16] & ~0x0C) | (((packet[0x0C] >> 6) & 0x03) << 2)
    s[0x12] = (s[0x12] & ~0x08) | (((packet[0x12] >> 3) & 0x01) << 3)
    s[0xA0] = (s[0xA0] & ~0x01) | (packet[0x12] & 0x01)
    s[0xA1] = packet[0x13]
    s[0xA2] = packet[0x14]
    s[0xA3] = packet[0x15]
    return bytes(s)


def resolve_flag(packet_or_none: bytes | None, *, fallback: int = FLAG_EFCS) -> int:
    """Fallo seguro: paquete ausente o inválido no habilita la ruta electrónica."""
    if packet_or_none is None:
        return fallback
    try:
        return flag_from_packet(packet_or_none)
    except ChannelError:
        return fallback


@dataclass(frozen=True)
class CapturePacket:
    """Copia inmutable del paquete de una captura."""

    packet: bytes

    @property
    def flag(self) -> int:
        return flag_from_packet(self.packet)

    @property
    def sram(self) -> bytes:
        return darwin_copy(self.packet)

    @property
    def darwin_flag(self) -> int:
        return self.sram[DARWIN_MODALITY]


@dataclass
class ModalityChannel:
    """Congela la modalidad al inicio de cada captura.

    `select` cambia la configuración global; `begin_capture` toma una copia.  Los
    cambios posteriores no afectan al paquete ya emitido.
    """

    field_value: int = 0
    capture: CapturePacket | None = None
    emitted: list[CapturePacket] = field(default_factory=list)
    _version: int = field(default=0, init=False)

    def select(self, field_value: int) -> int:
        flag_from_field(field_value)  # valida
        self.field_value = field_value
        self._version += 1
        return self.field_value

    def begin_capture(self, *, template: bytes | None = None) -> CapturePacket:
        if self.capture is not None:
            raise ChannelError("ya hay una captura activa")
        packet = build_packet(self.field_value, template=template)
        self.capture = CapturePacket(packet)
        self.emitted.append(self.capture)
        return self.capture

    def end_capture(self) -> None:
        if self.capture is None:
            raise ChannelError("no hay captura activa")
        self.capture = None

    @property
    def active(self) -> bool:
        return self.capture is not None


S_READERS: tuple[str, ...] = ()
"""Consumidores estáticos conocidos de S+0x3e en Darwin (barrido E25-25: ninguno)."""


def packet_field(packet: bytes, offset: int) -> int:
    if not 0 <= offset < len(packet):
        raise ChannelError("offset fuera del paquete")
    return packet[offset]


def packet_u16(packet: bytes, offset: int) -> int:
    if not 0 <= offset + 2 <= len(packet):
        raise ChannelError("offset fuera del paquete")
    return struct.unpack_from("<H", packet, offset)[0]
