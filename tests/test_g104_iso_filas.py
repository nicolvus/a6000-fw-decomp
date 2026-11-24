"""G104 §8.6 — filas ISO 64000…409600: cuevas de `viewUnified4` (fila ↔ enum) y `viewUnified2` (`getIso`/`setIso`/`isInhOn`), ejecutadas con Unicorn
sobre las bibliotecas 3.21 parcheadas; tabla de menú, imágenes y textos por bytes."""
import struct
import sys
from pathlib import Path

import pytest
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R6,
    UC_ARM_REG_R7,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import add_menu_entry as A
import iso_ui_patch as P
import iso_ui_recursos as U

USR = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked"
A7S = ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked"
pytestmark = pytest.mark.skipif(not (USR / "lib/viewUnified4.so").is_file() or not (A7S / "share/app/image_cmn_43.uxc").is_file(),
                                reason="firmware 3.21 / A7S 3.20 no disponibles")
NUEVAS = range(len(P.VALORES))
FIN, PILA, MEM = 0x7FF00000, 0x7FE00000, 0x7FD00000
TEXTOS = {v: 0xF000 + k for k, v in enumerate(P.VALORES)}
ICONOS = {v: (0xD000 + 2 * k, 0xD001 + 2 * k) for k, v in enumerate(P.VALORES)}


@pytest.fixture(scope="module")
def vu4():
    return P.patch_filas((USR / "lib/viewUnified4.so").read_bytes(), TEXTOS, ICONOS)


@pytest.fixture(scope="module")
def vu2():
    return P.patch_vu2((USR / "lib/viewUnified2.so").read_bytes())


def _uc(d: bytes) -> Uc:
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for t, off, va, _, fs, ms, _, _ in A._segments(d):
        if t == 1:
            ini, fin = va & ~0xFFF, (va + ms + 0xFFF) & ~0xFFF
            mu.mem_map(ini, fin - ini)
            mu.mem_write(va, d[off:off + fs])
    for b in (FIN, PILA, MEM):
        mu.mem_map(b, 0x10000)
    mu.reg_write(UC_ARM_REG_SP, PILA + 0x8000)
    mu.reg_write(UC_ARM_REG_LR, FIN | 1)
    return mu


def _llama(d: bytes, fn: int, *args) -> int:
    mu = _uc(d)
    for r, v in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2), args):
        mu.reg_write(r, v)
    mu.emu_start(fn | 1, FIN, count=500)
    return mu.reg_read(UC_ARM_REG_R0)


def test_vu4_fila_enum(vu4):
    """`0xef90c` fila → enum (r0 = objeto con `+0x154`) y `0xef894` enum → fila (centinela 0x3f)."""
    fe = lambda f: _llama(vu4, 0xEF90C, MEM, f)
    ef = lambda e: _llama(vu4, 0xEF894, MEM, e)
    assert [fe(P.FILA0 + k) for k in NUEVAS] == [P.ENUM0 + k for k in NUEVAS]
    assert (fe(0x21), fe(0x1E), fe(0x24), fe(0x3F), fe(P.FILA0 + len(P.VALORES))) == (0x4E, 0x4B, 0x4F, 0x4F, 0x4F)
    assert [ef(P.ENUM0 + k) for k in NUEVAS] == [P.FILA0 + k for k in NUEVAS]
    assert (ef(0x4E), ef(0x30), ef(0x4F), ef(0), ef(P.ENUM0 + len(P.VALORES))) == (0x21, 2, 0x3F, 0x3F, 0x3F)


def test_vu4_tabla(vu4):
    segs = A._segments(vu4)
    tabla, n = struct.unpack_from("<2I", vu4, A._off(segs, P.MENU_CAB))
    assert n == P.MENU_N + len(P.VALORES)
    filas = [struct.unpack_from("<10I", vu4, A._off(segs, tabla + 0x28 * i)) for i in range(n)]
    orig = (USR / "lib/viewUnified4.so").read_bytes()
    assert filas[:P.MENU_N] == [struct.unpack_from("<10I", orig, A._off(A._segments(orig), P.MENU_TABLA + 0x28 * i)) for i in range(P.MENU_N)]
    for k, v in enumerate(P.VALORES):
        f = filas[P.MENU_N + k]
        assert (f[2], f[3] & 0xFFFF, f[4] & 0xFFFF, f[6] & 0xFFFF) == (P.FILA0 + k, TEXTOS[v], *ICONOS[v])
    assert vu4[A._off(segs, P.VU4_VALIDAS):A._off(segs, P.VU4_VALIDAS) + 2] == bytes((P.FILA0 + len(P.VALORES), 0x26))   # movs r6,#0x49
    with pytest.raises(ValueError):
        P.patch_filas(vu4, TEXTOS, ICONOS)


