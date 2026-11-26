#!/usr/bin/env python3
"""Comprueba que reempaquetar el `firmware.tar` de Sony con su propio `nflasha15` no cambia
ni un byte (base = tar oficial 3.21, sin `--sin-wbi`, sin `--darwin-v3`).

Es la premisa de la «vía A operativa»: paquete oficial con la versión subida y nada más.
Solo lectura sobre `firmware/`; no escribe nada.

Uso: .venv/bin/python3 reports/evidence/film-pb-1-sub-riesgo-flash-20261126/reconstruir-tar-oficial.py
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_27 import build, sums, tarball  # noqa: E402

BASE = ROOT / "firmware/extracted/fw321/firmware.tar"
SONY15 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                 "0700_part_image/dev/nflasha15")
ENTRY = "dev/nflasha15"
NFLASHA15 = "0700_part_image/dev/nflasha15"  # build.py no exporta esta constante


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> dict:
    base = BASE.read_bytes()
    sony15 = SONY15.read_bytes()
    members = {e.name: e.data for e in tarball.parse(base)[0]}
    linea_antes = [ln for ln in members[build.PART_SUM].decode("ascii").splitlines()
                   if ln.rstrip().endswith("," + ENTRY + ",")]
    part_sum, detail = sums.update(members[build.PART_SUM].decode("ascii"), ENTRY, sony15)
    assert sums.verify(part_sum, ENTRY, sony15), "la suma recalculada no verifica"
    nuevo, rep = tarball.rebuild(base, {NFLASHA15: sony15,
                                        build.PART_SUM: part_sum.encode("ascii")})
    return {
        "tar_oficial_sha256": sha(base),
        "tar_reconstruido_sha256": sha(nuevo),
        "identico_byte_a_byte": nuevo == base,
        "linea_nflasha15_antes": linea_antes,
        "linea_nflasha15_despues": detail["line_after"],
        "miembros_tocados": rep,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(main(), indent=1, ensure_ascii=False))
