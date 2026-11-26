"""G115 (LUT-T-1) — curva 1D tras la gamma en el ajuste «LUT»: cueva ejecutada con Unicorn sobre `av-cam` real, zona de la curva y paquete `.LUT` v2.

La cueva pone `bd5 = 1`, `be1 = 8`, `bd1 = bd3 = 0` y `c68[8]` (`0x440013ec`) = la curva de 33 nodos expandida, en los cuatro ganchos
de `FUN_43852f7c` (los mismos que la curva de Film, G98). Con Off, o con una LUT que no lleva curva, no escribe nada.
Zona de la curva: `lut_t.ZONA_T18` (tramo del hueco G18); ZONA_A/ZONA_B son la tabla T1 y las tablas BOKS (G107 §3) y NO se tocan. G116: la cueva y la máquina van a `ZONA_L18`, no a ZONA_A/ZONA_B.
"""
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/lut")]
import avcam_dinamico as D
import cube_a6000 as C
import film_patch as F
import lut_patch as L
import lut_pkg as PK
import lut_sd_userland as U
import lut_t as T
import tono_post as P

pytestmark = pytest.mark.skipif(not C.BIN.exists(), reason="falta av-cam.bin")


@pytest.fixture(scope="module")
def img():
    return C.BIN.read_bytes()


@pytest.fixture(scope="module")
def curva():
    """Registro de 68 B de la curva T de la película (calculado, como lo empaqueta el PC)."""
    ch = C.descompone(C.lut_pelicula, usa_M=False, usa_T=True, usa_L=True)
    return T.registro(T.nodos(P.curva_post(ch)))


@pytest.fixture(scope="module")
def blob(curva):
    """Blob como el que escribe el userland: ranuras 1…4 válidas (tabla cualquiera) y curva solo en la 4."""
    return U.blob_tablas({1: bytes(1064), 2: bytes(1064), 3: bytes(1064), 4: bytes(1064)}, curvas={4: curva})


@pytest.fixture(scope="module")
def parche(img):
    return L.apply_bytes(img)


@pytest.fixture(scope="module")
def fabrica(img):
    """Los dos consumidores con la `FUN_43852f7c` de fábrica (sin cueva)."""
    return T.emula_tono(img, 0, None, entrada=None)


# ---------- ganchos y Off ----------
def test_ganchos_de_curva_son_los_de_film_y_no_se_pisan():
    assert T.SITIOS_T == F.SITIOS_T                      # mismo mecanismo (gamma extendida de Sony), no se duplica
    for h in T.SITIOS_T:
        assert h & 1 == 0 and F.F_PREP == T.F_PREP          # `bl` de 32 bits: solo hace falta media palabra


def test_off_y_lut_sin_curva_no_cambian_la_curva(img, parche, blob, fabrica):
    """Off (0) y las ranuras sin curva en el blob (1, 3) dejan los dos consumidores como de fábrica, sin tocar indicadores ni `c68[8]`."""
    ent = L.entrada_t()
    for opcion in (0, 1, 3):
        r = T.emula_tono(parche, opcion, blob, entrada=ent)
        assert r["curva"] == fabrica["curva"] and r["rejilla"] == fabrica["rejilla"]
        assert r["ind"] == fabrica["ind"] and r["c68_8"] == fabrica["c68_8"] == T.IDENTIDAD
        assert r["rejilla_ok"] and r["paleta"] is None


def test_off_con_la_curva_puesta_restaura_la_identidad(parche, blob):
    """Ranura con curva → Off → ranura con curva → ranura sin curva: `c68[8]` vuelve a la identidad de fábrica al salir de la curva."""
    ent = L.entrada_t()
    pasos = T.emula_secuencia(parche, [4, 0, 4, 2], blob, entrada=ent)
    con = pasos[0]["c68_8"]
    assert con != T.IDENTIDAD and pasos[0]["ind"]["bd5"] == 1
    assert [p["c68_8"] for p in pasos] == [con, T.IDENTIDAD, con, T.IDENTIDAD]


