#!/usr/bin/env python3
"""Lanzador del emulador de la A6000 (G22-E/T3): página de configuración previa al arranque; «Iniciar» lanza `live.py` con ese perfil.

uso: lanzador.py [--puerto 8700] [--puerto-vm 8600] [--work DIR] [--config JSON] [--perfil-dir NOMBRE]
  Sirve http://127.0.0.1:8700 (firmware/perfil, .dat importado, mapa de teclas, opciones futuras) y guarda ~/.config/a6000-emu/config.json.
  «Iniciar» arranca live.py (restaura el estado del perfil si existe) en --puerto-vm y salta a su ventana; el enlace «Configurador» de la
  ventana guarda el estado, cierra la VM y vuelve aquí. Solo toca el proceso que él mismo lanzó (PID propio).
"""
import argparse
import json
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import emu_config as E

WORK = HERE.parents[2] / "analysis/gui/g22/harness"


class Emulador:
    def __init__(self, work: Path, config: Path, puerto: int, puerto_vm: int, perfil: str) -> None:
        self.work, self.config, self.puerto, self.puerto_vm, self.perfil = work, config, puerto, puerto_vm, perfil
        self.p: subprocess.Popen | None = None
        self.lock = threading.Lock()

    @property
    def url_vm(self) -> str:
        return f"http://127.0.0.1:{self.puerto_vm}/"

    def corriendo(self) -> bool:
        return self.p is not None and self.p.poll() is None

    def estado(self) -> dict:
        return {"corriendo": self.corriendo(), "url": self.url_vm, "pid": self.p.pid if self.corriendo() and self.p else None}

    def puerto_libre(self) -> bool:
        with socket.socket() as s:
            return s.connect_ex(("127.0.0.1", self.puerto_vm)) != 0

    def pkg(self, cfg: dict) -> str:
        fw = cfg["firmware"]
        if fw["origen"] == "sony":
            return ""
        rel = fw["overlay"] if fw["origen"] == "overlay" else fw["dat"]
        ruta = (self.work / rel).resolve()
        if self.work.resolve() not in ruta.parents or not (ruta / "cam/usr").is_dir():
            raise ValueError(f"overlay no encontrado: {rel}")
        return str(ruta)

    def iniciar(self, cfg: dict) -> dict:
        with self.lock:
            cfg = E.guarda_config(cfg, self.config)
            if self.corriendo():
                return {"url": self.url_vm, "nota": "ya estaba en marcha"}
            if not self.puerto_libre():
                raise ValueError(f"el puerto {self.puerto_vm} ya está ocupado por otro proceso")
            cmd = [sys.executable, str(HERE / "live.py"), str(self.work), "--puerto", str(self.puerto_vm), "--config", str(self.config),
                   "--lanzador", f"http://127.0.0.1:{self.puerto}/"]
            if pkg := self.pkg(cfg):
                cmd += ["--pkg", pkg]
            if self.perfil:
                cmd += ["--perfil-dir", self.perfil]
            log = open(self.work / "lanzador-vm.log", "ab")  # noqa: SIM115 - lo hereda el proceso hijo
            self.p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=log)
            for _ in range(240):  # live.py construye el initrd en frío antes de abrir el puerto
                if not self.corriendo():
                    raise ValueError(f"live.py terminó (código {self.p.returncode}); ver {self.work / 'lanzador-vm.log'}")
                if not self.puerto_libre():
                    return {"url": self.url_vm, "nota": "arrancando"}
                time.sleep(0.5)
            raise ValueError("live.py no abrió el puerto en 120 s")

    def parar(self) -> str:
        with self.lock:
            if not self.corriendo() or self.p is None:
                return "no estaba en marcha"
            try:
                urllib.request.urlopen(urllib.request.Request(self.url_vm + "salir", data=b"", method="POST"), timeout=5).read()
            except OSError:
                self.p.terminate()
            try:
                self.p.wait(180)  # guarda el estado de la VM antes de salir
            except subprocess.TimeoutExpired:
                self.p.terminate()
                self.p.wait(30)
            return "detenida"


