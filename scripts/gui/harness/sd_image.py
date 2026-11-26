#!/usr/bin/env python3
"""Imagen FAT32 de la SD emulada (G22-E): carpeta de sd_emu.py → imagen «cabeza» (solo hasta el último dato, el resto son ceros) + nº total de sectores.

La SD de la A6000 (SDHC ≤ 32 GB) es FAT32 sin tabla de particiones (supertrozo, norma SD); `libInfraFsys` la lee con su propio FAT (PrFILE), sin kernel vfat.
El invitado recrea el disco completo con `ftruncate` (hueco disperso en tmpfs) y copia encima la cabeza (shim, `/dev/mmca`).
Uso: sd_image.py CARPETA SALIDA.head [tamaño_GB=4 [completa]]  → imprime los sectores totales.

`completa` (opt-in, `SD_ESTRUCTURA=1` en live.py) añade la estructura que `libmpr` nombra pero el árbol mínimo no traía (G22-E-1g/G22-REPRO,
[g22-avcam-puente §5.51](../docs/gui/g22-avcam-puente.md)): `AVF_INFO` con sus cuatro ficheros y `MP_ROOT/100ANV01`. Los ficheros de índice se crean
**vacíos** a propósito: su contenido real no existe en el repo (no hay volcado de una SD de la A6000), así que no se inventa ni un byte; la cámara
los lee como «no hay índice» y los crea/registra ella misma por el mismo `/dev/mmca` (que admite escritura). Qué exige cada nombre y por qué está en
`AVF_INFO_FICHEROS`/`CARPETAS_CODIGO`.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import sd_media

ETIQUETA = "A6000SD"  # NO_VERIFICADO: la cámara pone «NO_NAME» o la etiqueta del formateo; solo es cosmético
CARPETAS = ("DCIM", "DCIM/100MSDCF", "PRIVATE", "PRIVATE/M4ROOT", "PRIVATE/M4ROOT/CLIP", "PRIVATE/AVCHD")  # estructura base de la A6000 (sd_emu.py, docs del repo)
# Carpetas que el firmware nombra en su código: `\\PRIVATE\\M4ROOT\\{CLIP,SUB,THMBNL,GENERAL}` de xavcIfo_DbDirMngr (libmpr+0x947c8a), `AVF_INFO` del índice AV
# (libmpr+0x7a637f) y `MP_ROOT` (libmpr+0x7a743a/0x7a7ac1; en la tarjeta real del 25-11 los MP4 estaban en `MP_ROOT/100ANV01`, `MP_ROOT/103ANV01`).
# VERIFICADO como nombres (cadena + xref); NO_VERIFICADO que la cámara las cree vacías.
CARPETAS_CODIGO = ("PRIVATE/M4ROOT/SUB", "PRIVATE/M4ROOT/THMBNL", "PRIVATE/M4ROOT/GENERAL", "AVF_INFO", "MP_ROOT", "MP_ROOT/100ANV01")
# Ficheros del índice AV: los tres `AVIN0001.*` son las tablas `.data` 0x9D1270 y 0x9D12C0 de libmpr (VERIFICADO: nombre + descriptor); `PRV00001.BIN` es el
# que pide `Fsys_FindFirst("ms:/AVF_INFO")`/`…/PRV00001.BIN` (§5.51, MEDIDO). Se crean de 0 B: existencia sin contenido inventado.
# `STAT0000.BIN` lo pide el propio firmware al montar el volumen (MEDIDO: `Fsys_FindFirst("ms:/AVF_INFO/STAT0000.BIN")`, G22-REPRO); sin él la consulta se queda en AVF_INFO.
AVF_INFO_FICHEROS = ("AVF_INFO/AVIN0001.INP", "AVF_INFO/AVIN0001.BNP", "AVF_INFO/AVIN0001.INT", "AVF_INFO/PRV00001.BIN", "AVF_INFO/STAT0000.BIN")
MAX_CABEZA = 256 << 20


def ultimo_dato(f: int, tam: int) -> int:
    fin, pos = 0, 0
    while pos < tam:
        try:
            ini = os.lseek(f, pos, os.SEEK_DATA)
        except OSError:
            break
        pos = os.lseek(f, ini, os.SEEK_HOLE)
        fin = pos
    return fin


def entradas(completa: bool = False, media: bool = False) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(carpetas, ficheros) que crea `construye` antes de copiar la carpeta del anfitrión (que va aparte, con `mcopy -s`).

    `media` (SD_MEDIA=1, G22-PBMEDIA) implica `completa` y **no** deja el índice vacío: `sd_media.py` escribe
    `AVIN0001.INP/.BNP` con una entrada real y una foto JPEG de verdad en `DCIM/100MSDCF`.
    """
    if media:
        return CARPETAS + CARPETAS_CODIGO, ()
    return CARPETAS + (CARPETAS_CODIGO if completa else ()), AVF_INFO_FICHEROS if completa else ()