# ---------- la curva que se aplica ----------
def test_la_curva_de_la_ranura_se_aplica_en_los_dos_consumidores(img, parche, blob, curva):
    ent = L.entrada_t()
    r = T.emula_tono(parche, 4, blob, entrada=ent)
    assert r["ind"] == {"bd1": 0, "bd3": 0, "bd5": 1, "be1": 8}
    assert r["c68_8"] != T.IDENTIDAD and r["paleta"] == T.expande(T.lee_registro(curva))
    g = P.gamma(img, 1)                                   # gamma 1 (bd9 = 1) sobre la rampa obj+0x66e (x = 4·i)
    x = np.arange(512) * 4
    assert list(P.emula(parche, 1, np.array(r["paleta"]), bd5=1, be1=8)) == r["curva"]     # la tabla entra por c68[8], exacta
    # ... y el firmware añade su propia normalización de salida («cola»): la rama bd5 no devuelve `tabla[gamma]` pelado.
    # Medido: 0 en las sombras y hasta +9 códigos de 1023 cerca del blanco (la tabla llega a 1013 y la salida, a 1023).
    simple = [r["paleta"][min(int(v), 1023)] for v in g[x]]
    d = [b - a for a, b in zip(simple, r["curva"])]
    assert min(d) >= 0 and max(d) <= 16 and all(v == 0 for v in d[:131])
    assert r["rejilla"] != T.emula_tono(parche, 1, blob, entrada=ent)["rejilla"]      # la rejilla de 96 nodos también la aplica


def test_la_curva_del_blob_es_la_de_tono_post(curva, blob):
    """El registro de 68 B de la ranura lleva la curva T de la cadena (33 nodos, desviación ≤ 3 códigos de 1023 frente a los 1024)."""
    ch = C.descompone(C.lut_pelicula, usa_M=False, usa_T=True, usa_L=True)
    exacta = [int(v) for v in P.curva_post(ch)]
    compacta = T.expande(T.lee_registro(curva))
    assert len(curva) == T.REC and T.lee_registro(curva) == T.nodos(exacta)
    assert max(abs(a - b) for a, b in zip(exacta, compacta)) <= 3
    assert compacta[1023] == exacta[1023]                            # el extremo se copia tal cual
    off = T.BK_T_OFF
    assert T.lee_registro(blob[off + 3 * T.REC:off + 4 * T.REC]) == T.lee_registro(curva)
    assert T.lee_registro(blob[off:off + T.REC]) is None             # ranura 1: sin curva


def test_malloc_cero_no_aplica_la_curva(img, parche, blob):
    from unicorn import UcError
    try:                                                             # sin memoria: la cueva cae a fábrica (no revienta)
        r = T.emula_tono(parche, 4, blob, entrada=L.entrada_t(), malloc_ok=False)
    except UcError:                                                  # `malloc` = 0 hace `beq` y no escribe: nunca se llega a tocar memoria
        pytest.fail("la cueva no debe tocar memoria sin `malloc`")
    assert r["ind"] == {"bd1": 1, "bd3": 0, "bd5": 0, "be1": 0} and r["c68_8"] == T.IDENTIDAD


# ---------- blob de la SD ----------
def test_curva_solo_de_la_ranura_que_la_lleva(parche, blob, curva):
    ent = L.entrada_t()
    con = T.emula_tono(parche, 4, blob, entrada=ent)
    sin = T.emula_tono(parche, 1, blob, entrada=ent)
    vacia = T.emula_tono(parche, 5, blob, entrada=ent)
    assert con["ind"]["bd5"] == 1 and con["paleta"] == T.expande(T.lee_registro(curva))
    assert sin["ind"]["bd5"] == 0 and sin["c68_8"] == T.IDENTIDAD    # ranura válida sin curva: no se aplica
    assert vacia["ind"]["bd5"] == 0 and vacia["c68_8"] == T.IDENTIDAD  # ranura inexistente: tampoco
    # sin tarjeta (blob a cero) NO hay curva por defecto: sin tabla tampoco hay curva (G116)
    assert T.emula_tono(parche, 2, None, entrada=ent)["ind"]["bd5"] == 0


# ---------- zona de la curva ----------
def test_zona_de_la_curva_no_pisa_a_los_demas_parches(img):
    lo, hi = T.ZONA_T18
    assert D.ZONA_G18[0] <= lo < hi <= D.ZONA_G18[1]
    otros = {"PP color": (0x43FB7400, 0x43FB7500), "PP tone": (0x43FB7500, 0x43FB7EC0),
             "bulb timer": (0x43FB7F00, 0x43FB7F80), "gancho JPEG": (0x43FB7F80, 0x43FB7FC4),
             "Film": (0x43FB7E80, 0x43FB811C), "ISO": (0x43FB8280, 0x43FB8360)}
    for nombre, (a, b) in otros.items():
        assert b <= lo or hi <= a, nombre
    assert not any(img[lo - D.BASE:hi - D.BASE])                     # a cero en el fichero (lo comprueba `apply_bytes`)
    esc, _ = T.escrituras(L.AJ_SD)
    assert all(lo <= a and a + len(x) <= hi for a, x in esc) and sum(len(x) for _, x in esc) <= hi - lo


