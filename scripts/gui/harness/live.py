#!/usr/bin/env python3
"""Ventana en vivo del arnés de la UI (G22-D): la pantalla de im.elf en el navegador, con teclado y una imagen de «sensor» debajo.

uso: live.py DIR_TRABAJO [--pkg OVERLAY2] [--puerto 8600]
  Abre http://127.0.0.1:8600. La primera vez arranca en frío (≈ 2,5 min hasta el menú) y, 20 s después de la primera pantalla, guarda el
  estado de la VM en DIR/live/<sony|paquete>/estado.zst; las siguientes lo restauran (segundos). «Guardar estado» lo rehace en cualquier pantalla.
  --pkg = salida de pkg_usr.py (CFW). Teclas: flechas, Intro, Esc/M = MENU, espacio = disparador; botones en la página.
Cadena: el shim dibuja cada lista de la GPU en el búfer de color (gpu_draw), la copia a pantalla (0xb4…) marca el fotograma y el hilo LIVE
lo envía por virtio-serial (RGBA4444) solo si cambió; aquí se pasa a PNG y se empuja al navegador por SSE. Teclas al revés: «K clave valor índice».
Límite: la imagen del sensor solo se compone debajo de la OSD; ningún ajuste (Picture Profile, modos) la procesa: el proceso de imagen es de
av-cam, que el arnés no ejecuta.
"""
import argparse
import base64
import io
import json
import re
import socket
import struct
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run

# escenario de F3/F4 sin volcados: ciclo de modelos, menú abierto, cola de teclas 0x7a0020
SHIMENV = ("WAIT=999999 CVWAIT=0 POKE=fef348 OPENVIEW=view/ROOT,view/GLOBAL_MENU OPENVIEWAT=40 OPENVIEWGAP=14 "
           "STARTEV=11004002:100,11004012,11004013 STARTGAP=f SALVAGE=0 SKIPFN=7fa3d4=0 ACKQ0=58003f "
           "KEYQ=7a0020 KEYONACTIVE=0 KEYINIT=7000001:1:177 KEYINITON=06A_viewUnified2 LIVE=auto")
# {clave KEY_TACT_*, índice físico} medidos en §5.18z′
TECLAS = {"arriba": (0x3, 0x1), "abajo": (0x30, 0x5), "izquierda": (0x15, 0x3), "derecha": (0x1AF, 0x14), "menu": (0x1AB, 0x11),
          "intro": (0xE000000, 0x1BC), "disparador": (0xA7, 0xE)}


def rgba4444_png(w: int, h: int, raw: bytes) -> bytes:
    v = np.frombuffer(raw, "<u2").reshape(h, w)
    img = np.dstack([((v >> s) & 15).astype(np.uint8) * 17 for s in (12, 8, 4, 0)])
    out = io.BytesIO()
    Image.fromarray(img, "RGBA").save(out, "PNG", compress_level=1)
    return out.getvalue()


