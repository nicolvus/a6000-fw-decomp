"""G111 — Film: receta aplicada desde el hilo de la GUI y grises (FILM-9/FILM-10), en Unicorn sobre el binario real enlazado en su VA de vu2.

Se ejecutan `films_tramo_set` / `films_tramo_gris` (los que reciben los saltos de `setValue` e `isGrayedOut`); las funciones de vu2 (`FU.VU2`) son
sustitutos que registran sus argumentos. Iconos: `uxc_imagenes` (ida y vuelta sobre `image_cmn_169.uxc`).
"""
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/lut"), str(ROOT / "scripts/gui"), str(ROOT / "scripts")]
import film_userland as FU

NPZ = ROOT / "analysis/lut/g97/looks.npz"
VA = 0x7C8080
PP = (0x100, 0x100, 0x11F)                     # selector PP (primer ajuste PP) y rango de pids PP de una build con PP
TODAS = FU.ajuste_todas().pid
USUARIO_WB, USUARIO_DRO, USUARIO_PP = (8, 4800, -2, 5), 3, 4
MARCA_WB = (0x4D4C4946, 0x4E495742)
USUARIO_CS = {0x1070175: 2, 0x1070178: 1, 0x1070187: -2, 0x107018A: 3}
pytestmark = pytest.mark.skipif(not NPZ.exists(), reason="falta looks.npz")


@pytest.fixture(scope="module")
def compilado():
    return FU.compila(NPZ, VA, None, None, PP)