def test_parche_no_escribe_en_zonas_vivas(img, parche):
    dif = [i + D.BASE for i in range(len(img)) if img[i] != parche[i]]
    assert dif
    assert not any(0x43D620D9 <= a < 0x43FA8F00 for a in dif)
    assert any(T.ZONA_T18[0] <= a < T.ZONA_T18[1] for a in dif)          # y la cueva/máquina, en `ZONA_L18` (G116)
    assert not any(any(z[0] <= a < z[1] for z in (D.ZONA_A, D.ZONA_B)) for a in dif)


# ---------- paquete `.LUT` v1/v2 ----------
def test_paquete_v2_ida_y_vuelta_y_flag_de_t():
    carga = bytes(np.random.default_rng(5).integers(0, 256, PK.CARGA, dtype=np.uint8))
    t = [int(v) for v in np.clip(np.round(1023 * (np.arange(1024) / 1023) ** 1.4), 0, 1023)]
    b1, b2 = PK.paquete(carga), PK.paquete(carga, t)
    assert len(b1) == PK.TAM1 == 1080 and len(b2) == PK.TAM2 == 3128
    assert PK.desempaqueta(b1) == (carga, None) and PK.desempaqueta(b2) == (carga, PK.np_u16(t))
    assert PK.curva(PK.paquete(carga, t, usa_t=False)) is None
    malos = [b2[:-1], b2 + b"\0", struct.pack("<IBBHII", PK.MAGIC, 3, 1, PK.CARGA, 0, 0) + bytes(3112),
             struct.pack("<IBBHII", PK.MAGIC, 2, 1, PK.CARGA, 0, 0) + bytes(3112)]
    for m in malos:
        assert PK.desempaqueta(m) is None


@pytest.fixture(scope="module")
def arm():
    return U.compila()


def llama_paquete(arm, datos: bytes) -> tuple[bytes | None, bytes | None]:
    """`lutsd_paquete(p, n, dst, dst_t)` del ARM compilado → (carga, registro de la curva) o (None, None)."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
        UC_ARM_REG_SP,
    )
    blob, sim = arm
    code, buf, dst, dst_t, pila, fin = 0x10000000, 0x20000000, 0x21000000, 0x22000000, 0x30000000, 0x31000000
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for a in (code, buf, dst, dst_t, pila, fin):
        mu.mem_map(a, 0x10000)
    mu.mem_write(code, blob)
    mu.mem_write(buf, datos)
    mu.mem_write(dst_t, b"\xaa" * PK.TAM_CURVA)
    for r, v in ((UC_ARM_REG_R0, buf), (UC_ARM_REG_R1, len(datos)), (UC_ARM_REG_R2, dst), (UC_ARM_REG_R3, dst_t),
                 (UC_ARM_REG_SP, pila + 0x8000), (UC_ARM_REG_LR, fin | 1)):
        mu.reg_write(r, v)
    mu.emu_start((code + sim["lutsd_paquete"]) | 1, fin, count=4_000_000)
    if mu.reg_read(UC_ARM_REG_R0) != 1:
        return None, None
    return bytes(mu.mem_read(dst, PK.CARGA)), bytes(mu.mem_read(dst_t, T.REC))


def test_arm_igual_a_la_referencia_v1_y_v2(arm):
    carga = bytes(np.random.default_rng(6).integers(0, 256, PK.CARGA, dtype=np.uint8))
    t = [int(v) for v in np.clip(np.round(1023 * (np.arange(1024) / 1023) ** 0.8), 0, 1023)]
    c1, r1 = llama_paquete(arm, PK.paquete(carga))
    assert c1 == carga and T.lee_registro(r1) is None                        # v1: sin curva, registro a cero
    c2, r2 = llama_paquete(arm, PK.paquete(carga, t))
    assert c2 == carga and T.lee_registro(r2) == T.nodos(t)                  # v2: 33 nodos, igual que la referencia del PC
    assert r2 == PK.registro(t)
    _, r0 = llama_paquete(arm, PK.paquete(carga, t, usa_t=False))
    assert T.lee_registro(r0) is None                                       # usa_T = 0: curva guardada pero no usada
    malo = bytearray(PK.paquete(carga, t))
    malo[1100] ^= 1
    assert llama_paquete(arm, bytes(malo)) == (None, None) and llama_paquete(arm, PK.paquete(carga, t)[:-1]) == (None, None)
