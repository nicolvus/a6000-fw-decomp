"""E26 — verificación del 3.25 corregido (3.25c) contra cada causa del bloqueo del 3.25 (R36/R39).

Parte del `.dat` final (lo que se publica), no de artefactos intermedios:

1. contenedor: descifrado independiente (auditor E25-06, no fwtool) = FDAT, sumas, CRC, versión, modelo;
2. tar: qué miembros cambian frente al 3.21 oficial y frente al 3.25 que bloqueó la cámara;
3. `nflasha3`: invariantes de la ruta Loader3 → ARM7 → LDEC (`hardware_violations`), disposición
   frente a Sony, bloques no tocados idénticos a los de Sony, contenido lógico;
4. emulación R39: código real de Loader3 y del ARM7 sobre los 369 bloques, con el 3.21 de Sony y el
   3.25 que bloqueó como controles.

Escribe `analysis/e25-27/verify-325c.json` (sin binarios).  Sale con 1 si algo falla.  Solo lee.

Uso:
    .venv/bin/python scripts/e25_27/verify_325c.py [--dat RUTA]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "analysis/e26-recovery"))

from e25_24 import patch_bionz as PB  # type: ignore[import-not-found]
import r39_tpzl_emu as R39  # type: ignore[import-not-found]
from e25_06 import audit_packages as A  # type: ignore[import-not-found]

from e25_27 import build, fatimg, sums, tarball, tpzl

DAT = ROOT / "analysis/e25-27/artifacts-325c/package-3.25/firmware_packed.dat"
BRICK_DAT = ROOT / "analysis/e25-27/artifacts/package-3.25/firmware_packed.dat"
BRICK_DAT_SHA = "42c02504"  # prefijo del .dat instalado que bloqueó la cámara (R36 §2)
OUT = ROOT / "analysis/e25-27/verify-325c.json"
PARTITION_BYTES = 0x01E00000  # nflasha3 = 30 MiB (volcado del 20-10-2026)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def open_dat(path: Path, keys: tuple[bytes, bytes]) -> tuple[dict[str, Any], dict[str, bytes]]:
    """Descifra con el auditor E25-06 y devuelve (comprobaciones, miembros del tar)."""
    dat = path.read_bytes()
    info = A.parse_dat(dat)
    fdat = path.with_suffix(".fdat").read_bytes()
    dec = A.decrypt_fdat(dat, info["fdat_offset"], info["fdat_size"], keys, compare=fdat)
    hdr = A.parse_fdat_header(fdat[: A.FDAT_HDR])
    tar = fdat[hdr["firmware_offset"] : hdr["firmware_offset"] + hdr["firmware_size"]]
    upd = next(fs for fs in hdr["filesystems"] if fs["mode"] == "U")
    checks = {
        "dend_ok": info["dend_stored"] == info["dend_computed"],
        "descifrado_igual_a_fdat": dec.first_mismatch_vs_fdat is None,
        "bloques_sin_error": not (dec.bad_sum or dec.bad_flag or dec.bad_len),
        "crc_cabecera_ok": hdr["checksum_stored"] == hdr["checksum_computed"],
        "version_3_25_o_3_27": hdr["version"] in ("3.25", "3.27", "3.29", "3.30"),  # 3.27 = 3.25c; 3.29/3.30 = 3.25c + selector en vivo (3.30: también en el envío)
        "modelo_region": (hdr["model"], hdr["region"]) == (build.MODEL, build.REGION),
        "updater_oficial_3_21": sha(fdat[upd["offset"] : upd["offset"] + upd["size"]])
        == build.UPDATER_SHA256,
    }
    entries, _ = tarball.parse(tar)
    return {"sha256": sha(dat), "version": hdr["version"], **checks}, {e.name: e.data for e in entries}


def layout(img: tpzl.TpzlImage, raw: bytes) -> dict[str, Any]:
    ends = [o + s for o, s in img.entries]
    pads = [raw[o + len(img.block(i)) : ends[i]] for i, (o, _) in enumerate(img.entries)]
    return {
        "bloques": len(img.entries),
        "offsets_no_alineados_512": sum(o & 0x1FF != 0 for o, _ in img.entries),
        "bloques_contiguos": all(ends[i] == img.entries[i + 1][0] for i in range(len(ends) - 1)),
        "relleno_no_cero": sum(bool(p.strip(b"\x00")) for p in pads),
        "max_sectores_por_bloque": max(-(-s // 512) for _, s in img.entries),
        "tamano": len(raw),
        "violaciones_ldec": len(tpzl.hardware_violations(img)),
    }


def records(block: bytes) -> list[bytes]:
    out, pos = [], 0
    for _ in range(16):
        start = pos
        _, pos = tpzl._inflate_segment(block, pos)
        out.append(block[start:pos])
    return out


def records_kept(old: bytes, new: bytes) -> int:
    """Registros (bytes comprimidos) idénticos a los de Sony en la misma posición."""
    return sum(a == b for a, b in zip(records(old), records(new)))


def run(dat_path: Path = DAT) -> dict[str, Any]:
    keys = A.load_keys()
    pkg, new = open_dat(dat_path, keys)
    brick_pkg, brick = open_dat(BRICK_DAT, keys)
    stock = {e.name: e.data for e in tarball.parse(build.load_originals().tar)[0]}

    changed_vs_321 = sorted(n for n in new if new[n] != stock[n])
    changed_vs_brick = sorted(n for n in new if new[n] != brick[n])

    raw_new, raw_sony, raw_brick = (m[build.NFLASHA3] for m in (new, stock, brick))
    p_new, p_sony, p_brick = (tpzl.TpzlImage.parse(r) for r in (raw_new, raw_sony, raw_brick))
    lay_new, lay_sony, lay_brick = layout(p_new, raw_new), layout(p_sony, raw_sony), layout(p_brick, raw_brick)
    # el último bloque de Sony acaba antes que su entrada del TOC (fin de archivo): se compara sin el relleno
    identical = [i for i in range(len(p_sony.entries))
                 if p_new.block(i)[: len(p_sony.block(i))] == p_sony.block(i)
                 and not p_new.block(i)[len(p_sony.block(i)):].strip(b"\x00")]
    recompressed = sorted(set(range(len(p_sony.entries))) - set(identical))
    kept = {i: records_kept(p_sony.block(i), p_new.block(i)) for i in recompressed}

    d_new, d_sony = p_new.decompressed(), p_sony.decompressed()
    # páginas de 4096 B cambiadas por bloque de 64 KiB: _splice guarda exactamente esas como registros propios
    changed_pages = {i: sum(d_new[p:p + 4096] != d_sony[p:p + 4096] for p in range(i << 16, (i + 1) << 16, 4096))
                     for i in recompressed}
    fat_new, fat_sony = fatimg.Fat16.parse(d_new), fatimg.Fat16.parse(d_sony)
    avcam_bytes = set(fat_sony.offsets_for(build.AVCAM_NAME))
    diff = [i for i, (a, b) in enumerate(zip(d_new, d_sony)) if a != b]
    reverted, _ = fat_new.patch(build.AVCAM_NAME, fat_sony.read(build.AVCAM_NAME))

    bl = R39.BL.read_bytes()
    code, arm7 = bl[0x22800 : 0x22800 + R39.L3_LEN], bl[0x18800 : 0x18800 + 0x3800]
    emu = {}
    for name, raw in (("corregida_3.25c", raw_new), ("sony_3.21", raw_sony), ("bloqueo_3.25", raw_brick)):
        r = R39.run(raw, code, arm7)
        emu[name] = {"entradas": r["entradas"], "fallos": len(r["fallos"]),
                     "avisos_residuo": r["avisos_residuo"], "primer_fallo": r["primer_fallo"]}

    checks = {
        # contenedor
        **{f"contenedor.{k}": v for k, v in pkg.items() if k not in ("sha256", "version")},
        "control.dat_3_25_es_el_que_bloqueo": brick_pkg["sha256"].startswith(BRICK_DAT_SHA),
        # tar
        "tar.cambios_vs_3_21_solo_4_miembros": changed_vs_321
        == sorted([build.DARWIN_CORE, build.DARWIN_SUM, build.NFLASHA3, build.PART_SUM]),
        "tar.cambios_vs_3_25_solo_nflasha3_y_su_suma": changed_vs_brick
        == sorted([build.NFLASHA3, build.PART_SUM]),
        "tar.part_image_sum_verifica": sums.verify(
            new[build.PART_SUM].decode("ascii"), build.PART_ENTRY, raw_new),
        # defecto 1 de R36: residuo dentro del sector
        "nflasha3.residuo_0_en_todos_los_bloques": lay_new["offsets_no_alineados_512"] == 0,
        # defecto 2 de R36: registros distintos de 16 x 4096 / cota de Sony
        "nflasha3.sin_violaciones_ldec": lay_new["violaciones_ldec"] == 0,
        "nflasha3.relleno_0x00_como_sony": lay_new["relleno_no_cero"] == 0,
        "nflasha3.bloques_contiguos_como_sony": lay_new["bloques_contiguos"],
        "nflasha3.max_sectores_igual_que_sony": lay_new["max_sectores_por_bloque"]
        <= lay_sony["max_sectores_por_bloque"],
        "nflasha3.cabe_en_la_particion": lay_new["tamano"] < PARTITION_BYTES,
        "nflasha3.mismo_numero_de_bloques": lay_new["bloques"] == lay_sony["bloques"],
        "nflasha3.solo_bloques_0_48_57_recompuestos": recompressed == [0, 48, 57],
        "nflasha3.registros_de_sony_salvo_paginas_cambiadas": all(
            kept[i] == 16 - changed_pages[i] for i in recompressed),
        "control.sony_sin_violaciones": lay_sony["violaciones_ldec"] == 0,
        "control.3_25_detectado": lay_brick["violaciones_ldec"] > 0,
        # contenido lógico
        # 3.25/3.27: idéntico al 3.25 previsto; 3.29: solo difiere de él dentro de av-cam (cueva del selector)
        "contenido.igual_al_3_25_previsto": d_new == p_brick.decompressed()
        if pkg["version"] in ("3.25", "3.27")
        else {i for i, (a, b) in enumerate(zip(d_new, p_brick.decompressed())) if a != b} <= avcam_bytes,
        "bionz.cueva_selector_presente": (
            pkg["version"] not in ("3.29", "3.30")
            or fat_new.read(build.AVCAM_NAME)[PB.CAVE - PB.BASE:PB.CAVE - PB.BASE + PB.CAVE_LEN] == PB.cave_bytes()),
        "bionz.envio_lleva_ajuste_en_vivo": (
            pkg["version"] != "3.30"
            or (fat_new.read(build.AVCAM_NAME)[PB.SEND - PB.BASE:PB.SEND - PB.BASE + 4] == PB.bl(PB.SEND, PB.SEND_CAVE)
                and fat_new.read(build.AVCAM_NAME)[PB.SEND_CAVE - PB.BASE:PB.SEND_CAVE - PB.BASE + PB.SEND_CAVE_LEN]
                == PB.send_cave_bytes())),
        "contenido.cambios_solo_dentro_de_av_cam": set(diff) <= avcam_bytes,
        "contenido.av_cam_es_el_construido": sha(fat_new.read(build.AVCAM_NAME))
        == sha((dat_path.parents[1] / "av-cam.integrated.bin").read_bytes()),
        "contenido.revertir_av_cam_da_sony_exacto": reverted == d_sony,
        # emulación R39 (Loader3 + ARM7 reales, LDEC modelado)
        "emulacion.corregida_0_fallos": emu["corregida_3.25c"]["fallos"] == 0
        and emu["corregida_3.25c"]["entradas"] == lay_sony["bloques"],
        "emulacion.corregida_sin_avisos_residuo": emu["corregida_3.25c"]["avisos_residuo"] == 0,
        "control.emulacion_sony_0_fallos": emu["sony_3.21"]["fallos"] == 0,
        "control.emulacion_reproduce_el_bloqueo": emu["bloqueo_3.25"]["fallos"] > 0
        and emu["bloqueo_3.25"]["primer_fallo"] == 0,
    }
    return {
        "fase": "E26 — 3.25c experimental",
        "dat_sha256": pkg["sha256"],
        "bootloader_sha256": sha(bl),
        "todo_ok": all(checks.values()),
        "comprobaciones": checks,
        "disposicion": {"corregida": lay_new, "sony_3.21": lay_sony, "bloqueo_3.25": lay_brick},
        "emulacion": emu,
        "registros_de_sony_conservados": {str(k): v for k, v in kept.items()},
        "bytes_logicos_distintos_de_sony": len(diff),
        "tar_cambios_vs_3_21": changed_vs_321,
        "tar_cambios_vs_3_25": changed_vs_brick,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dat", type=Path, default=DAT)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)
    report = run(args.dat)
    args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, ok in report["comprobaciones"].items():
        print("OK  " if ok else "FALLO", name)
    print("todo_ok:", report["todo_ok"])
    return 0 if report["todo_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
