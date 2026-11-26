#!/usr/bin/env python3
"""Auditoría de un CFW instalable de la A6000: contenedor `.dat`, `/usr`, coherencia estática y arranque real en el arnés.

Uso:
  audita_cfw.py RUTA [--completo|--rapido] [--arranque|--sin-arranque] [--salida DIR]
                    [--perfil-dir X] [--puerto N] [--json] [--teclas menu,intro,...]
                    [--declara FICHERO.json] [--usr-sony DIR] [--espera S]
  audita_cfw.py DIRECTORIO --lote [--arranque] [--json]

RUTA puede ser un `.dat` de actualización, un directorio de paquete (con `nflasha15`/`nflasha15.bin`) o un
`nflasha15.bin` suelto; un directorio con `cam/usr` se trata como overlay ya extraído (salida de `pkg_usr.py`).
Solo lee el paquete y el firmware; todo lo temporal va a un directorio temporal y los informes a `--salida`.

Etapas (cada comprobación lleva id, ok, detalle y evidencia VERIFICADO/INFERENCIA/NO_VERIFICADO):
  1. contenedor `.dat` (cabecera FDAT, CRC, modelo/región, dend, bloques cifrados, updater oficial, tar y sumas);
  2. `/USR` frente al `/usr` de Sony de la misma versión (añadidos/cambiados/quitados con sha256);
  3. estructura y coherencia (ELF, parches binarios declarados, recursos/UXC y tablas de Backup/NVRAM);
  4. arranque en frío en QEMU (`live.py`) con perfil y puerto propios, 3 capturas y comparación con Sony de serie;
  5. informe JSON + resumen Markdown + consola. Código de salida 1 si falla algo de 1–3 o el arranque; 2 si el
     entorno no permite auditar (faltan claves, base Sony o artefactos del arnés): nunca un OK falso.

Coste medido (equipo de desarrollo, 8 vCPU): contenedor + `/usr` + estructura ≈ 25 s por CFW con `--completo`;
arranque en frío ≈ 3 min (≈ 7 s si el perfil ya tiene estado guardado). La primera vez que se ejecuta el arranque
también se captura la base de Sony de serie (≈ 3 min) y queda en `analysis/gui/g22/harness/audit-base-sony/`.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for _p in (ROOT / "scripts", ROOT / "references/fwtool", ROOT / "scripts/gui", HERE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

BLOCK = 1024
DAT_MAGIC = bytes.fromhex("895546550d0a1a0a")
N15 = "dev/nflasha15"
PARTICION = 104_857_600  # mount.conf: /dev/nflasha15 /usr raw 104857600
PUERTO_MIN, PUERTO_MAX = 8630, 8645
TRABAJO = ROOT / "analysis/gui/g22/harness"
BASE_SONY = TRABAJO / "audit-base-sony"
ARCH_CFW = ROOT / "analysis/gui/g22"
ARCH_DOCS = ROOT / "docs/gui/auditorias"
NFLASHA15_SONY = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15"
BK_TBL = TRABAJO / "overlay/cam/usr/share/bk.tbl"
SYM = {True: "OK", False: "FALLO", None: "NO VERIFICADO"}


class EntradaError(ValueError):
    """La ruta no es un CFW reconocible o falta un requisito para auditar (nunca se convierte en OK)."""


# ------------------------------------------------------------------------------------------------ utilidades
def sha256_bytes(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def sha256_file(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        while trozo := f.read(1 << 20):
            h.update(trozo)
    return h.hexdigest()


def ahora() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def dia() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d")


def add(checks: list[dict[str, Any]], cid: str, ok: bool | None, detalle: str, etapa: int, *,
        evidencia: str = "VERIFICADO", aviso: bool = False, material: bool = False) -> None:
    assert evidencia in ("VERIFICADO", "INFERENCIA", "NO_VERIFICADO"), evidencia
    checks.append({"id": cid, "etapa": etapa, "ok": ok, "detalle": detalle, "evidencia": evidencia,
                   "aviso": aviso, "material": material})


def veredicto(checks: list[dict[str, Any]]) -> str:
    """FALLO si algo demostrable falla; AVISO si solo hay avisos; PARCIAL si falta algo material; OK."""
    if any(c["ok"] is False for c in checks):
        return "FALLO"
    if any(c["aviso"] for c in checks):
        return "AVISO"
    if any(c["ok"] is None and c["material"] for c in checks):
        return "PARCIAL"
    return "OK"


def codigo_salida(r: dict[str, Any]) -> int:
    return 1 if r["veredicto"] == "FALLO" else 0


def _deps():
    from e25_06 import audit_packages as A  # type: ignore[import-not-found]
    from e25_27 import sums, tarball, tpzl  # type: ignore[import-not-found]
    return A, sums, tarball, tpzl


def _workers() -> int:
    env = os.environ.get("AUDITA_WORKERS")
    if env:
        return max(1, int(env))
    if "pytest" in sys.modules:  # bajo pytest no se usan procesos hijos (spawn reimporta el módulo de pruebas)
        return 1
    return max(1, min(8, os.cpu_count() or 1))


# ------------------------------------------------------------------------------------------------ detección
def detecta_tipo(ruta: Path) -> str:
    """`dat`, `nflasha15` (imagen TPZL suelta), `paquete` (directorio con la imagen) u `overlay` (`cam/usr`)."""
    if ruta.is_dir():
        if any((ruta / n).is_file() for n in ("nflasha15", "nflasha15.bin")):
            return "paquete"
        if (ruta / "cam/usr").is_dir():
            return "overlay"
        raise EntradaError(f"{ruta}: directorio sin nflasha15/nflasha15.bin ni cam/usr (no es un paquete de CFW)")
    if not ruta.is_file():
        raise EntradaError(f"{ruta}: no existe")
    with ruta.open("rb") as f:
        cab = f.read(8)
    if cab == DAT_MAGIC:
        return "dat"
    if cab[:4] == b"TPZL":
        return "nflasha15"
    raise EntradaError(f"{ruta}: no es un .dat de Sony, ni un nflasha15 TPZL, ni un directorio de paquete")


def ruta_imagen(ruta: Path, tipo: str) -> Path | None:
    if tipo == "nflasha15":
        return ruta
    if tipo == "paquete":
        for n in ("nflasha15", "nflasha15.bin"):
            if (ruta / n).is_file():
                return ruta / n
    return None


def huella(ruta: Path, tipo: str) -> tuple[str, int]:
    """(sha256, bytes) del artefacto: fichero tal cual, imagen del paquete o mapa del overlay."""
    img = ruta_imagen(ruta, tipo)
    if img is not None:
        return sha256_file(img), img.stat().st_size
    if tipo == "overlay":
        lineas = []
        for f in sorted((ruta / "cam/usr").rglob("*")):
            if f.is_file() and not f.is_symlink():
                lineas.append(f"{f.relative_to(ruta / 'cam/usr').as_posix()}:{sha256_file(f)}")
        datos = "\n".join(lineas).encode()
        return sha256_bytes(datos), len(datos)
    return sha256_file(ruta), ruta.stat().st_size


# ------------------------------------------------------------------------------------------------ .dat
def descifra_fdat(buf: bytes, off: int, size: int, keys: tuple[bytes, bytes]) -> tuple[bytes, dict[str, Any]]:
    """FDAT en claro (AES-ECB doble; los 512 B iniciales del primer bloque solo con la primera capa) y sus defectos."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    n = size // BLOCK
    d1 = Cipher(algorithms.AES(keys[0]), modes.ECB()).decryptor()
    d2 = Cipher(algorithms.AES(keys[1]), modes.ECB()).decryptor()
    st: dict[str, Any] = {"bloques": n, "bad_sum": [], "bad_flag": [], "bad_len": [], "pad_ff": True}
    out = bytearray()
    mv = memoryview(buf)
    for cstart in range(0, size - size % BLOCK, BLOCK * 1024):
        fin = min(cstart + BLOCK * 1024, size - size % BLOCK)
        p1 = d1.update(mv[off + cstart:off + fin])
        p2 = d2.update(p1)
        if cstart == 0:
            p2 = p1[:512] + p2[512:]
        for i in range(0, len(p2), BLOCK):
            idx = (cstart + i) // BLOCK
            blk = p2[i:i + BLOCK]
            if len(blk) < BLOCK:
                continue
            stored, flag = struct.unpack_from("<HH", blk)
            if sum(struct.unpack_from("<511H", blk, 2)) & 0xFFFF != stored:
                st["bad_sum"].append(idx)
            ultimo = idx == n - 1
            if bool(flag & 0x8000) != ultimo:
                st["bad_flag"].append(idx)
            ln = flag & 0x7FFF
            if ln > BLOCK - 4 or (not ultimo and ln != BLOCK - 4):
                st["bad_len"].append(idx)
                ln = min(ln, BLOCK - 4)
            if ultimo and set(blk[4 + ln:]) - {0xFF}:
                st["pad_ff"] = False
            out += blk[4:4 + ln]
    st["tamano"] = len(out)
    return bytes(out), st


def verifica_sumas(miembros: dict[str, bytes], sums: Any) -> dict[str, Any]:
    """Todas las líneas `0,…` de los `.sum` del tar que apuntan a un miembro presente."""
    fallidas: list[str] = []
    n = 0
    for nombre, datos in miembros.items():
        if not nombre.endswith(".sum"):
            continue
        texto = datos.decode("ascii", "replace")
        for linea in texto.splitlines():
            campos = linea.split(",")
            if len(campos) < 11 or campos[0] != "0":
                continue
            destino = next((m for m in miembros if m.endswith("/" + campos[10])), None)
            if destino is None:
                continue
            n += 1
            try:
                if not sums.verify(texto, campos[10], miembros[destino]):
                    fallidas.append(f"{nombre}:{campos[10]}")
            except sums.SumError as e:
                fallidas.append(f"{nombre}:{campos[10]} ({e})")
    return {"lineas": n, "fallidas": fallidas}


