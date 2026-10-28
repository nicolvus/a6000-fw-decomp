#!/usr/bin/env python3
"""E25-19b (tramo final) — cadena en vivo `entrada en vuelo del grupo 1 -> M -> [M] -> cap` y campos de `cap`, solo lectura.

Cadena (estática, ver §4i): la cola E+0x14 del gestor del grupo 1 guarda M; Run(M)=0x43b047d0 invoca el functor con r1=M;
los manejadores toman cap=[M] (0x43ae75dc). [M] lo fija 0x4381ba9c(plantilla, copia_de_cap) con la copia de 0x4378764c.
[M] es una dirección FÍSICA en System RAM (0x95xxxxxx), no virtual: se lee con /dev/mem sin RAM_OFF.
Uso: --confirm-readonly [--speed 4 | --idle N]; dispara UNA foto normal y no escribe nada.
"""

from __future__ import annotations

import argparse
import json
import struct
import threading
import time

from e25_19_readonly import HOST, Telnet, verify_originals
from e25_19_test import Camera, speed_args
from e25_19b_cadena import OUTDIR, RAM_OFF
from e25_19b_compuerta import decode_gestor

E1, E9 = 0x43EDBD9C, 0x43EDBE2C
RAM = (0x80000000, 0xC0000000)
# (nombre, desplazamiento en cap, bytes); 2 lotes de <= 8 regiones por límite de línea de telnet
LOTE_A = [
    ("n1d8_1e0", 0x1D8, 0x10),
    ("sel504", 0x504, 4),
    ("tim56c_570", 0x56C, 8),
    ("shd_svd_modo", 0x64C, 0x10),
    ("setread6bc", 0x6BC, 4),
    ("tmr728", 0x728, 0x10),
    ("b738", 0x738, 8),
    ("sec740", 0x740, 0x10),
]
LOTE_B = [
    ("b74c", 0x74C, 4),
    ("est4b64", 0x4B60, 0x10),
    ("c4b80", 0x4B80, 8),
    ("g5488", 0x5488, 0x10),
    ("fl4ad0", 0x4AD0, 0x10),
    ("c4ad8", 0x4AD8, 8),
]


def u32(b: bytes, o: int = 0) -> int:
    return struct.unpack_from("<I", b, o)[0]


def muestra(tr: Telnet) -> dict:
    """Una muestra: gestores 1 y 9, M de la primera entrada en cola de cada uno, [M] y campos de cap."""
    out: dict = {"t": time.time()}
    for nom, e in (("g1", E1), ("g9", E9)):
        g = decode_gestor(tr.read(e + RAM_OFF, 0x40))
        out[nom] = {k: g[k] for k in ("cola", "en_vuelo", "max_vuelo", "bloqueado")}
        if g["cola"] and 0x43000000 <= g["cola_next"] < 0x44100000:
            nodo = tr.read(g["cola_next"] + RAM_OFF, 0x20)
            m = u32(nodo, 8)
            mb = tr.read(m + RAM_OFF, 0x30)
            out[nom]["M"] = {
                "addr": hex(m),
                "cap_ptr": hex(u32(mb)),
                "ejecutor": hex(u32(mb, 4)),
                "manejador": hex(u32(mb, 0x10)),
                "id": u32(mb, 0x1C),
                "sub": mb[0x23],
                "pendiente": nodo[16],
            }
            cap = u32(mb)
            if RAM[0] <= cap < RAM[1] - 0x6000 and cap % 2 == 0 and "cap" not in out:
                regs = {}
                for lote in (LOTE_A, LOTE_B):
                    vals = tr.read_many([(cap + off, n) for _, off, n in lote])
                    regs.update(
                        {
                            f"{nom_}@{off:#x}": v.hex()
                            for (nom_, off, _), v in zip(lote, vals, strict=True)
                        }
                    )
                out["cap"] = {"phys": hex(cap), "origen": nom, "campos": regs}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm-readonly", action="store_true", required=True)
    ap.add_argument("--speed", default="4")
    ap.add_argument("--idle", type=int, default=0)
    a = ap.parse_args()
    cam, ctl, tr = Camera(HOST), Telnet(HOST), Telnet(HOST)
    res: dict = {"schema": "e25-19b-cap/v1", "speed": a.speed, "muestras": []}
    stop = threading.Event()

    def run() -> None:
        while not stop.is_set():
            try:
                res["muestras"].append(muestra(tr))
            except Exception as exc:  # noqa: BLE001 - se conserva la evidencia
                res["muestras"].append({"t": time.time(), "error": str(exc)})
                return

    try:
        assert verify_originals(ctl)["ok"], "originales T050 alterados"
        if a.idle:
            for _ in range(a.idle):
                res["muestras"].append(muestra(tr))
        else:
            assert "bursting=false" in cam.info()["raw"], "cámara ocupada"
            n, d = speed_args(a.speed)
            cam.get(f"/ss?n={n}&d={d}")
            time.sleep(0.5)
            c0 = int(cam.info()["count"])
            th = threading.Thread(target=run, daemon=True)
            th.start()
            time.sleep(0.5)
            res["t_shoot"] = t0 = time.time()
            res["reply"] = cam.get("/shoot")
            while time.time() - t0 < 120:
                if (
                    not cam.status().startswith(("shooting", "queued"))
                    and int(cam.info()["count"]) > c0
                ):
                    break
                time.sleep(0.15)
            time.sleep(1.5)
            stop.set()
            th.join(timeout=30)
        res["originales_ok_final"] = verify_originals(ctl)["ok"]
    finally:
        tr.close()
        ctl.close()
    out = (
        OUTDIR.parent / "e25-19b" / f"cap-{'reposo' if a.idle else a.speed + 's'}.json"
    )
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(
        out,
        "muestras",
        len(res["muestras"]),
        "originales",
        res.get("originales_ok_final"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
