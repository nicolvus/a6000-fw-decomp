"""G22 — configurador del arnés (`lanzador.py`): pestañas, API de estado/config y reenvío a la VM de las pestañas SD y Cámara.

Servidores reales en hilos con puerto efímero: el configurador tal cual y una VM de mentira que hace de `live.py` (solo los puntos
que usa la página). No se arranca QEMU ni se toca firmware.
"""
from __future__ import annotations

import json
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