def etapa_contenedor(ruta: Path, checks: list[dict[str, Any]], tmp: Path) -> dict[str, Any]:
    """Etapa 1: contenedor `.dat`. Devuelve {version, miembros, n15} o {} si no es un .dat válido."""
    A, sums, tarball, tpzl = _deps()
    datos = ruta.read_bytes()
    info = A.parse_dat(datos)
    add(checks, "contenedor.magia_dat", bool(info.get("magic_ok")), "cabecera DAT de Sony (89 55 46 55 0d 0a 1a 0a)", 1)
    if not info.get("magic_ok"):
        return {}
    orden = [c[0] for c in info["chunks"]]
    add(checks, "contenedor.orden_chunks", orden == ["DATV", "PROV", "UDID", "FDAT", "DEND"], f"chunks: {orden}", 1)
    add(checks, "contenedor.sin_cola", info.get("trailing") == 0, f"{info.get('trailing')} B tras DEND", 1)
    add(checks, "contenedor.dend_crc", info.get("dend_stored") == info.get("dend_computed"),
        f"almacenado {info.get('dend_stored')} / calculado {info.get('dend_computed')}", 1)
    add(checks, "contenedor.datv_prov", info.get("datv") == [0x100, 0] and info.get("prov") == 0x100,
        f"DATV={info.get('datv')} PROV={info.get('prov')} (isLens=0)", 1)
    if "fdat_offset" not in info:
        add(checks, "contenedor.fdat_presente", False, "no hay chunk FDAT", 1)
        return {}
    off, size = info["fdat_offset"], info["fdat_size"]
    add(checks, "contenedor.fdat_multiplo_1024", size % BLOCK == 0, f"FDAT cifrado {size} B", 1)
    if size % BLOCK:
        return {}
    try:
        keys = A.load_keys()
    except (OSError, KeyError, SyntaxError) as e:
        raise EntradaError(f"no se pudieron leer las claves de references/fwtool/fwtool/sony/constants.py: {e}") from e
    try:
        fdat, st = descifra_fdat(datos, off, size, keys)
    except Exception as e:  # noqa: BLE001 - un FDAT corrupto debe quedar como FALLO, no abortar el informe
        add(checks, "contenedor.descifrado", False, f"no se pudo descifrar el FDAT: {e}", 1)
        return {}
    add(checks, "contenedor.bloques_suma", not st["bad_sum"], f"{st['bloques']} bloques; suma mala en {st['bad_sum'][:5]}", 1)
    add(checks, "contenedor.bloques_ultimo", not st["bad_flag"], f"bandera de último bloque mala en {st['bad_flag'][:5]}", 1)
    add(checks, "contenedor.bloques_longitud", not st["bad_len"], f"longitudes anómalas en {st['bad_len'][:5]}", 1)
    add(checks, "contenedor.bloques_padding", st["pad_ff"], "relleno del último bloque a 0xFF", 1)
    hermano = ruta.with_suffix(".fdat")
    if hermano.is_file():
        add(checks, "contenedor.descifrado_vs_fdat", hermano.read_bytes() == fdat, f"{len(fdat)} B frente a {hermano.name}", 1)
    hdr = A.parse_fdat_header(fdat[:512])
    add(checks, "contenedor.fdat_magica", hdr["magic"] == "UDTRFIRM" and hdr["format"] == "0100",
        f"{hdr['magic']} / {hdr['format']}", 1)
    add(checks, "contenedor.cabecera_crc", hdr["checksum_stored"] == hdr["checksum_computed"],
        f"CRC-32 [12,512): {hdr['checksum_stored']} / {hdr['checksum_computed']}", 1)
    bcd = hdr["version_major"] == 3 and (hdr["version_minor"] >> 4) <= 9 and (hdr["version_minor"] & 0xF) <= 9
    add(checks, "contenedor.version_valida", bcd, f"versión {hdr['version']} (BCD)", 1)
    add(checks, "contenedor.modelo_a6000", hdr["model"] == 0x41030035, f"modelo 0x{hdr['model']:08x} (A6000 0x41030035)", 1)
    add(checks, "contenedor.region", hdr["region"] == 0, f"región {hdr['region']}", 1)
    add(checks, "contenedor.no_accesorio", hdr["model"] & 0xFF0000 != 0xA00000, "fuera de la familia 0xA0xxxx", 1)
    add(checks, "contenedor.modo_luw", hdr["mode"] == "U" and hdr["luw"] == "N", f"modo {hdr['mode']} / LUW {hdr['luw']}", 1)
    fs = hdr["filesystems"]
    user = fs[0]
    layout_ok = (hdr["num_filesystems"] == 2 and user["mode"] == "U" and user["offset"] == 512
                 and fs[1]["mode"] == "P" and fs[1]["offset"] == 512 and fs[1]["size"] == 0
                 and all(f["mode"] == "\x00" and f["offset"] == f["size"] == 0 for f in fs[2:]))
    add(checks, "contenedor.filesystems", layout_ok, f"U@{user['offset']}+{user['size']}, P@{fs[1]['offset']}+{fs[1]['size']}", 1)
    tar = fdat[hdr["firmware_offset"]:hdr["firmware_offset"] + hdr["firmware_size"]]
    add(checks, "contenedor.tar_dentro_fdat", len(tar) == hdr["firmware_size"]
        and hdr["firmware_offset"] + hdr["firmware_size"] <= len(fdat),
        f"tar@{hdr['firmware_offset']}+{hdr['firmware_size']} de {len(fdat)} B", 1)
    try:
        entradas, sobrante = tarball.parse(tar)
        miembros = {e.name: e.data for e in entradas}
        add(checks, "contenedor.tar_valido", True, f"{len(miembros)} miembros, {len(sobrante)} B de cola", 1)
    except Exception as e:  # noqa: BLE001 - el tar puede fallar de muchas formas y queremos el mensaje
        add(checks, "contenedor.tar_valido", False, f"tar inválido: {e}", 1)
        return {"version": hdr["version"]}
    a6000 = hdr["model"] == 0x41030035
    upd = fdat[user["offset"]:user["offset"] + user["size"]]
    try:
        from e25_27 import build
        oficial = build.UPDATER_SHA256
    except Exception:  # noqa: BLE001 - sin el constructor no se puede afirmar que sea el oficial
        oficial = ""
    if oficial and a6000:
        add(checks, "contenedor.updater_oficial", sha256_bytes(upd) == oficial,
            f"updater {len(upd)} B sha256 {sha256_bytes(upd)[:16]}… (oficial 3.21 {oficial[:16]}…)", 1)
    elif oficial:
        add(checks, "contenedor.updater_oficial", None, "modelo distinto de la A6000: no hay hash de referencia", 1,
            evidencia="NO_VERIFICADO")
    else:
        add(checks, "contenedor.updater_oficial", None, "no se pudo cargar build.UPDATER_SHA256", 1, evidencia="NO_VERIFICADO")
    sumas = verifica_sumas(miembros, sums)
    add(checks, "contenedor.tar_sumas", not sumas["fallidas"],
        f"{sumas['lineas']} líneas verificadas; fallan {sumas['fallidas'][:5]}", 1)
    nombre = next((n for n in miembros if n.endswith("/" + N15)), None)
    add(checks, "contenedor.nflasha15_presente", nombre is not None, nombre or "falta dev/nflasha15", 1)
    if nombre is None:
        return {"version": hdr["version"], "miembros": miembros}
    crudo = miembros[nombre]
    try:
        img = tpzl.TpzlImage.parse(crudo)
        add(checks, "contenedor.nflasha15_tpzl", True, f"{len(img.entries)} bloques de {img.block_size} B; {len(crudo)} B", 1)
        if a6000:
            add(checks, "contenedor.nflasha15_cabe_en_particion", len(crudo) <= PARTICION,
                f"{len(crudo)} B de {PARTICION} B", 1)
        else:
            add(checks, "contenedor.nflasha15_cabe_en_particion", None,
                "modelo distinto de la A6000: la partición de 100 MiB es la de esta cámara", 1, evidencia="NO_VERIFICADO")
        viol = tpzl.hardware_violations(img)
        add(checks, "contenedor.nflasha15_ldec", not viol, f"{len(viol)} violaciones: {viol[:3]}", 1)
        sony = _sony_n15()
        if sony and a6000:
            s_img = tpzl.TpzlImage.parse(sony.read_bytes())
            add(checks, "contenedor.nflasha15_bloque_0_igual_sony", img.block(0) == s_img.block(0),
                "bloque TPZL 0 idéntico al de Sony 3.21 (R55: recomponerlo colgó el LZP)", 1)
            add(checks, "contenedor.nflasha15_mismo_numero_bloques", len(img.entries) == len(s_img.entries),
                f"{len(img.entries)} bloques frente a {len(s_img.entries)} de Sony", 1)
        elif sony:
            add(checks, "contenedor.nflasha15_bloque_0_igual_sony", None,
                "modelo distinto de la A6000: no se compara con el nflasha15 de Sony 3.21", 1, evidencia="NO_VERIFICADO")
            add(checks, "contenedor.nflasha15_mismo_numero_bloques", None, "modelo distinto de la A6000", 1,
                evidencia="NO_VERIFICADO")
        else:
            add(checks, "contenedor.nflasha15_bloque_0_igual_sony", None,
                "falta el nflasha15 de Sony para comparar el bloque 0", 1, evidencia="NO_VERIFICADO", material=True)
    except Exception as e:  # noqa: BLE001 - TPZL dañado
        add(checks, "contenedor.nflasha15_tpzl", False, f"TPZL inválido: {e}", 1)
        return {"version": hdr["version"], "miembros": miembros}
    return {"version": hdr["version"], "miembros": miembros, "n15": crudo}


