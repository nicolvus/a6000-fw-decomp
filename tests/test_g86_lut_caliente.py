"""G86 FN-LUT-2 — cambio de LUT en tiempo real: gancho en la máquina de estados «[LUT] Write Cnt» (`0x437a24fc`) emulado con Unicorn sobre los bytes reales de `av-cam`.

Contexto emulado de la tarea de imagen: `this` (r0) = {+0 paquete, +8 config, +0xc objeto de trabajo con el contador `[+0x8a0]`}; llamadas externas a la máquina sustituidas por `movs r0,#v; bx lr`
(salvo `1a7c`, el detector de cambios, que es código real); `Copy3DLUT` (`0x437a1d7c`) se sustituye por un marcador porque su emulación completa ya está cubierta en `test_g71_lut.py`.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/lut")]
import lut_patch as L
import lut_sd_userland as U

BASE, MAQ, END = L.BASE, 0x437A24FC, 0x30000000
THIS, PKT, CFG, WORK, AUX, STACK = 0x20000000, 0x20001000, 0x20002000, 0x20004000, 0x20008000, 0x10000000
CNT = 0x8A0
COPY3D, GENERADOR = 0x437A1D7C, 0x437A1A7C
STUBS = {0x43AEB798: 0, 0x437A1D14: 0, 0x437A4BCC: 0, 0x43AEB0CC: 0, 0x43AEB6D4: 0, 0x437A19D0: 0, 0x43902718: 0, 0x437A4738: 0, COPY3D: 1}
pytestmark = pytest.mark.skipif(not L.C.BIN.is_file(), reason="av-cam.bin ausente")


@pytest.fixture(scope="module")
def imagenes():
    orig = L.C.BIN.read_bytes()
    return orig, L.apply_bytes(orig)


class Maquina:
    """Sesión Unicorn con la imagen y el contexto de la tarea; `ejecuta(valor)` simula una pasada de la máquina con el Backup = `valor`."""

    def __init__(self, img: bytes, valor: int = 0, estado: int = 0, ack: int = 0, pkt1: int = 0):
        from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
        self.mu = mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        mu.mem_map(BASE & ~0xFFF, ((len(img) + (BASE & 0xFFF)) + 0x200000) & ~0xFFF)
        mu.mem_write(BASE, img)
        for a, s in ((STACK - 0x10000, 0x20000), (THIS, 0x1000), (PKT, 0x1000), (CFG, 0x1000), (WORK, 0x4000), (AUX, 0x1000), (END, 0x1000)):
            mu.mem_map(a, s)
        for va, ret in STUBS.items():
            mu.mem_write(va, bytes([ret, 0x20, 0x70, 0x47]))        # movs r0,#ret ; bx lr
        mu.mem_write(THIS, struct.pack("<IIII", PKT, 0, CFG, WORK) + struct.pack("<II", 0, AUX))
        mu.mem_write(PKT + 1, bytes([pkt1]))
        mu.mem_write(PKT + 0xC0, struct.pack("<I", AUX))               # [pkt+0xc0] = bloque de ajustes de color (ceros)
        mu.mem_write(CFG + 0x7E, bytes([0x20]))                      # (sb>>5)&3 == 1: rama de las 3 ranuras de la tabla de ajustes
        mu.mem_write(WORK + CNT, bytes([estado]))
        mu.mem_write(0x43F9A54B, bytes([ack]))                       # celda que lee `0x437a9934` (eco del contador de trama)
        self.visitas: list[int] = []
        mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: self.visitas.append(a), begin=COPY3D, end=COPY3D)
        self.valor = None
        self.backup(valor)

    def backup(self, valor: int) -> None:
        """La rueda: la UI escribe el índice en el Backup `0x1070211` (se simula con el servicio de lectura = `movs r2,#v; strb r2,[r1]; movs r0,#0; bx lr`)."""
        self.mu.mem_write(0x435613B0, bytes([valor, 0x22, 0x0A, 0x70, 0x00, 0x20, 0x70, 0x47]))
        self.mu.ctl_remove_cache(0x435613B0, 0x435613B8)             # Unicorn conserva el bloque ya traducido
        self.valor = valor

    def reposo(self, estado: int = 0, ack: int = 0) -> None:
        """Pasadas con el eco = 1 hasta que los cachés del detector de cambios y la celda de la cueva reflejan el entorno (la máquina vuelve a 0); luego fija contador y eco y borra el registro de llamadas."""
        self.mu.mem_write(0x43F9A54B, bytes([1]))
        for _ in range(4):
            self.ejecuta()
        assert self.leer(WORK + CNT) == 0
        self.mu.mem_write(WORK + CNT, bytes([estado]))
        self.mu.mem_write(0x43F9A54B, bytes([ack]))
        self.mu.mem_write(CFG + 0x94, bytes(1))
        self.visitas.clear()

    def leer(self, a: int, n: int = 1) -> int:
        return int.from_bytes(self.mu.mem_read(a, n), "little")

    def ejecuta(self) -> None:
        from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP
        mu = self.mu
        mu.reg_write(UC_ARM_REG_SP, STACK)
        mu.reg_write(UC_ARM_REG_LR, END | 1)
        mu.reg_write(UC_ARM_REG_R0, THIS)
        mu.emu_start(MAQ | 1, END, count=200000)

    def estado(self) -> tuple[int, int, int, int]:
        """(contador, cfg[0x94], cfg[0x8c], cfg[0x90]) — el estado que la máquina deja para el aplicador."""
        return self.leer(WORK + CNT), self.leer(CFG + 0x94), self.leer(CFG + 0x8C, 4), self.leer(CFG + 0x90, 2)


def test_gancho_de_la_maquina_es_un_bl_a_la_cueva_en_zona_libre(imagenes):
    orig, p = imagenes
    off = L.HOOK_MAQ[0] - BASE
    assert orig[off:off + 4] == L.HOOK_MAQ[1] == bytes.fromhex("87680368")      # ldr r7,[r0,#8]; ldr r3,[r0]
    assert p[off:off + 4] != orig[off:off + 4]
    assert L.D.ZONA_L18[0] <= L.cueva_maquina()[0] < L.D.ZONA_L18[1]


def test_rueda_sin_el_gancho_no_rearma(imagenes):
    """Línea base: con la máquina de fábrica y el ajuste cambiando, la máquina no hace nada (contador 0 y sin Copy3DLUT)."""
    m = Maquina(imagenes[0])
    m.reposo()
    for v in (1, 2, 0):
        m.backup(v)
        m.ejecuta()
        assert m.estado()[0] == 0 and not m.visitas


def test_secuencia_1_2_3_1_off_rearma_cada_vez_y_entrega_la_tabla(imagenes):
    """Cada giro de la rueda: esa misma pasada de la máquina (código real) re-arma el estado 1, `Copy3DLUT` se ejecuta una vez y deja `cfg[0x8c/0x90]` listos; el gancho de escritura entrega la tabla del look."""
    p = imagenes[1]
    tablas = [bytes((i * 37 + k) % 256 for i in range(L.D.LUT_BYTES)) for k in (1, 2, 3)]
    blob = U.blob_tablas({k: t for k, t in zip((1, 2, 3), tablas)})
    m = Maquina(p)
    m.reposo()                                                  # arranque en Off, máquina en reposo
    orig_ptr, entregado = 0x11223344, []
    for opcion in (1, 2, 3, 1, 0):
        m.mu.mem_write(0x43F9A54B, bytes([1]))                  # eco del hardware recibido: la máquina vuelve a reposo entre giros
        for _ in range(3):
            m.ejecuta()
        assert m.estado()[0] == 0
        m.visitas.clear()
        m.backup(opcion)
        m.ejecuta()
        cnt, flag, ptr, valido = m.estado()
        assert (cnt, flag, valido) == (2, 1, 1) and ptr == WORK + 0x8C8 and m.visitas == [COPY3D], (opcion, m.estado())
        r, hw, _ = L.emular(p, 0, opcion, blob, orig=orig_ptr)
        entregado.append(r if opcion == 0 else hw)
    perm = list(struct.unpack_from("<405H", p, L.D.PERM - L.BASE))
    assert entregado[:4] == [L.D.desempaqueta_21(t, perm) for t in (tablas[0], tablas[1], tablas[2], tablas[0])] and entregado[4] == orig_ptr


@pytest.mark.parametrize("estado", [0, 1, 2, 3])
@pytest.mark.parametrize("ack", [0, 1])
@pytest.mark.parametrize("pkt1", [0, 1])
def test_sin_cambio_de_ajuste_el_parche_es_transparente(imagenes, estado, ack, pkt1):
    """Con el ajuste estable (Off ya visto), la máquina parcheada deja EXACTAMENTE la misma memoria de contexto y las mismas llamadas que la de fábrica, en cualquier estado del contador."""
    orig, p = imagenes
    a, b = Maquina(orig, 0, 0, 0, pkt1), Maquina(p, 0, 0, 0, pkt1)
    for x in (a, b):
        x.reposo(estado, ack)
        x.ejecuta()
    for reg, n in ((WORK, 0x4000), (CFG, 0x1000), (PKT, 0x1000), (AUX, 0x1000), (THIS, 0x1000), (0x43F9A000, 0x1000)):
        assert bytes(a.mu.mem_read(reg, n)) == bytes(b.mu.mem_read(reg, n)), hex(reg)
    assert a.visitas == b.visitas


@pytest.mark.parametrize("estado", [0, 1, 2, 3])
def test_cambio_de_ajuste_en_cualquier_estado_converge_a_contador_2_y_escritura_valida(imagenes, estado):
    """Aunque la máquina esté a medias (esperando el eco), el giro la reinicia en el estado 1 y deja `cfg[0x8c/0x90]` listos: no hay que esperar a un cambio de modo."""
    m = Maquina(imagenes[1])
    m.reposo(estado)
    m.backup(2)
    m.ejecuta()
    cnt, flag, ptr, valido = m.estado()
    assert (cnt, flag, valido) == (2, 1, 1) and ptr == WORK + 0x8C8


def test_la_cueva_sin_contexto_no_hace_nada(imagenes):
    """Defensa: con config y objeto de trabajo nulos la cueva no accede a ellos (no hay escritura) y solo reproduce las dos cargas del gancho."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_R0,
        UC_ARM_REG_R3,
        UC_ARM_REG_R7,
        UC_ARM_REG_SP,
    )
    p = imagenes[1]
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE & ~0xFFF, ((len(p) + (BASE & 0xFFF)) + 0x200000) & ~0xFFF)
    mu.mem_write(BASE, p)
    for a, s in ((STACK - 0x10000, 0x20000), (THIS, 0x1000), (END, 0x1000)):
        mu.mem_map(a, s)
    mu.mem_write(0x435613B0, bytes([2, 0x22, 0x0A, 0x70, 0x00, 0x20, 0x70, 0x47]))
    mu.reg_write(UC_ARM_REG_SP, STACK)
    mu.reg_write(UC_ARM_REG_LR, END | 1)
    mu.reg_write(UC_ARM_REG_R0, THIS)                               # THIS a ceros: paquete, config y objeto de trabajo nulos
    mu.emu_start(L.cueva_maquina()[0] | 1, END, count=2000)
    assert mu.reg_read(UC_ARM_REG_R0) == THIS and mu.reg_read(UC_ARM_REG_R7) == 0 and mu.reg_read(UC_ARM_REG_R3) == 0
    assert bytes(mu.mem_read(THIS, 0x20)) == bytes(0x20)


def test_integracion_en_los_builds(tmp_path, imagenes):
    """El CFW de objetivos encadena `lut_patch.apply_bytes` (que ya lleva el gancho) y `build_fn_lut.avcam` produce la misma imagen."""
    import build_cfw_objetivos  # noqa: F401  (rutas de los parches encadenados)
    import build_fn_lut
    import build_overlay_objetivos as O
    assert L.apply_bytes in O.AVCAM
    out = build_fn_lut.avcam(L.C.BIN, tmp_path / "av-cam.bin")
    assert out.read_bytes() == imagenes[1]
    a = L.HOOK_MAQ[0] - BASE
    assert O.encadena(imagenes[0], O.AVCAM)[a:a + 4] == imagenes[1][a:a + 4] != imagenes[0][a:a + 4]
