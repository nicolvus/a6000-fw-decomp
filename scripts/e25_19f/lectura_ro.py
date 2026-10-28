#!/usr/bin/env python3
"""E25-19f P4 — lectura física SOLO LECTURA: `cap` completo (0..0xe00) en vuelo y tras la exposición, en una foto normal.

Reposo: G+0x60/+0x7e/+0x7f y la tabla 0x43e95150..0x43e951a0. En vuelo (bucle rápido, solo `cap`): 0x19a..0x1a0 y 0x740..0x758.
No escribe en la cámara; dispara UNA foto normal por RemoteShutter como E25-19b. Uso: PYTHONPATH=scripts lectura_ro.py --confirm-readonly [--speed 4]
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from pathlib import Path

from e25_19_readonly import HOST, Telnet, verify_originals  # type: ignore[import-not-found]
from e25_19_test import Camera, speed_args  # type: ignore[import-not-found]
from e25_19b_cadena import RAM_OFF  # type: ignore[import-not-found]
from e25_19b_cap import E1, RAM, u32  # type: ignore[import-not-found]
from e25_19b_compuerta import decode_gestor  # type: ignore[import-not-found]

OUT = Path(__file__).resolve().parents[2] / "analysis/e25-19f"
G = 0x43E95950
TABLA = 0x43E95150
CAP_REGS = [(0x0, 0xE00)]


def globales(tr: Telnet) -> dict:
    g, t = tr.read_many([(G + 0x58 + RAM_OFF, 0x30), (TABLA + RAM_OFF, 0x50)])
    return {"G+0x58": g.hex(), "tabla@0x43e95150": t.hex()}


def muestra(tr: Telnet) -> dict | None:
    """Una muestra rápida: M del grupo 1 → cap físico → campos."""
    gs = decode_gestor(tr.read(E1 + RAM_OFF, 0x40))
    if not (gs["cola"] and 0x43000000 <= gs["cola_next"] < 0x44100000):
        return None
    m = u32(tr.read(gs["cola_next"] + RAM_OFF, 0x20), 8)
    cap = u32(tr.read(m + RAM_OFF, 4))
    if not (RAM[0] <= cap < RAM[1] - 0x6000 and cap % 2 == 0):
        return None
    vals = tr.read_many([(cap + o, n) for o, n in CAP_REGS])
    return {"t": time.time(), "cap": hex(cap), **{f"{o:#x}": v.hex() for (o, _), v in zip(CAP_REGS, vals, strict=True)}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm-readonly", action="store_true", required=True)
    ap.add_argument("--speed", default="4")
    a = ap.parse_args()
    cam, ctl, tr = Camera(HOST), Telnet(HOST), Telnet(HOST)
    res: dict = {"schema": "e25-19f-lectura/v1", "speed": a.speed, "muestras": []}
    stop = threading.Event()

    def run() -> None:
        while not stop.is_set():
            try:
                if (m := muestra(tr)) is not None:
                    res["muestras"].append(m)
            except Exception as exc:  # noqa: BLE001 - se conserva la evidencia
                res["error"] = str(exc)
                return

    try:
        assert verify_originals(ctl)["ok"], "originales T050 alterados"
        res["reposo"] = globales(ctl)
        res["status_reposo"] = cam.info()["raw"]
        assert "bursting=false" in res["status_reposo"], "cámara ocupada"
        n, d = speed_args(a.speed)
        cam.get(f"/ss?n={n}&d={d}")
        time.sleep(0.5)
        c0 = int(cam.info()["count"])
        th = threading.Thread(target=run, daemon=True)
        th.start()
        time.sleep(0.3)
        res["t_shoot"] = t0 = time.time()
        res["reply"] = cam.get("/shoot")
        while time.time() - t0 < 120:
            if not cam.status().startswith(("shooting", "queued")) and int(cam.info()["count"]) > c0:
                break
            time.sleep(0.15)
        time.sleep(1.0)
        stop.set()
        th.join(timeout=30)
        res["final"] = globales(ctl)
        res["originales_ok_final"] = verify_originals(ctl)["ok"]
    finally:
        tr.close()
        ctl.close()
    f = OUT / f"cap-completo-{a.speed}s-{time.strftime('%H%M%S')}.json"
    f.write_text(json.dumps(res, indent=1) + "\n")
    print(f, "muestras", len(res["muestras"]), "originales", res.get("originales_ok_final"), res.get("error"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
