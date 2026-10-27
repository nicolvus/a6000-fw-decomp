"""E25 — parcheo offline y reversible de Darwin para forzar la compuerta del motor a 0.

No instala nada, no genera FDAT/DAT y no toca la cámara. Solo lee/escribe copias locales del
`darwin_core.bin` (base ROM 0x4200) y produce un manifiesto JSON con cada byte modificado.

Variantes aceptadas:
  * original 3.21  SHA-256 5f2be06d...0bf4 (sin parche tipo 0)
  * tipo 0 (3.22)  SHA-256 ca41b46c...52dc (parche de bobina 0x20c74 ya aplicado)

El candidato E25 solo es un candidato M0 si la entrada ya lleva el parche tipo 0: con la
compuerta a 0 la lista L0 sigue ejecutando el estado 7, que llama a 0x20c90 (P4D=1) y ese
escritor está filtrado por 0x20c74. Sin tipo 0, L0 no sería suficiente.

Uso:
  python scripts/e25/patch_darwin.py inspect  INPUT
  python scripts/e25/patch_darwin.py apply    INPUT OUTPUT [--manifest JSON]
  python scripts/e25/patch_darwin.py verify   INPUT PATCHED [--manifest JSON]
  python scripts/e25/patch_darwin.py restore  PATCHED OUTPUT --manifest JSON
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BASE = 0x4200
SIZE = 157_276
SHA_ORIGINAL = "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
SHA_TIPO0 = "ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc"
VERSION_ADDR = 0x25B3C
VERSION_BYTES = b"VER0.78\x00"

# Parche tipo 0 ya instalado en la cámara (T024): 0x20c74 devuelve siempre 0.
TIPO0_ADDR = 0x20C78
TIPO0_BYTES = bytes.fromhex("09e000bf00bf00bf")
ORIGINAL_TYPE_BYTES = bytes.fromhex("faf702fa00f00700")

# E25: 0x1fe66 deja de leer la compuerta y retorna 0.
#   0x1fe68  movs r5, #0      (00 25)  [sin cambios]
#   0x1fe6a  b 0x1fe82       (0a e0)  [antes: mov r0, r5 = 28 46]
#   0x1fe82  mov r0, r5      (28 46)
#   0x1fe84  pop {r4,r5,r6,pc}
GATE_FN = 0x1FE66
GATE_EPILOGUE = 0x1FE82
PATCH_ADDR = 0x1FE6A
PATCH_OLD = bytes.fromhex("2846")
PATCH_NEW = bytes.fromhex("0ae0")

# Regiones que un parche de esta fase NO debe tocar (E24-02/E24-04/E24-05).
PROTECTED = [
    ("reset", 0x45C8, 0x4638),
    ("scatter_load", 0x43FC, 0x4404),
    ("bootloader_mailbox", 0x45BC, 0x45C8),
    ("upd_main", 0x8DA8, 0x8E00),
    ("initcom", 0x4BCA, 0x5000),
    ("com_task", 0xECE4, 0xED40),
    ("watchdog", 0xA4AC, 0xA540),
    ("power_table", 0x28C6C, 0x28D00),
    ("gpio_writer", 0x51C0, 0x51CC),
    ("type0_filter", 0x20C74, 0x20C90),
]


class ImageError(ValueError):
    """La imagen no es una variante conocida o está corrupta."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(data: bytes, addr: int, size: int) -> bytes:
    off = addr - BASE
    if off < 0 or off + size > len(data):
        raise ImageError(f"dirección fuera del binario: {addr:#x}+{size:#x}")
    return data[off:off + size]


def _file_offset(addr: int) -> int:
    return addr - BASE


@dataclass(frozen=True)
class Variant:
    name: str
    sha256: str
    tipo0_present: bool
    m0_candidate: bool
    description: str


ORIGINAL = Variant(
    "original_321", SHA_ORIGINAL, False, False,
    "Darwin 3.21 original, sin parche tipo 0; el candidato E25 no es M0 por sí solo",
)
TIPO0 = Variant(
    "tipo0_322", SHA_TIPO0, True, True,
    "Darwin 3.21 con parche tipo 0 de T024, empaquetado como 3.22; base del candidato M0",
)