# ------------------------------------------------------------------------------------------------ /usr
def _sony_n15() -> Path | None:
    env = os.environ.get("AUDITA_SONY_NFLASHA15")
    for p in ([Path(env)] if env else []) + [NFLASHA15_SONY]:
        if p.is_file():
            return p
    return None


def extrae_usr(imagen: bytes, destino: Path, tpzl: Any) -> Path:
    """TPZL → ext2 → `debugfs rdump` (sin root) en `destino`; devuelve la raíz del /usr extraído."""
    img = tpzl.TpzlImage.parse(imagen)
    if img.block_size != 65536:
        raise EntradaError(f"nflasha15 con bloques de {img.block_size} B: este arnés espera 65536")
    destino.mkdir(parents=True, exist_ok=True)
    ext = destino.parent / (destino.name + ".ext2")
    ext.write_bytes(img.decompressed(workers=_workers()))
    subprocess.run(["debugfs", "-R", f"rdump / {destino}", str(ext)], capture_output=True, check=True)
    ext.unlink(missing_ok=True)
    return destino


def mapa_usr(raiz: Path) -> dict[str, str]:
    """{ruta relativa: sha256} de los ficheros regulares (los enlaces simbólicos no se comparan)."""
    return {f.relative_to(raiz).as_posix(): sha256_file(f) for f in raiz.rglob("*") if f.is_file() and not f.is_symlink()}


def etapa_usr(imagen: bytes, usr_sony: Path | None, checks: list[dict[str, Any]], tmp: Path,
              decl: dict[str, Any]) -> dict[str, Any]:
    """Etapa 2: compara el /usr del CFW con el de Sony de la misma versión."""
    _, _, _, tpzl = _deps()
    cfw = extrae_usr(imagen, tmp / "cfw-usr", tpzl)
    if usr_sony is not None:
        sony = usr_sony
        add(checks, "usr.base_sony", sony.is_dir(), f"base Sony indicada: {sony}", 2)
        if not sony.is_dir():
            raise EntradaError(f"{sony}: no existe el /usr de Sony indicado")
    else:
        ruta_sony = _sony_n15()
        if ruta_sony is None:
            raise EntradaError("falta el nflasha15 de Sony 3.21 (firmware/extracted/fw321/…); "
                               "sin base Sony no se puede auditar el /usr (ni dar OK)")
        sony = extrae_usr(ruta_sony.read_bytes(), tmp / "sony-usr", tpzl)
        add(checks, "usr.base_sony", True, f"Sony 3.21 extraído de {ruta_sony}", 2)
    return compara_usr(cfw, sony, checks, decl)


def compara_usr(cfw: Path, sony: Path, checks: list[dict[str, Any]], decl: dict[str, Any]) -> dict[str, Any]:
    """Comparación /usr (común al .dat extraído y a un overlay): añadidos, cambiados, quitados y declaración."""
    m_cfw, m_sony = mapa_usr(cfw), mapa_usr(sony)
    anadidos = sorted(set(m_cfw) - set(m_sony))
    quitados = sorted(set(m_sony) - set(m_cfw))
    cambiados = sorted(k for k in m_cfw.keys() & m_sony.keys() if m_cfw[k] != m_sony[k])
    parcheados = decl.get("parcheados", {})
    parches = decl.get("parches", {})
    nuevos = decl.get("nuevos", {})
    justificados = set(decl.get("quitados", []))
    sin_justificar = [q for q in quitados if q not in justificados]
    if decl.get("overlay_parcial") and quitados:
        add(checks, "usr.ficheros_quitados", None,
            f"{len(quitados)} ficheros de Sony no están en el overlay parcial: no se puede distinguir un borrado", 2,
            evidencia="NO_VERIFICADO")
        sin_justificar = []
    else:
        add(checks, "usr.ficheros_quitados", not sin_justificar,
            f"{len(quitados)} quitados; sin justificar {len(sin_justificar)}: {sin_justificar[:8]}", 2)
    no_declarados = [c for c in cambiados if parcheados.get(c) != m_cfw[c] and c not in parches]
    nuevos_sin_declarar = [n for n in anadidos if n not in nuevos and n not in parcheados]
    aviso = bool(no_declarados or nuevos_sin_declarar)
    add(checks, "usr.cambios_declarados", True,
        f"{len(cambiados)} cambiados ({len(no_declarados)} sin declarar), {len(anadidos)} nuevos "
        f"({len(nuevos_sin_declarar)} sin declarar)", 2, evidencia="VERIFICADO", aviso=aviso)
    desajustes = [f for f, h in parcheados.items() if m_cfw.get(f) != h]
    add(checks, "usr.declaraciones_coherentes", not desajustes,
        f"{len(parcheados)} parcheados declarados; no coinciden {desajustes[:8]}", 2)
    return {"dir_cfw": cfw, "dir_sony": sony, "mapa_cfw": m_cfw, "mapa_sony": m_sony,
            "anadidos": anadidos, "cambiados": cambiados, "quitados": quitados,
            "sin_justificar": sin_justificar, "no_declarados": no_declarados,
            "nuevos_sin_declarar": nuevos_sin_declarar}


# ------------------------------------------------------------------------------------------------ declaraciones
def carga_declaraciones(ruta: Path, tipo: str, extra: Path | None) -> dict[str, Any]:
    """Declaración del CFW (qué cambia): `--declara`, `<ruta>.audit.json`, `audit-cfw.json` o `MANIFEST.json`."""
    candidatos: list[Path] = []
    if extra is not None:
        candidatos.append(extra)
    if tipo in ("paquete", "overlay"):
        candidatos += [ruta / "audit-cfw.json", ruta / "MANIFEST.json"]
    else:
        candidatos += [ruta.with_suffix(ruta.suffix + ".audit.json"), ruta.with_suffix(".audit.json")]
    for p in candidatos:
        if not p.is_file():
            continue
        try:
            bruto = json.loads(p.read_text())
        except (OSError, ValueError) as e:
            raise EntradaError(f"{p}: declaración ilegible ({e})") from e
        d = normaliza_declaracion(bruto)
        d["_fuente"] = str(p)
        return d
    return normaliza_declaracion({})


def _lista(v: Any) -> list[str]:
    if isinstance(v, dict):
        return [str(k) for k in v]
    if isinstance(v, list):
        return [str(x) for x in v]
    return []


def normaliza_declaracion(d: dict[str, Any]) -> dict[str, Any]:
    parcheados = d.get("parcheados") or {}
    if not isinstance(parcheados, dict):
        raise EntradaError("«parcheados» debe ser un objeto ruta → sha256")
    parches = d.get("parches") or d.get("offsets") or {}
    if not isinstance(parches, dict):
        raise EntradaError("«parches» debe ser un objeto ruta → lista de offsets/rangos")
    nv = d.get("nvram") or d.get("backup") or {}
    escrituras = nv.get("escrituras", []) if isinstance(nv, dict) else nv
    recursos = d.get("recursos") or d.get("etiquetas") or []
    nuevos = d.get("nuevos") or {}
    return {"version": d.get("version", ""), "parcheados": {str(k): str(v) for k, v in parcheados.items()},
            "nuevos": {str(k): str(v) for k, v in nuevos.items()} if isinstance(nuevos, dict)
            else {str(k): "" for k in _lista(nuevos)},
            "quitados": _lista(d.get("quitados")), "parches": {str(k): v for k, v in parches.items()},
            "recursos": recursos if isinstance(recursos, list) else [], "nvram": _ids_nvram(escrituras),
            "overlay_parcial": bool(d.get("overlay_parcial") or d.get("parcial")), "_fuente": ""}


def _ids_nvram(v: Any) -> list[int]:
    """Ids de Backup/NVRAM declarados: acepta enteros y cadenas «0x…»."""
    out = []
    for x in _lista(v):
        try:
            out.append(int(x, 0))
        except ValueError as e:
            raise EntradaError(f"id de NVRAM no numérico: {x!r}") from e
    return out


def rangos_declarados(v: Any) -> list[tuple[int, int]]:
    """[«0x10-0x20», 0x30, [0x40, 2]] → rangos [inicio, fin) en bytes."""
    out: list[tuple[int, int]] = []
    for x in v if isinstance(v, list) else [v]:
        if isinstance(x, int):
            out.append((x, x + 1))
        elif isinstance(x, str):
            m = re.fullmatch(r"\s*(0x[0-9a-fA-F]+|\d+)\s*-\s*(0x[0-9a-fA-F]+|\d+)\s*", x)
            if m:
                out.append((int(m.group(1), 0), int(m.group(2), 0)))
                continue
            m = re.fullmatch(r"\s*(0x[0-9a-fA-F]+|\d+)\s*\+?\s*(0x[0-9a-fA-F]+|\d+)?\s*", x)
            if m:
                ini = int(m.group(1), 0)
                out.append((ini, ini + (int(m.group(2), 0) if m.group(2) else 1)))
                continue
        elif isinstance(x, list) and len(x) == 2:
            out.append((int(x[0]), int(x[0]) + int(x[1])))
        else:
            raise EntradaError(f"rango de parche no reconocido: {x!r}")
    return out


def cuenta_diferencias(nuevo: bytes, viejo: bytes, rangos: list[tuple[int, int]] | None) -> tuple[int, int]:
    """(bytes distintos, bytes distintos fuera de los rangos declarados) sin construir listas de offsets."""
    import bisect
    ordenados = sorted(rangos or [])
    inicios = [r[0] for r in ordenados]

    def cubierto(off: int) -> bool:
        i = bisect.bisect_right(inicios, off) - 1
        return i >= 0 and off < ordenados[i][1]

    total = fuera = 0
    for i in range(max(len(nuevo), len(viejo))):
        a = nuevo[i] if i < len(nuevo) else None
        b = viejo[i] if i < len(viejo) else None
        if a != b:
            total += 1
            if not (rangos is not None and cubierto(i)):
                fuera += 1
    return total, fuera


