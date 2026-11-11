"""G30: parche `patch_libobj_ppeco` — selector de perfil (caso 0x4a) y eco del estado de lectura tras elegir un valor (2.º bucle de `pvt_ActionSetPictureProfile`).
Se ejecuta el código real parcheado con unicorn; solo se simulan la memoria del objeto y la función `0x4a5836` (setter del estado)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
pytest.importorskip("unicorn")
from unicorn import UC_HOOK_CODE, Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_SP

import patch_libobj_ppeco as E

LIB = ROOT / "analysis/gui/g22/files-363/lib/libObj.so"
needs = pytest.mark.skipif(not LIB.is_file(), reason="libObj ausente")
THIS, FRAME = 0x20000000, 0x20100000


def _maquina(img: bytes) -> Uc:
    phoff, phnum = struct.unpack_from("<I", img, 28)[0], struct.unpack_from("<H", img, 44)[0]
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x1100000)
    mu.mem_write(0, img[:0xFCA5A4])
    for i in range(phnum):
        t, off, va, _, fs, _, _, _ = struct.unpack_from("<8I", img, phoff + 32 * i)
        if t == 1 and va == E.CAVE_VA:
            mu.mem_write(va, img[off:off + fs])
    mu.mem_map(THIS, 0x200000)
    return mu


def _correr(mu: Uc, pc: int, fin: int, hooks=None):
    log = []

    def h(uc, addr, size, _):
        if hooks and addr in hooks:
            hooks[addr](uc, log)
        if addr == fin:
            uc.emu_stop()

    mu.hook_add(UC_HOOK_CODE, h)
    mu.reg_write(UC_ARM_REG_SP, THIS + 0x1F0000)
    mu.emu_start(pc | 1, fin, count=200)
    return log


@needs
def test_perfil_actual_sale_de_this_0x274_si_es_valido():
    mu = _maquina(E.patch(LIB.read_bytes()))
    for perfil in (0, 3, 9):
        mu.mem_write(THIS + 0x274, struct.pack("<I", perfil))
        mu.reg_write(UC_ARM_REG_R5, THIS)
        mu.reg_write(UC_ARM_REG_R7, FRAME)
        _correr(mu, 0x4A784C, 0x4A785E)
        assert struct.unpack("<I", bytes(mu.mem_read(FRAME + 0x54, 4)))[0] == perfil


@needs
def test_perfil_actual_cae_a_la_nvram_si_this_0x274_no_es_un_perfil():
    mu = _maquina(E.patch(LIB.read_bytes()))
    mu.mem_write(THIS + 0x274, struct.pack("<I", 0x1070EE2))      # valor inicial (id), no un perfil
    mu.mem_write(THIS + 0xF8C, struct.pack("<I", 0x12345678))
    mu.reg_write(UC_ARM_REG_R5, THIS)
    mu.reg_write(UC_ARM_REG_R7, FRAME)
    _correr(mu, 0x4A784C, 0x4A7850)                               # vuelve al resto del bloque original con r0 = [this+0xf8c]
    assert mu.reg_read(UC_ARM_REG_R0) == 0x12345678


@needs
def test_eco_llama_al_setter_de_estado_con_el_objeto_del_parametro_y_el_valor_de_app():
    mu = _maquina(E.patch(LIB.read_bytes()))
    i, idx, valor = 7, 5, 9
    mu.mem_write(THIS + 4 * i + 0x560, struct.pack("<I", idx))                    # [this+0x560+4i] = índice
    obj = 0x20180000
    mu.mem_write(THIS + 4 * (idx + 0x4B6) + 4, struct.pack("<I", obj))            # objeto de estado
    mu.mem_write(FRAME + 4, struct.pack("<I", THIS + 4 * i))                      # [r7+4] = this+4i
    mu.mem_write(FRAME + 0x148, struct.pack("<I", valor))
    mu.reg_write(UC_ARM_REG_R4, THIS)
    mu.reg_write(UC_ARM_REG_R7, FRAME)
    mu.reg_write(UC_ARM_REG_R9, 5)
    llamadas, flush, marcas = [], [], []
    modelo = 0x20190000
    mu.mem_write(obj, struct.pack("<I", modelo))                                   # [wrapper] = objeto con las banderas de cambio

    def setter(uc, log):
        llamadas.append((uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1), uc.reg_read(UC_ARM_REG_R2)))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)            # return

    def flush_(uc, log):
        flush.append(uc.reg_read(UC_ARM_REG_R0))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)

    def marca(uc, log):
        marcas.append((uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)

    _correr(mu, 0x4C0BE2, 0x4C0BFC, {0x4A5836: setter, 0x13259C: flush_, 0x132754: marca})
    assert llamadas == [(obj, 1, valor)] and marcas == [(modelo, 0x49), (modelo, 0x4A)] and flush == [modelo]                    # tras actualizar el estado se vacía la lista de cambios del modelo (notifica a la vista)
    assert mu.reg_read(UC_ARM_REG_R9) == 6                                         # sb += 1 (cuenta de parámetros convertidos)


@needs
def test_el_elf_parcheado_tiene_el_segmento_nuevo_en_orden_y_sin_solapes():
    img = E.patch(LIB.read_bytes())
    phoff, phnum = struct.unpack_from("<I", img, 28)[0], struct.unpack_from("<H", img, 44)[0]
    loads = [struct.unpack_from("<8I", img, phoff + 32 * i) for i in range(phnum) if struct.unpack_from("<I", img, phoff + 32 * i)[0] == 1]
    assert [s[2] for s in loads] == sorted(s[2] for s in loads) and len(loads) == 3
    assert (loads[1][2] - loads[1][1]) % 0x1000 == 0 and loads[0][2] + loads[0][5] <= loads[1][2] and loads[1][2] + loads[1][5] <= loads[2][2] & ~0xFFF


@needs
def test_trazas_usan_direccion_relativa_al_pc_y_no_dependen_de_la_base_de_carga(monkeypatch):
    """Regresión 3.69: movw/movt absolutos dieron SIGSEGV en cámara; la cueva trazada debe contar en DATA aunque el .so cargue en otra base."""
    monkeypatch.setattr(E, "TRACE", True)
    img = E.patch(LIB.read_bytes())
    base = 0x3000000
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(base, 0x1100000)
    phoff, phnum = struct.unpack_from("<I", img, 28)[0], struct.unpack_from("<H", img, 44)[0]
    mu.mem_write(base, img[:0xFCA5A4])
    for i in range(phnum):
        t, off, va, _, fs, _, _, _ = struct.unpack_from("<8I", img, phoff + 32 * i)
        if t == 1 and va == E.CAVE_VA:
            mu.mem_write(base + va, img[off:off + fs])
    mu.mem_map(THIS, 0x200000)
    mu.mem_write(THIS + 0x274, struct.pack("<I", 3))
    mu.reg_write(UC_ARM_REG_R5, THIS)
    mu.reg_write(UC_ARM_REG_R7, FRAME)
    mu.reg_write(UC_ARM_REG_SP, THIS + 0x1F0000)
    mu.emu_start((base + 0x4A784C) | 1, base + 0x4A785E, count=200)
    assert struct.unpack("<I", bytes(mu.mem_read(base + E.DATA + 0x50, 4)))[0] == 1


@needs
def test_guardado_del_perfil_avisa_a_la_vista_despues_de_guardarlo():
    """El selector Off/PP1–PP9 se leía con el valor viejo: la marca de cambio debe ir DESPUÉS de `str [this+0x274]`."""
    mu = _maquina(E.patch(LIB.read_bytes()))
    mu.reg_write(UC_ARM_REG_R4, THIS)
    mu.reg_write(UC_ARM_REG_R8, 4)
    eventos = []

    def marca(uc, log):
        eventos.append(("marca", uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1), struct.unpack("<I", bytes(uc.mem_read(THIS + 0x274, 4)))[0]))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)

    def flush_(uc, log):
        eventos.append(("flush", uc.reg_read(UC_ARM_REG_R0)))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)

    _correr(mu, 0x4C0D6C, 0x4C0D70, {0x132754: marca, 0x13259C: flush_})
    assert struct.unpack("<I", bytes(mu.mem_read(THIS + 0x274, 4)))[0] == 4
    assert eventos == [("marca", THIS, 0x4A, 4), ("marca", THIS, 0x49, 4), ("flush", THIS)]
