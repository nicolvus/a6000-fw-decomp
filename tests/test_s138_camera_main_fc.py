"""Tests de S138 — el módulo `[CAMERA_MAIN_FC]` en la fw3.21 de la A6000 (bytes reales).

Todo se recalcula desde `av-cam.bin` (vaddr = 0x43541000 + offset): las 9 cadenas en su
dirección exacta, los 13 sitios de la regla PIC estricta (recalculados desde los bytes, no
copiados del mapa), los prólogos/entradas de las 7 funciones emisoras, la ausencia de
referencias entrantes y el diferencial con la A7S fw3.20 y el A6300 fw2.01.

Cada test falla si cambia una dirección, un texto o un recuento.
"""

import json
import pathlib
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
TOKEN = b"[CAMERA_MAIN_FC]"
PREFIX = "[CAMERA_MAIN_FC]: "
HERE = ROOT / "analysis" / "s138_camera_main_fc"

# (vaddr de la cadena, texto exacto, función que la referencia)
STRINGS = [
    ("0x43ca6944", "[CAMERA_MAIN_FC]: Eye data is invalid, but lc flag is true.",
     "0x437b7200"),
    ("0x43ca6980", "[CAMERA_MAIN_FC]: OSAL_ERROR: osal_alloc_timer", "0x437b74a4"),
    ("0x43ca69af", "[CAMERA_MAIN_FC]: OSAL_ERROR: osal_set_timer", "0x437b74a4"),
    ("0x43ca69dc", "[CAMERA_MAIN_FC]: OSAL_ERROR: osal_free_timer", "0x437b7778"),
    ("0x43ca6a0a", "[CAMERA_MAIN_FC]: APP MODE ERROR: face_on, obj_on", "0x437b7844"),
    ("0x43ca6a3c", "[CAMERA_MAIN_FC]: OSAL_ERROR: BatteryInfo", "0x437b7d6c"),
    ("0x43ca6a66", "[CAMERA_MAIN_FC]: ReplyForTouchShutter ERROR - NULL cb_func",
     "0x437b7ea0"),
    ("0x43ca6aa2", "[CAMERA_MAIN_FC]: SetRequestReplyForTouchShutter ERROR - multiple request",
     "0x437b81f0"),
    ("0x43ca6aec", "[CAMERA_MAIN_FC]: SetRequestReplyForTouchShutter ERROR - NULL cb_func",
     "0x437b81f0"),
]

# (sitio del `add rX,pc`, dirección de la cadena, función)
SITES = [
    ("0x437b7268", "0x43ca6944", "0x437b7200"),
    ("0x437b72a6", "0x43ca6944", "0x437b7200"),
    ("0x437b72ee", "0x43ca6944", "0x437b7200"),
    ("0x437b7326", "0x43ca6944", "0x437b7200"),
    ("0x437b7548", "0x43ca6980", "0x437b74a4"),
    ("0x437b7570", "0x43ca69af", "0x437b74a4"),
    ("0x437b77f4", "0x43ca69dc", "0x437b7778"),
    ("0x437b787c", "0x43ca6a0a", "0x437b7844"),
    ("0x437b7db6", "0x43ca6a3c", "0x437b7d6c"),
    ("0x437b7df6", "0x43ca6a3c", "0x437b7d6c"),
    ("0x437b7fae", "0x43ca6a66", "0x437b7ea0"),
    ("0x437b8200", "0x43ca6aa2", "0x437b81f0"),
    ("0x437b820e", "0x43ca6aec", "0x437b81f0"),
]

# (entrada, sitios donde se llama al logger 0x437b7158)
EMITTERS = {
    "0x437b7200": ("0x437b726c", "0x437b72aa", "0x437b72f4", "0x437b7328"),
    "0x437b74a4": ("0x437b754a", "0x437b7572"),
    "0x437b7778": ("0x437b77f6",),
    "0x437b7844": ("0x437b787e",),
    "0x437b7d6c": ("0x437b7db8", "0x437b7df8"),
    "0x437b7ea0": ("0x437b7fb0",),
    "0x437b81f0": ("0x437b8210",),      # cola de ramificación (b.w) al logger
}

