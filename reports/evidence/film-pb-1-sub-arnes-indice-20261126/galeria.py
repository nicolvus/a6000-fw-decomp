#!/usr/bin/env python3
"""Cliente mínimo del arnés live (scripts/gui/harness/live.py) para llevar la UI a la galería sin navegador.

Uso (con la VM ya arrancada en --puerto P):
  galeria.py estado                       → texto de /estado
  galeria.py tecla reproduccion           → POST /tecla (mapa de TECLAS de live.py)
  galeria.py tecla reproduccion 3 7       → varias pulsaciones separadas por `espera` s
  galeria.py linea "E TRACEMAX=32"        → POST /linea (línea cruda al invitado)
  galeria.py captura salida.png           → primer fotograma del flujo SSE /eventos
  galeria.py refrescar                    → POST /refrescar (pide repintado)
"""
import base64
import json
import sys
import time
import urllib.request

P = "8600"


def base() -> str:
    return f"http://127.0.0.1:{P}"


def estado() -> str:
    return json.load(urllib.request.urlopen(base() + "/estado", timeout=5))["texto"]


def post(ruta: str, cuerpo: bytes = b"") -> bytes:
    r = urllib.request.Request(base() + ruta, data=cuerpo, method="POST")
    return urllib.request.urlopen(r, timeout=30).read()


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
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "estado":
        print(estado())
    elif cmd == "tecla":
        for a in (sys.argv[3:] or [""]):
            tecla(sys.argv[2], 1, int(a) if a else 0)
            time.sleep(2)
            print(estado())
    elif cmd == "linea":
        post("/linea", sys.argv[2].encode())
        print("ok")
    elif cmd == "captura":
        n = captura(sys.argv[2])
        print(f"{n} B -> {sys.argv[2]}")
    elif cmd == "refrescar":
        post("/refrescar")
        print("ok")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].startswith("--puerto="):
        P = sys.argv[1].split("=", 1)[1]
        del sys.argv[1]
    sys.exit(main())
