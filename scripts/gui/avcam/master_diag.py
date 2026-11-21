#!/usr/bin/env python3
"""DIAGNÓSTICO (G75 T65, E2E-15; NO va al arnés ni a la cámara): réplica fuera de línea de un `avcam.jsonl` con el «Master» de `[CLK_CTRL]` inyectado.

uso: master_diag.py avcam.jsonl FRAMES T_MASTER_MS T_FIN_MS
Entrega a la cola `0xc001bd` el mensaje `0x80c001bd {targetVfc, 1, 0}` con `targetVfc = [0x43e991cc] + FRAMES` (módulo 2^24) y `[0x43e4a5a4]`=2 (rol que exige `0x435a0596`).
Verificado en bytes: `0x4378e114…0x4378e124` hace X = (targetVfc − VFC) & 0xffffff, X cuenta tramas (`0x4378e1e0`) y a 0 abre la puerta de `0x43796954`.
Los valores (rol, FRAMES) los fabrica esta herramienta: el emisor real del Master no está en ningún binario de la cámara (G75 T13/T65)."""
import collections
import json
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import liro_vm as L  # noqa: E402
import puente  # noqa: E402

frames, t_master, t_fin = int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
vm, _ = puente.arranca(None)
rd = lambda a, n=4: int.from_bytes(bytes(vm.uc.mem_read(a, n)), "little")  # noqa: E731


def entrega(q: int, cab: bytes, datos: bytes) -> None:
    m = vm.malloc(max(len(datos), 0x40) + 12 + 0x20) + 12
    vm.uc.mem_write(m - 12, cab)
    vm.uc.mem_write(m, datos)
    vm.msz[m] = len(datos)
    L.entrega(vm, q, m)


def master() -> None:
    vm.wr(0x43E4A5A4, 2, 1)
    entrega(0xC001BD, struct.pack("<3I", 0, 1, 0x80C001BD), struct.pack("<3I", (rd(0x43E991CC) + frames) & 0xFFFFFF, 1, 0))


hecho = False
for r in (json.loads(x) for x in open(sys.argv[1])):
    if "entra" not in r:
        continue
    if r["t"] > t_fin:
        break
    if not hecho and r["t"] >= t_master:
        vm.limite = t_master
        L.planifica(vm, 20_000_000)
        master()
        hecho = True
    vm.limite = r["t"]
    L.planifica(vm, 20_000_000)
    entrega(int(r["entra"], 16), bytes.fromhex(r["cab"]), bytes.fromhex(r["datos"]))
if not hecho:
    vm.limite = t_master
    L.planifica(vm, 20_000_000)
    master()
w0 = time.time()
while vm.t < t_fin - 1 and time.time() - w0 < 400:
    vm.limite = min(vm.t + 500, t_fin)
    L.planifica(vm, 80_000_000)
print("t", round(vm.t), "[0x43ede338]", hex(rd(0x43EDE338)), "mod0", hex(rd(0x43E9BD58, 2)), "X", hex(rd(0x43E991D0)), "VFC", rd(0x43E991CC), "[0x43e9bab8]", hex(rd(0x43E9BAB8)))
c = collections.Counter(hex(int.from_bytes(bytes.fromhex(x[4][4:8]), "little")) for x in vm.salida_ext if x[0] > t_master and x[3] == 0x20002)
print("respuestas a ObjCamera tras el Master:", sorted(c.items()))
