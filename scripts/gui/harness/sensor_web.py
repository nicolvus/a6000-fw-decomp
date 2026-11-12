"""Sensor, SD y grabación de la ventana en vivo (G22-E/T4): HTML+JS de la página y puntos HTTP de `live.py`.

El disparo y la grabación los inicia hoy el ANFITRIÓN (botón/tecla en la página), no el firmware: el código de cámara de MOVIE no está
verificado. El fotograma guardado es la entrada del sensor, procesada por el ISP emulado (T9, isp_web.py) si está activado.
Puntos: GET /sd/estado, GET /sensor/media (fichero local de la config, con Range), POST /sd/foto (JPEG), POST /sd/video (WebM/MP4).
"""
import json
import mimetypes
import shutil
import subprocess
import tempfile
from pathlib import Path

import emu_config as E
import isp_web
import sd_emu as S

EXT_MEDIA = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v"}

HTML = """<label>Fuente del sensor <select id="fuente"><option value="imagen">Imagen</option><option value="video">Vídeo (bucle)</option>
<option value="webcam">Cámara web</option></select></label>
<div id="f_arch"><input type="file" id="img" accept="image/*,video/*"></div>
<div id="f_cam" hidden><select id="camsel"></select></div>
<label><input type="checkbox" id="ver" checked> mostrar imagen</label>
<div><button id="movie">● MOVIE</button> <span id="recst"></span></div>
<div id="sdst"></div>
<small id="aviso">Disparador y MOVIE los lanza el anfitrión (la ventana), no el firmware. Con «aplicar» desactivado se guarda la entrada del sensor <b>sin procesar</b>;
activado, el ISP emulado (panel de abajo) procesa lo que se ve y lo que se guarda: curvas y matriz REALES, el resto aproximado (ver «Etapas»). Código de MOVIE: NO_VERIFICADO.</small>""" + isp_web.HTML

