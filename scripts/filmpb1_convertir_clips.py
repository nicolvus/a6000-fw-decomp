#!/usr/bin/env python3
"""Convierte los clips de una carpeta a la cadencia de la cámara y verifica cada uno.

Para cada .MP4 de ENTRADA escribe en SALIDA el mismo clip con la cadencia declarada
cambiada (ver scripts/mp4_set_framerate.py) y comprueba, fichero a fichero:

- que las cajas que el lector de Sony usa siguen ahí (MSNV, 4 uuid, PROF, USMT, MTDT);
- que el tamaño no cambia (solo se reescriben valores de 32 bits);
- que ffprobe lee la cadencia pedida.

No toca los originales. Uso:

    filmpb1_convertir_clips.py CARPETA_ENTRADA CARPETA_SALIDA --fps 25
    filmpb1_convertir_clips.py CARPETA_ENTRADA CARPETA_SALIDA --dry-run
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

CAJAS = (b"MSNV", b"uuid", b"PROF", b"USMT", b"MTDT")
CONVERSOR = Path(__file__).with_name("mp4_set_framerate.py")


def cajas(datos: bytes) -> dict[str, int]:
    return {c.decode(): datos.count(c) for c in CAJAS}


def fps(ruta: Path) -> str:
    if not shutil.which("ffprobe"):
        return "?"
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=r_frame_rate", "-of", "default=nw=1:nk=1", str(ruta)],
        capture_output=True, text=True, check=False,
    )
    return salida.stdout.strip() or "?"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("entrada", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--fps", type=float, default=25.0)
    ap.add_argument("--dry-run", action="store_true", help="solo lista y comprueba, sin escribir")
    args = ap.parse_args()

    clips = sorted(p for p in args.entrada.iterdir() if p.suffix.lower() == ".mp4")
    if not clips:
        print(f"error: no hay .MP4 en {args.entrada}", file=sys.stderr)
        return 2
    args.salida.mkdir(parents=True, exist_ok=True)

    fallos = 0
    print(f"{'clip':16s} {'tamaño':>10s} {'fps antes':>10s} {'fps después':>11s}  cajas  estado")
    for clip in clips:
        original = clip.read_bytes()
        antes = cajas(original)
        fps_antes = fps(clip)
        faltan = [k for k, n in antes.items() if n == 0]
        if faltan:
            print(f"{clip.name:16s} {len(original):10d} {fps_antes:>10s} {'-':>11s}  faltan {faltan}  NO TOCADO")
            fallos += 1
            continue
        destino = args.salida / f"conv-{clip.name}"
        if args.dry_run:
            print(f"{clip.name:16s} {len(original):10d} {fps_antes:>10s} {'(dry-run)':>11s}  {sum(antes.values()):6d}  listo")
            continue
        r = subprocess.run(
            [sys.executable, str(CONVERSOR), str(clip), str(destino), "--fps", str(args.fps)],
            capture_output=True, text=True, check=False,
        )
        if r.returncode != 0:
            print(f"{clip.name:16s} {len(original):10d} {fps_antes:>10s} {'-':>11s}  error del conversor  FALLO")
            print(r.stderr.strip()[:200], file=sys.stderr)
            fallos += 1
            continue
        despues = cajas(destino.read_bytes())
        fps_despues = fps(destino)
        ok = despues == antes and destino.stat().st_size == len(original) and fps_despues.startswith(f"{args.fps:g}")
        fallos += 0 if ok else 1
        print(f"{clip.name:16s} {len(original):10d} {fps_antes:>10s} {fps_despues:>11s}  {sum(despues.values()):6d}  {'ok' if ok else 'FALLO'}")

    print(f"\n{len(clips) - fallos}/{len(clips)} correctos; salida en {args.salida}")
    return 0 if fallos == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
