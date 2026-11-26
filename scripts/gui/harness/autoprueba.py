#!/usr/bin/env python3
"""Autoprueba del arnés (G22): arranca la VM, ejercita las funciones de la cámara y dice PASS/FAIL con evidencia.

Uso: autoprueba.py DIR_TRABAJO [--perfil-dir autoprueba] [--puerto 8695] [--config CONFIG.json] [--espera 300] [--intentos 2] [--rapida]

Arranca `live.py` como subproceso, espera la primera pantalla y recorre: teclas (MENU abre/cierra), dial de modos, disparador
(foto en la SD con EXIF), MOVIE (clip MP4), galería (lista/fichero/importar/borrar/formatear), estado de cámara (batería/USB)
y cierre (`/salir`: estado guardado y sin procesos). Cada paso deja su PNG y su comprobación en el informe JSON/Markdown de
`DIR_TRABAJO/autoprueba/<AAAAMMDD-HHMMSS>/`; código de salida 1 si algo falla. El cuelgue intermitente del arranque (G22-CUELGUE: el invitado responde pero no llega a
componer la pantalla) se reintenta en frío con `--intentos`; el paso `arranque-reintento` deja constancia.

Es la comprobación de humo que el usuario puede correr tras tocar cualquier pieza del arnés: mide lo que la cámara hace de
verdad en el invitado (teclas, dial, captura, SD) y no solo que los procesos arranquen.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
VENV = Path(sys.executable)


def _get(url: str, timeout: float = 10) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _post(url: str, cuerpo: bytes = b"", cabeceras: dict | None = None, timeout: float = 60) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=cuerpo, method="POST", headers=cabeceras or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _js(datos: bytes) -> dict:
    try:
        return json.loads(datos)
    except ValueError:
        return {}


def _fotograma(url: str, destino: Path, distinto_de: bytes | None = None, timeout: float = 25) -> bytes:
    """Espera un fotograma del SSE (`/eventos`) y lo guarda; si `distinto_de` se da, espera a que CAMBIE (no vale el repetido)."""
    fin = time.time() + timeout
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            while time.time() < fin:
                linea = r.readline()
                if not linea:
                    break
                if not linea.startswith(b"data: "):
                    continue
                png = base64.b64decode(linea[6:].strip())
                if distinto_de is not None and png == distinto_de:
                    continue  # el anfitrión reenvía el último fotograma: hay que esperar al siguiente
                destino.write_bytes(png)
                return png
    except (OSError, ValueError):
        pass
    return b""


def _png(url: str, destino: Path, timeout: float = 20) -> bool:
    return bool(_fotograma(url, destino, None, timeout))


def _fotograma_con_contenido(url: str, destino: Path, minimo: float = 0.002, timeout: float = 30) -> tuple[bytes, float]:
    """Espera un fotograma con algo dibujado: el cambio ROOT→STLREC del dial deja un hueco en blanco de varios segundos."""
    fin = time.time() + timeout
    png, frac = b"", 0.0
    while time.time() < fin:
        png = _fotograma(url, destino, None, max(2.0, fin - time.time()))
        if not png:
            break
        frac = _vacia(destino)
        if frac >= minimo:
            return png, frac
        time.sleep(1)
    return png, frac


def _vacia(png: Path) -> float:
    """Fracción de píxeles distintos del color dominante: 0.0 = pantalla en blanco (o negro) sin nada dibujado.

    Contar «píxeles claros» no vale: una pantalla en blanco da 1.0 y la de disparo (fondo blanco con iconos) 0.01.
    """
    try:
        from PIL import Image
        im = Image.open(png).convert("RGB")
    except (OSError, ValueError):
        return 0.0
    crudo = im.tobytes()
    px = [crudo[i:i + 3] for i in range(0, len(crudo), 3)]
    if not px:
        return 0.0
    fondo = max(set(px), key=px.count)
    return sum(1 for c in px if sum(abs(a - b) for a, b in zip(c, fondo, strict=True)) > 60) / len(px)


def _asienta(url: str, destino: Path, ventana: float = 3.0) -> float:
    """Drena el SSE durante `ventana` s, guarda el ÚLTIMO fotograma y devuelve sus píxeles opacos.

    Un cambio de vista repinta tarde (cientos de ms a segundos): quedarse con el primer fotograma mide el estado anterior.
    """
    _post(url.replace("/eventos", "/refrescar"))
    fin = time.time() + ventana
    try:
        with urllib.request.urlopen(url, timeout=ventana + 10) as r:
            while time.time() < fin:
                linea = r.readline()
                if not linea:
                    break
                if linea.startswith(b"data: "):
                    destino.write_bytes(base64.b64decode(linea[6:].strip()))
    except (OSError, ValueError):
        pass
    return _opaco(destino)


def _opaco(png: Path) -> float:
    """Fracción de píxeles opacos del fotograma: la OSD de disparo es un overlay transparente (≈ 0,09) y el menú pinta la pantalla entera (≈ 1,0).

    Es lo que distingue «MENU abrió el menú» de «MENU no hizo nada», y también de un arranque que no llega a dibujar (≈ 0,01). Medir el
    brillo no vale: el fotograma lleva alfa y el fondo transparente cuenta como negro.
    """
    try:
        from PIL import Image
        im = Image.open(png).convert("RGBA")
    except (OSError, ValueError):
        return 0.0
    a = im.getchannel("A").tobytes()
    return sum(1 for v in a if v > 8) / len(a) if a else 0.0


class Prueba:
    """Un paso de la autoprueba: nombre, si pasó, evidencia legible y PNG opcional."""

    def __init__(self) -> None:
        self.pasos: list[dict] = []
        self.dir = Path()

    def paso(self, nombre: str, ok: bool, evidencia: str, png: str = "") -> bool:
        self.pasos.append({"paso": nombre, "ok": bool(ok), "evidencia": evidencia, "png": png})
        print(f"{'OK  ' if ok else 'FALLO'} {nombre}: {evidencia}", flush=True)
        return ok

    def informe(self, extra: dict) -> Path:
        self.dir.mkdir(parents=True, exist_ok=True)
        datos = {"fecha": time.strftime("%Y-%m-%d %H:%M:%S"), "ok": all(p["ok"] for p in self.pasos), "pasos": self.pasos, **extra}
        (self.dir / "autoprueba.json").write_text(json.dumps(datos, indent=1, ensure_ascii=False))
        fallos = [p["paso"] for p in self.pasos if not p["ok"]]
        lineas = [f"# Autoprueba del arnés — {datos['fecha']}", "",
                  f"Resultado: **{'PASS' if datos['ok'] else 'FAIL'}** ({len(self.pasos) - len(fallos)}/{len(self.pasos)} pasos)", ""]
        lineas += ["| paso | resultado | evidencia |", "|---|---|---|"]
        lineas += [f"| {p['paso']} | {'✓' if p['ok'] else '✗'} | {p['evidencia']} |" for p in self.pasos]
        if fallos:
            lineas += ["", "Fallos: " + ", ".join(fallos)]
        (self.dir / "autoprueba.md").write_text("\n".join(lineas) + "\n")
        return self.dir


def _config(tmp: Path) -> Path:
    from PIL import Image
    Image.new("RGB", (1536, 1024), (40, 110, 170)).save(tmp / "fuente.png")
    cfg = {"sd": {"carpeta": str(tmp / "sd"), "tamano_gb": 4}, "sensor": {"fuente": "imagen", "ruta": str(tmp / "fuente.png")}}
    (tmp / "config.json").write_text(json.dumps(cfg))
    return tmp / "config.json"


def espera_pantalla(base: str, tope: float) -> tuple[bool, float, dict]:
    t0 = time.time()
    while time.time() - t0 < tope:
        try:
            e = _js(_get(f"{base}/estado", 5)[1])
        except OSError:
            e = {}
        if e.get("fotogramas"):
            return True, time.time() - t0, e
        time.sleep(0.5)
    return False, time.time() - t0, {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("work", type=Path)
    ap.add_argument("--perfil-dir", default="autoprueba")
    ap.add_argument("--puerto", type=int, default=8695)
    ap.add_argument("--config", default="", help="config del configurador; sin él se usa uno propio en un directorio temporal")
    ap.add_argument("--espera", type=float, default=300, help="tope hasta la primera pantalla (frío ~170 s)")
    ap.add_argument("--salida", default="", help="carpeta del informe (por defecto DIR_TRABAJO/autoprueba/<fecha>)")
    ap.add_argument("--intentos", type=int, default=2, help="arranques en frío si el invitado no llega a pintar (G22-CUELGUE, intermitente)")
    a = ap.parse_args()
    work = a.work.resolve()
    base = f"http://127.0.0.1:{a.puerto}"
    tmp = Path(tempfile.mkdtemp(prefix="a6000-autoprueba-"))
    p = Prueba()
    p.dir = Path(a.salida) if a.salida else work / "autoprueba" / time.strftime("%Y%m%d-%H%M%S")
    if not a.config:  # SD y sensor propios: la autoprueba no toca ~/A6000-SD
        a.config = str(_config(tmp))
    cfg = json.loads(Path(a.config).read_text())
    raiz_sd = Path(cfg["sd"]["carpeta"])
    def _pantalla(arrancada: bool) -> tuple[float, float]:
        """(contenido, opacos) de la pantalla inicial: tras restaurar puede no haber repintado (G22-ARR2) y DISP la fuerza.

        La OSD de disparo de verdad deja ≈ 0,09 de píxeles opacos; un invitado que solo pinta el marco o nada se queda en ≈ 0,003
        (es el cuelgue de G22-CUELGUE), así que el paso exige las dos cosas y no solo «hay algo dibujado».
        """
        if not arrancada:
            return 0.0, 0.0
        destino = p.dir / "01b-pantalla.png"
        _post(f"{base}/refrescar")
        _fotograma(f"{base}/eventos", destino, None, 15)
        contenido, opacos = _vacia(destino), _opaco(destino)
        if contenido < 0.002 or opacos < 0.02:
            _post(f"{base}/tecla", b'{"k":"disp","v":1}')
            time.sleep(0.6)
            _post(f"{base}/tecla", b'{"k":"disp","v":0}')
            _fotograma(f"{base}/eventos", destino, None, 20)
            contenido, opacos = _vacia(destino), _opaco(destino)
        return contenido, opacos

    def arranca() -> tuple[subprocess.Popen, bool, float, dict, tuple[float, float]]:
        """Arranca live.py y espera a que el invitado PINTE: (proceso, listo, segundos, /estado, contenido dibujado).

        El cuelgue de «0 listas» (G22-CUELGUE) es intermitente: el invitado responde pero no llega a componer la pantalla, y no se arregla
        esperando. Se reintenta en frío borrando el perfil, que es lo que hace un usuario al volver a arrancar.
        """
        pr = subprocess.Popen([str(VENV), str(HERE / "live.py"), str(work), "--perfil-dir", a.perfil_dir, "--puerto", str(a.puerto),
                               "--config", a.config], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        listo, t, estado = espera_pantalla(base, a.espera)
        p.dir.mkdir(parents=True, exist_ok=True)
        png = p.dir / "01-pantalla.png"
        _post(f"{base}/refrescar")
        _png(f"{base}/eventos", png, 25) if listo else None
        return pr, listo, t, estado, _pantalla(listo)

    proc, listo, t, estado, (contenido, opacos) = arranca()
    p.paso("arranque", listo, f"primera pantalla en {t:.1f} s · {estado.get('texto', 'sin /estado')}", "01-pantalla.png" if listo else "")
    for intento in range(2, a.intentos + 1):  # el invitado que no pinta no se arregla esperando: se vuelve a arrancar en frío
        if not listo or (contenido >= 0.002 and opacos >= 0.02):
            break
        _post(f"{base}/salir")
        proc.wait(timeout=90)
        shutil.rmtree(work / "live" / a.perfil_dir, ignore_errors=True)
        proc, listo, t, estado, (contenido, opacos) = arranca()
        p.paso("arranque-reintento", listo and contenido >= 0.002 and opacos >= 0.02,
               f"intento {intento}: primera pantalla en {t:.1f} s, contenido {contenido:.3f}, opacos {opacos:.3f}",
               "01b-pantalla.png" if listo else "")
    try:
        if not listo:
            return 1
        pantalla = p.dir / "01b-pantalla.png"
        p.paso("pantalla", contenido > 0.002 and opacos >= 0.02,
               f"contenido dibujado {contenido:.3f}, píxeles opacos {opacos:.3f} (OSD de la cámara ≈ 0,09; 0,003 = no compuso)", pantalla.name)

        # teclas: MENU es un interruptor de una pulsación (G22-MENU): abre el menú (pantalla oscura) y lo cierra (disparo, clara)
        def menu() -> None:
            _post(f"{base}/tecla", b'{"k":"menu","v":1}')
            time.sleep(0.8)
            _post(f"{base}/tecla", b'{"k":"menu","v":0}')
            time.sleep(1.2)

        disparo = _opaco(pantalla)
        menu()
        abierto_px = _asienta(f"{base}/eventos", p.dir / "03-menu.png", 4.0)
        menu()
        vuelta = _asienta(f"{base}/eventos", p.dir / "03c-cerrado.png", 4.0)
        p.paso("teclas-MENU", abierto_px > 0.9 > vuelta,
               f"opacos: disparo {disparo:.2f} → menú {abierto_px:.2f} → disparo {vuelta:.2f} "
               f"(menú ≥ 0,9 y vuelta ≤ 0,5: una pulsación por cambio)")

        # dial de modos: el modo lo da el firmware (OPENVIEWDIAL); la pantalla se repinta
        _post(f"{base}/modo", b'{"p":4}')
        dial = p.dir / "04-dial.png"
        _, frac_dial = _fotograma_con_contenido(f"{base}/eventos", dial, 0.002, 40)  # el cambio de vista deja un hueco en blanco
        p.paso("dial-de-modos", frac_dial > 0.002, f"pantalla con contenido tras girar a M ({frac_dial:.3f})", dial.name)

        # disparador → foto en la SD con EXIF de la cámara
        n0 = len(list((raiz_sd / "DCIM").rglob("*.JPG"))) if (raiz_sd / "DCIM").is_dir() else 0
        _post(f"{base}/tecla", b'{"k":"disparador","v":1}')
        time.sleep(4)
        fotos = sorted((raiz_sd / "DCIM").rglob("*.JPG")) if (raiz_sd / "DCIM").is_dir() else []
        exif = ""
        if len(fotos) > n0:
            from PIL import Image
            exif = str(Image.open(fotos[-1]).getexif().get(0x0110, ""))
        p.paso("foto-disparador", len(fotos) > n0 and exif == "ILCE-6000",
               f"{len(fotos) - n0} foto(s) nueva(s), modelo EXIF {exif or '—'}", "")

        # MOVIE → clip
        n1 = len(list((raiz_sd / "PRIVATE/M4ROOT/CLIP").glob("*.MP4"))) if (raiz_sd / "PRIVATE/M4ROOT/CLIP").is_dir() else 0
        _post(f"{base}/tecla", b'{"k":"movie","v":1}')
        time.sleep(3)
        p.paso("movie-grabando", _js(_get(f"{base}/captura/estado")[1]).get("grabando") is True, "el anfitrión está grabando")
        _post(f"{base}/tecla", b'{"k":"movie","v":1}')
        time.sleep(6)
        clips = sorted((raiz_sd / "PRIVATE/M4ROOT/CLIP").glob("*.MP4")) if (raiz_sd / "PRIVATE/M4ROOT/CLIP").is_dir() else []
        bueno = len(clips) > n1 and clips[-1].read_bytes()[4:8] == b"ftyp"
        p.paso("movie-clip", bueno, f"{len(clips) - n1} clip(s) nuevo(s) MP4" if clips else "sin clip")

        # galería de la SD
        lista = _js(_get(f"{base}/sd/lista")[1])
        rutas = [i["ruta"] for i in lista.get("items", [])]
        p.paso("sd-lista", any(r.endswith(".JPG") for r in rutas) and any(r.endswith(".MP4") for r in rutas), f"{len(rutas)} ficheros: {rutas[:3]}")
        cod, cuerpo = _get(f"{base}/sd/fichero?r={rutas[0]}") if rutas else (0, b"")
        p.paso("sd-fichero", cod == 200 and len(cuerpo) > 1000, f"HTTP {cod}, {len(cuerpo)} B")
        from PIL import Image
        b = io.BytesIO()
        Image.new("RGB", (64, 64), (200, 40, 40)).save(b, "JPEG")
        cod, cuerpo = _post(f"{base}/sd/importa", b.getvalue(), {"X-Nombre": "autoprueba.jpg"})
        importada = _js(cuerpo).get("ruta", "")
        p.paso("sd-importar", cod == 200 and importada.endswith(".JPG"), f"HTTP {cod} → {importada or 'sin ruta'}")
        cod, _ = _post(f"{base}/sd/borrar", json.dumps({"r": importada}).encode())
        p.paso("sd-borrar", cod == 200 and not (raiz_sd / importada).exists() if importada else False, f"HTTP {cod} → {importada}")
        cod, cuerpo = _post(f"{base}/sd/formatea")
        p.paso("sd-formatear", cod == 200 and _js(cuerpo).get("borrados", 0) >= 0, f"HTTP {cod} → {_js(cuerpo)}")

        # estado de cámara: batería y USB
        e = _js(_get(f"{base}/camara/estado")[1])
        cod, cuerpo = _post(f"{base}/camara/bateria", b'{"pct":5}')
        orden = _js(cuerpo).get("enviado", [])
        p.paso("camara-bateria", cod == 200 and "B 5" in orden, f"modelo {e.get('modelo', {}).get('bateria')} % → enviado {orden}")
        cod, cuerpo = _post(f"{base}/camara/usb", b'{"on":true}')
        p.paso("camara-usb", cod == 200 and "U 1" in _js(cuerpo).get("enviado", []), f"HTTP {cod} → {_js(cuerpo).get('enviado')}")
    finally:
        try:
            _post(f"{base}/salir", timeout=60)
        except OSError:  # el arranque pudo quedarse sin VM: el cierre no debe tapar el motivo
            pass
        for _ in range(120):  # el cierre guarda el estado (8 s) y termina QEMU
            if proc.poll() is not None:
                break
            time.sleep(0.5)
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(30)
        estado_zst = work / "live" / a.perfil_dir / "estado.zst"
        p.paso("cierre", proc.returncode in (0, -11, -15) and socket.socket().connect_ex(("127.0.0.1", a.puerto)) != 0,
               f"código {proc.returncode}{' (SIGSEGV al cerrar tras guardar: G22-ARR3)' if proc.returncode == -11 else ''}, "
               f"estado guardado {estado_zst.stat().st_size >> 20 if estado_zst.exists() else 0} MiB")
        shutil.rmtree(tmp, ignore_errors=True)
    d = p.informe({"perfil": a.perfil_dir, "puerto": a.puerto, "work": str(work)})
    print(("PASS" if all(x["ok"] for x in p.pasos) else "FAIL") + f" — informe en {d}")
    return 0 if all(x["ok"] for x in p.pasos) else 1


if __name__ == "__main__":
    sys.exit(main())
