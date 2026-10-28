#!/usr/bin/env python3
"""Exposición real desde el RAW (ARW) con RemoteShutter v7: ISO fijo, barrido de velocidades, RAW+JPEG.

Uso: camera_raw_exposure.py OUTDIR [--host 192.168.1.29] [--iso 100] [--reps 2] [n/d ...]
Cambia el formato a rawjpeg y el ISO al valor fijo; al terminar (o si falla) deja jpeg e ISO automático (0).
Por disparo trae el ARW de la tarjeta (DCIM) y mide, en lineal y sin negro: media por canal CFA, fracción saturada,
perfil por bandas de filas y la exposición relativa media/(ISO/100). Si la velocidad escala la exposición, la media
lineal se duplica al duplicar el tiempo; el ajuste log2 vs log2(tiempo) debe dar pendiente ≈ 1."""
import argparse
import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import rawpy
from adb_shell.adb_device import AdbDeviceTcp

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("speeds", nargs="*")
ap.add_argument("--host", default="192.168.1.29")
ap.add_argument("--iso", type=int, default=100)
ap.add_argument("--reps", type=int, default=2)
a = ap.parse_args()
SPEEDS = a.speeds or ["1/4000", "1/2000", "1/1000", "1/500", "1/250", "1/125", "1/60", "1/30", "1/15", "1/8"]
OUT = Path(a.out)
OUT.mkdir(parents=True, exist_ok=False)


def get(p: str, t: float = 120) -> str:
    return urllib.request.urlopen(f"http://{a.host}:8080{p}", timeout=t).read().decode().strip()


adb = AdbDeviceTcp(a.host, 5555, default_transport_timeout_s=60)
adb.connect(rsa_keys=None, auth_timeout_s=10)


def card_files() -> set[str]:
    out = adb.shell("ls /mnt/sdcard/DCIM")
    folder = max((x for x in out.split() if x[:3].isdigit()), key=lambda x: int(x[:3]))
    return {f"{folder}/{f}" for f in adb.shell(f"ls /mnt/sdcard/DCIM/{folder}").split() if f.startswith("DSC")}


def idle() -> None:
    t0 = time.time()
    while time.time() - t0 < 60:
        if not get("/status").startswith(("shooting", "queued")):
            return
        time.sleep(0.3)
    raise TimeoutError("la cámara no quedó libre")


def raw_metrics(path: Path) -> dict:
    r = rawpy.imread(str(path))
    x = r.raw_image_visible.astype(np.float32)
    bl = np.array(r.black_level_per_channel, dtype=np.float32).mean()
    white = float(r.white_level)
    lin = x - bl
    cfa = r.raw_colors_visible
    chans = {n: float(lin[cfa == i].mean()) for i, n in enumerate(("R", "G1", "B", "G2"))}
    k = lin.shape[0] // 8
    return {
        "shape": list(x.shape), "black": float(bl), "white": white,
        "mean_lin": float(lin.mean()), "chans": chans,
        "sat_pct": round(float((x >= white - 1).mean() * 100), 3), "dark_pct": round(float((lin <= 8).mean() * 100), 2),
        "octavos": [round(float(lin[i * k:(i + 1) * k].mean()), 1) for i in range(8)],
    }


results, restore = [], []
try:
    print("fmt", get("/fmt?v=rawjpeg"), "iso", get(f"/iso?v={a.iso}"), flush=True)
    for sp in SPEEDS:
        n, d = sp.split("/")
        ss = get(f"/ss?n={n}&d={d}")
        for rep in range(a.reps):
            idle()
            before = card_files()
            get("/shoot")
            time.sleep(0.5)
            idle()
            time.sleep(1.5)  # la cámara termina de escribir el ARW tras el callback
            new = sorted(card_files() - before)
            arw = [f for f in new if f.endswith(".ARW")]
            row = {"speed": sp, "set": ss, "rep": rep, "nuevos": new}
            if arw:
                dst = OUT / f"{sp.replace('/', '_')}_r{rep}.ARW"
                adb.pull(f"/mnt/sdcard/DCIM/{arw[0]}", str(dst))
                row.update(raw_metrics(dst))
                row["rel"] = row["mean_lin"] / (a.iso / 100)
            results.append(row)
            print(sp, rep, ss, "ARW" if arw else "SIN ARW", row.get("mean_lin"), row.get("sat_pct"), flush=True)
finally:
    print("restaurar:", get("/iso?v=0"), get("/fmt?v=jpeg"), flush=True)

# Pendiente log2(media) vs log2(tiempo), solo puntos sin saturar y por encima del negro
pts = [(np.log2(int(r["speed"].split("/")[0]) / int(r["speed"].split("/")[1])), np.log2(r["mean_lin"]))
       for r in results if r.get("mean_lin", 0) > 20 and r.get("sat_pct", 100) < 0.5]
slope = float(np.polyfit(*zip(*pts), 1)[0]) if len(pts) > 2 else None
summary = {"iso": a.iso, "pendiente_log2": slope, "puntos": len(pts), "resultados": results}
(OUT / "report.json").write_text(json.dumps(summary, indent=1))
print("pendiente log2(media)/log2(tiempo) =", slope, "(1.0 = la velocidad escala la exposición)")
for r in results:
    if "mean_lin" in r:
        print(f"{r['speed']:>7} r{r['rep']} media={r['mean_lin']:8.1f} sat={r['sat_pct']}% octavos={r['octavos']}")