JS = r"""
const SN={tipo:'ninguna',img:null,vid:document.createElement('video'),stream:null,rec:null,t0:0,trozos:[],cfg:{}};
SN.vid.muted=true;SN.vid.loop=true;SN.vid.playsInline=true;
const cap=document.createElement('canvas');cap.width=1536;cap.height=1024;const cg=cap.getContext('2d');
function dibujaSensor(g,W,H){const s=SN.tipo=='imagen'?SN.img:SN.tipo=='ninguna'?null:SN.vid;if(!s)return false;
const sw=s.videoWidth||s.naturalWidth||0,sh=s.videoHeight||s.naturalHeight||0;if(!sw||!sh)return false;
const r=Math.max(W/sw,H/sh),w=sw*r,h=sh*r;g.save();g.beginPath();g.rect(0,0,W,H);g.clip();if(window.ISP&&ISP.on)ISP.dibuja(g,s,(W-w)/2,(H-h)/2,w,h,W,H);else g.drawImage(s,(W-w)/2,(H-h)/2,w,h);g.restore();return true}
function pinta(){x.fillStyle='#000';x.fillRect(0,0,640,480);if(document.getElementById('ver').checked){x.save();x.translate(0,26.5);dibujaSensor(x,640,427);x.restore()}
if(osd.complete)x.drawImage(osd,0,0);
if(SN.rec){const s=Math.floor((Date.now()-SN.t0)/1000);x.fillStyle='#e22';x.beginPath();x.arc(24,24,8,0,7);x.fill();x.fillStyle='#fff';x.font='16px monospace';
x.fillText('REC '+String(s/60|0).padStart(2,'0')+':'+String(s%60).padStart(2,'0'),38,30)}}
setInterval(()=>{if(SN.tipo=='video'||SN.tipo=='webcam'||SN.rec){if(SN.rec)dibujaSensor(cg,1536,1024);pinta()}},33);
function paraFuente(){if(SN.stream){SN.stream.getTracks().forEach(t=>t.stop());SN.stream=null}SN.vid.pause();SN.vid.removeAttribute('src');SN.vid.srcObject=null;SN.vid.load()}
function ponImagen(url){paraFuente();const i=new Image();i.onload=()=>{SN.img=i;SN.tipo='imagen';pinta()};i.src=url}
async function ponVideo(url){paraFuente();SN.vid.src=url;await SN.vid.play();SN.tipo='video'}
async function ponWebcam(id){paraFuente();SN.stream=await navigator.mediaDevices.getUserMedia({video:id?{deviceId:{exact:id}}:true});SN.vid.srcObject=SN.stream;await SN.vid.play();SN.tipo='webcam';
const d=(await navigator.mediaDevices.enumerateDevices()).filter(v=>v.kind=='videoinput'),s=document.getElementById('camsel');
s.innerHTML=d.map((v,n)=>`<option value="${v.deviceId}">${v.label||'cámara '+(n+1)}</option>`).join('');const act=SN.stream.getVideoTracks()[0].getSettings().deviceId;if(act)s.value=act}
function ponFichero(f){if(f.type.startsWith('video/')){fuente.value='video';muestra();ponVideo(URL.createObjectURL(f))}else{fuente.value='imagen';muestra();ponImagen(URL.createObjectURL(f))}}
const fuente=document.getElementById('fuente');
function muestra(){document.getElementById('f_arch').hidden=fuente.value=='webcam';document.getElementById('f_cam').hidden=fuente.value!='webcam'}
const aviso=t=>{document.getElementById('recst').textContent=t};
fuente.onchange=async()=>{muestra();try{if(fuente.value=='webcam')await ponWebcam();else if(SN.cfg.ruta&&SN.cfg.fuente==fuente.value)(fuente.value=='video'?ponVideo:ponImagen)('/sensor/media?'+Date.now())}catch(e){aviso('fuente: '+e.message)}};
document.getElementById('camsel').onchange=e=>ponWebcam(e.target.value).catch(er=>aviso('cámara: '+er.message));
document.getElementById('img').onchange=e=>{if(e.target.files[0])ponFichero(e.target.files[0])};
c.ondragover=e=>e.preventDefault();c.ondrop=e=>{e.preventDefault();if(e.dataTransfer.files[0])ponFichero(e.dataTransfer.files[0])};
async function sdEstado(){try{const s=await (await fetch('/sd/estado')).json(),g=v=>(v/2**30).toFixed(2);
document.getElementById('sdst').textContent=`SD ${g(s.cuota)} GB · libre ${g(s.libre)} GB · ${s.fotos} fotos · ≈ ${s.disparos_aprox} disparos / ${s.minutos_xavcs_aprox} min XAVC S restantes · ${s.raiz}`}catch(e){}}
async function disparo(){if(!SN.tipo||SN.tipo=='ninguna'){aviso('elige una fuente de sensor para disparar');return}
if(!dibujaSensor(cg,1536,1024)){aviso('la fuente aún no tiene fotograma');return}
cap.toBlob(async b=>{const r=await fetch('/sd/foto',{method:'POST',body:b});const j=await r.json();aviso(r.ok?'foto guardada: '+j.ruta+ISP.nota():'foto NO guardada: '+j.error);sdEstado()},'image/jpeg',.92)}
document.getElementById('movie').onclick=()=>SN.rec?paraRec():iniciaRec();
function iniciaRec(){if(!SN.tipo||SN.tipo=='ninguna'){aviso('elige una fuente de sensor para grabar');return}
const tipos=['video/webm;codecs=vp9','video/webm;codecs=vp8','video/webm'],t=tipos.find(v=>MediaRecorder.isTypeSupported(v));
SN.trozos=[];SN.rec=new MediaRecorder(cap.captureStream(30),{mimeType:t,videoBitsPerSecond:8e6});SN.rec.ondataavailable=e=>e.data.size&&SN.trozos.push(e.data);
SN.rec.onstop=async()=>{aviso('guardando vídeo…');const r=await fetch('/sd/video',{method:'POST',headers:{'Content-Type':SN.rec.mimeType||'video/webm'},body:new Blob(SN.trozos)});
const j=await r.json();SN.rec=null;aviso(r.ok?'vídeo guardado: '+j.ruta+(j.nota?' ('+j.nota+')':'')+ISP.nota():'vídeo NO guardado: '+j.error);document.getElementById('movie').textContent='● MOVIE';sdEstado()};
dibujaSensor(cg,1536,1024);SN.t0=Date.now();SN.rec.start(500);document.getElementById('movie').textContent='■ PARAR';aviso('grabando…')}
function paraRec(){if(SN.rec&&SN.rec.state!='inactive')SN.rec.stop()}
function sensorInicio(c){SN.cfg=c||{};if(c&&c.fuente){fuente.value=c.fuente;muestra();if(c.fuente=='webcam')ponWebcam().catch(e=>aviso('cámara: '+e.message));
else if(c.ruta)Promise.resolve((c.fuente=='video'?ponVideo:ponImagen)('/sensor/media?'+Date.now())).catch(e=>aviso(e.message))}sdEstado()}
muestra();sdEstado();
""" + isp_web.JS


def _cfg(ruta: str) -> dict:
    return E.carga_config(Path(ruta)) if ruta else E.valida_config({})