# ------------------------------------------------------------------------------------------------ ELF
def analiza_elf(datos: bytes) -> dict[str, Any]:
    """Validación mínima y autosuficiente de un ELF ARM EABI: cabecera, segmentos/secciones dentro del fichero y DT_NEEDED."""
    fallos: list[str] = []
    needed: list[str] = []
    soname = ""
    if len(datos) < 52:
        return {"ok": False, "fallos": ["menor que la cabecera ELF"], "needed": needed, "soname": soname}
    if datos[:4] != b"\x7fELF":
        return {"ok": False, "fallos": ["sin magia ELF"], "needed": needed, "soname": soname}
    if datos[4] != 1:
        fallos.append("no es ELF32")
    if datos[5] != 1:
        fallos.append("no es little-endian")
    (e_type, e_machine, e_version, _entry, e_phoff, e_shoff, e_flags, _ehsize, e_phentsize, e_phnum,
     e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from("<HHIIIIIHHHHHH", datos, 16)
    if e_machine != 40:
        fallos.append(f"máquina {e_machine} (se espera ARM=40)")
    if e_version != 1:
        fallos.append(f"versión ELF {e_version}")
    if (e_flags >> 24) != 5:
        fallos.append(f"EABI {e_flags >> 24} (se espera 5)")
    if not e_phnum or e_phoff + e_phnum * e_phentsize > len(datos):
        fallos.append("tabla de segmentos fuera del fichero")
    if e_shnum and (e_shoff + e_shnum * e_shentsize > len(datos) or e_shstrndx >= e_shnum):
        fallos.append("tabla de secciones fuera del fichero o sin tabla de nombres")
    cargas = 0
    dyn: tuple[int, int] | None = None
    for i in range(e_phnum if e_phoff + e_phnum * e_phentsize <= len(datos) else 0):
        p_type, p_offset, _p_vaddr, _p_paddr, p_filesz, p_memsz, _p_flags, _p_align = struct.unpack_from(
            "<IIIIIIII", datos, e_phoff + i * e_phentsize)
        if p_filesz > p_memsz:
            fallos.append(f"segmento {i}: filesz > memsz")
        if p_offset + p_filesz > len(datos):
            fallos.append(f"segmento {i}: {p_offset:#x}+{p_filesz:#x} fuera del fichero")
        if p_type == 1:
            cargas += 1
        if p_type == 2:
            dyn = (p_offset, p_filesz)
    if not cargas:
        fallos.append("sin segmento PT_LOAD")
    for i in range(e_shnum if e_shoff + e_shnum * e_shentsize <= len(datos) else 0):
        (_sh_name, sh_type, _sh_flags, _sh_addr, sh_offset, sh_size, sh_link, _sh_info,
         _sh_align, _sh_entsize) = struct.unpack_from("<IIIIIIIIII", datos, e_shoff + i * e_shentsize)
        if sh_type != 8 and sh_offset + sh_size > len(datos):
            fallos.append(f"sección {i}: {sh_offset:#x}+{sh_size:#x} fuera del fichero")
        if sh_link >= e_shnum and sh_type != 8:
            fallos.append(f"sección {i}: sh_link {sh_link} fuera de la tabla")
    if dyn is not None:
        off, tam = dyn
        entradas = [struct.unpack_from("<iI", datos, off + j) for j in range(0, min(tam, len(datos) - off), 8)]
        strtab = strsz = None
        etiquetas: list[tuple[int, int]] = []
        for tag, val in entradas:
            if tag == 0:
                break
            if tag == 5:
                strtab = val
            elif tag == 10:
                strsz = val
            elif tag in (1, 14):
                etiquetas.append((tag, val))
        if strtab is None:
            fallos.append("DT_STRTAB ausente")
        else:
            base = _vaddr_a_offset(datos, e_phoff, e_phnum, e_phentsize, strtab)
            if base is None:
                fallos.append("DT_STRTAB no cae en ningún PT_LOAD")
            else:
                limite = len(datos) if strsz is None else min(len(datos), base + strsz)
                for tag, val in etiquetas:
                    fin = datos.find(b"\0", base + val, limite)
                    if fin < 0:
                        fallos.append(f"cadena dinámica fuera de DT_STRTAB ({val:#x})")
                        continue
                    texto = datos[base + val:fin].decode("latin1")
                    if tag == 1:
                        needed.append(texto)
                    else:
                        soname = texto
    if not needed:
        fallos.append("sin DT_NEEDED (¿ELF estático o tabla dinámica rota?)")
    return {"ok": not fallos, "fallos": fallos, "needed": needed, "soname": soname, "tipo": e_type}


def _vaddr_a_offset(datos: bytes, phoff: int, phnum: int, phentsize: int, vaddr: int) -> int | None:
    for i in range(phnum):
        p_type, p_offset, p_vaddr, _pp, p_filesz, _pm, _pf, _pa = struct.unpack_from("<IIIIIIII", datos, phoff + i * phentsize)
        if p_type == 1 and p_vaddr <= vaddr < p_vaddr + p_filesz:
            return p_offset + (vaddr - p_vaddr)
    return None


# ------------------------------------------------------------------------------------------------ estructura
def nombres_del_invitado(dir_sony: Path) -> set[str]:
    """Nombres resolubles por el cargador en el invitado: /usr/lib del CFW y /lib de la raíz de la cámara."""
    nombres: set[str] = set()
    for raiz in (dir_sony.parent / "lib", TRABAJO / "stage/cam/lib", TRABAJO / "stage/cam/usr/lib"):
        if raiz.is_dir():
            nombres |= {f.name for f in raiz.iterdir() if f.is_file() or f.is_symlink()}
    return nombres


def etapa_estructura(usr: dict[str, Any], checks: list[dict[str, Any]], decl: dict[str, Any], tmp: Path) -> dict[str, Any]:
    """Etapa 3: ELF, parches binarios declarados, recursos/UXC y tablas de Backup/NVRAM."""
    cfw, sony = usr["dir_cfw"], usr["dir_sony"]
    disponibles = ({Path(n).name for n in usr["mapa_cfw"]} | {Path(n).name for n in usr["mapa_sony"]}
                   | nombres_del_invitado(sony))
    revisar = usr["anadidos"] + usr["cambiados"]
    fallos_elf: list[str] = []
    preexistentes: list[str] = []
    for rel in revisar:
        datos = (cfw / rel).read_bytes()
        if not datos.startswith(b"\x7fELF"):
            continue
        r = analiza_elf(datos)
        if not r["ok"]:
            fallos_elf.append(f"{rel}: {'; '.join(r['fallos'])}")
            continue
        faltan = [n for n in r["needed"] if n not in disponibles]
        if faltan:
            viejo = sony / rel
            needed_viejo: list[str] = []
            if viejo.is_file() and viejo.read_bytes().startswith(b"\x7fELF"):
                needed_viejo = analiza_elf(viejo.read_bytes())["needed"]
            heredados = [n for n in faltan if n in needed_viejo]
            nuevos = [n for n in faltan if n not in needed_viejo]
            if heredados:
                preexistentes.append(f"{rel}: {heredados}")
            if nuevos:
                fallos_elf.append(f"{rel}: DT_NEEDED sin resolver {nuevos}")
    add(checks, "estructura.elf", not fallos_elf, f"{len(revisar)} ficheros nuevos/cambiados; "
        f"{len(fallos_elf)} con problemas: {fallos_elf[:4]}", 3)
    if preexistentes:
        add(checks, "estructura.elf_preexistente", True, f"DT_NEEDED ya irresoluble en Sony: {preexistentes[:4]}", 3,
            evidencia="INFERENCIA", aviso=True)

    sin_declarar: dict[str, int] = {}
    rangos_malos: list[str] = []
    for rel in usr["cambiados"]:
        nuevo = (cfw / rel).read_bytes()
        viejo = (sony / rel).read_bytes()
        if nuevo == viejo:
            continue
        if decl["parcheados"].get(rel) == usr["mapa_cfw"][rel]:
            continue
        if rel in decl["parches"]:
            try:
                rangos = rangos_declarados(decl["parches"][rel])
            except EntradaError as e:
                rangos_malos.append(f"{rel}: {e}")
                continue
            if any(r[0] >= len(nuevo) or r[1] > len(nuevo) for r in rangos):
                rangos_malos.append(f"{rel}: un rango declarado sale del fichero ({len(nuevo)} B)")
            _total, fuera_rango = cuenta_diferencias(nuevo, viejo, rangos)
            if fuera_rango:
                sin_declarar[rel] = fuera_rango
        else:
            sin_declarar[rel] = cuenta_diferencias(nuevo, viejo, None)[1]
    add(checks, "estructura.parches", True, f"{len(usr['cambiados'])} ficheros cambiados; "
        f"{len(sin_declarar)} con bytes sin declarar: {sorted(sin_declarar)[:6]}", 3,
        evidencia="VERIFICADO", aviso=bool(sin_declarar or rangos_malos))
    if rangos_malos:
        add(checks, "estructura.parches_rangos", False, "; ".join(rangos_malos[:4]), 3)

    errores_uxc: list[str] = []
    n_uxc = 0
    sin_soporte: list[str] = []
    cambiados = set(usr["anadidos"]) | set(usr["cambiados"])
    for rel in usr["mapa_cfw"]:
        if not rel.endswith(".uxc"):
            continue
        datos = (cfw / rel).read_bytes()
        if not datos.startswith(b"uxc\x07"):
            continue
        try:
            recs = valida_uxc(datos)
        except (AssertionError, ValueError, struct.error, IndexError) as e:
            errores_uxc.append(f"{rel}: {e}")
            continue
        if recs is None:
            sin_soporte.append(rel)
        else:
            n_uxc += 1
    add(checks, "estructura.uxc", not errores_uxc, f"{n_uxc} ficheros de cadenas UXC verificados; "
        f"{len(sin_soporte)} con otro formato; errores: {errores_uxc[:4]}", 3)
    if sin_soporte:
        add(checks, "estructura.uxc_formato", None, "uxc no soportados por uxc_strings.py (no son tablas de cadenas): "
            f"{len(sin_soporte)}, {len([r for r in sin_soporte if r in cambiados])} cambiados: {sorted(sin_soporte)[:4]}", 3,
            evidencia="NO_VERIFICADO")
    if decl["recursos"]:
        faltan, no_verif = [], []
        for item in decl["recursos"]:
            rel = str(item.get("fichero", "")) if isinstance(item, dict) else str(item)
            etiqueta = str(item.get("etiqueta", "")) if isinstance(item, dict) else ""
            f = cfw / rel
            if not rel or not f.is_file():
                faltan.append(f"falta {rel!r}")
                continue
            datos = f.read_bytes()
            if not etiqueta:
                continue
            if datos.startswith(b"uxc\x07"):
                recs = valida_uxc(datos)
                if recs is None:
                    if etiqueta.encode() not in datos:
                        no_verif.append(f"{rel}: formato no soportado y la etiqueta no está en claro")
                elif etiqueta not in recs.values():
                    faltan.append(f"{rel}: no contiene {etiqueta!r}")
            elif etiqueta.encode() not in datos:
                faltan.append(f"{rel}: no contiene {etiqueta!r}")
        add(checks, "estructura.recursos", not faltan, f"{len(decl['recursos'])} recursos declarados: {faltan[:4]}", 3)
        if no_verif:
            add(checks, "estructura.recursos_no_verificables", None, f"{no_verif[:4]}", 3, evidencia="NO_VERIFICADO")
    else:
        add(checks, "estructura.recursos", None, "el CFW no declara recursos/etiquetas que comprobar", 3,
            evidencia="NO_VERIFICADO")

    ids = known_bk_ids()
    if decl["nvram"]:
        if not ids:
            add(checks, "estructura.nvram", None, "el CFW declara escrituras NVRAM pero falta bk.tbl del volcado", 3,
                evidencia="NO_VERIFICADO", material=True)
        else:
            fuera_ids = [i for i in decl["nvram"] if not in_rango_bk(i, ids)]
            add(checks, "estructura.nvram", not fuera_ids, f"{len(decl['nvram'])} ids escritos; fuera de los rangos conocidos: {fuera_ids[:6]}", 3)
    else:
        add(checks, "estructura.nvram", None, "el CFW no declara qué ids de Backup/NVRAM escribe: el arnés no puede demostrarlo", 3,
            evidencia="NO_VERIFICADO")
    return {"elf_revisados": revisar, "elf_fallos": fallos_elf, "sin_declarar": sin_declarar, "uxc": n_uxc}


def valida_uxc(datos: bytes) -> dict[int, str] | None:
    """Valida el índice común de un UXC; devuelve las cadenas si es una tabla `string_*` (tipo 0x1e04) y None si no."""
    if len(datos) < 0x10 or not datos.startswith(b"uxc\x07"):
        raise ValueError("cabecera UXC ausente")
    count = struct.unpack_from("<I", datos, 12)[0] & 0x1FFF
    base = 0x10 + 2 * count
    if base > len(datos):
        raise ValueError(f"índice de {count} ranuras fuera del fichero")
    for k in range(count):
        v = struct.unpack_from("<H", datos, 0x10 + 2 * k)[0]
        if v != 0xFFFF and base + 4 * v >= len(datos):
            raise ValueError(f"ranura {k} apunta fuera del fichero")
    if base + 4 > len(datos) or struct.unpack_from("<H", datos, base + 2)[0] != 0x1E04:
        return None  # otro formato de UXC (layouts, guías, imágenes…): no es una tabla de cadenas
    return uxc_strings_parse(datos)[2]


def uxc_strings_parse(datos: bytes) -> tuple[bytes, int, dict[int, str]]:
    import uxc_strings  # type: ignore[import-not-found]  # scripts/gui
    r = uxc_strings.parse(datos)
    for rid in r[2]:
        if not 0xE000 <= rid < 0xFFFF:
            raise ValueError(f"id {rid:#06x} fuera de 0xE000–0xFFFE")
    return r


def known_bk_ids() -> set[int]:
    """Ids que existen en bk.tbl (generado del volcado NVRAM completo, 2026-11-05)."""
    rutas = [Path(os.environ["AUDITA_BK_TBL"])] if os.environ.get("AUDITA_BK_TBL") else [BK_TBL]
    for p in rutas:
        if not p.is_file():
            continue
        ids, o = set(), 0
        datos = p.read_bytes()
        while o + 8 <= len(datos):
            i, n = struct.unpack_from("<II", datos, o)
            ids.add(i)
            o += 8 + ((n + 3) & ~3)
        return ids
    return set()


def in_rango_bk(ident: int, ids: set[int]) -> bool:
    """Id presente en el volcado o, si no, dentro de su rango [mín, máx] (INFERENCIA, no demostración)."""
    return ident in ids or (min(ids) <= ident <= max(ids))


# ------------------------------------------------------------------------------------------------ QEMU / arranque
def qemu_activos() -> list[str]:
    p = subprocess.run(["pgrep", "-x", "-a", "qemu-system-arm"], capture_output=True, text=True, check=False)
    return [ln for ln in p.stdout.splitlines() if ln.strip()]


def espera_hueco_qemu(maximo: float = 900.0) -> None:
    """No arrancar con 2 o más QEMU en el sistema: espera 30 s entre intentos (hasta `maximo`)."""
    t0 = time.time()
    while True:
        n = len(qemu_activos())
        if n < 2:
            return
        if time.time() - t0 > maximo:
            raise EntradaError(f"hay {n} qemu-system-arm en el sistema y no se libera un hueco en {maximo:.0f} s")
        time.sleep(30)


def puerto_libre(evitar: set[int] | None = None) -> int:
    evitar = evitar or set()
    for p in range(PUERTO_MIN, PUERTO_MAX + 1):
        if p in evitar:
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    raise EntradaError(f"sin puerto libre en {PUERTO_MIN}–{PUERTO_MAX}")


def _http(puerto: int, ruta: str, cuerpo: dict[str, Any] | None = None, timeout: float = 5.0) -> Any:
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:{puerto}{ruta}", data=datos,
                                 headers={"Content-Type": "application/json"} if datos else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        texto = r.read()
    try:
        return json.loads(texto)
    except ValueError:
        return texto.decode("utf-8", "replace")


def tecla(puerto: int, nombre: str, valor: int) -> None:
    _http(puerto, "/tecla", {"k": nombre, "v": valor})


class Frames:
    """Último PNG del flujo SSE `/eventos` de live.py (no toca la página ni el lienzo)."""

    def __init__(self, puerto: int) -> None:
        self.puerto, self.ultimo, self.n = puerto, b"", 0
        self.cv = threading.Condition()
        self.parar = threading.Event()
        self.hilo = threading.Thread(target=self._bucle, daemon=True)
        self.hilo.start()

    def _bucle(self) -> None:
        while not self.parar.is_set():
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.puerto}/eventos", timeout=5) as r:
                    for linea in r:
                        if self.parar.is_set():
                            return
                        if linea.startswith(b"data: "):
                            png = base64.b64decode(linea[6:].strip())
                            if png:
                                with self.cv:
                                    self.ultimo, self.n = png, self.n + 1
                                    self.cv.notify_all()
            except (OSError, ValueError):
                self.parar.wait(1)

    def espera(self, mayor_que: int, timeout: float) -> bool:
        with self.cv:
            return self.cv.wait_for(lambda: self.n > mayor_que, timeout=timeout)

    def cierra(self) -> None:
        self.parar.set()