class VM:
    """Proceso mínimo: el segmento de Film en su VA, vu2 sustituido por ganchos, Backup en un dict."""
    MGR, VBP, BUF, PILA, PARA = 0x30000000, 0x31000000, 0x32000000, 0x40000000, 0x50000000
    BK_R, BK_W = 0x50000010, 0x50000020

    def __init__(self, compilado, valores):
        from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
        blob, self.sim = compilado
        self.mu = mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        mu.mem_map(VA & ~0xFFF, (len(blob) + 0x2FFF) & ~0xFFF)
        mu.mem_write(VA, blob)
        mu.mem_map(0xE0000, 0x200000)
        for a in (self.MGR, self.VBP, self.BUF, self.PARA):
            mu.mem_map(a, 0x10000)
        mu.mem_map(self.PILA, 0x10000)
        mu.mem_write(self.MGR + 4, struct.pack("<I", self.VBP))
        self.valores, self.bk, self.llamadas = dict(valores), {FU.BK_ID: FU.blob_esperado(0, NPZ)}, []
        self.inv = {v & ~1: k for k, v in FU.VU2.items()} | {self.BK_R: "Backup_read", self.BK_W: "Backup_write"}
        mu.hook_add(UC_HOOK_CODE, self._gancho, begin=0xE0000, end=0x2E0000)
        mu.hook_add(UC_HOOK_CODE, self._gancho, begin=self.PARA, end=self.PARA + 0x100)

    def r(self, k):
        from unicorn.arm_const import UC_ARM_REG_R0
        return self.mu.reg_read(UC_ARM_REG_R0 + k)

    def pila(self, k):
        from unicorn.arm_const import UC_ARM_REG_SP
        return struct.unpack("<i", self.mu.mem_read(self.mu.reg_read(UC_ARM_REG_SP) + 4 * k, 4))[0]

    def s32(self, x):
        return x - (1 << 32) if x & 0x80000000 else x

    def _vuelve(self, ret=None, pop=0):
        from unicorn.arm_const import (
            UC_ARM_REG_LR,
            UC_ARM_REG_PC,
            UC_ARM_REG_R0,
            UC_ARM_REG_SP,
        )
        mu = self.mu
        if ret is not None:
            mu.reg_write(UC_ARM_REG_R0, ret & 0xFFFFFFFF)
        if pop:                                  # continuación tras un prólogo `push {…, lr}` replicado: deshace la pila y vuelve al llamador
            sp = mu.reg_read(UC_ARM_REG_SP)
            pc = struct.unpack("<I", mu.mem_read(sp + 4 * (pop - 1), 4))[0]
            mu.reg_write(UC_ARM_REG_SP, sp + 4 * pop)
            mu.reg_write(UC_ARM_REG_PC, pc)
        else:
            mu.reg_write(UC_ARM_REG_PC, mu.reg_read(UC_ARM_REG_LR))

    def _gancho(self, mu, addr, size, _):
        n = self.inv.get(addr)
        if n is None:
            return
        r, w = self.r, lambda a, v: mu.mem_write(a, struct.pack("<i", v))
        cstr = lambda a: bytes(mu.mem_read(a, 32)).split(b"\0")[0].decode()
        if n == "V_GETVALUE":
            ok = r(1) in self.valores
            if ok:
                w(r(2), self.valores[r(1)])
            return self._vuelve(int(ok))
        if n == "V_SETVALUE":
            self.llamadas.append(("set", r(1), self.s32(r(2))))
            return self._vuelve(0)
        if n == "V_SET_CONT":                          # resto del setValue original: guarda el valor
            self.llamadas.append(("orig", r(1), r(2)))
            self.valores[r(1)] = r(2)
            return self._vuelve(0, pop=4)
        if n == "V_GRIS_CONT":
            return self._vuelve(0x77, pop=2)
        if n in ("V_WB_CTOR", "V_CS_CTOR", "V_DRO_CTOR", "P_FREE"):
            return self._vuelve(0)
        if n == "V_WB_GET":
            for k, v in enumerate(USUARIO_WB):
                w(r(2) if k == 0 else r(3) if k == 1 else self.pila(k - 2), v)
            return self._vuelve(0)
        if n == "V_WB_SET":                            # el objeto llega marcado para `films_tramo_wbinh`
            assert struct.unpack("<II", mu.mem_read(r(0) + 8, 8)) == MARCA_WB
            self.llamadas.append(("wb", self.s32(r(2)), self.s32(r(3)), self.pila(0), self.pila(1)))
            return self._vuelve(0)
        if n == "V_CS_SET":
            self.llamadas.append(("cs", r(2), self.s32(r(3)), self.pila(0), self.pila(1), self.pila(2)))
            return self._vuelve(0)
        if n == "V_WBINH_CONT":                        # resto del isInhOn original
            self.llamadas.append(("inh", r(2)))
            return self._vuelve(1, pop=4)
        if n == "V_DRO_GET":
            w(r(2), USUARIO_DRO)
            return self._vuelve(0)
        if n == "V_DRO_CONV":
            w(r(2), 100 + r(1))
            return self._vuelve(1)
        if n == "P_DLOPEN":
            return self._vuelve(1 if cstr(r(0)) == "libbackup.so" else 0)
        if n == "P_DLSYM":
            return self._vuelve({"Backup_read": self.BK_R, "Backup_write": self.BK_W}.get(cstr(r(1)), 0) | 1)
        if n == "P_MALLOC":
            return self._vuelve(self.BUF)
        if n == "Backup_read":
            i = r(0)
            d = self.bk.get(i, bytes([USUARIO_CS[i] & 0xFF]) + bytes(7) if i in USUARIO_CS else None)
            if d is None:
                return self._vuelve(-1)
            mu.mem_write(r(1), d)
            return self._vuelve(0)
        if n == "Backup_write":
            self.llamadas.append(("bk", r(1)))
            self.bk[r(1)] = bytes(mu.mem_read(r(2), FU.BK_TAM))
            return self._vuelve(0)
        raise AssertionError(n)

    def llama(self, fn, *args):
        from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP
        mu = self.mu
        for k, a in enumerate(args):
            mu.reg_write(UC_ARM_REG_R0 + k, a & 0xFFFFFFFF)
        mu.reg_write(UC_ARM_REG_SP, self.PILA + 0xF000)
        mu.reg_write(UC_ARM_REG_LR, self.PARA + 0x81)
        self.llamadas.clear()
        mu.emu_start((VA + self.sim[fn]) | 1, self.PARA + 0x80, count=2_000_000)
        return self.s32(self.r(0))

    def copia(self):
        return struct.unpack("<11i", self.bk[FU.BK_ID][FU.OFF_REC:FU.OFF_REC + FU.COPIA_TAM])


def _receta(nombre):
    w0, k, ab, gm, est, con, sat, nit, dro = FU.receta_gui(nombre)
    enum = [0, 1, 2, 11, 12, 13, 3, 4, 5, 6, 7, 8, 9, 10][est]
    return [("set", PP[0], 0), ("wb", w0, k, ab, gm), ("cs", enum, 0, con, sat, nit), ("set", 0x18, 100 + dro)]


def test_look_guarda_la_copia_pone_la_receta_y_off_la_devuelve(compilado):
    vm = VM(compilado, {TODAS: 0, PP[0]: USUARIO_PP})
    p4 = FU.orden().index("kodak_portra_400") + 1
    vm.llama("films_tramo_set", vm.MGR, TODAS, p4)
    c = vm.llamadas
    assert c[0] == ("bk", FU.BK_ID) and c[-1] == ("orig", TODAS, p4)          # la copia queda en el blob ANTES de que la GUI guarde la fila
    assert c[1:-1] == _receta("Kodak Portra 400")
    assert vm.copia() == (1, *USUARIO_WB, 2, 1, -2, 3, USUARIO_DRO, USUARIO_PP)
    v5 = FU.orden().index("kodak_vision3_500t") + 1
    vm.llama("films_tramo_set", vm.MGR, TODAS, v5)                            # de look a look: la copia no cambia
    assert vm.llamadas[:-1] == _receta("Kodak Vision3 500T (daylight)") and vm.copia()[0] == 1
    vm.llama("films_tramo_set", vm.MGR, TODAS, 0)
    assert vm.llamadas == [("set", PP[0], USUARIO_PP), ("wb", *USUARIO_WB), ("cs", 12 - 10, 0, 1, -2, 3), ("set", 0x18, 100 + USUARIO_DRO),
                           ("bk", FU.BK_ID), ("orig", TODAS, 0)]
    assert vm.copia()[0] == 0