def _convierte(webm: bytes, destino: Path) -> str:
    """WebM del navegador → MP4 H.264 con ffmpeg; sin ffmpeg (o si falla) guarda el WebM tal cual y lo dice."""
    ff = shutil.which("ffmpeg")
    with tempfile.TemporaryDirectory() as t:
        src, out = Path(t) / "in.webm", Path(t) / "out.mp4"
        src.write_bytes(webm)
        if ff:
            r = subprocess.run([ff, "-v", "error", "-y", "-i", str(src), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                                "-fps_mode", "cfr", "-r", "30", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-movflags", "+faststart", str(out)],
                               check=False, capture_output=True, timeout=600)
            if r.returncode == 0 and out.stat().st_size:
                S.escribe_atomico(destino, out.read_bytes())
                return "MP4 H.264 convertido con ffmpeg; NO es un clip XAVC S conforme (resolución, tasa, audio y XML sin verificar)"
        w = destino.with_suffix(".WEBM")
        S.escribe_atomico(w, webm)
        destino.unlink(missing_ok=True)
        return "WEBM sin convertir (ffmpeg no disponible o falló); formato NO_VERIFICADO"


def maneja(h, metodo: str, ruta: str, cuerpo: bytes, cfg_ruta: str) -> bool:
    """Atiende los puntos del sensor/SD; devuelve False si `ruta` no es suya. `h` = manejador HTTP de live.py (con `.responde`)."""
    if not (ruta.startswith(("/sd/", "/sensor/"))):
        return False
    cfg = _cfg(cfg_ruta)
    raiz, gb = S.raiz_sd(cfg["sd"]["carpeta"]), cfg["sd"]["tamano_gb"]

    def js(obj: dict, codigo: int = 200) -> None:
        d = json.dumps(obj, ensure_ascii=False).encode()
        h.send_response(codigo)
        h.send_header("Content-Type", "application/json; charset=utf-8")
        h.send_header("Content-Length", str(len(d)))
        h.end_headers()
        h.wfile.write(d)

    try:
        if metodo == "GET" and ruta == "/sd/estado":
            js(S.estado(raiz, gb))
        elif metodo == "GET" and ruta == "/sensor/media":
            sirve_fichero(h, Path(cfg["sensor"]["ruta"]).expanduser())
        elif metodo == "POST" and ruta == "/sd/foto":
            jpg = S.jpeg_con_exif(cuerpo)
            if not S.cabe(raiz, gb, len(jpg)):
                return js({"error": "SD llena (cuota superada)"}, 507) or True
            n, num = S.siguiente_foto(raiz)
            d = S.ruta_foto(raiz, n, num)
            S.escribe_atomico(d, jpg)
            js({"ruta": str(d.relative_to(raiz)), "bytes": len(jpg)})
        elif metodo == "POST" and ruta == "/sd/video":
            if not S.cabe(raiz, gb, len(cuerpo)):  # el MP4 convertido ronda el tamaño del WebM: se comprueba antes y después
                return js({"error": "SD llena (cuota superada)"}, 507) or True
            n = S.siguiente_clip(raiz)
            d = S.ruta_clip(raiz, n)
            nota = _convierte(cuerpo, d)
            real = d if d.exists() else d.with_suffix(".WEBM")
            if S.usado(raiz) > S.cuota_bytes(gb):
                real.unlink(missing_ok=True)
                return js({"error": "SD llena (cuota superada)"}, 507) or True
            js({"ruta": str(real.relative_to(raiz)), "bytes": real.stat().st_size, "nota": nota})
        else:
            h.send_error(404)
    except (ValueError, OSError) as e:
        js({"error": str(e)}, 400)
    return True


def sirve_fichero(h, f: Path) -> None:
    """Sirve el fichero de imagen/vídeo de la config con Range (el `<video>` lo necesita para buclear y buscar)."""
    if f.suffix.lower() not in EXT_MEDIA or not f.is_file():
        h.send_error(404)
        return
    tam = f.stat().st_size
    ini, fin, codigo = 0, tam - 1, 200
    if (r := h.headers.get("Range", "")).startswith("bytes="):
        a, _, b = r[6:].partition("-")
        ini = int(a) if a else max(0, tam - int(b))
        fin = min(int(b), tam - 1) if a and b else tam - 1
        codigo = 206
    h.send_response(codigo)
    h.send_header("Content-Type", mimetypes.guess_type(f.name)[0] or "application/octet-stream")
    h.send_header("Accept-Ranges", "bytes")
    h.send_header("Content-Length", str(fin - ini + 1))
    if codigo == 206:
        h.send_header("Content-Range", f"bytes {ini}-{fin}/{tam}")
    h.end_headers()
    with f.open("rb") as fh:
        fh.seek(ini)
        resto = fin - ini + 1
        try:
            while resto > 0 and (d := fh.read(min(1 << 20, resto))):
                h.wfile.write(d)
                resto -= len(d)
        except (BrokenPipeError, ConnectionResetError):
            return
