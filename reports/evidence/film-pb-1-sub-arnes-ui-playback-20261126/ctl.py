#!/usr/bin/env python3
"""Cliente mínimo del arnés live (scripts/gui/harness/live.py) para las pruebas de vista de reproducción.

Copiado de reports/evidence/film-pb-1-sub-arnes-galeria-20261126/galeria.py (mismo autor de la
sesión anterior) y ampliado con `espera`, `esperafotograma` y `secuencia` para no depender del navegador.

Uso (VM ya arrancada en --puerto P, por defecto 8633):
  ctl.py estado                          → texto de /estado
  ctl.py esperafotograma [tmo]           → espera a que haya al menos un fotograma
  ctl.py tecla reproduccion [v]          → POST /tecla (mapa TECLAS de live.py)
  ctl.py teclas "abajo abajo intro"      → varias teclas, 1 s entre pulsación y suelta
  ctl.py linea "E VERB=1"                → POST /linea (línea cruda al invitado)
  ctl.py captura salida.png [tmo]        → primer fotograma del flujo SSE /eventos
  ctl.py refrescar                       → POST /refrescar
  ctl.py espera N                        → duerme N segundos
"""
import base64
import json
import sys
import time
import urllib.request

P = "8633"


def base() -> str:
    return f"http://127.0.0.1:{P}"


def estado() -> str:
    return json.load(urllib.request.urlopen(base() + "/estado", timeout=5))["texto"]


def post(ruta: str, cuerpo: bytes = b"") -> bytes:
    r = urllib.request.Request(base() + ruta, data=cuerpo, method="POST")
    return urllib.request.urlopen(r, timeout=60).read()


def tecla(k: str, v: int = 1, i: int = 0) -> None:
    post("/tecla", json.dumps({"k": k, "v": v, "i": i}).encode())


def captura(destino: str, tmo: float = 40.0) -> int:
    """Primer `data:` del flujo SSE /eventos (base64 PNG) → destino. Devuelve los bytes escritos."""
    r = urllib.request.urlopen(base() + "/eventos", timeout=tmo)
    t0 = time.time()
    while time.time() - t0 < tmo:
        ln = r.readline()
        if ln.startswith(b"data: "):
            png = base64.b64decode(ln[6:].strip())
            with open(destino, "wb") as f:
                f.write(png)
            return len(png)
    return 0


def main() -> int:
    global P
    if len(sys.argv) > 1 and sys.argv[1].startswith("--puerto="):
        P = sys.argv[1].split("=", 1)[1]
        del sys.argv[1]
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "estado":
        print(estado())
    elif cmd == "esperafotograma":
        tmo = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0
        t0 = time.time()
        while time.time() - t0 < tmo:
            e = estado()
            if "fotogramas" in e and not e.rstrip().endswith("pantalla…"):
                print(e)
                return 0
            time.sleep(3)
        print("tiempo agotado: " + estado())
        return 1
    elif cmd == "tecla":
        v = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        tecla(sys.argv[2], v)
        print("ok " + sys.argv[2])
    elif cmd == "teclas":
        for nombre in sys.argv[2].split():
            nomb = nombre.split(":")[0]
            tecla(nomb, 1)
            time.sleep(1.0)
            tecla(nomb, 0)
            time.sleep(1.0)
            print("ok " + nomb)
    elif cmd == "linea":
        post("/linea", sys.argv[2].encode())
        print("ok")
    elif cmd == "captura":
        n = captura(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 40.0)
        print(f"{n} B -> {sys.argv[2]}")
    elif cmd == "refrescar":
        post("/refrescar")
        print("ok")
    elif cmd == "espera":
        time.sleep(float(sys.argv[2]))
        print("ok")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
