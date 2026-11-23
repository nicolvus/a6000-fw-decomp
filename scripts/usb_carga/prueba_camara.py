#!/usr/bin/env python3
"""Prueba en la cámara de la carga USB con la A6000 encendida (USB-CARGA). Telnet del Tweak (root).

  prueba_camara.py subir                 sube analysis/usb-carga/build/*.ko a /tmp (tmpfs; desaparece al apagar)
  prueba_camara.py cargar [--buspwr]     insmod usb_darwin.ko (y usb_buspwr.ko con --buspwr)
  prueba_camara.py orden CMD...          escribe en /proc/udm/usb_darwin y muestra el dmesg nuevo.
                                         3 = tipo de adaptador, 4 = límite actual, '5 02' = límite 500 mA
                                         ('5 03' 900, '5 04' 1500, '5 05' 2000), E = activar carga, F = desactivar
  prueba_camara.py vigilar MIN [ETIQ]    nivel de batería (dumpsys) cada 60 s → analysis/camera-dumps/<fecha>-usb-carga/ETIQ.csv
  prueba_camara.py descargar             rmmod de ambos (apagar la cámara también lo deshace todo)
Nada se escribe en NAND ni en NVRAM. A6000_HOST=ip.
"""
import csv
import datetime
import pathlib
import re
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import camera_get as cg
from camera_telnet import run

RAIZ = pathlib.Path(__file__).resolve().parents[2]
BUILD = RAIZ / 'analysis/usb-carga/build'
OBB = cg.TMP_ROOT
MODS = ('usb_darwin', 'usb_buspwr')


def sh(*cmds: str, timeout: float = 30) -> list[str]:
    return run(cg.HOST, list(cmds), timeout=timeout)


def nivel() -> int:
    sh(f"echo 'PATH=/system/bin; dumpsys battery > /mnt/obb/bt.txt 2>&1' > {OBB}/bt.sh",
       'chroot /android /system/bin/sh /mnt/obb/bt.sh')
    txt = sh(f'cat {OBB}/bt.txt; rm -f {OBB}/bt.txt {OBB}/bt.sh')[0]
    m = re.search(r'level: (\d+)', txt)
    if not m:
        raise SystemExit(f'sin nivel de batería:\n{txt}')
    return int(m.group(1))


def subir() -> None:
    for m in MODS:
        subprocess.run([sys.executable, str(RAIZ / 'scripts/camera_push_file.py'), str(BUILD / f'{m}.ko'),
                        f'/tmp/{m}.ko', cg.HOST], check=True)


def cargar(buspwr: bool) -> None:
    for m in MODS[:1 + buspwr]:
        print(sh(f'insmod /tmp/{m}.ko; echo rc=$?; dmesg | tail -n 15')[0])
    print(sh('lsmod | grep usb_; ls -l /proc/udm/ | grep usb_')[0])


def orden(cmd: str) -> None:
    antes = len(sh('dmesg')[0].splitlines())
    sh(f"echo '{cmd}' > /proc/udm/usb_darwin")
    time.sleep(1)
    print('\n'.join(sh('dmesg')[0].splitlines()[antes - 5:]))


def vigilar(minutos: int, etiqueta: str) -> None:
    d = RAIZ / f'analysis/camera-dumps/{datetime.date.today():%Y%m%d}-usb-carga'
    d.mkdir(parents=True, exist_ok=True)
    with open(d / f'{etiqueta}.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['segundos', 'nivel'])
        t0 = time.time()
        for _ in range(minutos + 1):
            n = nivel()
            w.writerow([round(time.time() - t0), n])
            f.flush()
            print(f'{(time.time() - t0) / 60:5.1f} min  {n} %', flush=True)
            time.sleep(60)
    print('→', d / f'{etiqueta}.csv')


def main() -> None:
    a = sys.argv[1:]
    if a[:1] == ['subir']:
        subir()
    elif a[:1] == ['cargar']:
        cargar('--buspwr' in a)
    elif a[:1] == ['orden'] and len(a) > 1:
        orden(' '.join(a[1:]))
    elif a[:1] == ['vigilar'] and len(a) > 1:
        vigilar(int(a[1]), a[2] if len(a) > 2 else 'nivel')
    elif a[:1] == ['descargar']:
        print(sh('rmmod usb_buspwr; rmmod usb_darwin; lsmod | grep usb_')[0])
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
