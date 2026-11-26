"""Selección del ojo objetivo, suavizado y decisión de cuándo mover el punto de AF.

El punto de AF de la cámara es discreto y cada ``setTouchAFPosition`` puede relanzar
un ciclo de enfoque, así que no se manda un punto por cuadro: se manda cuando el ojo
se ha movido más de ``min_move`` (banda muerta) y como mucho ``max_hz`` veces por
segundo. Es lo mismo que hace el Eye AF de Sony: seguir el ojo sin reenfocar de más.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AfCommand:
    x: float
    y: float
    reason: str  # "move" | "cancel"


@dataclass
class _Target:
    x: float
    y: float
    side: str
    score: float
    face_area: float


def _as_target(eye) -> _Target:
    box = getattr(eye, "face_box", None) or (0.0, 0.0, 0.0, 0.0)
    area = float(box[2]) * float(box[3])
    return _Target(float(eye.x), float(eye.y), getattr(eye, "side", "unknown"), float(eye.confidence), area)


class EyeTracker:
    def __init__(
        self,
        min_move: float = 0.01,
        max_hz: float = 8.0,
        smooth: float = 0.4,
        lost_after: float = 1.5,
        switch_margin: float = 0.12,
        jump: float = 0.35,
    ) -> None:
        self.min_move = min_move
        self.period = 1.0 / max_hz if max_hz > 0 else 0.0
        self.smooth = smooth
        self.lost_after = lost_after
        self.switch_margin = switch_margin
        self.jump = jump
        self._pos: tuple[float, float] | None = None       # posición suavizada actual
        self._sent: tuple[float, float] | None = None      # última posición enviada
        self._sent_t = 0.0
        self._seen_t: float | None = None
        self._cancelled = True

    # -- interno ------------------------------------------------------------
    def _pick(self, targets: list[_Target]) -> tuple[_Target, bool]:
        """Devuelve el objetivo y si es un sujeto nuevo (hay que saltar sin suavizar)."""
        if self._pos is None:
            return max(targets, key=lambda t: t.face_area), True
        px, py = self._pos
        near = min(targets, key=lambda t: (t.x - px) ** 2 + (t.y - py) ** 2)
        far_better = max(targets, key=lambda t: t.face_area)
        # cambia de cara sólo si la otra es claramente mayor (evita saltar entre sujetos)
        if far_better is not near and far_better.face_area > near.face_area * (1 + self.switch_margin):
            return far_better, True
        return near, False

    # -- API ----------------------------------------------------------------
    def update(self, eyes: list, now: float) -> AfCommand | None:
        """``eyes``: candidatos del detector; ``now``: segundos monótonos."""
        if not eyes:
            if not self._cancelled and self._seen_t is not None and now - self._seen_t >= self.lost_after:
                self._cancelled = True
                self._sent = None
                self._pos = None
                return AfCommand(0.0, 0.0, "cancel")
            return None

        self._seen_t = now
        self._cancelled = False
        target, switched = self._pick([_as_target(e) for e in eyes])

        prev = self._pos
        salto = prev is None or switched
        if not salto and prev is not None:
            salto = (target.x - prev[0]) ** 2 + (target.y - prev[1]) ** 2 > self.jump ** 2
        if prev is None or salto:
            pos = (target.x, target.y)  # sujeto nuevo: salto directo, sin barrido
        else:
            a = self.smooth
            pos = (prev[0] + a * (target.x - prev[0]), prev[1] + a * (target.y - prev[1]))
        self._pos = pos

        sent = self._sent
        if sent is not None:
            if now - self._sent_t < self.period:
                return None
            dx, dy = pos[0] - sent[0], pos[1] - sent[1]
            if dx * dx + dy * dy < self.min_move * self.min_move:
                return None

        self._sent = pos
        self._sent_t = now
        return AfCommand(pos[0], pos[1], "move")

    @property
    def position(self) -> tuple[float, float] | None:
        return self._pos
