"""G22-DISPATCH — el reparto del evento de la tecla hasta la acción, leído de los binarios 3.21, sin QEMU.

Fija lo que el informe `docs/gui/g22-reproduccion-dispatch.md` da por VERIFICADO:

1. `Event` es `{+4 código (palabra), +8 destino (BYTE), +9 clase (BYTE)}` y `Event::getDest` es
   `ldrb r0,[r0,#8]` (`libObj+0x7eebf8`): el «destino» que reparte el framework es un byte, no una palabra.
2. `InputService::createEvent` (`libObj+0x1106b8`) fuerza **clase 1** y copia el destino de su 2.º argumento;
   **ninguno de sus 21 llamantes pasa un destino con el bit 8**, y la publicación de la tecla es
   `movs r2,#4` en `libObj+0x111972` → `createEvent` (`0x11197c`) → `pushFilterEvent` (`0x1119ea`).
3. El filtro de la vista (`viewUnified2+0x181fb8`) **no filtra**: escribe en la lista que le pasa `pushFilterEvent`
   (`InputService+0xc`), sintetiza `Event(0x15070010,4,1)` y `Event(0x150701a0,4,1)` y reengancha el original
   con `std::_List_node_base::_M_hook`.
4. Quien vacía esa lista es el propio `pushFilterEvent` (front/pop) hacia `0x127bb6` →
   `libObj+0x7f0adc` = `EventManager::push(evento, notify = 0)`; la vista no la lee nunca.
5. `AppSystem::dispatch` (`libObj+0x7eed0c`) reparte por bits de `Event[+8]`: 1/2/4 a tres gestores y **8 a la
   vista** (`[AppSystem+0x1c]->vtable[+8]`, la ranura del `DispatchEvent` de `libObj+0xf59f0`).
6. La **clase** (`Event[+9]`) no es una «clase de evento registrada»: en `EventManager::push` (`libObj+0x7ef960`)
   sólo elige cola (1 → cola 1, 0 → cola 0, otra → descartada) y `AppSystem::Main` sólo vacía la cola 0.
7. La tabla `{evento, acción}` de `viewUnified2.so` (`.rodata 0x3a03d4`, 19 entradas, `{0x150100f0, 4}`) tiene un
   único lector, `viewUnified2+0x1906a8`, **sin llamantes estáticos**.
8. La vista sí admite ids `0x15xxxxx` (`viewUnified2+0x17dfb0`): tres excepciones y el resto se despacha como id
   `2`; la máscara `0x7ffffffe` de la lista de teclas (`0x4aa848`) no se compara, la **devuelve**
   `InfraInput::GetEventStatus` (`libObj+0x805804`) en `_InfraInputEvent+8`.
9. `InputService::getInputEventStatus` (`libObj+0x114104`) es un mandato `ParamList` sin llamantes: no hay
   «modo VIEW» que consultar.

Los binarios viven en `analysis/gui/g22/harness/stage/cam/usr/lib` (no versionados): si faltan, el módulo se salta.
No arranca ninguna VM; el comportamiento en el invitado está en el informe y en `docs/gui/g22-cola-eventos.md`.
"""
from __future__ import annotations

import re
import struct
from pathlib import Path

import pytest

from test_g22_repro import Elf

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib"

if not (LIB / "libObj.so").exists() or not (LIB / "viewUnified2.so").exists():
    pytest.skip("faltan los binarios del arnés (analysis/gui/g22/harness/stage): test estático", allow_module_level=True)