class DarwinImage:
    """Copia local verificada de `darwin_core.bin` (admite la variante ya parcheada por E25)."""

    def __init__(self, path: Path, data: bytes):
        self.path = path
        self.data = data
        self.variant, self.patched = self._identify()

    @classmethod
    def load(cls, path: str | Path) -> DarwinImage:
        p = Path(path)
        if not p.is_file():
            raise ImageError(f"no existe: {p}")
        return cls(p, p.read_bytes())

    def _identify(self) -> tuple[Variant, bool]:
        n = len(self.data)
        if n != SIZE:
            raise ImageError(f"tamaño inesperado: {n} (esperado {SIZE})")
        ver = _slice(self.data, VERSION_ADDR, len(VERSION_BYTES))
        if ver != VERSION_BYTES:
            raise ImageError(f"cadena de versión inesperada en {VERSION_ADDR:#x}: {ver!r}")
        digest = sha256(self.data)
        if digest in (SHA_ORIGINAL, SHA_TIPO0):
            variant = ORIGINAL if digest == SHA_ORIGINAL else TIPO0
            want = ORIGINAL_TYPE_BYTES if variant is ORIGINAL else TIPO0_BYTES
            if _slice(self.data, TIPO0_ADDR, len(TIPO0_BYTES)) != want:
                raise ImageError(f"SHA {variant.name} pero bytes de tipo inesperados")
            return variant, False
        # Una imagen E25 válida es la base conocida con *solo* el parche de la compuerta.
        if _slice(self.data, PATCH_ADDR, len(PATCH_NEW)) == PATCH_NEW:
            base = bytearray(self.data)
            base[PATCH_ADDR - BASE:PATCH_ADDR - BASE + len(PATCH_NEW)] = PATCH_OLD
            base_digest = sha256(bytes(base))
            if base_digest in (SHA_ORIGINAL, SHA_TIPO0):
                variant = ORIGINAL if base_digest == SHA_ORIGINAL else TIPO0
                want = ORIGINAL_TYPE_BYTES if variant is ORIGINAL else TIPO0_BYTES
                if _slice(bytes(base), TIPO0_ADDR, len(TIPO0_BYTES)) != want:
                    raise ImageError("base E25 con bytes de tipo inesperados")
                return variant, True
        raise ImageError(f"SHA-256 desconocido: {digest}")

    def sha256(self) -> str:
        return sha256(self.data)

    def byte(self, addr: int) -> int:
        return _slice(self.data, addr, 1)[0]

    def bytes(self, addr: int, size: int) -> bytes:
        return _slice(self.data, addr, size)

    def has_patch(self) -> bool:
        return self.bytes(PATCH_ADDR, len(PATCH_NEW)) == PATCH_NEW


def _check_output_path(input_path: Path, output_path: Path) -> None:
    if input_path.resolve() == output_path.resolve():
        raise ImageError("la salida no puede ser el mismo archivo que la entrada")
    if output_path.suffix.lower() in (".fdat", ".dat"):
        raise ImageError("E25 no genera paquetes instalables (.fdat/.dat)")
    if output_path.suffix.lower() != ".bin":
        raise ImageError("la salida debe ser un .bin")


def _protected_hashes(data: bytes) -> dict[str, str]:
    return {name: sha256(_slice(data, start, end - start)) for name, start, end in PROTECTED}


def _diff(before: bytes, after: bytes) -> list[dict[str, Any]]:
    if len(before) != len(after):
        raise ImageError("los buffers difieren de tamaño")
    out = []
    for i, (b, a) in enumerate(zip(before, after)):
        if b != a:
            out.append({
                "file_offset": i,
                "rom_address": i + BASE,
                "before": f"{b:02x}",
                "after": f"{a:02x}",
            })
    return out


def _assert_authorized(diff: list[dict[str, Any]], allowed: set[int]) -> None:
    bad = [d for d in diff if d["rom_address"] not in allowed]
    if bad:
        raise ImageError(f"cambios fuera de las posiciones autorizadas: {bad}")


