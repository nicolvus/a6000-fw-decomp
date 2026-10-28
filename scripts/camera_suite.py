#!/usr/bin/env python3
"""Suite de verificación de imágenes con RemoteShutter v5: dispara y mide todo a la vez.

Uso: camera_suite.py OUTDIR [--host 192.168.1.29] [--quick]
Por disparo mide: latencia disparo→JPEG, tamaño, EXIF, luminancia, saturación, franjas oscuras, gradiente por filas y bandas;
en ráfagas, el intervalo de rearme; y el dmesg de la cámara antes/después.
No escribe RAM ni NVRAM ni drive_mode: solo `takePicture` y la velocidad (`/ss`). Genera report.json, report.md y montaje.jpg.
No se mide sonido: el obturador mecánico está desactivado por completo (B1a)."""
import argparse
import io
import json
import re
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
from PIL import ExifTags, Image

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--host", default="192.168.1.29")
ap.add_argument("--quick", action="store_true")
a = ap.parse_args()
H = f"http://{a.host}:8080"
OUT = Path(a.out)
OUT.mkdir(parents=True, exist_ok=False)
HERE = Path(__file__).parent


def get(p: str, t: float = 60) -> bytes:
    return urllib.request.urlopen(H + p, timeout=t).read()


def telnet(cmd: str) -> str:
    r = subprocess.run([sys.executable, str(HERE / "camera_telnet.py"), "--host", a.host, cmd],
                       capture_output=True, text=True, timeout=60, check=False)
    return r.stdout


def info() -> dict:
    t = get("/info").decode().strip()
    return {"raw": t, **dict(kv.split("=", 1) for kv in t.split() if "=" in kv)}


def wait_idle(limit: float = 90) -> None:
    t0 = time.time()
    while time.time() - t0 < limit:
        if info()["bursting"] == "false" and not get("/status").decode().startswith(("shooting", "queued")):
            return
        time.sleep(0.4)
    raise TimeoutError("la cámara no quedó libre")


