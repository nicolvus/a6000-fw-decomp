#!/usr/bin/env python3
"""E25-19b — muestrea las colas de los gestores durante un disparo normal y sigue nodo→M→cap (solo lectura).

Cadena (E25-19 §4b): centinela E+0x14 → nodo → [nodo+8] = M → [M] = cap. Con M en vuelo lee M (0x40 B) y,
si [M] es un puntero de RAM, los campos de `cap` de E25-19. Sin escrituras; un disparo, sin ráfagas ni BULB.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e25_19_readonly import (
    CAP_FIELDS,
    HOST,
    RAM_VIRT_OFF,
    ReadError,
    Telnet,
    now,
    verify_originals,
)
from e25_19_test import Camera, speed_args

GESTORES = [0x43ed8814, 0x43ed8844, 0x43ed8874, 0x43ed88a4, 0x43ed88d4, 0x43ed8904, 0x43ed8934, 0x43ed8e20,
            0x43edbd3c, 0x43edbd6c, 0x43edbd9c, 0x43edbdcc, 0x43edbdfc, 0x43edbe2c]
RAM = range(0x43000000, 0x44100000)


def v2p(v: int) -> int:
    return v + RAM_VIRT_OFF


def sample(tr: Telnet) -> dict:
    """Una pasada: centinelas y, para las colas no vacías, nodo, M y cap."""
    s: dict = {"t": time.time(), "colas": {}}
    regs = [(v2p(e + 0x14), 8) for e in GESTORES]
    heads = tr.read_many(regs[:7]) + tr.read_many(regs[7:])  # >8 regiones desborda la línea de comandos del telnet
    for e, h in zip(GESTORES, heads, strict=True):
        nxt, prv = struct.unpack("<II", h)
        if nxt == e + 0x14 and prv == e + 0x14:
            continue
        item: dict = {"next": f"{nxt:#x}", "prev": f"{prv:#x}"}
        s["colas"][f"{e:#x}"] = item
        if nxt in RAM and nxt % 4 == 0:
            try:
                node = tr.read(v2p(nxt), 0x20)
                m = struct.unpack_from("<I", node, 8)[0]
                item["nodo"] = node.hex()
                if m in RAM and m % 4 == 0:
                    mem = tr.read(v2p(m), 0x40)
                    cap = struct.unpack_from("<I", mem, 0)[0]
                    item["M"] = {"addr": f"{m:#x}", "hex": mem.hex(), "id": mem[0x1c], "sub": mem[0x23]}
                    if cap in RAM and cap % 4 == 0:
                        vals = tr.read_many([(v2p(cap + o), struct.calcsize(f)) for o, f, _ in CAP_FIELDS])
                        item["cap"] = {"addr": f"{cap:#x}", **{lab: struct.unpack(f, v)[0]
                                                               for (o, f, lab), v in zip(CAP_FIELDS, vals, strict=True)}}
            except ReadError as exc:
                item["error"] = str(exc)
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--speed", default="4")
    ap.add_argument("--confirm-readonly", action="store_true", required=True)
    a = ap.parse_args()
    cam, tr_ctl, tr = Camera(HOST), Telnet(HOST), Telnet(HOST)
    assert verify_originals(tr_ctl)["ok"], "originales alterados"
    assert cam.status().startswith("ready") or "bursting=false" in cam.info()["raw"], "cámara ocupada"
    n, d = speed_args(a.speed)
    cam.get(f"/ss?n={n}&d={d}")
    time.sleep(0.5)
    c0 = int(cam.info()["count"])
    out: list = []
    stop = threading.Event()

    def run() -> None:
        while not stop.is_set():
            try:
                out.append(sample(tr))
            except Exception as exc:  # noqa: BLE001 - se conserva la evidencia
                out.append({"t": time.time(), "error": str(exc)})
                return

    th = threading.Thread(target=run, daemon=True)
    th.start()
    time.sleep(0.5)
    t0 = time.time()
    reply = cam.get("/shoot")
    while time.time() - t0 < 120:
        st = cam.status()
        if not st.startswith(("shooting", "queued")) and int(cam.info()["count"]) > c0:
            break
        time.sleep(0.15)
    time.sleep(1.5)
    stop.set()
    th.join(timeout=30)
    ok = verify_originals(tr_ctl)["ok"]
    res = {"schema": "e25-19b-muestreo/v1", "speed": a.speed, "inicio": now(), "t_shoot": t0, "reply": reply,
           "originales_ok_final": ok, "muestras": out}
    path = Path(__file__).resolve().parents[1] / "analysis/e25-19b" / f"muestreo-{a.speed.replace('/', '_')}s.json"
    path.write_text(json.dumps(res, indent=1) + "\n")
    con = [x for x in out if x.get("colas")]
    print(path, "muestras", len(out), "con cola no vacía", len(con), "originales", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