def para_sesion(vm: subprocess.Popen | None, puerto: int, perfil: str) -> None:
    """POST /salir y, si algo queda, termina el QEMU de ESTE perfil (nunca otros)."""
    if vm is not None and vm.poll() is None:
        try:
            _http(puerto, "/salir", {}, timeout=10)
        except (OSError, ValueError):
            pass
        try:
            vm.wait(timeout=120)
        except subprocess.TimeoutExpired:
            vm.terminate()
            try:
                vm.wait(timeout=30)
            except subprocess.TimeoutExpired:
                vm.kill()
    for linea in [ln for ln in qemu_activos() if f"live/{perfil}/" in ln]:
        pid = int(linea.split()[0])
        for sig in (15, 9):
            try:
                os.kill(pid, sig)
            except OSError:
                break
            time.sleep(1)


def analiza_png(png: bytes) -> dict[str, Any]:
    import numpy as np
    from PIL import Image
    img = Image.open(io.BytesIO(png)).convert("RGB")
    a = np.asarray(img)
    no_fondo = int((a.max(axis=2) > 24).sum())
    colores = len(np.unique(a.reshape(-1, 3), axis=0))
    return {"w": img.width, "h": img.height, "no_fondo": no_fondo, "colores": colores,
            "negro": bool(a.max() < 8 or colores < 3)}


