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


def _maquina(img: bytes, inicial: bool = False) -> Uc:
    phoff, phnum = struct.unpack_from("<I", img, 28)[0], struct.unpack_from("<H", img, 44)[0]
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x1100000)
    mu.mem_write(0, img[:0xFCA5A4])
    for i in range(phnum):
        t, off, va, _, fs, _, _, _ = struct.unpack_from("<8I", img, phoff + 32 * i)
        if t == 1 and va == E.CAVE_VA:
            mu.mem_write(va, img[off:off + fs])
    mu.mem_map(THIS, 0x200000)
    if not inicial:
        mu.mem_write(E.FLAG_VA, struct.pack("<I", 1))                    # ppinit ya hecho (se prueba aparte)
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
    mu.mem_write(base + E.FLAG_VA, struct.pack("<I", 1))
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


# ---- G35: PP10 (perfil 10) y valores de fábrica en Reset ----
import pp_factory as PF


@needs
def test_los_limites_de_perfil_aceptan_hasta_10():
    img = E.patch(LIB.read_bytes())
    for va, _, nuevo in E.BOUNDS:
        assert img[va:va + len(nuevo) // 2].hex() == nuevo
    mu = _maquina(img)
    mu.mem_write(THIS + 0x274, struct.pack("<I", 10))
    mu.reg_write(UC_ARM_REG_R5, THIS)
    mu.reg_write(UC_ARM_REG_R7, FRAME)
    _correr(mu, 0x4A784C, 0x4A785E)
    assert struct.unpack("<I", bytes(mu.mem_read(FRAME + 0x54, 4)))[0] == 10              # el selector devuelve PP10
    mu.mem_write(THIS + 0x274, struct.pack("<I", 11))
    mu.mem_write(THIS + 0xF8C, struct.pack("<I", 0x777))
    _correr(mu, 0x4A784C, 0x4A7850)
    assert mu.reg_read(UC_ARM_REG_R0) == 0x777                                            # 11 no es perfil: cae a la NVRAM


@needs
def test_reset_usa_el_perfil_elegido_en_el_menu_y_si_no_el_de_la_nvram():
    mu = _maquina(E.patch(LIB.read_bytes()))
    mu.reg_write(UC_ARM_REG_R4, THIS)
    mu.reg_write(UC_ARM_REG_R7, FRAME)
    for perfil in (0, 9, 10):
        mu.mem_write(THIS + 0x274, struct.pack("<I", perfil))
        mu.mem_write(FRAME + 0x14, struct.pack("<I", 3))
        _correr(mu, 0x4C0E62, E.VUELVE_RPERFIL)
        assert struct.unpack("<I", bytes(mu.mem_read(FRAME + 0x14, 4)))[0] == perfil
    mu.mem_write(THIS + 0x274, struct.pack("<I", 0x1070EE2))                              # sin perfil elegido: el de la NVRAM (leído en [r7+0x14])
    mu.mem_write(FRAME + 0x14, struct.pack("<I", 4))
    _correr(mu, 0x4C0E62, E.VUELVE_RPERFIL)
    assert struct.unpack("<I", bytes(mu.mem_read(FRAME + 0x14, 4)))[0] == 4


@needs
def test_reset_escribe_el_valor_de_fabrica_del_parametro_en_lugar_de_leer_la_nvram():
    mu = _maquina(E.patch(LIB.read_bytes()))
    for perfil, i, esperado in ((10, 7, PF.GAMMA["slog3"]), (6, 0, PF.COLOR["sgamut"]), (0, 7, PF.GAMMA["movie"]), (2, 7, PF.GAMMA["itu709"]), (4, 0, PF.COLOR["cinema"])):
        mu.reg_write(UC_ARM_REG_R4, THIS)
        mu.reg_write(UC_ARM_REG_R3, THIS + 4 * (perfil * 31 + i))
        mu.reg_write(UC_ARM_REG_R1, FRAME + 0x10)
        mu.reg_write(UC_ARM_REG_R0, 0x55)
        _correr(mu, 0x4C0EA2, E.VUELVE_RVALOR)
        assert struct.unpack("<i", bytes(mu.mem_read(FRAME + 0x10, 4)))[0] == esperado and mu.reg_read(UC_ARM_REG_R0) == 0


def test_la_tabla_de_fabrica_tiene_11_perfiles_con_31_parametros_y_pp10_es_slog3_sgamut3():
    assert len(PF.tabla()) == 11 * 31 * 4
    assert PF.perfil(10)[7] == PF.GAMMA["slog3"] and PF.perfil(10)[0] == PF.COLOR["sgamut3"] and PF.perfil(8)[0] == PF.COLOR["sgamut3cine"]
    assert all(len(PF.perfil(k)) == 31 for k in range(11))


@needs
def test_reset_completo_del_perfil_10_escribe_los_31_valores_de_fabrica_en_sus_elementos():
    """Bucle real de `pvt_ActionExePictureProfileReset` (0x4c0e62…0x4c0ee4) con la NVRAM simulada: PP10 usa los elementos de [this+0xab4…]."""
    mu = _maquina(E.patch(LIB.read_bytes()))
    for n in range(10 * 31 * 2 + 31):                                    # handles distintos por posición: actuales (0x5dc…) y de «defaults» (0xab4…, = perfil 10)
        mu.mem_write(THIS + 0x5DC + 4 * n, struct.pack("<I", 0x1000 + n))
    mu.mem_write(THIS + 0x274, struct.pack("<I", 10))
    escritos, leidos = {}, []

    def nvram_lee(uc, log):                                              # NO debe leerse ningún elemento de «valores por defecto»
        leidos.append(uc.reg_read(UC_ARM_REG_R0))
        uc.reg_write(UC_ARM_REG_R0, 0)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def nvram_escribe(uc, log):
        h, p = uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)
        escritos[h] = struct.unpack("<i", bytes(uc.mem_read(p, 4)))[0]
        uc.reg_write(UC_ARM_REG_R0, 0)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    mu.reg_write(UC_ARM_REG_R4, THIS)
    mu.reg_write(UC_ARM_REG_R7, FRAME)
    mu.reg_write(UC_ARM_REG_R5, 0)
    mu.mem_write(FRAME + 0x14, struct.pack("<I", 0))
    mu.reg_write(UC_ARM_REG_SP, THIS + 0x1F0000)

    def h(uc, addr, size, _):
        if addr == 0xDD5F4:
            nvram_lee(uc, None)
        elif addr == 0xDD874:
            nvram_escribe(uc, None)
        elif addr == 0x4C0EE4:
            uc.emu_stop()
    mu.hook_add(UC_HOOK_CODE, h)
    mu.reg_write(UC_ARM_REG_LR, 0)
    mu.emu_start(0x4C0E62 | 1, 0x4C0EE4, count=20000)
    esperado = {0x1000 + 10 * 31 + i: v for i, v in enumerate(PF.perfil(10))}
    assert escritos == esperado and not leidos


