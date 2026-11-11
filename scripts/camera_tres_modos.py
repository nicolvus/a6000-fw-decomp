#!/usr/bin/env python3
"""E26-R87 — tripletas Silent / EFCS / Mecánico disparadas en remoto con RemoteShutter v9 (`/mode`), ARW a ISO fijo.

Por velocidad: `/ss`, y para cada modo `/mode?v=…` + `/shoot`; trae el ARW nuevo de la tarjeta por adb y lo guarda como
`DSC0NNNN.ARW` en OUTDIR (nombre de la tarjeta). Al final deja `/mode?v=menu`, JPEG e ISO automático.
Escribe `tripletas.txt` (SILENT,EFCS,MECH por línea) para `e26_r85_calibrar_fotos.py`.
Uso: camera_tres_modos.py OUTDIR [--host 192.168.1.18] [--iso 100] [n/d ...]
"""
import argparse
import os
import time
import urllib.request
from pathlib import Path

from adb_shell.adb_device import AdbDeviceTcp

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("speeds", nargs="*")
ap.add_argument("--host", default=os.environ.get("A6000_HOST", "192.168.1.18"))
ap.add_argument("--iso", type=int, default=100)
ap.add_argument("--modos", default="silent,efcs,mech")
a = ap.parse_args()
SPEEDS = a.speeds or ["1/4000", "1/1000", "1/500", "1/250", "1/125", "1/60"]
OUT = Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)


def get(p: str, t: float = 120) -> str:
    return urllib.request.urlopen(f"http://{a.host}:8080{p}", timeout=t).read().decode().strip()


adb = AdbDeviceTcp(a.host, 5555, default_transport_timeout_s=60)
adb.connect(rsa_keys=None, auth_timeout_s=10)


def card() -> set[str]:
    out = adb.shell("ls /mnt/sdcard/DCIM")
    folder = max((x for x in out.split() if x[:3].isdigit()), key=lambda x: int(x[:3]))
    return {f"{folder}/{f}" for f in adb.shell(f"ls /mnt/sdcard/DCIM/{folder}").split() if f.endswith(".ARW")}


def wait_done(t=60) -> str:
    t0 = time.time()
    while time.time() - t0 < t:
        s = get("/status")
        if s.startswith(("done", "shoot-error")):
            return s
        time.sleep(0.3)
    raise TimeoutError("sin callback")


trip = []
try:
    print("fmt", get("/fmt?v=raw"), "| iso", get(f"/iso?v={a.iso}"), flush=True)
    for sp in SPEEDS:
        n, d = sp.split("/")
        print(sp, get(f"/ss?n={n}&d={d}"), flush=True)
        fila = []
        for modo in a.modos.split(","):
            print("  ", get(f"/mode?v={modo}"), flush=True)
            antes = card()
            get("/shoot")
            st = wait_done()
            nuevo = []
            for _ in range(40):
                nuevo = sorted(card() - antes)
                if nuevo:
                    break
                time.sleep(0.5)
            if not nuevo or st.startswith("shoot-error"):
                raise RuntimeError(f"{sp} {modo}: {st} {nuevo}")
            time.sleep(1.0)    # que termine de escribir
            dst = OUT / Path(nuevo[-1]).name
            adb.pull(f"/mnt/sdcard/DCIM/{nuevo[-1]}", str(dst))
            fila.append(dst.stem)
            print(f"   {modo}: {dst.name} ({dst.stat().st_size} B) {st}", flush=True)
        trip.append(",".join(fila))
        (OUT / "tripletas.txt").write_text("\n".join(trip) + "\n")
finally:
    for p in ("/mode?v=menu", "/fmt?v=jpeg", "/iso?v=0"):
        try:
            print("restaura", get(p))
        except Exception as e:  # noqa: BLE001
            print("restaura-error", p, e)
