"""E25-18 — modelo de referencia (offline) del plan de exposición electrónica de todo el rango.

Una sola fórmula: la del productor nativo `0x4383fa40` (ejecutado, no reimplementado, vía emulación Unicorn) normalizada
frente al predicado de cuadro extra (`0x43a12ca8`), que suma exactamente un VTS (verificado en tests). Con `svd' = 0` y
VTS inicial = VTS el plan coincide con C3-B (`r5 = VTS - líneas`); fuera de ese caso se exige una capacidad no demostrada
físicamente y, sin ella, la salida es un `Rechazo` (nunca un `r5` negativo, saturado o truncado).
No describe comportamiento del IMX210.
"""
from __future__ import annotations

import math
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/e25_16"))
sys.path.insert(0, str(ROOT / "scripts/e25_17"))

VTS_MEDIDO = 4219          # T046/T047: referencia efectiva dentro de un cuadro
PERIODO_Q8 = 3891          # período de línea (15,2 µs) del modo 24 MP
SHD_MAX, SVD_MAX, SPL_MAX, VTS_MAX = 0x3FFF, 0xFFF, 0xFFF, 0xFFFF   # S202: bits que SetExposure conserva; u16 de record+0xd8
_EMUS: dict[int, object] = {}


@dataclass(frozen=True)
class Capacidades:
    """Lo no demostrado físicamente; por defecto, todo falso (E25-19 lo decide)."""
    vts_dinamico: bool = False        # el sensor/DFE aplica VTS ≠ 4219 por cuadro
    svd_multicuadro: bool = False     # svd > 0 integra de forma continua
    record_coherente: bool = False    # existe un 2.º punto que normaliza record+0x68/+0xd8..+0xdc para el planificador


@dataclass(frozen=True)
class Plan:
    tv: int
    lineas: int
    shd: int
    svd: int
    spl: int
    sint: int
    shutmode: int
    vts_inicial: int
    vts_intermedio: int
    vts_final: int
    ruta: str                              # "rapida" | "larga"
    requiere: tuple[str, ...]
    exposicion_us: float                   # modelo (svd*VTS + inicial - shd) * período
    nativo: dict = field(default_factory=dict)

    @property
    def lineas_totales(self) -> int:
        return self.svd * self.vts_intermedio + self.vts_inicial


@dataclass(frozen=True)
class Rechazo:
    motivo: str
    candidato: Plan | None = None


def tv_code(t: float) -> int:
    return round(0x1000 + 256.0 * math.log2(1.0 / t))


def _emu(pred: int):
    if pred not in _EMUS:
        from emu_core import BASE, FW, Emu  # type: ignore[import-not-found]
        e = Emu()
        e.mu.mem_write(0x4355FD4C, FW.read_bytes()[0x4355FD4C - BASE:0x4355FD4C - BASE + 0x40])   # división/resto reales
        _EMUS[pred] = e
    return _EMUS[pred]


def productor(tv: int, periodo_q8: int, vts: int, suelo: int, factor: int, pred: int) -> dict:
    """Ejecuta el `0x4383fa40` real sobre un scratch y devuelve los campos de salida de `record`."""
    from emular_productor import PREDICADO, REC, SET  # type: ignore[import-not-found]
    e = _emu(pred)
    mu = e.mu
    mu.mem_write(PREDICADO, struct.pack("<HH", 0x2000 | pred, 0x4770))
    mu.mem_write(REC, b"\0" * 0x200)
    mu.mem_write(SET, b"\0" * 0x600)
    mu.mem_write(REC + 0xC, struct.pack("<H", periodo_q8))
    mu.mem_write(REC + 0x1C, struct.pack("<H", suelo))
    mu.mem_write(REC + 0x20, struct.pack("<H", vts))
    mu.mem_write(REC + 0xF6, struct.pack("<H", tv))
    mu.mem_write(SET + 0x4B8, bytes([factor]))
    e.call(0x4383FA40, REC, SET)
    r = e.read(REC, 0x120)
    u16 = lambda o: struct.unpack_from("<H", r, o)[0]
    return {"lineas": struct.unpack_from("<I", r, 0xF0)[0], "shd": struct.unpack_from("<I", r, 0x64)[0], "svd": u16(0x68),
            "spl": u16(0x6A), "sint": r[0x6C], "shutmode": r[0x6D], "d8": u16(0xD8), "da": u16(0xDA), "dc": u16(0xDC)}


