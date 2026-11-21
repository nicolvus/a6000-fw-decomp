"""G68 — DR Prioridad: bytes originales, idempotencia, ramas a destino exacto, combinación con g61 y Unicorn (Off no cambia nada; Débil/Fuerte emiten DRO y sesgo)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g61"), str(ROOT / "scripts/g68")]
import cfw_ajustes as C
import drp_patch as P
import intervalo_patch as G61

pytestmark = pytest.mark.skipif(not P.SRC.exists(), reason="sin libObj extraído")


def test_bytes_originales_e_idempotencia():
    orig = P.SRC.read_bytes()
    img = P.apply_bytes(orig)
    assert len(img) == len(orig) and P.apply_bytes(orig) == img
    with pytest.raises(ValueError):
        P.apply_bytes(img)
    diff = [i for i in range(len(orig)) if orig[i] != img[i]]
    assert all(P.CAVE <= i < P.CAVE_FIN or P.HOOK[0] <= i < P.HOOK[0] + 4 for i in diff)


def test_ramas_a_destino_exacto():
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    vistos = set()
    piezas = P.piezas()
    for va, code in piezas.values():
        for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(code, va):
            if i.mnemonic in ("bl", "blx") or (i.mnemonic == "b.w" and not P.CAVE <= int(i.op_str[1:], 16) < P.CAVE_FIN):
                vistos.add(int(i.op_str[1:], 16))
    assert vistos == {*P.EXT, 0xDD5F4, P.CAVE, piezas["emite_c"][0], P.DESTINO}, {hex(x) for x in vistos}


def test_cueva_sin_referencias_y_sin_solape_con_g61():
    d = P.SRC.read_bytes()
    words = struct.unpack(f"<{len(d) // 4}I", d[:len(d) // 4 * 4])
    assert not any(P.CAVE <= (w & ~1) < P.CAVE_FIN for w in words)
    assert P.CAVE >= G61.CAVE_FIN
    both = G61.apply_bytes(P.apply_bytes(d))
    assert both == P.apply_bytes(G61.apply_bytes(d))


def test_ajuste_en_la_tabla():
    a = C.POR_ID["dr_prior"]
    assert [v for _, v in a.opciones] == [0, 1, 2] and a.backup in C.ID_LIBRES


def test_unicorn():
    P.comprobar()


def test_gancho_en_la_pulsacion_s1_y_no_en_el_ajuste_s1af():
    """G75 T57: el tipo de mensaje 0x4e (`ActionSetS1AF`, 0x689520) lo emite el menú «AF c/obturador» al cambiar el ajuste, no la semipulsación;
    la semipulsación emite `0x7506` en 0x67c130 (r4 = 0 al pulsar). El gancho va allí, antes de armar ese ObjMsg."""
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    a = P.HOOK[0]
    assert not 0x689520 <= a < 0x689628
    ins = list(Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(P.SRC.read_bytes()[0x67C130:0x67C160], 0x67C130))
    assert any(i.address > a and i.mnemonic == "movw" and i.op_str == "r2, #0x7506" for i in ins)
    assert next(i for i in ins if i.address == a).op_str == f"#{P.DESTINO:#x}"


def test_solo_al_pulsar_no_al_soltar():
    img = P.apply_bytes(P.SRC.read_bytes())
    B = C.POR_ID["dr_prior"].backup
    assert P.emular(img, {B: 2}, r4=1)["msgs"] == [] and P.emular(img, {B: 2}, r4=0)["msgs"]


def test_el_sesgo_va_como_parametro_signed_char():
    """G75 T57 (MEDIDO en el arnés): `ParamStd<int>` para 0x759e da «PreTypeCheck ERROR GetType()=7 ref paramType=3» y ObjCamera devuelve 3; el DRO (0x755a) sí va como int."""
    img = P.apply_bytes(P.SRC.read_bytes())
    r = P.emular(img, {C.POR_ID["dr_prior"].backup: 2})
    assert r["ctores"] == [G61.PLT_INT, 0xE1668]  # ParamStd<int>(DRO) y ParamStd<signed char>(sesgo)