PAGINA = r"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Emulador A6000</title><style>
:root{--bg:#14161a;--card:#1d2026;--fg:#e4e6ea;--mut:#8b93a0;--acc:#e8732a;--ok:#5cc07a;--bad:#e5645a;--line:#2d323b}
@media(prefers-color-scheme:light){:root{--bg:#f3f4f6;--card:#fff;--fg:#1c1f24;--mut:#68707c;--line:#d9dce2}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}
header{padding:20px 24px 4px}h1{margin:0;font-size:22px}header p{margin:2px 0 0;color:var(--mut)}
main{max-width:980px;margin:0 auto;padding:12px 16px 90px;display:grid;gap:14px}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 18px}
h2{margin:0 0 8px;font-size:16px}.mut{color:var(--mut);font-size:13px}.soon{font-size:11px;background:var(--line);color:var(--mut);border-radius:9px;padding:1px 8px;margin-left:6px;vertical-align:middle}
button,select,input[type=text],input[type=number]{background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 11px;font:inherit}
button{cursor:pointer}button:hover{border-color:var(--acc)}button.p{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:600;padding:10px 26px;font-size:16px}
button.cap{border-color:var(--acc);color:var(--acc)}.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:6px 0}
table{border-collapse:collapse;width:100%}td,th{padding:6px 8px;border-top:1px solid var(--line);text-align:left}
.chip{display:inline-block;background:var(--bg);border:1px solid var(--line);border-radius:5px;padding:1px 4px 1px 8px;margin:2px 3px 2px 0;font-family:monospace}
.chip b{cursor:pointer;color:var(--bad);padding:0 5px}#msg{min-height:1.4em}.err{color:var(--bad)}.okc{color:var(--ok)}
fieldset{border:0;padding:0;margin:0}fieldset[disabled]{opacity:.55}footer{position:fixed;left:0;right:0;bottom:0;background:var(--card);border-top:1px solid var(--line);padding:10px 24px;display:flex;gap:14px;align-items:center}
</style></head><body><header><h1>Emulador Sony A6000</h1><p>Configura el firmware, los botones y el entorno antes de arrancar la UI en QEMU.</p></header><main>
<section><h2>Firmware / perfil</h2>
<div class="row"><label><input type="radio" name="or" value="sony"> Sony 3.21 de serie</label></div>
<div class="row"><label><input type="radio" name="or" value="overlay"> Overlay CFW:</label> <select id="ov"></select></div>
<div class="row"><label><input type="radio" name="or" value="dat"> Paquete <code>.dat</code> importado:</label> <b id="datsel" class="mut">ninguno</b></div>
<div class="row"><input type="file" id="fdat" accept=".dat"> <span class="mut">o ruta</span> <input type="text" id="rdat" size="38" placeholder="/ruta/FirmwareData.dat">
<button id="imp">Importar</button></div>
<p class="mut">El <code>.dat</code> se descifra y valida (paquete A6000 íntegro) y se reduce a un overlay de ficheros distintos de Sony; no se instala nada.
Un perfil nuevo arranca en frío (≈ 2,5 min) y después se restaura en segundos.</p><div id="impmsg"></div></section>
<section><h2>Mapa de teclas</h2><p class="mut">Pulsa «Capturar» y luego la tecla del teclado. Un botón puede tener varias teclas; una tecla, un solo botón.
Solo figuran los botones con código de cámara medido; Fn, reproducción, rueda y dial se añadirán cuando se verifiquen.</p>
<table id="tt"></table><div class="row"><button id="rst">Restablecer valores por defecto</button></div></section>
<section><h2>Fuente del sensor <span class="soon">próximamente</span></h2><fieldset disabled><div class="row">
<select id="sfu"><option value="imagen">Imagen</option><option value="video">Vídeo</option><option value="webcam">Webcam</option></select>
<input type="text" id="sru" size="40" placeholder="ruta del fichero"></div></fieldset>
<p class="mut">Hoy la imagen se elige en la ventana en vivo (se compone bajo la OSD). Estos ajustes se guardan pero aún no tienen efecto.</p></section>
<section><h2>Tarjeta SD <span class="soon">próximamente</span></h2><fieldset disabled><div class="row">Tamaño <input type="number" id="sgb" min="1" max="2048" step="1" style="width:80px"> GB
&nbsp; Carpeta <input type="text" id="sca" size="40" placeholder="directorio del anfitrión"></div></fieldset></section>
<section><h2>Red <span class="soon">próximamente</span></h2><fieldset disabled><div class="row"><label><input type="checkbox" id="rte"> Telnet</label>
<label><input type="checkbox" id="rwi"> Wi-Fi por red local</label></div></fieldset></section>
</main><footer><button class="p" id="go">Iniciar</button><span id="msg" class="mut"></span><span style="flex:1"></span>
<span id="vm" class="mut"></span><button id="stop" hidden>Parar VM</button><button id="quit">Cerrar emulador</button></footer>
<script>
const $=id=>document.getElementById(id);let cfg,botones=[],cap=null;
const api=async(u,o)=>{const r=await fetch(u,o);const t=await r.text();let j;try{j=JSON.parse(t)}catch(e){j={error:t}}if(!r.ok)throw new Error(j.error||t);return j};
const msg=(t,c)=>{$('msg').textContent=t;$('msg').className=c||'mut'};
function pinta(){document.querySelector(`[name=or][value=${cfg.firmware.origen}]`).checked=true;$('ov').value=cfg.firmware.overlay;
$('datsel').textContent=cfg.firmware.dat||'ninguno';$('sfu').value=cfg.sensor.fuente;$('sru').value=cfg.sensor.ruta;$('sgb').value=cfg.sd.tamano_gb;
$('sca').value=cfg.sd.carpeta;$('rte').checked=cfg.red.telnet;$('rwi').checked=cfg.red.wifi;
$('tt').innerHTML='<tr><th>Botón de la cámara</th><th>Teclas</th><th></th></tr>';
for(const b of botones){const tr=$('tt').insertRow();tr.insertCell().textContent=b;const c=tr.insertCell();
for(const k of cfg.teclas[b]||[]){const s=document.createElement('span');s.className='chip';s.textContent=k;const x=document.createElement('b');x.textContent='×';
x.onclick=()=>{cfg.teclas[b]=cfg.teclas[b].filter(y=>y!=k);guarda()};s.append(x);c.append(s)}
const bt=document.createElement('button');bt.textContent=cap==b?'Pulsa una tecla…':'Capturar';if(cap==b)bt.className='cap';bt.onclick=()=>{cap=cap==b?null:b;pinta()};tr.insertCell().append(bt)}}
function lee(){const o=document.querySelector('[name=or]:checked').value;cfg.firmware.origen=o;cfg.firmware.overlay=$('ov').value;cfg.sensor={fuente:$('sfu').value,ruta:$('sru').value};
cfg.sd={tamano_gb:+$('sgb').value||4,carpeta:$('sca').value};cfg.red={telnet:$('rte').checked,wifi:$('rwi').checked}}
async function guarda(){lee();try{cfg=(await api('/api/config',{method:'POST',body:JSON.stringify(cfg)})).config;msg('guardado','okc')}catch(e){msg(e.message,'err');await carga()}pinta()}
async function carga(){const r=await api('/api/config');cfg=r.config;botones=r.botones;$('ov').innerHTML=r.overlays.map(o=>`<option>${o}</option>`).join('');
if(!cfg.firmware.overlay&&r.overlays.length)cfg.firmware.overlay=r.overlays[0];$('ov').value=cfg.firmware.overlay;vm(r.vm);pinta()}
function vm(v){$('vm').textContent=v.corriendo?`VM en marcha (PID ${v.pid}) · `:'';if(v.corriendo){const a=document.createElement('a');a.href=v.url;a.textContent='abrir ventana';$('vm').append(a)}$('stop').hidden=!v.corriendo}
addEventListener('keydown',e=>{if(!cap)return;e.preventDefault();const k=e.code;
for(const b in cfg.teclas){if(b!=cap&&cfg.teclas[b].includes(k)){msg(`${k} ya está en «${b}»; quítala allí primero`,'err');return}}
cfg.teclas[cap]=[...new Set([...(cfg.teclas[cap]||[]),k])];cap=null;guarda()});
document.querySelectorAll('[name=or],#ov,#sfu,#sru,#sgb,#sca,#rte,#rwi').forEach(e=>e.onchange=guarda);
$('rst').onclick=async()=>{cfg.teclas=(await api('/api/config?defecto=1')).config.teclas;guarda()};
$('imp').onclick=async()=>{const f=$('fdat').files[0],r=$('rdat').value.trim();if(!f&&!r){$('impmsg').innerHTML='<span class="err">Elige un fichero o escribe una ruta.</span>';return}
$('impmsg').textContent='descifrando y extrayendo (hasta ~30 s)…';try{const j=f?await api('/api/dat',{method:'POST',headers:{'X-Nombre':encodeURIComponent(f.name)},body:f}):
await api('/api/dat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ruta:r})});cfg=j.config;await carga();
$('impmsg').innerHTML=`<span class="okc">Importado: firmware ${j.version} (región ${j.region}), ${j.ficheros} ficheros distintos de Sony → ${j.overlay}</span>`}catch(e){$('impmsg').innerHTML='<span class="err"></span>';$('impmsg').firstChild.textContent=e.message}};
$('go').onclick=async()=>{lee();$('go').disabled=true;msg('arrancando… (un perfil nuevo tarda ≈ 2,5 min en frío)');try{const j=await api('/api/iniciar',{method:'POST',body:JSON.stringify(cfg)});location.href=j.url}catch(e){msg(e.message,'err');$('go').disabled=false}};
$('stop').onclick=async()=>{msg('guardando estado y parando…');await api('/api/parar',{method:'POST'});msg('VM detenida','okc');carga()};
$('quit').onclick=async()=>{await fetch('/api/cerrar',{method:'POST'}).catch(()=>{});document.body.innerHTML='<p style="padding:30px">Emulador cerrado. Puedes cerrar esta pestaña.</p>'};
carga().catch(e=>msg(e.message,'err'));setInterval(()=>api('/api/config').then(r=>vm(r.vm)).catch(()=>{}),4000);
</script></body></html>"""


def servidor(emu: Emulador) -> ThreadingHTTPServer:
    srv: ThreadingHTTPServer

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a: object) -> None:
            pass

        def json(self, obj: object, codigo: int = 200) -> None:
            cuerpo = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)

        def do_GET(self) -> None:
            ruta, _, q = self.path.partition("?")
            if ruta == "/":
                cuerpo = PAGINA.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(cuerpo)))
                self.end_headers()
                self.wfile.write(cuerpo)
            elif ruta == "/api/config":
                cfg = E.valida_config({}) if q == "defecto=1" else E.carga_config(emu.config)
                self.json({"config": cfg, "botones": E.botones_conocidos(), "overlays": E.overlays(emu.work), "vm": emu.estado()})
            elif ruta == "/api/estado":
                self.json(emu.estado())
            else:
                self.send_error(404)

        def do_POST(self) -> None:
            n = int(self.headers.get("Content-Length", 0))
            try:
                if self.path == "/api/dat":
                    self.json(self.importa(n))
                    return
                cuerpo = self.rfile.read(n)
                if self.path == "/api/config":
                    self.json({"config": E.guarda_config(json.loads(cuerpo), emu.config)})
                elif self.path == "/api/iniciar":
                    self.json(emu.iniciar(json.loads(cuerpo)))
                elif self.path == "/api/parar":
                    self.json({"estado": emu.parar()})
                elif self.path == "/api/cerrar":
                    self.json({"ok": True})
                    threading.Thread(target=lambda: (emu.parar(), srv.shutdown()), daemon=True).start()
                else:
                    self.send_error(404)
            except (ValueError, E.DatError, OSError) as e:  # json.JSONDecodeError es ValueError
                self.json({"error": str(e)}, 400)

        def importa(self, n: int) -> dict:
            if self.headers.get("Content-Type", "").startswith("application/json"):
                ruta = Path(json.loads(self.rfile.read(n))["ruta"]).expanduser()
                if not ruta.is_file():
                    raise E.DatError(f"No existe el fichero {ruta}")
                dat = ruta.read_bytes()
                origen = str(ruta)
            else:
                dat = bytearray()
                while len(dat) < n:
                    dat += self.rfile.read(min(1 << 20, n - len(dat)))
                origen = self.headers.get("X-Nombre", "subido.dat")
            res = E.importa_dat(bytes(dat), emu.work)
            cfg = E.carga_config(emu.config)
            cfg["firmware"] = {"origen": "dat", "overlay": cfg["firmware"]["overlay"], "dat": res["overlay"]}
            return {**res, "origen": origen, "config": E.guarda_config(cfg, emu.config)}

    srv = ThreadingHTTPServer(("127.0.0.1", emu.puerto), H)
    return srv


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--puerto", type=int, default=8700)
    ap.add_argument("--puerto-vm", type=int, default=8600)
    ap.add_argument("--work", type=Path, default=WORK)
    ap.add_argument("--config", type=Path, default=E.CONFIG_RUTA)
    ap.add_argument("--perfil-dir", default="", help="fuerza el directorio de perfil en live/ (pruebas)")
    a = ap.parse_args()
    emu = Emulador(a.work.resolve(), a.config, a.puerto, a.puerto_vm, a.perfil_dir)
    srv = servidor(emu)
    print(f"http://127.0.0.1:{a.puerto}", flush=True)
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: threading.Thread(target=lambda: (emu.parar(), srv.shutdown()), daemon=True).start())
    try:
        srv.serve_forever()
    finally:
        emu.parar()


if __name__ == "__main__":
    main()