def test_vu2_isinhon(vu2):
    """`0x1c1a20(this, enum, &pid)`: los nuevos dan el pid 0x2f (sin atenuar); los demás, como el original."""
    def pid(e):
        mu = _uc(vu2)
        mu.reg_write(UC_ARM_REG_R1, e)
        mu.reg_write(UC_ARM_REG_R2, MEM)
        mu.mem_write(MEM, b"\xff" * 4)
        mu.emu_start(0x1C1A20 | 1, FIN, count=200)
        return mu.reg_read(UC_ARM_REG_R0), struct.unpack("<I", mu.mem_read(MEM, 4))[0]
    assert all(pid(P.ENUM0 + k) == (1, P.PID_NUEVO) for k in NUEVAS)
    assert pid(0x4E) == (1, 0x20) and pid(P.ENUM0 + len(P.VALORES))[0] == 0 and pid(0x11)[0] == 0


def test_vu2_getiso(vu2):
    """Desde el `bl` de `0x1c14d8`: código → enum en `[r6]`; un código desconocido sigue al error original."""
    def enum(c):
        mu = _uc(vu2)
        mu.reg_write(UC_ARM_REG_R0, c)
        mu.reg_write(UC_ARM_REG_R6, MEM)
        fin = []
        mu.hook_add(UC_HOOK_CODE, lambda m, a, s, u: (fin.append(a), m.emu_stop()) if a in (0x1C14E2, P.GET_ERR) else None)
        mu.emu_start(P.GET_CMP | 1, FIN, count=200)
        return struct.unpack("<I", mu.mem_read(MEM, 4))[0] if fin == [0x1C14E2] else None
    assert [enum(c) for c in P.CODIGOS] == [P.ENUM0 + k for k in NUEVAS]
    assert enum(0x26) == 0x4E and enum(0x2A) is None and enum(0x51) is None


def test_vu2_setiso(vu2):
    """Desde `0x1c1dd6` con el enum en `[r7+4]`: el código que llega al constructor del valor (`0xee040`) antes de la cola común."""
    def codigo(e):
        mu = _uc(vu2)
        mu.reg_write(UC_ARM_REG_R7, MEM)
        mu.mem_write(MEM + 4, struct.pack("<I", e))
        visto = []

        def hook(m, a, s, u):
            if a == P.SET_NEW:                              # operator new (PLT, ARM): objeto falso
                m.reg_write(UC_ARM_REG_R0, MEM + 0x100)
                m.reg_write(UC_ARM_REG_PC, m.reg_read(UC_ARM_REG_LR))
            elif a == P.SET_CTOR:
                visto.append(m.reg_read(UC_ARM_REG_R1))
                m.reg_write(UC_ARM_REG_PC, m.reg_read(UC_ARM_REG_LR))
            elif a in (P.SET_COLA, P.SET_ERR):
                visto.append(a)
                m.emu_stop()
        mu.hook_add(UC_HOOK_CODE, hook)
        mu.emu_start(0x1C1DD6 | 1, FIN, count=300)
        return visto
    assert [codigo(P.ENUM0 + k) for k in NUEVAS] == [[c, P.SET_COLA] for c in P.CODIGOS]
    assert codigo(0x4E) == [0x26, P.SET_COLA] and codigo(0x30) == [8, P.SET_COLA]
    assert codigo(P.ENUM0 + len(P.VALORES)) == [P.SET_ERR] and codigo(0x20) == [P.SET_ERR]


def test_imagenes_y_textos(tmp_path):
    a6 = (USR / "share/app/image_cmn_169.uxc").read_bytes()
    a7 = (A7S / "share/app/image_cmn_43.uxc").read_bytes()
    ids = [i for p in U.ICONOS_A7S.values() for i in p]
    nuevo, mapa = U.imagenes(a6, a7, ids, U.refs_recurso([USR], 0x0205))
    for viejo, n in mapa.items():                         # mismos metadatos y datos que en la A7S
        assert U._registro(nuevo, n)[0][2:6] == U._registro(a7, viejo)[0][2:6] and U._registro(nuevo, n)[1] == U._registro(a7, viejo)[1]
    n6, _, tab = U._indice(a6)
    ultima = next(0xC000 + k for k in range(n6 - 1, 0, -1) if tab[k] != U.VACIA)
    for i in (0xC000, 0xC746, 0xC39A, ultima):            # los existentes: mismos metadatos y datos (el desplazamiento se mueve con los datos)
        (r0, b0), (r1, b1) = U._registro(a6, i), U._registro(nuevo, i)
        assert r0[:6] == r1[:6] and b0 == b1
    ids_t = U.ids_textos([USR])
    assert {v: ids_t[v] for v in U.TEXTOS_A6000} == U.TEXTOS_A6000 and len(set(ids_t.values())) == len(P.VALORES)
    hechos = U.escribir_textos(USR / "share/app", tmp_path, ids_t)
    import uxc_strings
    rec = uxc_strings.parse((tmp_path / "string_english.uxc").read_bytes())[2]
    assert "string_english.uxc" in hechos and rec[ids_t[409600]] == "ISO 409600" and rec[ids_t[64000]] == "ISO 64000"