def construye(raiz: Path, salida: Path, tamano_gb: float = 4.0, completa: bool = False, media: bool = False) -> int:
    """Crea la imagen y escribe la cabeza en `salida`; devuelve los sectores totales (512 B)."""
    sectores = int(tamano_gb * (1 << 30)) // 512
    carpetas, ficheros = entradas(completa, media)
    with tempfile.TemporaryDirectory() as t:
        img = Path(t) / "sd.img"
        with img.open("wb") as f:
            f.truncate(sectores * 512)
        subprocess.run(["mkfs.vfat", "-F", "32", "-n", ETIQUETA, "-S", "512", str(img)], check=True, capture_output=True)
        env = {**os.environ, "MTOOLS_SKIP_CHECK": "1"}
        for c in carpetas:
            subprocess.run(["mmd", "-i", str(img), "-D", "s", f"::{c}"], check=True, capture_output=True, env=env)
        vacio = Path(t) / "vacio"  # 0 B: el contenido del índice AV no está en el repo, no se inventa
        vacio.write_bytes(b"")
        for n in ficheros:
            subprocess.run(["mcopy", "-i", str(img), "-m", "-Q", str(vacio), f"::{n}"], check=True, capture_output=True, env=env)
        if media:  # foto real + índice AV coherente con ella (opt-in: no toca los arranques que ya funcionan)
            med = Path(t) / "media"
            mapa = sd_media.construye(med)
            for sub in sorted(p for p in med.iterdir() if p.is_dir()):
                subprocess.run(["mcopy", "-i", str(img), "-s", "-m", "-Q", "-o", str(sub), "::"], check=True, capture_output=True, env=env)
            if os.environ.get("SD_MEDIA_MAPA"):  # evidencia: qué se ha metido y con qué formato
                print(f"SD_MEDIA {mapa}", file=sys.stderr)
        if raiz.is_dir():
            for sub in sorted(p for p in raiz.iterdir() if p.is_dir()):
                subprocess.run(["mcopy", "-i", str(img), "-s", "-m", "-Q", "-o", str(sub), "::"], check=False, capture_output=True, env=env)
        fd = os.open(img, os.O_RDONLY)
        try:
            fin = min(((ultimo_dato(fd, sectores * 512) + 4095) // 4096) * 4096, sectores * 512)
            if fin > MAX_CABEZA:
                raise SystemExit(f"la cabeza de la imagen ({fin >> 20} MiB) supera {MAX_CABEZA >> 20} MiB: demasiados ficheros en {raiz}")
            salida.write_bytes(os.pread(fd, fin, 0))
        finally:
            os.close(fd)
    return sectores


if __name__ == "__main__":
    print(construye(Path(sys.argv[1]).expanduser(), Path(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 4.0,
                    "completa" in sys.argv[4:], "media" in sys.argv[4:]))
