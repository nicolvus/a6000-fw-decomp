"""G33: Black Level, Black Gamma, Knee y Gamma Still sobre la curva de gamma del núcleo — Unicorn sobre `av-cam.bin` (A6000 fw3.21) parcheado."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
uc = pytest.importorskip("unicorn")
pytest.importorskip("keystone")
pytestmark = pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam.bin ausente")
import pp_curves_patch
import pp_tone_patch as T
from unicorn import UC_HOOK_CODE, Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *

B, TAB = 0x43541000, 0x44001404
STACK, END = 0x45000000, 0x45100000


def imagen():
    base = AVCAM.read_bytes()
    img = bytearray(pp_curves_patch.apply(base, pp_curves_patch.patches(base, pp_curves_patch.A7S.read_bytes(),
                                                                          pp_curves_patch.A6300.read_bytes() if pp_curves_patch.A6300.is_file() else None)))
    for a, b, _ in T.patches(bytes(img)):
        img[a - B:a - B + len(b)] = b
    return bytes(img)


class Cam:
    def __init__(self, img=None):
        self.img = img or imagen()
        self.mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.mu.mem_map(B, (len(self.img) + 0xFFF) & ~0xFFF)
        self.mu.mem_write(B, self.img)
        self.mu.mem_map(STACK, 0x200000)

    def run(self, start, regs, stop, count=2_000_000):
        mu = self.mu
        for r, v in regs.items():
            mu.reg_write(r, v)
        mu.reg_write(UC_ARM_REG_SP, STACK + 0x100000)
        mu.reg_write(UC_ARM_REG_LR, END | 1)
        mu.mem_write(END, b"\x00\xbf" * 4)
        mu.emu_start(start | 1, stop, count=count)

    def u16s(self, a, n):
        return struct.unpack(f"<{n}H", bytes(self.mu.mem_read(a, 2 * n)))

    def ptr(self, g, modo):
        return struct.unpack("<I", bytes(self.mu.mem_read(TAB + 8 * g + 4 * modo, 4)))[0]

    def pp(self, **kw):
        campos = ["black", "bgr", "bgl", "sel", "kmode", "kmax", "ksens", "kpoint", "kslope", "dmode", "dlevel", "dvh", "dbw", "dlimit", "dcrisp", "dhil"]
        b = bytearray(16)
        for k, v in kw.items():
            b[campos.index(k)] = v & 0xFF
        self.mu.mem_write(T.SNAP, bytes(b))
        self.mu.mem_write(T.CACHE, bytes(24))

    def curva(self, orig, idx):
        self.run(T.CODE, {UC_ARM_REG_R0: orig, UC_ARM_REG_R1: idx}, END)
        return self.mu.reg_read(UC_ARM_REG_R0)


@pytest.fixture(scope="module")
def cam():
    return Cam()


MOVIE = (10, 1)


def test_neutro_devuelve_el_puntero_original(cam):
    p = cam.ptr(*MOVIE)
    for sel in (0, 4, 3, 2):
        cam.pp(sel=sel, kmode=0, kmax=4, ksens=1)
        assert cam.curva(p, 21) == p
    cam.pp(sel=4, black=0, bgl=0, kmode=1, kpoint=12, kslope=0)         # knee manual en 105 %: fuera de rango
    assert cam.curva(p, 21) == p


def test_black_level_sube_y_baja_el_negro_y_conserva_el_blanco(cam):
    p = cam.ptr(*MOVIE)
    orig = cam.u16s(p, 2048)
    cam.pp(sel=4, kmax=4, black=15)
    w = cam.curva(p, 21)
    assert w == T.W
    y = cam.u16s(w, 2048)
    assert y[0] > orig[0] + 40 and y[1500] > orig[1500] and y[2047] == orig[2047]
    cam.pp(sel=4, kmax=4, black=-15)
    y = cam.u16s(cam.curva(p, 21), 2048)
    assert y[0] == 0 and y[400] < orig[400] and y[2047] == orig[2047]


def test_la_cola_de_parametros_se_conserva_y_la_curva_es_monotona(cam):
    p = cam.ptr(*MOVIE)
    for kw in (dict(black=15, bgl=7, bgr=0, kmax=4), dict(black=-15, bgl=-7, bgr=2, kmax=4), dict(kmode=1, kpoint=0, kslope=-5), dict(kmode=0, kmax=0, ksens=0)):
        cam.pp(sel=4, **kw)
        w = cam.curva(p, 21)
        assert bytes(cam.mu.mem_read(w + 0x1000, 0x1A)) == bytes(cam.mu.mem_read(p + 0x1000, 0x1A))
        y = cam.u16s(w, 2048)
        assert all(a <= b for a, b in zip(y, y[1:])) and max(y) <= 2047


def test_black_gamma_actua_solo_en_sombras_y_segun_el_rango(cam):
    p = cam.ptr(*MOVIE)
    orig = cam.u16s(p, 2048)
    cam.pp(sel=4, kmax=4, bgl=7, bgr=0)
    y = cam.u16s(cam.curva(p, 21), 2048)
    cambia = [i for i in range(2048) if y[i] != orig[i]]
    assert cambia and max(orig[i] for i in cambia) <= 310 and all(y[i] > orig[i] for i in cambia)
    cam.pp(sel=4, kmax=4, bgl=7, bgr=2)
    y2 = cam.u16s(cam.curva(p, 21), 2048)
    assert max(orig[i] for i in range(2048) if y2[i] != orig[i]) <= 104
    cam.pp(sel=4, kmax=4, bgl=-7, bgr=1)
    y3 = cam.u16s(cam.curva(p, 21), 2048)
    assert any(y3[i] < orig[i] for i in range(2048)) and not any(y3[i] > orig[i] for i in range(2048))


def test_knee_manual_comprime_las_luces_y_el_punto_y_la_pendiente_cuentan(cam):
    p = cam.ptr(*MOVIE)
    orig = cam.u16s(p, 2048)
    cam.pp(sel=4, kmode=1, kpoint=0, kslope=0)                           # 75 %, pendiente 0,5
    y = cam.u16s(cam.curva(p, 21), 2048)
    pt = 1023 * 750 // 1000
    assert all(y[i] == orig[i] for i in range(2048) if orig[i] <= pt) and y[2047] < orig[2047]
    cam.pp(sel=4, kmode=1, kpoint=0, kslope=5)                           # más comprimida
    y5 = cam.u16s(cam.curva(p, 21), 2048)
    cam.pp(sel=4, kmode=1, kpoint=0, kslope=-5)
    ym5 = cam.u16s(cam.curva(p, 21), 2048)
    assert y5[2047] < y[2047] < ym5[2047]
    cam.pp(sel=4, kmode=0, kmax=0, ksens=0)                              # automática: suave
    ya = cam.u16s(cam.curva(p, 21), 2048)
    assert orig[2047] > ya[2047] > y[2047]


def test_knee_y_black_gamma_no_afectan_a_las_gammas_logaritmicas(cam):
    p = cam.ptr(0x17, 1)
    orig = cam.u16s(p, 2048)
    cam.pp(sel=2, kmode=1, kpoint=0, kslope=5, bgl=7)
    assert cam.curva(p, 0x17 * 2 + 1) == p
    cam.pp(sel=2, black=10, kmode=1, kpoint=0, bgl=7)
    y = cam.u16s(cam.curva(p, 0x17 * 2 + 1), 2048)
    assert y[0] > orig[0] and y[2047] == orig[2047] and y[1000] > orig[1000]


def test_gamma_still_en_video_usa_la_curva_de_fotografia(cam):
    p = cam.ptr(*MOVIE)
    foto = cam.u16s(cam.ptr(0, 0), 2048)
    cam.pp(sel=5, kmax=4)
    w = cam.curva(p, 21)
    assert w == T.W and list(cam.u16s(w, 2048)) == list(foto)
    assert bytes(cam.mu.mem_read(w + 0x1000, 0x1A)) == bytes(cam.mu.mem_read(p + 0x1000, 0x1A))
    cam.pp(sel=4, kmax=4)
    assert cam.curva(p, 21) == p                                          # Movie no cambia
    cam.pp(sel=5, kmax=4)
    assert cam.curva(cam.ptr(10, 0), 20) == 0                             # en fotografía (puntero nulo) no se inventa nada


def test_la_cache_evita_recalcular_y_se_invalida_al_cambiar_un_ajuste(cam):
    p = cam.ptr(*MOVIE)
    cam.pp(sel=4, kmax=4, black=5)
    a = cam.u16s(cam.curva(p, 21), 2048)
    cam.mu.mem_write(T.W, b"\xAA\xAA")                                    # si recalculara, sobrescribiría
    assert cam.u16s(cam.curva(p, 21), 1)[0] == 0xAAAA
    cam.mu.mem_write(T.SNAP, bytes([6]))
    b = cam.u16s(cam.curva(p, 21), 2048)
    assert b[0] > a[0]


def test_gancho_del_desempaquetador_copia_los_bytes_17_a_26(cam):
    msg = 0x45010000
    cam.mu.mem_write(msg, bytes(0x36))
    datos = bytes(range(0x40, 0x50))
    cam.mu.mem_write(msg + 0x17, datos)
    cam.mu.mem_write(T.SNAP, bytes(16))
    cam.run(0x43802A28, {UC_ARM_REG_R0: msg}, END)
    assert bytes(cam.mu.mem_read(T.SNAP, 16)) == datos and cam.mu.reg_read(UC_ARM_REG_R0) == 1


def test_tramplines_devuelven_el_puntero_en_el_registro_de_destino(cam):
    p = cam.ptr(*MOVIE)
    cam.pp(sel=4, kmax=4, black=15)
    # sitio 1: ldr.w r3,[r3,r1,lsl #2] con r3 = TAB, r1 = índice; deben conservar r0, r1, r2
    cam.run(0x43853226, {UC_ARM_REG_R3: TAB, UC_ARM_REG_R1: 21, UC_ARM_REG_R0: 111, UC_ARM_REG_R2: 222}, 0x4385322A)
    r = cam.mu.reg_read
    assert r(UC_ARM_REG_R3) == T.W and (r(UC_ARM_REG_R0), r(UC_ARM_REG_R1), r(UC_ARM_REG_R2)) == (111, 21, 222)
    # sitio 2: ldr.w r2,[r7,r2,lsl #2]
    cam.run(0x4385392E, {UC_ARM_REG_R7: TAB, UC_ARM_REG_R2: 21, UC_ARM_REG_R0: 5, UC_ARM_REG_R1: 6, UC_ARM_REG_R3: 7}, 0x43853932)
    assert r(UC_ARM_REG_R2) == T.W and (r(UC_ARM_REG_R0), r(UC_ARM_REG_R1), r(UC_ARM_REG_R3)) == (5, 6, 7)
    # sitio 3: ldr.w r6,[r3,r2,lsl #2]
    cam.run(0x43853C8E, {UC_ARM_REG_R3: TAB, UC_ARM_REG_R2: 21, UC_ARM_REG_R6: 0, UC_ARM_REG_R0: 9, UC_ARM_REG_R1: 8}, 0x43853C92)
    assert r(UC_ARM_REG_R6) == T.W and (r(UC_ARM_REG_R0), r(UC_ARM_REG_R1), r(UC_ARM_REG_R2), r(UC_ARM_REG_R3)) == (9, 8, 21, TAB)
    # con PP desactivado devuelven el puntero de la tabla
    cam.pp(sel=0, black=15)
    cam.run(0x43853226, {UC_ARM_REG_R3: TAB, UC_ARM_REG_R1: 21}, 0x4385322A)
    assert r(UC_ARM_REG_R3) == p


def test_pp_curve_cabe_en_la_cueva():
    assert T.CODE + len(T.BIN.read_bytes()) <= T.W and T.W + 0x1020 <= T.CAVE_END


# --- Detail --------------------------------------------------------------------------------------------------------------------------------------
def gancho_detail(cam, site, regs, estructura, off, ret):
    """Ejecuta el sitio con una estructura de halfwords en sp+off y devuelve (estructura tras el gancho, registros)."""
    sp = STACK + 0x100000
    cam.mu.mem_write(sp + off, struct.pack(f"<{len(estructura)}H", *estructura))
    regs = dict(regs)
    regs[UC_ARM_REG_SP] = sp
    for r, v in regs.items():
        cam.mu.reg_write(r, v)
    cam.mu.reg_write(UC_ARM_REG_LR, END | 1)
    cam.mu.mem_write(END, b"\x00\xbf" * 4)
    cam.mu.emu_start(site | 1, ret, count=100000)
    return struct.unpack(f"<{len(estructura)}H", bytes(cam.mu.mem_read(sp + off, 2 * len(estructura)))), cam.mu.reg_read


def test_detail_modo_automatico_o_pp_apagado_no_toca_nada(cam):
    for kw in (dict(sel=4, dmode=0, dlevel=7, dcrisp=7), dict(sel=0, dmode=1, dlevel=7, dcrisp=7)):
        cam.pp(**kw)
        g, _ = gancho_detail(cam, 0x438B3D52, {UC_ARM_REG_R5: 0x1000}, (200, 8, 8), 0xE0, 0x438B3D56)
        assert g == (200, 8, 8)
        c, _ = gancho_detail(cam, 0x438B336E, {UC_ARM_REG_R7: 0x1000}, (10, 20, 30, 1, 40, 50, 60, 2), 0xC8, 0x438B3372)
        assert c == (10, 20, 30, 1, 40, 50, 60, 2)


def test_detail_level_vh_y_limit_sobre_las_ganancias_apc(cam):
    def g(**kw):
        cam.pp(sel=4, dmode=1, dlimit=7, **kw)
        out, r = gancho_detail(cam, 0x438B3D52, {UC_ARM_REG_R5: 0x1000, UC_ARM_REG_R0: 77}, (200, 8, 8), 0xE0, 0x438B3D56)
        assert r(UC_ARM_REG_R6) == 0x1000 + 0x760 and r(UC_ARM_REG_R0) == 77        # instrucción desplazada ejecutada y registros conservados
        return out
    assert g(dlevel=0) == (200, 8, 8)
    assert g(dlevel=7)[0] > 200 > g(dlevel=-7)[0] > 0
    assert g(dlevel=7)[0] <= 0x1FF
    mas_v, mas_h = g(dvh=2), g(dvh=-2)
    assert mas_v[1] > 8 > mas_h[1] and mas_v[2] < 8 < mas_h[2]
    cam.pp(sel=4, dmode=1, dlimit=0, dlevel=0)
    out, _ = gancho_detail(cam, 0x438B3D52, {UC_ARM_REG_R5: 0x1000}, (400, 8, 8), 0xE0, 0x438B3D56)
    assert out[0] < 400                                                             # Limit bajo recorta


def test_detail_crispening_sube_el_coring_menos_los_aplk(cam):
    cam.pp(sel=4, dmode=1, dcrisp=7)
    c, r = gancho_detail(cam, 0x438B336E, {UC_ARM_REG_R7: 0x2000}, (10, 20, 30, 1, 40, 50, 460, 2), 0xC8, 0x438B3372)
    assert r(UC_ARM_REG_R4) == 0x2000 + 0x760
    assert c[0] > 10 and c[1] > 20 and c[2] > 30 and c[4] > 40 and c[5] > 50 and c[6] == 0x1FF
    assert c[3] == 1 and c[7] == 2
    cam.pp(sel=4, dmode=1, dcrisp=0)
    c, _ = gancho_detail(cam, 0x438B336E, {UC_ARM_REG_R7: 0x2000}, (10, 20, 30, 1, 40, 50, 60, 2), 0xC8, 0x438B3372)
    assert c == (10, 20, 30, 1, 40, 50, 60, 2)
