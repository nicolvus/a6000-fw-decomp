#!/usr/bin/env python3
"""FILM-PB-1 (26-11) — tar del CFW con el `AV-CAM.BIN` de FÁBRICA 3.21 (sin el parche PP del núcleo). NO instala nada.

Mismo camino que usó la build 3.93 (`scripts/gui/build_cfw_film.py`): `build_base_pp.main(base, salida, bionz=…)`,
que sustituye `AV-CAM.BIN` en la FAT de `nflasha3`, recompone SOLO los bloques TPZL tocados y actualiza
`part_image.sum` con `scripts/e25_27/{tarball,tpzl,fatimg,sums}`. El hook `bionz` devuelve el binario de fábrica
tal cual: ni PP del núcleo, ni S-Log3, ni B/N, ni Silent r5, ni LUT de películas, ni ISO.

Uso: construir.py BASE.tar SALIDA.tar [--avcam AVCAM.bin]

Verifica en el mismo run, con `mmap` para no cargar los 212 MB de cada tar en RAM: lectura de vuelta byte a byte,
`part_image.sum`, resto de miembros intacto (cabecera y SHA-256), bloque 0 de `nflasha3` igual al de Sony (R55),
disposición TPZL y rangos de bytes que cambian contra el av-cam del paquete instalado.
"""
import argparse
import hashlib
import json
import mmap
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "scripts"))
import build_base_pp
from e25_27 import build, fatimg, sums, tarball, tpzl

