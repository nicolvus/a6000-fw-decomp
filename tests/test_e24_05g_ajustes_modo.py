"""E24-05g: origen de 0x11/0x14, de 0x17 y byte 0 del 0x0b. Verifican bytes/tablas, no el texto del informe.
Informe: docs/capture/e24-05g-ajustes-modo-ocupacion.md
"""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
for d in ("e24_05g", "e24_05f", "e24_05", "e24_05d"):
    sys.path.insert(0, str(ROOT / "scripts" / d))

from dwn import DARWIN

if not DARWIN.exists():
    pytest.skip("falta darwin_core.bin", allow_module_level=True)

import ajustes_modo as a
import emisores as e


@pytest.fixture(scope="module")
def res():
    return json.loads(json.dumps(a.main()))


@pytest.fixture(scope="module")
def cg():
    c = a.Core()
    return c, e.G(c)


def calls(c, lo, n):
    return [i.operands[0].imm for i in c.dis(lo, n) if i.mnemonic in ("bl", "b.w") and i.operands[0].type == 2]


def test_0x18a_son_flags_de_las_filas_22_23_no_un_evento(res):
    t = res["tabla_filas"]
    assert t["fila22"] == ["0x1b137", "0x18a"] and t["fila23"] == ["0x1b123", "0x18a"] and t["fila24"] == ["0x1c0b7", "0x717"]


def test_manejador_fila24_arranca_la_fsm_de_ajustes(cg):
    c, g = cg
    assert calls(c, 0x1C0B6, 4) == [0x19C4C] and calls(c, 0x19C4C, 4) == [0x1AA28]
    assert g.callers[0x19C4C] == [0x1C0B8]


def test_publicador_del_mensaje_2_0x18(cg):
    c, _ = cg
    t = [i.mnemonic + " " + i.op_str for i in c.dis(0x1C02C + 0xA, 0x14)]
    assert "movs r0, #2" in t[0] and "strh.w r0, [sp]" in t[1] and "movs r0, #0x18" in t[2] and "strh.w r0, [sp, #2]" in t[3]
    assert 0x452C in calls(c, 0x1C02C, 0x20)


def test_gancho_0x1c04c_depende_del_bloque_10_bit3_y_de_un_pestillo(cg, res):
    c, _ = cg
    assert "0x1c04d" in res["ganchos"] and res["bloque10"][1] == "0x20003514"
    ins = [(i.mnemonic, i.op_str) for i in c.dis(0x1C04C, 0x2C)]
    assert ("movs", "r0, #0xa") in ins and ("lsls", "r0, r0, #0x1c") in ins and ("movs", "r0, #7") in ins
    assert 0x125DA in calls(c, 0x1C04C, 0x2C) and 0x1BB82 in calls(c, 0x1C04C, 0x2C) and 0x1C02C in calls(c, 0x1C04C, 0x2C)


def test_ganchos_se_ejecutan_tras_desempaquetar_cada_trama_0x31(cg):
    c, g = cg
    assert 0x127B8 in calls(c, 0x124A6, 0x70) and c.u32(0x127E4) == 0x282E0  # lista 0x282e0+0x1c
    assert sorted(g.callers[0x12330]) == [0x11F4A, 0x120A8]
    assert [i.mnemonic for i in c.dis(0x12330, 8)][-1] == "b.w"


def test_starter_evento_gates_s2a0_y_s2a2(cg):
    c, _ = cg
    t = {i.address: i.mnemonic + " " + i.op_str for i in c.dis(0x1AA28, 0xB0)}
    assert t[0x1AAAC] == "ldrb.w r0, [r5, #0x2a0]" and t[0x1AAB4] == "ldrb.w r0, [r5, #0x2a2]" and t[0x1AAB8] == "lsls r0, r0, #0x1d"
    assert t[0x1AA68] == "orr r0, r0, #4"  # el bit 2 de S+0x2a2 se fuerza antes de la comprobación
    assert t[0x1AA40] == "strb r0, [r5, #0x16]"  # S+0x2a0 = bit 7 de [0x20003945]


