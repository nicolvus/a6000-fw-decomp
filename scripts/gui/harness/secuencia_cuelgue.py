#!/usr/bin/env python3
"""Conductor de la secuencia de navegación que cuelga la UI (G22-CUELGUE, fila G22-E).

Repite la misma secuencia de teclas contra la ventana en vivo (`live.py`, puerto HTTP) y vigila
`GET /estado`: fotogramas (copias a pantalla que produce el invitado) y listas de GPU del último
fotograma. Se para cuando el invitado lleva `--ventana` pulsaciones seguidas sin producir ni un
fotograma (el síntoma documentado: «0 listas», las flechas dejan de responder), guarda el PNG del
último fotograma bueno y deja un CSV con cada pulsación y el estado leído antes y después.

uso: secuencia_cuelgue.py PUERTO [--vueltas N] [--max-pulsaciones N] [--minutos N]
                               [--espera s] [--pausa s] [--salida DIR] [--ventana N]
  Cada pulsación es `POST /tecla {"k": nombre, "v": 1}` y la suelta `v: 0` (lo que hace la ventana al
  teclado). Tras la pulsación se espera hasta `--espera` s a que llegue un fotograma nuevo; si no llega
  ninguno, esa pulsación cuenta como «sin respuesta» (la ventana con WLALL=1 puede tardar segundos en
  pintar, así que no basta con mirar /estado una vez).

Sin QEMU: `secuencia(3)` da la lista exacta de teclas y `cuelga(historial)` la regla de parada; las
pruebas de `tests/test_g22_hang.py` las usan.
"""

import argparse
import base64
import csv
import http.client
import json
import sys
import time
from pathlib import Path

# Secuencia exacta, una vuelta: abrir MENU, cambiar de pestaña a derecha e izquierda, bajar una fila,
# entrar en la fila y cerrar el MENU (el bucle está medido en el informe: docs/gui/g22-cuelgue-navegacion.md).
SECUENCIA = ("menu", "derecha", "abajo", "derecha", "izquierda", "abajo", "intro", "menu")


def secuencia(vueltas: int) -> list[str]:
    """Lista de teclas de `vueltas` vueltas de la secuencia fija (sin pausas: el conductor las pone)."""
    return [k for _ in range(max(0, vueltas)) for k in SECUENCIA]


def cuelga(historial: list[dict], ventana: int = 5) -> bool:
    """¿El invitado se ha parado? `historial` = pulsaciones con `fotogramas` leídos tras pulsar.

    Cuelgue = las últimas `ventana` pulsaciones no han traído ningún fotograma nuevo (delta 0), es
    decir la UI no vuelve a copiar a pantalla aunque le lleguen teclas. No se declara antes de tener
    `ventana` pulsaciones.
    """
    if len(historial) < ventana or ventana <= 0:
        return False
    return all(not p["nuevo"] for p in historial[-ventana:])


class Vivo:
    def __init__(self, puerto: int, tmo: float = 10.0) -> None:
        self.puerto, self.tmo = puerto, tmo

    def _pide(self, metodo: str, ruta: str, cuerpo: bytes = b"") -> bytes:
        c = http.client.HTTPConnection("127.0.0.1", self.puerto, timeout=self.tmo)
        c.request(metodo, ruta, cuerpo)
        d = c.getresponse().read()
        c.close()
        return d

    def estado(self) -> dict:
        return json.loads(self._pide("GET", "/estado"))

    def tecla(self, nombre: str, v: int) -> None:
        self._pide("POST", "/tecla", json.dumps({"k": nombre, "v": v}).encode())

    def pulsa(self, nombre: str, pausa: float) -> None:
        for v in (1, 0):
            self.tecla(nombre, v)
        time.sleep(pausa)

    def png(self, destino: Path, espera: float = 1.5) -> bool:
        """Último fotograma recibido por /eventos (SSE) tras pedir un refresco."""
        self._pide("POST", "/refrescar", b"{}")
        c = http.client.HTTPConnection("127.0.0.1", self.puerto, timeout=self.tmo)
        c.request("GET", "/eventos")
        r = c.getresponse()
        ultimo, t0 = None, time.time()
        while time.time() - t0 < espera + 3:
            try:
                ln = r.fp.readline()
            except (TimeoutError, OSError):  # el SSE solo manda «: vivo» cada 15 s: un silencio más largo no es un fallo
                continue
            if ln.startswith(b"data: "):
                ultimo = base64.b64decode(ln[6:].strip())
                if time.time() - t0 > espera:
                    break
        c.close()
        if not ultimo:
            return False
        destino.write_bytes(ultimo)
        return True