N15, N3 = "0700_part_image/dev/nflasha15", build.NFLASHA3
AVCAM_FABRICA = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
CHUNK = 1 << 20


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def miembros(ruta: Path):
    """(nombre, cabecera, desplazamiento de datos, tamaño) de cada miembro del tar, sin cargarlo en RAM."""
    with open(ruta, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        pos = 0
        while pos + 512 <= len(mm):
            cab = mm[pos:pos + 512]
            if cab == b"\0" * 512:
                break
            nombre = cab[:100].split(b"\0", 1)[0].decode("utf-8", "replace")
            tam = tarball._parse_number(cab[124:136])
            yield nombre, cab, pos + 512, tam
            pos += 512 + ((tam + 511) // 512) * 512


def sha_rango(ruta: Path, off: int, tam: int) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        for k in range(off, off + tam, CHUNK):
            h.update(mm[k:min(k + CHUNK, off + tam)])
    return h.hexdigest()


def leer_miembro(ruta: Path, nombre: str) -> bytes:
    with open(ruta, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        for n, _cab, off, tam in miembros(ruta):
            if n == nombre:
                return mm[off:off + tam]
    raise KeyError(nombre)


def rangos(a: bytes, b: bytes) -> list[dict]:
    """Rangos [inicio, fin), en bytes del fichero, donde `a` y `b` difieren (mismo tamaño)."""
    out, i = [], 0
    while i < min(len(a), len(b)):
        if a[i] != b[i]:
            j = i
            while j < len(a) and a[j] != b[j]:
                j += 1
            out.append({"inicio": f"0x{i:08x}", "fin": f"0x{j:08x}", "bytes": j - i})
            i = j
        else:
            i += 1
    return out


def fat_de(part: bytes) -> fatimg.Fat16:
    return fatimg.Fat16.parse(tpzl.TpzlImage.parse(part).decompressed(workers=1))


def rangos_del_fichero(fat: fatimg.Fat16, nombre: str) -> list[tuple[int, int]]:
    """Intervalos [inicio, fin) del descomprimido que ocupa el fichero, por su cadena de clústeres."""
    e = fat.find(nombre)
    out, resto = [], e.size
    for c in e.clusters:
        base, tam = fat.cluster_offset(c), min(resto, fat.cluster_size)
        out.append((base, base + tam))
        resto -= tam
        if resto == 0:
            break
    return out


def main(base: Path, salida: Path, avcam: Path) -> dict:
    fabrica = avcam.read_bytes()
    assert fabrica[4:8] == b"ORIL", "el fichero no lleva la firma ORIL (LIRO en LE)"
    assert sha(fabrica) == build.AVCAM_SHA256, f"el av-cam no es el de fábrica 3.21: {sha(fabrica)}"
    rep = build_base_pp.main(base, salida, bionz=lambda _original: fabrica)  # núcleo = 3.21 sin ningún parche

    # 1) estructura y resto de miembros: cabecera y SHA-256 (mmap, sin cargar los tars)
    ent_in = list(miembros(base))
    ent_out = list(miembros(salida))
    tocados = {N3, build.PART_SUM}
    intacto, alterados = True, []
    for (n_in, cab_in, off_in, tam_in), (n_out, cab_out, off_out, tam_out) in zip(ent_in, ent_out):
        if n_in != n_out:
            raise AssertionError(f"orden de miembros distinto: {n_in} / {n_out}")
        if n_in in tocados:
            continue
        igual = cab_in == cab_out and sha_rango(base, off_in, tam_in) == sha_rango(salida, off_out, tam_out)
        if not igual:
            intacto = False
            alterados.append(n_in)

    # 2) AV-CAM.BIN de vuelta desde el tar nuevo, y su FAT frente a la del paquete
    n3_new, n3_old = leer_miembro(salida, N3), leer_miembro(base, N3)
    sum_new, sum_old = leer_miembro(salida, build.PART_SUM), leer_miembro(base, build.PART_SUM)
    fat_new, fat_old = fat_de(n3_new), fat_de(n3_old)
    av_new, av_old = fat_new.read(build.AVCAM_NAME), fat_old.read(build.AVCAM_NAME)
    part_new = tpzl.TpzlImage.parse(n3_new)
    sony3 = tpzl.TpzlImage.parse(build.load_originals().members[N3])

    # 3) el descomprimido solo puede cambiar en los clústeres de AV-CAM.BIN (ni FAT, ni vmlinux, ni initrd, ni sabin)
    dec_new, dec_old = part_new.decompressed(workers=1), tpzl.TpzlImage.parse(n3_old).decompressed(workers=1)
    permitidos = rangos_del_fichero(fat_new, build.AVCAM_NAME) + rangos_del_fichero(fat_old, build.AVCAM_NAME)
    permitidos.sort()
    distintos, fuera, k = 0, [], 0
    for i, (a, b) in enumerate(zip(dec_old, dec_new)):
        if a == b:
            continue
        distintos += 1
        while k < len(permitidos) and permitidos[k][1] <= i:
            k += 1
        if not (k < len(permitidos) and permitidos[k][0] <= i):
            fuera.append(i)
    ends = [o + s for o, s in part_new.entries]
    info = {
        "base_tar": str(base), "base_sha256": sha_rango(base, 0, base.stat().st_size),
        "salida_tar": str(salida), "salida_sha256": sha_rango(salida, 0, salida.stat().st_size),
        "avcam_fabrica": {"ruta": str(avcam), "bytes": len(fabrica), "sha256": sha(fabrica)},
        "build_base_pp": rep,
        "verificacion": {
            "miembros_mismo_numero_y_orden": [e[0] for e in ent_in] == [e[0] for e in ent_out],
            "miembros": len(ent_in),
            "avcam_de_vuelta_igual_que_el_de_fabrica": av_new == fabrica,
            "avcam_de_vuelta_sha256": sha(av_new),
            "part_image_sum_valida": sums.verify(sum_new.decode("ascii"), build.PART_ENTRY, n3_new),
            "part_sum_linea_antes": sums.update(sum_old.decode("ascii"), build.PART_ENTRY, n3_new)[1]["line_before"],
            "part_sum_linea_despues": sums.update(sum_old.decode("ascii"), build.PART_ENTRY, n3_new)[1]["line_after"],
            "resto_de_miembros_intacto": intacto,
            "miembros_alterados_por_error": alterados,
            "nflasha3_bloque_0_igual_que_sony": part_new.block(0) == sony3.block(0),
            "nflasha3_mismo_numero_de_bloques_que_sony": len(part_new.entries) == len(sony3.entries),
            "nflasha15_intacta": sha_rango(base, next(e for e in ent_in if e[0] == N15)[2], next(e for e in ent_in if e[0] == N15)[3])
                                == sha_rango(salida, next(e for e in ent_out if e[0] == N15)[2], next(e for e in ent_out if e[0] == N15)[3]),
            "descomprimido_solo_cambia_el_avcam": not fuera,
            "bytes_distintos_en_el_descomprimido": distintos,
            "offsets_fuera_del_avcam": fuera[:20],
            "clusters_avcam": {"primero": fat_new.cluster_offset(fat_new.find(build.AVCAM_NAME).clusters[0]),
                               "clusters": len(fat_new.find(build.AVCAM_NAME).clusters),
                               "tamano_cluster": fat_new.cluster_size},
        },
        "nflasha3": {"bytes_entrada": len(n3_old), "bytes_salida": len(n3_new), "bloques": len(part_new.entries),
                     "bloques_recompuestos": rep["bloques_tpzl"],
                     "contiguo": all(ends[i] == part_new.entries[i + 1][0] for i in range(len(ends) - 1)),
                     "alineado_512": all(o & 0x1FF == 0 for o, _ in part_new.entries),
                     "violaciones_ldec": len(tpzl.hardware_violations(part_new)),
                     "max_sectores": max(-(-s // 512) for _, s in part_new.entries)},
        "avcam": {"bytes_paquete": len(av_old), "bytes_fabrica": len(av_new),
                  "bytes_distintos_vs_paquete": sum(1 for a, b in zip(av_old, av_new) if a != b),
                  "rangos_vs_paquete": rangos(av_old, av_new), "sha256_paquete": sha(av_old)},
    }
    (salida.parent / "construir.json").write_text(json.dumps(info, indent=1))
    return info


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("base", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--avcam", type=Path, default=AVCAM_FABRICA)
    a = ap.parse_args()
    print(json.dumps(main(a.base.resolve(), a.salida.resolve(), a.avcam), indent=1))
