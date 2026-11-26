#!/usr/bin/env python3
"""Lanzador del emulador de la A6000 (G22-E/T3): página de configuración previa al arranque; «Iniciar» lanza `live.py` con ese perfil.

uso: lanzador.py [--puerto 8700] [--puerto-vm 8600] [--work DIR] [--config JSON] [--perfil-dir NOMBRE]
  Sirve http://127.0.0.1:8700 con seis pestañas (firmware/perfil, teclas, sensor, SD, red y cámara) y guarda
  ~/.config/a6000-emu/config.json. «Iniciar» arranca live.py (restaura el estado del perfil si existe) en --puerto-vm; el enlace
  «Configurador» de esa ventana guarda el estado, cierra la VM y vuelve aquí. Solo toca el proceso que él mismo lanzó (PID propio).
  Las pestañas SD y Cámara hablan con la VM por /api/vm/<ruta de live.py> (reenvío en el servidor, sin CORS): si la VM no está
  arrancada la página lo dice y enseña lo configurado, sin inventar el dato.
"""
import argparse
import json
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import emu_config as E

WORK = HERE.parents[2] / "analysis/gui/g22/harness"
PREFIJOS_VM = ("/sd/", "/camara/", "/estado")  # rutas de live.py que usa el configurador (pestañas SD y Cámara, y el estado en vivo)
AUDITA = HERE / "audita_cfw.py"  # auditor de CFW instalables: el configurador solo lo lanza, no reimplementa sus etapas
AUDIT_UI = "audit-ui"  # AUDIT_UI/<fecha>-<artefacto>/ = carpeta de salida (--salida) de cada auditoría lanzada desde la página


class VmApagada(ValueError):
    """La VM no está en marcha o no contesta: el mensaje va tal cual a la página."""


class Ocupado(ValueError):
    """Ya hay una auditoría en marcha: el configurador solo admite una a la vez (HTTP 409)."""


def ahora() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def qemu_en_marcha() -> int:
    """Cuántos `qemu-system-arm` hay en el sistema (el auditor solo arranca con menos de 2: lo avisa la página)."""
    try:
        import audita_cfw
        return len(audita_cfw.qemu_activos())
    except (OSError, ImportError):
        return 0


def comando_auditoria(ruta: Path, destino: Path, *, completo: bool, arranque: bool) -> list[str]:
    """CLI equivalente de `audita_cfw.py`: por defecto `--rapido --sin-arranque`, informes en `--salida` (la carpeta del trabajo).

    `-u` = sin búfer: la consola de la auditoría llega línea a línea a la página en vez de aparecer al terminar.
    """
    return [sys.executable, "-u", str(AUDITA), str(ruta), "--completo" if completo else "--rapido",
            "--arranque" if arranque else "--sin-arranque", "--salida", str(destino)]


def valida_ruta_auditable(work: Path, ruta: str) -> tuple[Path, str]:
    """(ruta absoluta, tipo) de lo que se puede auditar; `ValueError` con el motivo si no.

    Acepta exactamente lo que acepta `audita_cfw.detecta_tipo` —`.dat`, directorio de paquete con
    `nflasha15`/`nflasha15.bin`, esa imagen suelta u overlay con `cam/usr`— y no inventa un segundo criterio: la
    ruta relativa se resuelve contra el directorio de trabajo del arnés, así vale tal cual lo que guarda `importa_dat`.
    """
    texto = (ruta or "").strip()
    if not texto:
        raise ValueError("falta la ruta a auditar (.dat, paquete con nflasha15, nflasha15.bin u overlay)")
    r = Path(texto).expanduser()
    if not r.is_absolute():
        r = work / r
    r = r.resolve()
    tipo = _auditor().detecta_tipo(r)  # EntradaError (ValueError) si no existe o no es un CFW reconocible
    if tipo == "dat" and r.suffix.lower() != ".dat":
        raise ValueError(f"{r.name}: un paquete de Sony debe llamarse .dat")
    if tipo == "nflasha15" and not r.name.startswith("nflasha15"):
        raise ValueError(f"{r.name}: la imagen suelta debe llamarse nflasha15 o nflasha15.bin")
    if tipo == "overlay" and (work / "pkgdat").resolve() in r.parents and not any(
            (r / n).is_file() for n in ("audit-cfw.json", "MANIFEST.json")):
        # `importa_dat` deja en pkgdat/ un overlay PARCIAL (solo lo distinto de Sony): como /usr completo marcaría
        # como «quitados» todos los ficheros de Sony, un FALLO falso. Se audita el .dat original.
        raise ValueError(f"{r.name}: overlay parcial de un .dat importado (solo lo distinto de Sony: se audita el "
                         ".dat original por su ruta, o el paquete con su audit-cfw.json)")
    return r, tipo


def _auditor():
    """Módulo `audita_cfw` (import perezoso: el configurador no carga criptografía ni fwtool si no se audita)."""
    import audita_cfw
    return audita_cfw