class Vm:
    def __init__(self, work: Path, pkg: str) -> None:
        self.dir = work / "live" / (Path(pkg).name if pkg else "sony")
        self.dir.mkdir(parents=True, exist_ok=True)
        self.estado, self.ui, self.mon = self.dir / "estado.zst", self.dir / "ui.sock", self.dir / "mon.sock"
        initrd = self.dir / "initrd.gz"
        restaurar = self.estado.exists() and initrd.exists()
        if not restaurar:  # el estado guardado solo vale con el mismo initrd (tamaño de las ROM de QEMU)
            import tempfile
            with tempfile.TemporaryDirectory() as t:
                initrd.write_bytes(run.build_initrd(work, HERE / "im.sh", Path(t), SHIMENV, pkg).read_bytes())
        for s in (self.ui, self.mon):
            s.unlink(missing_ok=True)
        extra = ["-chardev", f"socket,id=ui,path={self.ui},server=on,wait=off", "-device", "virtio-serial-device",
                 "-device", "virtserialport,chardev=ui,name=a6000ui,nr=1", "-monitor", f"unix:{self.mon},server=on,wait=off"]
        if restaurar:
            extra += ["-incoming", f"exec:zstd -dc {self.estado}"]
        self.cmd = run.qemu_cmd(work, initrd, extra, ["-display", "none", "-serial", f"file:{self.dir / 'consola.log'}"])
        self.p = subprocess.Popen(self.cmd, stdin=subprocess.DEVNULL)
        self.t0, self.restaurado = time.time(), restaurar
        self.png, self.seq, self.cv = b"", 0, threading.Condition()
        self.sock: socket.socket | None = None
        self.fps, self.coste = 0.0, ""
        threading.Thread(target=self.lector, daemon=True).start()
        if not restaurar:
            threading.Thread(target=self.autoguardado, daemon=True).start()

    def autoguardado(self) -> None:
        """Arranque en frío: guarda el estado 20 s después de la primera pantalla (el menú ya pintado) para que el siguiente arranque sea inmediato."""
        with self.cv:
            self.cv.wait_for(lambda: self.seq > 0)
        time.sleep(20)
        print(self.guardar(), flush=True)

    def lector(self) -> None:
        while not self.ui.exists():
            time.sleep(0.1)
        s = socket.socket(socket.AF_UNIX)
        s.connect(str(self.ui))
        s.sendall(b"R\n")  # tras restaurar, el invitado reenvía la pantalla actual aunque no haya cambiado
        self.sock, buf, marcas, prev = s, b"", [], None
        while True:
            d = s.recv(1 << 20)
            if not d:
                return
            buf += d
            while True:
                i = buf.find(b"A6KF")
                if i < 0 or len(buf) < i + 24:
                    break
                wh, *cont = struct.unpack_from("<5I", buf, i + 4)
                w, h = wh & 0xFFFF, wh >> 16
                n = w * h * 2
                if len(buf) < i + 24 + n:
                    break
                png = rgba4444_png(w, h, buf[i + 24:i + 24 + n])
                buf = buf[i + 24 + n:]
                now = time.time()
                marcas = [t for t in marcas if now - t < 2] + [now]
                if prev:  # coste en el invitado desde el fotograma anterior: listas, ms de dibujo, relleno/copias y LDEC
                    dl, *dt = ((a - b) & 0xFFFFFFFF for a, b in zip(cont, prev, strict=True))
                    self.coste = f"{dl} listas · dibujo {dt[0] / 1000:.0f} ms · copias {dt[1] / 1000:.0f} ms · LDEC {dt[2] / 1000:.0f} ms"
                prev = cont
                with self.cv:
                    self.png, self.seq, self.fps = png, self.seq + 1, len(marcas) / 2
                    self.cv.notify_all()

    def tecla(self, k: int, v: int, i: int) -> None:
        if self.sock:
            self.sock.sendall(f"K {k:x} {v:x} {i:x}\n".encode())

    def monitor(self, orden: str) -> str:
        s = socket.socket(socket.AF_UNIX)
        s.connect(str(self.mon))
        s.settimeout(2)
        s.sendall(orden.encode() + b"\n")
        time.sleep(0.3)
        out = b""
        try:
            while d := s.recv(65536):
                out += d
        except TimeoutError:
            pass
        s.close()
        return out.decode(errors="replace")

    def guardar(self) -> str:
        tmp = self.estado.with_suffix(".tmp")
        self.monitor(f'migrate "exec:zstd -1 -T0 > {tmp}"')
        for _ in range(600):
            info = self.monitor("info migrate")
            if re.search(r"status:\s*completed", info, re.IGNORECASE):  # QEMU 11: «Status: completed»; antes «Migration status: completed»
                tmp.replace(self.estado)
                self.monitor("cont")
                return f"estado guardado ({self.estado.stat().st_size >> 20} MiB)"
            if re.search(r"status:\s*(failed|cancelled)", info, re.IGNORECASE):
                self.monitor("cont")
                return "fallo al guardar: " + info[-300:]
            time.sleep(0.5)
        return "tiempo agotado al guardar"


