"""Estado de la cámara en el arnés (G22-E): batería 0-100, carga, jack USB y HDMI — modelo del ANFITRIÓN, sin QEMU.

Lo que este módulo NO hace: leer el estado real de la cámara. No hay vía verificada de lectura del jack ni del nivel de batería (no hay
registro de la cámara para eso; la batería que pinta la OSD la produce av-cam por AVQ). Aquí solo se guarda lo que el anfitrión decide y se
traduce a las órdenes del shim (`B <pct>` / `U <0|1>`, puerto LIVE), que es lo que el firmware consume.
"""
from __future__ import annotations

from dataclasses import dataclass

SECCION = "camara"
DEFECTO: dict = {"bateria": 100, "usb": False, "hdmi": False}


def pct(v: object) -> int:
    """Nivel de batería válido (entero 0-100, no bool); ValueError con el mensaje que verá la página."""
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError("camara.bateria debe ser un entero entre 0 y 100")  # noqa: TRY004 - la API devuelve ValueError como error de validación
    if not 0 <= v <= 100:
        raise ValueError("camara.bateria debe estar entre 0 y 100")
    return v


@dataclass(frozen=True)
class Estado:
    """Lo que el anfitrión cree de la cámara. `cargando` se deduce del jack USB, como en la cámara (INFERENCIA, ver el informe)."""

    bateria: int = 100
    usb: bool = False
    hdmi: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "bateria", pct(self.bateria))
        object.__setattr__(self, "usb", bool(self.usb))
        object.__setattr__(self, "hdmi", bool(self.hdmi))

    @property
    def cargando(self) -> bool:
        return self.usb

    def con(self, *, bateria: object = None, usb: object = None, hdmi: object = None) -> Estado:
        """Copia con los campos indicados cambiados (valida igual que el constructor)."""
        return Estado(bateria=self.bateria if bateria is None else bateria,  # type: ignore[arg-type]
                      usb=self.usb if usb is None else usb, hdmi=self.hdmi if hdmi is None else hdmi)  # type: ignore[arg-type]

    def ordenes(self) -> list[bytes]:
        """Órdenes del protocolo LIVE que dejan el invitado en este estado (batería primero: no dependen entre sí)."""
        return [f"B {self.bateria}\n".encode(), b"U 1\n" if self.usb else b"U 0\n"]

    def a_dict(self) -> dict:
        return {"bateria": self.bateria, "usb": self.usb, "hdmi": self.hdmi, "cargando": self.cargando}


def desde_config(cfg: dict | None) -> Estado:
    """Estado guardado en la sección `camara` del config del configurador; sin sección, los valores por defecto."""
    d = {**DEFECTO, **((cfg or {}).get(SECCION) or {})}
    return Estado(bateria=d["bateria"], usb=d["usb"], hdmi=d["hdmi"])  # type: ignore[arg-type]


def a_config(e: Estado) -> dict:
    """Sección `camara` normalizada para `emu_config.guarda_config`."""
    return {"bateria": e.bateria, "usb": e.usb, "hdmi": e.hdmi}