def metrics(jpg: bytes) -> dict:
    im = Image.open(io.BytesIO(jpg))
    exif = {ExifTags.TAGS.get(k, k): v for k, v in (im._getexif() or {}).items()}
    g = np.asarray(im.convert("L"), dtype=np.float32)
    rows = g.mean(axis=1)
    sm = np.convolve(rows, np.ones(7) / 7, mode="same")
    k = max(len(rows) // 8, 1)
    return {
        "size": im.size, "bytes": len(jpg), "lum": round(float(g.mean()), 1),
        "sat_pct": round(float((g >= 250).mean() * 100), 1), "dark_pct": round(float((g <= 5).mean() * 100), 1),
        "rows_min": round(float(rows.min()), 1), "rows_max": round(float(rows.max()), 1),
        "octavos": [round(float(rows[i * k:(i + 1) * k].mean()), 0) for i in range(8)],
        "bandas": round(float(np.sqrt(np.mean((sm[8:] - sm[:-8]) ** 2))), 2),
        "exif": {k2: str(exif.get(k2)) for k2 in ("ExposureTime", "ISOSpeedRatings", "FNumber") if k2 in exif},
    }


def dmesg() -> set[str]:
    return {line for line in telnet("dmesg").splitlines() if line.strip()}


# ------------------------------------------------------------------ medición
report: dict = {"host": a.host, "inicio": time.strftime("%Y-%m-%d %H:%M:%S"), "shots": [], "bursts": []}
report["info_inicial"] = info()["raw"]
dm0 = dmesg()
get("/nr?v=0")
get("/log?clear=1")
SPEEDS = ["1/4000", "1/250", "1/15"] if a.quick else ["1/4000", "1/1000", "1/250", "1/60", "1/15"]
REPS = 1 if a.quick else 2


def clock_offset() -> float:
    h = time.time()
    t = int(info()["t"]) / 1000
    return h - t  # reloj PC = reloj cámara + offset (±RTT)


def pull_new(prev_count: int) -> list[tuple[int, bytes]]:
    n = int(info()["count"])
    return [(i, get(f"/jpg?i={i}")) for i in range(prev_count + 1, n + 1)]


def run_log(since_count: int) -> list[dict]:
    rows = []
    for line in get("/log").decode().splitlines():
        i, t0, ms, by, rt = (int(v) for v in line.split(","))
        if i > since_count:
            rows.append({"n": i, "t0": t0 / 1000, "ms": ms, "bytes": by, "reintentos": rt})
    return rows


for sp in SPEEDS:
    n, d = sp.split("/")
    ss = get(f"/ss?n={n}&d={d}").decode().strip()
    for rep in range(REPS):
        wait_idle()
        c0 = int(info()["count"])
        off = clock_offset()
        get("/shoot")
        time.sleep(0.5)
        wait_idle()
        (n_img, jpg), = pull_new(c0)
        row = run_log(c0)[0]
        m = metrics(jpg)
        (OUT / f"{n_img:03d}_{n}_{d}_r{rep}.jpg").write_bytes(jpg)
        report["shots"].append({"speed": sp, "set": ss, "rep": rep, "ms": row["ms"], "reintentos_apertura": row["reintentos"], **m,
                                })
        print(sp, rep, ss, row["ms"], "ms", m["lum"], "lum", m["sat_pct"], "% sat", flush=True)

# Ráfagas: rearme sin pausa (gap 0) y con pausa
for n_b, gap, sp in ([(4, 0, "1/250")] if a.quick else [(8, 0, "1/250"), (5, 500, "1/250"), (4, 0, "1/15")]):
    n, d = sp.split("/")
    get(f"/ss?n={n}&d={d}")
    wait_idle()
    c0 = int(info()["count"])
    off = clock_offset()
    ts = time.time()
    get(f"/burst?n={n_b}&gap={gap}")
    time.sleep(1)
    wait_idle(180)
    rows = run_log(c0)
    imgs = dict(pull_new(c0))
    gaps = [round((rows[i + 1]["t0"] - rows[i]["t0"]) * 1000 - rows[i]["ms"]) for i in range(len(rows) - 1)]
    lum = []
    for r in rows:
        m = metrics(imgs[r["n"]])
        lum.append(m["lum"])
        (OUT / f"{r['n']:03d}_burst_{n}_{d}.jpg").write_bytes(imgs[r["n"]])
    report["bursts"].append({"n": n_b, "gap_ms": gap, "speed": sp, "disparos": len(rows), "ms": [r["ms"] for r in rows], "reintentos_apertura": [r["reintentos"] for r in rows],
                             "rearme_ms": gaps, "lum": lum, "estado_final": get("/status").decode().strip()})
    print("rafaga", n_b, gap, sp, len(rows), "disparos; ms", [r["ms"] for r in rows], flush=True)

dm1 = dmesg()
nuevas = sorted(dm1 - dm0)
report["dmesg_nuevas"] = nuevas
report["dmesg_errores"] = [line for line in nuevas if re.search(r"error|fail|oops|panic|watchdog|timeout|reset", line, re.IGNORECASE)]
# ------------------------------------------------------------------ veredicto
sh, bu = report["shots"], report["bursts"]
c = {
    "todos_done": all(s["bytes"] > 100_000 for s in sh) and all(b["disparos"] == b["n"] for b in bu),
    "sin_shoot_error": not any("error" in b["estado_final"] for b in bu),
    "sin_franjas_negras": all(s["dark_pct"] < 5 and s["rows_min"] > 3 for s in sh),
    "sin_dmesg_errores": not report["dmesg_errores"],
    "tamaño_1616x1080": all(tuple(s["size"]) == (1616, 1080) for s in sh),
    "rearme_estable": all(max(b["rearme_ms"] or [0]) < 3000 for b in bu),
    "exposicion_escala_con_velocidad": len({s["lum"] for s in sh if s["speed"] in ("1/4000", "1/1000", "1/250")}) > 1
    and statistics.mean(s["lum"] for s in sh if s["speed"] == "1/15") < statistics.mean(s["lum"] for s in sh if s["speed"] == "1/4000"),
}
report["veredicto"] = c
(OUT / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
lines = ["| velocidad | rep | ms | lum | sat % | oscuro % | bandas |", "|---|---|---|---|---|---|---|"]
for s in sh:
    lines.append(f"| {s['speed']} | {s['rep']} | {s['ms']} | {s['lum']} | {s['sat_pct']} | {s['dark_pct']} | {s['bandas']} |")
lines += ["", "| ráfaga | disparos | ms por disparo | rearme ms | reintentos de apertura | lum |", "|---|---|---|---|---|---|"]
for b in bu:
    lines.append(f"| {b['n']}×{b['speed']} gap {b['gap_ms']} | {b['disparos']} | {b['ms']} | {b['rearme_ms']} | {b['reintentos_apertura']} | {b['lum']} |")
lines += ["", "Estado final de ráfagas: " + "; ".join(f"{b['n']}×{b['speed']} → {b['estado_final']}" for b in bu), "", "Veredicto: " + ", ".join(f"{k}={'SÍ' if v else 'NO'}" for k, v in c.items()),
          f"dmesg: {len(nuevas)} líneas nuevas, {len(report['dmesg_errores'])} con palabras de error"]
(OUT / "report.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))

# Montaje de todas las imágenes
jp = sorted(OUT.glob("*.jpg"))[:24]
tw, th = 404, 270
sheet = Image.new("RGB", (tw * 6, th * ((len(jp) + 5) // 6)))
for i, p in enumerate(jp):
    sheet.paste(Image.open(p).resize((tw, th)), ((i % 6) * tw, (i // 6) * th))
sheet.save(OUT / "montaje.jpg")