class Auditor:
    """Un trabajo de `audita_cfw.py` como subproceso: consola, código de salida, informe JSON/Markdown y estado en vivo."""

    def __init__(self, work: Path) -> None:
        self.work = work
        self.arch = work.parent  # analysis/gui/g22: donde el CLI deja `audit-<AAAAMMDD>-<sha8>.json` (historial)
        self.p: subprocess.Popen | None = None
        self.ruta, self.tipo, self.comando = "", "", ""
        self.destino: Path | None = None
        self.codigo: int | None = None
        self.salida: list[str] = []
        self.inicio, self.fin = "", ""
        self.informe: dict | None = None
        self.completo = self.arranque = False
        self.lock = threading.Lock()

    def corriendo(self) -> bool:
        return self.p is not None and self.p.poll() is None

    def estado(self) -> dict:
        """Lo que enseña la página: {corriendo, ruta, codigo, salida, informe, inicio, fin} y el detalle del trabajo."""
        return {"corriendo": self.corriendo(), "ruta": self.ruta or None, "codigo": self.codigo,
                "salida": "".join(self.salida), "informe": self.informe, "inicio": self.inicio or None,
                "fin": self.fin or None, "tipo": self.tipo or None, "completo": self.completo,
                "arranque": self.arranque, "destino": str(self.destino) if self.destino else None,
                "comando": self.comando, "qemu": qemu_en_marcha()}

    def lanzar(self, ruta: str, *, completo: bool = False, arranque: bool = False) -> dict:
        """Arranca la auditoría (una a la vez). 409 → `Ocupado`; ruta inválida → `ValueError`."""
        with self.lock:
            destino_ruta, tipo = valida_ruta_auditable(self.work, ruta)  # primero el motivo exacto (400), luego el turno
            if self.corriendo():
                raise Ocupado(f"ya hay una auditoría en marcha ({self.ruta}); espera a que acabe")
            self.completo, self.arranque = bool(completo or arranque), bool(arranque)
            destino = self.work / AUDIT_UI / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{_slug(destino_ruta)}"
            destino.mkdir(parents=True, exist_ok=True)
            cmd = comando_auditoria(destino_ruta, destino, completo=self.completo, arranque=self.arranque)
            self.ruta, self.tipo, self.destino, self.comando = str(destino_ruta), tipo, destino, " ".join(cmd)
            self.codigo, self.informe, self.salida = None, None, []
            self.inicio, self.fin = ahora(), ""
            self.p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True, bufsize=1)
            threading.Thread(target=self._bombea, daemon=True).start()
            avisos = ["tarda ≈50 s con --rapido (etapas 1–2) y ≈3 min con --completo"] if self.completo else \
                     ["--rapido: solo contenedor y /USR (≈50 s); ni estructura ni arranque"]
            if self.arranque:
                avisos.append(f"arranque real en QEMU: necesita un hueco (hay {qemu_en_marcha()} qemu-system-arm; "
                              "el auditor solo arranca con menos de 2 y espera hasta 15 min)")
            return {**self.estado(), "avisos": avisos}

    def _bombea(self) -> None:
        p = self.p
        assert p is not None and p.stdout is not None
        try:
            for linea in p.stdout:
                self.salida.append(linea)
                if len(self.salida) > 4000:  # una auditoría escribe ~200 líneas; el tope solo evita crecer sin fin
                    del self.salida[:1000]
        finally:
            self.codigo = p.wait()
            self.fin = ahora()
            self.informe = self._localiza()

    def _localiza(self) -> dict | None:
        """Informe JSON que dejó el auditor en la carpeta del trabajo, reducido a lo que pinta la página."""
        if self.destino is None or not self.destino.is_dir():
            return None
        jsons = sorted((p for p in self.destino.glob("audit-*.json") if p.is_file()),
                       key=lambda p: p.stat().st_mtime)
        if not jsons:
            return None
        fichero = jsons[-1]
        try:
            r = json.loads(fichero.read_text())
        except (OSError, ValueError):
            return None
        if not isinstance(r, dict):
            return None
        md = Path(str(r.get("markdown") or ""))
        usr = r.get("usr") or {}
        return {"f": self.rel(fichero), "json": str(fichero),
                "markdown": str(md) if md.is_file() else "",
                "markdown_f": self.rel(md) if md.is_file() else "",
                "veredicto": r.get("veredicto", ""), "version": r.get("version", ""), "sha256": r.get("sha256", ""),
                "fecha": r.get("fecha", ""), "coste_s": r.get("coste_s"),
                "checks": [{k: c.get(k) for k in ("id", "etapa", "ok", "aviso", "evidencia", "detalle")}
                           for c in r.get("checks") or [] if isinstance(c, dict)],
                "usr": {k: len(usr.get(k) or []) for k in ("anadidos", "cambiados", "quitados")},
                "arranque": bool(r.get("arranque"))}

    def rel(self, ruta: Path) -> str:
        """Ruta del informe relativa a la raíz de auditorías (es lo que viaja en `?f=`); '' si está fuera."""
        try:
            return ruta.resolve().relative_to(self.arch.resolve()).as_posix()
        except (ValueError, OSError):
            return ""

    def informe_fichero(self, f: str) -> tuple[str, bytes]:
        """Contenido de un informe del trabajo o del historial: solo `.json`/`.md` dentro de las carpetas de auditoría."""
        if not (f or "").strip():
            raise ValueError("falta el fichero del informe (?f=…)")
        r = Path(f).expanduser()
        r = (r if r.is_absolute() else self.arch / r).resolve()
        if r.suffix.lower() not in (".json", ".md"):
            raise ValueError(f"{f}: solo se sirven informes .json o .md")
        en_raiz = r.parent == self.arch.resolve() and r.name.startswith("audit-") and r.suffix == ".json"
        if not (en_raiz or r.parent.parent == (self.work / AUDIT_UI).resolve()):
            raise ValueError(f"{f}: fuera de las carpetas de auditoría del configurador")
        if not r.is_file():
            raise ValueError(f"{f}: no existe")
        tipo = "application/json; charset=utf-8" if r.suffix == ".json" else "text/markdown; charset=utf-8"
        return tipo, r.read_bytes()

    def historial(self) -> dict:
        """Auditorías ya hechas: `audit-*.json` de la raíz de G22 (CLI) y de cada carpeta `audit-ui/` (configurador)."""
        fichas = [*sorted(self.arch.glob("audit-*.json")), *sorted((self.work / AUDIT_UI).glob("*/audit-*.json"))]
        items = []
        for p in fichas:
            if not p.is_file():
                continue
            item = {"f": self.rel(p), "nombre": p.name, "fecha": "", "fecha_fuente": "informe", "veredicto": "",
                    "version": "", "sha256": "", "ruta": "", "coste_s": None, "markdown": "", "error": ""}
            try:
                j = json.loads(p.read_text())
            except (OSError, ValueError) as e:
                item["error"] = f"{type(e).__name__}: {e}"
            else:
                if not isinstance(j, dict):
                    item["error"] = "el informe no es un objeto JSON"
                else:
                    md = Path(str(j.get("markdown") or ""))
                    item.update({"fecha": j.get("fecha", ""), "veredicto": j.get("veredicto", ""),
                                 "version": j.get("version", ""), "sha256": j.get("sha256") or j.get("dat_sha256", ""),
                                 "ruta": j.get("ruta", ""), "coste_s": j.get("coste_s"),
                                 "markdown": self.rel(md) if md.is_file() else ""})
            if not item["fecha"]:  # informe antiguo o ilegible: la fecha del fichero, y se dice de dónde sale
                item["fecha"] = datetime.fromtimestamp(p.stat().st_mtime).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
                item["fecha_fuente"] = "fichero"
            items.append(item)
        items.sort(key=lambda it: str(it["fecha"]), reverse=True)
        return {"auditorias": items, "vacio": not items, "raiz": str(self.arch),
                "carpetas": [str(self.arch), str(self.work / AUDIT_UI)]}


def _slug(ruta: Path) -> str:
    base = ruta.name or "cfw"
    limpio = "".join(c if (c.isalnum() or c in "-_") else "-" for c in base)[:40].strip("-")
    return limpio or "cfw"


