"""G22-REPRO — estructura del árbol FAT32 que recibe el invitado (`sd_image.py`), sin QEMU.

Comprueba lo que se puede medir en el anfitrión: qué entradas crea `construye`, que `mkfs.vfat`/`mmd`/`mcopy` las aceptan y que los ficheros del
índice AV (`AVF_INFO/AVIN0001.*`, `PRV00001.BIN`) existen con 0 B —contenido no inventado— cuando se pide la estructura completa (`SD_ESTRUCTURA=1`).
El resto (que la cámara los lea y monte el volumen) es medición en el invitado: ver `docs/gui/g22-repro-reproduccion-sd.md`.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/harness"))

import sd_image

FALTA = [h for h in ("mkfs.vfat", "mmd", "mcopy", "mdir") if shutil.which(h) is None]
pytestmark = pytest.mark.skipif(bool(FALTA), reason=f"faltan herramientas mtools/dosfstools: {', '.join(FALTA)}")
MT = {"MTOOLS_SKIP_CHECK": "1"}


def mdir(img: Path, ruta: str) -> str:
    r = subprocess.run(["mdir", "-i", str(img), "-/", ruta], check=False, capture_output=True, text=True, env={**MT, "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"})
    assert r.returncode == 0, r.stderr
    return r.stdout


def cabeza(tmp_path: Path, completa: bool) -> Path:
    """Imagen pequeña (256 MiB) con una foto en DCIM/100MSDCF y la estructura pedida."""
    raiz = tmp_path / "sd"
    (raiz / "DCIM" / "100MSDCF").mkdir(parents=True)
    (raiz / "DCIM" / "100MSDCF" / "DSC00001.JPG").write_bytes(b"\xff\xd8\xff\xe0" + bytes(120))
    salida = tmp_path / ("completa.head" if completa else "base.head")
    sectores = sd_image.construye(raiz, salida, 0.25, completa=completa)
    assert sectores == (0.25 * (1 << 30)) // 512
    assert salida.stat().st_size > 0
    return salida


def test_entradas_sin_estructura_es_la_tarjeta_base() -> None:
    carpetas, ficheros = sd_image.entradas(False)
    assert ficheros == ()
    assert "DCIM/100MSDCF" in carpetas and "PRIVATE/M4ROOT" in carpetas
    assert "AVF_INFO" not in carpetas and "MP_ROOT" not in carpetas


def test_entradas_con_estructura_anade_lo_que_nombra_el_binario() -> None:
    carpetas, ficheros = sd_image.entradas(True)
    for c in ("AVF_INFO", "MP_ROOT", "PRIVATE/M4ROOT/SUB", "PRIVATE/M4ROOT/THMBNL", "PRIVATE/M4ROOT/GENERAL"):
        assert c in carpetas
    assert ficheros == ("AVF_INFO/AVIN0001.INP", "AVF_INFO/AVIN0001.BNP", "AVF_INFO/AVIN0001.INT", "AVF_INFO/PRV00001.BIN",
                        "AVF_INFO/STAT0000.BIN")  # STAT0000.BIN: medido con Fsys_FindFirst en el invitado (G22-REPRO)
    # sin la estructura completa no se crea ni un fichero: el árbol mínimo no cambia de comportamiento
    assert sd_image.entradas(False)[1] == ()


def test_imagen_base_tiene_la_foto_y_no_tiene_avf_info(tmp_path: Path) -> None:
    img = cabeza(tmp_path, completa=False)
    raiz = mdir(img, "::/")
    assert "DCIM" in raiz and "PRIVATE" in raiz
    assert "AVF_INFO" not in raiz
    carpeta = mdir(img, "::/DCIM/100MSDCF")
    assert "DSC00001 JPG" in carpeta


def test_imagen_completa_lleva_avf_info_vacio_y_mp_root(tmp_path: Path) -> None:
    img = cabeza(tmp_path, completa=True)
    raiz = mdir(img, "::/")
    assert "AVF_INFO" in raiz and "MP_ROOT" in raiz
    avf = mdir(img, "::/AVF_INFO")
    for nombre in ("AVIN0001 INP", "AVIN0001 BNP", "AVIN0001 INT", "PRV00001 BIN", "STAT0000 BIN"):
        assert nombre in avf, avf
    # 0 B a propósito: el contenido del índice AV no está en el repo y no se inventa
    for linea in avf.splitlines():
        if linea.split() and linea.split()[0].startswith(("AVIN0001", "PRV00001", "STAT0000")):
            assert linea.split()[-3] == "0" or " 0 " in linea, linea
    assert "100ANV01" in mdir(img, "::/MP_ROOT")
    assert "DSC00001 JPG" in mdir(img, "::/DCIM/100MSDCF")  # la foto del anfitrión sigue copiándose


def test_imagen_completa_admite_ficheros_del_anfitrion_en_avf_info(tmp_path: Path) -> None:
    """Si el anfitrión pone ficheros en AVF_INFO de su carpeta, mcopy -s los copia encima del árbol (no rompe el orden mmd → mcopy)."""
    raiz = tmp_path / "sd"
    (raiz / "AVF_INFO").mkdir(parents=True)
    (raiz / "AVF_INFO" / "AVIN0001.INP").write_bytes(bytes(0x80))
    salida = tmp_path / "x.head"
    sd_image.construye(raiz, salida, 0.25, completa=True)
    assert "AVIN0001 INP       128" in mdir(salida, "::/AVF_INFO")
