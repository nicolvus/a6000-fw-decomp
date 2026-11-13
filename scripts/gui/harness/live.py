#!/usr/bin/env python3
"""Ventana en vivo del arnés de la UI (G22-D): la pantalla de im.elf en el navegador, con teclado y una imagen de «sensor» debajo.

uso: live.py DIR_TRABAJO [--pkg OVERLAY2] [--puerto 8600]
  Abre http://127.0.0.1:8600. La primera vez arranca en frío (≈ 2,5 min hasta el menú) y, 20 s después de la primera pantalla, guarda el
  estado de la VM en DIR/live/<sony|paquete>/estado.zst; las siguientes lo restauran (segundos). Se guarda también al salir (Ctrl+C, SIGTERM,
  POST /salir) y con «Guardar estado»; el guardado es atómico. El estado se invalida solo si cambia el shim, im.sh, run.py, SHIMENV o el overlay.
  Persistencia: la hora local del anfitrión se envía al invitado («T») al conectar y cada 30 s (sobrevive a restaurar un estado viejo);
  las escrituras de la UI a la NVRAM («NV») van a nvram.json del perfil y se aplican sobre la copia de bk.tbl en cada arranque en frío.
  --pkg = salida de pkg_usr.py (CFW). Teclas: flechas, Intro, Esc/M = MENU, espacio = disparador; botones en la página.
Cadena: el shim dibuja cada lista de la GPU en el búfer de color (gpu_draw), la copia a pantalla (0xb4…) marca el fotograma y el hilo LIVE
lo envía por virtio-serial (RGBA4444) solo si cambió; aquí se pasa a PNG y se empuja al navegador por SSE. Teclas al revés: «K clave valor índice».
Límite: la imagen del sensor solo se compone debajo de la OSD; ningún ajuste (Picture Profile, modos) la procesa: el proceso de imagen es de
av-cam, que el arnés no ejecuta.
"""
import argparse
import base64
import hashlib
import io
import json
import os
import re
import signal
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
import isp_web
import run
import sensor_web

# escenario de F3/F4 sin volcados: ciclo de modelos, menú abierto, cola de teclas 0x7a0020
SHIMENV = ("WAIT=999999 CVWAIT=0 POKE=fef348 OPENVIEW=view/ROOT,@V00E OPENVIEWAT=40 OPENVIEWGAP=14 "
           "STARTEV=11004002:100,11004012,11004013 POSTROOTEV=11004002:e3 STARTGAP=f SALVAGE=0 SKIPFN=7fa3d4=0 ACKQ0=58003f "
           "KEYQ=7a0020 KEYONACTIVE=0 KEYINIT=7000001:1:177 KEYINITON=06A_viewUnified2 LIVE=auto " + os.environ.get("SHIMEXTRA", ""))  # SHIMEXTRA="WAITLOG=3000": variables de diagnóstico del shim
# {clave KEY_TACT_*, índice físico} medidos en §5.18z′
TECLAS = {"arriba": (0x3, 0x1), "abajo": (0x30, 0x5), "izquierda": (0x15, 0x3), "derecha": (0x1AF, 0x14), "menu": (0x1AB, 0x11),
          "intro": (0xE000000, 0x1BC), "disparador": (0xA7, 0xE)}


def rgba4444_png(w: int, h: int, raw: bytes) -> bytes:
    v = np.frombuffer(raw, "<u2").reshape(h, w)
    img = np.dstack([((v >> s) & 15).astype(np.uint8) * 17 for s in (12, 8, 4, 0)])
    out = io.BytesIO()
    Image.fromarray(img, "RGBA").save(out, "PNG", compress_level=1)
    return out.getvalue()


MAC_CAMARA = "fc:c2:de:3a:5d:5c"  # la que muestra «Mostr. Direcc. MAC» (PsmNsGetMacAddress, NVRAM del volcado); ath0 la lleva como en la cámara