def build_manifest(image: DarwinImage, output: bytes, method: str = "B1a") -> dict[str, Any]:
    diff = _diff(image.data, output)
    allowed = set(range(PATCH_ADDR, PATCH_ADDR + len(PATCH_NEW)))
    _assert_authorized(diff, allowed)
    before_protected = _protected_hashes(image.data)
    after_protected = _protected_hashes(output)
    protected_ok = before_protected == after_protected
    tipo0_before = _slice(image.data, TIPO0_ADDR, len(TIPO0_BYTES))
    tipo0_after = _slice(output, TIPO0_ADDR, len(TIPO0_BYTES))
    output_sha = sha256(output)
    return {
        "schema": "a6000.e25.manifest.v1",
        "generated_by": "scripts/e25/patch_darwin.py",
        "method": method,
        "input": {
            "path": str(image.path),
            "sha256": sha256(image.data),
            "size": len(image.data),
            "variant": image.variant.name,
            "darwin_version": "VER0.78",
            "tipo0_present": image.variant.tipo0_present,
        },
        "patch": {
            "id": "E25-GATE-ZERO",
            "description": (
                "0x1fe66 retorna 0 sin leer [0x20000050+canal]; los tres arrancadores de la "
                "máquina exterior eligen L0 [0,7,8,9,10] y 0x1f5a6 retorna antes del motor"
            ),
            "base": f"{BASE:#x}",
            "function": f"{GATE_FN:#x}",
            "epilogue": f"{GATE_EPILOGUE:#x}",
            "bytes_changed": len(diff),
            "patches": [{
                "rom_address": f"{PATCH_ADDR:#x}",
                "file_offset": _file_offset(PATCH_ADDR),
                "before_hex": PATCH_OLD.hex(),
                "after_hex": PATCH_NEW.hex(),
                "size": len(PATCH_NEW),
                "instruction_before": "mov r0, r5",
                "instruction_after": "b 0x1fe82",
            }],
        },
        "preserved": {
            "tipo0": {
                "address": f"{TIPO0_ADDR:#x}",
                "before_hex": tipo0_before.hex(),
                "after_hex": tipo0_after.hex(),
                "unchanged": tipo0_before == tipo0_after,
                "present": image.variant.tipo0_present,
            },
            "protected_regions": [
                {"name": name, "start": f"{start:#x}", "end": f"{end:#x}",
                 "sha256_before": before_protected[name], "sha256_after": after_protected[name],
                 "unchanged": before_protected[name] == after_protected[name]}
                for name, start, end in PROTECTED
            ],
            "all_protected_unchanged": protected_ok,
        },
        "diff": diff,
        "output": {
            "path": None,  # se rellena al escribir
            "sha256": output_sha,
            "size": len(output),
        },
        "safety": {
            "installable": False,
            "fdat_generated": False,
            "m0_candidate": image.variant.m0_candidate,
            "requires_tipo0": True,
            "recovery_blocker": "E24-04: no hay recuperación independiente demostrada",
            "warning": (
                "Candidato offline. No instalar: E24-04 sigue abierto y no se ha demostrado "
                "recuperación si Darwin no arranca."
            ),
        },
    }