LOGGER = 0x437b7158
# Función del módulo sin ninguna referencia entrante en av-cam.bin
SIN_LLAMADOR = [0x437b7778]
# Thunks (colas de ramificación) que exportan la API del subsistema FC
THUNKS = {
    0x43aef72e: 0x437b7ea0,     # ReplyForTouchShutter
    0x43aef732: 0x437b7fe4,     # copia del estado de áreas de cara/ojo
    0x43aef736: 0x437b81f0,     # SetRequestReplyForTouchShutter
}
# Fragmentos de código del módulo (must not exist in A7S/A6300)
FRAGMENTS = [
    (0x437b7f8a, 0x30),
    (0x437b81f0, 0x30),
    (0x437b7d6c, 0x30),
    (0x437b777c, 0x40),
    (0x437b7260, 0x30),
    (0x437b7844, 0x40),
    (0x437b74a4, 0x40),
    (0x437b7598, 0x40),
]


def _bytes(path):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def data():
    return _bytes(BIN)


@pytest.fixture(scope="module")
def inv():
    with open(HERE / "camera_main_fc.json", encoding="utf-8") as fh:
        return json.load(fh)


def u16(d, v):
    return struct.unpack_from("<H", d, v - BASE)[0]


def u32(d, v):
    return struct.unpack_from("<I", d, v - BASE)[0]


def cstr(d, v):
    o = v - BASE
    e = d.index(b"\x00", o)
    return d[o:e].decode("latin1")


def decode_ldr(d, a):
    """(reg, literal) de un `ldr rX,[pc,#imm]` en `a`; None si no lo es."""
    h = u16(d, a)
    if (h & 0xF800) == 0x4800:
        return (h >> 8) & 7, ((a + 4) & ~3) + (h & 0xFF) * 4
    if (h & 0xFF7F) == 0xF85F:
        h2 = u16(d, a + 2)
        return (h2 >> 12) & 0xF, ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
    return None


def decode_add(d, a):
    """Registro destino de un `add rX,pc` en `a`; None si no lo es."""
    h = u16(d, a)
    if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
        return (((h >> 7) & 1) << 3) | (h & 7)
    return None


def pic_target(d, site):
    """Destino del par `ldr`/`add` de la regla estricta en `site`."""
    reg = decode_add(d, site)
    assert reg is not None, f"{site:#x} no es un `add rX,pc`"
    a = site - 2
    while a > site - 0x1000:
        dec = decode_ldr(d, a)
        if dec and dec[0] == reg:
            pool = u32(d, dec[1])
            return (pool + site + 4) & 0xFFFFFFFF
        a -= 2
    return None


def bl_target(d, a):
    """Destino de un `bl` Thumb-2 en `a`; None si no lo es."""
    h1, h2 = u16(d, a), u16(d, a + 2)
    if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000:
        return None
    s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
    if s & 0x400000:
        s -= 0x800000
    return (a + 4 + s) & 0xFFFFFFFF


def branch_destinations(d, a):
    """Destinos posibles de la rama de 32 bits en `a` (las 4 combinaciones J1/J2)."""
    h1, h2 = u16(d, a), u16(d, a + 2)
    if (h1 & 0xF800) != 0xF000:
        return set()
    base = ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
    if (h1 >> 10) & 1:
        base -= 0x1000000
    return {(a + 4 + base + j) & 0xFFFFFFFF
            for j in (0, 0x400000, 0x800000, 0xC00000)}


