#!/usr/bin/env python3
"""E25-19b — campos de la compuerta `0x43afc544` de cada gestor, solo lectura (/dev/mem por Telnet).

Por gestor E: +0x24 bloqueado (Block/Unblock 0x437e52b0/0x437e54b4), +0x2c máximo en vuelo, +0x2d en vuelo,
+0x28 último, +0x2e habilitado, lista diferida E+4 y cola E+0x14 con sus nodos. Clasifica por qué se difiere
(`motivo`). Uso: --confirm-readonly [--speed 4 | --idle N]; dispara UNA foto normal y no escribe nada.
"""
from __future__ import annotations

import argparse
import json
import struct
import threading
import time

from e25_19_readonly import HOST, Telnet, verify_originals
from e25_19_test import Camera, speed_args
from e25_19b_cadena import BIN, OUTDIR, RAM_OFF, static_chain


def decode_gestor(blk: bytes) -> dict:
    """Campos de un gestor E (0x40 B desde E): lista diferida E+4, cola E+0x14, y los de la compuerta."""
    nd, pd, cd = struct.unpack_from("<III", blk, 4)
    nq, pq, cq = struct.unpack_from("<III", blk, 0x14)
    return {"diferidas": cd, "dif_next": nd, "dif_prev": pd, "cola": cq, "cola_next": nq, "cola_prev": pq,
            "bloqueado": blk[0x24], "ultimo": struct.unpack_from("<I", blk, 0x28)[0],
            "max_vuelo": blk[0x2C], "en_vuelo": blk[0x2D], "habilitado": blk[0x2E]}


def decode_nodo(node: bytes) -> dict:
    """Nodo de cola: next, prev y elemento (nodo+8): M, y bytes +8 (pendiente) y +9 del elemento."""
    return {"M": struct.unpack_from("<I", node, 8)[0], "pendiente": node[16], "b9": node[17]}


def motivo(g: dict, nodos: list[dict], b5490: int | None = None) -> str:
    """Resultado de 0x43afc544(E, b5490, flag=0, ·) en el orden de los bytes; `indeterminado` si falta cap."""
    if g["diferidas"]:
        return "difiere:lista_diferida"
    if g["bloqueado"]:
        return "difiere:bloqueado"
    if g["en_vuelo"] >= g["max_vuelo"]:
        return "difiere:limite_vuelo"
    cand = {n["b9"] for n in nodos if n["pendiente"] == 0} if g["habilitado"] else set()
    if cand and b5490 is None:
        return f"indeterminado:coincidencia(cap+0x5490 in {sorted(cand)})"
    if b5490 in cand:
        return "difiere:entrada_pendiente_coincide"
    if g["en_vuelo"] == 0:
        return "acepta:en_vuelo_0"
    return "indeterminado:acepta_solo_si_[E+0x28]==arg"


def snapshot(tr: Telnet, gestores: list[int]) -> dict:
    out = {}
    es = sorted(set(gestores) - {0})
    for e, blk in zip(es, tr.read_many([(e + RAM_OFF, 0x40) for e in es[:7]]) + tr.read_many(
            [(e + RAM_OFF, 0x40) for e in es[7:]]), strict=True):  # >8 regiones desborda la línea de telnet
        g = decode_gestor(blk)
        g["indice"] = gestores.index(e)
        nodos = []
        nxt = g["cola_next"]
        for _ in range(min(g["cola"], 4)):
            if not 0x43000000 <= nxt < 0x44100000 or nxt % 2:
                break
            raw = tr.read(nxt + RAM_OFF, 0x20)
            nodos.append(decode_nodo(raw))
            nxt = struct.unpack_from("<I", raw, 0)[0]
        g["nodos"] = [{k: f"{v:#x}" if k == "M" else v for k, v in n.items()} for n in nodos]
        g["motivo"] = motivo(g, nodos)
        out[f"{e:#x}"] = g
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm-readonly", action="store_true", required=True)
    ap.add_argument("--speed", default="4", help="velocidad del único disparo normal")
    ap.add_argument("--idle", type=int, default=0, help="solo N muestras en reposo, sin disparar")
    a = ap.parse_args()
    ch = static_chain(BIN.read_bytes())
    cam, ctl, tr = Camera(HOST), Telnet(HOST), Telnet(HOST)
    res: dict = {"schema": "e25-19b-compuerta/v2", "speed": a.speed, "muestras": []}
    stop = threading.Event()

    def run() -> None:
        while not stop.is_set():
            try:
                res["muestras"].append({"t": time.time(), "g": snapshot(tr, ch["gestores"])})
            except Exception as exc:  # noqa: BLE001 - se conserva la evidencia
                res["muestras"].append({"t": time.time(), "error": str(exc)})
                return

    try:
        assert verify_originals(ctl)["ok"], "originales T050 alterados"
        if a.idle:
            for _ in range(a.idle):
                res["muestras"].append({"t": time.time(), "g": snapshot(tr, ch["gestores"])})
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
                if not cam.status().startswith(("shooting", "queued")) and int(cam.info()["count"]) > c0:
                    break
                time.sleep(0.15)
            time.sleep(1.5)
            stop.set()
            th.join(timeout=30)
        res["originales_ok_final"] = verify_originals(ctl)["ok"]
    finally:
        tr.close()
        ctl.close()
    out = OUTDIR.parent / "e25-19b" / f"compuerta-{'reposo' if a.idle else a.speed + 's'}.json"
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(out, "muestras", len(res["muestras"]), "originales", res.get("originales_ok_final"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
