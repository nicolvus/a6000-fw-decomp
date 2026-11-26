#!/usr/bin/env python3
"""Eye AF nativo para `av-cam.bin` (BIONZ) — parche del CFW, sin APK.

Qué cambia
==========
En `0x437b7200` (módulo `[CAMERA_MAIN_FC]`) el firmware elige de dónde sale el área de AF según
el **modo de área** (`r6`, tercer argumento):

* `r6 == 2` → ojo 2 si `ctx+0xdf` es válido, si no ojo 1 (`ctx+0xde`), si no ceros;
* `r6 == 1` → ojo 1 si es válido;
* cualquier otro (0 = Wide) → marco basado en la cara, **sin ojos**.

El parche anula la comparación `cmp r6, #2 / bne` (`0x437b723a`/`0x437b723c`): al no ramificar,
**todos** los modos de área entran por la vía del ojo 2 → ojo 1 → ceros. Es la prioridad de ojo que
tienen las a6xxx de fábrica, sin tocar el detector ni el resto del flujo.

Evidencia: `docs/capture/eye-af-nativo-a6000.md` §2 y `analysis/eyeaf/avcam_eye_native.md`
(desensamblado de `0x437b7200` y `0x437b723a`–`0x437b7260`).

Integración: `scripts/e25_27/build.py::apply_patches` lo aplica tras el selector y C3-B, así que el
`nflasha3` del CFW ya sale con Eye AF (no hay APK ni paso manual). Reversión = los mismos 2 bytes
(`restore_bytes`). Este script no escribe cámara, ni RAM, ni NVRAM.

Uso suelto (depuración sobre una copia de la imagen):
    python3 scripts/cfw/eye_af_patch.py --apply  OUT/av-cam.bin
    python3 scripts/cfw/eye_af_patch.py --check  OUT/av-cam.bin      # 0 = aplicado, 3 = no
    python3 scripts/cfw/eye_af_patch.py --revert OUT/av-cam.bin
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

BASE = 0x43541000  # av-cam.bin se carga aquí (convención del proyecto)

# `cmp r6, #2` + `bne 0x437b72b0`: si no se ramifica, el bloque del modo 2 (ojos) se ejecuta siempre.
SITE = 0x437B723C
PATCH = {SITE: (bytes.fromhex("38d1"), bytes.fromhex("00bf"))}  # bne -> nop

SHA_INPUT = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"  # 3.21 oficial
TAMANO_INPUT = 11_427_236
ROL = "Eye AF: cualquier modo de área usa ojo2→ojo1 (prioridad de ojo de las a6xxx)"


def allowed_addresses() -> set[int]:
    return {SITE, SITE + 1}


def _off(vaddr: int) -> int:
    return vaddr - BASE


def _diff(antes: bytes, despues: bytes) -> list[dict[str, Any]]:
    return [{"address": BASE + i, "before": f"{a:02x}", "after": f"{b:02x}", "role": ROL}
            for i, (a, b) in enumerate(zip(antes, despues)) if a != b]


def apply_bytes(data: bytes) -> tuple[bytes, list[dict[str, Any]]]:
    """Devuelve (imagen con Eye AF, diff por byte). Idempotente; exige los bytes originales."""
    out = bytearray(data)
    for va, (orig, nuevo) in PATCH.items():
        actual = bytes(data[_off(va):_off(va) + len(orig)])
        if actual == nuevo:
            continue
        if actual != orig:
            raise ValueError(f"{va:#x}: bytes {actual.hex()} (esperado {orig.hex()})")
        out[_off(va):_off(va) + len(nuevo)] = nuevo
    nuevo_img = bytes(out)
    if len(nuevo_img) != len(data):
        raise ValueError("el parche cambia el tamaño de av-cam.bin")
    return nuevo_img, _diff(data, nuevo_img)


def restore_bytes(data: bytes) -> bytes:
    """Vuelve a los bytes originales (para verificar que la reversión es exacta)."""
    out = bytearray(data)
    for va, (orig, nuevo) in PATCH.items():
        if bytes(data[_off(va):_off(va) + len(nuevo)]) == nuevo:
            out[_off(va):_off(va) + len(orig)] = orig
    return bytes(out)


def estado(data: bytes) -> str:
    orig, nuevo = PATCH[SITE]
    actual = data[_off(SITE):_off(SITE) + len(orig)]
    return "aplicado" if actual == nuevo else "sin aplicar" if actual == orig else "desconocido"


def describir(data: bytes) -> str:
    return f"{SITE:#010x}: {data[_off(SITE) - 2:_off(SITE) + 4].hex()}  ({estado(data)})"


def leer(ruta: Path) -> bytes:
    data = ruta.read_bytes()
    if len(data) != TAMANO_INPUT:
        raise SystemExit(f"{ruta}: tamaño {len(data)} != {TAMANO_INPUT} (no es la av-cam de 3.21)")
    return data


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Eye AF nativo en av-cam.bin (CFW, sin APK)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--apply", metavar="AVCAM", type=Path)
    g.add_argument("--revert", metavar="AVCAM", type=Path)
    g.add_argument("--check", metavar="AVCAM", type=Path)
    a = p.parse_args(argv)

    ruta = a.apply or a.revert or a.check
    data = leer(ruta)
    print(f"entrada: {ruta}  sha256={hashlib.sha256(data).hexdigest()[:16]}…  {describir(data)}")

    if a.check:
        return 0 if estado(data) == "aplicado" else 3

    if a.apply:
        nuevo, diff = apply_bytes(data)
    else:
        nuevo, diff = restore_bytes(data), []
    if nuevo == data:
        print("sin cambios (ya estaba así)")
        return 0
    if a.apply and {d["address"] for d in diff} != allowed_addresses():
        raise SystemExit(f"el parche tocó bytes inesperados: {sorted(d['address'] for d in diff)}")

    ruta.write_bytes(nuevo)
    print(f"escrito {ruta}  sha256={hashlib.sha256(nuevo).hexdigest()}  {describir(nuevo)}")
    print("el paquete lo recompone el constructor del CFW; este script no instala nada")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
