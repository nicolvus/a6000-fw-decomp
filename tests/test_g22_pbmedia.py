"""G22-PBMEDIA — el índice AV de la SD emulada (`sd_media.py`) y su cableado en `sd_image.py`, sin QEMU.

Lo que se comprueba aquí es la **estructura** que este cambio genera: tamaño de registro (0x80), offsets de
cada campo dentro del registro, cabecera, recuento derivado del tamaño y coherencia con el JPEG real que se
mete en `DCIM/100MSDCF`. Que la cámara lo acepte (`getModelInfo(model/MEDIA, 0) -> 1`) es medición en el
invitado: `docs/gui/g22-pbmedia-indice-avf.md`.

Los bytes del formato salen del descriptor `.data` `0x9d1270` de `libmpr.so` (registro 0x80 en +0x10, máximo
0x2710 en +0x14, file ID en +0x28) y del volcado de campos de `libmpr` 0x1de066 (cDirPath `+0xb8`,
cFileName `+0xca`, nFileSize `+0xd8` ⇒ Δ 0x12/0x0e/0x20). El test 6 lee ese descriptor del binario cuando
está disponible, para que el generador no se separe de la evidencia.
"""
from __future__ import annotations

import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/harness"))

import sd_image
import sd_media

HARNESS_LIBMPR = ROOT / "analysis/gui/g22/harness/stage/cam/usr/lib/libmpr.so"
FW_LIBMPR = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so"
LIBMPR = HARNESS_LIBMPR if HARNESS_LIBMPR.exists() else FW_LIBMPR
DESCRIPTOR = 0x9D1270  # .data de libmpr: descriptor de AVIN0001.INP
MT = {"MTOOLS_SKIP_CHECK": "1"}
FALTA = [h for h in ("mkfs.vfat", "mmd", "mcopy", "mdir", "mtype") if shutil.which(h) is None]


def test_registro_de_0x80_con_los_campos_en_su_offset():
    r = sd_media.registro("DCIM/100MSDCF", "DSC00001.JPG", 0x1234, 1616, 1080, ms=0, n90k=0, codec=0, perfil=0)
    assert len(r) == sd_media.REGISTRO == 0x80
    assert r[0x00:0x0D] == b"DCIM/100MSDCF"  # cDirPath en +0x00, máx 0x12
    assert r[0x12:0x1E] == b"DSC00001.JPG"  # cFileName en +0x12, máx 0x0E
    assert struct.unpack_from("<I", r, 0x20)[0] == 0x1234  # nFileSize
    assert r[0x24] == 1  # bIsValid
    assert struct.unpack_from("<I", r, 0x28)[0] == 1616  # nWidth
    assert struct.unpack_from("<I", r, 0x2C)[0] == 1080  # nHeight
    assert r[0x1E:0x20] == b"\0\0" and r[0x25:0x28] == b"\0\0\0"  # relleno a cero entre campos


def test_registro_trunca_los_nombres_al_tamano_del_campo():
    r = sd_media.registro("D" * 40, "N" * 40, 1, 2, 3)
    assert r[0x00:0x12] == b"D" * 0x12  # cDirPath corta en 0x12, no invade cFileName
    assert r[0x12:0x20] == b"N" * 0x0E  # cFileName corta en 0x0E, no invade nFileSize


def test_indice_cabecera_mas_registros_y_id_del_descriptor():
    regs = [sd_media.registro("DCIM/100MSDCF", f"DSC0000{i}.JPG", 10 * i, 4, 3) for i in (1, 2, 3)]
    d = sd_media.avin(regs)
    assert len(d) == sd_media.CABECERA + 3 * sd_media.REGISTRO  # el recuento lo da el tamaño
    assert d[:16] == sd_media.ID  # file ID del descriptor (+0x28)
    assert d[sd_media.CABECERA:sd_media.CABECERA + 0x0D] == b"DCIM/100MSDCF"
    c = sd_media.CABECERA
    assert d[c + sd_media.REGISTRO:c + 2 * sd_media.REGISTRO][0x12:0x1E] == b"DSC00002.JPG"  # el 2.º registro empieza justo tras el 1.º
    # cabecera configurable (para probar la hipótesis en el invitado) y cabecera sin ID
    assert len(sd_media.avin(regs, cabecera=0)) == 3 * sd_media.REGISTRO
    assert sd_media.avin(regs, id_=b"")[:16] == bytes(16)


def test_construye_es_coherente_con_el_jpeg(tmp_path: Path):
    mapa = sd_media.construye(tmp_path)
    foto = tmp_path / mapa["foto"]
    datos = foto.read_bytes()
    assert datos[:2] == b"\xff\xd8"  # JPEG de verdad
    assert mapa["foto_bytes"] == len(datos)
    ancho, alto = sd_media.tamano_jpeg(datos)
    assert (mapa["ancho"], mapa["alto"]) == (ancho, alto) and ancho > 0
    indice = (tmp_path / "AVF_INFO/AVIN0001.INP").read_bytes()
    assert indice == (tmp_path / "AVF_INFO/AVIN0001.BNP").read_bytes()  # primario y respaldo iguales
    assert len(indice) == mapa["indice_bytes"] == mapa["cabecera"] + mapa["registros"] * sd_media.REGISTRO
    reg = indice[mapa["offset_registro0"]:mapa["offset_registro0"] + sd_media.REGISTRO]
    assert reg[0x00:0x0D] == b"DCIM/100MSDCF"
    assert reg[0x12:0x1E] == b"DSC00001.JPG"
    assert struct.unpack_from("<I", reg, 0x20)[0] == len(datos)  # tamaño del fichero que hay en la SD
    assert struct.unpack_from("<I", reg, 0x28)[0] == ancho
    for vacio in ("AVIN0001.INT", "PRV00001.BIN", "STAT0000.BIN"):
        assert (tmp_path / "AVF_INFO" / vacio).stat().st_size == 0  # sin contenido inventado


