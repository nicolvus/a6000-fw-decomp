#!/usr/bin/env python3
"""E25-11: volcados de 4 MiB de RAM (solo lectura, /dev/mem) tras un disparo a cada velocidad, y búsqueda de lo que sigue a la velocidad.

Uso: camera_ram_speed_scan.py OUTDIR [fisica_inicial_hex=83c00000]   (RemoteShutter v7 abierta, adb 5555)
Por velocidad 1/60, 1/250, 1/500, 1/1000: /ss, /shoot y `dd if=/dev/mem` de 4 MiB al archivo OUTDIR/r_<d>.bin (los ficheros de /data son de solo
lectura: se borra antes de cada volcado). Después busca halfwords = 0x1000+256·log2(1/t) (código Tv de 0x4382fac8), pasos de ±256/±527 y
valores monótonos o proporcionales al tiempo. No escribe RAM, NVRAM ni flash."""
import math
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
from adb_shell.adb_device import AdbDeviceTcp

H = "192.168.1.29"
OUT = Path(sys.argv[1])
BASE = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x83C00000
SPEEDS = (60, 250, 500, 1000)
OUT.mkdir(parents=True, exist_ok=True)


def get(p, t=120):
    return urllib.request.urlopen(f"http://{H}:8080{p}", timeout=t).read().decode().strip()


adb = AdbDeviceTcp(H, 5555, default_transport_timeout_s=120)
adb.connect(rsa_keys=None, auth_timeout_s=10)
for den in SPEEDS:
    get(f"/ss?n=1&d={den}")
    get("/shoot")
    time.sleep(1)
    while get("/status").startswith(("shooting", "queued")):
        time.sleep(0.3)
    time.sleep(1)
    tmp = f"/data/local/tmp/m{den}.bin"
    adb.shell(f"rm -f {tmp}; dd if=/dev/mem bs=1048576 skip={BASE >> 20} count=4 of={tmp} 2>/dev/null")
    adb.pull(tmp, str(OUT / f"r_{den}.bin"))
    adb.shell(f"rm -f {tmp}")
    print("volcado", den, get("/status"), flush=True)

w = {d: np.frombuffer((OUT / f"r_{d}.bin").read_bytes(), dtype="<u2").astype(int) for d in SPEEDS}
exp = {d: round(4096 + 256 * math.log2(d)) for d in SPEEDS}
tv = np.ones(len(w[60]), bool)
for d, x in exp.items():
    tv &= abs(w[d] - x) <= 3
print("halfwords con el código Tv 0x1000+256·log2(1/t) (±3) en las 4 velocidades:", int(tv.sum()))
for sgn in (1, -1):
    m = (abs(w[500] - w[250] - sgn * 256) <= 4) & (abs(w[1000] - w[500] - sgn * 256) <= 4) & (abs(w[250] - w[60] - sgn * 527) <= 6)
    print("pasos ±256/±527 (1/256 EV), signo", sgn, int(m.sum()))
idx = np.nonzero((w[250] - w[60] == 6) & (w[500] - w[250] == 3) & (w[1000] - w[500] >= 3))[0]
print("índices en tercios de EV (6, 3, 3–4):", [hex(BASE + 2 * i) for i in idx[:12]])