def vigila(vivo: Vivo, vueltas: int, max_puls: int, minutos: float, pausa: float, espera: float,
           ventana: int, salida: Path) -> dict:
    """Conduce la secuencia y devuelve el resumen; escribe pulsaciones.csv y los PNG de antes/después."""
    salida.mkdir(parents=True, exist_ok=True)
    teclas = secuencia(vueltas)
    hist: list[dict] = []
    t0 = time.time()
    ultimo = vivo.estado()
    vivo.png(salida / "antes.png")
    cuelgue_en: int | None = None
    prev, prev_listas = ultimo.get("fotogramas", 0), ultimo.get("listas_total", 0)
    for i, nombre in enumerate(teclas, 1):
        if i > max_puls or (time.time() - t0) / 60 > minutos:
            break
        vivo.pulsa(nombre, pausa)
        est, t = vivo.estado(), time.time()
        while time.time() - t < espera and est.get("fotogramas", 0) <= prev:  # da tiempo a pintar antes de darla por perdida
            time.sleep(0.2)
            est = vivo.estado()
        fot = est.get("fotogramas", 0)
        fila = {"n": i, "tecla": nombre, "s": round(time.time() - t0, 2), "fotogramas": fot,
                "nuevo": max(0, fot - prev), "listas": est.get("listas", 0),
                "listas_nuevas": max(0, est.get("listas_total", 0) - prev_listas),
                "listas_total": est.get("listas_total", 0), "opacos": est.get("opacos", 0.0)}
        prev, prev_listas = fot, est.get("listas_total", prev_listas)
        hist.append(fila)
        if cuelga(hist, ventana):
            cuelgue_en = i
            break
    vivo.png(salida / "despues.png")
    with (salida / "pulsaciones.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hist[0]) if hist else ["n"])
        w.writeheader()
        w.writerows(hist)
    fin = vivo.estado()
    resumen = {"pulsaciones": len(hist), "cuelgue_en": cuelgue_en, "segundos": round(time.time() - t0, 1),
               "fotogramas_antes": ultimo.get("fotogramas"), "fotogramas_despues": fin.get("fotogramas"),
               "listas_antes": ultimo.get("listas"), "listas_despues": fin.get("listas"),
               "listas_total_antes": ultimo.get("listas_total"), "listas_total_despues": fin.get("listas_total"),
               "opacos_antes": ultimo.get("opacos"), "opacos_despues": fin.get("opacos"),
               "texto": fin.get("texto")}
    (salida / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n")
    return resumen


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("puerto", type=int)
    ap.add_argument("--vueltas", type=int, default=60, help="vueltas de la secuencia (8 teclas cada una)")
    ap.add_argument("--max-pulsaciones", type=int, default=300)
    ap.add_argument("--minutos", type=float, default=5.0)
    ap.add_argument("--pausa", type=float, default=0.4, help="s tras cada pulsación")
    ap.add_argument("--espera", type=float, default=3.0, help="s máx esperando a que el invitado esté quieto antes de pulsar")
    ap.add_argument("--ventana", type=int, default=5, help="pulsaciones seguidas sin fotograma nuevo para declarar cuelgue")
    ap.add_argument("--salida", type=Path, default=Path("analysis/gui/g22/harness/cuelgue"))
    a = ap.parse_args()
    r = vigila(Vivo(a.puerto), a.vueltas, a.max_pulsaciones, a.minutos, a.pausa, a.espera, a.ventana, a.salida)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    sys.exit(0 if r["cuelgue_en"] else 1)  # 1 = no se reprodujo (aguantó)


if __name__ == "__main__":
    main()
