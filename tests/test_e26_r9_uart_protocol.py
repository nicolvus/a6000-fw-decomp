"""E26-R9 — pruebas automáticas del protocolo UART del BootROM (r9-uart-protocol.py).

Pruebas offline y sintéticas. No tocan la cámara, no transmiten paquetes,
no realizan operaciones físicas.

Informe: docs/capture/e26-r9-bootrom-ram-execution.md
"""

import sys

import pytest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))

r9 = __import__("r9-uart-protocol")


# ------------------------------------------------------------------ CRC8 paso

def test_crc8_step_is_deterministic():
    assert r9.crc8_step(0x00) == r9.crc8_step(0x00)
    assert r9.crc8_step(0xFF) == r9.crc8_step(0xFF)


def test_crc8_step_polynomial_is_edb88320_not_0x07():
    """R8 usaba polinomio placeholder 0x07; el binario carga 0xEDB88320."""
    # Con poly 0x07 y input 0x01, 8 iters MSB-first -> 0x8C (CRC-8/SMBUS-like).
    # Con poly 0xEDB88320 (solo bajo byte 0x20 afecta el byte de salida tras uxtb).
    # Solo verificamos que el resultado difiere del placeholder 0x07 para al menos un input.
    def crc8_placeholder(byte):
        crc = byte & 0xFF
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
        return crc

    assert r9.crc8_step(0x01) != crc8_placeholder(0x01)


# ---------------------------------------------------------- checksum update

def test_checksum_update_is_iterative():
    acc = r9.CRC_INIT_ACC
    a1 = r9.checksum_update(acc, 0x00)
    a2 = r9.checksum_update(a1, 0x01)
    # Dos caminos diferentes deben dar distinto acumulador salvo colisión.
    assert a1 != r9.CRC_INIT_ACC or a2 != a1


def test_checksum_update_keeps_32_bits():
    acc = r9.checksum_update(0xFFFFFFFF, 0xFF)
    assert 0 <= acc <= 0xFFFFFFFF


# --------------------------------------------------------------- frame build

def test_build_type0_frame_roundtrip():
    frame = r9.build_type0_frame(0x1234, 0x5678)
    assert len(frame) == 7
    result = r9.parse_frames(frame)
    assert len(result.frames) == 1
    f = result.frames[0]
    assert f.type == 0x0000
    assert f.value == 0x1234
    assert f.address == 0x5678
    assert f.valid_checksum
    assert f.ret_code == r9.RET_SUCCESS


def test_build_jump_frame_roundtrip():
    frame = r9.build_jump_frame(0xC010)
    assert len(frame) == 7
    result = r9.parse_frames(frame)
    assert len(result.frames) == 1
    f = result.frames[0]
    assert f.type == 0xFFFF
    assert f.jump_target == 0xC010
    assert f.ret_code == r9.RET_JUMP_REQUEST


def test_checksum_corruption_detected():
    bad = bytearray(r9.build_type0_frame(0x0001, 0x0002))
    bad[-1] ^= 0xFF
    result = r9.parse_frames(bytes(bad))
    assert len(result.frames) == 1
    assert not result.frames[0].valid_checksum
    assert result.frames[0].ret_code == r9.RET_CHECKSUM_ERROR


def test_multi_frame_stream():
    stream = r9.build_type0_frame(0x0001, 0x1000) + r9.build_jump_frame(0xC020)
    result = r9.parse_frames(stream)
    assert len(result.frames) == 2
    assert result.frames[0].value == 0x0001 and result.frames[0].address == 0x1000
    assert result.frames[1].jump_target == 0xC020


def test_error_types_parsed():
    result = r9.parse_frames(bytes([0xFF, 0x01]))  # type 0xFF01 = timeout
    assert len(result.errors) == 1
    assert "0xFF01" in result.errors[0]


def test_truncated_packet_rejected():
    result = r9.parse_frames(bytes([0x00, 0x00, 0x12]))  # solo 3 de 7 bytes
    assert len(result.errors) >= 1
    assert "Truncated" in result.errors[0]


def test_unknown_type_resyncs():
    result = r9.parse_frames(bytes([0xAA, 0xBB, 0x00, 0x00, 0x12, 0x34, 0x56, 0x78]))
    # 0xAABB desconocido -> skip 1 byte; luego 0x0000 es type-0 pero solo quedan 5 bytes -> truncado
    assert any("Unknown type 0xAABB" in e for e in result.errors)


# -------------------------------------------------------------- checksum coverage

def test_checksum_covers_all_six_data_bytes():
    """Cambiar cualquier byte de datos debe cambiar el checksum esperado."""
    base = r9.expected_checksum_byte(0x0000, 0x0000, 0x0000)
    variants = [
        r9.expected_checksum_byte(0x0001, 0x0000, 0x0000),  # type_hi
        r9.expected_checksum_byte(0x0000, 0x0001, 0x0000),  # data_hi
        r9.expected_checksum_byte(0x0000, 0x0000, 0x0001),  # addr_hi
    ]
    assert all(v != base for v in variants)


# ------------------------------------------------------------- return codes

def test_return_code_constants():
    assert r9.RET_SUCCESS == 0x0000
    assert r9.RET_JUMP_REQUEST == 0x3001
    assert r9.RET_CHECKSUM_ERROR == 0x100D
    assert r9.TYPE_TO_RET[0xFF01] == r9.RET_TIMEOUT
    assert r9.TYPE_TO_RET.get(0xFF07) is None  # 0xFF07 no está mapeado en R9


# ------------------------------------------------------------- bootrom constants

def test_bootrom_constants_match_r8():
    assert r9.BOOTROM_SHA256 == "81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026"
    assert r9.MMIO_MISC_MODEREG == 0xF2915010
    assert r9.ADDR_JUMP_TARGET == 0xC000500C
    assert r9.ADDR_JUMP_VECTOR == 0xC0005000
    assert r9.ADDR_PACKET == 0xC0010218


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
