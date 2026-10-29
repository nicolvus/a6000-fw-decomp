"""E25-24 — parche offline de BIONZ (`av-cam.bin`) para publicar la modalidad.

El parche no implementa la exposición electrónica: solo copia el campo EFCS
(`cap+0x41c`, escrito desde `bloque+0x210`) al byte libre `pkt[0x0e]` del mensaje
`0x0c`, en las dos ramas del constructor (`[sp+0x44]` = 1 y ≠ 1).  Darwin usa ese
byte para suprimir o conservar su ruta mecánica.

Sitios (bytes originales verificados):

    0x4384133e  40 f0 1a 81  bne.w 0x43841576   -> 2 NOP (cae al cave)
    0x43841342  00 23 23 70  movs r3,#0; strb r3,[r4] -> bl cave
    0x43841476  a3 73        strb r3,[r4,#0xe]  -> NOP (el cave ya escribió)
    0x43541a80  relleno de ceros entre cabecera y código -> cave de 20 B

No genera FDAT/DAT, no instala nada y no toca la cámara.  El binario parcheado no
se versiona; solo el manifiesto con hashes y bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .thumb import NOP, b_w, bl

BASE = 0x43541000
SIZE = 11_427_236
SHA256 = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"

BRANCH = 0x4384133E
BRANCH_OLD = bytes.fromhex("40f01a81")
CALL = 0x43841342
CALL_OLD = bytes.fromhex("00232370")
STORE = 0x43841476
STORE_OLD = bytes.fromhex("a373")
CAVE = 0x43541A80
CAVE_LEN = 20
CAVE_OLD = bytes(CAVE_LEN)          # relleno de ceros verificado


class ImageError(ValueError):
    """Imagen desconocida, corrupta o no reversible."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(data: bytes, addr: int, size: int) -> bytes:
    off = addr - BASE
    if off < 0 or off + size > len(data):
        raise ImageError(f"dirección fuera de av-cam.bin: {addr:#x}+{size:#x}")
    return data[off:off + size]


def cave_bytes() -> bytes:
    """Cave: replica pkt[0]=0, escribe pkt[0x0e]=cap+0x41c y elige la rama."""
    out = bytearray()
    out += bytes.fromhex("0023")            # movs r3,#0
    out += bytes.fromhex("2370")            # strb r3,[r4]
    out += bytes.fromhex("d9f81c24")        # ldr.w r2,[sb,#0x41c]
    out += bytes.fromhex("a273")            # strb r2,[r4,#0xe]
    out += bytes.fromhex("0129")            # cmp r1,#1
    out += bytes.fromhex("01d0")            # beq +2 -> bx lr
    bw_addr = CAVE + len(out)
    out += b_w(bw_addr, 0x43841576)         # rama [sp+0x44] != 1
    out += bytes.fromhex("7047")            # bx lr
    if len(out) != CAVE_LEN:
        raise AssertionError(f"cave de {len(out)} B, esperado {CAVE_LEN}")
    return bytes(out)


PATCHES: tuple[tuple[int, bytes, bytes, str], ...] = (
    (BRANCH, BRANCH_OLD, NOP + NOP, "bne.w -> NOP; el cave decide la rama"),
    (CALL, CALL_OLD, bl(CALL, CAVE), "movs/strb -> bl cave"),
    (STORE, STORE_OLD, NOP, "store duplicado -> NOP"),
    (CAVE, CAVE_OLD, cave_bytes(), "cave: pkt[0x0e] = cap+0x41c"),
)


@dataclass(frozen=True)
class BionzImage:
    path: Path
    data: bytes

    @classmethod
    def load(cls, path: str | Path) -> BionzImage:
        p = Path(path)
        if not p.is_file():
            raise ImageError(f"no existe: {p}")
        data = p.read_bytes()
        if len(data) != SIZE:
            raise ImageError(f"tamaño inesperado: {len(data)} (esperado {SIZE})")
        digest = sha256(data)
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


def apply_bytes(data: bytes) -> tuple[bytes, list[dict[str, Any]]]:
    """Aplica el parche sobre una copia y devuelve (imagen, diff)."""
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


def build_manifest(image: BionzImage, output: bytes, diff: list[dict[str, Any]]) -> dict[str, Any]:
    bad = [d for d in diff if d["address"] not in allowed_addresses()]
    if bad:
        raise ImageError(f"cambios fuera de los sitios autorizados: {bad[:3]}")
    return {
        "phase": "E25-24",
        "component": "BIONZ av-cam.bin",
        "source": str(image.path),
        "source_sha256": image.sha256(),
        "patched_sha256": sha256(output),
        "status": "offline-candidate",
        "installable": False,
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
            "original": CAVE_OLD.hex(),
            "note": "relleno de ceros entre la cabecera LIRO y el código (0x8e4-0xaff); "
                    "verificado sin referencias BL/literal; la instalación exige comprobar "
                    "que el cargador no consume ese relleno",
        },
        "semantics": {
            "EFCS_ON": "campo +0x210 = 0 -> pkt[0x0e] = 0 -> Darwin conserva la ruta original",
            "EFCS_OFF": "campo +0x210 = 1 -> pkt[0x0e] = 1 -> Darwin suprime bobinas y motor",
        },
        "reversal": "restaurar los bytes `before` de sites; no hay cambios fuera de diff",
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
    image = BionzImage.load(args.input)
    if args.restore:
        restored = restore_bytes(image.data)
        payload = {
            "phase": "E25-24",
            "component": "BIONZ av-cam.bin",
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
