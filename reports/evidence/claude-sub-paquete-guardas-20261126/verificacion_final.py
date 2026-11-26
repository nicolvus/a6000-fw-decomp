#!/usr/bin/env python3
"""Verificación de cierre: el `/usr` del 4.05 lleva el `libmpr.so` parcheado y nada más que el pp + él.

- Compara la lista de ficheros distintos del `/usr` con la del pp + `lib/libmpr.so`.
- Extrae `lib/libmpr.so` del `firmware.tar` del paquete 4.05 (el mismo que el DAT, byte a byte por la
  aserción de `build_package_nflasha15.py`) y comprueba sha256, modo, uid y gid frente al `.so` parcheado
  y al original de Sony.
- Deja un SHA256SUMS de todos los artefactos.
Solo lee/escribe en /tmp y en el directorio de evidencia.
"""
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parent
BUILD = ROOT / "build/cfw_bypass_guardas"
PP_AUDIT = ROOT / "build/cfw_func393-pp.audit.json"
STOCK = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so"
sys.path.insert(0, str(ROOT / "scripts"))
from e25_27 import tpzl  # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> dict:
    propio = json.loads((EV / "audit.json").read_text())
    pp = json.loads(PP_AUDIT.read_text())
    esperado = sorted(set(pp["ficheros_distintos_ext2"]) | {"lib/libmpr.so"})
    igual_que_pp_mas_libmpr = sorted(propio["ficheros_distintos_ext2"]) == esperado
    assert igual_que_pp_mas_libmpr, (set(esperado) ^ set(propio["ficheros_distintos_ext2"]))
    assert propio["todo_ok"] and not [k for k, v in propio["comprobaciones"].items() if not v]

    # /usr/lib/libmpr.so tal como viaja en el tar del paquete
    with tarfile.open(BUILD / "pkg-4.05/firmware.tar") as t:
        n15 = t.extractfile("0700_part_image/dev/nflasha15").read()
    ext = tpzl.TpzlImage.parse(n15).decompressed()
    with tempfile.TemporaryDirectory() as tmp:
        img = Path(tmp) / "usr.ext2"
        img.write_bytes(ext)
        out = Path(tmp) / "libmpr.so"
        subprocess.run(["debugfs", "-R", f"dump /lib/libmpr.so {out}", str(img)], capture_output=True, check=True)
        stat = subprocess.run(["debugfs", "-R", "stat /lib/libmpr.so", str(img)], capture_output=True, text=True, check=True).stdout
        got = out.read_bytes()
        campos = {k: stat.split(f"{k}:")[1].split()[0] for k in ("Mode", "User", "Group", "Size")}
    parcheado = BUILD / "files/lib/libmpr.so"
    orig = STOCK.read_bytes()
    checks = {
        "ext2_libmpr_igual_al_parcheado": got == parcheado.read_bytes(),
        "sha256_parcheado": hashlib.sha256(got).hexdigest() == "63dfaed5a6ebf8e6d9a94a8bf29a5effdb98350cc680d41abf913617a92e1578",
        "solo_8_bytes_sobre_el_original": sorted(i for i, (a, b) in enumerate(zip(got, orig)) if a != b) == [0x437BFA, 0x437BFB, 0x437BFC, 0x437BFD, 0x437C2C, 0x437C2D, 0x437C2E, 0x437C2F],
        "tamano_igual_que_el_original": len(got) == len(orig),
        "modo_0555": campos["Mode"] == "0555", "uid_57285": campos["User"] == "57285", "gid_1000": campos["Group"] == "1000",
        "tamano_en_ext2": int(campos["Size"]) == len(orig),
    }
    assert all(checks.values()), checks
    artefactos = [BUILD / "libmpr.so", BUILD / "files/lib/libmpr.so", BUILD / "files/MANIFEST.json", BUILD / "files/SHA256SUMS",
                  BUILD / "nflasha15-405.bin", BUILD / "pkg-4.05/firmware.tar",
                  BUILD / "pkg-4.05/package-4.05/firmware_packed.dat", BUILD / "pkg-4.05/package-4.05/firmware_packed.fdat",
                  BUILD / "pkg-4.05/package-4.05/SHA256SUMS", BUILD / "pkg-4.05/container.json"]
    (EV / "SHA256SUMS").write_text("".join(f"{sha(p)}  {p.relative_to(ROOT)}\n" for p in artefactos))
    return {"ficheros_distintos_ext2": len(propio["ficheros_distintos_ext2"]),
            "igual_que_pp_mas_libmpr": igual_que_pp_mas_libmpr, "comprobaciones": checks,
            "ext2_stat": campos, "artefactos_hasheados": len(artefactos)}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