# ---------------------------------------------------------------- libObj (VA del ELF)
EVENT_CTOR = 0x7F17F8  # Event::Event(unsigned long, unsigned char, unsigned char)
EVENT_GETDEST = 0x7EEBF8  # Event::getDest()  -> ldrb r0,[r0,#8]
CREATE_EVENT = 0x1106B8  # InputService::createEvent(unsigned long, unsigned char)
TECLA_DEST = 0x111972  # movs r2,#4  (destino de la publicación de la tecla)
TECLA_PUSHFILTER = 0x1119EA  # b.w InputService::pushFilterEvent
PUSHFILTER = 0x1117F4  # InputService::pushFilterEvent(Event*)
PUSHFILTER_PLT = 0xDCE8C  # su stub de .plt dentro de libObj
ADM_PUSH = 0x127BB6  # AbstractUtilityManager::pushEvent -> EventManager::push(notify=0)
ADM_PUSH_NOTIFY = 0x127BC4  # AbstractUtilityManager::notify
EM_PUSH_SIN_AVISO = 0x7F0ADC
EM_PUSH = 0x7EF960  # EventManager::push(Event*, bool)
EM_POP = 0x7EF940
EM_TRASVASE = 0x7EF910
EM_COUNT = 0x7EF9FC
EM_CLASE = 0x7EF88C
APP_MAIN = 0x7EEEE8  # AppSystem::Main (hilo «Appframework»)
APP_DISPATCH = 0x7EED0C  # AppSystem::dispatch(Event*)
DISPATCH_THUNK = 0xF59F0  # DefRootView::ActionEventMapBase::DispatchEvent (vtable[+8])
VIEW_GETEVENTID = 0x121D58  # ViewBase::GetEventId()
VIEW_MAP_ID = 0xF2FE0  # mapa de traducción de ids de la vista
VIEW_GETTRIGGER = 0x7F1A98  # View::getTriggerTable() -> [View+0x20]
GINPUTSTATUS = 0x114104  # InputService::getInputEventStatus(ParamList*, ParamList const*)
INFRA_GETSTATUS = 0x805804  # InfraInput::GetEventStatus(int, int, _InfraInputEvent*)
MASCARA_SIN_CONDICION = 0x7FFFFFFE
# G22-TECLA (27-11-2026): el destino de la tecla NO lo fija `libObj+0x111972` (DESTKEY): con ese parche puesto la medida
# siguió dando `dest=4` y `TRACE 1106b8 r1=150100f2 r2=4 lr=libObj+0x113080` señala el `blx` de `0x11307c`, cuyo
# `movs r2,#4` está en `0x113076`. La función gemela `0x11191c` (con el `movs` en `0x111972`) no tiene ni una referencia.
TECLA_DEST_VIVA = 0x113076  # movs r2,#4 de la publicación de la tecla (04 22)
TECLA_CREATE_BLX = 0x11307C  # blx InputService::createEvent
CREATE_EVENT_PLT = 0xDF280  # stub .plt de createEvent en libObj
TECLA_DEST_MUERTA = 0x111972  # el `movs r2,#4` de DESTKEY: código sin llamantes
TECLA_BASE_MAS_UNO = 0x113054  # adds r1,r6,#1 (suelta)
TECLA_BASE_MAS_DOS = 0x11304C  # adds r1,r6,#2 (pulsación, r6 = 0x150100f0)


FILTRO_DEST_1 = 0x18201C  # movs r2,#4 -> Event(0x15070010,4,1) del filtro
FILTRO_DEST_2 = 0x182042  # movs r2,#4 -> Event(0x150701a0,4,1) del filtro
FILTRO_FIN = 0x182068  # fin del filtro (pop {r4,r5,r6,r7,pc} en 0x182068)

# ------------------------------------------------------------ viewUnified2 (VA del ELF)
FILTRO = 0x181FB8  # el filtro registrado en libObj+0x10a8c50 (el invitado tenía +1)
FILTRO_LITS = 0x182078  # 9 códigos de evento del conmutador del filtro
LISTA_PUSH = 0x181F9E  # push_back(&lista, evento)
LISTA_HOOK = 0x181F9A  # b.w std::_List_node_base::_M_hook
TABLA_EVENTO_ACCION = 0x3A03D4  # 19 pares {evento, acción}
BUSCADOR_ACCION = 0x1906A8  # único lector de la tabla
VISTA_DISPATCH = 0x17DF8C  # (vista) ViewBase::GetEventId() -> ActionEventMap::DispatchEvent
KEYLIST_GRUPO_F = 0x4AA848  # {0x1f7, 0x150100f0, 0x7ffffffe}
DESCRIPTOR_GRUPO_F = 0x4AA6C8  # {lista, callback, 4, 0, 0}

# ----------------------------------------------------------------------------- helpers
def _h(lib: Elf, va: int) -> int:
    o = lib.v2o(va)
    assert o is not None, f"VA sin segmento: {va:#x}"
    return int.from_bytes(lib.d[o : o + 2], "little")


def _w(lib: Elf, va: int) -> int:
    o = lib.v2o(va)
    assert o is not None, f"VA sin segmento: {va:#x}"
    return struct.unpack_from("<I", lib.d, o)[0]


def _bl_target(lib: Elf, va: int) -> int | None:
    """Destino de un `bl`/`blx`/`b.w` Thumb-2 de 4 bytes (0xF000 + 0xD000/0xC000/0x9000), o None."""
    h1, h2 = _h(lib, va), _h(lib, va + 2)
    if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) not in (0xD000, 0xC000, 0x9000):
        return None
    s = (h1 >> 10) & 1
    imm10 = h1 & 0x3FF
    j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
    i1, i2 = 1 - (j1 ^ s), 1 - (j2 ^ s)
    imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | ((h2 & 0x7FF) << 1)
    if s:
        imm -= 1 << 25
    return (va + 4 + imm) & 0xFFFFFFFF


