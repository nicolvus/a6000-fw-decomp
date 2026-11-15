"""G61 — intervalómetro sobre el autodisparador continuo de `libObj` 3.21: bytes originales, idempotencia, cueva sin referencias y Unicorn (Off / 5 s con N = 10)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g61")]
import cfw_ajustes as C
import intervalo_patch as P

pytestmark = pytest.mark.skipif(not P.SRC.exists(), reason="sin libObj extraído")


def test_bytes_originales_e_idempotencia():
    orig = P.SRC.read_bytes()
    img = P.apply_bytes(orig)
    assert len(img) == len(orig) and P.apply_bytes(orig) == img
    with pytest.raises(ValueError):                                   # sobre la imagen ya parcheada los ganchos no son los originales
        P.apply_bytes(img)
    a, old = P.TOMA
    assert orig[a:a + 4] == old and img[a:a + 4] != old
    diff = [i for i in range(len(orig)) if orig[i] != img[i]]
    cuevas = range(P.CAVE, P.CAVE_FIN)
    assert all(i in cuevas or any(h <= i < h + 4 for h in (*P.ESPERA[0], P.INICIO[0], P.TOMA[0])) for i in diff)


def test_saltos_de_la_cueva_a_destino_exacto():
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    p = P.piezas()
    va, code = p["toma"]
    ds = {i.address: i for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(code, va) if i.mnemonic == "b.w"}
    destinos = {int(i.op_str[1:], 16) for i in ds.values()}
    assert {P.FIN_SEQ, P.REARME} <= destinos


def test_cueva_sin_referencias_y_contador_en_pagina_del_bss():
    d = P.SRC.read_bytes()
    n = len(d) // 4 * 4
    words = struct.unpack(f"<{n // 4}I", d[:n])
    assert not any(P.CAVE <= (w & ~1) < P.CAVE_FIN for w in words)    # ni vtable ni puntero a la cueva
    ex = 0xF5FE34                                                      # .ARM.exidx: la función 0x2648d8 empieza en la cueva y no hay otra dentro
    ini = []
    for i in range(0x6A770 // 8):
        v = struct.unpack_from("<I", d, ex + i * 8)[0] & 0x7FFFFFFF
        ini.append(ex + i * 8 + (v - (1 << 31) if v & 0x40000000 else v))
    assert P.CAVE in ini and not any(P.CAVE < a < P.CAVE_FIN for a in ini)
    assert 0x10E2BD0 <= P.CTR < 0x10E3000                              # cola de página tras el fin del .bss (VA 0xfd25a4 + memsz 0x11062c)


def test_unicorn_off_y_intervalo_5s_n10():
    P.comprobar()


def test_ajustes_nuevos_caben_en_el_menu():
    i, n = C.POR_ID["intervalo"], C.POR_ID["n_disparos"]
    assert len(i.opciones) == len(n.opciones) == 7 and i.opciones[0] == ("Off", 0) and n.opciones[-1][1] == 0
    assert len({a.backup for a in C.AJUSTES}) == len(C.AJUSTES) and len({a.pid for a in C.AJUSTES}) == len(C.AJUSTES)
