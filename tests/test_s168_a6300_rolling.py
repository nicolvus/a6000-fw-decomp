"""Tests de S168 — control positivo del «rolling shutter» del A6300 (cadena muerta).

Todos los tests comprueban **bytes reales**: si cambia una dirección, un texto o un
contador, el test falla.

Convenio del repo: `vaddr = 0x43541000 + file_offset` (válido también para la A7S fw3.20
y el A6300 fw2.01).
"""
import json
import os
import struct

import pytest

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A6000 = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
A7S = os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                           "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
ANA = os.path.join(ROOT, "analysis/s168_a6300_rolling")

ROLLING = b"position num in rolling is strange %d"
VD = b"position num in vd is strange %d"
VA_ROLLING = 0x43D9FE03
VA_VD = 0x43D9FDE2


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def a6000():
    return _read(A6000)


@pytest.fixture(scope="module")
def a7s():
    return _read(A7S)


@pytest.fixture(scope="module")
def a6300():
    return _read(A6300)


# --------------------------------------------------------------------------
# 1) Existencia y unicidad de las cadenas
# --------------------------------------------------------------------------

def test_rolling_existe_en_a6300_con_la_direccion_exacta(a6300):
    off = a6300.find(ROLLING)
    assert off >= 0, "la cadena del rolling deberia existir en el A6300 fw2.01"
    assert BASE + off == VA_ROLLING
    assert a6300[off:off + len(ROLLING)] == ROLLING


def test_rolling_no_existe_en_a6000_ni_en_a7s(a6000, a7s):
    assert a6000.count(ROLLING) == 0
    assert a7s.count(ROLLING) == 0


def test_vd_existe_en_a6300_con_la_direccion_exacta(a6300):
    off = a6300.find(VD)
    assert off >= 0
    assert BASE + off == VA_VD


def test_cuenta_de_la_familia_position_num(a6000, a7s, a6300):
    assert a6300.count(b"position num in") == 2
    assert a6000.count(b"position num in") == 0
    assert a7s.count(b"position num in") == 0


def test_rolling_en_cualquier_grafia_solo_en_a6300_y_una_vez(a6000, a7s, a6300):
    def n(b):
        return b.count(b"rolling") + b.count(b"Rolling") + b.count(b"ROLLING")
    assert n(a6000) == 0
    assert n(a7s) == 0
    assert n(a6300) == 1


def test_roll_bruto_no_es_evidencia_de_rolling_shutter(a6000):
    """Casi todo 'roll' en la A6000 es 'Controller'/'Scroll'; solo hay 3 excepciones reales."""
    import re
    ctx = [m.group().decode("latin1") for m in re.finditer(rb"[ -~]{0,24}[Rr]oll[ -~]{0,24}", a6000)]
    assert ctx, "deberia haber contextos con 'roll'"
    excepciones = sorted({t for t in ctx
                          if "Controller" not in t and "Scroll" not in t
                          and "controller" not in t and "scroll" not in t})
    assert len(excepciones) == 3, excepciones
    assert any("RollAD,%d" in x for x in excepciones)
    assert "SetDistRoll" in excepciones
    assert "SetRoll" in excepciones


def test_las_tres_excepciones_de_roll_son_las_esperadas(a6000, a7s, a6300):
    assert a6000.count(b"SetDistRoll") == 1
    assert a6000.count(b"SetRoll") == 1
    assert a6000.count(b"RollAD") == 1
    assert a7s.count(b"SetDistRoll") == 1
    assert a7s.count(b"SetRoll") == 1
    assert a7s.count(b"RollAD") == 0
    assert a6300.count(b"SetDistRoll") == 1
    assert a6300.count(b"SetRoll") == 1
    assert a6300.count(b"RollAD") == 0


# --------------------------------------------------------------------------
# 2) Referencias de codigo (regla estricta, replicada aqui)
# --------------------------------------------------------------------------