def compara_png(cfw: bytes, sony: bytes) -> dict[str, Any]:
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(io.BytesIO(cfw)).convert("RGB"), dtype=np.int16)
    b = np.asarray(Image.open(io.BytesIO(sony)).convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        return {"comparable": False, "motivo": f"tamaños {a.shape} y {b.shape}"}
    dist = np.abs(a - b).max(axis=2) > 16
    return {"comparable": True, "fraccion_distinta": round(float(dist.mean()), 4),
            "no_fondo": [int((a.max(axis=2) > 24).sum()), int((b.max(axis=2) > 24).sum())]}


def sesion_arranque(overlay: Path | None, perfil: str, puerto: int, salida: Path, etiqueta: str,
                    teclas: str, espera_max: float, hueco_max: float = 900.0) -> dict[str, Any]:
    """Arranca live.py (perfil y puerto propios), espera la primera pantalla y captura 3 PNG + secuencia opcional."""
    live = HERE / "live.py"
    env = {**os.environ, "LIVE_REINTENTOS": os.environ.get("AUDITA_REINTENTOS", "2"),
           "LIVE_ARRANQUE_MAX": str(int(espera_max))}
    argv = [sys.executable, str(live), str(TRABAJO), "--perfil-dir", perfil, "--puerto", str(puerto)]
    if overlay is not None:
        argv += ["--pkg", str(overlay)]
    log = salida / f"{etiqueta}-live.log"
    t_inicio = time.time()
    t0 = t_inicio
    vm: subprocess.Popen | None = None
    frames: Frames | None = None
    res: dict[str, Any] = {"etiqueta": etiqueta, "perfil": perfil, "puerto": puerto, "pngs": {}, "metricas": {},
                           "im_exit": False, "qemu_murio": False, "error": "",
                           "consola": str(TRABAJO / "live" / perfil / "consola.log")}
    try:
        espera_hueco_qemu(hueco_max)
        t0 = time.time()  # el tope de arranque cuenta desde que hay hueco de QEMU, no desde la espera
        res["espera_hueco_s"] = round(t0 - t_inicio, 1)
        with log.open("wb") as out:
            vm = subprocess.Popen(argv, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env)
        frames = Frames(puerto)
        while time.time() - t0 < espera_max:
            if vm.poll() is not None:
                res["qemu_murio"] = True
                break
            try:
                st = _http(puerto, "/estado", timeout=2)
            except (OSError, ValueError):
                st = None
            if isinstance(st, dict) and int(st.get("fotogramas", 0)) > 0:
                res["arranque_s"] = round(time.time() - t0, 1)
                break
            time.sleep(2)
        consola = Path(res["consola"])
        if consola.is_file() and "IMEXIT " in consola.read_text(errors="replace"):
            res["im_exit"] = True  # im.elf murió (el supervisor ya pudo reintentar; queda registrado)
        if frames.espera(0, 5):
            time.sleep(2)
        res["primera"] = frames.ultimo if frames else b""
        if res["primera"]:
            (salida / f"{etiqueta}-1-primera.png").write_bytes(res["primera"])
            res["pngs"]["primera"] = f"{etiqueta}-1-primera.png"
            res["metricas"]["primera"] = analiza_png(res["primera"])
        if res["primera"]:
            n = frames.n if frames else 0
            tecla(puerto, "menu", 1)
            tecla(puerto, "menu", 0)
            res["menu_abre"] = bool(frames and frames.espera(n, 45))
            time.sleep(2)
            if frames and frames.ultimo:
                (salida / f"{etiqueta}-2-menu.png").write_bytes(frames.ultimo)
                res["pngs"]["menu"] = f"{etiqueta}-2-menu.png"
                res["metricas"]["menu"] = analiza_png(frames.ultimo)
            n = frames.n if frames else 0
            tecla(puerto, "menu", 1)
            tecla(puerto, "menu", 0)
            if frames and frames.espera(n, 15):
                time.sleep(1)
            if frames and frames.ultimo:
                (salida / f"{etiqueta}-3-disparo.png").write_bytes(frames.ultimo)
                res["pngs"]["disparo"] = f"{etiqueta}-3-disparo.png"
                res["metricas"]["disparo"] = analiza_png(frames.ultimo)
            if teclas:
                for nombre in [t.strip() for t in teclas.split(",") if t.strip()]:
                    tecla(puerto, nombre, 1)
                    time.sleep(0.2)
                    tecla(puerto, nombre, 0)
                    time.sleep(0.6)
                time.sleep(2)
                if frames and frames.ultimo:
                    (salida / f"{etiqueta}-4-teclas.png").write_bytes(frames.ultimo)
                    res["pngs"]["teclas"] = f"{etiqueta}-4-teclas.png"
                    res["metricas"]["teclas"] = analiza_png(frames.ultimo)
    except EntradaError:
        raise  # sin hueco de QEMU o entorno incompleto: no es un fallo del CFW
    except Exception as e:  # noqa: BLE001 - la sesión nunca debe tumbar el informe
        res["error"] = f"{type(e).__name__}: {e}"
    finally:
        if frames:
            frames.cierra()
        para_sesion(vm, puerto, perfil)
        res["primera"] = bool(res.get("primera"))  # los bytes no van al informe; el PNG queda en `pngs`
        res["coste_s"] = round(time.time() - t_inicio, 1)
        res["live_log"] = str(log)
    return res


def base_sony(salida: Path, teclas: str, espera_max: float, puerto: int) -> dict[str, Any]:
    """Captura (o reutiliza) las 3 pantallas del Sony de serie; caché en el directorio del arnés."""
    BASE_SONY.mkdir(parents=True, exist_ok=True)
    meta = BASE_SONY / "meta.json"
    pngs = {k: BASE_SONY / f"base-{k}.png" for k in ("primera", "menu", "disparo")}
    try:
        previo = json.loads(meta.read_text())
    except (OSError, ValueError):
        previo = {}
    firma = sha256_bytes((TRABAJO / "vmlinuz").read_bytes()[:1 << 20] + (TRABAJO / "base.cpio.gz").read_bytes()[:1 << 20]
                         + (HERE / "live.py").read_bytes() + teclas.encode())
    if not os.environ.get("AUDITA_BASE_RECAPTURA") and previo.get("firma") == firma and all(p.is_file() for p in pngs.values()):
        return {"pngs": {k: str(p) for k, p in pngs.items()}, "cache": True, "metricas": previo.get("metricas", {})}
    p = puerto_libre({puerto})
    try:
        r = sesion_arranque(None, "audit-base-sony", p, BASE_SONY, "base", teclas, espera_max, hueco_max=120)
    except EntradaError as e:
        return {"pngs": {}, "cache": False, "metricas": {}, "error": str(e)}
    if r["pngs"]:
        meta.write_text(json.dumps({"firma": firma, "teclas": teclas, "metricas": r["metricas"], "coste_s": r["coste_s"]}))
    return {"pngs": {k: str(BASE_SONY / v) for k, v in r["pngs"].items()}, "cache": False,
            "metricas": r["metricas"], "coste_s": r["coste_s"], "error": r.get("error", "")}


def etapa_arranque(usr: dict[str, Any] | None, checks: list[dict[str, Any]], salida: Path, perfil: str,
                   puerto: int | None, teclas: str, espera_max: float) -> dict[str, Any]:
    """Etapa 4: arranque en frío del CFW y comparación con Sony de serie (mismas teclas)."""
    faltan = [n for n in ("vmlinuz", "base.cpio.gz", "stage/cam/usr") if not (TRABAJO / n).exists()]
    if not usr:
        add(checks, "arranque.overlay", False, "no hay /usr del CFW que superponer", 4)
        return {}
    faltan += [n for n in ("debugfs", "qemu-system-arm") if shutil.which(n) is None]
    add(checks, "arranque.artefactos", not faltan, f"faltan {faltan}" if faltan else "vmlinuz, base.cpio.gz y stage/cam/usr",
        4, material=bool(faltan))
    if faltan:
        return {}
    overlay = salida / f"overlay-{perfil}"
    shutil.rmtree(overlay, ignore_errors=True)
    (overlay / "cam/usr").mkdir(parents=True)  # un CFW sin cambios también debe dar un overlay válido a live.py
    for rel in usr["anadidos"] + usr["cambiados"]:
        destino = overlay / "cam/usr" / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(usr["dir_cfw"] / rel, destino)
    if usr.get("quitados"):
        add(checks, "arranque.quitados", None,
            f"el overlay no puede borrar {len(usr['quitados'])} ficheros de Sony: en QEMU seguirán presentes", 4,
            evidencia="NO_VERIFICADO")
    puerto_cfw = puerto or puerto_libre()
    try:
        r = sesion_arranque(overlay, perfil, puerto_cfw, salida, "cfw", teclas, espera_max)
    except EntradaError as e:
        add(checks, "arranque.no_arrancado", None, f"no se pudo arrancar (entorno): {e}", 4,
            evidencia="NO_VERIFICADO", material=True)
        return {}
    base = base_sony(salida, teclas, espera_max, puerto_cfw)
    r["base_sony"] = base
    if r.get("error"):
        add(checks, "arranque.sesion", False, f"la sesión falló: {r['error']}", 4)
    add(checks, "arranque.qemu_vivo", not r["qemu_murio"], "QEMU sigue vivo hasta el final" if not r["qemu_murio"]
        else "QEMU terminó antes de tiempo", 4)
    add(checks, "arranque.im_elf", not r["im_exit"], "im.elf no salió con IMEXIT" if not r["im_exit"]
        else "im.elf abortó (IMEXIT en consola.log)", 4)
    frames_ok = bool(r.get("primera") or r.get("pngs", {}).get("primera"))
    segundos = r.get("arranque_s", r.get("coste_s"))
    add(checks, "arranque.primera_pantalla", frames_ok,
        f"primera pantalla a los {segundos} s (más {r.get('espera_hueco_s', 0)} s de espera de hueco)"
        if frames_ok else f"0 fotogramas en {espera_max:.0f} s", 4)
    negro = [k for k, m in r.get("metricas", {}).items() if m["negro"]]
    add(checks, "arranque.pantalla_no_negra", frames_ok and not negro,
        f"capturas negras: {negro}" if negro else ("primera pantalla, menú y disparo con contenido" if frames_ok
                                                   else "no hay pantalla que analizar"), 4)
    add(checks, "arranque.menu_abre", bool(r.get("menu_abre")), "MENU cambió la pantalla" if r.get("menu_abre")
        else "MENU no cambió la pantalla en 45 s", 4)
    faltan_png = [p for p in ("primera", "menu", "disparo") if p not in r.get("pngs", {})]
    add(checks, "arranque.capturas", not faltan_png, f"faltan {faltan_png}" if faltan_png else "3 PNG guardados", 4)
    menu_base = base.get("pngs", {}).get("menu", "")
    if r.get("pngs", {}).get("menu") and menu_base and Path(menu_base).is_file():
        m = compara_png((salida / r["pngs"]["menu"]).read_bytes(), Path(menu_base).read_bytes())
        r["comparacion"] = m
        vacio = m.get("comparable") and m["no_fondo"][1] > 2000 and m["no_fondo"][0] < 0.2 * m["no_fondo"][1]
        add(checks, "arranque.menu_frente_sony", not vacio, f"píxeles con contenido CFW/Sony: {m.get('no_fondo')}; "
            f"distintos {m.get('fraccion_distinta')}", 4, evidencia="INFERENCIA",
            aviso=bool(m.get("fraccion_distinta", 0) > 0.5))
        add(checks, "arranque.comparacion_sony", True, f"{m}", 4, evidencia="INFERENCIA")
    else:
        add(checks, "arranque.comparacion_sony", None, "sin captura de Sony de serie con la que comparar", 4,
            evidencia="NO_VERIFICADO", material=True)
    log = Path(r.get("live_log", ""))
    if log.is_file() and re.search(r"arranque \d+/\d+ fallido", log.read_text(errors="replace")):
        add(checks, "arranque.reintentos", True, "el arranque necesitó un reintento (SEGV intermitente conocido)", 4,
            evidencia="INFERENCIA", aviso=True)
    return r


# ------------------------------------------------------------------------------------------------ auditoría
def nombres_teclas() -> set[str]:
    """Claves del literal TECLAS de live.py, sin importarlo (evita cargar numpy/PIL solo para validar)."""
    import ast
    try:
        for n in ast.parse((HERE / "live.py").read_text()).body:
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "TECLAS" for t in n.targets) \
                    and isinstance(n.value, ast.Dict):
                return {k.value for k in n.value.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
    except (OSError, SyntaxError):
        pass
    return set()


def artefactos_arranque() -> list[str]:
    faltan = [n for n in ("vmlinuz", "base.cpio.gz", "stage/cam/usr") if not (TRABAJO / n).exists()]
    faltan += [n for n in ("debugfs", "qemu-system-arm") if shutil.which(n) is None]
    return faltan


def arranque_disponible() -> bool:
    """¿Están el initramfs, el rootfs de la cámara y QEMU para la etapa 4?"""
    return not artefactos_arranque()


def prepara_overlay(ruta: Path, usr_sony: Path | None, checks: list[dict[str, Any]], tmp: Path,
                    decl: dict[str, Any]) -> dict[str, Any]:
    """Overlay (`cam/usr`) que representa el /usr completo del CFW: compara ficheros, sin TPZL."""
    sony = usr_sony
    if sony is None:
        s = _sony_n15()
        if s is None:
            raise EntradaError("falta el /usr de Sony (firmware/extracted/fw321/… o --usr-sony)")
        sony = extrae_usr(s.read_bytes(), tmp / "sony-usr", _deps()[3])
    add(checks, "usr.base_sony", sony.is_dir(), f"base Sony: {sony}", 2)
    return compara_usr(ruta / "cam/usr", sony, checks, decl)


def audita(ruta: Path, *, completo: bool = True, arranque: bool | None = None, salida: Path | None = None,
           perfil: str = "", puerto: int | None = None, teclas: str = "", declara: Path | None = None,
           usr_sony: Path | None = None, espera: float = 300.0) -> dict[str, Any]:
    """Audita un CFW y devuelve el informe. Lanza EntradaError si no se puede auditar (nunca un OK falso)."""
    t0 = time.time()
    ruta = ruta.expanduser().resolve()
    tipo = detecta_tipo(ruta)
    if puerto is not None and not PUERTO_MIN <= puerto <= PUERTO_MAX:
        raise EntradaError(f"--puerto {puerto} fuera de {PUERTO_MIN}–{PUERTO_MAX}")
    if teclas:
        desconocidas = sorted({t.strip() for t in teclas.split(",") if t.strip()} - nombres_teclas())
        if desconocidas:
            raise EntradaError(f"teclas desconocidas en --teclas: {desconocidas}")
    if shutil.which("debugfs") is None:
        raise EntradaError("falta debugfs (e2fsprogs): sin él no se puede extraer el /usr del nflasha15")
    sha, tam = huella(ruta, tipo)
    s8 = sha[:8]
    checks: list[dict[str, Any]] = []
    decl = carga_declaraciones(ruta, tipo, declara)
    explicita = salida is not None
    destino = (salida or (ARCH_CFW / f"audit-{s8}")).resolve()
    destino.mkdir(parents=True, exist_ok=True)
    r: dict[str, Any] = {"ruta": str(ruta), "tipo": tipo, "sha256": sha, "tamano": tam, "version": "",
                         "checks": checks, "veredicto": "", "fecha": ahora(), "coste_s": 0.0,
                         "declaracion": decl.get("_fuente", ""), "json": "", "markdown": ""}
    if not completo:
        add(checks, "modo.rapido", True, "solo contenedor y /USR (sin estructura ni arranque)", 0, evidencia="INFERENCIA")
    usr: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix=".tmp-audita-cfw-", dir=destino) as t:
        tmp = Path(t)
        imagen: bytes | None = None
        if tipo == "dat":
            try:
                extra = etapa_contenedor(ruta, checks, tmp)
            except EntradaError:
                raise
            except Exception as e:  # noqa: BLE001 - contenedor dañado: FALLO, no traza
                add(checks, "contenedor.excepcion", False, f"{type(e).__name__}: {e}", 1)
                extra = {}
            r["version"] = extra.get("version", "")
            imagen = extra.get("n15")
        else:
            add(checks, "contenedor.no_aplica", None,
                f"{tipo}: no hay contenedor .dat que auditar (se audita el /usr y el arranque)", 1,
                evidencia="NO_VERIFICADO")
            r["version"] = decl.get("version", "") or "desconocida"
            if tipo in ("nflasha15", "paquete"):
                p = ruta_imagen(ruta, tipo)
                imagen = p.read_bytes() if p is not None else None
        otro_modelo = any(c["id"] == "contenedor.modelo_a6000" and c["ok"] is False for c in checks)
        if tipo == "overlay":
            usr = prepara_overlay(ruta, usr_sony, checks, tmp, decl)
        elif otro_modelo:
            add(checks, "usr.no_aplica", None,
                "el .dat no es de la A6000: comparar su /usr con el de Sony 3.21 no diría nada", 2,
                evidencia="NO_VERIFICADO")
        elif imagen is not None:
            try:
                usr = etapa_usr(imagen, usr_sony, checks, tmp, decl)
            except EntradaError:
                raise
            except Exception as e:  # noqa: BLE001 - ext2/TPZL dañado: FALLO
                add(checks, "usr.extraccion", False, f"no se pudo extraer el /usr del CFW: {type(e).__name__}: {e}", 2)
        else:
            add(checks, "usr.no_disponible", False, "no hay nflasha15 que extraer (contenedor inválido o sin partición /usr)", 2)
        r["usr"] = {k: usr.get(k, []) for k in ("anadidos", "cambiados", "quitados", "sin_justificar")}
        r["usr"]["hashes"] = {k: usr.get("mapa_cfw", {}).get(k, "") for k in usr.get("anadidos", []) + usr.get("cambiados", [])}
        if usr and completo:
            try:
                r["estructura"] = etapa_estructura(usr, checks, decl, tmp)
            except Exception as e:  # noqa: BLE001 - un recurso dañado no debe impedir el informe
                add(checks, "estructura.excepcion", False, f"{type(e).__name__}: {e}", 3)
        if completo:
            faltan = artefactos_arranque()
            if arranque is True and faltan:
                raise EntradaError(f"--arranque pedido pero faltan artefactos del arnés: {faltan}")
            if arranque is None:
                arranque = bool(usr) and not faltan
            if arranque and usr:
                r["arranque"] = etapa_arranque(usr, checks, destino, perfil or f"audit-{s8}", puerto, teclas, espera)
            else:
                detalle = ("--sin-arranque" if faltan == [] else f"faltan {faltan}")
                add(checks, "arranque.omitido", None,
                    f"el arranque NO se ha probado ({detalle})", 4, evidencia="NO_VERIFICADO",
                    material=bool(arranque is not False and not faltan))
        elif arranque:
            add(checks, "arranque.omitido", None, "--rapido no ejecuta el arranque", 4, evidencia="NO_VERIFICADO")
    r["veredicto"] = veredicto(checks)
    r["coste_s"] = round(time.time() - t0, 1)
    r["json"], r["markdown"] = escribe_informes(r, destino, explicita)
    return r


