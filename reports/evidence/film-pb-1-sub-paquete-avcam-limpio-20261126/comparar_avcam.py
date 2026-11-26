#!/usr/bin/env python3
"""FILM-PB-1 (26-11) — ¿qué bytes del `AV-CAM.BIN` cambian entre fábrica 3.21, base 3.38, paquete instalado 3.93 y paquete limpio 3.94?

Atribuye los 34 013 B que separan el av-cam instalado del de fábrica a las dos capas que se suman:
  A = parches del «BIONZ 3.38» del proyecto (el av-cam del CFW 3.38, `analysis/e25-27/artifacts-338/`)
  B = lo que añadía el paquete 3.93 encima (PP del núcleo, Silent r5, S-Log3/B-N/Hi-Light, películas, ISO)
y comprueba que el av-cam del 3.94 es el de fábrica sin ningún parche.

Uso: comparar_avcam.py  → JSON a stdout
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_27 import build, fatimg, tarball, tpzl

N3 = build.NFLASHA3
FABRICA = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE338 = ROOT / "analysis/e25-27/artifacts-338/av-cam.integrated.bin"
TAR_INSTALADO = ROOT / "build/cfw_func393/pp/base-film.tar"
TAR_LIMPIO = ROOT / "build/cfw_avcam_limpio/base-film-avcam321.tar"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def avcam_de_tar(ruta: Path) -> bytes:
    m = {e.name: e.data for e in tarball.parse(ruta.read_bytes())[0]}
    return fatimg.Fat16.parse(tpzl.TpzlImage.parse(m[N3]).decompressed(workers=1)).read(build.AVCAM_NAME)


def tramos(a: bytes, b: bytes, hueco: int = 0) -> list[tuple[int, int]]:
    """Tramos [inicio, fin) donde `a` y `b` difieren; `hueco` une tramos separados por menos de esos bytes."""
    crudo, i = [], 0
    while i < len(a):
        if a[i] != b[i]:
            j = i
            while j < len(a) and a[j] != b[j]:
                j += 1
            crudo.append([i, j])
            i = j
        else:
            i += 1
    fuera: list[tuple[int, int]] = []
    for ini, fin in crudo:
        if fuera and ini - fuera[-1][1] < hueco:
            fuera[-1] = (fuera[-1][0], fin)
        else:
            fuera.append((ini, fin))
    return fuera


def bytes_en(a: bytes, b: bytes) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


def main() -> dict:
    nuevo = avcam_de_tar(TAR_LIMPIO)
    binarios = {"fabrica_321": FABRICA.read_bytes(), "base338": BASE338.read_bytes(),
                "instalado_393": avcam_de_tar(TAR_INSTALADO), "limpio_394": nuevo}
    assert len({len(v) for v in binarios.values()}) == 1, "av-cams de tamaños distintos"
    propio = {k: {"bytes": len(v), "sha256": sha(v)} for k, v in binarios.items()}
    pares = [("fabrica_321", "base338"), ("base338", "instalado_393"), ("fabrica_321", "instalado_393"), ("fabrica_321", "limpio_394")]
    difusos = {}
    for x, y in pares:
        a, b = binarios[x], binarios[y]
        t = tramos(a, b)
        agrupado = tramos(a, b, hueco=16)
        difusos[f"{x}_vs_{y}"] = {
            "bytes": bytes_en(a, b), "tramos_contiguos": len(t), "tramos_con_hueco_16B": len(agrupado),
            "mayores": sorted(({"inicio": f"0x{i:08x}", "fin": f"0x{j:08x}", "bytes": j - i} for i, j in t), key=lambda d: -d["bytes"])[:8],
        }
    # atribución: bytes de A (fábrica→3.38) y de B (3.38→instalado); el 3.94 debe quitar TODOS
    a_i, b_i, inst = binarios["fabrica_321"], binarios["base338"], binarios["instalado_393"]
    A = {i for i in range(len(a_i)) if a_i[i] != b_i[i]}
    B = {i for i in range(len(b_i)) if b_i[i] != inst[i]}
    nuevos = []
    for i in range(len(a_i)):
        if nuevo[i] != a_i[i]:
            nuevos.append(i)
    return {
        "binarios": propio,
        "diferencias": difusos,
        "atribucion": {
            "A_parches_3_38": len(A), "B_anadidos_del_paquete_393": len(B), "A_unido_B": len(A | B), "A_interseccion_B": len(A & B),
            "instalado_vs_fabrica": len(A | B),
            "tramos_A_con_hueco_16B": len(tramos(a_i, b_i, 16)), "tramos_B_con_hueco_16B": len(tramos(b_i, inst, 16)),
        },
        "limpio_394": {"bytes_distintos_del_avcam_de_fabrica": len(nuevos), "es_el_de_fabrica": nuevo == a_i,
                       "deshace_A": A <= set(nuevos) or len(nuevos) == 0, "avcam_sha256": sha(nuevo)},
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
