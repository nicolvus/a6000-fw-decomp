"""G22-ACCION4 — el eslabón «código de entrada → acción de vista», leído de los ELF 3.21, sin QEMU.

Fija lo que el informe `docs/gui/g22-reproduccion-dispatch.md` §10 da por VERIFICADO:

1. **El traductor vive en `libScalarDaemon.so`, no en la vista.** `convertViewEventToAB(unsigned int code,
   unsigned int &accion)` (`libScalarDaemon+0x13a704`, símbolo exportado `_Z21convertViewEventToABTjRj`, 48 B)
   recorre una tabla de 19 pares de 8 B en `libScalarDaemon+0x19db0c` comparando contra **`code & ~0xf`**
   (`13a70c  bic r5,r0,#0xf`, halfwords `f020 050f`): por eso la pulsación `0x150100f2` y la suelta
   `0x150100f1` de la tecla Reproducción caen las dos en la fila `{0x150100f0 → 4}` y devuelven **acción 4**.
2. **La copia de esa tabla en `viewUnified2.so` (`.rodata 0x3a03d4`) es la misma tabla, byte a byte**, y su único
   lector (`viewUnified2+0x1906a8`) es **código muerto**: 0 ramas (16 y 32 bits) y 0 punteros en los ocho
   `viewUnified*.so` y en `libObj.so`. Es la corrección del §7.4: la tabla no está «sin usar por falta de llamante
   estático», está **duplicada**: la viva es la del daemon.
3. **El consumo en la capa de vista existe pero está desconectado**: `ScalarView::TriggerTableEvent`
   (`libObj+0x1170e8`) es el **único** llamante de `convertViewEventToAB` (en `0x1170f4`), y no tiene ni un
   llamante ni un puntero (candidata a `[View+0x20]`, la «tabla de disparo» de `View::getTriggerTable`
   `libObj+0x7f1a98`, que devuelve **una función**, no una tabla de datos). `ViewBase::transformByTriggerTable`
   (`libObj+0x1208ec`) y `…ForFuncEvent` (`+0x120935`) —las que compondrían el id de vista `0x1306cNNN` con
   `0x1208d2`: `(getView()<<12) + id + 0x13000000`— tampoco tienen llamantes en ninguna de las ocho bibliotecas
   de vista.
4. **El único puente de una vista al ejecutor de acciones** es `ScalarView::EventHandler(Event*, unsigned long)`
   (`libObj+0x116bd0`) → `ScalarDaemonIf::onSystemEventReceived` (`libObj+0x116c28`), y sólo lo llama
   `viewUnified8+0x15418` (una ranura virtual). Medido en el invitado con la tecla pulsada: 0 disparos (§8.5).
5. **La vía que sí usa la cámara para una tecla es la del daemon, por KEY_CODE**:
   `SCALARDAEMON::InputServantObserver::notifyKeyEventCallback` (`libScalarDaemon+0xda20c`) →
   `ScalarDaemon::onKeyEventReceived(KEY_CODE, KEY_STATE)` (`+0xd37b8`) →
   `EventDispatcher::dispatchKeyEvent` (`+0xd5654`, sólo mira `KEY_CODE <= 2` y lanza el proceso síncrono
   `0x102c`). No usa el código `0x1501xxxx`: ése es el camino del *evento*, y está cortado.
6. El interruptor del arnés `PLAYVIEW=1` (§10.6) engancha `InputService::createEvent` (`libObj+0x1106b8`) con un
   UDF repetible —emulando el `push {r3,r4,r5,r6,r7,lr}` en el manejador, como `OYD`— y, **sólo** para
   `0x150100f2`, llama a las dos funciones del firmware: el traductor de arriba y
   `viewManagerIf::openView("view/INDEX_PLAYBACK", 0)` (`libObj+0x1251fd`). No parchea ni una instrucción del
   traductor ni del abridor; lo único que pone el arnés es el llamante que al firmware 3.21 le falta.

Los binarios viven en `analysis/gui/g22/harness/stage/cam/usr/lib` (no versionados): si faltan, el módulo se
salta. No arranca ninguna VM; la medida en el invitado está en el informe y en
`reports/evidence/g22-accion4-20261127/`.
"""
from __future__ import annotations

