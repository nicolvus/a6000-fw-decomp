#!/usr/bin/env python3
"""E25-10: exposición por fila en RAW con parche RAM (ShutMode 0 + r5 forzado), como T035–T039 pero midiendo el ARW.

Uso: camera_r5_raw.py OUTDIR [r5 ...]   (con r5 dados solo mide esos a 1/250; (RemoteShutter v7 abierta, telnet 23 y adb 5555, escena fija, escena no tocada durante la prueba)
Solo RAM, nada de flash/NVRAM. Parches (BIONZ, direcciones de T034/T035): ShutMode 0 `0x836d6fb6` y r5 `0x836d7000`
(`movs r0,#hi; mov.w lr,#lo`, r5 = 256·hi + lo). Antes: comprueba el código original y G+0x784. Siempre revierte y verifica;
aborta (y revierte) si un disparo no termina en 45 s. Deja jpeg e ISO automático."""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import rawpy
from adb_shell.adb_device import AdbDeviceTcp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from camera_telnet import run

HOST, G784 = "192.168.1.29", 0x83E9BCCC
SM_A, SM_O, SM_N = 0x836D6FB6, "91f80990", "4ff00009"
R5_A, R5_O = 0x836D7000, "28125ffa85fe"
NB = 32
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=False)


def rd(addr, n):
    out = run(HOST, [f"dd if=/dev/mem bs=1 skip={addr} count={n} of=/android/dev/z 2>/dev/null; chroot /android /system/bin/hd /dev/z; rm -f /android/dev/z"])[0]
    data = bytearray()
    for line in out.splitlines():
        parts = line.replace(":", " ").split()
        if parts and len(parts[0]) == 8 and all(c in "0123456789abcdef" for c in parts[0]):
            data += bytes(int(x, 16) for x in parts[1:17] if len(x) == 2)
    return data[:n].hex()


def wr(addr, hexs):
    esc = "".join(f"\\0{int(hexs[i:i + 2], 16):03o}" for i in range(0, len(hexs), 2))
    assert addr % 2 == 0 and len(hexs) % 4 == 0
    run(HOST, [f"echo -ne '{esc}' | dd of=/dev/mem bs=2 seek={addr // 2} count={len(hexs) // 4} 2>/dev/null"])


def r5_bytes(v):
    return f"{v >> 8:02x}20" + f"4ff0{v & 255:02x}0e"


def get(p, t=120):
    return urllib.request.urlopen(f"http://{HOST}:8080{p}", timeout=t).read().decode().strip()


adb = AdbDeviceTcp(HOST, 5555, default_transport_timeout_s=60)
adb.connect(rsa_keys=None, auth_timeout_s=10)


def card_files():
    folder = max((x for x in adb.shell("ls /mnt/sdcard/DCIM").split() if x[:3].isdigit()), key=lambda x: int(x[:3]))
    return {f"{folder}/{f}" for f in adb.shell(f"ls /mnt/sdcard/DCIM/{folder}").split() if f.startswith("DSC")}


def shoot(tag):
    before = card_files()
    get("/shoot")
    t0 = time.time()
    time.sleep(0.5)
    while get("/status").startswith(("shooting", "queued")):
        if time.time() - t0 > 45:
            raise TimeoutError(f"{tag}: el disparo no termina")
        time.sleep(0.3)
    time.sleep(1.5)
    arw = sorted(f for f in card_files() - before if f.endswith(".ARW"))
    if not arw:
        raise RuntimeError(f"{tag}: sin ARW")
    dst = OUT / f"{tag}.ARW"
    adb.pull(f"/mnt/sdcard/DCIM/{arw[0]}", str(dst))
    r = rawpy.imread(str(dst))
    x = r.raw_image_visible.astype(np.float32) - np.mean(r.black_level_per_channel)
    k = x.shape[0] // NB
    return [round(float(x[i * k:(i + 1) * k].mean()), 2) for i in range(NB)]


cur = (rd(SM_A, 4), rd(R5_A, 6))
print("código", cur, "G+0x784", rd(G784, 4), flush=True)
assert cur == (SM_O, R5_O), f"código inesperado {cur}: no se parchea"
res = []
try:
    print("fmt", get("/fmt?v=rawjpeg"), "iso", get("/iso?v=100"), flush=True)
    for sp in ("1/8", "1/15", "1/60"):  # referencia sin parche: ajusta escena y τ por banda
        n, d = sp.split("/")
        get(f"/ss?n={n}&d={d}")
        res.append({"modo": "normal", "T": int(n) / int(d), "bandas": shoot(f"ref_{n}_{d}")})
        print("ref", sp, flush=True)
    wr(SM_A, SM_N)
    assert rd(SM_A, 4) == SM_N
    plan = (("1/250", [int(v) for v in sys.argv[2:]]),) if sys.argv[2:] else (
        ("1/250", [None, 0, 1000, 2000, 3000, 3500, 4000, 4100, 4200, 4300]), ("1/30", [None, 1240, 2500, 4000]))
    for sp, r5s in plan:
        n, d = sp.split("/")
        get(f"/ss?n={n}&d={d}")
        for v in r5s:
            if v is None:
                wr(R5_A, R5_O)
            else:
                wr(R5_A, r5_bytes(v))
                assert rd(R5_A, 6) == r5_bytes(v), "r5 no aplicado"
            tag = f"sm0_{n}_{d}_r5_{v}"
            res.append({"modo": "sm0", "T": int(n) / int(d), "r5": v, "bandas": shoot(tag)})
            print(tag, "G+0x784", rd(G784, 4), flush=True)
finally:
    wr(R5_A, R5_O)
    wr(SM_A, SM_O)
    time.sleep(0.5)
    fin = (rd(SM_A, 4), rd(R5_A, 6))
    print("revertido", fin, "OK" if fin == (SM_O, R5_O) else "FALLO", flush=True)
    try:
        print("restaurar", get("/iso?v=0"), get("/fmt?v=jpeg"), flush=True)
    except Exception as e:  # noqa: BLE001
        print("restaurar ISO/formato falló:", e, flush=True)
    with open(OUT / "bandas.json", "w") as fh:
        json.dump({"nb": NB, "resultados": res}, fh)