def normalizar(nat: dict, vts: int, pred: int) -> dict | None:
    """Quita el cuadro previo del predicado: shd -= VTS, svd -= 1. None si el plan nativo no lo admite."""
    if pred == 0:
        return dict(nat)
    if pred != 1 or nat["svd"] < 1 or nat["shd"] < vts:
        return None
    return {**nat, "shd": nat["shd"] - vts, "svd": nat["svd"] - 1}


def c3b_r5(lineas: int, vts: int = VTS_MEDIDO, suelo: int = 1) -> int:
    """Diseño A previo: r5 = VTS - líneas. Solo válido dentro de un cuadro."""
    r5 = vts - lineas
    if r5 < max(suelo, 2):
        raise ValueError(f"C3-B no representa {lineas} líneas con VTS {vts} (r5={r5})")
    return r5


def planificar(tv: int, *, periodo_q8: int = PERIODO_Q8, vts: int = VTS_MEDIDO, suelo: int = 1, factor: int = 1, pred: int = 1,
               modo: str = "foto", caps: Capacidades | None = None, bulb: bool = False) -> Plan | Rechazo:
    caps = caps or Capacidades()
    if bulb:
        return Rechazo("BULB: sin Tv; fin electrónico y emisor de 0x8000 no demostrados (E25-18 §7)")
    if modo != "foto":
        return Rechazo(f"modo '{modo}': solo captura fija; Live View y vídeo no se tocan")
    if periodo_q8 != PERIODO_Q8 or vts != VTS_MEDIDO:
        return Rechazo(f"período {periodo_q8} / VTS {vts} distintos de los medidos ({PERIODO_Q8}/{VTS_MEDIDO})")
    if pred not in (0, 1):
        return Rechazo(f"predicado {pred} fuera de {{0,1}}")
    nat = productor(tv, periodo_q8, vts, suelo, factor, pred)
    pl = normalizar(nat, vts, pred)
    if pl is None:
        return Rechazo("plan nativo incompatible con la normalización del predicado", None)
    if not (max(suelo, 1) <= pl["shd"] <= SHD_MAX) or pl["svd"] > SVD_MAX or pl["spl"] > SPL_MAX:
        return Rechazo(f"fuera de rango de registro (shd={pl['shd']}, svd={pl['svd']}, spl={pl['spl']})")
    total = pl["lineas"] + pl["shd"]                     # = svd*VTS + d8
    inicial = total - pl["svd"] * vts
    interm = vts if pl["svd"] else total
    if inicial > VTS_MAX or not 0 < inicial:
        return Rechazo(f"VTS inicial {inicial} no cabe en u16")
    req: tuple[str, ...] = ()
    if inicial != vts:
        req += ("vts_dinamico",)
    if pl["svd"]:
        req += ("svd_multicuadro", "vts_dinamico", "record_coherente")
    req = tuple(dict.fromkeys(req))
    plan = Plan(tv, pl["lineas"], pl["shd"], pl["svd"], pl["spl"], pl["sint"], pl["shutmode"], inicial, interm, interm,
                "larga" if req else "rapida", req, (pl["svd"] * interm + inicial - pl["shd"]) * periodo_q8 / 256, nat)
    if plan.shutmode != 0:
        return Rechazo(f"ShutMode nativo {plan.shutmode} ≠ 0: no hay variante validada", plan)
    faltan = [c for c in req if not getattr(caps, c)]
    if faltan:
        return Rechazo("capacidad no demostrada físicamente: " + ", ".join(faltan), plan)
    return plan
