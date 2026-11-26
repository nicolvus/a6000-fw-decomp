"""G22-DIAL-FN — dial de modos, Fn y rueda por la ruta real del firmware.

Sin QEMU: comprueba (a) el mensaje exacto que el arnés manda al driver de entrada para cada tecla,
(b) que el dial de modo se apoya en la ruta real (evento del driver + modo que da el firmware) y no
en un número del anfitrión, y (c) que el shim pide ese modo a `CmnViewBigModelUtil::getRecViewFromDial`
en caliente y sigue usando el valor medido en el arranque. Evidencia medida y offsets: docs/gui/g22-dial-fn-rueda.md.
"""
import inspect
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "gui" / "harness"))
import live


def _vm_falsa(monkeypatch):
    """Vm sin QEMU: registra lo que se enviaría al invitado."""
    vm = object.__new__(live.Vm)
    vm.cerrojo_dial, vm.sock, vm.enviados = live.threading.Lock(), None, []
    vm.tecla = lambda k, v, i: vm.enviados.append(("K", k, v, i))
    vm.envia = lambda d: vm.enviados.append(d)
    monkeypatch.setattr(live.time, "sleep", lambda _s: None)
    monkeypatch.setattr(live.threading, "Thread",
                        lambda target, args=(), daemon=None: type("T", (), {"start": lambda self: target(*args)})())
    return vm


def test_mapa_de_teclas_del_dial_fn_y_rueda():
    """T7 §5: clave del driver e índice físico de Fn, rueda, dial superior y dial de modo (medidos en el arnés)."""
    assert live.TECLAS["fn"] == (0x70A1, 0x95)
    assert live.TECLAS["rueda_der"] == (0x10000015, 0x1E5, 1) and live.TECLAS["rueda_izq"] == (0x10000015, 0x1E5, -1)
    assert live.TECLAS["dial_der"] == (0x10000014, 0x1E4, 1) and live.TECLAS["dial_izq"] == (0x10000014, 0x1E4, -1)
    assert live.DIAL_MODO == (0x7025, 0x27)


def test_mensajes_al_driver_de_entrada(monkeypatch):
    """`pulsa` manda {clave, 0, valor, 0, índice} por la línea «K» de live.py (shim: mbx_post_raw a 0x7a0020)."""
    vm = _vm_falsa(monkeypatch)
    live.pulsa(vm, "fn", 1)
    live.pulsa(vm, "rueda_der", 1)
    live.pulsa(vm, "dial_izq", 1)
    live.pulsa(vm, "rueda_der", 0)  # los diales no tienen suelta: v=0 no manda nada
    assert vm.enviados == [("K", 0x70A1, 1, 0x95), ("K", 0x10000015, 1, 0x1E5), ("K", 0x10000014, -1 & 0xFFFFFFFF, 0x1E4)]


def test_el_giro_no_pone_el_modo_desde_python(monkeypatch):
    """El modo lo da el firmware: la reapertura va sin argumento («O view/STLREC») para que el shim lo pida a getRecViewFromDial."""
    vm = _vm_falsa(monkeypatch)
    for _nombre, estado in live.POSICIONES_MODO:
        vm.enviados.clear()
        vm.gira(estado)
        assert vm.enviados == [("K", 0x7025, estado, 0x27), b"O view/ROOT 0\n", b"O view/STLREC\n"], estado


def test_el_atajo_solo_se_usa_si_no_hay_ruta_real(monkeypatch):
    """La fila del giro en la evidencia: el atajo que queda es la REAPERTURA (el evento no repinta el icono), no el modo."""
    fuente = inspect.getsource(live.Vm.gira)
    assert "OPENVIEWDIAL" in fuente and "getRecViewFromDial" in fuente
    assert "shortcut" not in inspect.getsource(live.Vm.reabre_vista)  # la reapertura ya no es un atajo de valor
    # el atajo está declarado donde toca: la reapertura sigue siendo del arnés
    assert "sigue siendo del arnés" in fuente
    vm = _vm_falsa(monkeypatch)
    vm.gira(live.POSICIONES_MODO[1][1])
    assert vm.enviados[1:] == [b"O view/ROOT 0\n", b"O view/STLREC\n"]  # sin número de modo en el camino caliente


def test_shimenv_del_dial():
    env = live.construye_shimenv(True, "")
    v = dict(t.split("=", 1) for t in env.split() if "=" in t)
    assert v["OPENVIEWDIAL"] == "1"                      # modo del firmware en caliente
    assert v["OPENVIEWARG"] == f"{live.VISTA_REC:x}"     # modo medido en el arranque (el dial aún no tiene estado)
    assert v["KEYINIT"] == f"7000001:1:177,7025:{live.DIAL_INICIAL:x}:27"
    assert v["KEYQ"] == "7a0020"


def test_posiciones_del_dial_verificadas():
    """Estados con icono comprobado; 3 = P (getExposureMode en viewUnified2+0x18e594 → 0x18e852 `movs r4,#0x15`).

    G22-DIAL-POS añade película (8) y SCN (0xb), medidos con OPENVIEWDIAL y captura; MR (1) y panorámica (0x10)
    siguen fuera porque dan la misma pantalla byte a byte y sin indicador de modo (tests/test_g22_dial_pos.py).
    """
    assert dict(live.POSICIONES_MODO) == {"Auto": 2, "P": 3, "A": 4, "S": 5, "M": 6, "Película": 8, "SCN": 0xB}
    assert live.DIAL_INICIAL == 3 == live.VISTA_REC


def test_shim_pide_el_modo_al_firmware_en_caliente():
    """El shim resuelve CmnViewBigModelUtil::getInstance/getRecViewFromDial y sólo lo usa en la apertura en caliente."""
    fuente = (RAIZ / "scripts" / "gui" / "harness" / "shim" / "sonyshim.c").read_text()
    assert '_ZN19CmnViewBigModelUtil18getRecViewFromDialEv' in fuente
    assert '_ZN19CmnViewBigModelUtil11getInstanceEv' in fuente
    assert 'getenv("OPENVIEWDIAL")' in fuente
    # el arranque sigue con OPENVIEWARG (a los OPENVIEWAT s el dial no tiene estado)
    arranque = fuente[fuente.index("static void *openviewer"):fuente.index("static void *injector")]
    assert 'getenv("OPENVIEWDIAL")' not in arranque and 'getenv("OPENVIEWARG")' in arranque
    caliente = fuente[fuente.index("static void *openhot"):fuente.index("static void *live_keys")]
    assert "modo_caliente" in caliente


@pytest.mark.skipif(not (RAIZ / "firmware/extracted/fw321").exists(), reason="firmware 3.21 extraído no disponible")
def test_instruccion_del_mapa_de_modo_en_getexposuremode():
    """Bytes: 3 → P es `0x18e594 cmp r4,#3` / `0x18e596 beq.w 0x18e852` / `0x18e852 movs r4,#0x15` (viewUnified2 3.21)."""
    lib = RAIZ / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/viewUnified2.so"
    b = lib.read_bytes()
    assert b[0x18E594:0x18E598].hex() == "032c0cf0" or b[0x18E594:0x18E596].hex() == "032c"
    assert b[0x18E852:0x18E854].hex() == "1524"