def test_starter_por_disparo_en_el_bucle_de_captura(cg):
    c, g = cg
    assert g.callers[0x17CEE] == [0x1817C] and g.callers[0x17C26] == [0x17E56]
    seq = calls(c, 0x1811A, 0x90)
    assert seq.index(0x17F8C) < seq.index(0x17CEE) < seq.index(0x1961C)
    assert calls(c, 0x17CEA, 4) == [0x1A3EC]
    t = {i.address: i.op_str for i in c.dis(0x1A4B4, 0x14)}
    assert t[0x1A4B8] == "r2, #1" and t[0x1A4C0] == "r2, r2, #0x1d"


def test_modos_0_a_8_envian_0x11_y_0x14_y_9_10_no(res):
    for m in res["tabla_modos"]:
        s = m["seq"]
        assert (0 in s and 2 in s) == (m["key"] <= 8)
    assert res["tabla_modos"][9]["seq"] == [21, 23] and res["tabla_modos"][10]["seq"] == [22, 23]


def test_0x17_lo_pide_darwin_a_si_mismo(cg):
    c, g = cg
    assert sorted(g.callers[0x1B290]) == [0xD356, 0x1F02C]
    assert sorted(g.callers[0xD34E]) == [0x18F6E, 0x1909A]
    assert g.func(0x18F6E) == 0x18D6E and g.func(0x1909A) == 0x18FA0
    assert 0x18FA0 in [x for x in g.callers and [g.func(s) for s in g.callers[0x18FA0]]] or g.callers[0x18FA0]
    assert calls(c, 0x7C66, 6) == [0x125F6] or 0x125F6 in calls(c, 0x7C66, 6)
    assert calls(c, 0x1F02A, 8) == [0x1B290]
    # estado 27 de la FSM A está en la lista de la operación 0x16e92 (0x0e/0x10), tras el 0x10 (estado 24)
    f = e.fsm_table(c, e.FSM_A)["states"]
    assert f[27] == 0x175A0 and 0x1F02A in calls(c, 0x175A0, 8)
    lst = next(o for o in e.installers(c, e.G(c), e.FSM_A, 0x32) if o["entry"] == 0x16E92)["seq"]
    assert lst.index(24) < lst.index(27) < lst.index(28)


def test_solo_el_modo_0_emite_0x17(cg):
    _c, g = cg
    assert [s for s in g.callers[0x12260] if 0x125F6 <= s < 0x12770] == [0x1274A]


def test_0x125f6_modo0_no_toca_bobinas_ni_compuerta(res):
    for k in ("modo0", "modo1", "estado27_modo0", "estado28_espera", "starter_evento", "starter_disparo"):
        assert res["cierres"][k]["golpes"] == []


def test_modo2_y_espera_estado31_si_alcanzan_el_mecanismo(res):
    assert "0x20c74" in res["cierres"]["modo2"]["golpes"]
    assert {"0x1fe66", "0x20cb2", "0x20d00"} <= set(res["cierres"]["esperas_estado31"]["golpes"])


def test_espera_estado31_sale_por_una_entrada_gpio(cg, res):
    c, g = cg
    assert res["gpio_espera_estado31"] == "P29"
    t = [(i.mnemonic, i.op_str) for i in c.dis(0x1EC9C, 0x14)]
    assert ("mov.w", "r0, #0x124") in t and any(m == "bl" and o == "#0x51c6" for m, o in t)
    assert 0x16C44 in calls(c, 0x1905E, 4) and g.callers[0x16C44] == [0x1905E]


def test_bionz_esperas_y_byte0(res):
    b = res["bionz"]
    assert b["esperas"]["0x11"] == ["0x438cc56c"] and b["esperas"]["0x14"] == ["0x438cc7c8", "0x438ccb0e"]
    assert b["tbb_tipos"] == [4, 19, 9, 19, 14, 19, 24, 29]


def test_bionz_clasifica_byte0_del_0x0b():
    z = a.Bz()
    t = [(i.address, i.mnemonic, i.op_str) for i in z.dis(0x438C25B4, 0x50)]
    ops = {x[0]: x[1:] for x in t}
    assert ops[0x438C25BE] == ("ldrb", "r3, [r3]") and ops[0x438C25C2][0] == "beq"  # clase 0 -> 0x438c2682
    assert ops[0x438C25C4] == ("tst.w", "r3, #1")  # bit 0 = clase 1 (reintento); si no, 0x438c277c
    assert ops[0x438C25F0] == ("cmp", "r1, #0x13")  # tope de reintentos
    assert a._bl_target(z, 0x438C25B0) == 0x438D025C and ops[0x438C25C8][0] == "beq.w"