def test_fila_de_marca_y_pid_ajeno(compilado):
    vm = VM(compilado, {TODAS: 0, PP[0]: 0})
    kodak = FU.ajustes()[0].pid
    vm.llama("films_tramo_set", vm.MGR, kodak, 6)                              # Kodak, opción 6 = Portra 400
    assert vm.llamadas[1:-1] == _receta("Kodak Portra 400")
    vm.llama("films_tramo_set", vm.MGR, 0x17, 3)                               # otro ajuste: solo el setValue original
    assert vm.llamadas == [("orig", 0x17, 3)]


def test_wbinh_salta_la_inhibicion_solo_al_objeto_marcado(compilado):
    vm = VM(compilado, {})
    obj = vm.BUF + 0x100
    vm.mu.mem_write(obj, struct.pack("<4I", 0x1234, 0, *MARCA_WB))
    assert vm.llama("films_tramo_wbinh", obj, vm.VBP, 1) == 0 and vm.llamadas == []
    vm.mu.mem_write(obj + 8, struct.pack("<2I", 0, 0))
    assert vm.llama("films_tramo_wbinh", obj, vm.VBP, 1) == 1 and vm.llamadas == [("inh", 1)]


def test_grises(compilado):
    p4, v5 = FU.orden().index("kodak_portra_400") + 1, FU.orden().index("kodak_vision3_500t") + 1
    gris = lambda vals, pid: VM(compilado, vals).llama("films_tramo_gris", VM.MGR, pid)
    sigue = 0x77                                                               # sin decisión: prólogo original de isGrayedOut
    for pid in (0x18, 0x19, 0x1A, PP[0], PP[1], PP[2]):
        assert gris({TODAS: p4, PP[0]: 0}, pid) == 1
        assert gris({TODAS: 0, PP[0]: 0}, pid) == sigue
    assert gris({TODAS: p4, PP[0]: 0}, 0x17) == 1                             # AWB: en gris con cualquier look
    assert gris({TODAS: v5, PP[0]: 0}, 0x17) == 1                              # kelvin fijo del look
    assert gris({TODAS: p4, PP[0]: 0}, 0x46) == sigue                          # EFCS y demás: la cadena de siempre
    for pid in (TODAS, FU.ajustes()[1].pid):
        assert gris({TODAS: 0, PP[0]: 3}, pid) == 1                            # con un PP puesto, Film en gris
        assert gris({TODAS: 0, PP[0]: 0}, pid) == sigue


def test_imagenes_uxc_ida_y_vuelta():
    import iconos_film as I
    import uxc_imagenes as U
    src = ROOT / "analysis/gui/g22/harness/stage/cam/usr/share/app/image_cmn_169.uxc"
    if not src.exists():
        pytest.skip("falta image_cmn_169.uxc")
    d = src.read_bytes()
    std = U.decodifica(d, 0xC7A6)                                              # «Std.» del Estilo creativo, 70×35
    assert std.shape == (35, 70, 4) and std[..., 3].max() == 255
    film, pp = I.carga()
    nuevo, ids = U.anade(d, film[:3] + pp[:2])
    for img, rid in zip(film[:3] + pp[:2], ids):
        assert np.abs(U.decodifica(nuevo, rid).astype(int) - img.astype(int)).max() <= 8   # RGBA4444
    assert all((U.decodifica(nuevo, rid) == U.decodifica(d, rid)).all() for rid in (0xC000, 0xC7A6, 0xDC97))
    assert U.anade(d, [])[0] == d                                              # CAM-394: sin imágenes, el original byte a byte
    _, _, primero, tab = U._indice(nuevo)
    ids_reg = [i for _, i in sorted((t, primero + i) for i, t in enumerate(tab) if t != U.VACIA)]
    assert ids_reg == sorted(ids_reg)                                          # registros en orden de id, como Sony
    R = U.registros(nuevo)
    assert sorted(R) == sorted(R, key=lambda k: R[k][1]) and all(q % 4 == 0 for _, q in R.values())   # datos en orden de id, alineados a 4