# ------------------------------------------------------------------------------------------------ informes
def escribe_informes(r: dict[str, Any], salida: Path, explicita: bool) -> tuple[str, str]:
    s8 = r["sha256"][:8]
    if explicita:
        destino_json = salida / f"audit-{dia()}-{s8}.json"
        destino_md = salida / f"{s8}.md"
    else:
        destino_json = ARCH_CFW / f"audit-{dia()}-{s8}.json"
        destino_md = ARCH_DOCS / f"{s8}.md"
    destino_json.parent.mkdir(parents=True, exist_ok=True)
    destino_md.parent.mkdir(parents=True, exist_ok=True)
    destino_json.write_text(json.dumps(r, indent=1, ensure_ascii=False))
    destino_md.write_text(informe_markdown(r))
    return str(destino_json), str(destino_md)


def informe_markdown(r: dict[str, Any]) -> str:
    lineas = [f"# Auditoría CFW {r['version']} — `{r['sha256'][:8]}`", "",
              f"- Artefacto: `{r['ruta']}` ({r['tipo']})", f"- SHA-256: `{r['sha256']}`",
              f"- Fecha: {r['fecha']}", f"- Coste: {r['coste_s']} s",
              f"- Declaración: `{r['declaracion'] or 'ninguna'}`", f"- **Veredicto: {r['veredicto']}**", "",
              "| Etapa | Comprobación | Resultado | Evidencia | Detalle |", "|---|---|---|---|---|"]
    for c in r["checks"]:
        estado = "AVISO" if c["aviso"] and c["ok"] is not False else SYM[c["ok"]]
        detalle = str(c["detalle"]).replace("|", "\\|")[:220]
        lineas.append(f"| {c['etapa']} | `{c['id']}` | {estado} | {c['evidencia']} | {detalle} |")
    u = r.get("usr") or {}
    if u:
        lineas += ["", "## /usr frente a Sony", "",
                   f"- Añadidos ({len(u.get('anadidos', []))}): {', '.join(f'`{x}`' for x in u.get('anadidos', [])[:30]) or '—'}",
                   f"- Cambiados ({len(u.get('cambiados', []))}): {', '.join(f'`{x}`' for x in u.get('cambiados', [])[:30]) or '—'}",
                   f"- Quitados ({len(u.get('quitados', []))}): {', '.join(f'`{x}`' for x in u.get('quitados', [])[:30]) or '—'}"]
    if r.get("arranque"):
        a = r["arranque"]
        lineas += ["", "## Arranque en el arnés", "",
                   f"- Perfil `{a.get('perfil')}`, puerto {a.get('puerto')}, coste {a.get('coste_s')} s",
                   f"- Capturas: {', '.join(sorted(a.get('pngs', {}))) or 'ninguna'}",
                   f"- Comparación con Sony: {a.get('comparacion', 'no disponible')}"]
    lineas += ["", "## Límites", "",
               "Emulación de la UI con un kernel ajeno y el shim: un OK aquí no demuestra el comportamiento en cámara.",
               "Loader2/3, Darwin, el hardware y las tablas de recursos que no se declaren siguen siendo riesgo de cámara.",
               "Los ids de Backup/NVRAM solo se comprueban si el CFW los declara; si no, quedan NO VERIFICADOS.", ""]
    return "\n".join(lineas)


