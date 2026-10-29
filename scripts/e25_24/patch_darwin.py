"""E25-24 — parche offline de Darwin: compuerta condicionada por captura.

Sustituye B1a (bloqueo global del motor) y el parche tipo 0 (bloqueo global de
bobinas) por una compuerta que solo se cierra cuando el mensaje `0x0c` de esa
captura trae `pkt[0x0e] != 0` (modo Electronic).  Con 0 se ejecuta la ruta
original de Sony (EFCS: segunda cortina mecánica).

Sitios (bytes originales verificados):

    0x20c78  fa f7 02 fa  bl 0x1b080  -> bl cave   (tipo de bobina, 0x20c74)
    0x1fe6c  fb f7 08 f9  bl 0x1b080  -> bl cave   (compuerta del motor, 0x1fe66)
    0x4318   16 B a cero (tabla de vectores) -> cave de 14 B
    0x4330   4 B a cero (tabla de vectores)  -> literal 0x20003716

El cave lee `S+0x3e` (copia de `pkt[0x0e]` que hace `0x17f8c`).  No toca
`0x20c74`, `0x1fe66`, `InitCom`, `Upd`, reset, watchdog ni GPIO.  No genera
FDAT/DAT y no se instala.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .thumb import b_w, bl

BASE = 0x4200
SIZE = 157_276
SHA256 = "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
SHA_TIPO0 = "ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc"
SHA_B1A = "55a366a5fc95f01ccb044ae352db90f0122ee779cab69063b6b99da8b3dcea1d"

COIL_BL = 0x20C78
COIL_OLD = bytes.fromhex("faf702fa")
MOTOR_BL = 0x1FE6C
MOTOR_OLD = bytes.fromhex("fbf708f9")
CAVE = 0x4318
CAVE_LEN = 14
CAVE_OLD = bytes(CAVE_LEN)            # 0x4318..0x4325, vector 70 no usado
LITERAL = 0x4330
LITERAL_OLD = bytes(4)                # vector 76 no usado
FLAG_ADDR = 0x20003716                # S+0x3e, S = 0x200036d8


class ImageError(ValueError):
    """Imagen desconocida, corrupta o no reversible."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(data: bytes, addr: int, size: int) -> bytes:
    off = addr - BASE
    if off < 0 or off + size > len(data):
        raise ImageError(f"dirección fuera de darwin_core.bin: {addr:#x}+{size:#x}")
    return data[off:off + size]


def cave_bytes() -> bytes:
    out = bytearray()
    out += bytes.fromhex("054a")          # ldr r2,[pc,#0x14] -> 0x4330
    out += bytes.fromhex("1278")          # ldrb r2,[r2]
    out += bytes.fromhex("0ab1")          # cbz r2, 0x4322
    out += bytes.fromhex("0020")          # movs r0,#0
    out += bytes.fromhex("7047")          # bx lr
    out += b_w(CAVE + len(out), 0x1B080)  # EFCS: ruta original
    if len(out) != CAVE_LEN:
        raise AssertionError(f"cave de {len(out)} B, esperado {CAVE_LEN}")
    return bytes(out)


PATCHES: tuple[tuple[int, bytes, bytes, str], ...] = (
    (COIL_BL, COIL_OLD, bl(COIL_BL, CAVE), "tipo de bobina -> cave"),
    (MOTOR_BL, MOTOR_OLD, bl(MOTOR_BL, CAVE), "compuerta del motor -> cave"),
    (CAVE, CAVE_OLD, cave_bytes(), "cave: flag 0 -> original; flag != 0 -> 0"),
    (LITERAL, LITERAL_OLD, FLAG_ADDR.to_bytes(4, "little"), "literal S+0x3e"),
)

# Regiones que este parche no debe tocar (E24-02/E24-04/E24-05).
PROTECTED: tuple[tuple[str, int, int], ...] = (
    ("reset", 0x45C8, 0x4638),
    ("scatter_load", 0x43FC, 0x4404),
    ("bootloader_mailbox", 0x45BC, 0x45C8),
    ("upd_main", 0x8DA8, 0x8E00),
    ("initcom", 0x4BCA, 0x5000),
    ("com_task", 0xECE4, 0xED40),
    ("watchdog", 0xA4AC, 0xA540),
    ("power_table", 0x28C6C, 0x28D00),
    ("gpio_writer", 0x51C0, 0x51CC),
)


@dataclass(frozen=True)
class DarwinImage:
    path: Path
    data: bytes

    @classmethod
    def load(cls, path: str | Path) -> DarwinImage:
        p = Path(path)
        if not p.is_file():
            raise ImageError(f"no existe: {p}")
        data = p.read_bytes()
        if len(data) != SIZE:
            raise ImageError(f"tamaño inesperado: {len(data)} (esperado {SIZE})")
        digest = sha256(data)
        if digest in (SHA_TIPO0, SHA_B1A):
            raise ImageError("la entrada ya lleva tipo 0/B1a; este parche parte del original")
        if digest != SHA256:
            try:
                restored = restore_bytes(data)
            except ImageError as exc:
                raise ImageError(f"SHA-256 desconocido: {digest}") from exc
            if sha256(restored) != SHA256:
                raise ImageError(f"SHA-256 desconocido: {digest}")
        return cls(p, data)

    def sha256(self) -> str:
        return sha256(self.data)