def _pic_refs(blob, dest):
    """Referencias PIC de `dest` con la regla estricta canónica del repo."""
    U16 = struct.Struct("<H").unpack_from
    U32 = struct.Struct("<I").unpack_from
    n = len(blob)
    starts = set()
    prev = False
    for i in range(n):
        cur = 32 <= blob[i] < 127
        if cur and not prev:
            starts.add(BASE + i)
        prev = cur
    ldrs = {}
    a = BASE
    while a < BASE + n:
        o = a - BASE
        if o < 0 or o > n - 4:
            a += 2
            continue
        h = U16(blob, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(blob, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= n - 4:
                ldrs.setdefault(reg, []).append((a, U32(blob, o2)[0]))
        a += 2
    for v in ldrs.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in ldrs.items()}
    out = []
    a = BASE
    while a < BASE + n:
        o = a - BASE
        if o < 0 or o > n - 4:
            a += 2
            continue
        h = U16(blob, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            reg = (((h >> 7) & 1) << 3) | (h & 7)
            v = ldrs.get(reg)
            if v:
                i = _bisect(keys[reg], a) - 1
                if i >= 0:
                    la, w = v[i]
                    if a - la <= 4096:
                        tgt = (w + (a + 4)) & 0xFFFFFFFF
                        if tgt == dest and tgt in starts:
                            out.append(a)
        a += 2
    return sorted(out)


def _bisect(lst, x):
    lo, hi = 0, len(lst)
    while lo < hi:
        mid = (lo + hi) // 2
        if lst[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def test_la_cadena_del_rolling_no_tiene_ninguna_referencia_pic(a6300):
    assert _pic_refs(a6300, VA_ROLLING) == []


def test_la_cadena_del_vd_tiene_una_referencia_pic_concreta(a6300):
    assert _pic_refs(a6300, VA_VD) == [0x43729166]


def test_control_positivo_en_la_a6000(a6000):
    """Control del método: la cadena de S166 debe tener 1 referencia en la A6000."""
    assert _pic_refs(a6000, 0x43C7751A) == [0x43636CE6]


# --------------------------------------------------------------------------
# 3) Bytes concretos del sitio vivo
# --------------------------------------------------------------------------

def test_pool_y_sitio_de_la_referencia_al_vd(a6300):
    assert struct.unpack("<I", a6300[0x43729174 - BASE:0x43729178 - BASE])[0] == 0x00676C78
    assert struct.unpack("<H", a6300[0x43729164 - BASE:0x43729166 - BASE])[0] == 0x4803
    assert struct.unpack("<H", a6300[0x43729166 - BASE:0x43729168 - BASE])[0] == 0x4478


def test_codigo_de_la_funcion_que_calcula_el_ancho(a6300):
    """0x4372914c: calculo de ancho en bits con control de rango."""
    code = a6300[0x4372914C - BASE:0x43729174 - BASE]
    def hw(va):
        return struct.unpack("<H", a6300[va - BASE:va - BASE + 2])[0]
    assert hw(0x4372914C) == 0xB508          # push {r3, lr}
    assert hw(0x43729156) == 0x2101          # movs r1, #1
    assert hw(0x43729158) == 0x4081          # lsl.w r1, r0, #1
    assert hw(0x4372915C) == 0x1E4B          # subs r3, r1, #1
    assert hw(0x43729160) == 0x2BFE          # cmp r3, #0xfe
    assert hw(0x4372916C) == 0x2108          # movs r1, #8
    assert hw(0x43729170) == 0xBD08          # pop {r3, pc}


def test_el_texto_del_vd_esta_justo_despues_del_pool(a6300):
    off = VA_VD - BASE
    assert a6300[off - 2:off] == b")\x00"  # cola de la cadena anterior
    assert a6300[off:off + len(VD)] == VD


# --------------------------------------------------------------------------
# 4) Datos estructurados del hito
# --------------------------------------------------------------------------

def test_json_del_hito_consistente():
    with open(os.path.join(ANA, "rolling.json"), encoding="utf-8") as fh:
        j = json.load(fh)
    assert j["milestone"] == "S168"
    assert j["firmwares"]["A6300_fw201"]["position_num_in_rolling"] == 1
    assert j["firmwares"]["A6300_fw201"]["position_num_in_vd"] == 1
    assert j["firmwares"]["A6000_fw321"]["position_num_in_rolling"] == 0
    assert j["firmwares"]["A7S_fw320"]["position_num_in_rolling"] == 0
    assert j["refs_pic_estricta_A6300"]["0x43d9fe03_position_num_in_rolling"] == []
    assert j["refs_pic_estricta_A6300"]["0x43d9fde2_position_num_in_vd"] == ["0x43729166"]
    assert j["refs_metodo_inverso_A6300"]["0x43d9fe03_position_num_in_rolling"] == []


def test_mapa_vivo_muerto_de_la_banda():
    with open(os.path.join(ANA, "alive_map.json"), encoding="utf-8") as fh:
        j = json.load(fh)
    por_addr = {c["addr"]: c for c in j["cadenas"]}
    assert por_addr["43d9fdc5"]["n_refs_pic"] == 1
    assert por_addr["43d9fde2"]["n_refs_pic"] == 1
    assert por_addr["43d9fe03"]["n_refs_pic"] == 0
    assert por_addr["43d9fe29"]["n_refs_pic"] == 1
    assert por_addr["43d9fe50"]["n_refs_pic"] == 1
    for c in j["cadenas"]:
        assert c["punteros_absolutos"] == []
        assert c["movw_movt"] == []


def test_informe_del_hito_menciona_la_correccion_de_s164():
    with open(os.path.join(ANA, "rolling.md"), encoding="utf-8") as fh:
        t = fh.read()
    assert "S164" in t and "muerta" in t
    assert "0x43729166" in t
