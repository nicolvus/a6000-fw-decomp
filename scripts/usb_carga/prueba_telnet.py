#!/usr/bin/env python3
"""Prueba USB-CARGA-3 entera por telnet (sin modo servicio): control `normal` y luego `carga`, con el mismo límite.

USB_CHG_IC_SET se envía con /usr/bin/adjstctl.elf (uso medido: `adjstctl.elf BLOQUE CÓDIGO b:DATO …`). Cada minuto
se lee el nivel real (`dumpsys battery`). Al final, y ante cualquier error, se deja `normal`.
Sirve con el PC o con un cargador de pared (la cámara solo necesita Wi-Fi/telnet).
Uso: prueba_telnet.py [--ma 900] [--control 20] [--carga 40]   (A6000_HOST=ip)
Salida: analysis/camera-dumps/<fecha>-usb-carga-telnet/nivel-<mA>mA.csv
"""
import argparse
import datetime
import os
import pathlib
import re
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import camera_get as cg
import chg_ic_set as c
from camera_telnet import run

RAIZ = pathlib.Path(__file__).resolve().parents[2]


def orden(modo: str, ma: int) -> str:
    datos = ' '.join(f'b:{b:#04x}' for b in c.carga_util(modo, ma))
    out = run(cg.HOST, [f'/usr/bin/adjstctl.elf {c.BLOQUE:#x} {c.CODIGO:#x} {datos} 2>&1; echo rc=$?'])[0]
    if 'rc=0' not in out:
        raise RuntimeError(f'adjstctl falló:\n{out}')
    return out.split('datasz')[-1].strip()


def nivel() -> int:
    o = cg.TMP_ROOT
    run(cg.HOST, [f"echo 'PATH=/system/bin; dumpsys battery > /mnt/obb/bt.txt 2>&1' > {o}/bt.sh",
                  'chroot /android /system/bin/sh /mnt/obb/bt.sh'])
    m = re.search(r'level: (\d+)', run(cg.HOST, [f'cat {o}/bt.txt; rm -f {o}/bt.txt {o}/bt.sh'])[0])
    if not m:
        raise RuntimeError('sin nivel de batería')
    return int(m.group(1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--ma', type=int, default=900)
    ap.add_argument('--control', type=int, default=20, help='minutos con `normal`')
    ap.add_argument('--carga', type=int, default=40, help='minutos con `carga`')
    a = ap.parse_args()
    d = RAIZ / f'analysis/camera-dumps/{datetime.date.today():%Y%m%d}-usb-carga-telnet'
    d.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    def fase(f, modo: str, minutos: int) -> None:
        print(modo, '→', orden(modo, a.ma), flush=True)
        for _ in range(minutos + 1):
            fila = f'{time.time() - t0:.0f},{modo},{nivel()}'
            print(fila, flush=True)
            f.write(fila + '\n')
            f.flush()
            time.sleep(60)

    with open(d / f'nivel-{a.ma}mA.csv', 'a') as f:
        try:
            fase(f, 'normal', a.control)
            fase(f, 'carga', a.carga)
        finally:
            print('final normal →', orden('normal', a.ma), flush=True)


if __name__ == '__main__':
    main()