def _nvram(mu, marca=0, falla_lee=False, falla_escribe_marca=False):
    """NVRAM simulada de los elementos: lecturas (0xdd5f4) y escrituras (0xdd874); devuelve (escrituras en orden, nº de lecturas)."""
    for n in range(400):
        mu.mem_write(THIS + 0x5DC + 4 * n, struct.pack("<I", 0x1000 + n))
    marca_id = 0x1000 + 341
    escrituras, lecturas = [], []

    def h(uc, addr, size, _):
        if addr == 0xDD5F4:
            lecturas.append(uc.reg_read(UC_ARM_REG_R0))
            uc.mem_write(uc.reg_read(UC_ARM_REG_R1), struct.pack("<I", marca))
            uc.reg_write(UC_ARM_REG_R0, 1 if falla_lee else 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif addr == 0xDD874:
            hid, v = uc.reg_read(UC_ARM_REG_R0), struct.unpack("<i", bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1), 4)))[0]
            escrituras.append((hid, v))
            uc.reg_write(UC_ARM_REG_R0, 1 if (falla_escribe_marca and hid == marca_id) else 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
    from unicorn import UC_HOOK_CODE
    mu.hook_add(UC_HOOK_CODE, h)
    return escrituras, lecturas


def _selector(mu):
    mu.mem_write(THIS + 0x274, struct.pack("<I", 3))
    mu.reg_write(UC_ARM_REG_R5, THIS)
    mu.reg_write(UC_ARM_REG_R7, FRAME)
    mu.reg_write(UC_ARM_REG_SP, THIS + 0x1F0000)
    mu.reg_write(UC_ARM_REG_LR, 0x1234)
    mu.emu_start(0x4A784C | 1, 0x4A785E, count=100000)


def _flag(mu):
    return struct.unpack("<I", bytes(mu.mem_read(E.FLAG_VA, 4)))[0]


@needs
def test_primer_arranque_escribe_los_valores_de_fabrica_en_los_11_perfiles_y_la_marca_una_sola_vez():
    mu = _maquina(E.patch(LIB.read_bytes()), inicial=True)
    escrituras, lecturas = _nvram(mu)
    _selector(mu)
    marca_id = 0x1000 + 341
    assert escrituras[0] == (marca_id, E.MARCA_FABRICA) and _flag(mu) == 1
    tabla = struct.unpack("<341i", PF.tabla())
    assert escrituras[1:] == [(0x1000 + k, tabla[k]) for k in range(341)]
    assert escrituras[1 + 10 * 31 + 7][1] == PF.GAMMA["slog3"]                            # PP10: gamma S-Log3
    n = len(escrituras)
    _selector(mu)                                                                          # segunda llamada: la bandera evita todo trabajo
    assert len(escrituras) == n and len(lecturas) == 1
    assert struct.unpack("<I", bytes(mu.mem_read(FRAME + 0x54, 4)))[0] == 3                # y el selector sigue devolviendo el perfil


@needs
def test_con_la_marca_ya_puesta_no_se_toca_la_nvram():
    mu = _maquina(E.patch(LIB.read_bytes()), inicial=True)
    escrituras, _ = _nvram(mu, marca=E.MARCA_FABRICA)
    _selector(mu)
    assert escrituras == [] and _flag(mu) == 1


@needs
def test_si_la_nvram_falla_no_se_aplica_nada_y_se_reintenta_despues():
    for kw in (dict(falla_lee=True), dict(falla_escribe_marca=True)):
        mu = _maquina(E.patch(LIB.read_bytes()), inicial=True)
        escrituras, _ = _nvram(mu, **kw)
        _selector(mu)
        assert _flag(mu) == 0 and all(h == 0x1000 + 341 for h, _ in escrituras)            # a lo sumo el intento de escribir la marca