def imprime_consola(r: dict[str, Any]) -> None:
    print(f"AUDITORÍA CFW — {r['ruta']}")
    print(f"  tipo {r['tipo']} · versión {r['version']} · sha256 {r['sha256']} · {r['coste_s']} s")
    etapa = None
    for c in r["checks"]:
        if c["etapa"] != etapa:
            etapa = c["etapa"]
            titulo = {0: "MODO", 1: "CONTENEDOR", 2: "/USR", 3: "ESTRUCTURA", 4: "ARRANQUE"}.get(etapa, str(etapa))
            print(f"\n[{etapa}] {titulo}")
        marca = "✗" if c["ok"] is False else ("⚠" if c["aviso"] else ("·" if c["ok"] is None else "✓"))
        print(f"  {marca} {c['id']}: {c['detalle']}" + (f"  [{c['evidencia']}]" if c["evidencia"] != "VERIFICADO" else ""))
    n = {k: sum(1 for c in r["checks"] if c["ok"] is k) for k in (True, False, None)}
    print(f"\nVEREDICTO: {r['veredicto']}  ({n[True]} ok, {n[False]} fallos, {n[None]} no verificados)")
    if r.get("json"):
        print(f"Informe: {r['json']}\nResumen: {r['markdown']}")


# ------------------------------------------------------------------------------------------------ lote
def descubre_lote(directorio: Path) -> list[Path]:
    vistos: list[Path] = []
    for p in sorted(directorio.rglob("*")):
        if p.is_file() and p.name.endswith(".dat") and p.stat().st_size > 1 << 20:
            with p.open("rb") as f:
                if f.read(8) == DAT_MAGIC:
                    vistos.append(p)
        elif p.is_file() and p.name in ("nflasha15", "nflasha15.bin"):
            with p.open("rb") as f:
                if f.read(4) == b"TPZL" and p.parent not in vistos:
                    vistos.append(p.parent)
        elif p.is_dir() and p.parent == directorio and (p / "cam/usr").is_dir():
            vistos.append(p)
    paquetes = {p for p in vistos if p.is_dir()}
    return [p for p in vistos if not (p.is_file() and p.parent in paquetes)]


def audita_lote(directorio: Path, *, completo: bool, arranque: bool | None, salida: Path | None, declara: Path | None,
                usr_sony: Path | None, teclas: str, espera: float, puerto: int | None) -> dict[str, Any]:
    items = descubre_lote(directorio)
    if not items:
        raise EntradaError(f"{directorio}: no se encontró ningún .dat, paquete con nflasha15 ni overlay cam/usr")
    destino = (salida or ARCH_CFW).resolve()
    destino.mkdir(parents=True, exist_ok=True)
    index: dict[str, Any] = {"fecha": ahora(), "directorio": str(directorio), "items": []}
    for p in items:
        try:
            r = audita(p, completo=completo, arranque=arranque, salida=destino, puerto=puerto, teclas=teclas,
                       declara=declara, usr_sony=usr_sony, espera=espera)
            index["items"].append({"ruta": r["ruta"], "sha256": r["sha256"], "sha8": r["sha256"][:8],
                                   "version": r["version"], "veredicto": r["veredicto"], "coste_s": r["coste_s"],
                                   "json": r["json"], "fallos": [c["id"] for c in r["checks"] if c["ok"] is False]})
        except EntradaError as e:
            index["items"].append({"ruta": str(p), "sha256": "", "sha8": "", "version": "",
                                   "veredicto": "ERROR", "coste_s": 0.0, "error": str(e)})
    destino_json = destino / f"audit-lote-{dia()}.json"
    destino_md = (ARCH_DOCS if destino == ARCH_CFW else destino) / f"lote-{dia()}.md"
    destino_md.parent.mkdir(parents=True, exist_ok=True)
    destino_json.write_text(json.dumps(index, indent=1, ensure_ascii=False))
    lineas = [f"# Lote de auditorías CFW — {index['fecha']}", "", f"Directorio: `{directorio}`", "",
              "| CFW | Versión | SHA-256 | Veredicto | Fallos | Coste |", "|---|---|---|---|---|---|"]
    for it in index["items"]:
        lineas.append(f"| {Path(it['ruta']).name} | {it.get('version', '')} | `{it.get('sha8', '')}` | "
                      f"{it['veredicto']} | {', '.join(it.get('fallos', [])) or it.get('error', '')} | {it.get('coste_s', '')} s |")
    destino_md.write_text("\n".join(lineas) + "\n")
    index["json"], index["markdown"] = str(destino_json), str(destino_md)
    return index


# ------------------------------------------------------------------------------------------------ CLI
def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ruta", type=Path, help=".dat, directorio de paquete, nflasha15.bin o directorio con --lote")
    ap.add_argument("--lote", action="store_true", help="audita todos los CFW del directorio y genera un índice")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--completo", dest="completo", action="store_true", default=True, help="etapas 1–4 (por defecto)")
    g.add_argument("--rapido", dest="completo", action="store_false", help="solo contenedor y /USR")
    b = ap.add_mutually_exclusive_group()
    b.add_argument("--arranque", dest="arranque", action="store_true", help="prueba el arranque en QEMU (por defecto si hay artefactos)")
    b.add_argument("--sin-arranque", dest="arranque", action="store_false", help="no arranca QEMU")
    ap.set_defaults(arranque=None)
    ap.add_argument("--salida", type=Path, help="directorio de informes, capturas y overlay (por defecto analysis/gui/g22)")
    ap.add_argument("--perfil-dir", default="", help="perfil propio del arnés (por defecto audit-<sha8>)")
    ap.add_argument("--puerto", type=int, help=f"puerto de live.py ({PUERTO_MIN}–{PUERTO_MAX}; por defecto, libre)")
    ap.add_argument("--json", action="store_true", help="solo JSON por stdout")
    ap.add_argument("--teclas", default="", help="secuencia extra de teclas separadas por comas (menu,intro,derecha,…)")
    ap.add_argument("--declara", type=Path, help="JSON con lo que declara el CFW (nuevos/parcheados/quitados/parches/recursos/nvram)")
    ap.add_argument("--usr-sony", type=Path, help="/usr de Sony ya extraído con el que comparar (por defecto el 3.21 del repo)")
    ap.add_argument("--espera", type=float, default=float(os.environ.get("AUDITA_ESPERA", "300")),
                    help="tope de espera de la primera pantalla en segundos (por defecto 300)")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = _parser().parse_args(argv)
    try:
        if a.lote:
            if not a.ruta.is_dir():
                raise EntradaError("--lote necesita un directorio")
            idx = audita_lote(a.ruta, completo=a.completo, arranque=a.arranque, salida=a.salida, declara=a.declara,
                              usr_sony=a.usr_sony, teclas=a.teclas, espera=a.espera, puerto=a.puerto)
            if a.json:
                print(json.dumps(idx, indent=1, ensure_ascii=False))
            else:
                print(f"Lote de {len(idx['items'])} CFW — {idx['fecha']}")
                for it in idx["items"]:
                    print(f"  {it['veredicto']:<8} {Path(it['ruta']).name} ({it.get('version', '?')}, {it.get('sha8', '')})")
                print(f"Índice: {idx['json']}\nTabla: {idx['markdown']}")
            return 1 if any(it["veredicto"] in ("FALLO", "ERROR") for it in idx["items"]) else 0
        r = audita(a.ruta, completo=a.completo, arranque=a.arranque, salida=a.salida, perfil=a.perfil_dir,
                   puerto=a.puerto, teclas=a.teclas, declara=a.declara, usr_sony=a.usr_sony, espera=a.espera)
    except EntradaError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, indent=1, ensure_ascii=False))
    else:
        imprime_consola(r)
    return codigo_salida(r)


if __name__ == "__main__":
    sys.exit(main())
