#!/usr/bin/env python3
"""Arma build/cfw_bypass_guardas/files a partir del overlay `pp` (3.93) + lib/libmpr.so parcheado.

Copia el árbol de fuentes del `pp`, añade el `.so` con las dos guardas anuladas y actualiza
`MANIFEST.json` (originales/parcheados/md5) y `SHA256SUMS`. Antes de escribir comprueba que las 30
entradas heredadas siguen casando con sus ficheros, con el original de Sony (3.21) y con sus md5.
Solo escribe bajo build/cfw_bypass_guardas/.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PP = ROOT / "build/cfw_func393/pp/files"
DST = ROOT / "build/cfw_bypass_guardas/files"
SO = ROOT / "build/cfw_bypass_guardas/libmpr.so"
STOCK = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked"
REL = "lib/libmpr.so"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()  # noqa: S324  (md5 es el formato del MANIFEST, no seguridad)


def main() -> dict:
    assert not DST.exists(), f"ya existe {DST}"
    shutil.copytree(PP, DST)
    shutil.copy2(SO, DST / REL)

    man = json.loads((PP / "MANIFEST.json").read_text())
    heredadas = sorted(man["parcheados"])
    assert set(heredadas) == set(man["originales"]) == set(man["md5"]), "claves descuadradas en el pp"
    # 1) el estilo del pp se reproduce exactamente (json indent=1 + sort_keys), para que el diff sea solo la entrada nueva
    assert json.dumps(man, indent=1, sort_keys=True) == (PP / "MANIFEST.json").read_text(), "el pp no está en indent=1/sort_keys"
    # 2) los ficheros copiados y sus originales de Sony casan con lo declarado
    copiados_ok = {r: sha(DST / r) == man["parcheados"][r] for r in heredadas}
    originales_ok = {r: sha(STOCK / r) == man["originales"][r] for r in heredadas}
    md5_ok = {r: man["md5"][r] == {"original": md5(STOCK / r), "parcheado": md5(DST / r)} for r in heredadas}
    assert all(copiados_ok.values()) and all(originales_ok.values()) and all(md5_ok.values()), (
        [r for r, v in copiados_ok.items() if not v], [r for r, v in originales_ok.items() if not v], [r for r, v in md5_ok.items() if not v])

    # 3) entrada nueva: original = el de Sony 3.21 / el mismo que lleva el ext2 de base-film.tar (9a74a3bb…)
    man["originales"][REL] = sha(STOCK / REL)
    man["parcheados"][REL] = sha(DST / REL)
    man["md5"][REL] = {"original": md5(STOCK / REL), "parcheado": md5(DST / REL)}
    assert man["originales"][REL] != man["parcheados"][REL], "el .so no difiere del original"
    (DST / "MANIFEST.json").write_text(json.dumps(man, indent=1, sort_keys=True))

    sums = "".join(f"{h}  {r}\n" for r, h in man["parcheados"].items())
    (DST / "SHA256SUMS").write_text(sums)
    viejo = (PP / "SHA256SUMS").read_text().splitlines()
    nuevo = sums.splitlines()
    return {
        "ficheros": len(man["parcheados"]),
        "heredadas_intactas": f"{sum(copiados_ok.values())}/{len(copiados_ok)}",
        "sha256sums_lineas_heredadas_iguales": nuevo[: len(viejo)] == viejo,
        "lineas_nuevas": [ln for ln in nuevo if ln not in viejo],
        "libmpr_original_sha256": man["originales"][REL], "libmpr_parcheado_sha256": man["parcheados"][REL],
        "libmpr_md5": man["md5"][REL], "tamano": (DST / REL).stat().st_size,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
    sys.exit(0)
