"""E26-R77: orden temporal de la preparación y P4D en Darwin 3.21 (estático, por bytes)."""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DZ = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
capstone = pytest.importorskip("capstone")
pytestmark = pytest.mark.skipif(not DZ.is_file(), reason="firmware original ausente")
B = 0x4200


@pytest.fixture(scope="module")
def d() -> bytes:
    return DZ.read_bytes()


def _u32(d: bytes, a: int) -> int:
    return struct.unpack_from("<I", d, a - B)[0]


def _dis(d: bytes, a: int, n: int):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    return list(md.disasm(d[a - B:a - B + 4 * n], a))[:n]


def _calls(d: bytes, a: int, n: int) -> list[tuple[int, int]]:
    return [(i.address, int(i.op_str[1:], 16)) for i in _dis(d, a, n) if i.mnemonic in ("bl", "b.w")]


def _callers(d: bytes, t: int) -> list[int]:
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    out, a = [], B
    while a < B + len(d):
        ok = False
        for i in md.disasm(d[a - B:a - B + 0x1000], a):
            ok = True
            a = i.address + i.size
            if i.mnemonic in ("bl", "b.w") and i.op_str == f"#{t:#x}":
                out.append(i.address)
        if not ok:
            a += 2
    return out


def _seq(d: bytes, a: int, n: int) -> list[int]:
    out = []
    while d[a - B] < n:
        out.append(d[a - B])
        a += 1
    return out


def test_p4d_solo_con_tipo_1_o_2(d):
    t = [f"{i.mnemonic} {i.op_str}" for i in _dis(d, 0x20C90, 12)][:12]
    assert t[1:3] == ["bl #0x20c74", "cmp r0, #0"] and t[3] == "beq #0x20cb0"
    assert t[5:7] == ["cmp r0, #3", "beq #0x20cb0"]
    assert "mov.w r0, #0x234" in t and "b.w #0x51c0" in t


def test_cuatro_llamadores_de_p4d_y_sus_ids(d):
    assert _callers(d, 0x20c90) == [0x1F694, 0x1F8A2, 0x1F914, 0x20154]
    # (tabla, id) -> funcion de accion {id, funcion}
    assert _u32(d, 0x29868 + 8 * 0 + 4) == 0x1F68B
    assert _u32(d, 0x29868 + 8 * 10 + 4) == 0x1F88B
    assert _u32(d, 0x29868 + 8 * 13 + 4) == 0x1F8FD
    assert _u32(d, 0x29D0C + 8 * 7 + 4) == 0x2014D


def test_secuencias_de_las_maquinas_p4d(d):
    assert _seq(d, 0x297C0 - 0x29, 0x1A)[:4] == [0x18, 0x19, 0x00, 0x15]
    assert _seq(d, 0x297C0 - 0x14, 0x1A)[:2] == [0x01, 0x05]
    assert _seq(d, 0x29CF0 - 0x13, 10) == [0, 2, 3, 6, 9]
    assert _seq(d, 0x29CF0 - 0xD, 10) == [0, 4, 5, 6, 9]
    assert _seq(d, 0x29CF0 - 0x7, 10) == [0, 1, 4, 5, 6, 9]
    assert _seq(d, 0x29CF0 - 0x18, 10) == [0, 7, 8, 9]


def test_p4d_solo_se_arranca_desde_la_maquina_29cf0(d):
    assert _callers(d, 0x1F396) == [0x20126] and _callers(d, 0x1F3B6) == [0x2013A]
    assert _callers(d, 0x1FFCE) == [0x199CA]  # b.w desde 0x199b8
    assert sorted(_callers(d, 0x199B8)) == [0x17AC2, 0x18668, 0x191EC]
    assert sorted(_callers(d, 0x19998)) == [0x17E8E, 0x18642]


def test_armado_antes_de_arrancar_p4d_en_0x190fc(d):
    c = _calls(d, 0x190FC, 100)
    pos = {t: a for a, t in c}
    assert pos[0x18D6E] < pos[0x1E6BA] < pos[0x199B8] and pos[0x18FA0] < pos[0x18D6E]
    ins = {i.address: f"{i.mnemonic} {i.op_str}" for i in _dis(d, 0x190FC, 100)}
    assert ins[0x191E2] == "cmp r0, #3" and ins[0x191E4] == "beq #0x191f0"  # tipo 3 no arranca


def test_efcs_anula_acciones_previas(d):
    ins = [f"{i.mnemonic} {i.op_str}" for i in _dis(d, 0x196A2, 8)]
    assert ins[2] == "ldrb.w r1, [r1, #0x31]" and ins[3] == "lsls r2, r1, #0x1e"
    for a in (0x185EA, 0x1860C, 0x18636, 0x18690):  # acciones 02 03 04 06
        assert 0x196A2 in [t for _, t in _calls(d, a, 6)]
    # lista observada (pkt[0x0c]=0): S+0x32 = 0 o S+0x3c fuera de 1..4
    assert _seq(d, 0x28FDC - 0x54, 0x31) == [2, 9, 3, 4, 0xD, 0xA, 0xF, 6, 0x13, 0x14, 0x1A, 0x1C, 0x1F, 0x20, 0x30]
    assert _seq(d, 0x28FDC - 0x44, 0x31)[:11] == [2, 9, 3, 4, 0xA, 6, 0x13, 0x14, 0x1A, 0x1C, 0x1F]
    assert _seq(d, 0x28FDC - 0x34, 0x31)[:13] == [0xB, 0xC, 7, 0x17, 5, 8, 0x15, 0x16, 0x18, 0x19, 0x1D, 0x1E, 0x1F]


def test_preparacion_p4c_primero_y_esperas(d):
    assert _calls(d, 0x17CEE, 3)[0][1] == 0x16E7A
    c = [t for _, t in _calls(d, 0x1811A, 60)]
    assert c.index(0x17CEE) < c.index(0x1961C)


def test_tipo_y_clase_salen_del_mismo_byte(d):
    assert _calls(d, 0x20C74, 3)[0][1] == 0x1B080
    assert _calls(d, 0x1FE66, 6)[0][1] == 0x1B080
    assert d[0x1FE7A - B:0x1FE80 - B].hex() == "040303030303"