import re
import struct
from pathlib import Path

import pytest

from test_g22_repro import Elf
from test_g22_dispatch import _plt

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib"
SHIM = ROOT / "scripts/gui/harness/shim/sonyshim.c"

if not (LIB / "libObj.so").exists() or not (LIB / "viewUnified2.so").exists() \
        or not (LIB / "libScalarDaemon.so").exists():
    pytest.skip("faltan los binarios del arnés (analysis/gui/g22/harness/stage): test estático",
                allow_module_level=True)

# ---------------------------------------------------------------- libScalarDaemon.so (VA del ELF 3.21)
SD_CONVERT = 0x13A704       # convertViewEventToAB(unsigned int, unsigned int&)
SD_TABLA = 0x19DB0C         # la tabla {codigo -> accion} VIVA (19 pares de 8 B)
SD_LITERAL_TABLA = 0x13A730  # literal PIC de esa tabla (0x000633f6)
SD_N_ENTRADAS = 19          # `cmp r3,#0x13` en 0x13a728
SD_GETINSTANCE = 0xD552C    # ScalarDaemon::getInstance (no usado por el test; referencia)
SD_NOTIFY_KEY = 0xDA20C     # InputServantObserver::notifyKeyEventCallback(void*, void*)
SD_ON_KEY = 0xD37B8         # ScalarDaemon::onKeyEventReceived(KEY_CODE, KEY_STATE)
SD_DISPATCH_KEY = 0xD5654   # EventDispatcher::dispatchKeyEvent(KEY_CODE, KEY_STATE)
SD_ON_SYSTEM_EVENT = 0xD4CF4  # ScalarDaemon::onSystemEventReceived(Event&, ViewBase*)

# ---------------------------------------------------------------- viewUnified2.so
VU_TABLA = 0x3A03D4         # la copia MUERTA de la misma tabla
VU_LECTOR = 0x1906A8        # su único lector (0 llamantes, 0 punteros)
VU_FILTRO = 0x181FB8        # el filtro de la vista que sintetiza 0x15070010/0x150701a0

# ---------------------------------------------------------------- libObj.so
CREATE_EVENT = 0x1106B8     # InputService::createEvent(unsigned long, unsigned char)
TRIGGER_EVENT = 0x1170E8    # ScalarView::TriggerTableEvent(unsigned int)
TRIGGER_CALL = 0x1170F4     # blx convertViewEventToAB dentro de la anterior
VIEW_EVENTHANDLER = 0x116BD0  # ScalarView::EventHandler(Event*, unsigned long)
DAEMON_CALL = 0x116C28      # blx ScalarDaemonIf::onSystemEventReceived dentro de la anterior
TRANSFORM_TT = 0x1208EC     # ViewBase::transformByTriggerTable(unsigned long)
TRANSFORM_TTF = 0x120935    # ViewBase::transformByTriggerTableForFuncEvent(unsigned long)
COMPONE_ID = 0x1208D2       # compone (getView()<<12)+id+0x13000000
GETTRIGGER = 0x7F1A98       # View::getTriggerTable() -> [View+0x20]
OPENVIEW_THUNK = 0x1251FD   # viewManagerIf::openView(char const*, int)

SIM_CONVERT = "_Z21convertViewEventToABTjRj"
SIM_ONSYSTEM = "_ZN14ScalarDaemonIf21onSystemEventReceivedER5EventP8ViewBase"
SIM_EVENTHANDLER = "_ZN10ScalarView12EventHandlerEP5Eventm"
SIM_OPENVIEW = "_ZN13viewManagerIf8openViewEPKci"
SIM_TT = "_ZN8ViewBase23transformByTriggerTableEm"
SIM_TTF = "_ZN8ViewBase35transformByTriggerTableForFuncEventEm"

CODIGO_PULSACION = 0x150100F2   # 0x150100f0 + 2 (pulsación), medido con EQTRACE
CODIGO_SUELTA = 0x150100F1      # 0x150100f0 + 1
MASCARA_ACCION = 0xF            # `bic r5,r0,#0xf`
ACCION_REPRODUCCION = 4

VISTAS = [f"viewUnified{n}.so" for n in range(2, 9)]