class Emulador:
    def __init__(self, work: Path, config: Path, puerto: int, puerto_vm: int, perfil: str) -> None:
        self.work, self.config, self.puerto, self.puerto_vm, self.perfil = work, config, puerto, puerto_vm, perfil
        self.p: subprocess.Popen | None = None
        self.t0: float | None = None  # arranque del proceso de la VM, para el uptime que enseña la página
        self.lock = threading.Lock()
        self.auditor = Auditor(work)  # auditoría de CFW como subproceso (pestaña Firmware)
        self.importado: dict | None = None  # último .dat importado: se ofrece para auditar sin volver a subirlo

    @property
    def url_vm(self) -> str:
        return f"http://127.0.0.1:{self.puerto_vm}/"

    def corriendo(self) -> bool:
        return self.p is not None and self.p.poll() is None

    def pide_vm(self, metodo: str, ruta: str, cuerpo: bytes | None = None, tipo: str | None = None,
                cabeceras: dict[str, str] | None = None, timeout: float = 10) -> tuple[int, str, bytes]:
        """Reenvía `metodo ruta` (con su query) a la VM y devuelve (código, tipo, cuerpo); los errores HTTP de la VM se devuelven tal cual."""
        if not self.corriendo():
            raise VmApagada("la VM no está en marcha: arranca el emulador para verla")
        if not ruta.startswith(PREFIJOS_VM):
            raise ValueError(f"ruta no permitida: {ruta}")
        req = urllib.request.Request(self.url_vm.rstrip("/") + ruta, data=cuerpo, method=metodo)
        if tipo:
            req.add_header("Content-Type", tipo)
        for k, v in (cabeceras or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.headers.get("Content-Type", "application/octet-stream"), r.read()
        except urllib.error.HTTPError as e:  # 404/400 de la VM: se reenvían para que la página enseñe el aviso
            return e.code, e.headers.get("Content-Type", "application/octet-stream"), e.read()
        except OSError as e:
            raise VmApagada(f"la VM no responde en {self.url_vm}: {e}") from e

    def estado_vm(self) -> dict:
        """GET /estado de live.py (texto y fotogramas); {} si la VM aún no contesta."""
        try:
            return json.loads(self.pide_vm("GET", "/estado", timeout=2)[2])
        except (ValueError, OSError):
            return {}

    def estado(self) -> dict:
        corriendo = self.corriendo()
        est: dict = {"corriendo": corriendo, "url": self.url_vm, "pid": self.p.pid if corriendo and self.p else None,
                     "perfil": self.perfil, "uptime": None, "fotogramas": None, "texto": ""}
        if corriendo:
            est["uptime"] = round(time.monotonic() - self.t0, 1) if self.t0 else None
            vm = self.estado_vm()
            est["texto"], est["fotogramas"] = vm.get("texto", ""), vm.get("fotogramas")
        return est

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
                if (a3 := Path(pkg + ".nflasha3")).is_file():  # E2E-1: el av-cam del mismo paquete (junto al overlay, lo deja importa_dat)
                    cmd += ["--avcam-de", str(a3)]
            if self.perfil:
                cmd += ["--perfil-dir", self.perfil]
            log = open(self.work / "lanzador-vm.log", "ab")  # noqa: SIM115 - lo hereda el proceso hijo
            self.p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=log)
            self.t0 = time.monotonic()
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
            self.t0 = None
            return "detenida"


