"""E25-25 — canal de modalidad: paquete, copia Darwin y congelación por captura."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from e25_25 import channel as C


def test_paquete_de_22_bytes_y_offset():
    p = C.build_packet(0)
    assert len(p) == C.PACKET_LEN == 22
    assert p[C.PACKET_MODALITY] == 0
    assert C.build_packet(1)[C.PACKET_MODALITY] == 1


def test_conversion_de_campo():
    assert C.flag_from_field(0) == C.FLAG_EFCS
    assert C.flag_from_field(1) == C.FLAG_ELECTRONIC
    with pytest.raises(C.ChannelError):
        C.flag_from_field(2)


def test_copia_darwin_coloca_el_byte_en_s_mas_0x3e():
    p = C.build_packet(1)
    s = C.darwin_copy(p)
    assert s[0x00] == p[0]
    assert s[0x0E] == 1
    assert C.CapturePacket(p).darwin_flag == 1
    assert C.DARWIN_S + C.DARWIN_PACKET + C.DARWIN_MODALITY == 0x20003716


def test_plantilla_conserva_el_resto():
    template = bytes(range(22))
    p = C.build_packet(1, template=template)
    assert p[0] == template[0] and p[1] == template[1]
    assert p[0x0D] == template[0x0D] and p[0x15] == template[0x15]
    assert p[0x0E] == 1


def test_congelacion_por_captura():
    ch = C.ModalityChannel()
    ch.select(1)
    cap = ch.begin_capture()
    ch.select(0)  # el usuario cambia el menú durante la captura
    assert cap.flag == 1 and cap.darwin_flag == 1
    ch.end_capture()
    assert ch.begin_capture().flag == 0


def test_no_se_permite_doble_captura():
    ch = C.ModalityChannel()
    ch.begin_capture()
    with pytest.raises(C.ChannelError):
        ch.begin_capture()
    ch.end_capture()


def test_fallo_seguro_con_paquete_invalido():
    assert C.resolve_flag(None) == C.FLAG_EFCS
    assert C.resolve_flag(b"\xff" * C.PACKET_LEN) == C.FLAG_EFCS
    assert C.resolve_flag(C.build_packet(1)) == C.FLAG_ELECTRONIC
    with pytest.raises(C.ChannelError):
        C.flag_from_packet(b"\x00" * 21)


def test_campos_del_paquete():
    p = C.build_packet(0)
    assert C.packet_field(p, 0) == 0
    assert C.packet_u16(p, 2) == 0
    with pytest.raises(C.ChannelError):
        C.packet_field(p, 22)
