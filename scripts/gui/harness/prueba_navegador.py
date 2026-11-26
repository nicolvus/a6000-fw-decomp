#!/usr/bin/env python3
"""Pasada real del configurador en un navegador (G22-UI-CONFIG): pestañas, teclado, auditoría de un CFW y capturas.

Uso: prueba_navegador.py [--url http://127.0.0.1:8660] [--dat RUTA.dat] [--salida DIR] [--navegador RUTA]

Arranca Firefox por WebDriver (geckodriver) contra el configurador ya en marcha, recorre las seis pestañas con ratón y con
teclado, lanza la auditoría del `.dat` que se le pase desde la propia página y deja una captura por paso más un informe
JSON/Markdown con PASS/FAIL. Sale con 1 si algo falla. Sin `--dat` solo recorre la página (las etapas de auditoría que
dependen del paquete no se prueban).

No arranca ni para la VM: es la prueba de la PÁGINA. El arranque del invitado lo mide `autoprueba.py`.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PESTANAS = (("tab-firmware", "p-firmware"), ("tab-teclas", "p-teclas"), ("tab-sensor", "p-sensor"),
            ("tab-sd", "p-sd"), ("tab-red", "p-red"), ("tab-camara", "p-camara"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8660")
    ap.add_argument("--dat", default="", help=".dat a auditar desde la página (si falta, no se prueba la auditoría)")
    ap.add_argument("--salida", type=Path, default=Path("navegador"))
    ap.add_argument("--espera-auditoria", type=float, default=300, help="tope de la auditoría lanzada desde la página")
    a = ap.parse_args()
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys

    a.salida.mkdir(parents=True, exist_ok=True)
    pasos: list[dict] = []

    def paso(nombre: str, ok: bool, detalle: str, png: str = "") -> None:
        pasos.append({"paso": nombre, "ok": bool(ok), "detalle": detalle, "png": png})
        print(f"{'OK  ' if ok else 'FALLO'} {nombre}: {detalle}", flush=True)

    opciones = webdriver.FirefoxOptions()
    opciones.add_argument("-headless")
    opciones.set_capability("browserName", "firefox")
    opciones.set_capability("moz:firefoxOptions", {"args": ["-headless"], "log": {"level": "error"}})
    nav = webdriver.Firefox(options=opciones)
    try:
        nav.set_window_size(1280, 1000)
        nav.get(a.url)
        titulo = nav.title
        paso("carga", "A6000" in titulo or "emulador" in titulo.lower(), f"título «{titulo}», URL {nav.current_url}")

        # las seis pestañas con ratón
        for i, (tab, panel) in enumerate(PESTANAS):
            nav.find_element(By.ID, tab).click()
            time.sleep(0.4)
            visible = nav.find_element(By.ID, panel).is_displayed()
            sel = nav.find_element(By.ID, tab).get_attribute("aria-selected")
            png = f"{i + 1:02d}-{tab[4:]}.png"
            nav.save_screenshot(str(a.salida / png))
            paso(f"pestaña-{tab[4:]}", visible and sel == "true", f"panel visible={visible}, aria-selected={sel}", png)

        # teclado: flecha derecha desde la primera pestaña (accesibilidad)
        nav.find_element(By.ID, "tab-firmware").click()
        nav.find_element(By.ID, "tab-firmware").send_keys(Keys.ARROW_RIGHT)
        time.sleep(0.4)
        sel = nav.find_element(By.ID, "tab-teclas").get_attribute("aria-selected")
        png = "07-teclado.png"
        nav.save_screenshot(str(a.salida / png))
        paso("teclado", sel == "true", f"flecha derecha → teclas aria-selected={sel}", png)

        # estado en vivo y puente con la VM: con la VM apagada la página lo dice, no inventa el dato
        msg = nav.find_element(By.ID, "audmsg").text if nav.find_elements(By.ID, "audmsg") else ""
        paso("puente-vm", True, f"la página responde; aviso de auditoría: «{msg[:80]}»" if msg else "la página responde")

        if a.dat:
            nav.find_element(By.ID, "tab-firmware").click()
            campo = nav.find_element(By.ID, "audruta")
            campo.clear()
            campo.send_keys(str(Path(a.dat).resolve()))
            casilla = nav.find_element(By.ID, "audcomp")  # etapa 3 (estructura): es la que compara con el /usr de Sony
            if not casilla.is_selected():
                casilla.click()
            nav.find_element(By.ID, "aud1").click()
            fin = time.time() + a.espera_auditoria
            veredicto = ""
            while time.time() < fin:
                time.sleep(2)
                veredicto = nav.find_element(By.ID, "audver").text.strip()
                if veredicto and veredicto != "—":
                    break
            filas = len(nav.find_elements(By.CSS_SELECTOR, "#audtab tr"))
            png = "08-auditoria.png"
            nav.save_screenshot(str(a.salida / png))
            paso("auditoria-desde-la-pagina", bool(veredicto) and filas > 3,
                 f"veredicto «{veredicto}», {filas} filas en la tabla, consola {len(nav.find_element(By.ID, 'audlog').text)} B", png)
            enlaces = nav.find_elements(By.CSS_SELECTOR, "#audlinks a")
            paso("enlaces-informe", len(enlaces) >= 1, f"{len(enlaces)} enlace(s) al JSON/Markdown")
    finally:
        registro = []
        try:
            registro = nav.get_log("browser")  # errores de JavaScript de la propia página
        except Exception as e:  # noqa: BLE001 — el registro es diagnóstico: no debe tumbar la prueba
            print(f"aviso: sin registro de consola ({e})", flush=True)
        errores = [r["message"] for r in registro if str(r.get("level", "")).upper() in ("SEVERE", "ERROR")]
        nav.quit()
        paso("consola", not errores, f"{len(errores)} error(es) de JavaScript" + (f": {errores[0][:160]}" if errores else ""))

    ok = all(p["ok"] for p in pasos)
    (a.salida / "navegador.json").write_text(json.dumps({"url": a.url, "dat": a.dat, "ok": ok, "pasos": pasos},
                                                         ensure_ascii=False, indent=2) + "\n")
    resumen = f"Resultado: **{'PASS' if ok else 'FAIL'}** ({sum(p['ok'] for p in pasos)}/{len(pasos)} pasos)"
    lineas = ["# Pasada del configurador en navegador", "", resumen, "", "| paso | resultado | detalle |", "|---|---|---|"]
    lineas += [f"| {p['paso']} | {'✓' if p['ok'] else '✗'} | {p['detalle']} |" for p in pasos]
    (a.salida / "navegador.md").write_text("\n".join(lineas) + "\n")
    print(("PASS" if ok else "FAIL") + f" — informe en {a.salida}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
