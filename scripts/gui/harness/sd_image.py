#!/usr/bin/env python3
"""Imagen FAT32 de la SD emulada (G22-E): carpeta de sd_emu.py → imagen «cabeza» (solo hasta el último dato, el resto son ceros) + nº total de sectores.

La SD de la A6000 (SDHC ≤ 32 GB) es FAT32 sin tabla de particiones (supertrozo, norma SD); `libInfraFsys` la lee con su propio FAT (PrFILE), sin kernel vfat.
El invitado recrea el disco completo con `ftruncate` (hueco disperso en tmpfs) y copia encima la cabeza (shim, `/dev/mmca`).
Uso: sd_image.py CARPETA SALIDA.head [tamaño_GB=4]  → imprime los sectores totales.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ETIQUETA = "A6000SD"  # NO_VERIFICADO: la cámara pone «NO_NAME» o la etiqueta del formateo; solo es cosmético
CARPETAS = ("DCIM", "DCIM/100MSDCF", "PRIVATE", "PRIVATE/M4ROOT", "PRIVATE/M4ROOT/CLIP", "PRIVATE/AVCHD")  # estructura base de la A6000 (sd_emu.py, docs del repo)
# Carpetas que libmpr nombra en el código (cadenas `\\PRIVATE\\M4ROOT\\{CLIP,SUB,THMBNL,GENERAL}` de xavcIfo_DbDirMngr, +0x947c8a; `AVF_INFO` del índice AV, +0x7a637f). VERIFICADO como nombres;
# NO_VERIFICADO que la cámara las cree vacías ni que su falta cause el «ERROR» de la OSD: por eso solo con completa=True (opt-in, SD_ESTRUCTURA=1 en live.py).
CARPETAS_CODIGO = ("PRIVATE/M4ROOT/SUB", "PRIVATE/M4ROOT/THMBNL", "PRIVATE/M4ROOT/GENERAL", "AVF_INFO")
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


def construye(raiz: Path, salida: Path, tamano_gb: float = 4.0, completa: bool = False) -> int:
    """Crea la imagen y escribe la cabeza en `salida`; devuelve los sectores totales (512 B)."""
    sectores = int(tamano_gb * (1 << 30)) // 512
    with tempfile.TemporaryDirectory() as t:
        img = Path(t) / "sd.img"
        with img.open("wb") as f:
            f.truncate(sectores * 512)
        subprocess.run(["mkfs.vfat", "-F", "32", "-n", ETIQUETA, "-S", "512", str(img)], check=True, capture_output=True)
        env = {**os.environ, "MTOOLS_SKIP_CHECK": "1"}
        for c in CARPETAS + (CARPETAS_CODIGO if completa else ()):
            subprocess.run(["mmd", "-i", str(img), "-D", "s", f"::{c}"], check=True, capture_output=True, env=env)
        if raiz.is_dir():
            for sub in sorted(p for p in raiz.iterdir() if p.is_dir()):
                subprocess.run(["mcopy", "-i", str(img), "-s", "-m", "-Q", str(sub), "::"], check=False, capture_output=True, env=env)
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
    print(construye(Path(sys.argv[1]).expanduser(), Path(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 4.0))
