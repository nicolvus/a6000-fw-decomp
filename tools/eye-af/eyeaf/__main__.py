"""CLI: ``python -m eyeaf --host 192.168.1.29``.

Eye AF en tiempo real sobre el Camera Remote API de la cámara (app Smart Remote Control).
``--check`` diagnostica la cámara sin arrancar Live View; ``--dry-run`` ejecuta la visión
sin escribir el punto de AF.
"""
from __future__ import annotations

import argparse
import sys

from .api import CameraError, CameraRemoteAPI
from .loop import EyeAF
from .tracker import EyeTracker


def check(api: CameraRemoteAPI) -> int:
    try:
        print("versiones:", ", ".join(api.versions()))
        types = api.method_types()
        for name in ("startLiveview", "setTouchAFPosition", "getTouchAFPosition",
                     "cancelTouchAFPosition", "setFocusMode", "getEvent", "actTakePicture"):
            print(f"{name:24s} {'sí' if name in types else 'NO'} {types.get(name)}")
        available = api.available_api_list()
        print("\ndisponibles ahora:", ", ".join(available))
        ok = "setTouchAFPosition" in available or "setTouchAFPosition" in types
        return 0 if ok else 2
    except CameraError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="eyeaf", description="Eye AF en tiempo real para la Sony A6000")
    p.add_argument("--host", required=True, help="IP de la cámara (app Smart Remote Control)")
    p.add_argument("--port", type=int, default=None, help="puerto de la API (por defecto: autodetecta 8080/10000)")
    p.add_argument("--check", action="store_true", help="diagnóstico de la API y salir")
    p.add_argument("--dry-run", action="store_true", help="detectar sin mover el punto de AF")
    p.add_argument("--preview", action="store_true", help="ventana con el seguimiento (ESC sale, ESPACIO dispara)")
    p.add_argument("--record", help="graba el seguimiento a un .mp4")
    p.add_argument("--max-seconds", type=float)
    p.add_argument("--focus-mode", help="p. ej. AF-C para seguimiento continuo")
    p.add_argument("--coord", default="percent", choices=["percent", "normalized", "centered", "pixels"],
                   help="espacio de coordenadas de setTouchAFPosition (A6000: 0..100 porcentaje)")
    p.add_argument("--min-move", type=float, default=0.01, help="banda muerta en unidades normalizadas")
    p.add_argument("--max-hz", type=float, default=3.0, help="máximo de órdenes de AF por segundo")
    p.add_argument("--smooth", type=float, default=0.4, help="suavizado EMA (1 = sin suavizado)")
    p.add_argument("--lost-after", type=float, default=1.5, help="s tras perder el ojo para cancelar el toque")
    p.add_argument("--model", help="ruta al modelo del detector (si aplica)")
    args = p.parse_args(argv)

    api = CameraRemoteAPI(args.host, args.port)
    if args.check:
        return check(api)

    from .detector import EyeDetector

    detector = EyeDetector(model_path=args.model)
    tracker = EyeTracker(min_move=args.min_move, max_hz=args.max_hz,
                         smooth=args.smooth, lost_after=args.lost_after)
    if args.focus_mode:
        try:
            api.set_focus_mode(args.focus_mode)
            print(f"modo de enfoque: {args.focus_mode}")
        except CameraError as e:
            print(f"aviso: no se pudo fijar el modo de enfoque ({e})", file=sys.stderr)

    app = EyeAF(api, detector, tracker, coord=args.coord, preview=args.preview,
                record=args.record, dry_run=args.dry_run)
    try:
        stats = app.run(max_seconds=args.max_seconds)
    except KeyboardInterrupt:
        return 0
    except CameraError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"\ncuadros={stats.frames} órdenes={stats.commands} errores={stats.errors} "
          f"media={stats.fps:.1f} fps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
