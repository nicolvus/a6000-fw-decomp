"""G95 (LUT-PKG-1) — paquete `.LUT` precalculado en el PC: el hilo de la SD solo valida y copia (ARM compilado = referencia)."""
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lut"))
import cube_a6000 as C
import lut_pkg as P
import lut_sd_userland as U

pytestmark = pytest.mark.skipif(not C.BIN.exists(), reason="falta av-cam.bin")


@pytest.fixture(scope="module")
def arm():
    return U.compila()


def llama(arm, datos: bytes) -> bytes | None:
    """Ejecuta `lutsd_paquete(p, n, dst)` del ARM compilado en Unicorn → carga copiada o None."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_SP,
    )
    blob, sim = arm
    code, buf, dst, pila, fin = 0x10000000, 0x20000000, 0x21000000, 0x30000000, 0x31000000
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for a in (code, buf, dst, pila, fin):
        mu.mem_map(a, 0x10000)
    mu.mem_write(code, blob)
    mu.mem_write(buf, datos)
    for r, v in ((UC_ARM_REG_R0, buf), (UC_ARM_REG_R1, len(datos)), (UC_ARM_REG_R2, dst), (UC_ARM_REG_SP, pila + 0x8000), (UC_ARM_REG_LR, fin | 1)):
        mu.reg_write(r, v)
    mu.emu_start((code + sim["lutsd_paquete"]) | 1, fin, count=2_000_000)
    return bytes(mu.mem_read(dst, P.CARGA)) if mu.reg_read(UC_ARM_REG_R0) == 1 else None


def test_paquete_ida_y_vuelta_y_arm_igual_a_referencia(arm):
    carga = bytes(np.random.default_rng(1).integers(0, 256, P.CARGA, dtype=np.uint8))
    b = P.paquete(carga)
    assert len(b) == P.TAM and P.valida(b) == carga and llama(arm, b) == carga
    malos = [b[:-1], b + b"\0", bytearray(b), bytearray(b), bytearray(b), bytearray(b)]
    malos[2][0] ^= 1                    # firma
    malos[3][4] = 2                     # versión
    malos[4][6] ^= 1                    # longitud declarada
    malos[5][100] ^= 0x80               # carga ⇒ CRC
    for m in malos:
        assert P.valida(bytes(m)) is None and llama(arm, bytes(m)) is None


def test_paquete_de_cube_es_la_tabla_ajustada_en_el_pc(tmp_path):
    ruta = tmp_path / "pelicula.cube"
    C.escribe_cube(ruta, C.lut_pelicula, 17, "pelicula")
    carga = P.valida(P.desde_cube(ruta))
    img = C.BIN.read_bytes()
    perm = list(struct.unpack_from("<405H", img, P.D.PERM - P.D.BASE))
    tab, lo, hi = C.lee_cube(ruta)
    q = C.descompone(lambda x: C.aplica_cube(tab, lo, hi, x), usa_M=False, usa_T=False, usa_L=True).q
    assert carga == P.D.empaqueta_21(C.empaqueta_hw(q, img), perm)


def test_hilo_usa_el_paquete_antes_que_el_cube(arm):
    cam = U.Camara()
    if not hasattr(cam, "acepta"):
        pytest.skip("el Fsys simulado de esta versión solo sirve .cube")
    carga = bytes(np.random.default_rng(2).integers(0, 256, P.CARGA, dtype=np.uint8))
    malo = bytearray(P.paquete(carga))
    malo[200] ^= 1
    cam.ficheros = {1: P.paquete(carga), 2: bytes(malo)}       # ranura 1: paquete válido; 2: CRC malo y sin .cube ⇒ inválida
    cam.acepta = lambda p, letra: p.startswith(letra + ":/LUT/LUT") and p.endswith(".LUT")
    cam.pasos = [None]
    U.emula(cam, *arm)
    b = cam.backup
    assert b[8:14] == bytes([1, 0, 0, 0, 0, 0]) and b[16:16 + P.CARGA] == carga
    assert "E:/LUT/LUT1.LUT" in cam.aperturas