def test_libobj_codigos():
    """`libObj`: código → VALUEID (`0x4e0ea8`) e inverso (`0x4e10b8`) con 0x4b…0x50 como la A7S; los demás, como el original."""
    import iso_libobj_patch as L
    orig = (USR / "lib/libObj.so").read_bytes()
    nuevo = L.patch(orig)

    def valor(d, c):
        mu = _uc(d)
        mu.reg_write(UC_ARM_REG_R1, c)
        mu.reg_write(UC_ARM_REG_R2, MEM)
        mu.mem_write(MEM, b"\xff" * 4)
        mu.emu_start(L.A_VALUEID | 1, FIN, count=300)
        return mu.reg_read(UC_ARM_REG_R0), struct.unpack("<I", mu.mem_read(MEM, 4))[0]
    codigo = lambda d, v: _llama(d, L.A_CODIGO, 0, v)
    assert [valor(nuevo, c) for c in L.CODIGOS] == [(1, v) for v in L.VALUEIDS]
    assert [codigo(nuevo, v) for v in L.VALUEIDS] == list(L.CODIGOS)
    for c in (0, 8, 0x26, 0x27, 0x29, 0x2A, 0x3A, 0x4A, 0x51):
        assert valor(nuevo, c) == valor(orig, c), hex(c)
    for v in (0x21, 0x48, 0x276, 0x277, 0x1E5, 0x501, 0x511):
        assert codigo(nuevo, v) == codigo(orig, v), hex(v)
    with pytest.raises(ValueError):
        L.patch(nuevo)


def test_vu2_indicador(vu2):
    """Indicador ISO de la pantalla de disparo: los códigos nuevos van a la rama del número (iconos normales) y el número sale de la tabla."""
    from unicorn.arm_const import UC_ARM_REG_R3, UC_ARM_REG_R4

    def rama(c):
        mu = _uc(vu2)
        mu.reg_write(UC_ARM_REG_R3, c)
        mu.reg_write(UC_ARM_REG_R4, 1)
        fin = []
        mu.hook_add(UC_HOOK_CODE, lambda m, a, s, u: (fin.append(a), m.emu_stop()) if a in (P.IND_SIGUE, P.IND_NUMERO, P.IND_RANGO + 4) else None)
        mu.emu_start(P.IND_RANGO | 1, FIN, count=100)
        return fin[0], mu.reg_read(UC_ARM_REG_R4)

    def numero(c):
        mu = _uc(vu2)
        mu.reg_write(UC_ARM_REG_R3, c)
        mu.emu_start(P.IND_TABLA | 1, P.IND_TABLA + 8, count=100)
        return mu.reg_read(UC_ARM_REG_R2)
    assert all(rama(c) == (P.IND_NUMERO, 0) for c in P.CODIGOS)
    assert rama(0x26)[0] == P.IND_RANGO + 4 and rama(0x3A)[0] == P.IND_SIGUE and rama(0x51)[0] == P.IND_SIGUE
    assert [numero(c) for c in P.CODIGOS] == list(P.VALORES)
    assert (numero(0x26), numero(0x0B)) == (51200, 100)


def test_cfw_hasta_204800():
    """El CFW lleva `N_CFW` filas (hasta 204800): las siguientes no existen ni se convierten."""
    n = P.N_CFW
    v4 = P.patch_filas((USR / "lib/viewUnified4.so").read_bytes(), TEXTOS, ICONOS, n)
    v2 = P.patch_vu2((USR / "lib/viewUnified2.so").read_bytes(), n)
    assert P.VALORES[n - 1] == 204800
    assert _llama(v4, 0xEF90C, MEM, P.FILA0 + n - 1) == P.ENUM0 + n - 1 and _llama(v4, 0xEF90C, MEM, P.FILA0 + n) == 0x4F
    assert _llama(v4, 0xEF894, MEM, P.ENUM0 + n) == 0x3F
    segs = A._segments(v4)
    assert struct.unpack_from("<2I", v4, A._off(segs, P.MENU_CAB))[1] == P.MENU_N + n
    mu = _uc(v2)
    mu.reg_write(UC_ARM_REG_R1, P.ENUM0 + n)
    mu.reg_write(UC_ARM_REG_R2, MEM)
    mu.emu_start(0x1C1A20 | 1, FIN, count=200)
    assert mu.reg_read(UC_ARM_REG_R0) == 0