def _protected(data: bytes) -> dict[str, str]:
    return {name: sha256(_slice(data, a, b - a)) for name, a, b in PROTECTED}


def apply_bytes(data: bytes) -> tuple[bytes, list[dict[str, Any]]]:
    if len(data) != SIZE:
        raise ImageError("tamaño inesperado")
    out = bytearray(data)
    diff: list[dict[str, Any]] = []
    for addr, old, new, role in PATCHES:
        if len(old) != len(new):
            raise AssertionError(f"parche de tamaño distinto en {addr:#x}")
        have = _slice(data, addr, len(old))
        if have not in (old, new):
            raise ImageError(f"bytes inesperados en {addr:#x}: {have.hex()} (esperado {old.hex()})")
        if have == new:
            continue
        off = addr - BASE
        out[off:off + len(new)] = new
        for i, (b, a) in enumerate(zip(old, new)):
            if b != a:
                diff.append({
                    "address": addr + i,
                    "before": f"{b:02x}",
                    "after": f"{a:02x}",
                    "role": role,
                })
    return bytes(out), diff


def allowed_addresses() -> set[int]:
    out: set[int] = set()
    for addr, old, new, _ in PATCHES:
        for i, (b, a) in enumerate(zip(old, new)):
            if b != a:
                out.add(addr + i)
    return out


def restore_bytes(data: bytes) -> bytes:
    out = bytearray(data)
    for addr, old, new, _ in PATCHES:
        off = addr - BASE
        if out[off:off + len(new)] != new:
            raise ImageError(f"el parche no está aplicado en {addr:#x}")
        out[off:off + len(old)] = old
    return bytes(out)


def build_manifest(image: DarwinImage, output: bytes, diff: list[dict[str, Any]]) -> dict[str, Any]:
    bad = [d for d in diff if d["address"] not in allowed_addresses()]
    if bad:
        raise ImageError(f"cambios fuera de los sitios autorizados: {bad[:3]}")
    before = _protected(image.data)
    after = _protected(output)
    changed = {k: (before[k], after[k]) for k in before if before[k] != after[k]}
    if changed:
        raise ImageError(f"región protegida alterada: {sorted(changed)}")
    return {
        "phase": "E25-24",
        "component": "Darwin darwin_core.bin",
        "source": str(image.path),
        "source_sha256": image.sha256(),
        "patched_sha256": sha256(output),
        "status": "offline-candidate",
        "installable": False,
        "supersedes": ["B1a (bloqueo global del motor)", "tipo 0 (bloqueo global de bobinas)"],
        "sites": [
            {"address": hex(a), "before": o.hex(), "after": n.hex(), "role": r}
            for a, o, n, r in PATCHES
        ],
        "diff": diff,
        "diff_count": len(diff),
        "cave": {
            "address": hex(CAVE),
            "bytes": cave_bytes().hex(),
            "length": CAVE_LEN,
            "flag_address": hex(FLAG_ADDR),
            "note": "0x4318..0x4327 y 0x4330..0x4333 eran cero (vectores 70 y 76, sin "
                    "referencias BL/literal); el resto de la tabla de vectores no se toca",
        },
        "protected": {name: before[name] for name, _, _ in PROTECTED},
        "semantics": {
            "pkt[0x0e] == 0": "EFCS: 0x20c74 y 0x1fe66 ejecutan 0x1b080 original",
            "pkt[0x0e] != 0": "Electronic: ambas compuertas devuelven 0 (sin bobinas ni motor)",
        },
        "reversal": "restaurar los bytes `before`; 0x20c74/0x1fe66/InitCom/Upd/watchdog "
                    "no se modifican y vuelven a su comportamiento original al restaurar",
    }


def _check_output(input_path: Path, output_path: Path) -> None:
    if input_path.resolve() == output_path.resolve():
        raise ImageError("la salida no puede ser la entrada")
    if output_path.suffix.lower() in (".fdat", ".dat"):
        raise ImageError("E25-24 no genera paquetes instalables")
    if output_path.suffix.lower() != ".bin":
        raise ImageError("la salida debe ser .bin")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--restore", action="store_true", help="revierte un parche ya aplicado")
    args = ap.parse_args()
    _check_output(args.input, args.output)
    image = DarwinImage.load(args.input)
    if args.restore:
        restored = restore_bytes(image.data)
        payload = {
            "phase": "E25-24",
            "component": "Darwin darwin_core.bin",
            "action": "restore",
            "source_sha256": image.sha256(),
            "restored_sha256": sha256(restored),
            "original_sha256": SHA256,
            "verified": sha256(restored) == SHA256,
        }
        args.output.write_bytes(restored)
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        if args.manifest:
            args.manifest.write_text(text + "\n")
        print(text)
        return
    patched, diff = apply_bytes(image.data)
    args.output.write_bytes(patched)
    manifest = build_manifest(image, patched, diff)
    text = json.dumps(manifest, indent=2, ensure_ascii=False)
    if args.manifest:
        args.manifest.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
