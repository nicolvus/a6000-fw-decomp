"""AE de av-cam hacia ObjCamera (cola 0x20002) con una escena de luminancia constante (G22-E, §5.18 de docs/gui/g22-avcam-puente.md).

VERIFICADO (RE de libObj 3.21): el receptor `CAMUSER_CAMLIRO_RCV_THREAD` (`libObj+0xae787c`) pasa los mensajes tipo 6 a `0xadb380`, que los convierte en eventos
`0x3100:0x85xx` para el modelo; los de exposición son `0x2014` (`MSGID_NOTIFY_SHUT_SPEED_EVT 0x8531`, conversor `0x9ac048`) y `0x2023`
(`MSGID_NOTIFY_FNO_EVT 0x8530`, conversor `0x9abe0c`). La disposición de la carga es la de esos conversores (offsets dentro del mensaje, cabecera de 8 B).
shortcut: av-cam real calcula la exposición con el ISP/AE (inexistente en la LIRO VM; su emisor `0x435eb650` solo se alcanza por llamada virtual y no corre);
aquí el AE lo calcula el anfitrión con una luminancia de escena constante (dato de entrada intercambiable) y la unidad de FNO (×100) está sin confirmar;
mejorar cuando av-cam ejecute su AE o se midan las unidades en pantalla.
"""
from __future__ import annotations

import math
import struct
import threading
import time
from dataclasses import dataclass

COLA_OBJCAMERA = 0x20002
CAB = "000000000100000001000300"   # cabecera osal vista en la notificación espontánea 0x1016 de av-cam (origen: cola 0x30001)
TIPO_CAP = 6
ID_VELOCIDAD, ID_F = 0x2014, 0x2023

# serie de 1/3 de paso (num, den)
VELOCIDADES = [(1, d) for d in (4000, 3200, 2500, 2000, 1600, 1250, 1000, 800, 640, 500, 400, 320, 250, 200, 160, 125, 100, 80, 60, 50, 40, 30, 25, 20, 15, 13, 10, 8, 6, 5, 4)] \
    + [(n, 10) for n in (3, 4, 5, 6, 8)] + [(10, 10), (13, 10), (16, 10), (2, 1), (25, 10), (32, 10), (4, 1), (5, 1), (6, 1), (8, 1), (10, 1), (13, 1), (15, 1), (20, 1), (25, 1), (30, 1)]
ISOS = (100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800, 16000, 25600)


def _cab(id_: int, largo: int) -> bytearray:
    m = bytearray(largo)
    struct.pack_into("<BBHI", m, 0, TIPO_CAP, 0, id_, 0)   # notificación espontánea: seq 0 (sin bit de respuesta)
    return m


def msg_velocidad(num: int, den: int, minimo: tuple[int, int], maximo: tuple[int, int], valido: bool = True, grados: int = 1) -> bytes:
    """0x2014 → PARAMID_SHUT_SPEED_NUMER/DENOM (0x951c/d), _MIN_ (0x95b8/9), _MAX_ (0x95ba/b), SHUT_DATA_VALID 0x95bc, SHUT_SPEED_DEGREE 0x9871 (mínimo 1: con 0 `PreTypeCheck` rechaza el evento entero, medido en el perfil p1)."""
    m = _cab(ID_VELOCIDAD, 0x23)
    struct.pack_into("<H", m, 0x08, num)
    struct.pack_into("<I", m, 0x0C, den)
    struct.pack_into("<H", m, 0x10, minimo[0])
    struct.pack_into("<I", m, 0x14, minimo[1])
    struct.pack_into("<H", m, 0x18, maximo[0])
    struct.pack_into("<I", m, 0x1C, maximo[1])
    m[0x20] = int(valido)
    struct.pack_into("<H", m, 0x21, grados)
    return bytes(m)


def msg_f(fno: int, actual_min: int, actual_max: int, fmin: int, fmax: int, valido: bool = True) -> bytes:
    """0x2023 → PARAMID_FNO 0x951b (y FNO_DISP_OPTION 0x9749: 0 = barra), FNO_CURRENT_MIN/MAX 0x9787/8, FNO_MIN/MAX 0x95b5/6, FNO_DATA_VALID 0x95b7."""
    m = _cab(ID_F, 0x13)
    struct.pack_into("<HHHHH", m, 0x08, fno, actual_min, actual_max, fmin, fmax)
    m[0x12] = int(valido)
    return bytes(m)


@dataclass(frozen=True)
class Escena:
    """Dato de entrada del AE: EV a ISO 100 de la escena (12 ≈ exterior nublado/ventana luminosa; 6-7 ≈ interior)."""
    ev100: float = 12.0


@dataclass(frozen=True)
class Programa:
    t: float
    num: int
    den: int
    f: int      # F×100
    iso: int


def programa(escena: Escena, iso: int | None, ev_comp: float, f: int = 350, objetivo_min: float = 1 / 60) -> Programa:
    """Programa P: abertura fija (f/3,5 de un zoom estándar), tiempo = N²·2^comp / (2^EV100·ISO/100) al 1/3 de paso; ISO automático (100…6400) si `iso` es None."""
    n2 = (f / 100) ** 2

    def t_de(i: int) -> float:
        return n2 * 2 ** ev_comp / (2 ** escena.ev100 * i / 100)
    i = iso or 100
    if iso is None:
        for i in ISOS[:19]:
            if t_de(i) <= objetivo_min:
                break
    t = t_de(i)
    num, den = min(VELOCIDADES, key=lambda v: abs(math.log2(v[0] / v[1]) - math.log2(t)))
    return Programa(num / den, num, den, f, i)


class Emisor:
    """Envía a ObjCamera, cada `periodo` s, el AE de la escena: lo que el AE de av-cam notificaría con el live view activo."""

    def __init__(self, enviar, escena: Escena | None = None, periodo: float = 1.0) -> None:
        self.enviar, self.escena, self.periodo = enviar, escena or Escena(), periodo
        self.iso: int | None = None
        self.ev_comp = 0.0
        self.f = 350
        self.activo = False
        self._hilo: threading.Thread | None = None

    def arranca(self) -> None:
        if not self._hilo:
            self.activo = True
            self._hilo = threading.Thread(target=self._bucle, daemon=True)
            self._hilo.start()

    def mensajes(self) -> list[bytes]:
        p = programa(self.escena, self.iso, self.ev_comp, self.f)
        return [msg_velocidad(p.num, p.den, (1, 4000), (30, 1)), msg_f(p.f, p.f, 2200, p.f, 2200)]

    def emite(self) -> None:
        for m in self.mensajes():
            self.enviar(f"Q {COLA_OBJCAMERA:x} {CAB} {m.hex()}\n".encode())

    def _bucle(self) -> None:
        while self.activo:
            self.emite()
            time.sleep(self.periodo)