def red_args(red: dict | None) -> tuple[str, list[str]]:
    """(NET para SHIMENV, args de QEMU) de la config red: slirp (red local del anfitrión) + virtio-net; telnet = hostfwd 127.0.0.1:puerto → 23 del invitado."""
    red = red or {}
    modos = [m for m in ("telnet", "wifi") if red.get(m)]
    if not modos:
        return "", []
    fwd = f",hostfwd=tcp:127.0.0.1:{red.get('puerto', 2323)}-:23" if "telnet" in modos else ""
    return " NET=" + ",".join(modos), ["-netdev", "user,id=n0" + fwd, "-device", f"virtio-net-device,netdev=n0,mac={MAC_CAMARA}"]


def huella(work: Path, pkg: str, shimenv: str) -> str:
    """Hash de todo lo que fija el initrd y la RAM guardada: shim (overlay), im.sh, run.py, SHIMENV y el overlay del paquete."""
    h = hashlib.sha256(shimenv.encode())
    ficheros = [HERE / "im.sh", HERE / "run.py"]
    for raiz in (work / "overlay", Path(pkg) if pkg else None):
        if raiz and raiz.is_dir():
            ficheros += sorted(f for f in raiz.rglob("*") if f.is_file())
    for f in ficheros:
        h.update(f.name.encode() + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()


def escribe_atomico(destino: Path, datos: bytes) -> None:
    tmp = destino.with_name(destino.name + ".tmp")
    tmp.write_bytes(datos)
    tmp.replace(destino)


def msg_hora(ahora: float) -> bytes:
    """«T época_local_hex»: hora local del anfitrión (UTC + zona); el shim la avanza con su reloj monotónico."""
    return f"T {int(ahora) + time.localtime(ahora).tm_gmtoff:x}\n".encode()


class Vm:
    def __init__(self, work: Path, pkg: str, perfil: str = "", red: dict | None = None) -> None:
        net, net_args = red_args(red)
        self.red = red if net else {}
        shimenv = SHIMENV + net
        self.dir = work / "live" / (perfil or (Path(pkg).name if pkg else "sony"))
        self.dir.mkdir(parents=True, exist_ok=True)
        self.estado, self.ui, self.mon = self.dir / "estado.zst", self.dir / "ui.sock", self.dir / "mon.sock"
        initrd, sello = self.dir / "initrd.gz", self.dir / "huella.txt"
        self.nvram_f = self.dir / "nvram.json"
        self.nvram = {int(k, 16): bytes.fromhex(v) for k, v in self.carga(self.nvram_f).items()}
        actual = huella(work, pkg, shimenv)
        if not sello.exists() or sello.read_text() != actual:  # cambió el shim, im.sh, run.py, SHIMENV u overlay: el estado ya no vale
            for f in (self.estado, initrd, sello):
                f.unlink(missing_ok=True)
        restaurar = self.estado.exists() and initrd.exists()
        if not restaurar:  # el estado guardado solo vale con el mismo initrd (tamaño de las ROM de QEMU); en frío se rehace con la NVRAM actual
            import tempfile
            with tempfile.TemporaryDirectory() as t:
                escribe_atomico(initrd, run.build_initrd(work, HERE / "im.sh", Path(t), shimenv, pkg, self.nvram).read_bytes())
            sello.write_text(actual)
        for s in (self.ui, self.mon):
            s.unlink(missing_ok=True)
        extra = ["-chardev", f"socket,id=ui,path={self.ui},server=on,wait=off", "-device", "virtio-serial-device",
                 "-device", "virtserialport,chardev=ui,name=a6000ui,nr=1", "-monitor", f"unix:{self.mon},server=on,wait=off", *net_args]
        if restaurar:
            extra += ["-incoming", f"exec:zstd -dc {self.estado}"]
        self.cmd = run.qemu_cmd(work, initrd, extra, ["-display", "none", "-serial", f"file:{self.dir / 'consola.log'}"])
        self.p = subprocess.Popen(self.cmd, stdin=subprocess.DEVNULL)
        self.t0, self.restaurado = time.time(), restaurar
        self.png, self.seq, self.cv = b"", 0, threading.Condition()
        self.sock: socket.socket | None = None
        self.cerrojo = threading.Lock()  # un solo guardado a la vez
        self.fps, self.coste = 0.0, ""
        threading.Thread(target=self.lector, daemon=True).start()
        threading.Thread(target=self.reloj, daemon=True).start()
        if not restaurar:
            threading.Thread(target=self.autoguardado, daemon=True).start()

    @staticmethod
    def carga(f: Path) -> dict:
        try:
            return json.loads(f.read_text())
        except (OSError, ValueError):
            return {}

    def envia(self, datos: bytes) -> None:
        if self.sock:
            try:
                self.sock.sendall(datos)
            except OSError:
                pass

    def reloj(self) -> None:
        """Pone la hora real en el invitado al conectar (también tras restaurar un estado de hace días) y la reajusta cada 30 s."""
        while True:
            if self.sock:
                self.envia(msg_hora(time.time()))
            time.sleep(30 if self.sock else 0.5)

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
                if buf.startswith(b"\x01NV "):  # NV id hex: la UI escribió un registro de backup
                    j = buf.find(b"\n")
                    if j < 0:
                        break
                    self.nv(buf[4:j].decode())
                    buf = buf[j + 1:]
                    continue
                if buf.startswith(b"\x01WL "):  # línea de diagnóstico del shim (WAITLOG): va a shim.log
                    j = buf.find(b"\n")
                    if j < 0:
                        break
                    with (self.dir / "shim.log").open("ab") as f:
                        f.write(f"{time.time() % 1000:.2f} ".encode() + buf[4:j + 1])  # hora del anfitrión (mod 1000 s) delante, para comparar con la del invitado
                    buf = buf[j + 1:]
                    continue
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

    def nv(self, texto: str) -> None:
        i, _, datos = texto.partition(" ")
        self.nvram[int(i, 16)] = bytes.fromhex(datos)
        escribe_atomico(self.nvram_f, json.dumps({f"{k:x}": v.hex() for k, v in self.nvram.items()}).encode())

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
        with self.cerrojo:
            tmp = self.estado.with_suffix(".tmp")  # se escribe aparte y se renombra al terminar: un corte no deja un estado a medias
            tmp.unlink(missing_ok=True)
            self.monitor(f'migrate "exec:zstd -1 -T0 > {tmp}"')
            for _ in range(600):
                info = self.monitor("info migrate")
                if re.search(r"status:\s*completed", info, re.IGNORECASE):  # QEMU 11: «Status: completed»; antes «Migration status: completed»
                    tmp.replace(self.estado)
                    self.monitor("cont")
                    return f"estado guardado ({self.estado.stat().st_size >> 20} MiB)"
                if re.search(r"status:\s*(failed|cancelled)", info, re.IGNORECASE):
                    tmp.unlink(missing_ok=True)
                    self.monitor("cont")
                    return "fallo al guardar: " + info[-300:]
                time.sleep(0.5)
            tmp.unlink(missing_ok=True)
            return "tiempo agotado al guardar"


PAGINA = """<!doctype html><html lang="es"><head><meta charset="utf-8"><title>A6000 en vivo</title><style>
:root{--bg:#111;--fg:#ddd;--mut:#888;--acc:#e8732a}body{margin:0;background:var(--bg);color:var(--fg);font:14px system-ui,sans-serif}
main{display:flex;gap:16px;padding:16px;flex-wrap:wrap;align-items:flex-start}canvas{width:640px;height:auto;max-width:100%;image-rendering:pixelated;background:#000;border:1px solid #333;outline:none}
aside{width:280px}button{background:#222;color:var(--fg);border:1px solid #444;border-radius:4px;padding:6px 10px;margin:2px;cursor:pointer}
button:active{background:var(--acc)}.pad{display:grid;grid-template-columns:repeat(3,64px);gap:4px;margin:8px 0}.pad button{margin:0}
small,#st{color:var(--mut)}label{display:block;margin:10px 0 4px}</style></head><body><main>
<canvas id="c" width="640" height="480" tabindex="0"></canvas><aside>
<div id="st">conectando…</div>
<div class="pad"><span></span><button data-k="arriba">▲</button><span></span><button data-k="izquierda">◀</button>
<button data-k="intro">OK</button><button data-k="derecha">▶</button><span></span><button data-k="abajo">▼</button><span></span></div>
<button data-k="menu">MENU</button><button data-k="disparador">Disparador</button>
<!--SENSOR-->
<label>Escala <select id="esc"><option selected>1</option><option>1.5</option><option>2</option></select></label>
<p><button id="guardar">Guardar estado</button> <a id="volver" href="#" hidden>⚙ Configurador</a></p><small>Teclado: flechas, Intro, Esc/M = MENU, espacio = disparador. «Guardar estado» hace que el
próximo arranque empiece en esta pantalla. La imagen no se procesa con los ajustes de la cámara (av-cam no se emula).</small></aside></main>
<script>
const c=document.getElementById('c'),x=c.getContext('2d'),st=document.getElementById('st');let osd=new Image(),info={};/*SENSORJS*/
const es=new EventSource('/eventos');es.onmessage=e=>{const i=new Image();i.onload=()=>{osd=i;pinta()};i.src='data:image/png;base64,'+e.data};
setInterval(async()=>{try{info=await (await fetch('/estado')).json();st.textContent=info.texto}catch(e){st.textContent='sin conexión'}},1000);
const tecla=(k,v)=>{if(k=='disparador'&&v==1)disparo();return fetch('/tecla',{method:'POST',body:JSON.stringify({k,v})})};
document.querySelectorAll('[data-k]').forEach(b=>{b.onpointerdown=()=>tecla(b.dataset.k,1);b.onpointerup=b.onpointerleave=e=>{if(e.type=='pointerup'||e.buttons)tecla(b.dataset.k,0)}});
let mapa={ArrowUp:'arriba',ArrowDown:'abajo',ArrowLeft:'izquierda',ArrowRight:'derecha',Enter:'intro',Escape:'menu',KeyM:'menu',Space:'disparador'};
fetch('/config').then(r=>r.json()).then(c=>{if(c.mapa)mapa=c.mapa;sensorInicio(c.sensor);if(c.lanzador){const a=document.getElementById('volver');a.href=c.lanzador;a.hidden=false;
a.onclick=async e=>{e.preventDefault();st.textContent='guardando y cerrando…';await fetch('/salir',{method:'POST'});setTimeout(()=>location.href=c.lanzador,1500)}}}).catch(()=>{});
addEventListener('keydown',e=>{const k=mapa[e.code];if(!k||e.target.tagName=='INPUT'&&e.target.type!='checkbox')return;e.preventDefault();if(!e.repeat)tecla(k,1)});
addEventListener('keyup',e=>{const k=mapa[e.code];if(k){e.preventDefault();tecla(k,0)}});
document.getElementById('ver').onchange=pinta;document.getElementById('esc').onchange=e=>c.style.width=640*e.target.value+'px';
document.getElementById('guardar').onclick=async()=>{st.textContent='guardando…';alert(await (await fetch('/guardar',{method:'POST'})).text())};
</script></body></html>"""


CONFIG: dict = {"ruta": "", "lanzador": ""}  # lo fija main (--config, --lanzador)


def configuracion() -> dict:
    """Mapa de teclas del config.json del configurador (se relee en cada carga de la página); sin config, la página usa su mapa fijo."""
    from emu_config import carga_config, mapa_inverso
    cfg = carga_config(Path(CONFIG["ruta"])) if CONFIG["ruta"] else None
    return {"mapa": mapa_inverso(cfg["teclas"]) if cfg else None, "lanzador": CONFIG["lanzador"], "sensor": cfg["sensor"] if cfg else None}


def servidor(vm: Vm, puerto: int) -> ThreadingHTTPServer:
    srv: ThreadingHTTPServer
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
            if sensor_web.maneja(self, "GET", self.path.partition("?")[0], b"", CONFIG["ruta"]):  # sensor, SD y grabación (T4)
                return
            if isp_web.maneja(self, "GET", self.path, b"", vm):  # ISP emulado (T9)
                return
            if self.path == "/":
                self.responde(PAGINA.replace("<!--SENSOR-->", sensor_web.HTML).replace("/*SENSORJS*/", sensor_web.JS).encode(), "text/html; charset=utf-8")
            elif self.path == "/estado":
                t = time.time() - vm.t0
                fase = ("restaurado" if vm.restaurado else "arranque en frío") + f", {t:.0f} s"
                texto = f"{fase} · {vm.seq} fotogramas · {vm.fps:.1f} fps · último: {vm.coste}" if vm.seq else f"{fase}: esperando la primera pantalla…"
                if vm.red.get("telnet"):
                    texto += f" · telnet 127.0.0.1:{vm.red['puerto']}"
                if vm.p.poll() is not None:
                    texto = f"QEMU terminó (código {vm.p.returncode})"
                self.responde(json.dumps({"texto": texto, "fotogramas": vm.seq}).encode(), "application/json")
            elif self.path == "/config":  # mapa de teclado {KeyboardEvent.code: botón} y enlace al configurador (lanzador.py)
                self.responde(json.dumps(configuracion()).encode(), "application/json")
            elif self.path == "/eventos":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                visto = -1
                try:
                    while True:
                        with vm.cv:
                            nuevo = vm.cv.wait_for(lambda v=visto: vm.seq != v, timeout=15)
                            png, visto = vm.png, vm.seq
                        # sin fotograma nuevo en 15 s solo un comentario de vida: reenviar el último hacía que parecieran fotogramas nuevos
                        self.wfile.write(b"data: " + base64.b64encode(png) + b"\n\n" if nuevo and png else b": vivo\n\n")
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    return
            else:
                self.send_error(404)

        def do_POST(self) -> None:
            cuerpo = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            if sensor_web.maneja(self, "POST", self.path, cuerpo, CONFIG["ruta"]):
                return
            if isp_web.maneja(self, "POST", self.path, cuerpo, vm):
                return
            if self.path == "/tecla":
                d = json.loads(cuerpo)
                k, i = TECLAS[d["k"]]
                vm.tecla(k, int(d["v"]), i)
                self.responde(b"ok", "text/plain")
            elif self.path == "/refrescar":  # pide al invitado el fotograma actual (aunque no haya cambiado): sirve para comprobar si una tecla cambió la pantalla
                if vm.sock:
                    vm.sock.sendall(b"R\n")
                self.responde(b"ok", "text/plain")
            elif self.path == "/linea":  # diagnóstico: una línea cruda al invitado (p. ej. «Y 3» = tipo de fecha del shim)
                vm.envia(cuerpo.strip() + b"\n")
                self.responde(b"ok", "text/plain")
            elif self.path == "/salir":  # guarda el estado y cierra (main lo hace al salir de serve_forever)
                self.responde(b"saliendo", "text/plain")
                threading.Thread(target=srv.shutdown, daemon=True).start()
            elif self.path == "/guardar":
                self.responde(vm.guardar().encode(), "text/plain; charset=utf-8")
            else:
                self.send_error(404)

    srv = ThreadingHTTPServer(("127.0.0.1", puerto), H)
    return srv


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("work", type=Path)
    ap.add_argument("--pkg", default="", help="overlay de pkg_usr.py (CFW)")
    ap.add_argument("--puerto", type=int, default=8600)
    ap.add_argument("--perfil-dir", default="", help="nombre del directorio de perfil en live/ (por defecto sony o el nombre del overlay)")
    ap.add_argument("--config", default="", help="config.json del configurador (mapa de teclas)")
    ap.add_argument("--lanzador", default="", help="URL del configurador (enlace «volver»)")
    a = ap.parse_args()
    CONFIG.update(ruta=a.config, lanzador=a.lanzador)
    from emu_config import carga_config
    red = carga_config(Path(a.config))["red"] if a.config else None
    vm = Vm(a.work.resolve(), str(Path(a.pkg).resolve()) if a.pkg else "", a.perfil_dir, red)
    srv = servidor(vm, a.puerto)
    print(f"http://127.0.0.1:{a.puerto}  ({'restaurando estado' if vm.restaurado else 'arranque en frío, ≈ 2,5 min hasta el menú'})", flush=True)
    for sig in (signal.SIGINT, signal.SIGTERM):  # salir = guardar el estado y cerrar QEMU
        signal.signal(sig, lambda *_: threading.Thread(target=srv.shutdown, daemon=True).start())
    try:
        srv.serve_forever()
    finally:
        if vm.p.poll() is None:
            if vm.seq:  # solo hay estado válido si ya se pintó una pantalla
                print(vm.guardar(), flush=True)
            vm.p.terminate()
            vm.p.wait()


if __name__ == "__main__":
    main()