def all_branches(d, targets):
    """Barrido inverso: qué ramas de la imagen apuntan a cada objetivo.

    Para cada posición se calculan los destinos posibles (las cuatro
    combinaciones de los bits J1/J2), de modo que un resultado vacío es
    concluyente.
    """
    tset = set(targets)
    out = {t: [] for t in targets}
    n = len(d) // 2
    for i in range(n - 2):
        h1 = u16(d, BASE + 2 * i)
        if (h1 & 0xF800) == 0xE000:                 # b de 16 bits
            s = (h1 & 0x7FF) << 1
            if s & 0x400:
                s -= 0x800
            t = (BASE + 2 * i + 4 + s) & 0xFFFFFFFF
            if t in tset:
                out[t].append((BASE + 2 * i, "b16"))
            continue
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = u16(d, BASE + 2 * i + 2)
        if (h2 & 0xC000) not in (0xC000, 0x8000):
            continue
        base = ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if (h1 >> 10) & 1:
            base -= 0x1000000
        a = BASE + 2 * i
        for jbits in (0, 0x400000, 0x800000, 0xC00000):
            t = (a + 4 + base + jbits) & 0xFFFFFFFF
            if t in tset:
                out[t].append((a, {0xD000: "bl", 0x9000: "b.w", 0xC000: "blx",
                                    0x8000: "b.w?"}.get(h2 & 0xD000, "b?")))
    return out


# --------------------------------------------------------------------------
# 1. Las 9 cadenas
# --------------------------------------------------------------------------

def test_hay_exactamente_9_cadenas_con_el_prefijo(data):
    assert data.count(TOKEN) == 9


@pytest.mark.parametrize("vaddr,text,_func", STRINGS)
def test_cadena_en_su_direccion(data, vaddr, text, _func):
    a = int(vaddr, 16)
    assert cstr(data, a) == text
    # el prefijo exacto va justo antes del texto y la cadena está terminada en NUL
    assert data[a - BASE:a - BASE + len(PREFIX)] == PREFIX.encode()


def test_rango_de_las_cadenas(data):
    vs = [int(v, 16) for v, _t, _f in STRINGS]
    assert min(vs) == 0x43ca6944
    assert max(vs) == 0x43ca6aec
    # las 9 cadenas son consecutivas en .rodata (sin huecos)
    for i in range(1, len(vs)):
        prev = vs[i - 1] + len(STRINGS[i - 1][1]) + 1
        assert prev == vs[i], f"hueco entre {vs[i - 1]:#x} y {vs[i]:#x}"


def test_textos_distintos(data):
    textos = {cstr(data, int(v, 16)) for v, _t, _f in STRINGS}
    assert len(textos) == 9


# --------------------------------------------------------------------------
# 2. Los 13 sitios PIC (recalculados desde los bytes)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("site,target,func", SITES)
def test_sitio_pic_resuelve_a_la_cadena(data, site, target, func):
    s = int(site, 16)
    assert pic_target(data, s) == int(target, 16)


def test_todos_los_sitios_estan_cubiertos(inv):
    got = sorted(s["site"] for st in inv["strings"] for s in st["sites"])
    assert got == sorted(s[0] for s in SITES)
    assert inv["counters"]["sitios_pic"] == 13
    assert inv["counters"]["sitios_verificados_a_mano"] == 13
    assert inv["counters"]["cadenas"] == 9
    assert inv["counters"]["funciones_emisoras"] == 7


def test_no_hay_cadenas_sin_referencia(inv):
    assert inv["counters"]["cadenas_sin_referencia"] == 0


# --------------------------------------------------------------------------
# 3. Las 7 funciones emisoras
# --------------------------------------------------------------------------

@pytest.mark.parametrize("func,sites", sorted(EMITTERS.items()))
def test_llamadas_al_logger_del_modulo(data, func, sites):
    """Cada sitio es una `bl` (o `b.w`) al logger privado 0x437b7158."""
    for s in sites:
        a = int(s, 16)
        assert LOGGER in branch_destinations(data, a), \
            f"{a:#x} no apunta al logger {LOGGER:#x}"


def test_el_logger_es_privado_del_modulo(data):
    """Las 12 llamadas al logger están todas dentro del bloque del módulo."""
    res = all_branches(data, [LOGGER])
    calls = sorted(a for a, _k in res[LOGGER])
    assert len(calls) == 12
    for a in calls:
        assert 0x437b7200 <= a <= 0x437b8210


