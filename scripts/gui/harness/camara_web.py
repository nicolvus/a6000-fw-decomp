"""Batería, jack USB y HDMI del arnés (G22-E): página propia y puntos HTTP para `live.py`.

El modelo es el del ANFITRIÓN (`estado_camara.py`, sección `camara` del config del configurador) y viaja al invitado como órdenes del
protocolo LIVE del shim: `B <0..100>` (nivel de batería que devuelve la respuesta emulada de CamMgr, CAMGREMU) y `U <0|1>` (jack USB
como el driver de entrada de la cámara: clave 0x7000001, evento 0x15040010, índice físico 0x177, §5.18w de g22-arnes-ui-qemu.md).

Puntos: GET /camara/ (página), GET /camara/estado, POST /camara/bateria, POST /camara/usb, POST /camara/hdmi.

Límites (ver docs/gui/g22-estado-camara.md): (1) con el puente AVQ activo contesta el CamMgr real de av-cam y la batería que se pinta en
la OSD es la suya, no `B`; (2) HDMI solo se guarda en el modelo: el shim no tiene orden verificada para ese jack y el bucle CEC del
invitado está silenciado (NO_VERIFICADO, sin efecto en el firmware).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import emu_config as E
import estado_camara

CONFIG_RUTA = E.CONFIG_RUTA  # se puede sustituir en los tests (config de un directorio temporal)

HTML = """<fieldset><legend>Batería, carga y USB</legend>
<label>Batería <input type="range" id="cam_b" min="0" max="100" step="1"> <output id="cam_bv">100</output> %</label>
<label><input type="checkbox" id="cam_usb"> jack USB conectado (carga)</label>
<label><input type="checkbox" id="cam_hdmi"> salida HDMI</label>
<div id="cam_modelo"></div><div id="cam_invitado"></div></fieldset>"""

JS = r"""
function camPinta(j){const m=j.modelo;document.getElementById('cam_b').value=m.bateria;document.getElementById('cam_bv').textContent=m.bateria;
document.getElementById('cam_usb').checked=m.usb;document.getElementById('cam_hdmi').checked=m.hdmi;
document.getElementById('cam_modelo').textContent=`modelo: batería ${m.bateria} % · ${m.cargando?'cargando':'sin carga'} · USB ${m.usb?'conectado':'desconectado'} · HDMI ${m.hdmi?'sí':'no'}`;
const g=j.invitado||{};document.getElementById('cam_invitado').textContent=(g.conectado?'invitado: puerto abierto':'invitado: SIN conexión')+(g.shim&&g.shim.length?' · shim: '+g.shim[g.shim.length-1]:'')}
async function camEstado(){const j=await (await fetch('/camara/estado')).json();camPinta(j)}
async function camPunto(p,cuerpo){const r=await fetch('/camara/'+p,{method:'POST',body:JSON.stringify(cuerpo)});const j=await r.json();
if(!r.ok){document.getElementById('cam_modelo').textContent='error: '+(j.error||r.status);return}camPinta(j)}
document.getElementById('cam_b').oninput=e=>document.getElementById('cam_bv').textContent=e.target.value;
document.getElementById('cam_b').onchange=e=>camPunto('bateria',{pct:Number(e.target.value)});
document.getElementById('cam_usb').onchange=e=>camPunto('usb',{on:e.target.checked});
document.getElementById('cam_hdmi').onchange=e=>camPunto('hdmi',{on:e.target.checked});
camEstado();
"""

PAGINA = ("<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\"><title>A6000 — estado de la cámara (G22-E)</title><style>"
          "body{font:14px system-ui,sans-serif;margin:12px;background:#111;color:#ddd}fieldset{border:1px solid #444;margin:0}"
          "output{display:inline-block;min-width:3em;text-align:right}div{margin:6px 0;color:#9cd}</style></head><body>"
          + HTML + "<script>" + JS + "</script></body></html>")


def _ruta_config(vm) -> Path:
    """Config del configurador: `vm.cfg_ruta` si existe, el `--config` de live.py (su global CONFIG) y, si no, el de emu_config.

    Se lee el global de `live` a través de sys.modules para no añadir más líneas de enganche en live.py ni un import circular.
    """
    ruta = getattr(vm, "cfg_ruta", "")
    if not ruta:
        vivo = sys.modules.get("live")
        ruta = (getattr(vivo, "CONFIG", None) or {}).get("ruta", "") if vivo else ""
    return Path(ruta or CONFIG_RUTA)


def _estado(vm) -> estado_camara.Estado:
    return estado_camara.desde_config(E.carga_config(_ruta_config(vm)))


def _guarda(vm, e: estado_camara.Estado) -> estado_camara.Estado:
    """Deja `e` en la sección `camara` del config (valida y escribe atómico con emu_config.guarda_config)."""
    ruta = _ruta_config(vm)
    cfg = E.carga_config(ruta)
    cfg[estado_camara.SECCION] = estado_camara.a_config(e)
    return estado_camara.desde_config(E.guarda_config(cfg, ruta))


def invitado(vm) -> dict:
    """Lo medible del invitado sin la cámara: puerto LIVE abierto y las últimas líneas del shim sobre estos eventos.

    Las busca en el log del propio shim (`live/<perfil>/shim.log`, con WAITLOG/WLALL) y en la consola del invitado, que es donde
    aparecen si live.py arrancó con FULLLOG.
    """
    d = Path(getattr(vm, "dir", "") or "")
    ultimas: list[str] = []
    for nombre in ("shim.log", "consola.log"):
        f = d / nombre
        try:
            with f.open("rb") as fh:
                fh.seek(max(0, f.stat().st_size - 60000))
                for ln in fh.read().decode("utf-8", "replace").splitlines():
                    if "JACK USB" in ln or "BATERIA" in ln or "CamMgr MSGID" in ln:
                        ultimas.append(ln.strip())
        except OSError:
            continue
    return {"conectado": bool(getattr(vm, "sock", None)), "dir": str(d), "shim": ultimas[-6:]}


def maneja(h, metodo: str, ruta: str, cuerpo: bytes, vm) -> bool:
    """Atiende /camara/*; `vm` expone `.envia(bytes)`, `.sock`, `.dir` y opcionalmente `.cfg_ruta`. False si la ruta no es suya."""
    if not ruta.startswith("/camara"):
        return False

    def resp(datos: bytes, tipo: str, codigo: int = 200) -> None:
        h.send_response(codigo)
        h.send_header("Content-Type", tipo)
        h.send_header("Content-Length", str(len(datos)))
        h.end_headers()
        h.wfile.write(datos)

    def js(obj: dict, codigo: int = 200) -> None:
        resp(json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8", codigo)

    if metodo == "GET" and ruta in ("/camara", "/camara/"):
        resp(PAGINA.encode(), "text/html; charset=utf-8")
        return True
    try:
        if metodo == "GET" and ruta == "/camara/estado":
            js({"modelo": _estado(vm).a_dict(), "invitado": invitado(vm), "config": str(_ruta_config(vm))})
        elif metodo == "POST" and ruta.startswith("/camara/") and ruta.count("/") == 2 and ruta[8:] in ("bateria", "usb", "hdmi"):
            punto = ruta[8:]
            d = json.loads(cuerpo or b"{}")
            if not isinstance(d, dict):
                raise ValueError("el cuerpo debe ser un objeto JSON")
            antes = _estado(vm)
            if punto == "bateria":
                e, orden = antes.con(bateria=d.get("pct")), 0
            elif punto == "usb":
                e, orden = antes.con(usb=d.get("on")), 1
            else:
                e, orden = antes.con(hdmi=d.get("on")), None  # HDMI no se envía: el shim no tiene orden para ese jack
            e = _guarda(vm, e)
            enviado = b"" if orden is None else e.ordenes()[orden]
            if enviado:
                vm.envia(enviado)
            r = {"modelo": e.a_dict(), "enviado": [enviado.decode().strip()] if enviado else [], "invitado": invitado(vm)}
            if punto == "hdmi":
                r["nota"] = ("HDMI: solo modelo del anfitrión; el shim no tiene orden verificada para ese jack y el bucle CEC del invitado "
                             "está silenciado (NO_VERIFICADO, sin efecto en el firmware)")
            js(r)
        else:
            h.send_error(404)
    except (ValueError, OSError, KeyError) as e:
        js({"error": str(e)}, 400)
    return True