def apply(input_path: str | Path, output_path: str | Path, manifest_path: str | Path | None = None) -> dict[str, Any]:
    image = DarwinImage.load(input_path)
    out = Path(output_path)
    _check_output_path(image.path, out)
    if image.has_patch():
        raise ImageError("la entrada ya lleva el parche E25")
    if image.bytes(PATCH_ADDR, len(PATCH_OLD)) != PATCH_OLD:
        raise ImageError(f"bytes originales inesperados en {PATCH_ADDR:#x}: "
                         f"{image.bytes(PATCH_ADDR, len(PATCH_OLD)).hex()}")
    data = bytearray(image.data)
    data[_file_offset(PATCH_ADDR):_file_offset(PATCH_ADDR) + len(PATCH_NEW)] = PATCH_NEW
    output = bytes(data)
    manifest = build_manifest(image, output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(output)
    manifest["output"]["path"] = str(out)
    if manifest_path is not None:
        mp = Path(manifest_path)
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def verify(input_path: str | Path, patched_path: str | Path, manifest_path: str | Path | None = None) -> dict[str, Any]:
    image = DarwinImage.load(input_path)
    patched_data = Path(patched_path).read_bytes()
    if len(patched_data) != len(image.data):
        raise ImageError(f"tamaño inesperado en el parcheado: {len(patched_data)}")
    if patched_data[PATCH_ADDR - BASE:PATCH_ADDR - BASE + len(PATCH_NEW)] != PATCH_NEW:
        raise ImageError("el binario no contiene el parche E25")
    expected = bytearray(image.data)
    expected[PATCH_ADDR - BASE:PATCH_ADDR - BASE + len(PATCH_NEW)] = PATCH_NEW
    if bytes(expected) != patched_data:
        raise ImageError("el binario contiene cambios distintos del parche E25")
    manifest = build_manifest(image, patched_data)
    if manifest_path is not None:
        mp = Path(manifest_path)
        if not mp.is_file():
            raise ImageError(f"no existe el manifiesto: {mp}")
        old = json.loads(mp.read_text())
        if old.get("output", {}).get("sha256") != manifest["output"]["sha256"]:
            raise ImageError("el SHA-256 no coincide con el manifiesto")
        if old.get("diff") != manifest["diff"]:
            raise ImageError("el diff no coincide con el manifiesto")
    return manifest


def restore(patched_path: str | Path, output_path: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    patched = DarwinImage.load(patched_path)
    mp = Path(manifest_path)
    if not mp.is_file():
        raise ImageError(f"no existe el manifiesto: {mp}")
    manifest = json.loads(mp.read_text())
    if manifest.get("schema") != "a6000.e25.manifest.v1":
        raise ImageError("manifiesto de esquema desconocido")
    expected_input = manifest["input"]["sha256"]
    out = Path(output_path)
    _check_output_path(patched.path, out)
    if sha256(patched.data) != manifest["output"]["sha256"]:
        raise ImageError("el binario parcheado no coincide con el manifiesto")
    if patched.data[PATCH_ADDR - BASE:PATCH_ADDR - BASE + len(PATCH_NEW)] != PATCH_NEW:
        raise ImageError("el binario no contiene el parche E25")
    data = bytearray(patched.data)
    data[PATCH_ADDR - BASE:PATCH_ADDR - BASE + len(PATCH_NEW)] = PATCH_OLD
    restored = bytes(data)
    if sha256(restored) != expected_input:
        raise ImageError("la restauración no reproduce el SHA-256 de entrada")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(restored)
    return {
        "restored": str(out),
        "sha256": sha256(restored),
        "matches_manifest_input": sha256(restored) == expected_input,
        "bytes_changed": len(PATCH_NEW),
    }


def inspect(path: str | Path) -> dict[str, Any]:
    image = DarwinImage.load(path)
    return {
        "path": str(image.path),
        "sha256": sha256(image.data),
        "size": len(image.data),
        "variant": image.variant.name,
        "patched": image.patched,
        "tipo0_present": image.variant.tipo0_present,
        "m0_candidate": image.variant.m0_candidate and image.patched,
        "gate_bytes": image.bytes(GATE_FN, 0x20).hex(),
        "patch_present": image.has_patch(),
        "gate_patch_old_here": image.bytes(PATCH_ADDR, len(PATCH_OLD)) == PATCH_OLD,
        "gate_patch_new_here": image.bytes(PATCH_ADDR, len(PATCH_NEW)) == PATCH_NEW,
    }


def _main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="E25: parche offline y reversible de la compuerta del motor")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("inspect", help="verifica e identifica una copia de darwin_core.bin")
    p.add_argument("input")

    p = sub.add_parser("apply", help="aplica el parche E25 a una copia")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--manifest", default=None)

    p = sub.add_parser("verify", help="comprueba que un binario solo difiere en el parche E25")
    p.add_argument("input")
    p.add_argument("patched")
    p.add_argument("--manifest", default=None)

    p = sub.add_parser("restore", help="revierte byte a byte usando el manifiesto")
    p.add_argument("patched")
    p.add_argument("output")
    p.add_argument("--manifest", required=True)

    args = ap.parse_args(argv)
    try:
        if args.cmd == "inspect":
            print(json.dumps(inspect(args.input), indent=2, ensure_ascii=False))
        elif args.cmd == "apply":
            m = apply(args.input, args.output, args.manifest)
            print(json.dumps({k: m[k] for k in ("method", "input", "patch", "output", "safety")},
                             indent=2, ensure_ascii=False))
            print(f"diff: {len(m['diff'])} bytes; tipo0 presente: {m['preserved']['tipo0']['present']}; "
                  f"tipo0 sin cambios: {m['preserved']['tipo0']['unchanged']}; "
                  f"regiones protegidas intactas: {m['preserved']['all_protected_unchanged']}")
        elif args.cmd == "verify":
            m = verify(args.input, args.patched, args.manifest)
            print(f"OK: {m['output']['sha256']} ({len(m['diff'])} bytes modificados; "
                  f"tipo0={m['preserved']['tipo0']['present']})")
        elif args.cmd == "restore":
            print(json.dumps(restore(args.patched, args.output, args.manifest), indent=2, ensure_ascii=False))
    except ImageError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
