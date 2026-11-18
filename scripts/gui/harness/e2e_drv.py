#!/usr/bin/env python3
"""Conductor de pruebas E2E sobre `live.py` (G75 T49): pulsa teclas y guarda capturas de la pantalla de la VM.

uso: e2e_drv.py PUERTO PASO...   con PASO = tecla[*n] (arriba, abajo, intro, menu, dial_der…) | png=RUTA | esp=SEGUNDOS | linea=TEXTO | env=K=V
  Cada tecla se pulsa y suelta y se espera KEYWAIT s (0,6 por defecto; la VM con trazas va lenta). `png=` guarda el último fotograma recibido por /eventos (SSE).
  `linea=` envía una línea cruda al shim («E TRACEFN=…», «Z …»); `env=K=V` es atajo de «E K=V».
"""
import base64
import http.client
import json
import os
import sys
import time


def post(puerto: int, ruta: str, cuerpo: bytes) -> None:
    c = http.client.HTTPConnection("127.0.0.1", puerto, timeout=10)
    c.request("POST", ruta, cuerpo)
    c.getresponse().read()
    c.close()


def captura(puerto: int, destino: str, espera: float = 1.5) -> None:
    """Lee /eventos hasta 3 s tras `espera` s y guarda el último fotograma (la pantalla puede no cambiar: se pide un refresco)."""
    post(puerto, "/refrescar", b"{}")
    c = http.client.HTTPConnection("127.0.0.1", puerto, timeout=20)
    c.request("GET", "/eventos")
    r = c.getresponse()
    ultimo, t0 = None, time.time()
    while time.time() - t0 < espera + 3:
        ln = r.fp.readline()
        if ln.startswith(b"data: "):
            ultimo = base64.b64decode(ln[6:].strip())
            if time.time() - t0 > espera:
                break
    c.close()
    if ultimo:
        open(destino, "wb").write(ultimo)
    else:
        print("sin fotograma:", destino)


def main() -> None:
    puerto = int(sys.argv[1])
    for p in sys.argv[2:]:
        if p.startswith("png="):
            captura(puerto, p[4:])
        elif p.startswith("esp="):
            time.sleep(float(p[4:]))
        elif p.startswith("linea="):
            post(puerto, "/linea", p[6:].encode())
        elif p.startswith("env="):
            post(puerto, "/linea", b"E " + p[4:].encode())
        else:
            k, _, n = p.partition("*")
            for _ in range(int(n or 1)):
                for v in (1, 0):
                    post(puerto, "/tecla", json.dumps({"k": k, "v": v}).encode())
                time.sleep(float(os.environ.get("KEYWAIT", "0.6")))


if __name__ == "__main__":
    main()