PAGINA = """<!doctype html><html lang="es"><head><meta charset="utf-8"><title>A6000 en vivo</title><style>
:root{--bg:#111;--fg:#ddd;--mut:#888;--acc:#e8732a}body{margin:0;background:var(--bg);color:var(--fg);font:14px system-ui,sans-serif}
main{display:flex;gap:16px;padding:16px;flex-wrap:wrap}canvas{width:960px;max-width:100%;image-rendering:pixelated;background:#000;border:1px solid #333;outline:none}
aside{width:280px}button{background:#222;color:var(--fg);border:1px solid #444;border-radius:4px;padding:6px 10px;margin:2px;cursor:pointer}
button:active{background:var(--acc)}.pad{display:grid;grid-template-columns:repeat(3,64px);gap:4px;margin:8px 0}.pad button{margin:0}
small,#st{color:var(--mut)}label{display:block;margin:10px 0 4px}</style></head><body><main>
<canvas id="c" width="640" height="480" tabindex="0"></canvas><aside>
<div id="st">conectando…</div>
<div class="pad"><span></span><button data-k="arriba">▲</button><span></span><button data-k="izquierda">◀</button>
<button data-k="intro">OK</button><button data-k="derecha">▶</button><span></span><button data-k="abajo">▼</button><span></span></div>
<button data-k="menu">MENU</button><button data-k="disparador">Disparador</button>
<label>Imagen del sensor (debajo de la OSD)</label><input type="file" id="img" accept="image/*">
<label><input type="checkbox" id="ver" checked> mostrar imagen</label>
<label>Escala <select id="esc"><option>1</option><option selected>1.5</option><option>2</option></select></label>
<p><button id="guardar">Guardar estado</button></p><small>Teclado: flechas, Intro, Esc/M = MENU, espacio = disparador. «Guardar estado» hace que el
próximo arranque empiece en esta pantalla. La imagen no se procesa con los ajustes de la cámara (av-cam no se emula).</small></aside></main>
<script>
const c=document.getElementById('c'),x=c.getContext('2d'),st=document.getElementById('st');let osd=new Image(),fondo=null,info={};
function pinta(){x.fillStyle='#000';x.fillRect(0,0,640,480);if(fondo&&document.getElementById('ver').checked){const r=Math.max(640/fondo.width,480/fondo.height),
w=fondo.width*r,h=fondo.height*r;x.drawImage(fondo,(640-w)/2,(480-h)/2,w,h)}if(osd.complete)x.drawImage(osd,0,0)}
const es=new EventSource('/eventos');es.onmessage=e=>{const i=new Image();i.onload=()=>{osd=i;pinta()};i.src='data:image/png;base64,'+e.data};
setInterval(async()=>{try{info=await (await fetch('/estado')).json();st.textContent=info.texto}catch(e){st.textContent='sin conexión'}},1000);
const tecla=(k,v)=>fetch('/tecla',{method:'POST',body:JSON.stringify({k,v})});
document.querySelectorAll('[data-k]').forEach(b=>{b.onpointerdown=()=>tecla(b.dataset.k,1);b.onpointerup=b.onpointerleave=e=>{if(e.type=='pointerup'||e.buttons)tecla(b.dataset.k,0)}});
const mapa={ArrowUp:'arriba',ArrowDown:'abajo',ArrowLeft:'izquierda',ArrowRight:'derecha',Enter:'intro',Escape:'menu',m:'menu',M:'menu',' ':'disparador'};
addEventListener('keydown',e=>{const k=mapa[e.key];if(!k||e.target.tagName=='INPUT'&&e.target.type!='checkbox')return;e.preventDefault();if(!e.repeat)tecla(k,1)});
addEventListener('keyup',e=>{const k=mapa[e.key];if(k){e.preventDefault();tecla(k,0)}});
document.getElementById('img').onchange=e=>{const f=e.target.files[0];if(!f)return;const i=new Image();i.onload=()=>{fondo=i;pinta()};i.src=URL.createObjectURL(f)};
c.ondragover=e=>e.preventDefault();c.ondrop=e=>{e.preventDefault();const f=e.dataTransfer.files[0];if(f){const i=new Image();i.onload=()=>{fondo=i;pinta()};i.src=URL.createObjectURL(f)}};
document.getElementById('ver').onchange=pinta;document.getElementById('esc').onchange=e=>c.style.width=640*e.target.value+'px';
document.getElementById('guardar').onclick=async()=>{st.textContent='guardando…';alert(await (await fetch('/guardar',{method:'POST'})).text())};
</script></body></html>"""


def servidor(vm: Vm, puerto: int) -> ThreadingHTTPServer:
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
                self.responde(PAGINA.encode(), "text/html; charset=utf-8")
            elif self.path == "/estado":
                t = time.time() - vm.t0
                fase = ("restaurado" if vm.restaurado else "arranque en frío") + f", {t:.0f} s"
                texto = f"{fase} · {vm.seq} fotogramas · {vm.fps:.1f} fps · último: {vm.coste}" if vm.seq else f"{fase}: esperando la primera pantalla…"
                if vm.p.poll() is not None:
                    texto = f"QEMU terminó (código {vm.p.returncode})"
                self.responde(json.dumps({"texto": texto, "fotogramas": vm.seq}).encode(), "application/json")
            elif self.path == "/eventos":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                visto = -1
                try:
                    while True:
                        with vm.cv:
                            vm.cv.wait_for(lambda v=visto: vm.seq != v, timeout=15)
                            png, visto = vm.png, vm.seq
                        self.wfile.write(b"data: " + base64.b64encode(png) + b"\n\n" if png else b": vivo\n\n")
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    return
            else:
                self.send_error(404)

        def do_POST(self) -> None:
            cuerpo = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            if self.path == "/tecla":
                d = json.loads(cuerpo)
                k, i = TECLAS[d["k"]]
                vm.tecla(k, int(d["v"]), i)
                self.responde(b"ok", "text/plain")
            elif self.path == "/guardar":
                self.responde(vm.guardar().encode(), "text/plain; charset=utf-8")
            else:
                self.send_error(404)

    return ThreadingHTTPServer(("127.0.0.1", puerto), H)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("work", type=Path)
    ap.add_argument("--pkg", default="", help="overlay de pkg_usr.py (CFW)")
    ap.add_argument("--puerto", type=int, default=8600)
    a = ap.parse_args()
    vm = Vm(a.work.resolve(), str(Path(a.pkg).resolve()) if a.pkg else "")
    srv = servidor(vm, a.puerto)
    print(f"http://127.0.0.1:{a.puerto}  ({'restaurando estado' if vm.restaurado else 'arranque en frío, ≈ 2,5 min hasta el menú'})", flush=True)
    try:
        srv.serve_forever()
    finally:
        vm.p.terminate()


if __name__ == "__main__":
    main()