PAGINA = r"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Emulador A6000</title><style>
:root{--bg:#14161a;--card:#1d2026;--fg:#e4e6ea;--mut:#8b93a0;--acc:#e8732a;--ok:#5cc07a;--bad:#e5645a;--line:#2d323b}
@media(prefers-color-scheme:light){:root{--bg:#f3f4f6;--card:#fff;--fg:#1c1f24;--mut:#68707c;--line:#d9dce2}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}
h1{margin:0;font-size:22px}h2{margin:0 0 10px;font-size:17px}
h3{margin:16px 0 6px;font-size:13px;color:var(--mut);text-transform:uppercase;letter-spacing:.04em}
code{font-family:ui-monospace,monospace;font-size:.92em}a{color:var(--acc)}
:focus-visible{outline:2px solid var(--acc);outline-offset:2px}[hidden]{display:none!important}
.mut{color:var(--mut);font-size:13px}
header{padding:16px 24px 4px}
.cab{display:flex;gap:18px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;max-width:1000px;margin:0 auto}
.cab p{margin:3px 0 0;color:var(--mut);font-size:13px;max-width:520px}
.estado{display:flex;gap:8px;align-items:center;flex-wrap:wrap;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 12px;max-width:560px;font-size:13px}
.estado #estado-det{font-size:12px;color:var(--mut)}
.luz{width:10px;height:10px;border-radius:50%;background:var(--bad);box-shadow:0 0 6px var(--bad)}
.luz.on{background:var(--ok);box-shadow:0 0 6px var(--ok)}
nav[role=tablist]{display:flex;gap:4px;flex-wrap:wrap;max-width:1000px;margin:12px auto 0;padding:0 16px}
nav[role=tablist] button{background:transparent;border:1px solid transparent;border-bottom:2px solid transparent;border-radius:8px 8px 0 0;padding:8px 14px;color:var(--mut);font-weight:600}
nav[role=tablist] button[aria-selected=true]{background:var(--card);border-color:var(--line);border-bottom-color:var(--acc);color:var(--fg)}
main{max-width:1000px;margin:0 auto;padding:16px 16px 90px}
section[role=tabpanel]{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
button,select,input[type=text],input[type=number]{background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 11px;font:inherit}
button{cursor:pointer}button:hover:not(:disabled){border-color:var(--acc)}button:disabled{opacity:.45;cursor:not-allowed}
button.p{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:600}
button.cap{border-color:var(--acc);color:var(--acc)}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:8px 0}
fieldset{border:0;padding:0;margin:0}
label.op{display:inline-flex;gap:6px;align-items:center;margin:4px 16px 4px 0}
table{border-collapse:collapse;width:100%}td,th{padding:6px 8px;border-top:1px solid var(--line);text-align:left}
th{font-size:12px;color:var(--mut);text-transform:uppercase}
.chip{display:inline-block;background:var(--bg);border:1px solid var(--line);border-radius:5px;padding:1px 4px 1px 8px;margin:2px 3px 2px 0;font-family:monospace}
.chip b{cursor:pointer;color:var(--bad);padding:0 5px}
.aviso{min-height:1.3em;margin:6px 0 0;font-size:13px;color:var(--mut)}
.aviso.err{color:var(--bad)}.aviso.okc{color:var(--ok)}
.galeria{display:grid;grid-template-columns:repeat(auto-fill,minmax(124px,1fr));gap:10px;margin-top:8px}
.mini{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:6px;display:flex;flex-direction:column;gap:4px;font-size:12px}
.mini img{width:100%;height:84px;object-fit:cover;border-radius:4px;background:#000}
.mini .noimg{margin:0;height:84px;display:flex;align-items:center;justify-content:center;background:var(--card);border-radius:4px;color:var(--mut);font-family:monospace}
.mini .nom{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mini .tam{font-size:11px;color:var(--mut)}
.mini button.x{font-size:11px;padding:3px 6px}
footer{position:fixed;left:0;right:0;bottom:0;background:var(--card);border-top:1px solid var(--line);padding:10px 24px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
footer #msg{flex:1;min-width:180px;margin:0}
#audlog{max-height:240px;overflow:auto;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:8px;margin:8px 0 0;font:12px/1.35 ui-monospace,monospace;white-space:pre-wrap}
#audtab td:first-child{font-family:ui-monospace,monospace;font-size:12px;white-space:nowrap}
#audtab td:nth-child(2){white-space:nowrap}
.vok{color:var(--ok)}.vbad{color:var(--bad)}.vavo{color:var(--acc)}
</style></head><body>
<header><div class="cab"><div><h1>Emulador Sony A6000</h1><p>Configura firmware, teclas, sensor, SD, red y cámara antes de arrancar la UI en QEMU.</p></div>
<div class="estado" role="status" aria-live="polite"><span class="luz" id="luz" aria-hidden="true"></span><b id="estado-txt">VM parada</b>
<span id="estado-det">comprobando…</span><a id="vmurl" href="#" hidden>Abrir ventana del emulador →</a></div></div></header>
<nav role="tablist" aria-label="Secciones del configurador">
<button role="tab" id="tab-firmware" aria-controls="p-firmware" aria-selected="true" tabindex="0">Firmware</button>
<button role="tab" id="tab-teclas" aria-controls="p-teclas" aria-selected="false" tabindex="-1">Teclas</button>
<button role="tab" id="tab-sensor" aria-controls="p-sensor" aria-selected="false" tabindex="-1">Sensor</button>
<button role="tab" id="tab-sd" aria-controls="p-sd" aria-selected="false" tabindex="-1">SD</button>
<button role="tab" id="tab-red" aria-controls="p-red" aria-selected="false" tabindex="-1">Red</button>
<button role="tab" id="tab-camara" aria-controls="p-camara" aria-selected="false" tabindex="-1">Cámara</button>
</nav><main>
<section role="tabpanel" id="p-firmware" aria-labelledby="tab-firmware" tabindex="0"><h2>Firmware y perfil</h2>
<fieldset><legend class="mut">Origen</legend>
<label class="op"><input type="radio" name="or" value="sony"> Sony 3.21 de serie</label>
<label class="op"><input type="radio" name="or" value="overlay"> Overlay CFW existente</label>
<label class="op"><input type="radio" name="or" value="dat"> Paquete <code>.dat</code> importado</label></fieldset>
<div class="row"><label for="ov">Overlay</label><select id="ov"></select>
<span class="mut">Paquete importado:</span><b id="datsel" class="mut">ninguno</b></div>
<h3>Importar paquete <code>.dat</code></h3>
<div class="row"><label for="fdat">Fichero</label><input type="file" id="fdat" accept=".dat">
<label for="rdat" class="mut">o ruta</label><input type="text" id="rdat" size="34" placeholder="/ruta/FirmwareData.dat">
<button id="imp">Importar</button></div>
<p class="aviso" id="impmsg" role="status" aria-live="polite"></p>
<p class="mut">El <code>.dat</code> se descifra y valida (paquete A6000 íntegro) y se reduce a un overlay de ficheros distintos de Sony; no se instala nada.
Un perfil nuevo arranca en frío (≈ 2 min) y después se restaura en segundos.</p>
<h3>Auditoría del CFW en el arnés</h3>
<div class="row"><label for="audruta">Artefacto</label>
<input type="text" id="audruta" size="44" placeholder=".dat, paquete con nflasha15, nflasha15.bin u overlay cam/usr">
<button id="audusa">Usar el importado</button></div>
<div class="row"><label class="op"><input type="checkbox" id="audcomp"> incluir estructura (etapa 3, más lenta)</label>
<button id="aud1" class="p">Auditar el .dat</button><button id="aud2" class="cap">Auditar con arranque</button>
<button id="audref">Refrescar historial</button></div>
<p class="aviso" id="audmsg" role="status" aria-live="polite"></p>
<div id="audres" hidden>
<p class="row"><b id="audver">—</b><span class="mut" id="auddet"></span></p>
<p class="mut" id="audlinks"></p>
<table id="audtab"></table>
<pre id="audlog" tabindex="0" aria-label="consola de la auditoría"></pre>
<p class="mut" id="audlim">Un fallo (✗) de esta tabla es del <b>CFW</b>, no de la cámara: se detecta en el arnés antes de instalar nada.
Un ✓ tampoco demuestra que funcione en la cámara —el arnés emula la UI con un kernel ajeno, un shim y una imagen de sensor sintética;
el LDEC real, Darwin, el flasheo, la NVRAM no declarada, el hardware y los layouts <code>.uxc</code> quedan fuera—. Límites:
<code>docs/gui/g22-auditoria-cfw.md</code> §5. ? = no demostrable (nunca se presenta como OK).</p>
</div>
<h3>Auditorías anteriores</h3>
<table id="audhist"></table><p class="mut" id="audhmsg" role="status" aria-live="polite"></p>
<p class="mut">La auditoría la hace <code>scripts/gui/harness/audita_cfw.py</code> como subproceso (misma herramienta que por CLI):
una sola a la vez, sin flashear ni escribir firmware, y con el <code>.dat</code> o el paquete tal cual están en disco.</p></section>
<section role="tabpanel" id="p-teclas" aria-labelledby="tab-teclas" tabindex="0" hidden><h2>Mapa de teclas</h2>
<p class="mut">Pulsa «Capturar» y luego la tecla del teclado. Un botón puede tener varias teclas; una tecla, un solo botón.
Solo figuran los botones con código de cámara medido; se añaden al ampliar <code>TECLAS</code> de <code>live.py</code>.</p>
<table id="tt"></table><p class="aviso" id="teclasmsg" role="status" aria-live="polite"></p>
<div class="row"><button id="rst">Restablecer teclas por defecto</button></div></section>
<section role="tabpanel" id="p-sensor" aria-labelledby="tab-sensor" tabindex="0" hidden><h2>Fuente del sensor</h2>
<div class="row"><label for="sfu">Fuente</label>
<select id="sfu"><option value="imagen">Imagen</option><option value="video">Vídeo</option><option value="webcam">Webcam</option></select>
<label for="sru">Ruta</label><input type="text" id="sru" size="40" placeholder="imagen o vídeo del anfitrión (opcional)"></div>
<p class="mut">Es la fuente inicial de la ventana en vivo; allí se cambia en caliente (imagen, vídeo en bucle o cámara web, que pide permiso al navegador). La imagen se compone bajo la OSD en 3:2 y se guarda tal cual entra: la cámara no la procesa (sin Picture Profile).</p></section>
<section role="tabpanel" id="p-sd" aria-labelledby="tab-sd" tabindex="0" hidden><h2>Tarjeta SD</h2>
<div class="row"><label for="sgb">Tamaño</label><input type="number" id="sgb" min="1" max="2048" step="1" style="width:90px"><span class="mut">GB</span>
<label for="sca">Carpeta</label><input type="text" id="sca" size="34" placeholder="vacío = ~/A6000-SD"></div>
<p class="mut">Disparo (botón «disparador») y MOVIE los guarda el anfitrión en esa carpeta con la estructura de la A6000 (<code>DCIM/100MSDCF/DSC00001.JPG</code>, <code>PRIVATE/M4ROOT/CLIP/C0001.MP4</code>); no se escribe si se supera el tamaño.</p>
<h3>Contenido de la SD del emulador</h3><p class="mut" id="sdconf"></p>
<div class="row"><label for="sdsub">Subir fichero</label><input type="file" id="sdsub" accept="image/*,video/*">
<button id="sdref">Actualizar</button><button id="sdform">Formatear…</button></div>
<p class="aviso" id="sdmsg" role="status" aria-live="polite"></p><div class="galeria" id="sdlista"></div>
<p class="mut">La lista, las miniaturas, la subida, el borrado y el formato los hace el emulador en marcha (<code>/sd/lista</code>, <code>/sd/fichero</code>, <code>/sd/importa</code>, <code>/sd/borrar</code>, <code>/sd/formatea</code>).</p></section>
<section role="tabpanel" id="p-red" aria-labelledby="tab-red" tabindex="0" hidden><h2>Red</h2>
<div class="row"><label class="op"><input type="checkbox" id="rte"> Telnet</label>
<label class="op"><input type="checkbox" id="rwi"> Wi-Fi por red local</label>
<label for="rpu">Puerto telnet</label><input type="number" id="rpu" min="1024" max="65535" style="width:90px"></div>
<p class="mut">La A6000 solo ofrece telnet (OpenMemories Tweak, puerto 23, root) por Wi-Fi; aquí el invitado tiene una interfaz <code>ath0</code> en la red del ordenador (slirp) y <code>telnetd</code> del busybox de la cámara llega por <code>127.0.0.1:puerto</code>. Cambiar la red reinicia en frío (≈ 2 min). Sin adb: el firmware no trae <code>adbd</code>. El menú Inalámbrico no se activa (ver la guía).</p></section>
<section role="tabpanel" id="p-camara" aria-labelledby="tab-camara" tabindex="0" hidden><h2>Cámara: batería, USB y HDMI</h2>
<div class="row"><label for="cbt">Batería</label><input type="number" id="cbt" min="0" max="100" step="1" style="width:90px"><span class="mut">%</span></div>
<div class="row"><label class="op"><input type="checkbox" id="cusb"> USB conectado</label>
<label class="op"><input type="checkbox" id="chdmi"> HDMI conectado</label></div>
<div class="row"><button id="camlee">Leer del emulador</button><button id="camapi">Aplicar al emulador</button></div>
<p class="aviso" id="camsg" role="status" aria-live="polite"></p>
<p class="mut">Se guardan en la config (sección <code>camara</code>) y, con la VM en marcha, se leen de <code>/camara/estado</code> y se envían a
<code>/camara/bateria</code>, <code>/camara/usb</code> y <code>/camara/hdmi</code> con cuerpo <code>{"valor": …}</code>.</p></section>
</main><footer><button class="p" id="go">▶ Iniciar</button><button id="stop" disabled>■ Parar</button>
<button id="quit">Cerrar emulador</button><span class="aviso" id="msg" role="status" aria-live="polite"></span></footer>
<script>
const $=id=>document.getElementById(id);
let cfg=null,botones=[],cap=null,ultimo={corriendo:false};
const api=async(u,o)=>{const r=await fetch(u,o);const t=await r.text();let j;try{j=JSON.parse(t)}
catch(e){j={error:/^\s*</.test(t)?'la VM no ofrece este punto (HTTP '+r.status+')':t}}if(!r.ok)throw new Error(j.error||t);return j};
const aviso=(id,t,c)=>{const e=$(id);e.textContent=t;e.className='aviso '+(c||'')};
const msg=(t,c)=>aviso('msg',t,c);
const hms=s=>{s=Math.max(0,Math.round(s));const h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;
return h?h+':'+String(m).padStart(2,'0')+':'+String(x).padStart(2,'0'):m+':'+String(x).padStart(2,'0')};
/* --- pestañas: clic y teclado (flechas, Inicio, Fin) --- */
const TABS=[...document.querySelectorAll('[role=tab]')];
function activa(tab,foco){for(const t of TABS){const on=t===tab;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;$(t.getAttribute('aria-controls')).hidden=!on}
if(foco)tab.focus();if(tab.id=='tab-sd')sdLista();if(tab.id=='tab-camara')camLee();if(tab.id=='tab-firmware')audHistorial()}
TABS.forEach((t,i)=>{t.onclick=()=>activa(t);t.onkeydown=e=>{if(cap)return;let j=null;
if(e.key=='ArrowRight')j=(i+1)%TABS.length;else if(e.key=='ArrowLeft')j=(i-1+TABS.length)%TABS.length;
else if(e.key=='Home')j=0;else if(e.key=='End')j=TABS.length-1;
if(j!==null){e.preventDefault();activa(TABS[j],true)}}});
/* --- estado en vivo de la VM --- */
function pintaEstado(v){ultimo=v||{};const on=!!v.corriendo;const d=[];
$('luz').className='luz'+(on?' on':'');$('estado-txt').textContent=on?'VM en marcha':'VM parada';
if(on){if(v.uptime!=null)d.push('uptime '+hms(v.uptime));if(v.fotogramas!=null)d.push(v.fotogramas+' fotogramas');
if(v.pid)d.push('PID '+v.pid);if(v.texto)d.push(v.texto)}
else d.push('pulsa «Iniciar» para arrancar la UI en QEMU');
$('estado-det').textContent=d.join(' · ');
const a=$('vmurl');a.hidden=!on;if(on)a.href=v.url;
$('go').disabled=on;$('stop').disabled=!on;$('sdform').disabled=!on;$('sdsub').disabled=!on;$('sdref').disabled=!on}
async function vigila(){try{pintaEstado(await api('/api/estado'))}catch(e){$('estado-det').textContent='sin conexión con el configurador'}}
/* --- config --- */
function pinta(){const f=cfg.firmware;const r=document.querySelector('[name=or][value='+f.origen+']');if(r)r.checked=true;
$('ov').value=f.overlay;$('datsel').textContent=f.dat||'ninguno';
$('sfu').value=cfg.sensor.fuente;$('sru').value=cfg.sensor.ruta;
$('sgb').value=cfg.sd.tamano_gb;$('sca').value=cfg.sd.carpeta;
$('rte').checked=cfg.red.telnet;$('rwi').checked=cfg.red.wifi;$('rpu').value=cfg.red.puerto;
camPinta(cfg.camara||{bateria:100,usb:false,hdmi:false});pintaTeclas()}
function lee(){const o=document.querySelector('[name=or]:checked');if(o)cfg.firmware.origen=o.value;
cfg.firmware.overlay=$('ov').value;cfg.sensor={fuente:$('sfu').value,ruta:$('sru').value.trim()};
cfg.sd={tamano_gb:+$('sgb').value||4,carpeta:$('sca').value.trim()};
cfg.red={telnet:$('rte').checked,wifi:$('rwi').checked,puerto:+$('rpu').value||2323};
const b=+$('cbt').value;
cfg.camara={bateria:Number.isFinite(b)?Math.min(100,Math.max(0,Math.round(b))):100,usb:$('cusb').checked,hdmi:$('chdmi').checked}}
function pintaTeclas(){$('tt').innerHTML='<tr><th>Botón de la cámara</th><th>Teclas</th><th>Capturar</th></tr>';
for(const b of botones){const tr=$('tt').insertRow();tr.insertCell().textContent=b;const c=tr.insertCell();
for(const k of cfg.teclas[b]||[]){const s=document.createElement('span');s.className='chip';s.textContent=k;
const x=document.createElement('b');x.textContent='×';x.title='quitar '+k;x.onclick=()=>{cfg.teclas[b]=cfg.teclas[b].filter(y=>y!=k);guarda()};
s.append(x);c.append(s)}
const bt=document.createElement('button');bt.textContent=cap==b?'Pulsa una tecla…':'Capturar';
if(cap==b)bt.className='cap';bt.onclick=()=>{cap=cap==b?null:b;pintaTeclas()};tr.insertCell().append(bt)}}
async function guarda(){lee();try{cfg=(await api('/api/config',{method:'POST',body:JSON.stringify(cfg)})).config;msg('guardado','okc')}
catch(e){msg(e.message,'err');await carga()}pinta()}
async function carga(){const r=await api('/api/config');cfg=r.config;botones=r.botones;importado=r.importado||null;
$('ov').innerHTML=r.overlays.map(o=>'<option>'+o+'</option>').join('');
if(!cfg.firmware.overlay&&r.overlays.length)cfg.firmware.overlay=r.overlays[0];
if(!$('audruta').value&&importado&&importado.ruta_dat)$('audruta').value=importado.ruta_dat
pinta();pintaEstado(r.vm);$('sdconf').textContent='Cuota '+cfg.sd.tamano_gb+' GB · carpeta '+(cfg.sd.carpeta||'~/A6000-SD');
audSondea();audHistorial()}
/* --- SD --- */
const ES_IMG=/\.(jpe?g|png|webp|gif|bmp)$/i;
const humano=n=>n==null?'':n>=1048576?(n/1048576).toFixed(1)+' MB':n>=1024?Math.round(n/1024)+' kB':n+' B';
function ficheros(j){const l=Array.isArray(j)?j:(j&&(j.ficheros||j.lista||j.items))||[];
return l.map(e=>typeof e=='string'?{r:e}:{r:e.r||e.ruta||e.nombre||'',
bytes:typeof e.bytes=='number'?e.bytes:(typeof e.tamano=='number'?e.tamano:null)}).filter(e=>e.r)}
function miniatura(f){const d=document.createElement('div');d.className='mini';const nom=f.r.split('/').pop();
if(ES_IMG.test(f.r)){const i=document.createElement('img');i.loading='lazy';i.alt=nom;
i.src='/api/vm/sd/fichero?r='+encodeURIComponent(f.r);d.append(i)}
else{const p=document.createElement('p');p.className='noimg';p.textContent=(f.r.split('.').pop()||'?').toUpperCase();d.append(p)}
const t=document.createElement('span');t.className='nom';t.title=f.r;t.textContent=nom;d.append(t);
const b=document.createElement('span');b.className='tam';b.textContent=humano(f.bytes);d.append(b);
const x=document.createElement('button');x.className='x';x.textContent='Borrar';x.setAttribute('aria-label','Borrar '+f.r);
x.onclick=()=>sdBorra(f.r);d.append(x);return d}
async function sdLista(){const caja=$('sdlista');caja.innerHTML='';
const sd=cfg?cfg.sd:{tamano_gb:4,carpeta:''};
$('sdconf').textContent='Cuota '+sd.tamano_gb+' GB · carpeta '+(sd.carpeta||'~/A6000-SD');
if(!ultimo.corriendo){aviso('sdmsg','Arranca el emulador para ver la SD.');return}
aviso('sdmsg','leyendo la SD del emulador…');
try{const fs=ficheros(await api('/api/vm/sd/lista'));let tot=0;
if(!fs.length)caja.textContent='SD vacía.';
for(const f of fs){tot+=f.bytes||0;caja.append(miniatura(f))}
aviso('sdmsg',fs.length+' ficheros · '+humano(tot),'okc')}
catch(e){aviso('sdmsg',e.message,'err')}}
async function sdBorra(r){if(!confirm('¿Borrar '+r+' de la SD del emulador?'))return;
try{await api('/api/vm/sd/borrar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({r})});
aviso('sdmsg','borrado: '+r,'okc')}catch(e){aviso('sdmsg',e.message,'err')}sdLista()}
$('sdsub').onchange=async e=>{const f=e.target.files[0];if(!f){sdLista();return}
aviso('sdmsg','subiendo '+f.name+'…');
try{await api('/api/vm/sd/importa',{method:'POST',headers:{'X-Nombre':encodeURIComponent(f.name)},body:f});
aviso('sdmsg','subido: '+f.name,'okc')}catch(err){aviso('sdmsg',err.message,'err')}
e.target.value='';sdLista()};
$('sdref').onclick=()=>sdLista();
$('sdform').onclick=async()=>{if(!confirm('¿Formatear la SD del emulador? Se borran todos los ficheros de la carpeta.'))return;
try{await api('/api/vm/sd/formatea',{method:'POST'});aviso('sdmsg','SD formateada','okc')}
catch(e){aviso('sdmsg',e.message,'err')}sdLista()};
/* --- cámara: batería, USB y HDMI --- */
const num=(o,...ks)=>{for(const k of ks)if(typeof o[k]=='number')return o[k];return undefined};
const bol=(o,...ks)=>{for(const k of ks)if(typeof o[k]=='boolean')return o[k];return undefined};
function camPinta(c){$('cbt').value=c.bateria==null?100:c.bateria;$('cusb').checked=!!c.usb;$('chdmi').checked=!!c.hdmi}
function camMezcla(base,j){const o={...base};const b=num(j,'bateria','valor','nivel');if(b!==undefined)o.bateria=b;
const u=bol(j,'usb','conectado');if(u!==undefined)o.usb=u;const h=bol(j,'hdmi');if(h!==undefined)o.hdmi=h;return o}
async function camLee(){camPinta(cfg.camara||{bateria:100,usb:false,hdmi:false});
if(!ultimo.corriendo){aviso('camsg','La VM está parada: se muestran los valores guardados en la config.');return}
try{const j=await api('/api/vm/camara/estado');camPinta(camMezcla(cfg.camara||{},j));aviso('camsg','leído del emulador','okc')}
catch(e){aviso('camsg','el emulador no ofrece el estado de la cámara: '+e.message,'err')}}
$('camlee').onclick=()=>camLee();
$('camapi').onclick=async()=>{await guarda();if(!ultimo.corriendo){aviso('camsg','guardado en la config; con la VM parada se aplicará al arrancar');return}
const c=cfg.camara,r=[];
for(const [k,v] of [['bateria',c.bateria],['usb',c.usb],['hdmi',c.hdmi]]){
try{await api('/api/vm/camara/'+k,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({valor:v})});
r.push(k+' ok')}catch(e){r.push(k+': '+e.message)}}
aviso('camsg',r.join(' · '),r.every(x=>x.endsWith('ok'))?'okc':'err')};
/* --- teclas: captura --- */
addEventListener('keydown',e=>{if(!cap)return;e.preventDefault();const k=e.code;
for(const b in cfg.teclas){if(b!=cap&&cfg.teclas[b].includes(k)){aviso('teclasmsg',k+' ya está en «'+b+'»; quítala allí primero','err');return}}
cfg.teclas[cap]=[...new Set([...(cfg.teclas[cap]||[]),k])];cap=null;aviso('teclasmsg','');guarda()});
$('rst').onclick=async()=>{try{cfg.teclas=(await api('/api/config?defecto=1')).config.teclas;await guarda()}
catch(e){msg(e.message,'err')}};
$('imp').onclick=async()=>{const f=$('fdat').files[0],r=$('rdat').value.trim();
if(!f&&!r){aviso('impmsg','Elige un fichero o escribe una ruta.','err');return}
aviso('impmsg','descifrando y extrayendo (hasta ~30 s)…');
try{const j=f?await api('/api/dat',{method:'POST',headers:{'X-Nombre':encodeURIComponent(f.name)},body:f})
:await api('/api/dat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ruta:r})});
cfg=j.config;await carga();importado=j.importado||null;
if(importado&&importado.ruta_dat)$('audruta').value=importado.ruta_dat;
aviso('impmsg','Importado: firmware '+j.version+' (región '+j.region+'), '+j.ficheros+
' ficheros distintos de Sony → '+j.overlay+' · ya puedes auditarlo aquí mismo','okc')}catch(e){aviso('impmsg',e.message,'err')}};
/* --- auditoría del CFW: subproceso de scripts/gui/harness/audita_cfw.py, estado cada 2 s --- */
let audT=null,importado=null;
const VCLASE={OK:'vok',AVISO:'vavo',PARCIAL:'vavo',FALLO:'vbad'};
const marca=c=>c.ok===true?'✓':(c.ok===false?'✗':'?');
function audEnlace(caja,txt,f){if(!f)return;const a=document.createElement('a');
a.href='/api/auditar/informe?f='+encodeURIComponent(f);a.target='_blank';a.rel='noopener';a.textContent=txt;caja.append(a)}
function audTabla(checks){const t=$('audtab');t.innerHTML='<tr><th>Comprobación</th><th>Resultado</th><th>Detalle</th></tr>';
for(const c of checks){const tr=t.insertRow(),a=tr.insertCell(),b=tr.insertCell(),d=tr.insertCell();
a.textContent=c.id;b.textContent=marca(c)+(c.aviso?' (aviso)':'');
b.className=c.ok===false?'vbad':(c.aviso?'vavo':(c.ok===null?'mut':'vok'));d.textContent=c.detalle;d.title=c.evidencia||''}}
function audPinta(j){
const on=!!j.corriendo;$('aud1').disabled=on;$('aud2').disabled=on;$('audlog').textContent=j.salida||'';
if(on){aviso('audmsg','auditando '+(j.ruta||'')+' — '+(j.arranque?'arranque real en QEMU (≈3 min)':'solo estática (≈50 s)')+'…');
if(!audT)audT=setInterval(audSondea,2000);return}
if(audT){clearInterval(audT);audT=null}
const inf=j.informe;
if(!inf){if(j.codigo!=null){$('audres').hidden=false;aviso('audmsg','sin informe: el auditor salió con código '+j.codigo+
(j.codigo===2?' (no se pudo auditar: mira la consola)':' (revisa la consola)'),'err')}return}
$('audres').hidden=false;
$('audver').textContent='Veredicto '+inf.veredicto;$('audver').className=VCLASE[inf.veredicto]||'mut';
$('auddet').textContent=' · versión '+(inf.version||'?')+' · sha256 '+(inf.sha256||'').slice(0,12)+' · '+inf.coste_s+' s · '+
inf.checks.filter(c=>c.ok===false).length+' ✗ y '+inf.checks.filter(c=>c.ok===null).length+' ? de '+inf.checks.length+' comprobaciones'+
(inf.arranque?' · con arranque real':' · sin arranque (no probado)');
const caja=$('audlinks');caja.innerHTML='';
audEnlace(caja,'informe JSON',inf.f);if(inf.markdown_f){caja.append(' · ');audEnlace(caja,'resumen Markdown',inf.markdown_f)}
if(j.destino){caja.append(' · carpeta ');const k=document.createElement('code');k.textContent=j.destino;caja.append(k)}
audTabla(inf.checks);
aviso('audmsg',j.codigo===0?'terminada sin fallos demostrables (código 0)':'encontró fallos (código '+j.codigo+')',
j.codigo===0?'okc':'err');
audHistorial()}
async function audSondea(){try{audPinta(await api('/api/auditar/estado'))}catch(e){aviso('audmsg',e.message,'err')}}
async function audInicia(arranque){const ruta=$('audruta').value.trim();
if(!ruta){aviso('audmsg','escribe la ruta del .dat o del paquete a auditar, o pulsa «Usar el importado»','err');return}
if(arranque&&!confirm('El arranque real tarda ≈3 min, necesita un hueco de QEMU (máximo 2 en el sistema) y no sustituye a la cámara. ¿Seguir?'))return;
aviso('audmsg','lanzando la auditoría…');
try{audPinta(await api('/api/auditar',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({ruta:ruta,arranque:!!arranque,completo:$('audcomp').checked||!!arranque})}))}
catch(e){aviso('audmsg',e.message,'err')}}
$('aud1').onclick=()=>audInicia(false);
$('aud2').onclick=()=>audInicia(true);
$('audusa').onclick=()=>{const f=(importado&&importado.ruta_dat)||'';
if(!importado){aviso('audmsg','todavía no hay ningún .dat importado','err');return}
if(!f){aviso('audmsg','el .dat se subió desde el navegador y solo queda el paquete parcial ('+importado.overlay+
'): escribe la ruta del .dat original —sigue en tu disco— para auditarlo entero','err');$('audruta').value='';return}
$('audruta').value=f;aviso('audmsg','se auditará '+f,'okc')};
async function audHistorial(){const t=$('audhist');
try{const j=await api('/api/auditar/historial');t.innerHTML='';
if(j.vacio){const tr=t.insertRow().insertCell();tr.className='mut';
tr.textContent='Todavía no hay ninguna auditoría hecha: lanza la primera con «Auditar el .dat».';
$('audhmsg').textContent='se buscan audit-*.json en '+j.raiz;return}
const h=t.insertRow();for(const x of ['Fecha','Veredicto','Versión','Artefacto','Informe']){
const th=document.createElement('th');th.textContent=x;h.append(th)}
for(const a of j.auditorias){const tr=t.insertRow();
tr.insertCell().textContent=(a.fecha||'').slice(0,19).replace('T',' ');
const v=tr.insertCell();v.textContent=a.veredicto||(a.error?'ilegible':'—');v.className=VCLASE[a.veredicto]||'mut';
tr.insertCell().textContent=a.version||'—';
tr.insertCell().textContent=(a.ruta||a.nombre)+((a.sha256||'').length>8?' ('+a.sha256.slice(0,8)+')':'');
const c=tr.insertCell();audEnlace(c,'JSON',a.f);if(a.markdown){c.append(' · ');audEnlace(c,'MD',a.markdown)}
if(!a.f)c.textContent='—'}
$('audhmsg').textContent=j.auditorias.length+' auditorías (fecha del informe o, si no la trae, del fichero);'}
catch(e){$('audhmsg').textContent='historial no disponible: '+e.message}}
$('audref').onclick=()=>audHistorial();
document.querySelectorAll('#ov,#sfu,#sru,#sgb,#sca,#rte,#rwi,#rpu,#cbt,#cusb,#chdmi').forEach(e=>e.onchange=async()=>{
await guarda();if(e.id=='sca'||e.id=='sgb')sdLista()});
$('go').onclick=async()=>{lee();$('go').disabled=true;msg('arrancando… (un perfil nuevo tarda ≈ 2 min en frío)');
try{const j=await api('/api/iniciar',{method:'POST',body:JSON.stringify(cfg)});
msg('VM en marcha en '+j.url+(j.nota?' ('+j.nota+')':''),'okc');await vigila()}
catch(e){msg(e.message,'err');$('go').disabled=false}};
$('stop').onclick=async()=>{msg('guardando estado y parando…');$('stop').disabled=true;
try{const j=await api('/api/parar',{method:'POST'});msg('VM detenida ('+j.estado+')','okc')}catch(e){msg(e.message,'err')}
await vigila();sdLista()};
$('quit').onclick=async()=>{if(!confirm('¿Cerrar el emulador? Se para la VM (guardando su estado) y se cierra este servidor.'))return;
try{await fetch('/api/cerrar',{method:'POST'})}catch(e){}
document.body.innerHTML='<p style="padding:30px">Emulador cerrado. Puedes cerrar esta pestaña.</p>'};
carga().catch(e=>msg(e.message,'err'));
vigila();setInterval(vigila,3000);
</script></body></html>"""


def servidor(emu: Emulador) -> ThreadingHTTPServer:
    srv: ThreadingHTTPServer

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a: object) -> None:
            pass

        def envia(self, codigo: int, tipo: str, cuerpo: bytes) -> None:
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)

        def json(self, obj: object, codigo: int = 200) -> None:
            self.envia(codigo, "application/json; charset=utf-8", json.dumps(obj, ensure_ascii=False).encode())

        def lee(self, n: int) -> bytes:
            cuerpo = b""
            while len(cuerpo) < n:
                datos = self.rfile.read(min(1 << 20, n - len(cuerpo)))
                if not datos:
                    break
                cuerpo += datos
            return cuerpo

        def a_la_vm(self, metodo: str, cuerpo: bytes) -> None:
            """Reenvía /api/vm/<ruta de live.py> (con su query) y devuelve la respuesta tal cual."""
            ruta = self.path[len("/api/vm"):]
            if not ruta.startswith("/"):
                self.json({"error": "falta la ruta de la VM"}, 400)
                return
            cab = {k: v for k, v in self.headers.items() if k.lower() == "x-nombre"}
            try:
                codigo, tipo, datos = emu.pide_vm(metodo, ruta, cuerpo or None, self.headers.get("Content-Type"), cab)
            except VmApagada as e:
                self.json({"error": str(e)}, 503)
                return
            except (ValueError, OSError) as e:
                self.json({"error": str(e)}, 400)
                return
            self.envia(codigo, tipo, datos)

        def do_GET(self) -> None:
            ruta, _, q = self.path.partition("?")
            if ruta == "/":
                self.envia(200, "text/html; charset=utf-8", PAGINA.encode())
            elif ruta == "/api/config":
                cfg = E.valida_config({}) if q == "defecto=1" else E.carga_config(emu.config)
                self.json({"config": cfg, "botones": E.botones_conocidos(), "overlays": E.overlays(emu.work),
                           "vm": emu.estado(), "importado": emu.importado})
            elif ruta == "/api/estado":
                self.json(emu.estado())
            elif ruta == "/api/auditar/estado":
                self.json(emu.auditor.estado())
            elif ruta == "/api/auditar/historial":
                self.json(emu.auditor.historial())
            elif ruta == "/api/auditar/informe":
                try:
                    tipo, datos = emu.auditor.informe_fichero(urllib.parse.parse_qs(q).get("f", [""])[0])
                except (ValueError, OSError) as e:
                    self.json({"error": str(e)}, 400)
                    return
                self.envia(200, tipo, datos)
            elif ruta.startswith("/api/vm/"):
                self.a_la_vm("GET", b"")
            else:
                self.send_error(404)

        def do_POST(self) -> None:
            n = int(self.headers.get("Content-Length", 0) or 0)
            try:
                if self.path == "/api/dat":
                    self.json(self.importa(n))
                    return
                if self.path.startswith("/api/vm/"):
                    self.a_la_vm("POST", self.lee(n))
                    return
                cuerpo = self.lee(n)
                if self.path == "/api/config":
                    self.json({"config": E.guarda_config(json.loads(cuerpo), emu.config)})
                elif self.path == "/api/auditar":
                    d = json.loads(cuerpo or b"{}")
                    if not isinstance(d, dict):
                        raise ValueError("cuerpo JSON inválido: se espera {\"ruta\": …, \"arranque\": bool, \"completo\": bool}")
                    self.json(emu.auditor.lanzar(str(d.get("ruta") or ""), completo=bool(d.get("completo")),
                                                 arranque=bool(d.get("arranque"))), 202)
                elif self.path == "/api/iniciar":
                    self.json(emu.iniciar(json.loads(cuerpo)))
                elif self.path == "/api/parar":
                    self.json({"estado": emu.parar()})
                elif self.path == "/api/cerrar":
                    self.json({"ok": True})
                    threading.Thread(target=lambda: (emu.parar(), srv.shutdown()), daemon=True).start()
                else:
                    self.send_error(404)
            except Ocupado as e:  # una sola auditoría a la vez
                self.json({"error": str(e)}, 409)
            except (ValueError, E.DatError, OSError) as e:  # json.JSONDecodeError es ValueError
                self.json({"error": str(e)}, 400)

        def importa(self, n: int) -> dict:
            ruta_dat = ""
            if self.headers.get("Content-Type", "").startswith("application/json"):
                ruta = Path(json.loads(self.lee(n))["ruta"]).expanduser()
                if not ruta.is_file():
                    raise E.DatError(f"No existe el fichero {ruta}")
                dat = ruta.read_bytes()
                origen = ruta_dat = str(ruta)
            else:
                dat = self.lee(n)
                origen = self.headers.get("X-Nombre", "subido.dat")
            res = E.importa_dat(dat, emu.work)
            cfg = E.carga_config(emu.config)
            cfg["firmware"] = {"origen": "dat", "overlay": cfg["firmware"]["overlay"], "dat": res["overlay"]}
            # el .dat de origen se ofrece tal cual para auditarlo sin volver a subirlo; si vino del navegador solo
            # queda el paquete parcial (overlay), que no se puede auditar como /usr completo (la página lo avisa)
            emu.importado = {"origen": origen, "version": res["version"], "overlay": res["overlay"],
                             "ruta_dat": ruta_dat, "parcial": not ruta_dat}
            return {**res, "origen": origen, "config": E.guarda_config(cfg, emu.config), "importado": emu.importado}

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
    for nombre, valor in (("--puerto", a.puerto), ("--puerto-vm", a.puerto_vm)):
        if not 1024 <= valor <= 65535:
            ap.error(f"{nombre} debe estar entre 1024 y 65535")
    if a.puerto == a.puerto_vm:
        ap.error("--puerto y --puerto-vm deben ser distintos")
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
