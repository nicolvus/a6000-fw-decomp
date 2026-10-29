"""E25-26 — C3-B: exposición electrónica condicionada a la modalidad (offline).

Enganche verificado en E25-18: `0x438c82fe` (`bl 0x436d6118`, obtener el imager),
justo antes de `SetExposure` (`0x438c830c`).  La cueva:

* solo actúa en el paso 0 (el `cbnz cap+0x4b9c` de `0x438c82d8` ya lo garantiza);
* solo con `cap+0x41c == 1` (Electronic, copia por captura del selector);
* solo con `r7 = svd nativo <= 1` (rutas rápidas; no toca largas);
* normaliza el plan nativo: si `svd == 1` resta el VTS (`cap+0x5e0`) al `shd`
  (`cap+0x64c`), que es exactamente deshacer el cuadro extra del predicado;
* escribe `cap+0x650 = 0` y `cap+0x655 = 0` (ShutMode 0) para `SetExposure`;
* si el VTS es cero o el `shd` no supera al VTS, no toca nada (fallo seguro);
* conserva r0 (retorno de `0x436d6118`), r4, r6 y r7, y la alineación de pila.

No reejecuta `0x4383fa40`: consume su salida ya copiada a `cap+0x64c` por
`0x437f8a50 -> 0x4383fd6c`.  No escribe fuera de `cap+0x64c`, `+0x650`, `+0x655`.
No genera FDAT/DAT ni se instala.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from e25_24.patch_bionz import BASE, BionzImage, ImageError, _slice, sha256
from e25_24.thumb import bl

SIZE = 11_427_236
SHA256_ORIGINAL = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"

HOOK = 0x438C82FE
HOOK_OLD = bytes.fromhex("0df60bff")       # bl 0x436d6118
HOOK_TARGET = 0x436D6118
CAVE = 0x43541840
CAVE_LEN = 52

CAP_MODALITY = 0x41C
CAP_VTS = 0x5E0
CAP_SHD = 0x64C
CAP_SVD = 0x650
CAP_SHUTMODE = 0x655
CAP_STEP = 0x4B9C
CAP_IMAGER = 0x12F8

# Regiones que C3-B no debe tocar.
PROTECTED: tuple[tuple[str, int, int], ...] = (
    ("liro_header", 0x43541000, 0x4354141C),
    ("api_table_dest", 0x435410D8, 0x4354141C),
    ("header_metadata_tail", 0x435418D8, 0x435418E4),
    ("got_zero_object", 0x43541900, 0x43541B00),
    ("text_start", 0x43541B00, 0x43541B80),
    ("start_exposure_pre", 0x438C828C, 0x438C82FE),
    ("start_exposure_post", 0x438C8302, 0x438C8344),
)


def cave_bytes(cave: int = CAVE) -> bytes:
    """Cueva de 52 B; las ramas se codifican con la dirección real."""
    if cave % 2:
        raise ValueError("la cueva debe estar alineada a 2 B")
    out = bytearray()
    out += bytes.fromhex("02b5")            # push {r1, lr}      (alineación 8 B)
    out += bytes.fromhex("d4f81c14")        # ldr.w r1,[r4,#0x41c]
    out += bytes.fromhex("0129")            # cmp r1,#1
    out += bytes.fromhex("11d1")            # bne skip            -> 0x2e
    out += bytes.fromhex("012f")            # cmp r7,#1
    out += bytes.fromhex("0fd8")            # bhi skip            -> 0x2e
    out += bytes.fromhex("4fb1")            # cbz r7, write       -> 0x24
    out += bytes.fromhex("b4f8e025")        # ldrh.w r2,[r4,#0x5e0]
    out += bytes.fromhex("5ab1")            # cbz r2, skip        -> 0x2e
    out += bytes.fromhex("d4f84c36")        # ldr.w r3,[r4,#0x64c]
    out += bytes.fromhex("9342")            # cmp r3,r2
    out += bytes.fromhex("07d9")            # bls skip            -> 0x2e
    out += bytes.fromhex("9b1a")            # subs r3,r3,r2
    out += bytes.fromhex("c4f84c36")        # str.w r3,[r4,#0x64c]
    out += bytes.fromhex("0023")            # movs r3,#0          (write)
    out += bytes.fromhex("84f85536")        # strb.w r3,[r4,#0x655]
    out += bytes.fromhex("a4f85036")        # strh.w r3,[r4,#0x650]
    out += bl(cave + len(out), HOOK_TARGET)  # skip: bl 0x436d6118
    out += bytes.fromhex("02bd")            # pop {r1, pc}
    if len(out) != CAVE_LEN:
        raise AssertionError(f"cueva de {len(out)} B, esperado {CAVE_LEN}")
    return bytes(out)


def hook_bytes(cave: int = CAVE) -> bytes:
    return bl(HOOK, cave)


def _protected(data: bytes) -> dict[str, str]:
    return {name: sha256(_slice(data, a, b - a)) for name, a, b in PROTECTED}


def apply_bytes(data: bytes, *, cave: int = CAVE) -> tuple[bytes, list[dict[str, Any]]]:
    """Aplica C3-B sobre una imagen original o ya parcheada por el selector E25-24."""
    if len(data) != SIZE:
        raise ImageError("tamaño inesperado")
    out = bytearray(data)
    if _slice(data, HOOK, 4) not in (HOOK_OLD, hook_bytes(cave)):
        raise ImageError(f"hook inesperado en {HOOK:#x}: {_slice(data, HOOK, 4).hex()}")
    current = _slice(data, cave, CAVE_LEN)
    if current not in (bytes(CAVE_LEN), cave_bytes(cave)):
        raise ImageError(f"la cueva no está libre en {cave:#x}: {current.hex()}")
    diff: list[dict[str, Any]] = []
    for addr, old, new, role in (
        (HOOK, HOOK_OLD, hook_bytes(cave), "bl imager -> bl cueva C3-B"),
        (cave, bytes(CAVE_LEN), cave_bytes(cave), "cueva C3-B"),
    ):
        off = addr - BASE
        have = bytes(data[off:off + len(old)])
        if have == new:
            continue
        if have != old:
            raise ImageError(f"bytes inesperados en {addr:#x}: {have.hex()}")
        out[off:off + len(new)] = new
        for i, (b, a) in enumerate(zip(old, new)):
            if b != a:
                diff.append({"address": addr + i, "before": f"{b:02x}", "after": f"{a:02x}", "role": role})
    return bytes(out), diff


def allowed_addresses(*, cave: int = CAVE) -> set[int]:
    out: set[int] = set()
    for addr, old, new in ((HOOK, HOOK_OLD, hook_bytes(cave)), (cave, bytes(CAVE_LEN), cave_bytes(cave))):
        for i, (b, a) in enumerate(zip(old, new)):
            if b != a:
                out.add(addr + i)
    return out


def restore_bytes(data: bytes, *, cave: int = CAVE) -> bytes:
    out = bytearray(data)
    for addr, new in ((HOOK, hook_bytes(cave)), (cave, cave_bytes(cave))):
        off = addr - BASE
        if out[off:off + len(new)] != new:
            raise ImageError(f"C3-B no aplicado en {addr:#x}")
    out[HOOK - BASE:HOOK - BASE + 4] = HOOK_OLD
    out[cave - BASE:cave - BASE + CAVE_LEN] = bytes(CAVE_LEN)
    return bytes(out)


def manifest(image: BionzImage, output: bytes, diff: list[dict[str, Any]], *, cave: int = CAVE) -> dict[str, Any]:
    bad = [d for d in diff if d["address"] not in allowed_addresses(cave=cave)]
    if bad:
        raise ImageError(f"cambios fuera de los sitios autorizados: {bad[:3]}")
    before = _protected(image.data)
    after = _protected(output)
    changed = {k: (before[k], after[k]) for k in before if before[k] != after[k]}
    if changed:
        raise ImageError(f"región protegida alterada: {sorted(changed)}")
    return {
        "phase": "E25-26",
        "component": "BIONZ av-cam.bin",
        "source_sha256": image.sha256(),
        "patched_sha256": sha256(output),
        "status": "offline-candidate",
        "installable": False,
        "hook": {"address": hex(HOOK), "before": HOOK_OLD.hex(), "after": hook_bytes(cave).hex()},
        "cave": {"address": hex(cave), "bytes": cave_bytes(cave).hex(), "length": CAVE_LEN,
                 "region": "área reservada de la cabecera LIRO (0x141c-0x18d8); cero en A6000 y A7S, "
                           "sin punteros ni ramas, después del memcpy API 0x435410d8-0x4354141c"},
        "conditions": {
            "mode": "cap+0x41c == 1 (Electronic)",
            "step": "paso 0 (cbnz cap+0x4b9c en 0x438c82d8 ya lo garantiza)",
            "native_svd": "r7 <= 1 (solo ruta rápida)",
            "vts": "cap+0x5e0 != 0 y cap+0x64c > cap+0x5e0",
        },
        "writes": [hex(CAP_SHD), hex(CAP_SVD), hex(CAP_SHUTMODE)],
        "does_not_write": [hex(CAP_MODALITY), hex(CAP_STEP), hex(CAP_IMAGER), "record", "Darwin"],
        "semantics": {
            "EFCS": "cap+0x41c == 0 -> sin cambios; Sony conserva shd/svd/ShutMode",
            "Electronic": "svd' = 0; shd' = shd - VTS (si svd == 1); ShutMode = 0",
        },
        "diff": diff,
        "diff_count": len(diff),
        "protected": {name: before[name] for name, _, _ in PROTECTED},
    }


def _check_output(input_path: Path, output_path: Path) -> None:
    if input_path.resolve() == output_path.resolve():
        raise ImageError("la salida no puede ser la entrada")
    if output_path.suffix.lower() in (".fdat", ".dat"):
        raise ImageError("E25-26 no genera paquetes instalables")
    if output_path.suffix.lower() != ".bin":
        raise ImageError("la salida debe ser .bin")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--cave", type=lambda s: int(s, 0), default=CAVE)
    args = ap.parse_args()
    _check_output(args.input, args.output)
    image = BionzImage.load(args.input)
    patched, diff = apply_bytes(image.data, cave=args.cave)
    args.output.write_bytes(patched)
    text = json.dumps(manifest(image, patched, diff, cave=args.cave), indent=2, ensure_ascii=False)
    if args.manifest:
        args.manifest.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