def test_construye_admite_una_foto_del_repo_con_exif():
    foto = sd_media.busca_foto()
    if foto is None:
        pytest.skip("no hay ninguna foto JPEG en el repo")
    assert foto.suffix.lower() in (".jpg", ".jpeg")
    assert sd_media.exif(foto.read_bytes()[:0x20000])


def test_sd_image_media_implica_estructura_y_no_deja_el_indice_vacio():
    carpetas, ficheros = sd_image.entradas(completa=False, media=True)
    assert "AVF_INFO" in carpetas and "MP_ROOT/100ANV01" in carpetas
    assert ficheros == ()  # los escribe sd_media, no la lista vacía
    carpetas2, ficheros2 = sd_image.entradas(completa=True)
    assert set(carpetas2) <= set(carpetas)  # SD_MEDIA no quita nada de SD_ESTRUCTURA
    assert ficheros2 == sd_image.AVF_INFO_FICHEROS  # sin SD_MEDIA sigue creándolos de 0 B
    assert sd_image.entradas() == (sd_image.CARPETAS, ())  # por defecto, sin cambios


@pytest.mark.skipif(bool(FALTA), reason=f"faltan herramientas mtools/dosfstools: {', '.join(FALTA)}")
def test_imagen_fat_con_media_lleva_la_foto_y_el_indice(tmp_path: Path):
    vacia = tmp_path / "sd_vacia"
    vacia.mkdir()
    salida = tmp_path / "media.head"
    sectores = sd_image.construye(vacia, salida, 0.25, media=True)
    assert sectores == (0.25 * (1 << 30)) // 512

    def mdir(ruta: str) -> str:
        r = subprocess.run(["mdir", "-i", str(salida), "-/", ruta], check=False, capture_output=True, text=True,
                           env={**MT, "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"})
        assert r.returncode == 0, r.stderr
        return r.stdout

    assert "DSC00001 JPG" in mdir("::/DCIM/100MSDCF")
    assert "AVIN0001 INP" in mdir("::/AVF_INFO")
    # el índice que ha llegado a la imagen es el mismo que genera sd_media (y su file ID se puede localizar)
    img = salida.read_bytes()
    off = img.find(sd_media.ID)
    assert off > 0 and off % 512 == 0  # empieza en un sector: la traza SDIO lo puede mapear a offset de fichero


@pytest.mark.skipif(bool(FALTA), reason=f"faltan herramientas mtools/dosfstools: {', '.join(FALTA)}")
def test_media_reemplaza_los_archivos_conflictivos_solo_en_la_imagen(tmp_path: Path):
    raiz = tmp_path / "sd"
    indice = raiz / "AVF_INFO/AVIN0001.INP"
    indice.parent.mkdir(parents=True)
    indice.write_bytes(b"indice previo")
    foto = raiz / "DCIM/100MSDCF/DSC00001.JPG"
    foto.parent.mkdir(parents=True)
    foto.write_bytes(b"foto previa")
    otro = foto.with_name("DSC00002.JPG")
    otro.write_bytes(b"otra foto")
    imagen = tmp_path / "media.head"
    sd_image.construye(raiz, imagen, 0.25, media=True)

    def leer(ruta: str) -> bytes:
        return subprocess.run(["mtype", "-i", str(imagen), ruta], check=True, capture_output=True).stdout

    assert leer("::/AVF_INFO/AVIN0001.INP") != indice.read_bytes()
    assert leer("::/DCIM/100MSDCF/DSC00001.JPG").startswith(b"\xff\xd8")
    assert leer("::/DCIM/100MSDCF/DSC00002.JPG") == b"otra foto"
    assert indice.read_bytes() == b"indice previo" and foto.read_bytes() == b"foto previa"


def _va_a_offset(d: bytes, va: int) -> int:
    """VA → desplazamiento de fichero con los `PT_LOAD` del ELF (el .data de libmpr NO va en el primer segmento)."""
    e_phoff = struct.unpack_from("<I", d, 0x1C)[0]
    e_phentsize, e_phnum = struct.unpack_from("<HH", d, 0x2A)
    for i in range(e_phnum):
        p_type, p_offset, p_vaddr, _pa, p_filesz = struct.unpack_from("<IIIII", d, e_phoff + i * e_phentsize)
        if p_type == 1 and p_vaddr <= va < p_vaddr + p_filesz:
            return p_offset + (va - p_vaddr)
    raise AssertionError(f"VA {va:#x} fuera de los PT_LOAD")


@pytest.mark.skipif(not LIBMPR.exists(), reason="no está libmpr.so (firmware ni arnés)")
def test_el_descriptor_de_libmpr_dice_registro_0x80_y_el_id_que_escribe_el_generador():
    d = LIBMPR.read_bytes()
    off = _va_a_offset(d, DESCRIPTOR)
    cab = d[off:off + 0x50]
    assert cab[0x00:0x10].rstrip(b"\0") == b"AVIN0001.INP"
    assert struct.unpack_from("<I", cab, 0x10)[0] == sd_media.REGISTRO  # 0x80
    assert struct.unpack_from("<I", cab, 0x14)[0] == sd_media.MAXIMO  # 0x2710
    assert cab[0x28:0x28 + 16] == sd_media.ID  # el generador escribe el mismo file ID