# ---------------------------------------------------------------- utilidades
@pytest.fixture(scope="module")
def libobj() -> Elf:
    return Elf(LIB / "libObj.so")


@pytest.fixture(scope="module")
def vdos() -> Elf:
    return Elf(LIB / "viewUnified2.so")


@pytest.fixture(scope="module")
def daemon() -> Elf:
    return Elf(LIB / "libScalarDaemon.so")


def _u16(lib: Elf, va: int) -> int:
    return struct.unpack_from("<H", lib.d, lib.v2o(va))[0]


def _u32(lib: Elf, va: int) -> int:
    return struct.unpack_from("<I", lib.d, lib.v2o(va))[0]


def _pares(lib: Elf, va: int, n: int) -> list[tuple[int, int]]:
    return [(_u32(lib, va + 8 * k), _u32(lib, va + 8 * k + 4)) for k in range(n)]


def _ramas32(lib: Elf) -> list[tuple[int, int]]:
    """(VA, destino) de TODAS las ramas Thumb-2 de 4 bytes (`bl`, `blx` inmediato y `b.w`) de `.text`.

    Barrido aritmético de los dos alineamientos (cada mitad de 2 B), sin desensamblador: así no se pierde ninguna
    rama real, que es lo que hace falta para afirmar «0 llamantes». `blx` (T2) alinea la base: Align(PC,4)+imm.
    """
    t = lib.secs[".text"]
    o = lib.v2o(t["addr"])
    datos = lib.d[o:o + t["size"]]
    salida = []
    for p in range(0, len(datos) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", datos, p)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) not in (0xD000, 0xC000, 0x9000):
            continue
        s = (h1 >> 10) & 1
        imm10 = h1 & 0x3FF
        j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
        i1, i2 = 1 - (j1 ^ s), 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        va = t["addr"] + p
        base = (va + 4) & ~3 if (h2 & 0xD000) == 0xC000 else va + 4
        salida.append((va, (base + imm) & 0xFFFFFFFF))
    return salida


def _ramas16(lib: Elf) -> list[tuple[int, int]]:
    """(VA, destino) de las ramas Thumb de 16 bits (`b` T2 y `b<cond>` T1) de `.text`.

    `_ramas` (importada) sólo cubre las de 32 bits; para afirmar «0 llamantes» hay que mirar las dos.
    """
    t = lib.secs[".text"]
    o = lib.v2o(t["addr"])
    datos = lib.d[o:o + t["size"]]
    salida = []
    for p in range(0, len(datos) - 3, 2):
        hw = struct.unpack_from("<H", datos, p)[0]
        a = t["addr"] + p
        if (hw & 0xF000) == 0xE000:
            imm = hw & 0x7FF
            if imm & 0x400:
                imm -= 0x800
            salida.append((a, a + 4 + (imm << 1)))
        elif (hw & 0xF000) == 0xD000 and ((hw >> 8) & 0xF) not in (0xE, 0xF):
            imm = hw & 0xFF
            if imm & 0x80:
                imm -= 0x100
            salida.append((a, a + 4 + (imm << 1)))
    return salida


_RAMAS_CACHE: dict[int, list[tuple[int, int]]] = {}


def _ramas(lib: Elf) -> list[tuple[int, int]]:
    """Ramas de 16 y 32 bits de `.text`, memorizadas por objeto."""
    if id(lib) not in _RAMAS_CACHE:
        _RAMAS_CACHE[id(lib)] = _ramas32(lib) + _ramas16(lib)
    return _RAMAS_CACHE[id(lib)]


def _sin_llamantes(lib: Elf, destino: int) -> list[int]:
    """Sitios de rama (16 o 32 bits) que apuntan a `destino` dentro de su propio `.text`."""
    return [va for va, d in _ramas(lib) if d == destino]


def _llamadas(lib: Elf, simbolo: str, plt: dict[int, str]) -> list[int]:
    """Sitios que llaman al stub .plt del símbolo importado `simbolo`."""
    stubs = {va for va, n in plt.items() if n == simbolo}
    return [va for va, d in _ramas(lib) if d in stubs]


SECCIONES_CON_PUNTEROS = (".text", ".rodata", ".data.rel.ro", ".got", ".data")


def _palabras_iguales(lib: Elf, valor: int) -> list[int]:
    """VAs de las palabras (4 B) de las secciones que pueden llevar punteros cuyo contenido es `valor`.

    Se excluyen `.dynsym`, `.dynstr`, `.gnu.*` y `.rel.*`: ahí el mismo número aparece como `st_value` del propio
    símbolo o como addend de relocación y daría un falso positivo (pasó en la primera versión de este test).
    """
    out = []
    for nombre in SECCIONES_CON_PUNTEROS:
        sec = lib.secs.get(nombre)
        if not sec:
            continue
        o = lib.v2o(sec["addr"])
        if o is None:
            continue
        datos = lib.d[o:o + sec["size"]]
        for p in range(0, len(datos) - 3, 4):
            if struct.unpack_from("<I", datos, p)[0] == valor:
                out.append(sec["addr"] + p)
    return out


# ---------------------------------------------------------------- 1. la tabla viva y su copia muerta
def test_la_tabla_de_codigo_a_accion_es_la_misma_en_el_daemon_y_en_la_vista(daemon: Elf, vdos: Elf) -> None:
    """`{código → acción}`: 19 pares de 8 B, idénticos en `libScalarDaemon+0x19db0c` y `viewUnified2+0x3a03d4`."""
    viva = _pares(daemon, SD_TABLA, SD_N_ENTRADAS)
    copia = _pares(vdos, VU_TABLA, SD_N_ENTRADAS)
    assert viva == copia, "la copia de la tabla en viewUnified2 ya no coincide con la del daemon"
    assert viva[0] == (0x150100F0, ACCION_REPRODUCCION), "la primera fila es {0x150100f0, 4}"
    codigos = [c for c, _ in viva]
    assert len(set(codigos)) == SD_N_ENTRADAS, "19 códigos distintos"
    # la 20.ª no es una fila: la tabla termina (basura del pozo) y el lector corta en 19
    assert viva[-1][0] == 0x15050050


def test_convertViewEventToAB_enmascara_con_0xf_y_recorre_las_19_filas(daemon: Elf) -> None:
    """El traductor vivo, con sus bytes: `bic r5,r0,#0xf`, el literal PIC y el `cmp r3,#0x13`."""
    assert _u16(daemon, SD_CONVERT) == 0xB5F0, "push {r4,r5,r6,r7,lr}"
    assert _u16(daemon, SD_CONVERT + 0x02) == 0x2300, "movs r3,#0 (índice)"
    assert _u16(daemon, SD_CONVERT + 0x06) == 0x4A09, "ldr r2,[pc,#0x24] (literal de la tabla)"
    assert _u16(daemon, SD_CONVERT + 0x08) == 0xF020 and _u16(daemon, SD_CONVERT + 0x0A) == 0x050F, \
        "bic r5,r0,#0xf  (la máscara que hace que +1 y +2 caigan en la misma fila)"
    assert _u16(daemon, SD_CONVERT + 0x0E) == 0x447A, "add r2,pc"
    assert (_u16(daemon, SD_CONVERT + 0x10), _u16(daemon, SD_CONVERT + 0x12)) == (0xF852, 0x6033), \
        "ldr.w r6,[r2,r3,lsl #3]  (fila i)"
    assert _u16(daemon, SD_CONVERT + 0x1C) == 0x6853, "ldr r3,[r2,#4]  (la acción)"
    assert _u16(daemon, SD_CONVERT + 0x1E) == 0x600B, "str r3,[r1]    (acción de salida)"
    assert _u16(daemon, SD_CONVERT + 0x24) == 0x2B13, "cmp r3,#0x13   (19 filas)"
    assert _u32(daemon, SD_LITERAL_TABLA) + (SD_CONVERT + 0x0E) + 4 == SD_TABLA, \
        "el literal PIC resuelve a la tabla 0x19db0c"
    assert _u16(daemon, SD_CONVERT + 0x0C) == 0x00DC, "lsls r4,r3,#3  (byte de la fila)"


def test_la_pulsacion_y_la_suelta_caen_en_la_accion_4() -> None:
    """`& ~0xf` sobre los dos códigos de la tecla: 0x150100f2 y 0x150100f1 → 0x150100f0 → acción 4."""
    assert CODIGO_PULSACION & ~MASCARA_ACCION == 0x150100F0
    assert CODIGO_SUELTA & ~MASCARA_ACCION == 0x150100F0
    # y la fila de esa clave es la de la acción 4 (comprobado en la tabla del daemon, test anterior)
    assert ACCION_REPRODUCCION == 4


def test_el_lector_de_la_copia_de_la_vista_es_codigo_muerto(vdos: Elf) -> None:
    """`viewUnified2+0x1906a8`: 0 ramas (16 y 32 bits) y 0 punteros en las ocho vistas y en libObj."""
    assert _sin_llamantes(vdos, VU_LECTOR) == [], "hay una rama nueva al lector de la copia muerta"
    for nombre in VISTAS + ["libObj.so"]:
        lib = Elf(LIB / nombre)
        assert _palabras_iguales(lib, VU_LECTOR) == [], f"{nombre}: hay una palabra con 0x1906a8"
        assert _palabras_iguales(lib, VU_LECTOR | 1) == [], f"{nombre}: hay una palabra con 0x1906a9"


# ---------------------------------------------------------------- 2. el consumo desconectado
def test_triggerTableEvent_es_el_unico_llamante_del_traductor_y_no_tiene_llamantes(libobj: Elf) -> None:
    """`libObj+0x1170f4` es el único `blx` a `convertViewEventToAB`; `0x1170e8` no tiene llamantes."""
    plt = _plt(libobj)
    sitios = _llamadas(libobj, SIM_CONVERT, plt)
    assert sitios == [TRIGGER_CALL], f"llamantes de convertViewEventToAB: {[hex(s) for s in sitios]}"
    assert _sin_llamantes(libobj, TRIGGER_EVENT) == [], "ScalarView::TriggerTableEvent tiene llamante"
    for va in _palabras_iguales(libobj, TRIGGER_EVENT | 1):
        pytest.fail(f"hay un puntero a ScalarView::TriggerTableEvent en {va:#x}")


def test_las_transformaciones_de_la_tabla_de_disparo_no_tienen_llamantes(libobj: Elf) -> None:
    """`transformByTriggerTable` y `…ForFuncEvent`: 0 ramas y ninguna biblioteca de vista las importa."""
    for fn in (TRANSFORM_TT, TRANSFORM_TTF):
        assert _sin_llamantes(libobj, fn) == [], f"hay una rama a {fn:#x}"
        for va in _palabras_iguales(libobj, fn | 1):
            pytest.fail(f"hay un puntero a {fn:#x} en {va:#x}")
    for nombre in VISTAS:
        plt = _plt(Elf(LIB / nombre))
        assert SIM_TT not in plt.values() and SIM_TTF not in plt.values(), \
            f"{nombre} importa (y podría llamar) las transformaciones"


def test_la_tabla_de_disparo_es_una_funcion_y_devuelve_la_ranura_0x20(libobj: Elf) -> None:
    """`View::getTriggerTable` (`0x7f1a98`) es `ldr r0,[r0,#0x20]; bx lr` y sus dos únicos lectores son las
    dos transformaciones muertas: la «tabla de disparo» es una FUNCIÓN, no una tabla de datos."""
    assert _u16(libobj, GETTRIGGER) == 0xB580, "push {r7,lr}"
    assert _u16(libobj, GETTRIGGER + 4) == 0x6A00, "ldr r0,[r0,#0x20]"
    assert _u16(libobj, GETTRIGGER + 6) == 0xBD80, "pop {r7,pc}"
    plt = _plt(libobj)
    assert _llamadas(libobj, "_ZN4View15getTriggerTableEv", plt) == [0x1208F6, 0x12093E]


def test_el_id_de_vista_se_compone_con_1208d2(libobj: Elf) -> None:
    """`0x1208d2` = si el id ya es de vista lo deja y si no compone `(getView()<<12) + id + 0x13000000`."""
    assert _u16(libobj, COMPONE_ID) == 0xF421 and _u16(libobj, COMPONE_ID + 2) == 0x6300 | 0x7E, "bic r3,r1,#0xfe0"
    assert _u16(libobj, COMPONE_ID + 0x0E) == 0x0300, "lsls r0,r0,#0xc  (vista << 12)"
    # `add.w r1,r1,#0x13000000` en +0x12
    w = (_u16(libobj, COMPONE_ID + 0x12) << 16) | _u16(libobj, COMPONE_ID + 0x14)
    assert w == 0xF101_5198, f"se esperaba add.w r1,r1,#0x13000000 (f101 5198) y hay {w:#x}"


def test_el_unico_puente_de_una_vista_al_ejecutor_es_eventhandler(libobj: Elf) -> None:
    """`ScalarView::EventHandler` → `ScalarDaemonIf::onSystemEventReceived`, y sólo lo llama viewUnified8."""
    plt = _plt(libobj)
    assert _llamadas(libobj, SIM_ONSYSTEM, plt) == [DAEMON_CALL], "el puente al daemon cambia de sitio"
    assert _sin_llamantes(libobj, VIEW_EVENTHANDLER) == [], "ScalarView::EventHandler tiene llamante en libObj"
    sitios = _llamadas(Elf(LIB / "viewUnified8.so"), SIM_EVENTHANDLER, _plt(Elf(LIB / "viewUnified8.so")))
    assert sitios == [0x15418], f"llamantes de ScalarView::EventHandler: {[hex(s) for s in sitios]}"
    for n in (2, 3, 4, 5, 6, 7):
        nombre = f"viewUnified{n}.so"
        assert SIM_EVENTHANDLER not in _plt(Elf(LIB / nombre)).values(), f"{nombre} también lo llama"


def test_la_via_de_tecla_del_daemon_no_usa_el_codigo_del_evento(daemon: Elf) -> None:
    """`dispatchKeyEvent` sólo mira `KEY_CODE <= 2` y lanza el proceso síncrono 0x102c; no mira 0x1501xxxx."""
    d = daemon
    base = SD_DISPATCH_KEY
    assert _u16(d, base) == 0xB590, "push {r4,r7,lr}"
    assert _u16(d, base + 0x10) == 0x2C02, "cmp r4,#2  (el único filtro sobre el KEY_CODE)"
    w = (_u16(d, base + 0x14) << 16) | _u16(d, base + 0x16)
    assert w == 0xF241_012C, f"movw r1,#0x102c (proceso síncrono) y hay {w:#x}"
    # onKeyEventReceived es un thunk de 14 B que reenvía al EventDispatcher
    assert _u16(d, SD_ON_KEY) == 0xB580 and _u16(d, SD_ON_KEY + 4) == 0x6800
    assert _u16(d, SD_ON_KEY + 0xA) == 0xF7FB, "b.w dispatchKeyEvent"


# ---------------------------------------------------------------- 3. el interruptor del arnés
def test_el_shim_tiene_el_interruptor_playview() -> None:
    """`PLAYVIEW=1`: UDF en createEvent con `push` emulado, sólo 0x150100f2, y las dos funciones del firmware."""
    s = SHIM.read_text(encoding="utf-8")
    assert "PLAYVIEW" in s
    # comprueba los bytes antes de escribir y emula la instrucción que sustituye
    assert "*p != 0xb5f8" in s, "no comprueba los bytes de libObj+0x1106b8 (f8 b5 = push)"
    assert "c->arm_sp - 24" in s and "w[5] = c->arm_lr" in s, "no emula el `push {r3,r4,r5,r6,r7,lr}`"
    assert "c->arm_r1 == 0x150100f2" in s, "no filtra por el código de la pulsación de Reproducción"
    # las dos funciones del firmware, por nombre exportado (nada de offsets cableados)
    assert SIM_CONVERT in s and SIM_OPENVIEW in s
    # se arma en el gancho de libObj y el trabajo lo hace un hilo (no el manejador de señal)
    assert re.search(r"strstr\(f, \"libObj\.so\"\)[^}]*playview_arm\(\)", s), "no se arma al cargar libObj"
    assert re.search(r"getenv\(\"PLAYVIEW\"\)[^\n]*pthread_create\(&th, 0, playviewer, 0\)", s), \
        "no arranca el hilo que hace las llamadas"
    # el manejador sólo emula y marca: la señal no llama a dlsym ni a openView
    bloque = s[s.index("static void playview_hit(mcontext_t *c) {"):s.index("static void playview_arm")]
    assert "dlsym" not in bloque and "openView" not in bloque
