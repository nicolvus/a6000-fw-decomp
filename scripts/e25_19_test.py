#!/usr/bin/env python3
"""E25-19 — controlador de disparos normales con lectura concurrente de RAM (solo lectura).

Usa solo RemoteShutter (`/ss`, `/shoot`, `/status`, `/info`, `/log`) y el lector `e25_19_readonly`.
Sin ráfagas, sin BULB, sin reintentos automáticos, sin escrituras en la cámara. Entre disparos
comprueba salud (estado libre, telnet, bytes originales, dmesg) y se detiene ante la primera anomalía.

Uso: e25_19_test.py --confirm-readonly [--speeds 1/30 1/8 1 4] [--cap-phys 0x...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e25_19_readonly import HOST, OUTDIR, Telnet, diff, now, snapshot, verify_originals

ERR_RE = re.compile(r"error|fail|oops|panic|watchdog|timeout|reset", re.IGNORECASE)


def speed_args(sp: str) -> tuple[int, int]:
    """'1/30' → (1, 30); '4' → (4, 1)."""
    n, _, d = sp.partition("/")
    return int(n), int(d or 1)


class Camera:
    def __init__(self, host: str):
        self.base = f"http://{host}:8080"

    def get(self, path: str, t: float = 60) -> str:
        return urllib.request.urlopen(self.base + path, timeout=t).read().decode().strip()

    def info(self) -> dict:
        raw = self.get("/info")
        return {"raw": raw, **dict(kv.split("=", 1) for kv in raw.split() if "=" in kv)}

    def status(self) -> str:
        return self.get("/status")


def dmesg_lines(tr: Telnet) -> set[str]:
    return {line for line in tr.run("dmesg").splitlines() if line.strip()}


def health(cam: Camera, tr: Telnet, dm0: set[str]) -> dict:
    """Condición de continuar: libre, telnet vivo, originales intactos, sin errores nuevos."""
    h: dict = {"status": cam.status(), "info": cam.info()["raw"]}
    orig = verify_originals(tr)
    new = sorted(dmesg_lines(tr) - dm0)
    h["originales_ok"] = orig["ok"]
    h["dmesg_nuevas"] = new
    h["dmesg_errores"] = [x for x in new if ERR_RE.search(x)]
    busy = h["status"].startswith(("shooting", "queued")) or "error" in h["status"]
    h["ok"] = not busy and "bursting=false" in h["info"] and orig["ok"] and not h["dmesg_errores"]
    return h


def poll(tr: Telnet, stop: threading.Event, out: list, cap_phys: int | None) -> None:
    """Lecturas sucesivas hasta `stop`; cada una lleva su hora para ordenar contra el disparo."""
    while not stop.is_set():
        try:
            out.append(snapshot(tr, f"poll{len(out)}", cap_phys, light=True))
        except Exception as exc:  # noqa: BLE001 - se conserva la evidencia
            out.append({"error": str(exc), "t_epoch": time.time()})
            return


def shoot(cam: Camera, tr_poll: Telnet, speed: str, cap_phys: int | None, settle: float) -> dict:
    n, d = speed_args(speed)
    rec: dict = {"speed": speed, "set": cam.get(f"/ss?n={n}&d={d}")}
    time.sleep(0.5)
    c0 = int(cam.info()["count"])
    rec["pre"] = snapshot(tr_poll, "pre", cap_phys)
    samples: list = []
    stop = threading.Event()
    th = threading.Thread(target=poll, args=(tr_poll, stop, samples, cap_phys), daemon=True)
    th.start()
    time.sleep(0.3)  # varias lecturas previas al disparo, con la cámara libre
    rec["t_shoot_epoch"] = time.time()
    rec["shoot_reply"] = cam.get("/shoot")
    rec["t_shoot_reply_epoch"] = time.time()
    t_end = None
    while time.time() - rec["t_shoot_epoch"] < 150:
        st = cam.status()
        rec.setdefault("status_trace", []).append([round(time.time() - rec["t_shoot_epoch"], 3), st])
        if "error" in st:
            rec["status_error"] = st
            break
        if not st.startswith(("shooting", "queued")) and int(cam.info()["count"]) > c0:
            t_end = time.time()
            break
        time.sleep(0.15)
    rec["t_done_epoch"] = t_end
    time.sleep(settle)  # estado posterior estabilizado
    stop.set()
    th.join(timeout=30)
    rec["samples"] = samples
    rec["post"] = snapshot(tr_poll, "post", cap_phys)
    rec["duracion_s"] = None if t_end is None else round(t_end - rec["t_shoot_epoch"], 3)
    log = [ln for ln in cam.get("/log").splitlines() if ln.split(",")[0].isdigit() and int(ln.split(",")[0]) > c0]
    rec["log_remoteshutter"] = log
    rec["diff_pre_post"] = diff(rec["pre"], rec["post"])
    rec["completada"] = t_end is not None and bool(log)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=HOST)
    ap.add_argument("--speeds", nargs="+", default=["1/30", "1/8", "1", "4"])
    ap.add_argument("--cap-phys", type=lambda x: int(x, 0))
    ap.add_argument("--settle", type=float, default=2.0)
    ap.add_argument("--confirm-readonly", action="store_true", required=True)
    a = ap.parse_args()

    cam = Camera(a.host)
    tr_ctl, tr_poll = Telnet(a.host), Telnet(a.host)
    dm0 = dmesg_lines(tr_ctl)
    res: dict = {"schema": "e25-19-test/v1", "inicio": now(), "host": a.host, "shots": [], "abort": None}
    res["salud_inicial"] = health(cam, tr_ctl, dm0)
    if not res["salud_inicial"]["ok"]:
        res["abort"] = "salud inicial no OK; no se dispara"
    else:
        for sp in a.speeds:
            rec = shoot(cam, tr_poll, sp, a.cap_phys, a.settle)
            rec["salud"] = health(cam, tr_ctl, dm0)
            res["shots"].append(rec)
            ok = rec["completada"] and rec["salud"]["ok"]
            print(f"{sp}: dur={rec['duracion_s']} s muestras={len(rec['samples'])} completada={rec['completada']} salud={rec['salud']['ok']}",
                  flush=True)
            if not ok:
                res["abort"] = f"anomalía tras {sp}; se detienen las pruebas (sin reintento ni recuperación)"
                break
    res["fin"] = now()
    out = OUTDIR / f"disparos-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(out, "abort:", res["abort"])
    return 0 if not res["abort"] else 1


if __name__ == "__main__":
    sys.exit(main())
