"""G22 — configurador del arnés (`lanzador.py`): pestañas, API de estado/config, auditoría de CFW y reenvío a la VM.

Servidores reales en hilos con puerto efímero: el configurador tal cual y una VM de mentira que hace de `live.py` (solo los puntos
que usa la página). No se arranca QEMU ni se toca firmware: el auditor (`audita_cfw.py`) se ejecuta de verdad solo sobre un `.dat`
sintético de 72 B, y el resto de casos de auditoría usan un comando falso inyectado con `monkeypatch`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
import time
import types
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts/gui/harness"
sys.path.insert(0, str(HARNESS))

import lanzador as L  # el módulo no arranca nada al importarlo


def pide(url: str, metodo: str = "GET", cuerpo: bytes | None = None, cabeceras: dict[str, str] | None = None) -> tuple[int, str, bytes]:
    """Petición HTTP al configurador; los códigos de error se devuelven, no se lanzan."""
    req = urllib.request.Request(url, data=cuerpo, method=metodo, headers=cabeceras or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read()


class VMFalsa:
    """`live.py` de mentira: /estado, /sd/lista, /sd/fichero, /sd/importa, /sd/borrar, /sd/formatea y /camara/*.

    `falta` guarda las rutas que deben contestar 404 (para probar que el configurador avisa en vez de romper) y `peticiones`
    apunta (método, ruta, cuerpo, cabeceras) de todo lo recibido.
    """

    def __init__(self) -> None:
        self.peticiones: list[tuple[str, str, bytes, dict[str, str]]] = []
        self.falta: set[str] = set()
        self.camara: dict[str, object] = {"bateria": 73, "usb": True, "hdmi": False}
        vm = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a: object) -> None:
                pass

            def responde(self, obj: object, codigo: int = 200, tipo: str = "application/json; charset=utf-8") -> None:
                d = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
                self.send_response(codigo)
                self.send_header("Content-Type", tipo)
                self.send_header("Content-Length", str(len(d)))
                self.end_headers()
                self.wfile.write(d)

            def do_GET(self) -> None:
                ruta = self.path.partition("?")[0]
                vm.peticiones.append(("GET", self.path, b"", {}))
                if ruta == "/estado":
                    return self.responde({"texto": "restaurado, 12 s", "fotogramas": 34})
                if ruta in vm.falta:
                    return self.responde({"error": f"no existe {ruta}"}, 404)
                if ruta == "/sd/lista":
                    return self.responde({"raiz": "/tmp/sd", "ficheros": [
                        {"r": "DCIM/100MSDCF/DSC00001.JPG", "bytes": 4096},
                        {"r": "PRIVATE/M4ROOT/CLIP/C0001.MP4", "bytes": 8192}]})
                if ruta == "/sd/fichero":
                    return self.responde(b"\xff\xd8jpeg", tipo="image/jpeg")
                if ruta == "/camara/estado":
                    return self.responde(vm.camara)
                self.responde({"error": "404"}, 404)

            def do_POST(self) -> None:
                n = int(self.headers.get("Content-Length", 0) or 0)
                cuerpo = self.rfile.read(n) if n else b""
                vm.peticiones.append(("POST", self.path, cuerpo, dict(self.headers)))
                ruta = self.path.partition("?")[0]
                if ruta in vm.falta:
                    return self.responde({"error": f"no existe {ruta}"}, 404)
                if ruta == "/sd/importa":
                    return self.responde({"r": "DCIM/100MSDCF/" + urllib.parse.unquote(self.headers.get("X-Nombre", "subido")),
                                          "bytes": len(cuerpo)})
                if ruta in ("/sd/borrar", "/sd/formatea"):
                    return self.responde({"ok": True})
                if ruta.startswith("/camara/"):
                    valor = json.loads(cuerpo or b"{}").get("valor")
                    vm.camara[ruta.rsplit("/", 1)[-1]] = valor
                    return self.responde({ruta.rsplit("/", 1)[-1]: valor})
                self.responde({"error": "404"}, 404)

        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.puerto = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def cierra(self) -> None:
        self.srv.shutdown()
        self.srv.server_close()


@pytest.fixture()
def conf(tmp_path: Path):
    """Configurador real en un hilo (puerto efímero) con una VM falsa como `--puerto-vm`."""
    work = tmp_path / "work"
    work.mkdir()
    config = tmp_path / "config.json"
    vm = VMFalsa()
    emu = L.Emulador(work, config, 0, vm.puerto, "prueba")
    srv = L.servidor(emu)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield types.SimpleNamespace(base=f"http://127.0.0.1:{srv.server_address[1]}", emu=emu, srv=srv, vm=vm,
                                config=config, work=work)
    vm.cierra()
    srv.shutdown()
    srv.server_close()


@pytest.fixture()
def en_marcha(conf):
    """Igual que `conf` pero con el configurador convencido de que la VM corre (un proceso inofensivo, sin QEMU)."""
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    conf.emu.p, conf.emu.t0 = p, time.monotonic() - 12.0
    yield conf
    p.kill()
    p.wait(10)


def test_pagina_con_las_seis_pestanas(conf) -> None:
    """La página es HTML propio, con las seis pestañas y sus paneles enlazados (teclado y lectores de pantalla)."""
    codigo, tipo, cuerpo = pide(conf.base + "/")
    assert codigo == 200 and tipo.startswith("text/html")
    html = cuerpo.decode()
    assert html.count('role="tab"') == 6
    for nombre in ("Firmware", "Teclas", "Sensor", "SD", "Red", "Cámara"):
        assert f">{nombre}</button>" in html, nombre
    for seccion in ("firmware", "teclas", "sensor", "sd", "red", "camara"):
        assert f'aria-controls="p-{seccion}"' in html and f'id="p-{seccion}"' in html
        assert f'aria-labelledby="tab-{seccion}"' in html
    # estado en vivo, botones diferenciados y los puntos que usan las pestañas nuevas
    assert 'id="estado-txt"' in html and 'id="luz"' in html and 'id="vmurl"' in html
    assert 'id="go"' in html and 'id="stop"' in html and 'id="quit"' in html
    assert "/api/vm/sd/lista" in html and "/api/vm/camara/estado" in html


def test_api_estado_sin_vm(conf) -> None:
    """Sin VM: corriendo = false, la URL del puerto de la VM y ni uptime ni fotogramas inventados."""
    codigo, tipo, cuerpo = pide(conf.base + "/api/estado")
    j = json.loads(cuerpo)
    assert codigo == 200 and tipo.startswith("application/json")
    assert j["corriendo"] is False and j["url"] == f"http://127.0.0.1:{conf.vm.puerto}/"
    assert j["uptime"] is None and j["fotogramas"] is None and j["pid"] is None


def test_api_estado_con_vm_en_marcha(en_marcha) -> None:
    """Con la VM en marcha el estado trae uptime y fotogramas (de /estado de la VM) además del PID."""
    j = json.loads(pide(en_marcha.base + "/api/estado")[2])
    assert j["corriendo"] is True and j["fotogramas"] == 34 and j["texto"] == "restaurado, 12 s"
    assert 11 <= j["uptime"] < 60 and j["pid"] == en_marcha.emu.p.pid


def test_api_config_ida_y_vuelta(conf) -> None:
    """POST /api/config normaliza y guarda; GET devuelve lo mismo y el fichero queda escrito. Un valor malo da 400."""
    cfg = json.loads(pide(conf.base + "/api/config")[2])["config"]
    assert cfg["camara"] == {"bateria": 100, "usb": False, "hdmi": False} and cfg["sd"]["tamano_gb"] == 4
    cfg["sd"] = {"tamano_gb": 8, "carpeta": "/tmp/sd-prueba"}
    cfg["camara"] = {"bateria": 42, "usb": True, "hdmi": True}
    cfg["red"]["puerto"] = 2424
    cab = {"Content-Type": "application/json"}
    codigo, _, cuerpo = pide(conf.base + "/api/config", "POST", json.dumps(cfg).encode(), cab)
    assert codigo == 200
    vuelta = json.loads(cuerpo)["config"]
    assert vuelta["sd"] == {"tamano_gb": 8, "carpeta": "/tmp/sd-prueba"}
    assert vuelta["camara"] == {"bateria": 42, "usb": True, "hdmi": True} and vuelta["red"]["puerto"] == 2424
    assert json.loads(pide(conf.base + "/api/config")[2])["config"] == vuelta
    assert json.loads(conf.config.read_text()) == vuelta
    codigo, _, cuerpo = pide(conf.base + "/api/config", "POST", json.dumps({**cfg, "camara": {"bateria": 200}}).encode(), cab)
    assert codigo == 400 and "bateria" in json.loads(cuerpo)["error"]


def test_pestana_sd_contra_la_vm(en_marcha) -> None:
    """Lista, miniatura, subida con X-Nombre, borrado y formato llegan a la VM por /api/vm/… y vuelven tal cual."""
    c = en_marcha
    codigo, tipo, cuerpo = pide(c.base + "/api/vm/sd/lista")
    assert codigo == 200 and tipo.startswith("application/json")
    assert [f["r"] for f in json.loads(cuerpo)["ficheros"]] == ["DCIM/100MSDCF/DSC00001.JPG", "PRIVATE/M4ROOT/CLIP/C0001.MP4"]
    r = urllib.parse.quote("DCIM/100MSDCF/DSC00001.JPG")
    codigo, tipo, cuerpo = pide(c.base + f"/api/vm/sd/fichero?r={r}")
    assert (codigo, tipo, cuerpo) == (200, "image/jpeg", b"\xff\xd8jpeg")
    codigo, _, cuerpo = pide(c.base + "/api/vm/sd/importa", "POST", b"\x89PNG\r\n", {"X-Nombre": urllib.parse.quote("DSC00009.JPG")})
    assert codigo == 200 and json.loads(cuerpo) == {"r": "DCIM/100MSDCF/DSC00009.JPG", "bytes": 6}
    cab = {"Content-Type": "application/json"}
    codigo, _, cuerpo = pide(c.base + "/api/vm/sd/borrar", "POST", json.dumps({"r": "DCIM/100MSDCF/DSC00001.JPG"}).encode(), cab)
    assert codigo == 200 and json.loads(cuerpo) == {"ok": True}
    assert pide(c.base + "/api/vm/sd/formatea", "POST", b"")[0] == 200
    recibido = {p[1]: p for p in c.vm.peticiones if p[0] == "POST"}  # lo que llegó a la VM de mentira
    assert recibido["/sd/importa"][3]["X-Nombre"] == "DSC00009.JPG"
    assert json.loads(recibido["/sd/borrar"][2]) == {"r": "DCIM/100MSDCF/DSC00001.JPG"}


def test_pestana_camara_lee_y_escribe(en_marcha) -> None:
    """Cámara: el estado de la VM se lee y los tres valores se escriben con {"valor": …}; la config los guarda."""
    c = en_marcha
    assert json.loads(pide(c.base + "/api/vm/camara/estado")[2]) == {"bateria": 73, "usb": True, "hdmi": False}
    for clave, valor in (("bateria", 55), ("usb", False), ("hdmi", True)):
        codigo, _, cuerpo = pide(c.base + f"/api/vm/camara/{clave}", "POST", json.dumps({"valor": valor}).encode(),
                                 {"Content-Type": "application/json"})
        assert codigo == 200 and json.loads(cuerpo) == {clave: valor}
    assert c.vm.camara == {"bateria": 55, "usb": False, "hdmi": True}
    cfg = json.loads(pide(c.base + "/api/config")[2])["config"]
    cfg["camara"] = {"bateria": 55, "usb": False, "hdmi": True}
    codigo, _, cuerpo = pide(c.base + "/api/config", "POST", json.dumps(cfg).encode(), {"Content-Type": "application/json"})
    assert codigo == 200 and json.loads(cuerpo)["config"]["camara"] == {"bateria": 55, "usb": False, "hdmi": True}


def test_avisos_si_la_vm_no_esta_o_no_tiene_el_punto(en_marcha) -> None:
    """404 de la VM → se reenvía con su motivo; VM caída → 503 con «arranca el emulador»; ruta ajena → 400."""
    c = en_marcha
    c.vm.falta.add("/sd/lista")
    codigo, _, cuerpo = pide(c.base + "/api/vm/sd/lista")
    assert codigo == 404 and json.loads(cuerpo)["error"] == "no existe /sd/lista"
    codigo, _, cuerpo = pide(c.base + "/api/vm/tecla")
    assert codigo == 400 and "no permitida" in json.loads(cuerpo)["error"]
    c.emu.p.kill()
    c.emu.p.wait(10)
    codigo, _, cuerpo = pide(c.base + "/api/vm/sd/lista")
    assert codigo == 503 and "arranca el emulador" in json.loads(cuerpo)["error"]
    assert json.loads(pide(c.base + "/api/estado")[2])["corriendo"] is False


def test_lanzador_rechaza_puertos_invalidos() -> None:
    """Robustez de la CLI: puerto fuera de rango o igual al de la VM no arranca el servidor (código 2 de argparse)."""
    for args in (["--puerto", "80"], ["--puerto-vm", "70000"], ["--puerto", "8701", "--puerto-vm", "8701"]):
        r = subprocess.run([sys.executable, str(HARNESS / "lanzador.py"), *args], check=False, capture_output=True, text=True, timeout=120)
        assert r.returncode == 2 and "error" in r.stderr, args


# --------------------------------------------------------------------------- auditoría de CFW desde el configurador
CAB = {"Content-Type": "application/json"}
DAT_MAGIC = bytes.fromhex("895546550d0a1a0a")


def espera_auditoria(conf, tope: float = 120.0) -> dict:
    """Sondea `/api/auditar/estado` como la página hasta que el trabajo termina; devuelve el estado final."""
    t0 = time.monotonic()
    while time.monotonic() - t0 < tope:
        j = json.loads(pide(conf.base + "/api/auditar/estado")[2])
        if not j["corriendo"] and j["codigo"] is not None:
            return j
        time.sleep(0.1)
    raise AssertionError(f"la auditoría no terminó en {tope} s")


def auditor_falso(work: Path, *, dormir: float = 0.0, veredicto: str = "OK") -> Path:
    """Guion que hace de `audita_cfw.py`: escribe consola (stdout y stderr), informe JSON y resumen Markdown en `--salida`."""
    guion = work / "auditor-falso.py"
    guion.write_text(
        "import json,pathlib,sys,time\n"
        "d=pathlib.Path(sys.argv[2]);d.mkdir(parents=True,exist_ok=True)\n"
        "print('AUDITORÍA CFW — ' + sys.argv[1])\n"
        "print('aviso por stderr', file=sys.stderr)\n"
        f"time.sleep({dormir})\n"
        "r={'ruta':sys.argv[1],'tipo':'paquete','sha256':'deadbeef'*8,'version':'3.99','veredicto':"
        f"'{veredicto}','fecha':'2026-01-02T03:04:05+0100','coste_s':0.1,\n"
        "   'checks':[{'id':'contenedor.no_aplica','etapa':1,'ok':None,'detalle':'paquete','evidencia':"
        "'NO_VERIFICADO','aviso':False,'material':False},"
        "{'id':'usr.ficheros_quitados','etapa':2,'ok':True,'detalle':'ninguno','evidencia':'VERIFICADO',"
        "'aviso':False,'material':False}],\n"
        "   'usr':{'anadidos':['lib/x.so'],'cambiados':[],'quitados':[]},"
        "'markdown':str(d/'deadbeef.md')}\n"
        "(d/'audit-20260102-deadbeef.json').write_text(json.dumps(r))\n"
        "(d/'deadbeef.md').write_text('# Auditoría CFW 3.99\\n')\n",
        encoding="utf-8")
    return guion


def test_comando_de_auditoria_equivale_al_cli() -> None:
    """Las banderas del configurador son las del CLI: `--rapido --sin-arranque` por defecto y `--salida` a la carpeta del trabajo."""
    ruta, destino = Path("/tmp/cfw.dat"), Path("/tmp/out")
    base = [sys.executable, "-u", str(HARNESS / "audita_cfw.py"), str(ruta)]  # -u: consola sin búfer
    assert L.comando_auditoria(ruta, destino, completo=False, arranque=False) == [*base, "--rapido", "--sin-arranque",
                                                                                  "--salida", str(destino)]
    assert L.comando_auditoria(ruta, destino, completo=True, arranque=True) == [*base, "--completo", "--arranque",
                                                                               "--salida", str(destino)]


def test_auditar_estado_antes_de_nada(conf) -> None:
    """GET /api/auditar/estado sin ningún trabajo: apagado y sin datos inventados."""
    codigo, tipo, cuerpo = pide(conf.base + "/api/auditar/estado")
    j = json.loads(cuerpo)
    assert codigo == 200 and tipo.startswith("application/json")
    assert j["corriendo"] is False and j["ruta"] is None and j["codigo"] is None
    assert j["salida"] == "" and j["informe"] is None and j["inicio"] is None and j["fin"] is None
    assert j["destino"] is None and j["comando"] == ""


def test_auditar_rechaza_lo_que_no_es_un_cfw(conf) -> None:
    """400 con el motivo: ruta vacía, .dat inexistente, fichero cualquiera y directorio sin nflasha15 ni cam/usr."""
    def post(**d: object) -> tuple[int, str]:
        codigo, _, cuerpo = pide(conf.base + "/api/auditar", "POST", json.dumps(d).encode(), CAB)
        return codigo, json.loads(cuerpo).get("error", "")

    assert post(ruta="   ")[0] == 400 and "falta la ruta" in post(ruta="   ")[1]
    codigo, error = post(ruta=str(conf.work / "no-existe.dat"))
    assert codigo == 400 and "no existe" in error
    assert post(ruta="tampoco-existe.dat")[1].endswith("no existe")  # relativa al directorio de trabajo del arnés
    otro = conf.work / "firmware.json"
    otro.write_text("{}")
    codigo, error = post(ruta=str(otro))
    assert codigo == 400 and "no es un .dat de Sony" in error
    vacio = conf.work / "vacio"
    vacio.mkdir()
    codigo, error = post(ruta=str(vacio))
    assert codigo == 400 and "directorio sin nflasha15" in error
    # overlay parcial de un .dat importado: auditarlo como /usr completo daría un FALLO falso
    parcial = conf.work / "pkgdat" / "dat-3.21-deadbeef" / "cam" / "usr"
    parcial.mkdir(parents=True)
    (parcial / "lib.so").write_bytes(b"ELF")
    codigo, error = post(ruta=str(parcial.parent.parent))
    assert codigo == 400 and "overlay parcial" in error
    (parcial.parent.parent / "audit-cfw.json").write_text(json.dumps({"overlay_parcial": True}))
    assert post(ruta=str(parcial.parent.parent))[0] != 400  # con su declaración, el overlay sí es auditable
    assert json.loads(pide(conf.base + "/api/auditar/estado")[2])["codigo"] is None  # nada de lo rechazado arrancó nada


def test_auditar_dat_sintetico_con_el_auditor_real(conf) -> None:
    """Subproceso real de `audita_cfw.py` sobre un `.dat` de 72 B: termina, deja código 1, JSON de FALLO y enlace servible."""
    dat = conf.work / "sintetico.dat"
    dat.write_bytes(DAT_MAGIC + b"\0" * 64)
    codigo, _, cuerpo = pide(conf.base + "/api/auditar", "POST", json.dumps({"ruta": str(dat)}).encode(), CAB)
    j = json.loads(cuerpo)
    assert codigo == 202 and j["corriendo"] is True and j["tipo"] == "dat"
    assert j["completo"] is False and j["arranque"] is False  # por defecto --rapido --sin-arranque
    assert "--rapido" in j["comando"] and "--sin-arranque" in j["comando"] and j["destino"]
    fin = espera_auditoria(conf)
    assert fin["codigo"] == 1, fin["salida"]  # sin FDAT → FALLO, nunca un OK falso
    assert fin["inicio"] and fin["fin"]
    inf = fin["informe"]
    assert inf["veredicto"] == "FALLO" and "contenedor.fdat_presente" in [c["id"] for c in inf["checks"]]
    assert Path(inf["json"]).is_file() and (conf.work / "audit-ui") in Path(inf["json"]).parents
    codigo, tipo, cuerpo = pide(conf.base + "/api/auditar/informe?f=" + urllib.parse.quote(inf["f"]))
    assert codigo == 200 and tipo.startswith("application/json")
    assert json.loads(cuerpo)["veredicto"] == "FALLO"
    codigo, tipo, _ = pide(conf.base + "/api/auditar/informe?f=" + urllib.parse.quote(inf["markdown_f"]))
    assert codigo == 200 and tipo.startswith("text/markdown")


def test_auditar_paquete_sintetico_con_comando_falso(conf, monkeypatch: pytest.MonkeyPatch) -> None:
    """Paquete con `nflasha15`: se lanza el subproceso, se captura stdout+stderr, el código y el informe (con enlaces)."""
    pkg = conf.work / "pkg-sintetico"
    pkg.mkdir()
    origen = conf.work / "nflasha15.pequeno"
    origen.write_bytes(b"TPZL" + b"\0" * 60)
    shutil.copyfile(origen, pkg / "nflasha15")  # tan pequeño como el original: el contenido no lo mira el comando falso
    guion = auditor_falso(conf.work)
    monkeypatch.setattr(L, "comando_auditoria",
                        lambda ruta, destino, *, completo, arranque: [sys.executable, str(guion), str(ruta), str(destino)])
    codigo, _, cuerpo = pide(conf.base + "/api/auditar", "POST",
                             json.dumps({"ruta": "pkg-sintetico", "completo": True}).encode(), CAB)
    j = json.loads(cuerpo)
    assert codigo == 202 and j["tipo"] == "paquete" and j["ruta"].endswith("pkg-sintetico")  # ruta relativa al arnés
    fin = espera_auditoria(conf)
    assert fin["codigo"] == 0, fin["salida"]
    assert "AUDITORÍA CFW" in fin["salida"] and "aviso por stderr" in fin["salida"]  # stdout+stderr en un solo texto
    inf = fin["informe"]
    assert inf["veredicto"] == "OK" and inf["version"] == "3.99" and inf["coste_s"] == 0.1
    assert inf["markdown_f"].endswith("deadbeef.md") and inf["usr"]["anadidos"] == 1
    assert [c["id"] for c in inf["checks"]] == ["contenedor.no_aplica", "usr.ficheros_quitados"]
    for f, prefijo in ((inf["f"], "application/json"), (inf["markdown_f"], "text/markdown")):
        codigo, tipo, _ = pide(conf.base + "/api/auditar/informe?f=" + urllib.parse.quote(f))
        assert codigo == 200 and tipo.startswith(prefijo), (f, tipo)


def test_auditar_409_mientras_hay_un_trabajo_en_curso(conf, monkeypatch: pytest.MonkeyPatch) -> None:
    """Un solo trabajo a la vez: el segundo POST da 409; al terminar, el hueco queda libre."""
    dat = conf.work / "lento.dat"
    dat.write_bytes(DAT_MAGIC + b"\0" * 64)
    guion = auditor_falso(conf.work, dormir=1.5)
    monkeypatch.setattr(L, "comando_auditoria",
                        lambda ruta, destino, *, completo, arranque: [sys.executable, str(guion), str(ruta), str(destino)])
    assert pide(conf.base + "/api/auditar", "POST", json.dumps({"ruta": str(dat)}).encode(), CAB)[0] == 202
    codigo, _, cuerpo = pide(conf.base + "/api/auditar", "POST", json.dumps({"ruta": str(dat)}).encode(), CAB)
    assert codigo == 409 and "ya hay una auditoría en marcha" in json.loads(cuerpo)["error"]
    # una ruta mala se explica igual (400) aunque esté ocupado: primero el motivo, luego el turno
    codigo, _, cuerpo = pide(conf.base + "/api/auditar", "POST", json.dumps({"ruta": "/tmp/no-existe.dat"}).encode(), CAB)
    assert codigo == 400 and "no existe" in json.loads(cuerpo)["error"]
    assert espera_auditoria(conf)["codigo"] == 0
    assert pide(conf.base + "/api/auditar", "POST", json.dumps({"ruta": str(dat)}).encode(), CAB)[0] == 202
    assert espera_auditoria(conf)["codigo"] == 0


def test_informe_no_permite_salir_de_las_carpetas_de_auditoria(conf) -> None:
    """`?f=` solo sirve `.json`/`.md` de la carpeta del trabajo o de `audit-*.json` de la raíz; lo demás es 400."""
    trabajo = conf.work / "audit-ui" / "20260101-000000-x"
    trabajo.mkdir(parents=True)
    (trabajo / "audit-20260101-deadbeef.json").write_text(json.dumps({"veredicto": "OK"}))
    (trabajo / "nota.txt").write_text("no es un informe")
    (conf.work.parent / "audit-20250101-cafe.json").write_text(json.dumps({"veredicto": "FALLO"}))
    (conf.work.parent / "config.json").write_text("{}")
    (conf.work / "config.json").write_text("{}")

    def estado(f: str) -> int:
        return pide(conf.base + "/api/auditar/informe?f=" + urllib.parse.quote(f))[0]

    del_trabajo = (conf.work.relative_to(conf.work.parent) / "audit-ui/20260101-000000-x").as_posix()  # ''work/audit-ui/…''
    assert estado(f"{del_trabajo}/audit-20260101-deadbeef.json") == 200  # las rutas de `?f=` son relativas a la raíz de G22
    assert estado(str(conf.work / "audit-ui/20260101-000000-x/audit-20260101-deadbeef.json")) == 200  # o absolutas
    assert estado("audit-20250101-cafe.json") == 200  # convención del CLI en la raíz de G22
    for malo in ("", "../../../etc/passwd", "/etc/passwd", f"{del_trabajo}/../../../config.json", "config.json",
                 f"{del_trabajo}/nota.txt", f"{del_trabajo}/", "audit-ui/20260101-000000-x/audit-20260101-deadbeef.json"):
        assert estado(malo) == 400, malo


def test_historial_vacio_y_con_informes(conf) -> None:
    """Historial: vacío se dice tal cual; con informes, cada uno con veredicto y fecha; el ilegible no lo rompe."""
    j = json.loads(pide(conf.base + "/api/auditar/historial")[2])
    assert j["vacio"] is True and j["auditorias"] == [] and Path(j["raiz"]) == conf.work.parent
    ejemplo = {"veredicto": "AVISO", "fecha": "2026-01-01T10:00:00+0100", "version": "3.99",
               "sha256": "deadbeef" + "0" * 56, "ruta": "/tmp/cfw.dat", "coste_s": 48.2}
    (conf.work.parent / "audit-20260101-deadbeef.json").write_text(json.dumps(ejemplo))
    trabajo = conf.work / "audit-ui" / "20260102-000000-y"
    trabajo.mkdir(parents=True)
    (trabajo / "audit-20260102-0000beef.json").write_text(json.dumps({**ejemplo, "veredicto": "OK",
                                                                      "fecha": "2026-01-02T10:00:00+0100"}))
    (conf.work.parent / "audit-20260103-roto.json").write_text("{no es json")
    j = json.loads(pide(conf.base + "/api/auditar/historial")[2])
    assert j["vacio"] is False and len(j["auditorias"]) == 3
    assert [a["veredicto"] for a in j["auditorias"]] == ["", "OK", "AVISO"]  # ordenado por fecha, lo último arriba
    ultimo = j["auditorias"][2]
    assert (ultimo["f"], ultimo["version"], ultimo["coste_s"]) == ("audit-20260101-deadbeef.json", "3.99", 48.2)
    assert pide(conf.base + "/api/auditar/informe?f=" + urllib.parse.quote(ultimo["f"]))[0] == 200
    roto = j["auditorias"][0]
    assert roto["error"] and roto["veredicto"] == "" and roto["fecha_fuente"] == "fichero" and roto["fecha"]


def test_pestana_firmware_ofrece_la_auditoria(conf) -> None:
    """La pestaña Firmware trae el panel de auditoría, los dos botones, la tabla, la consola, el historial y los límites."""
    html = pide(conf.base + "/")[2].decode()
    for trozo in ('id="audruta"', 'id="audusa"', 'id="audcomp"', 'id="aud1"', 'id="aud2"', 'id="audtab"', 'id="audlog"',
                  'id="audver"', 'id="audlinks"', 'id="audhist"', 'id="audhmsg"', 'id="audlim"', "Auditar el .dat",
                  "Auditar con arranque", "Usar el importado", "/api/auditar/estado", "/api/auditar/historial",
                  "/api/auditar/informe?f=", "g22-auditoria-cfw.md"):
        assert trozo in html, trozo
    assert "no de la cámara" in html and "tampoco demuestra que funcione en la cámara" in html
    assert "setInterval(audSondea,2000)" in html  # estado en vivo cada 2 s
    assert json.loads(pide(conf.base + "/api/config")[2])["importado"] is None
