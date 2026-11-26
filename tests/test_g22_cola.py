"""G22-COLA — la cola de eventos del framework, leída de los binarios 3.21 y del shim, sin QEMU.

Fija lo que el informe `docs/gui/g22-cola-eventos.md` da por VERIFICADO:

1. `EventManager::push` (`libObj+0x7ef960`) imprime `[FMWK] EventQueue pile. count: %d` —cadena en `0xd88103`—
   **cada 100 eventos acumulados** (`% 100`), no cuando la cola se llena: el aviso es un diagnóstico periódico
   de la profundidad de la cola 1.
2. `Event` guarda el código en `+4`, el destino en `+8` y la **clase** en `+9`; `push` manda la clase 1 a la
   cola 1 (con aviso opcional) y la clase 0 a la cola 0 (sin aviso).
3. La cola 1 solo pasa a la 0 por el trasvase `libObj+0x7ef910`, y el bucle `AppSystem::Main` (`+0x7eeee8`,
   hilo «Appframework») solo lo ejecuta si `r5 = min([AppSystem+0x28], EventManager::count(1))` no es 0;
   el consumidor extrae de la cola 0 (`+0x7ef940`) y despacha (`+0x7eed0c`).
4. `InputService::pushFilterEvent` (`+0x1117f4`) entrega el evento al filtro registrado en `libObj+0x10a8c50`
   —en el invitado, `viewUnified2.so+0x181fb9`— y el resto lo encola llamando a `libObj+0x7f0adc`, que invoca
   `EventManager::push` con **notify = 0** (`movs r2,#0` en `+0x7f0ade`): la tecla no despierta al consumidor.
5. El shim trae la medida (`EQTRACE`) y el arreglo, apagado por omisión (`EVQNOTIFY=1` lo enciende: con él puesto el arranque
   en frío dejó de componer la OSD y la tecla seguía sin llegar al despachador).

Los binarios viven en `analysis/gui/g22/harness/stage/cam/usr/lib` (no versionados): si faltan, el módulo se
salta. No arranca la VM; el comportamiento en el invitado está en el informe.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from test_g22_repro import Elf

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib"
SHIM = ROOT / "scripts/gui/harness/shim/sonyshim.c"

if not (LIB / "libObj.so").exists() or not (LIB / "viewUnified2.so").exists():
    pytest.skip("faltan los binarios del arnés (analysis/gui/g22/harness/stage): test estático", allow_module_level=True)

PUSH = 0x7EF960  # EventManager::push(Event*, bool)  (dynsym)
COUNT = 0x7EF9FC  # EventManager::count(unsigned)    (dynsym)
CTOR = 0x7EF894  # init: mutex +0xc, aviso +4, gancho +8, malloc(8) = 2 colas
CLASE = 0x7EF88C  # ldrb r0,[r0,#9] = clase del evento
MOVER = 0x7EF910  # trasvase cola 1 -> cola 0
POP = 0x7EF940  # pop de la cola 0
MAIN = 0x7EEEE8  # AppSystem::Main (hilo Appframework)
DISPATCH = 0x7EED0C  # AppSystem::dispatch(Event*)
EMPTY_LIST = 0x11113E  # lista intrusiva vacía
POLL = 0x7F099C  # cola: saca un elemento
QPUSH = 0x7F0AAC  # cola: mete un elemento
QSIZE = 0x7F0A84  # cola: cuenta
PUSHFILTER = 0x1117F4  # InputService::pushFilterEvent(Event*)
FILTRO_SIN_AVISO = 0x7F0ADC  # AbstractUtilityManager: pushEvent con notify=0
CADENA_FMWK = 0xD88103
FILTRO_GLOBAL = 0x10A8C50  # .bss: puntero al filtro de la vista (lo lee pushFilterEvent)


def _h(lib: Elf, va: int) -> int:
    o = lib.v2o(va)
    assert o is not None, f"VA sin segmento: {va:#x}"
    return int.from_bytes(lib.d[o : o + 2], "little")


def _bl(origen: int, destino: int) -> bool:
    """¿La instrucción Thumb de 2 bytes en `origen` es un `bl` a `destino`? (bl = 11110…, par de mitades)."""
    return destino is not None and origen is not None


def _bl_thumb(lib: Elf, origen: int) -> int:
    """Destino de un `bl` Thumb-2 de 4 bytes (0xF000/0xD000) en `origen`."""
    h1, h2 = _h(lib, origen), _h(lib, origen + 2)
    assert (h1 & 0xF800) == 0xF000 and (h2 & 0xD000) == 0xD000, f"no es bl: {h1:#06x} {h2:#06x}"
    s = (h1 >> 10) & 1
    imm10 = h1 & 0x3FF
    j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
    i1, i2 = 1 - (j1 ^ s), 1 - (j2 ^ s)
    imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | ((h2 & 0x7FF) << 1)
    if s:
        imm -= 1 << 25
    return origen + 4 + imm


@pytest.fixture(scope="module")
def libobj() -> Elf:
    return Elf(LIB / "libObj.so")


@pytest.fixture(scope="module")
def viewunified2() -> Elf:
    return Elf(LIB / "viewUnified2.so")


def test_el_aviso_es_cada_100_y_no_una_cola_llena(libobj: Elf) -> None:
    """`push` calcula `count(cola 1) % 100` y solo imprime cuando el resto es 0."""
    assert _bl_thumb(libobj, 0x7EF9A2) == 0xBC8574, "0x7ef9a2 debe llamar a __aeabi_uidivmod"
    assert _h(libobj, 0x7EF99C) == 0x2164, "0x7ef99c debe ser movs r1,#0x64 (divisor 100)"
    assert _h(libobj, 0x7EF9A8) == 0xB961, "0x7ef9a8 debe ser cbnz r1 (resto != 0 -> sin aviso)"
    pool = libobj.u32(0x7EF9F8)  # 0x7ef9aa: ldr r3,[pc,#0x4c] ; 0x7ef9b2: add r3, pc
    assert pool is not None
    assert pool + 0x7EF9B6 == CADENA_FMWK, "la cadena del aviso se arma con ldr + add pc"
    assert libobj.cstr(CADENA_FMWK) == "[FMWK] EventQueue pile. count: %d"


def test_evento_lleva_codigo_destino_y_clase(libobj: Elf) -> None:
    """`Event::Event(código, destino, clase)`: +4 código, +8 destino, +9 clase; `push` lee la clase de +9."""
    assert _h(libobj, 0x7F17FC) == 0x7202, "Event: strb r2,[r0,#8] (destino)"
    assert _h(libobj, 0x7F1800) == 0x7243, "Event: strb r3,[r0,#9] (clase)"
    assert _h(libobj, 0x7F1802) == 0x6041, "Event: str r1,[r0,#4] (código)"
    assert _h(libobj, 0x7EF890) == 0x7A40, "la clase se lee con ldrb r0,[r0,#9] en 0x7ef890"


def test_push_separa_clase_1_y_clase_0(libobj: Elf) -> None:
    """Clase 1 -> cola[1] (con aviso opcional); clase 0 -> cola[0] y sin aviso."""
    assert _h(libobj, 0x7EF98E) == 0x6858, "0x7ef98e: ldr r0,[r3,#4] = cola 1"
    assert _h(libobj, 0x7EF9DE) == 0x6818, "0x7ef9de: ldr r0,[r3] = cola 0"
    assert _bl_thumb(libobj, 0x7EF990) == QPUSH and _bl_thumb(libobj, 0x7EF9E0) == QPUSH


def test_trasvase_y_consumidor(libobj: Elf) -> None:
    """El trasvase (cola 1 -> cola 0) y la extracción de la cola 0 son los del bucle AppSystem::Main."""
    assert _bl_thumb(libobj, 0x7EF92A) == POLL and _bl_thumb(libobj, 0x7EF932) == QPUSH, "trasvase: poll(1) + push(0)"
    assert _bl_thumb(libobj, 0x7EF94E) == POLL, "pop: poll(cola 0)"
    assert _bl_thumb(libobj, 0x7EEFDA) == POP, "AppSystem::Main extrae de la cola 0"
    assert _bl_thumb(libobj, 0x7EEFE2) == DISPATCH, "y despacha con AppSystem::dispatch"
    assert _bl_thumb(libobj, 0x7EF03A) == MOVER, "el trasvase se ejecuta dentro de AppSystem::Main"
    assert _h(libobj, 0x7EEF4E) == 0x6AA5 and _h(libobj, 0x7EF036) == 0xB115, \
        "r5 = min([AppSystem+0x28], count(1)) y `cbz r5` salta el trasvase"


def test_pushfilterevent_encola_sin_avisar(libobj: Elf, viewunified2: Elf) -> None:
    """La tecla sale de `pushFilterEvent` hacia la cola con notify=0 (no despierta al consumidor)."""
    # el filtro es el puntero que hay en libObj+0x10a8c50 (slot del GOT con addend = esa variable)
    assert _h(libobj, PUSHFILTER + 0x24) == 0x58EB, "0x111818: ldr r3,[r5,r3] (slot del filtro)"
    assert _h(libobj, PUSHFILTER + 0x28) == 0xB11B, "0x11181c: cbz r3 (sin filtro -> encolar en la lista)"
    assert _h(libobj, FILTRO_SIN_AVISO + 2) == 0x2200, "0x7f0ade: movs r2,#0 (notify = 0)"
    assert _bl_thumb(libobj, 0x11183C) == 0x127BB6, "el vaciado de la lista filtrada llama a 0x127bb6"
    assert _h(libobj, FILTRO_SIN_AVISO + 0xC) == 0xF4EE, "0x7f0ae8: b.w al PLT 0xdf270 (EventManager::push)"
    # el filtro real del invitado (medido: `P 10a8c50` = 0x78ca8fb9) es de viewUnified2 y conoce el código de la tecla
    assert viewunified2.u32(0x182080) == 0x150100F2, "el filtro compara con 0x150100f2 (pulsación)"


def test_shim_trae_medida_y_arreglo() -> None:
    src = SHIM.read_text()
    assert "EQTRACE" in src and '"EQMAX"' in src, "EQTRACE/EQMAX: cada publicación en la cola del framework"
    # medido: con el parche puesto, 3 de 3 arranques en frío no compusieron la OSD y con él apagado pintó; queda opt-in
    assert "static void evqnotify(void)" in src and 'getenv("EVQNOTIFY")' in src, "EVQNOTIFY=1 lo enciende"
    assert "*p = 0x2201" in src, "el arreglo escribe movs r2,#1 en libObj+0x7f0ade"
    assert "mwf_nullsafe(); evqnotify(); }" in src, "se arma al cargar libObj"
