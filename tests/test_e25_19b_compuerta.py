"""E25-19b: hechos de la compuerta de eventos (0x43afc544) comprobados por bytes de av-cam.bin."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from e25_19b_callers import callers
from e25_19b_dis import BIN, dis

pytestmark = pytest.mark.skipif(not BIN.exists(), reason="falta av-cam.bin")


def first(addr: int) -> str:
    return dis(BIN.read_bytes(), addr, 4)[0].split(": ", 1)[1]


def test_campos_de_la_compuerta():
    assert first(0x43AFC15A) == "ldrb.w r0, [r0, #0x24]"  # bloqueado
    assert first(0x43AFBF44) == "ldr r0, [r0, #0x1c]"  # id de grupo de M
    assert first(0x43AE75DC) == "ldr r0, [r0]"  # cap = [M]
    d = "\n".join(dis(BIN.read_bytes(), 0x43AFC160, 0x10))
    assert "[r0, #0x2d]" in d and "[r0, #0x2c]" in d and "movhs r0, #0" in d  # en_vuelo < max


def test_bloqueo_de_grupo_solo_desde_un_sitio():
    c = callers(BIN.read_bytes(), {0x437E52B0, 0x437E54B4})
    assert c[0x437E52B0] == [0x437DE594] and c[0x437E54B4] == [0x437DE134]


def test_compuerta_motivos_y_decodificacion():
    import struct

    from e25_19b_compuerta import decode_gestor, decode_nodo, motivo

    blk = bytearray(0x40)
    struct.pack_into("<III", blk, 0x14, 0x43ED8E5C, 0x43ED8E5C, 1)  # cola con un nodo
    blk[0x2C], blk[0x2D] = 1, 1  # máximo 1, en vuelo 1 (medido en el grupo 1 durante 4 s)
    g = decode_gestor(bytes(blk))
    assert (g["cola"], g["max_vuelo"], g["en_vuelo"], g["bloqueado"], g["diferidas"]) == (1, 1, 1, 0, 0)
    assert motivo(g, []) == "difiere:limite_vuelo"
    g["en_vuelo"] = 0
    assert motivo(g, []) == "acepta:en_vuelo_0"
    g["habilitado"] = 1  # la coincidencia solo aplica con E+0x2e activo
    nodo = decode_nodo(struct.pack("<IIIIBB", 0, 0, 0x43EEB0E8, 0, 0, 1) + bytes(18))
    assert nodo == {"M": 0x43EEB0E8, "pendiente": 0, "b9": 1}
    assert motivo(g, [nodo]).startswith("indeterminado:coincidencia")
    assert motivo(g, [nodo], b5490=1) == "difiere:entrada_pendiente_coincide"
    g["bloqueado"] = 1
    assert motivo(g, [nodo]) == "difiere:bloqueado"


def test_bytes_de_la_compuerta_y_la_liberacion():
    assert first(0x437E5DE8 + 2) == "ldrb.w r1, [r0, #0x2d]"  # Done(E): en_vuelo--
    d = "\n".join(dis(BIN.read_bytes(), 0x437E5E18, 6))
    assert "subs r1, #1" in d and "strb.w r1, [r0, #0x2d]" in d
    assert first(0x437E5336) == "strb.w r2, [r4, #0x2c]"  # constructor: máximo en vuelo = 1
    c = callers(BIN.read_bytes(), {0x437E5DE8, 0x437E611C})
    assert c[0x437E5DE8] == [0x437E60BE, 0x437E61A2] and c[0x437E611C] == [0x437E5638, 0x437E577A]


def test_esperas_osal_son_infinitas_y_los_candidatos_las_alcanzan():
    from e25_19b_esperas import buscar, wrappers

    d = BIN.read_bytes()
    wr = wrappers(d)
    assert sorted(wr.values()) == ["osal_rcv_msg_tmo", "osal_sig_sem", "osal_snd_msg", "osal_wai_sem_tmo"]
    assert "mov.w r1, #-1" in "\n".join(dis(d, 0x436CEAD6, 4))  # timeout infinito antes de wai_sem
    p = buscar(d, 0x437F00A4, 6, wr)["primitivas"]
    assert "osal_wai_sem_tmo" in p and "osal_rcv_msg_tmo" in p
