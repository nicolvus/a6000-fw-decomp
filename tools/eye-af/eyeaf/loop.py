"""Bucle de Eye AF en tiempo real: cuadro de Live View -> ojo -> punto de AF de la cámara."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .api import CameraError, CameraRemoteAPI, parse_af_result
from .liveview import LiveviewStream
from .tracker import EyeTracker


def to_camera(x: float, y: float, mode: str, width: int = 0, height: int = 0) -> tuple[float, float]:
    """Convierte coordenadas normalizadas (origen arriba-izquierda) al espacio que pide la API.

    La A6000 (orb-server, fw3.21) pide porcentaje del encuadre 0..100 — ver
    analysis/eyeaf/orb_touchaf.md §1.
    """
    if mode == "percent":
        return x * 100.0, y * 100.0
    if mode == "normalized":
        return x, y
    if mode == "centered":
        return x * 2 - 1, y * 2 - 1
    if mode == "pixels":
        return x * width, y * height
    raise ValueError(f"espacio de coordenadas desconocido: {mode}")


@dataclass
class Stats:
    frames: int = 0
    detects: int = 0
    commands: int = 0
    af_ok: int = 0
    af_fail: int = 0
    errors: int = 0
    t0: float = field(default_factory=time.monotonic)
    last_report: float = field(default_factory=time.monotonic)

    @property
    def fps(self) -> float:
        dt = time.monotonic() - self.t0
        return self.frames / dt if dt > 0 else 0.0


class EyeAF:
    def __init__(
        self,
        api: CameraRemoteAPI,
        detector,
        tracker: EyeTracker | None = None,
        coord: str = "percent",
        preview: bool = False,
        record: str | None = None,
        dry_run: bool = False,
        report: float = 1.0,
        on_frame=None,
    ) -> None:
        self.api = api
        self.detector = detector
        self.tracker = tracker or EyeTracker()
        self.coord = coord
        self.preview = preview
        self.record = record
        self.dry_run = dry_run
        self.report_every = report
        self.on_frame = on_frame
        self.stats = Stats()
        self._writer: Any = None

    # -- interno ------------------------------------------------------------
    def _apply(self, cmd, shape) -> None:
        h, w = shape[:2]
        if cmd.reason == "cancel":
            if not self.dry_run:
                try:
                    self.api.cancel_touch_af()
                except CameraError:
                    self.stats.errors += 1
            return
        x, y = to_camera(cmd.x, cmd.y, self.coord, w, h)
        if self.dry_run:
            return
        try:
            res = self.api.set_touch_af(x, y)
            self.stats.commands += 1
            ok = parse_af_result(res)
            self.stats.af_ok += 1 if ok else 0
            self.stats.af_fail += 1 if ok is False else 0
        except CameraError:
            self.stats.errors += 1

    def _draw(self, frame, cmd, eyes):
        import cv2

        h, w = frame.shape[:2]
        for e in eyes:
            cv2.circle(frame, (int(e.x * w), int(e.y * h)), 6, (0, 255, 0), 2)
        if cmd is not None and cmd.reason == "move":
            cv2.drawMarker(frame, (int(cmd.x * w), int(cmd.y * h)), (0, 0, 255),
                           cv2.MARKER_CROSS, 24, 2)
        cv2.putText(frame, f"{self.stats.fps:.1f} fps  af:{self.stats.commands}",
                    (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1, cv2.LINE_AA)
        return frame

    # -- API ----------------------------------------------------------------
    def run_frames(self, frames, max_frames: int | None = None, max_seconds: float | None = None,
                   verbose: bool = True) -> Stats:
        """Procesa un iterable de cuadros BGR (permite probar sin cámara)."""
        import cv2

        t_end = time.monotonic() + max_seconds if max_seconds else None
        for frame in frames:
            if max_frames is not None and self.stats.frames >= max_frames:
                break
            if t_end is not None and time.monotonic() > t_end:
                break
            self.stats.frames += 1
            self.stats.detects += 1
            eyes = self.detector.detect(frame)
            cmd = self.tracker.update(eyes, time.monotonic())
            if cmd is not None:
                self._apply(cmd, frame.shape)
            if self.record:
                if self._writer is None:
                    h, w = frame.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore[attr-defined]
                    self._writer = cv2.VideoWriter(self.record, fourcc, 15, (w, h))
                self._writer.write(frame)
            if self.preview or self.on_frame:
                shown = self._draw(frame.copy(), cmd, eyes)
                if self.on_frame:
                    self.on_frame(shown, cmd, eyes)
                if self.preview:
                    cv2.imshow("Eye AF", shown)
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:
                        break
                    if key == 32 and not self.dry_run:  # barra espaciadora: dispara
                        try:
                            self.api.act_take_picture()
                        except CameraError:
                            self.stats.errors += 1
            if verbose and time.monotonic() - self.stats.last_report >= self.report_every:
                self.stats.last_report = time.monotonic()
                pos = self.tracker.position
                print(f"{self.stats.fps:5.1f} fps  ojos={len(eyes)}  "
                      f"af={self.stats.commands} (ok={self.stats.af_ok} ko={self.stats.af_fail})  "
                      f"errores={self.stats.errors}  "
                      f"punto={'—' if pos is None else f'({pos[0]:.3f},{pos[1]:.3f})'}", flush=True)
        if self._writer is not None:
            self._writer.release()
        if self.preview:
            cv2.destroyAllWindows()
        return self.stats

    def run(self, max_seconds: float | None = None, verbose: bool = True) -> Stats:
        """Arranca Live View en la cámara y sigue el ojo hasta que se pare."""
        url = self.api.start_liveview()
        if verbose:
            print(f"liveview: {url}", flush=True)
        with LiveviewStream(url) as stream:
            try:
                return self.run_frames(stream.frames(), max_seconds=max_seconds, verbose=verbose)
            finally:
                try:
                    self.api.stop_liveview()
                except CameraError:
                    pass
