#!/usr/bin/env python3
"""Prueba USB-CARGA-3 por el canal senser (cámara encendida y conectada al PC por USB).

Fases en una sola sesión de servicio: línea base (BATT_V e IB_TEMPERATURE cada PASO s durante BASE min),
USB_CHG_IC_SET `carga`, vigilancia durante CARGA min y USB_CHG_IC_SET `normal` al final, también si algo falla
o la temperatura cruda sube más de --delta-temp sobre la base. Guarda todo en
analysis/camera-dumps/<fecha>-usb-carga-senser/registro.csv (respuestas en bruto: su formato no está verificado).
Uso: prueba_senser.py [--ma 500] [--base 3] [--carga 10] [--paso 30] [--delta-temp 8] [--solo-leer]
"""
import argparse
import csv
import datetime
import os
import pathlib
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import chg_ic_set as c

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'references', 'pmca'))
from pmca.commands.usb import senserShellCommand

RAIZ = pathlib.Path(__file__).resolve().parents[2]
LECTURAS = {'BATT_V': (0x0D01, 0x10), 'IB_TEMPERATURE': (0x0D03, 0x01)}


def leer(cam, nombre: str) -> bytes:
    try:
        return cam._sendAdjustControlPacket(*LECTURAS[nombre]) or b''
    except Exception as e:  # noqa: BLE001  una lectura fallida no debe impedir volver a `normal`
        return f'ERR {e}'.encode()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--ma', type=int, default=500)
    ap.add_argument('--base', type=float, default=3)
    ap.add_argument('--carga', type=float, default=10)
    ap.add_argument('--paso', type=float, default=30)
    ap.add_argument('--delta-temp', type=int, default=8, help='corte: subida máxima del primer byte de IB_TEMPERATURE')
    ap.add_argument('--solo-leer', action='store_true')
    a = ap.parse_args()
    d = RAIZ / f'analysis/camera-dumps/{datetime.date.today():%Y%m%d}-usb-carga-senser'
    d.mkdir(parents=True, exist_ok=True)

    def run(cam):
        cam.readHasp()
        with open(d / 'registro.csv', 'a', newline='') as f:
            w = csv.writer(f)
            t0 = time.time()

            def muestra(fase: str) -> bytes:
                v, t = leer(cam, 'BATT_V'), leer(cam, 'IB_TEMPERATURE')
                w.writerow([round(time.time() - t0), fase, v.hex(' '), t.hex(' ')])
                f.flush()
                print(f'{time.time() - t0:6.0f} s {fase:6s} BATT_V={v.hex(" ")} IB_TEMP={t.hex(" ")}', flush=True)
                return t

            def fase(nombre: str, minutos: float, t_ref: bytes | None = None) -> None:
                fin = time.time() + minutos * 60
                while True:
                    t = muestra(nombre)
                    if t_ref and t[:1] and t_ref[:1] and not t.startswith(b'ERR') and t[0] - t_ref[0] > a.delta_temp:
                        raise RuntimeError(f'corte por temperatura: {t_ref.hex()} → {t.hex()}')
                    if time.time() >= fin:
                        return
                    time.sleep(a.paso)

            w.writerow(['segundos', 'fase', 'BATT_V', 'IB_TEMPERATURE'])
            t_base = muestra('base')
            fase('base', a.base)
            if a.solo_leer:
                return
            try:
                r = cam._sendAdjustControlPacket(c.BLOQUE, c.CODIGO, c.carga_util('carga', a.ma))
                print('USB_CHG_IC_SET carga →', r.hex(' ') if r else '(vacía)')
                w.writerow([round(time.time() - t0), 'orden', 'carga', a.ma])
                fase('carga', a.carga, t_base)
            finally:
                r = cam._sendAdjustControlPacket(c.BLOQUE, c.CODIGO, c.carga_util('normal', 100))
                print('USB_CHG_IC_SET normal →', r.hex(' ') if r else '(vacía)')
                w.writerow([round(time.time() - t0), 'orden', 'normal', 100])
                muestra('fin')
        print('→', d / 'registro.csv')

    senserShellCommand(complete=run)


if __name__ == '__main__':
    main()
