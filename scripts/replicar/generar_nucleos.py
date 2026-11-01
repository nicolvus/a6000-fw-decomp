#!/usr/bin/env python3
"""Genera los dos darwin_core.bin que necesita scripts/e25_05/build_packages.py a partir del Darwin OFICIAL 3.21.

Entrada:  firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin (SHA-256 oficial, comprobado).
Salidas:  analysis/darwin-patch/darwin_core_tipo0.bin           (parche «tipo 0», 3.22)
          analysis/e25/darwin_core_tipo0_sin_rearme.bin         (tipo 0 + B1a, 3.23)
Ambas salidas se verifican contra el SHA-256 publicado; si no coinciden, aborta sin escribir."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x4200  # dirección de carga de darwin_core.bin
OFICIAL = "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
TIPO0 = ("ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc",
         ROOT / "analysis/darwin-patch/darwin_core_tipo0.bin")
B1A = ("55a366a5fc95f01ccb044ae352db90f0122ee779cab69063b6b99da8b3dcea1d",
       ROOT / "analysis/e25/darwin_core_tipo0_sin_rearme.bin")
P_TIPO0 = (0x20C78, bytes.fromhex("09e000bf00bf00bf"))  # b 0x20c8e; nop; nop; nop
P_B1A = (0x1FE6A, bytes.fromhex("0ae0"))                # 28 46 -> 0a e0


def parchear(datos: bytes, addr: int, nuevo: bytes) -> bytes:
    off = addr - BASE
    return datos[:off] + nuevo + datos[off + len(nuevo):]


def main() -> None:
    src = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
    core = src.read_bytes()
    if hashlib.sha256(core).hexdigest() != OFICIAL:
        sys.exit("darwin_core.bin no es el del firmware oficial 3.21")
    tipo0 = parchear(core, *P_TIPO0)
    b1a = parchear(tipo0, *P_B1A)
    for (sha, destino), datos in ((TIPO0, tipo0), (B1A, b1a)):
        if hashlib.sha256(datos).hexdigest() != sha:
            sys.exit(f"SHA-256 inesperado para {destino.name}")
    for (_, destino), datos in ((TIPO0, tipo0), (B1A, b1a)):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(datos)
        print("OK", destino.relative_to(ROOT))


if __name__ == "__main__":
    main()
