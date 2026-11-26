"""Control del punto de AF: banda muerta, límite de frecuencia, pérdida y cambio de cara."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "eye-af"))

from eyeaf.tracker import EyeTracker


@dataclass
class Eye:
    x: float
    y: float
    confidence: float = 0.9
    side: str = "right"
    face_box: tuple = (0.3, 0.2, 0.2, 0.2)


def test_primera_deteccion_mueve_el_punto():
    t = EyeTracker()
    cmd = t.update([Eye(0.5, 0.4)], now=0.0)
    assert cmd is not None and cmd.reason == "move"
    assert (round(cmd.x, 3), round(cmd.y, 3)) == (0.5, 0.4)


def test_banda_muerta_y_limite_de_frecuencia():
    t = EyeTracker(min_move=0.05, max_hz=10.0, smooth=1.0)
    assert t.update([Eye(0.5, 0.5)], now=0.0) is not None
    # movimiento pequeño: no se manda
    assert t.update([Eye(0.51, 0.5)], now=0.5) is None
    # movimiento grande pero demasiado pronto: tampoco
    t2 = EyeTracker(min_move=0.01, max_hz=2.0, smooth=1.0)
    assert t2.update([Eye(0.5, 0.5)], now=0.0) is not None
    assert t2.update([Eye(0.9, 0.9)], now=0.1) is None
    assert t2.update([Eye(0.9, 0.9)], now=0.6) is not None


def test_suavizado_acerca_la_posicion():
    t = EyeTracker(min_move=0.0, max_hz=1000.0, smooth=0.5)
    assert t.update([Eye(0.0, 0.0)], now=0.0) is not None
    t.update([Eye(0.2, 0.2)], now=0.01)
    assert t.position == pytest.approx((0.1, 0.1))  # EMA, sin salto


def test_salto_limpio_cuando_el_sujeto_aparece_lejos():
    t = EyeTracker(min_move=0.0, max_hz=1000.0, smooth=0.5, jump=0.35)
    t.update([Eye(0.0, 0.0)], now=0.0)
    cmd = t.update([Eye(0.9, 0.9)], now=0.01)
    assert cmd is not None and cmd.x == 0.9  # un barrido por el encuadre no tiene sentido


def test_cancela_al_perder_el_ojo():
    t = EyeTracker(lost_after=1.0)
    assert t.update([Eye(0.5, 0.5)], now=0.0) is not None
    assert t.update([], now=0.5) is None
    cmd = t.update([], now=1.1)
    assert cmd is not None and cmd.reason == "cancel"
    assert t.update([], now=2.0) is None  # sólo se cancela una vez


def test_prefiere_la_cara_mas_grande_y_cambia_si_es_mucho_mayor():
    t = EyeTracker(switch_margin=0.2)
    grande = Eye(0.2, 0.2, face_box=(0.1, 0.1, 0.3, 0.3))   # área 0.09
    pequena = Eye(0.8, 0.8, face_box=(0.7, 0.7, 0.1, 0.1))  # área 0.01
    cmd = t.update([pequena, grande], now=0.0)
    assert cmd is not None and cmd.x == 0.2
    # la pequeña se acerca un poco: no debe saltar
    cerca = Eye(0.21, 0.21, face_box=(0.1, 0.1, 0.1, 0.1))
    t.update([cerca], now=1.0)
    assert abs(t.position[0] - 0.2) < 0.05
    # aparece una cara mucho mayor: salta a ella
    enorme = Eye(0.9, 0.9, face_box=(0.5, 0.5, 0.8, 0.8))
    cmd = t.update([enorme], now=2.0)
    assert cmd is None or cmd.x > 0.5
