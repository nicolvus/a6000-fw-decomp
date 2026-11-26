#!/usr/bin/env python3
"""Ciclo de arranque en vivo con marcas de tiempo (evidencia del informe §2–§3).

uso: ciclo_live.py PERFIL PUERTO [acción …]
  acciones:  frames           espera a la primera pantalla (tope 400 s) y anota el tiempo
             linea:TEXTO      POST /linea con TEXTO (p. ej. «E TRACEFN2=5bad00»)
             espera:SEG       duerme SEG s
             salir            POST /salir (guarda estado) y espera a que live.py termine
             guardar          POST /guardar
Imprime «t=SS.SS evento detalle» (t desde que se lanzó live.py) y devuelve 0 si terminó bien.
Variables: ESTABLE_WORK (DIR_TRABAJO), SHIMEXTRA, TRACELIB, TRACEFN2… (las del arnés) y SENAL=kill para
matar live.py sin guardar al acabar. Pensado para lanzarse desde scripts/gui/harness con «live.py» intacto.
"""
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
HARNESS = AQUI.parents[3] / "scripts/gui/harness"
if not HARNESS.is_dir():                      # copia dentro de reports/: se busca el repo hacia arriba
    p = AQUI
    while p != p.parent and not (p / "scripts/gui/harness/live.py").exists():
        p = p.parent
    HARNESS = p / "scripts/gui/harness"
W = Path(os.environ.get("ESTABLE_WORK") or HARNESS.parents[2] / "analysis/gui/g22/harness")


def t0f(inicio: float) -> str:
    return f"t={time.time() - inicio:6.2f}"


def estado(puerto: int) -> dict:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{puerto}/estado", timeout=4) as r:
            return json.load(r)
    except (OSError, ValueError):
        return {}


def post(puerto: int, ruta: str, cuerpo: bytes = b"") -> str:
    req = urllib.request.Request(f"http://127.0.0.1:{puerto}{ruta}", data=cuerpo, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode(errors="replace")[:200]
    except (OSError, urllib.error.HTTPError) as e:
        return f"ERROR {e}"


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    perfil, puerto = sys.argv[1], int(sys.argv[2])
    pd = W / "live" / perfil
    pd.mkdir(parents=True, exist_ok=True)
    # se lanza por estable.sh (el comando que entrega el informe), no por live.py directamente
    cmd = ["sh", str(HARNESS / "estable.sh"), perfil, "live"]
    ent = {**os.environ, "PUERTO": str(puerto), "ESTABLE_REUSA": "1"}
    inicio = time.time()
    hijo = subprocess.Popen(cmd, env=ent, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print(f"t=  0.00 lanzado live.py perfil={perfil} puerto={puerto} frío={'no' if (pd / 'estado.zst').exists() else 'sí'}", flush=True)
    rc = 0
    try:
        for acc in sys.argv[3:]:
            tipo, _, arg = acc.partition(":")
            if tipo == "frames":
                while time.time() - inicio < 460:
                    e = estado(puerto)
                    if e.get("fotogramas"):
                        print(f"{t0f(inicio)} primera_pantalla fotogramas={e['fotogramas']} texto={e.get('texto', '')!r}", flush=True)
                        break
                    time.sleep(1)
                else:
                    print(f"{t0f(inicio)} SIN_PANTALLA tras 460 s", flush=True); rc = 1
            elif tipo == "linea":
                print(f"{t0f(inicio)} linea {arg!r} -> {post(puerto, '/linea', arg.encode())}", flush=True)
            elif tipo == "espera":
                time.sleep(float(arg))
            elif tipo == "guardar":
                print(f"{t0f(inicio)} guardar -> {post(puerto, '/guardar')}", flush=True)
            elif tipo == "salir":
                print(f"{t0f(inicio)} salir -> {post(puerto, '/salir')}", flush=True)
                try:
                    hijo.wait(timeout=180)
                except subprocess.TimeoutExpired:
                    print(f"{t0f(inicio)} live.py no terminó en 180 s", flush=True)
            elif tipo == "estado":
                e = estado(puerto)
                print(f"{t0f(inicio)} estado fotogramas={e.get('fotogramas')} texto={e.get('texto', '')!r}", flush=True)
    finally:
        if hijo.poll() is None:
            if os.environ.get("SENAL") == "kill":
                hijo.send_signal(signal.SIGKILL); print(f"{t0f(inicio)} live.py muerto a la fuerza", flush=True)
            else:
                hijo.send_signal(signal.SIGTERM)
            try:
                hijo.wait(timeout=120)
            except subprocess.TimeoutExpired:
                hijo.kill()
        print(f"{t0f(inicio)} fin live.py rc={hijo.returncode}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
