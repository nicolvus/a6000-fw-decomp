"""E25-24 — selector binario EFCS / Electronic (modelo offline).

La selección reutiliza el ajuste EFCS existente: el modelo 0x2b4 escribe 0 en
`bloque+0x210` (EFCS activado) y el 0x2b5 escribe 1 (EFCS desactivado).  Este módulo
no reinterpreta el campo original: lo usa como selector de modalidad y deriva una
variable de modalidad explícita para el resto del sistema.

    EFCS ON  (campo 0) -> Mode.EFCS        -> segunda cortina mecánica (ruta Sony)
    EFCS OFF (campo 1) -> Mode.ELECTRONIC  -> sin cortinas mecánicas (ruta Silent)

La máquina de estados impide cambiar de modalidad durante una captura y exige una
recuperación explícita tras un error.  No describe hardware ni sustituye una prueba
física.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

EFCS_MODEL_ON = 0x2B4
EFCS_MODEL_OFF = 0x2B5
FIELD_EFCS_ON = 0
FIELD_EFCS_OFF = 1


class Mode(str, Enum):
    EFCS = "efcs"
    ELECTRONIC = "electronic"


class State(str, Enum):
    EFCS_READY = "efcs_ready"
    ELECTRONIC_READY = "electronic_ready"
    CAPTURE_ACTIVE = "capture_active"
    ERROR = "error"
    RECOVERY = "recovery"


class SelectorError(ValueError):
    """Error de selección o de transición."""


class InvalidSelection(SelectorError):
    """Valor de menú/campo fuera del dominio conocido."""


class TransitionRejected(SelectorError):
    """Transición no permitida en el estado actual."""


_READY = {Mode.EFCS: State.EFCS_READY, Mode.ELECTRONIC: State.ELECTRONIC_READY}


def mode_from_model(model: int) -> Mode:
    """Conversor de modelo de menú (0x2b4/0x2b5) a modalidad."""
    if model == EFCS_MODEL_ON:
        return Mode.EFCS
    if model == EFCS_MODEL_OFF:
        return Mode.ELECTRONIC
    raise InvalidSelection(f"modelo de menú no soportado: {model:#x}")


def mode_from_field(value: int) -> Mode:
    """Valor del campo EFCS (+0x210) a modalidad.

    El valor original se conserva: 0 con EFCS activado y 1 con EFCS desactivado
    (T012).  No se invierte ni se reutiliza como ShutMode.
    """
    if value == FIELD_EFCS_ON:
        return Mode.EFCS
    if value == FIELD_EFCS_OFF:
        return Mode.ELECTRONIC
    raise InvalidSelection(f"valor del campo EFCS no soportado: {value:#x}")


def field_from_mode(mode: Mode) -> int:
    """Valor que debe llevar `+0x210` para una modalidad."""
    return FIELD_EFCS_ON if mode is Mode.EFCS else FIELD_EFCS_OFF


def packet_flag(mode: Mode) -> int:
    """Byte que viaja en `pkt[0x0e]` y lee Darwin (0 = mecánica, 1 = sin mecánica)."""
    return 0 if mode is Mode.EFCS else 1


def route_for(mode: Mode) -> str:
    return "efcs_original" if mode is Mode.EFCS else "silent_electronico"


@dataclass(frozen=True)
class CaptureTicket:
    """Modalidad congelada al inicio de una captura."""

    mode: Mode
    packet_flag: int
    route: str


@dataclass
class Selector:
    """Máquina de estados del selector.

    El estado inicial es EFCS_READY, que es también el valor seguro por defecto:
    si un byte de modalidad falta o queda a cero, la ruta original sigue activa.
    """

    mode: Mode = Mode.EFCS
    state: State = field(init=False)
    last_error: str = ""
    _captures: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.state = _READY[self.mode]

    @property
    def capture_active(self) -> bool:
        return self.state is State.CAPTURE_ACTIVE

    @property
    def ready(self) -> bool:
        return self.state in (State.EFCS_READY, State.ELECTRONIC_READY)

    def _require_ready(self) -> None:
        if self.state is State.CAPTURE_ACTIVE:
            raise TransitionRejected("no se cambia de modalidad durante una captura")
        if self.state in (State.ERROR, State.RECOVERY):
            raise TransitionRejected(f"estado {self.state.value}: requiere recuperación")

    def select(self, model: int) -> Mode:
        """Selecciona por modelo de menú.  Idempotente si el valor no cambia."""
        return self.select_mode(mode_from_model(model))

    def select_field(self, value: int) -> Mode:
        """Selecciona por el valor leído del campo EFCS."""
        return self.select_mode(mode_from_field(value))

    def select_mode(self, mode: Mode) -> Mode:
        self._require_ready()
        if mode is self.mode:
            return self.mode
        self.mode = mode
        self.state = _READY[mode]
        return self.mode

    def begin_capture(self) -> CaptureTicket:
        """Congela la modalidad.  Solo desde un estado listo."""
        if not self.ready:
            raise TransitionRejected(f"no se puede capturar en {self.state.value}")
        self.state = State.CAPTURE_ACTIVE
        self._captures += 1
        return CaptureTicket(self.mode, packet_flag(self.mode), route_for(self.mode))

    def end_capture(self) -> None:
        if self.state is not State.CAPTURE_ACTIVE:
            raise TransitionRejected("no hay captura activa")
        self.state = _READY[self.mode]

    def fail(self, reason: str) -> None:
        """Fallo de inicialización, comunicación o estado inesperado."""
        self.last_error = reason
        self.state = State.ERROR

    def recover(self) -> None:
        """Recuperación comprobada: vuelve al estado listo de la última modalidad."""
        if self.state not in (State.ERROR, State.RECOVERY):
            raise TransitionRejected("la recuperación solo aplica desde ERROR/RECOVERY")
        self.state = State.RECOVERY
        self.state = _READY[self.mode]

    def reset(self) -> None:
        """Reinicio: modalidad segura EFCS y estado limpio (no cambia el campo persistido)."""
        self.mode = Mode.EFCS
        self.state = State.EFCS_READY
        self.last_error = ""
        self._captures = 0

    @property
    def captures(self) -> int:
        return self._captures