def _arm_imm(w: int) -> int:
    """Inmediato (rotado) de una instrucción data-processing ARM: es como codifica .plt la base del .got."""
    imm12 = w & 0xFFF
    rot = (imm12 >> 8) & 0xF
    imm8 = imm12 & 0xFF
    if not rot:
        return imm8
    return ((imm8 >> (2 * rot)) | (imm8 << (32 - 2 * rot))) & 0xFFFFFFFF


def _plt(lib: Elf) -> dict[int, str]:
    """Mapa VA de entrada de stub (.plt, ARM) -> nombre del símbolo importado (vía .rel.plt)."""
    d = lib.d
    rel = lib.secs[".rel.plt"]
    sim = lib.secs[".dynsym"]
    strs = lib.secs[".dynstr"]
    slots: dict[int, str | None] = {}
    for i in range(rel["size"] // 8):
        off, info = struct.unpack_from("<II", d, rel["off"] + i * 8)
        idx = info >> 8
        n, *_ = struct.unpack_from("<IIIBBH", d, sim["off"] + idx * 16)
        nombre = None
        if n:
            fin = d.find(b"\0", strs["off"] + n)
            nombre = d[strs["off"] + n : fin].decode()
        slots[off] = nombre
    salida: dict[int, str] = {}
    sec = lib.secs[".plt"]
    va = sec["addr"]
    while va < sec["addr"] + sec["size"] - 12:
        o = lib.v2o(va)
        assert o is not None
        w0, w1, w2 = struct.unpack_from("<III", d, o)
        es_stub = (
            (w0 & 0xFFFFF000) == 0xE28FC000
            and (w1 & 0xFFFFF000) == 0xE28CC000
            and (w2 >> 24) == 0xE5
            and ((w2 >> 16) & 0xF) == 0xC
        )
        if es_stub:
            slot = va + 8 + _arm_imm(w0) + _arm_imm(w1) + (w2 & 0xFFF)  # LDR: offset sin rotar
            nombre = slots.get(slot)
            if nombre:
                salida[va] = nombre
                if va >= 4 and _w(lib, va - 4) == 0x46C04778:  # «bx pc ; nop»
                    salida[va - 4] = nombre
            va += 12
        else:
            va += 4
    return salida


_RAMAS: dict[int, list[tuple[int, int]]] = {}


def _ramas(lib: Elf) -> list[tuple[int, int]]:
    """(VA, destino) de todas las ramas Thumb-2 de 32 bits de `.text` (bl/blx/b.w), memorizado.

    Se buscan primero las mitades `0xF0xx` (segundo byte 0xF0…0xF7 en un offset par) y sólo ésas se decodifican:
    recorrer los 11 MB de `libObj` mitad a mitad en Python puro costaba ~25 s.
    """
    if id(lib) in _RAMAS:
        return _RAMAS[id(lib)]
    t = lib.secs[".text"]
    o = lib.v2o(t["addr"])
    assert o is not None
    datos = lib.d[o : o + t["size"]]
    salida = []
    for m in re.finditer(rb".[\xf0-\xf7]", datos, re.DOTALL):
        if m.start() % 2:
            continue
        va = t["addr"] + m.start()
        destino = _bl_target(lib, va)
        if destino is not None:
            salida.append((va, destino))
    _RAMAS[id(lib)] = salida
    return salida


_CACHE: dict[tuple[int, str], list[int]] = {}


def _llamadas(lib: Elf, nombre: str, plt: dict[int, str] | None = None) -> list[int]:
    """Sitios de llamada (bl/blx/b.w) al stub .plt del símbolo importado `nombre` (memorizado)."""
    clave = (id(lib), nombre)
    if clave in _CACHE:
        return _CACHE[clave]
    plt = plt or _plt(lib)
    stubs = {va for va, n in plt.items() if n == nombre}
    sitios = [va for va, destino in _ramas(lib) if destino in stubs]
    _CACHE[clave] = sitios
    return sitios


def _sin_llamantes_a(lib: Elf, destino: int) -> list[int]:
    """Sitios de bl/blx/b.w (cualquiera) que apuntan a `destino` dentro del propio .text."""
    return [va for va, d in _ramas(lib) if d == destino]


def _destino_antes_de(lib: Elf, sitio: int, ventana: int = 0x18) -> int | None:
    """Último `movs/mov r2,#imm` antes de un sitio de llamada (destino que pasa el llamante)."""
    va = sitio - ventana
    ultimo = None
    while va < sitio:
        h = _h(lib, va)
        if (h & 0xFFF8) == 0x2200:  # movs r2,#imm8
            ultimo = h & 0xFF
        va += 2
    return ultimo


@pytest.fixture(scope="module")
def libobj() -> Elf:
    return Elf(LIB / "libObj.so")


@pytest.fixture(scope="module")
def viewunified2() -> Elf:
    return Elf(LIB / "viewUnified2.so")


@pytest.fixture(scope="module")
def plt_obj(libobj: Elf) -> dict[int, str]:
    return _plt(libobj)


@pytest.fixture(scope="module")
def plt_view(viewunified2: Elf) -> dict[int, str]:
    return _plt(viewunified2)


# ------------------------------------------------------------------------------- casos
def test_evento_codigo_palabra_y_destino_clase_bytes(libobj: Elf) -> None:
    """`Event`: código (palabra) en +4, destino (byte) en +8, clase (byte) en +9; `getDest` lee un byte."""
    assert _h(libobj, EVENT_CTOR + 4) == 0x7202, "0x7f17fc: strb r2,[r0,#8] (destino)"
    assert _h(libobj, EVENT_CTOR + 8) == 0x7243, "0x7f1800: strb r3,[r0,#9] (clase)"
    assert _h(libobj, EVENT_CTOR + 0xA) == 0x6041, "0x7f1802: str r1,[r0,#4] (código)"
    assert _h(libobj, EVENT_GETDEST + 4) == 0x7A00, "0x7eebfc: ldrb r0,[r0,#8] (getDest devuelve un byte)"
    assert _h(libobj, EM_CLASE + 4) == 0x7A40, "0x7ef890: ldrb r0,[r0,#9] (la clase se lee de +9)"


def test_create_event_fuerza_clase_1(libobj: Elf) -> None:
    """`InputService::createEvent` = `Event(código, destino, 1)`: la clase no la elige el llamante."""
    assert _h(libobj, CREATE_EVENT + 0x10) == 0x462A, "0x1106c8: mov r2,r5 (el destino es el 2.º argumento)"
    assert _h(libobj, CREATE_EVENT + 0x12) == 0x2301, "0x1106ca: movs r3,#1 (clase 1 fija)"
    assert _h(libobj, CREATE_EVENT + 0x16) == 0xF7CA, "0x1106ce: blx al PLT de Event::Event"


def test_ningun_create_event_usa_el_bit_8(libobj: Elf, plt_obj: dict[int, str]) -> None:
    """Los 21 llamantes de `createEvent` pasan destino 0, 1 o 4: **ninguno** enciende la vista (bit 8)."""
    sitios = _llamadas(libobj, "_ZN12InputService11createEventEmh", plt_obj)
    assert len(sitios) >= 20, f"se esperaban >=20 llamantes de createEvent, hay {len(sitios)}"
    destinos = {sitio: _destino_antes_de(libobj, sitio) for sitio in sitios}
    con_bit8 = {hex(s): d for s, d in destinos.items() if d is not None and d & 8}
    assert not con_bit8, f"algún createEvent enciende el bit 8 de la vista: {con_bit8}"
    conocidos = {d for d in destinos.values() if d is not None}
    assert conocidos <= {0, 1, 4}, f"destinos inesperados en createEvent: {conocidos}"
    assert destinos.get(0x11197C) == 4, "la publicación de la tecla usa destino 4"


def test_publicacion_de_la_tecla_es_destino_4(libobj: Elf, plt_obj: dict[int, str]) -> None:
    """`libObj+0x111972` (`04 22` = `movs r2,#4`) y salto a `pushFilterEvent` en `0x1119ea`."""
    assert _h(libobj, TECLA_DEST) == 0x2204, "0x111972: movs r2,#4 — destino de todos los eventos de tecla"
    assert _bl_target(libobj, TECLA_PUSHFILTER) == PUSHFILTER_PLT, "0x1119ea: b.w al PLT de pushFilterEvent"
    assert plt_obj.get(PUSHFILTER_PLT) == "_ZN12InputService15pushFilterEventEP5Event"


def test_filtro_de_la_vista_escribe_en_la_lista_del_servicio(viewunified2: Elf, plt_view: dict[int, str]) -> None:
    """El filtro es `(lista, evento)`: lee `Event::getId` y hace `push_back` (dos copias + el original)."""
    assert _h(viewunified2, FILTRO + 2) == 0xB085, "0x181fba: sub sp,#0x14 (marco del filtro)"
    assert _bl_target(viewunified2, FILTRO + 0xC) in {v for v, n in plt_view.items() if n == "_ZNK5Event5getIdEv"}
    codigos = [_w(viewunified2, FILTRO_LITS + 4 * i) for i in range(9)]
    assert codigos == [
        0x15050012, 0x15010032, 0x150100F2, 0x15070050, 0x15060020,
        0x150800C2, 0x15070010, 0x150700C0, 0x150701A0,
    ], "literal pool del conmutador del filtro (0x182078…0x182098)"
    assert _bl_target(viewunified2, LISTA_HOOK) in {v for v, n in plt_view.items() if n == "_ZNSt15_List_node_base7_M_hookEPS_"}


def test_filtro_sintetiza_dos_eventos_de_vista_con_destino_4(viewunified2: Elf) -> None:
    """Para `0x150100f2` sintetiza `Event(0x15070010,4,1)` y, como no es `0x150700c0`, `Event(0x150701a0,4,1)`."""
    assert _h(viewunified2, 0x181FE8) == 0x4B25, "0x181fe8: ldr r3,[pc,#0x94] -> [0x182080] = 0x150100f2"
    assert _w(viewunified2, 0x182080) == 0x150100F2
    assert _h(viewunified2, 0x181FEC) == 0xD012, "0x181fec: beq 0x182014 (0x150100f2 toma la rama que sintetiza)"
    assert _w(viewunified2, 0x182090) == 0x15070010, "código de la 1.ª copia"
    assert _h(viewunified2, 0x18201C) == 0x2204, "0x18201c: movs r2,#4 (destino de la 1.ª copia)"
    assert _h(viewunified2, 0x18201E) == 0x2301, "0x18201e: movs r3,#1 (clase de la 1.ª copia)"
    assert _w(viewunified2, 0x182094) == 0x150700C0, "0x182034: el único id que NO recibe la 2.ª copia"
    assert _w(viewunified2, 0x182098) == 0x150701A0, "código de la 2.ª copia"
    assert _h(viewunified2, 0x182042) == 0x2204, "0x182042: movs r2,#4 (destino de la 2.ª copia)"


def test_pushfilterevent_vacia_la_lista_hacia_eventmanager(libobj: Elf, plt_obj: dict[int, str]) -> None:
    """Quien consume la lista es `pushFilterEvent`: front/pop → `0x127bb6` → `EventManager::push(notify=0)`."""
    assert _h(libobj, PUSHFILTER + 0xC) == 0xF106, "0x111800: add.w r4,r6,#0xc (la lista es this+0xc)"
    assert _bl_target(libobj, PUSHFILTER + 0x1C) == 0x1114B0, "0x111810: bl 0x1114b0 (clear de la lista)"
    assert _bl_target(libobj, PUSHFILTER + 0x3E) == 0x11127E, "0x111832: front() del bucle de vaciado"
    assert _bl_target(libobj, PUSHFILTER + 0x4E) == 0x1114DE, "0x111842: pop_front()"
    assert _bl_target(libobj, PUSHFILTER + 0x54) == 0x11113E, "0x111848: empty()"
    assert _h(libobj, PUSHFILTER + 0x5A) == 0xD0EF, "0x11184e: beq 0x111830 (while !empty())"
    assert _bl_target(libobj, PUSHFILTER + 0x48) == ADM_PUSH, "0x11183c: bl 0x127bb6 (pushEvent del elemento)"
    assert _bl_target(libobj, PUSHFILTER + 0x5E) == ADM_PUSH_NOTIFY, "0x111852: bl 0x127bc4 (notify)"
    assert _h(libobj, ADM_PUSH + 4) == 0x6840, "0x127bba: ldr r0,[r0,#4] (el EventManager del gestor)"
    assert _bl_target(libobj, ADM_PUSH + 0xA) == EM_PUSH_SIN_AVISO, "0x127bc0: b.w 0x7f0adc (push sin aviso)"
    assert _h(libobj, EM_PUSH_SIN_AVISO + 2) == 0x2200, "0x7f0ade: movs r2,#0 (notify = 0)"


def test_dispatch_reparte_por_destino_y_solo_bit8_llega_a_la_vista(libobj: Elf) -> None:
    """`AppSystem::dispatch`: 1/2/4 a tres gestores y 8 a `[this+0x1c]->vtable[+8]` (DispatchEvent)."""
    assert _w(libobj, 0x7EEE20) == 0x0F01F016, "0x7eee20: tst.w r6,#1"
    assert _w(libobj, 0x7EEDDA) == 0x0302F006, "0x7eedda: and r3,r6,#2"
    assert _w(libobj, 0x7EED94) == 0x0304F006, "0x7eed94: and r3,r6,#4"
    assert _w(libobj, 0x7EEE5A) == 0x0608F006, "0x7eee5a: and r6,r6,#8"
    assert _h(libobj, 0x7EEE62) == 0x69E0, "0x7eee62: ldr r0,[r4,#0x1c]"
    assert _h(libobj, 0x7EEE66) == 0x6803 and _h(libobj, 0x7EEE68) == 0x689B and _h(libobj, 0x7EEE6A) == 0x4798, \
        "0x7eee66-0x7eee6a: ldr r3,[r0] · ldr r3,[r3,#8] · blx r3 (el DispatchEvent virtual)"
    assert _h(libobj, DISPATCH_THUNK + 6) == 0x689B and _h(libobj, DISPATCH_THUNK + 8) == 0x4798, \
        "el thunk de DispatchEvent usa la misma ranura +8"
    assert _h(libobj, 0x7EF332) == 0x61E0, "0x7ef332: str r0,[r4,#0x1c] (la vista raíz en AppSystem)"
    # el reparto de 4 llama a 0x7f4528 y el de 8 es el único que toca el objeto de la vista
    assert _bl_target(libobj, 0x7EEDAA) == 0x7F4528, "0x7eeda6/0x7eedaa: el destino 4 va a 0x7f4528"


def test_clase_solo_elige_cola(libobj: Elf) -> None:
    """`EventManager::push`: clase 1 → cola 1 (con aviso cada 100), clase 0 → cola 0, otra → descartada."""
    assert _h(libobj, EM_PUSH + 0x14) == 0x2801, "0x7ef974: cmp r0,#1"
    assert _h(libobj, EM_PUSH + 0x18) == 0xD12B, "0x7ef978: bne 0x7ef9d2 (no es clase 1)"
    assert _h(libobj, 0x7EF98E) == 0x6858, "0x7ef98e: ldr r0,[r3,#4] = cola 1"
    assert _h(libobj, 0x7EF99C) == 0x2164, "0x7ef99c: movs r1,#0x64 (aviso cada 100)"
    assert _h(libobj, 0x7EF9D2) == 0xB950, "0x7ef9d2: cbnz r0 (cualquier clase != 0 se descarta)"
    assert _h(libobj, 0x7EF9DE) == 0x6818, "0x7ef9de: ldr r0,[r3] = cola 0"
    assert _h(libobj, EM_COUNT + 0xE) == 0xF853 and _h(libobj, EM_COUNT + 0x10) == 0x0025, \
        "0x7efa0a: ldr.w r0,[r3,r5,lsl #2] (la cola se indexa por el argumento)"
    assert _bl_target(libobj, APP_MAIN + 0xF2) == EM_POP, "0x7eefda: AppSystem::Main extrae de la cola 0"
    assert _bl_target(libobj, APP_MAIN + 0xFA) == APP_DISPATCH, "0x7eefe2: y despacha"
    assert _bl_target(libobj, APP_MAIN + 0x152) == EM_TRASVASE, "0x7ef03a: trasvase 1 -> 0"
    assert _h(libobj, 0x7EF036) == 0xB115, "0x7ef036: cbz r5 (sin cuenta, no hay trasvase)"


def test_tabla_evento_accion_y_su_unico_lector(libobj: Elf, viewunified2: Elf) -> None:
    """19 pares `{evento, acción}` en `.rodata 0x3a03d4`; el primero `{0x150100f0, 4}`; lector sin llamantes."""
    assert _w(viewunified2, TABLA_EVENTO_ACCION) == 0x150100F0
    assert _w(viewunified2, TABLA_EVENTO_ACCION + 4) == 4, "la acción de la Reproducción es la 4"
    assert _h(viewunified2, BUSCADOR_ACCION + 0x20) == 0x2B13, "0x1906c8: cmp r3,#0x13 (19 entradas)"
    assert _w(viewunified2, 0x1906D0) == 0x0020FD1E, "0x1906d0: literal que +pc da 0x3a03d4"
    assert 0x0020FD1E + 0x1906B6 == TABLA_EVENTO_ACCION
    # el buscador no tiene llamantes ni bl, ni b.w, ni bx: no hay ningún puntero a él en el fichero
    sitios = _sin_llamantes_a(viewunified2, BUSCADOR_ACCION)
    assert sitios == [], f"la tabla solo la lee 0x1906a8, y no debe tener llamantes: {[hex(s) for s in sitios]}"
    for seccion in (".data.rel.ro", ".data", ".rodata"):
        s = viewunified2.secs[seccion]
        for va in range(s["addr"], s["addr"] + s["size"] - 4, 4):
            if viewunified2.v2o(va) is None:
                continue
            assert _w(viewunified2, va) not in (BUSCADOR_ACCION, BUSCADOR_ACCION | 1), \
                f"puntero al buscador en {seccion}:{va:#x}"


def test_la_vista_acepta_ids_1501xxxx(viewunified2: Elf) -> None:
    """La vista prueba `(id & 0xFFFFF000)==0x15000000`, exceptúa tres ids y despacha el resto como id 2."""
    assert _h(viewunified2, VISTA_DISPATCH + 0x24) == 0x0D23, "0x17dfb0: lsrs r3,r4,#0x14"
    assert _h(viewunified2, VISTA_DISPATCH + 0x26) == 0x051B, "0x17dfb2: lsls r3,r3,#0x14 (id & 0xFFFFF000)"
    assert _h(viewunified2, VISTA_DISPATCH + 0x28) == 0xF1B3 and _h(viewunified2, VISTA_DISPATCH + 0x2A) == 0x5FA8, \
        "0x17dfb4: cmp.w r3,#0x15000000"
    assert _w(viewunified2, VISTA_DISPATCH + 0x5C) == 0x150700C0, "excepción 1 (literal de 0x17dfe8)"
    assert _w(viewunified2, VISTA_DISPATCH + 0x60) == 0x15010011, "excepción 2 (literal de 0x17dfec)"
    assert _w(viewunified2, VISTA_DISPATCH + 0x64) == 0x15090002, "excepción 3 (literal de 0x17dff0)"
    assert _h(viewunified2, 0x17DFD2) == 0x2402, "0x17dfd2: movne r4,#2 (el resto de 0x15xxxxx -> id 2)"
    assert _bl_target(viewunified2, 0x17DFDE) is not None
    assert _h(viewunified2, 0x17DFD4) == 0xF8D5 and _h(viewunified2, 0x17DFD6) == 0x0124, \
        "0x17dfd4: ldr.w r0,[r5,#0x124] (el ActionEventMap de la vista)"


def test_lista_de_teclas_del_grupo_f_y_su_mascara(libobj: Elf, viewunified2: Elf) -> None:
    """Descriptor `0xf` → lista `0x4aa848` con `{0x1f7, 0x150100f0, 0x7ffffffe}`; la máscara se devuelve, no se compara."""
    assert [_w(viewunified2, DESCRIPTOR_GRUPO_F + 4 * i) for i in range(3)] == [KEYLIST_GRUPO_F, 0x181A3D, 4]
    assert [_w(viewunified2, KEYLIST_GRUPO_F + 4 * i) for i in range(3)] == [0x1F7, 0x150100F0, MASCARA_SIN_CONDICION]
    assert _w(viewunified2, 0x4AA854) == 0x7095 and _w(viewunified2, 0x4AA858) == 0x15010120, "2.ª entrada del grupo"
    # InfraInput::GetEventStatus copia la máscara en _InfraInputEvent+8 y por defecto pone 0x7ffffffe
    assert _h(libobj, INFRA_GETSTATUS + 0xC6) == 0x60A5, "0x8058ca: str r5,[r4,#8] (la máscara en la salida)"
    assert _w(libobj, 0x805918) == MASCARA_SIN_CONDICION, "0x805918: literal 0x7ffffffe"
    assert _h(libobj, 0x8058B2) == 0xF06F, "0x8058b2: mvn r5,#0x80000000 (valor cuando la clave está inhibida)"


def test_get_input_event_status_no_es_portero(libobj: Elf, plt_obj: dict[int, str]) -> None:
    """`getInputEventStatus` es un mandato `ParamList`: sin llamantes y ajeno al camino de la tecla."""
    assert _h(libobj, GINPUTSTATUS) == 0xE92D, "0x114104: push.w (entrada del mandato)"
    assert _w(libobj, 0x114258) == 0x17005003 and _w(libobj, 0x11425C) == 0x17005008, "parámetros de consulta"
    sitios = _sin_llamantes_a(libobj, GINPUTSTATUS)
    assert sitios == [], f"getInputEventStatus no debe tener llamantes: {[hex(s) for s in sitios]}"
    # y la vista tiene su propio traductor de ids y su tabla de disparo (paso 2 del informe)
    assert _h(libobj, VIEW_GETEVENTID + 0x1E) == 0xF425 and _h(libobj, VIEW_GETEVENTID + 0x20) == 0x637E, \
        "0x121d76: bic r3,r5,#0xfe0 (limpia los 12 bits bajos para comparar la clase de la vista)"
    assert _bl_target(libobj, VIEW_GETEVENTID + 0x12) == VIEW_MAP_ID, "0x121d6a: bl 0xf2fe0 (mapa de ids)"
    assert _h(libobj, VIEW_GETTRIGGER + 4) == 0x6A00, "0x7f1a9c: ldr r0,[r0,#0x20] (la tabla de disparo)"


# ------------------------------------------------- G22-TECLA: quién fija el destino de los tres eventos
def test_el_destino_de_la_tecla_esta_en_113076_y_llama_a_create_event(libobj: Elf) -> None:
    """`TRACE 1106b8 … lr=libObj+0x113080`: el llamante es el `blx` de `0x11307c`, y su `movs r2,#4` está en `0x113076`.

    Es la función gemela **viva** de `0x11191c` (la del `movs` de DESTKEY en `0x111972`, sin referencias): el código del
    evento se calcula desde la base (`r6`, `0x150100f0` para la Reproducción) con `+1` (suelta → `0x150100f1`), `+2`
    (pulsación → `0x150100f2`) o `+4` según el estado que devuelve `InputService::changeTactStatus`.
    """
    assert _h(libobj, TECLA_DEST_VIVA) == 0x2204, "0x113076: movs r2,#4 (bytes 04 22)"
    assert _bl_target(libobj, TECLA_CREATE_BLX) == CREATE_EVENT_PLT, "0x11307c: blx createEvent (0xdf280)"
    assert _h(libobj, 0x113074) == 0x4B23, "0x113074: ldr r3,[pc,#0x8c] (desplazamiento del singleton en el .got)"
    assert _h(libobj, 0x113078) == 0x58EE, "0x113078: ldr r6,[r5,r3] (la instancia de InputService)"
    assert _h(libobj, 0x11307A) == 0x6830, "0x11307a: ldr r0,[r6] (this = la instancia)"
    assert _h(libobj, 0x113080) == 0x4605, "0x113080: mov r5,r0 (retorno de createEvent, y el lr de la traza)"
    assert _h(libobj, TECLA_BASE_MAS_DOS) == 0x1CB1, "0x11304c: adds r1,r6,#2 (pulsación)"
    assert _h(libobj, TECLA_BASE_MAS_UNO) == 0x1C71, "0x113054: adds r1,r6,#1 (suelta)"
    assert _h(libobj, 0x113050) == 0x1D31, "0x113050: adds r1,r6,#4 (estado 2 con [r4+0x14] != 0)"
    # los parámetros que añade después: 0x1b, 0x1c y 0x20 (los mismos que la gemela muerta)
    assert _h(libobj, 0x11309A) == 0x2120, "0x11309a: movs r1,#0x20 (tercer addParameter)"
    assert _h(libobj, 0x11309C) == 0x4642, "0x11309c: mov r2,r8 (valor del parámetro 0x20)"


def test_la_gemela_111972_no_tiene_ni_una_referencia(libobj: Elf) -> None:
    """`DESTKEY` parchea `0x111972` y la medida siguió dando `dest=4`: ese código no se ejecuta (0 ramas y 0 punteros)."""
    assert _h(libobj, TECLA_DEST_MUERTA) == 0x2204, "0x111972: movs r2,#4 (mismo molde que la viva)"
    assert _sin_llamantes_a(libobj, 0x11191C) == [], "ninguna rama apunta a la función gemela"
    for seccion in (".data.rel.ro", ".data", ".rodata", ".got", ".text"):
        s = libobj.secs.get(seccion)
        if not s:
            continue
        for va in range(s["addr"], s["addr"] + s["size"] - 4, 4):
            if libobj.v2o(va) is None:
                continue
            assert _w(libobj, va) not in (0x11191C, 0x11191D), f"puntero a la gemela en {seccion}:{va:#x}"


def test_el_filtro_fija_el_destino_de_sus_dos_copias_y_no_toca_el_original(viewunified2: Elf) -> None:
    """Los dos `movs r2,#4` del filtro (`0x18201c`, `0x182042`) son el destino de `0x15070010` y `0x150701a0`.

    Y el original entra en la lista con el destino que le dio `createEvent`: entre `0x181fb8` y `0x182068` no hay ningún
    `strb rX,[rY,#8]` (codificación T1 `0x7200..0x723f`) ni otra escritura sobre `[evento+8]`.
    """
    assert _h(viewunified2, FILTRO_DEST_1) == 0x2204, "0x18201c: movs r2,#4"
    assert _h(viewunified2, FILTRO_DEST_1 + 2) == 0x2301, "0x18201e: movs r3,#1 (clase)"
    assert _w(viewunified2, 0x182090) == 0x15070010, "0x182090: código de la 1.ª copia"
    assert _h(viewunified2, FILTRO_DEST_2) == 0x2204, "0x182042: movs r2,#4"
    assert _h(viewunified2, FILTRO_DEST_2 + 2) == 0x2301, "0x182044: movs r3,#1 (clase)"
    assert _w(viewunified2, 0x182098) == 0x150701A0, "0x182098: código de la 2.ª copia"
    escrituras = [va for va in range(FILTRO, FILTRO_FIN, 2) if 0x7200 <= _h(viewunified2, va) <= 0x723F]
    assert escrituras == [], f"strb rX,[rY,#8] dentro del filtro: {[hex(v) for v in escrituras]}"