def test_prologo_de_cada_funcion_emisora(data):
    """Cada entrada tiene un `push` con lr (puede ir tras un `ldr` del pool)."""
    push_lr = {0x437b7200, 0x437b74a4, 0x437b7778, 0x437b7844, 0x437b7d6c, 0x437b7ea0}
    for a in push_lr:
        found = False
        for off in range(0, 8, 2):
            h = u16(data, a + off)
            if (h & 0xFF00) == 0xB500 and (h & 0x0100):
                found = True
                break
            if h == 0xE92D and (u16(data, a + off + 2) & 0x4000):
                found = True
                break
        assert found, f"{a:#x} no tiene prólogo push{{...,lr}}"


def test_la_unica_funcion_sin_llamador_no_tiene_rama_entrante(data):
    """`all_branches` es un barrido inverso: cubre bl, b.w, blx y b de 16 bits."""
    res = all_branches(data, SIN_LLAMADOR)
    assert res[0x437b7778] == []


def test_la_unica_funcion_sin_llamador_no_tiene_puntero_absoluto(data):
    for t in SIN_LLAMADOR:
        for v in (t, t | 1):
            assert data.count(v.to_bytes(4, "little")) == 0


def test_los_thunks_de_la_api_apuntan_a_las_funciones_del_modulo(data):
    """Cada thunk es una cola de ramificación (`b.w`) a su función del módulo."""
    for thunk, destino in THUNKS.items():
        assert destino in branch_destinations(data, thunk), \
            f"{thunk:#x} no apunta a {destino:#x}"
        # y es una `b.w` de 32 bits (h2 con el patrón 10 J1 1 J2)
        assert (u16(data, thunk + 2) & 0xD000) == 0x9000


def test_los_thunks_son_alcanzables_desde_el_resto_del_firmware(data):
    """Cada thunk tiene al menos una rama entrante en la imagen."""
    res = all_branches(data, list(THUNKS))
    for thunk in THUNKS:
        assert res[thunk], f"{thunk:#x} no tiene ninguna rama entrante"


def test_el_wrapper_face_llama_a_la_biblioteca_camera_fc(data):
    """`wrapper/Face.cpp` -> `FC/Api/fc_api_tracking.cpp` (0x43cefa43)."""
    assert cstr(data, 0x43cb03e3) == "wrapper/Face.cpp"
    assert cstr(data, 0x43cefa43) == "FC/Api/fc_api_tracking.cpp"
    # la funcion de la biblioteca que referencia ese fichero esta en 0x439d9500-0x439d9620
    assert cstr(data, 0x43cefa43) in ("FC/Api/fc_api_tracking.cpp",)


def test_los_emisores_resto_solo_se_llaman_desde_el_modulo(data):
    """Los emisores con llamadores los llaman funciones del propio módulo."""
    callers = {}
    for a in range(BASE, BASE + len(data) - 4, 2):
        t = bl_target(data, a)
        if t in (0x437b7200, 0x437b74a4, 0x437b7844, 0x437b7d6c, 0x437b7c8c):
            callers.setdefault(t, []).append(a)
    assert callers == {
        0x437b7200: [0x437b7682, 0x437b76d4],
        0x437b74a4: [0x437b768c, 0x437b76de, 0x437b770c],
        0x437b7844: [0x437b7ed4],
        0x437b7d6c: [0x437b7ee6],
        0x437b7c8c: [0x437b7ee0],
    }
    for cs in callers.values():
        for c in cs:
            assert 0x437b7200 <= c <= 0x437b7f00


# --------------------------------------------------------------------------
# 4. Semántica verificada en el código
# --------------------------------------------------------------------------

def test_flags_de_ojo_en_el_contexto(data):
    """Los dos flags del contexto se leen en [ctx+0xde] y [ctx+0xdf]."""
    # 0x437b723e: ldrb.w r3,[r4,#0xdf]  -> 0xf894 0x30df
    assert data[0x437b723e - BASE:0x437b7242 - BASE] == bytes.fromhex("94f8df30")
    # 0x437b7274: ldrb.w r3,[r4,#0xde]  -> 0xf894 0x30de
    assert data[0x437b7274 - BASE:0x437b7278 - BASE] == bytes.fromhex("94f8de30")


