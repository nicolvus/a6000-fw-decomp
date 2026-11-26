"""G22-CUELGUE — el cuelgue de la UI al navegar el menú (0 listas de GPU): sin QEMU.

Cubre las tres piezas que se añadieron para reproducirlo y diagnosticarlo:
- la secuencia exacta de teclas y la regla de parada (`scripts/gui/harness/secuencia_cuelgue.py`),
- el conductor completo (`vigila`) contra una `live.py` de mentira que deja de mandar fotogramas,
- lo que este cambio toca del arnés: `GET /estado` con `listas`/`listas_total` (`live.estado_json`) y
  `PMROUNDS` en `im.sh` (más de tres volcados del grafo de espera por hilo).

No arranca QEMU ni toca el firmware: la VM es un servidor HTTP en un hilo y `im.sh` se lee como texto.
"""
from __future__ import annotations

import base64
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts/gui/harness"
sys.path.insert(0, str(HARNESS))

import live
import secuencia_cuelgue as SC

# --- secuencia y detector (puro) -----------------------------------------------------------------


def test_secuencia_es_la_de_la_reproduccion() -> None:
    """La secuencia es la documentada: MENU, pestaña a la derecha/izquierda, bajar, Intro y cerrar MENU."""
    assert SC.SECUENCIA == ("menu", "derecha", "abajo", "derecha", "izquierda", "abajo", "intro", "menu")


def test_secuencia_repite_vueltas_completas() -> None:
    assert SC.secuencia(0) == []
    assert len(SC.secuencia(3)) == 24
    assert SC.secuencia(2) == list(SC.SECUENCIA) * 2


def test_cuelga_necesita_la_ventana_entera() -> None:
    """Con menos pulsaciones que la ventana no se declara cuelgue por muy parado que esté."""
    parado = [{"nuevo": 0}] * 3
    assert SC.cuelga(parado, ventana=4) is False
    assert SC.cuelga(parado, ventana=3) is True
    assert SC.cuelga(parado, ventana=0) is False


def test_cuelga_pide_ventana_completa_sin_fotogramas() -> None:
    hist = [{"nuevo": 0}, {"nuevo": 0}, {"nuevo": 0}, {"nuevo": 0}, {"nuevo": 0}]
    assert SC.cuelga(hist, ventana=5) is True


def test_cuelga_no_salta_si_alguna_pulsacion_pinta() -> None:
    hist = [{"nuevo": 0}, {"nuevo": 0}, {"nuevo": 1}, {"nuevo": 0}, {"nuevo": 0}]
    assert SC.cuelga(hist, ventana=5) is False


# --- /estado: los números que se expusieron (sin QEMU) --------------------------------------------


class _VmDeMentira:
    def __init__(self, fotogramas: int = 9, listas: int = 4, total: int = 31, opacos: float = 0.0912) -> None:
        self.seq, self.listas, self.listas_total, self.opacos = fotogramas, listas, total, opacos


def test_estado_json_expone_fotogramas_listas_y_alfa_opaco() -> None:
    """`opacos` es la métrica que distingue la OSD pintada (≈0,09) de la pantalla vacía del cuelgue (≈0,005)."""
    assert live.estado_json(_VmDeMentira()) == {"fotogramas": 9, "listas": 4, "listas_total": 31, "opacos": 0.0912}


# --- conductor completo contra una live.py de mentira ---------------------------------------------


PNG = b"A6KF"  # lo único que mira el conductor: bytes del último fotograma


class VivaFalsa:
    """Servidor que hace de `live.py`: cuenta las pulsaciones y deja de producir fotogramas tras `aguanta`."""

    def __init__(self, aguanta: int = 6) -> None:
        self.aguanta, self.pulsaciones, self.fotogramas, self.listas_total = aguanta, 0, 1, 5
        self.teclas: list[str] = []
        viva = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a: object) -> None:
                pass

            def _json(self, obj: object) -> None:
                d = json.dumps(obj).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(d)))
                self.end_headers()
                self.wfile.write(d)

            def do_GET(self) -> None:
                if self.path == "/estado":
                    self._json({"texto": "falsa", "fotogramas": viva.fotogramas, "listas": 0,
                                "listas_total": viva.listas_total})
                elif self.path == "/eventos":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.end_headers()
                    self.wfile.write(b"data: " + base64.b64encode(PNG) + b"\n\n")  # un «fotograma» mínimo (base64, como live.py)
                else:
                    self.send_error(404)

            def do_POST(self) -> None:
                n = int(self.headers.get("Content-Length", 0))
                cuerpo = self.rfile.read(n)
                if self.path == "/tecla":
                    k = json.loads(cuerpo)["k"]
                    if json.loads(cuerpo)["v"] == 1:  # la pulsación (no la suelta) mueve la cuenta
                        viva.pulsaciones += 1
                        viva.teclas.append(k)
                        if viva.pulsaciones > viva.aguanta:  # a partir de aquí, 0 fotogramas nuevos
                            pass
                        else:
                            viva.fotogramas += 1
                            viva.listas_total += 2
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"ok")

        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.puerto = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def cierra(self) -> None:
        self.srv.shutdown()


def test_vigila_se_para_al_cesar_los_fotogramas(tmp_path: Path) -> None:
    """El invitado pinta 6 pulsaciones y luego nada: el conductor lo detecta y deja antes/después."""
    viva = VivaFalsa(aguanta=6)
    try:
        r = SC.vigila(SC.Vivo(viva.puerto), vueltas=10, max_puls=80, minutos=1, pausa=0, espera=0,
                      ventana=5, salida=tmp_path)
    finally:
        viva.cierra()
    assert r["cuelgue_en"] is not None, r
    assert r["cuelgue_en"] == 11  # 6 con fotograma + 5 sin él = ventana
    assert (tmp_path / "pulsaciones.csv").exists()
    assert (tmp_path / "antes.png").read_bytes() == PNG
    assert (tmp_path / "despues.png").read_bytes() == PNG
    filas = (tmp_path / "pulsaciones.csv").read_text().strip().splitlines()
    assert filas[0].startswith("n,tecla") and len(filas) == r["pulsaciones"] + 1
    assert json.loads((tmp_path / "resumen.json").read_text())["cuelgue_en"] == r["cuelgue_en"]


def test_vigila_aguanta_si_sigue_pintando(tmp_path: Path) -> None:
    """Si cada pulsación pinta, no hay cuelgue y el conductor sale con la cuenta pedida."""
    viva = VivaFalsa(aguanta=10_000)
    try:
        r = SC.vigila(SC.Vivo(viva.puerto), vueltas=1, max_puls=8, minutos=1, pausa=0, espera=0,
                      ventana=5, salida=tmp_path)
    finally:
        viva.cierra()
    assert r["cuelgue_en"] is None
    assert r["pulsaciones"] == 8
    assert r["fotogramas_despues"] > r["fotogramas_antes"]


# --- piezas del arnés que este trabajo toca --------------------------------------------------------


def test_im_sh_pmwait_permite_mas_rondas() -> None:
    """Un cuelgue tardío no cabe en los tres volcados de antes: PMROUNDS los amplía y el defecto sigue en 3."""
    txt = (HARNESS / "im.sh").read_text()
    bloque = txt.split('if [ -n "$PMWAIT" ]', 1)[1].split("\nfi", 1)[0]  # solo el volcado de PMWAIT
    assert "while [ $r -lt ${PMROUNDS:-3} ]" in bloque
    assert "for r in 1 2 3; do PP=" not in bloque
