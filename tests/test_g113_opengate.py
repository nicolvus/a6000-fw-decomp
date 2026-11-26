"""G113 — parche av-cam del opengate (Unicorn): alto 3:2 del modo 0x19 y raster 1440×960 del codificador."""
import struct
import sys
from pathlib import Path

import pytest
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_R4,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/gui")]
import og_avcam_patch as P

AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
pytestmark = pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam no disponible")
SALIDA = 0x10000000


@pytest.fixture(scope="module")
def img():
    d = AVCAM.read_bytes()
    return d, P.apply_bytes(d)


def _perfil(data: bytes, ancho: int, alto: int, modo: int, codec: int = 0) -> int:
    """Ejecuta FUN_436124b8(data=estructura de petición) y devuelve el índice de perfil (0 = error)."""
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(P.BASE, (len(data) + 0xFFFFF) // 0x100000 * 0x100000 + 0x100000)
    mu.mem_write(P.BASE, data)
    mu.mem_map(0x20000000, 0x3000)
    req, codec_ptr = 0x20000000, 0x20002000
    buf = bytearray(0x60)
    buf[0x4E] = modo
    struct.pack_into("<H", buf, 0x56, ancho)
    struct.pack_into("<H", buf, 0x58, alto)
    mu.mem_write(req, bytes(buf))
    mu.mem_write(codec_ptr, struct.pack("<I", codec))
    mu.reg_write(UC_ARM_REG_SP, 0x20001000)
    mu.reg_write(UC_ARM_REG_LR, SALIDA | 1)
    mu.reg_write(UC_ARM_REG_R0, 0x20000080)
    mu.reg_write(UC_ARM_REG_R1, req)
    mu.reg_write(UC_ARM_REG_R2, 4)
    mu.reg_write(UC_ARM_REG_R3, codec_ptr)
    error = []
    mu.hook_add(UC_HOOK_CODE, lambda m, a, s, u: (error.append(1), m.emu_stop()) if a in (SALIDA, 0x435AB880) else None)
    mu.emu_start(0x436124B8 | 1, SALIDA, count=500)
    return 0 if error else mu.reg_read(UC_ARM_REG_R0)


def test_patch_idempotente_y_bytes(img):
    orig, nuevo = img
    assert P.apply_bytes(nuevo) == nuevo
    assert P.apply_24p(P.apply_24p(orig)) == P.apply_24p(orig)
    assert P.alto_camcore(orig) == 1124 and P.alto_camcore(nuevo) == 1333
    # el resto de la fila 72 B del modo 0x19 no cambia
    fila = slice(P.ALTO_PTR - P.BASE - 0x3C, P.ALTO_PTR - P.BASE + 0x0C)
    assert orig[fila] != nuevo[fila] and orig[fila][:0x3C] == nuevo[fila][:0x3C]
    assert orig[fila][0x3E:] == nuevo[fila][0x3E:]


def test_camcore_3_2_sin_tocar_periodo(img):
    _, nuevo = img
    for tabla in (0x43BC1AE8, 0x43BC1B84):           # A (60Hz) y B (50Hz): el modo 0x19 conserva a·b
        a, b, _c = struct.unpack_from("<III", nuevo, tabla - P.BASE + 12 * P.MODO_OG)
        assert (a, b) == (693, 1625)
        assert P.alto_camcore(nuevo) < b              # 1333 líneas activas caben en 1625 de cuadro


def test_encoder_acepta_1440x960(img):
    _, nuevo = img
    assert _perfil(nuevo, 1440, 960, modo=1) == 1     # camino progresivo (perfil 1, 1440×1080 → 960)
    assert _perfil(nuevo, 1440, 960, modo=0) == 0     # el camino entrelazado (perfil 4 = 540) no se toca


def test_encoder_conserva_1440x1080(img):
    orig, nuevo = img
    for d in (orig, nuevo):                            # AVCHD 1440×1080 sigue funcionando
        assert _perfil(d, 1440, 1080, modo=1) == 1    # AVCHD 1440×1080 progresivo sigue en el perfil 1
        assert _perfil(d, 1440, 1080, modo=0) == 4    # 1440×1080i sigue en el perfil 4 (540 por campo)


def test_encoder_conserva_1080p_y_720p(img):
    orig, nuevo = img
    for d in (orig, nuevo):
        assert _perfil(d, 1920, 1080, modo=1) == 7        # param_3=4 ⇒ 7; 1080i (5) daría 6
        assert _perfil(d, 1280, 720, modo=1) == 5        # +0x32 = 0 ⇒ perfil 5 (8 si 6/7)
        assert _perfil(d, 640, 480, modo=1) == 3


def _pedido(data: bytes, ancho: int, alto: int) -> tuple[int, int]:
    """Ejecuta la cueva OG-E con un bloque de formato falso y devuelve (ancho, alto) tras el paso."""
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(P.BASE, (len(data) + 0xFFFFF) // 0x100000 * 0x100000 + 0x100000)
    mu.mem_write(P.BASE, data)
    mu.mem_map(0x20000000, 0x2000)
    objeto = 0x20000000                                   # r4 = objeto; el bloque de formato va en +0x404
    mu.mem_write(objeto + 0x45A, struct.pack("<HH", ancho, alto))
    mu.reg_write(UC_ARM_REG_R4, objeto)
    mu.reg_write(UC_ARM_REG_LR, SALIDA | 1)
    mu.hook_add(UC_HOOK_CODE, lambda m, a, s, u: m.emu_stop() if a in (0x43A7C8FA, SALIDA) else None)
    mu.emu_start(P.CUEVA_PEDIDO | 1, 0x43A7C8FA, count=100)
    return struct.unpack("<HH", mu.mem_read(objeto + 0x45A, 4))


def test_pedido_1080p_pasa_a_1440x960(img):
    orig, nuevo = img
    assert bytes(nuevo[P.SITIO_PEDIDO - P.BASE:P.SITIO_PEDIDO - P.BASE + 4]) != bytes.fromhex(P.BL_ORIG)
    assert _pedido(nuevo, *P.PEDIDO_VIEJO) == P.PEDIDO_OG          # 1920×1080 → 1440×960
    assert _pedido(nuevo, 1280, 720) == (1280, 720)                # 720p intacto
    assert _pedido(nuevo, 1440, 1080) == (1440, 1080)              # AVCHD intacto
    assert _pedido(nuevo, 640, 480) == (640, 480)                  # 480p intacto
    assert not any(orig[P.CUEVA_PEDIDO - P.BASE:P.CUEVA_PEDIDO - P.BASE + 40])


def test_60p_3_2_cabe_en_el_cuadro(img):
    """OG-D: 676×1333 ciclos = 59,986 Hz; 1333 líneas activas caben en el cuadro de 1333."""
    orig, _nuevo = img
    n60 = P.apply_bytes(orig)
    assert P.apply_bytes(n60) == n60
    for i in P.MODOS_60P:
        assert struct.unpack_from("<H", n60, P.CAMCORE + 72 * i + 0x3C - P.BASE)[0] == P.ALTO_OG
        for tabla in (0x43BC1AE8, 0x43BC1B84):
            a, b, _c = struct.unpack_from("<III", n60, tabla - P.BASE + 12 * i)
            assert (a, b) == P.AB_60P and a * b <= 901_108
    # el modo 24p conserva su periodo (48 Hz) y el 16:9 de 60p ya no existe en 0x10/0x1a
    assert struct.unpack_from("<III", n60, 0x43BC1AE8 - P.BASE + 12 * P.MODO_OG)[:2] == (693, 1625)


def test_altura_no_soportada_sigue_siendo_error(img):
    """1440×1080 sigue siendo la única altura válida a 1440 de ancho: 1000 no entra (no lo inventamos)."""
    orig, nuevo = img
    assert _perfil(nuevo, 1440, 1000, modo=1) == 0
    assert _perfil(orig, 1440, 960, modo=1) == 0       # antes del parche, 1440×960 no existía
