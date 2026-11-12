#!/usr/bin/env python3
"""T9 — compara el shader WebGL2 (Chromium headless, sin QEMU) con la referencia CPU `modelo.aplica` en puntos de control.
Sirve la página real de `live.py` con una VM falsa (NVRAM en memoria), ejecuta `ISP.sonda()` y devuelve las diferencias.
Uso: prueba_shader.py [--captura ruta.png] [--puerto 8604]; sale con 1 si alguna diferencia supera 2/255."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "harness")]
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import modelo as M

CHROME = next(iter(sorted((Path.home() / ".cache/ms-playwright").glob("chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell"))), None) or shutil.which("chromium")
PUNTOS = [(0, 0, 0), (255, 255, 255), (128, 128, 128), (30, 30, 30), (200, 60, 40), (40, 160, 90), (60, 80, 220), (250, 220, 20)]
CASOS = {"movie": {"gamma": 4}, "cine1": {"gamma": 6, "saturation": 2}, "slog2": {"gamma": 11, "phase": 3, "cd_r": 4}, "still_bl": {"gamma": 5, "black_level": 5, "saturation": -3}}


class VmFalsa:
    def __init__(self) -> None:
        self.nvram: dict[int, bytes] = {}
        self.p = type('P', (), {'poll': lambda self: None})()
        self.cv = threading.Condition()
        self.png = b''
        self.t0, self.seq, self.fps, self.coste, self.restaurado, self.red = time.time(), 0, 0, "", False, {}

    def nv(self, texto: str) -> None:
        i, _, d = texto.partition(" ")
        self.nvram[int(i, 16)] = bytes.fromhex(d)


def prueba_js() -> str:
    return ("(async()=>{while(!(window.ISP&&ISP.t&&ISP.lut))await new Promise(r=>setTimeout(r,50));ISP.k=2;ISP.on=true;const R={};"
            f"const P={json.dumps(PUNTOS)},C={json.dumps(CASOS)};"
            "try{for(const [n,c] of Object.entries(C)){ISP.p=Object.assign({},ISP.t.neutro,c);R[n]=P.map(p=>ISP.sonda(p));}}catch(e){R.error=String(e.stack)}"
            "document.body.insertAdjacentHTML('beforeend','<pre id=res>'+JSON.stringify(R)+'</pre>')})()")


def main() -> int:
    puerto = int(sys.argv[sys.argv.index("--puerto") + 1]) if "--puerto" in sys.argv else 8604
    captura = sys.argv[sys.argv.index("--captura") + 1] if "--captura" in sys.argv else None
    if not CHROME:
        print("sin Chromium headless")
        return 2
    vm = VmFalsa()
    import isp_web
    import sensor_web
    pagina = ("<!doctype html><meta charset=utf-8><body><canvas id=c width=640 height=480></canvas><aside>" + sensor_web.HTML + "</aside><script>"
              "const c=document.getElementById('c'),x=c.getContext('2d'),st={};let osd=new Image(),info={};" + sensor_web.JS + prueba_js() + "</script></body>").encode()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a: object) -> None:
            pass

        def responde(self, cuerpo: bytes, tipo: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)

        def do_GET(self) -> None:
            if self.path == "/":
                self.responde(pagina, "text/html; charset=utf-8")
            elif not (isp_web.maneja(self, "GET", self.path, b"", vm) or sensor_web.maneja(self, "GET", self.path, b"", "")):
                self.send_error(404)

        def do_POST(self) -> None:
            isp_web.maneja(self, "POST", self.path, self.rfile.read(int(self.headers.get("Content-Length", 0))), vm)

    srv = ThreadingHTTPServer(("127.0.0.1", puerto), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        args = [str(CHROME), "--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--virtual-time-budget=8000", "--enable-logging=stderr", "--v=0"]
        r = subprocess.run([*args, "--dump-dom", f"http://127.0.0.1:{puerto}/"], check=False, capture_output=True, text=True, timeout=90)
        out = r.stdout
        print([l for l in r.stderr.splitlines() if 'CONSOLE' in l or 'rror' in l][:8])
        if captura:
            subprocess.run([*args, f"--screenshot={captura}", "--window-size=1100,1100", f"http://127.0.0.1:{puerto}/"], check=False, capture_output=True, timeout=90)
    finally:
        srv.shutdown()
    m = re.search(r"<pre id=\"res\">(.*?)</pre>", out, re.DOTALL)
    if not m:
        print("la página no devolvió resultados", out[-300:])
        return 1
    import html
    res = json.JSONDecoder().raw_decode(html.unescape(m.group(1)))[0]
    if "error" in res:
        print(res["error"][:600])
        return 1
    t = M.Tablas()
    peor = 0.0
    for n, c in CASOS.items():
        ref = np.round(M.aplica(np.array(PUNTOS, float)[None] / 255, c, t, exposicion=2.0)[0] * 255)
        d = np.abs(ref - np.array(res[n])).max()
        peor = max(peor, d)
        print(f"{n}: máx |shader − CPU| = {d:.0f}/255")
    return 0 if peor <= 2 else 1


if __name__ == "__main__":
    sys.exit(main())