def test_face_y_obj_en_el_contexto(data):
    """face_on = [ctx+0x49c] y obj_on = [ctx+0x49e]."""
    assert data[0x437b7868 - BASE:0x437b786c - BASE] == bytes.fromhex("93f89c24")
    assert data[0x437b786e - BASE:0x437b7872 - BASE] == bytes.fromhex("93f89e24")


def test_ranura_del_callback_de_disparo_tactil(data):
    """El puntero de callback vive en 0x43eb3bf0 y se invoca con `blx r1`."""
    assert u32(data, 0x43eb3bf0) == 0
    # 0x437b7fa2: blx r1  -> 0x4788
    assert u16(data, 0x437b7fa2) == 0x4788
    # 0x437b7fa0: cbz r1, #0x437b7fa6  -> 0xb109
    assert u16(data, 0x437b7fa0) == 0xB109


def test_ruta_de_error_de_la_trajа_null_cb(data):
    """Si el callback es NULL se emite la traza #7 en 0x43ca6a66."""
    assert cstr(data, 0x43ca6a66) == (
        "[CAMERA_MAIN_FC]: ReplyForTouchShutter ERROR - NULL cb_func")
    assert pic_target(data, 0x437b7fae) == 0x43ca6a66


# --------------------------------------------------------------------------
# 5. Diferencial
# --------------------------------------------------------------------------

def test_el_token_no_existe_en_a7s_ni_en_a6300():
    assert _bytes(A7S).count(TOKEN) == 0
    assert _bytes(A6300).count(TOKEN) == 0


def test_los_nucleos_de_texto_no_existen_en_los_otros_firmwares():
    a7s = _bytes(A7S)
    a6300 = _bytes(A6300)
    for _v, text, _f in STRINGS:
        core = text[len(PREFIX):].encode("latin1")
        assert core not in a7s
        assert core not in a6300


def test_el_codigo_del_modulo_no_existe_en_los_otros_firmwares(data):
    a7s = _bytes(A7S)
    a6300 = _bytes(A6300)
    for addr, ln in FRAGMENTS:
        frag = data[addr - BASE:addr - BASE + ln]
        assert frag not in a7s
        assert frag not in a6300


def test_la_biblioteca_camera_fc_existe_en_los_tres_firmwares():
    for path in (BIN, A7S, A6300):
        d = _bytes(path)
        assert d.count(b"Camera::FC::") == 45
        assert d.count(b"FC/") == 101


def test_touchshutter_solo_en_la_a6000():
    assert _bytes(BIN).count(b"TouchShutter") == 3
    assert _bytes(A7S).count(b"TouchShutter") == 0
    assert _bytes(A6300).count(b"TouchShutter") == 0


# --------------------------------------------------------------------------
# 6. La cadena de disparo táctil documentada no toca el módulo
# --------------------------------------------------------------------------

CHAIN = [0x4379d838, 0x4379e6a8, 0x4379eba0, 0x43809ed8,
         0x437df640, 0x437df338, 0x437eabfc, 0x437e4de4]


def test_la_cadena_de_disparo_tactil_no_llama_al_modulo(data):
    """Ninguna función de la cadena salta a la zona FC ni a la biblioteca Camera::FC."""
    for start in CHAIN:
        a = start
        while a < start + 0x400:
            t = bl_target(data, a)
            if t is not None:
                assert not (0x437b6000 <= t < 0x437b8400), \
                    f"{start:#x} salta a la zona FC en {t:#x}"
                assert not (0x439d0000 <= t < 0x43a00000), \
                    f"{start:#x} salta a Camera::FC en {t:#x}"
            a += 2


def test_la_cadena_usa_el_id_0x3011(data):
    """El id 0x3011 se materializa en la ruta documentada (0x4379eba0)."""
    assert data.count(bytes.fromhex("11300000")) >= 1
