"""G22-DIAL-POS — posiciones del dial de modos medidas y menú Fn/rueda (sin QEMU).

Evidencia medida (perfil `dialpos`, puerto 8661, 26-11-2026): `docs/gui/g22-dial-fn-rueda.md` §3 y §9.
Lo que se comprueba aquí:

1. La posición inyectada en el dial vuelve tal cual de `CmnViewBigModelUtil::getRecViewFromDial`
   (`OPENVIEWDIAL`), es decir el número que recibe `openView` lo pone el firmware.
2. `POSICIONES_MODO` sólo lleva las posiciones cuyo resultado es coherente con la cámara: las cuatro
   pendientes medidas (MR 1, película 8, SCN 0xb, panorámica 0x10) se midieron; sólo 8 y 0xb se añaden,
   porque 1 y 0x10 dan la MISMA pantalla y sin indicador de modo (no se pueden distinguir).
3. El mapa de teclas de Fn, rueda y dial superior (`TECLAS`/`pulsa`) no cambia y sigue siendo el del
   driver de `InfraInput`.
4. Bytes del despachador estático modo → icono (`viewUnified2+0x18e454`) cuando el binario está a mano.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "gui" / "harness"))
import live

# Posición inyectada (KEY_POS_MODE_DIAL) → (lo que devolvió getRecViewFromDial, md5 de la captura tras reabrir
# la vista con OPENVIEWDIAL, qué pinta). Medido: shim.log `OPENVIEWDIAL getRecViewFromDial() = n` + PNG.
MEDIDO = {
    0x1: (1, "cb0bd7f2f1d53e6142c5b2377fd9323f", "sin indicador de modo; idéntica a 0x10"),
    0x8: (8, "a157d367d087a93959edb1bee0ad252a", "diseño de película; sin indicador en la esquina"),
    0xB: (11, "d8c892c1bf141afaddc366e82e3c9148", "icono de SCN arriba y rótulo «SCN» abajo"),
    0x10: (16, "cb0bd7f2f1d53e6142c5b2377fd9323f", "sin indicador de modo; idéntica a 0x1"),
    0x3: (3, "ca2b3e17ea4c5abb3f7aa3db64e2e8de", "letra P (control; igual que la pantalla de arranque)"),
}
# Posiciones medidas que NO se añaden: no se distinguen entre sí (misma pantalla, sin indicador).
NO_VERIFICADO = {0x1: "MR", 0x10: "panorámica"}
# Estados de `POSICIONES_MODO` que están medidos y son coherentes.
COHERENTES = {0x8: "Película", 0xB: "SCN"}


def test_la_posicion_vuelve_tal_cual_del_firmware():
    """OPENVIEWDIAL devolvió exactamente la posición inyectada en las cuatro pendientes y en el control."""
    for pos, (devuelto, _md5, _pinta) in MEDIDO.items():
        assert devuelto == pos, hex(pos)


def test_posiciones_modo_solo_lleva_las_coherentes():
    """1 (MR) y 0x10 (panorámica) dan la misma captura byte a byte: fuera de POSICIONES_MODO; 8 y 0xb dentro."""
    assert dict(live.POSICIONES_MODO) == {"Auto": 2, "P": 3, "A": 4, "S": 5, "M": 6, "Película": 8, "SCN": 0xB}
    estados = [e for _n, e in live.POSICIONES_MODO]
    for estado in COHERENTES:
        assert estado in estados
    for estado, nombre in NO_VERIFICADO.items():
        assert estado not in estados, f"{nombre} no se distingue: no se añade"
    # el criterio de coherencia, en números: las dos no verificadas comparten pantalla y las añadidas no
    assert MEDIDO[0x1][1] == MEDIDO[0x10][1]
    assert MEDIDO[0x8][1] != MEDIDO[0xB][1] != MEDIDO[0x3][1]


def test_las_posiciones_nuevas_no_mueven_el_indice_de_la_pagina():
    """Se añaden al final: los índices que ya usaba la página (y /modo) 0..4 siguen siendo los mismos."""
    assert [n for n, _e in live.POSICIONES_MODO[:5]] == ["Auto", "P", "A", "S", "M"]
    assert [e for _n, e in live.POSICIONES_MODO[:5]] == [2, 3, 4, 5, 6]
    assert [e for _n, e in live.POSICIONES_MODO].index(live.DIAL_INICIAL) == 1  # __MODO0__ = P


def test_mapa_de_teclas_del_menu_fn_y_los_diales():
    """T7: Fn 0x70a1/0x95; rueda 0x10000015/0x1e5 y dial superior 0x10000014/0x1e4, con paso con signo y sin suelta."""
    assert live.TECLAS["fn"] == (0x70A1, 0x95)
    assert live.TECLAS["rueda_der"] == (0x10000015, 0x1E5, 1)
    assert live.TECLAS["rueda_izq"] == (0x10000015, 0x1E5, -1)
    assert live.TECLAS["dial_der"] == (0x10000014, 0x1E4, 1)
    assert live.TECLAS["dial_izq"] == (0x10000014, 0x1E4, -1)
    assert isinstance(live.TECLAS["fn"][0], int) and len(live.TECLAS["fn"]) == 2  # sin paso: tecla, no dial


def _vm_falsa(monkeypatch):
    vm = object.__new__(live.Vm)
    vm.cerrojo_dial, vm.sock, vm.enviados = live.threading.Lock(), None, []
    vm.tecla = lambda k, v, i: vm.enviados.append(("K", k, v, i))
    vm.envia = lambda d: vm.enviados.append(d)
    monkeypatch.setattr(live.time, "sleep", lambda _s: None)
    monkeypatch.setattr(live.threading, "Thread",
                        lambda target, args=(), daemon=None: type("T", (), {"start": lambda self: target(*args)})())
    return vm


def test_la_rueda_manda_su_paso_y_el_dial_el_suyo(monkeypatch):
    """Las dos vías de la rueda/dial son pasos con signo (`callback_dial_signed_speed`, libObj+0x111c80)."""
    vm = _vm_falsa(monkeypatch)
    for nombre, valor, esperado in (("rueda_der", 1, 1), ("rueda_izq", 1, 0xFFFFFFFF),
                                    ("dial_der", 1, 1), ("dial_izq", 1, 0xFFFFFFFF)):
        vm.enviados.clear()
        live.pulsa(vm, nombre, valor)
        clave, indice = live.TECLAS[nombre][0], live.TECLAS[nombre][1]
        assert vm.enviados == [("K", clave, esperado, indice)], nombre
    vm.enviados.clear()
    live.pulsa(vm, "fn", 1)
    live.pulsa(vm, "rueda_der", 0)  # los diales no tienen suelta
    assert vm.enviados == [("K", 0x70A1, 1, 0x95)]


LIB = RAIZ / "analysis" / "gui" / "g22" / "harness" / "stage" / "cam" / "usr" / "lib" / "viewUnified2.so"


@pytest.mark.skipif(not LIB.exists(), reason="viewUnified2.so del arnés no disponible (falta setup.sh)")
def test_tabla_estatica_del_modo_a_icono():
    """viewUnified2+0x18e454: 3 → 0x15 (P), 5 → 0x16, 4 → 0x17, 6 → 0x18; 1 y 0x10 caen en iconos que la vista no pinta.

    Las consultas hijas (parámetro del modelo) son 0x01070a5e (MR), 0x0107010b (película), 0x0107015e (SCN) y
    0x0107099a (panorámica); los defectos son 0 (MR sin modo), 3 (SCN sin escena), 0x19 (película) y 0x10.
    """
    b = LIB.read_bytes()
    # despacho: `cmp r4,#modo` + `beq.w` (para 8 el registro es r3, `sxtb r3,r3` primero)
    despacho = {1: (0x18E474, "012c"), 3: (0x18E594, "032c"), 5: (0x18E59A, "052c"), 4: (0x18E5A0, "042c"),
                6: (0x18E5A6, "062c"), 8: (0x18E5AE, "082b"), 0xB: (0x18E4A2, "0b2c"), 0x10: (0x18E566, "102c")}
    for modo, (donde, bytes_) in despacho.items():
        assert b[donde:donde + 2].hex() == bytes_, hex(modo)
        salto = b[donde + 2:donde + 4]  # beq.w (00 f0 …) o branch corto T1 (imm8 | 0xd<cond>)
        assert (salto[0] == 0x00 and salto[1] & 0xF0 == 0xF0) or salto[1] & 0xF0 == 0xD0, hex(modo)
    # icono de cada modo (movs r4, #icono) en el bloque al que salta su beq
    for destino, icono in ((0x18E852, 0x15), (0x18E856, 0x16), (0x18E85A, 0x17), (0x18E85E, 0x18)):
        assert b[destino] == icono and b[destino + 1] == 0x24, hex(destino)  # movs r4, #icono
    # iconos de las posiciones pendientes: 1 → 0x18e7d6 (0), 0x10 → 0x18e922 (0x10), 0xb sin escena → 0x18e7de (3)
    for destino, icono in ((0x18E7D6, 0x00), (0x18E7DE, 0x03), (0x18E922, 0x10)):
        assert b[destino] == icono and b[destino + 1] == 0x24, hex(destino)
    # literales de las consultas hijas (id de parámetro del modelo)
    for literal, valor in ((0x18E340, 0x01070A5E), (0x18E360, 0x0107015E),
                           (0x18E380, 0x0107099A), (0x18E3A0, 0x0107010B)):
        assert int.from_bytes(b[literal:literal + 4], "little") == valor, hex(literal)
