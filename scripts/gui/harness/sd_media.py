"""Medios de la SD emulada (G22-PBMEDIA): una foto JPEG real + el índice AV `AVF_INFO` coherente con ella.

Se activa con `SD_MEDIA=1` (live.py → sd_image.construye(..., media=True)); por defecto no cambia nada.

FORMATO DEDUCIDO (ver docs/gui/g22-pbmedia-indice-avf.md §2 para las direcciones y la evidencia):

  * Descriptor de `AVIN0001.INP` en `.data` de `libmpr.so` VA `0x9d1270` (52 B útiles, 0x50 de zanja):
        +0x00 char name[0x10]  "AVIN0001.INP"
        +0x10 u32 0x80         ← tamaño de registro
        +0x14 u32 0x2710       ← nº máximo de registros (10 000)
        +0x18 u32 0xffffffff   ← centinela
        +0x1c u32 1
        +0x20 u32 0x4b0
        +0x24 u32 0x86
        +0x28 u8  id[16]       ← "file ID" del índice (GETAVINDEXFILEID)
  * Registro (0x80 B, alineación 4, sin `pack`), deducido del volcado `[AVI][MON]` de `libmpr` 0x1de066
    (cDirPath en `r7+0xb8`, cFileName en `r7+0xca`, nFileSize en `r7+0xd8`… ⇒ Δ 0x12/0x0e/0x20…):
        +0x00 char cDirPath[0x12]   p. ej. "DCIM/100MSDCF"
        +0x12 char cFileName[0x0e]  p. ej. "DSC00001.JPG"
        +0x20 u32  nFileSize        bytes del fichero
        +0x24 u8   bIsValid         (1 = válido)
        +0x28 u32  nWidth
        +0x2c u32  nHeight
        +0x30 u32  nMsec            duración en ms (0 en fotos)
        +0x34 u32  n90kHz           duración en unidades de 90 kHz (0 en fotos)
        +0x38 u32  emVideoCodec     4 = AVC (0 en fotos)
        +0x3c u32  emProfileIndication
  * Cabecera del fichero: `CABECERA = 0x100` B (el u32 del descriptor en +0x40). Los primeros 16 B llevan
    el `file ID` de +0x28 del descriptor; el resto, ceros. `SD_MEDIA_CAB` permite probar otros tamaños y
    `SD_MEDIA_ID=0` deja la cabecera a ceros, para no confundir la hipótesis con el dato.

Todo lo que este módulo escribe está calculado a partir del JPEG real que mete en `DCIM/100MSDCF`; no se
 inventa ningún byte de contenido del firmware.
"""
import os
import struct
from pathlib import Path

REGISTRO = 0x80  # descriptor libmpr .data 0x9d1270 (+0x10)
MAXIMO = 0x2710  # descriptor libmpr .data 0x9d1270 (+0x14)
CABECERA = int(os.environ.get("SD_MEDIA_CAB", "0x100"), 0)  # descriptor +0x40
ID = bytes.fromhex("ff067581fa7be290452784b05e6110ad")  # descriptor +0x28: avindexFileId
FICHERO_DIR = "DCIM"  # primera carpeta DCF
CARPETA = "100MSDCF"
NOMBRE_FOTO = "DSC00001.JPG"
# Extensiones de foto real que se pueden copiar tal cual; el resto se convierte con PIL (venv).
EXT_FOTO = (".jpg", ".jpeg", ".JPG", ".JPEG")
BUSQUEDA_FOTO = ("analysis/camera-dumps", "reports/evidence")


def registro(dirpath: str, nombre: str, tamano: int, ancho: int, alto: int,
             ms: int = 0, n90k: int = 0, codec: int = 0, perfil: int = 0, valido: int = 1) -> bytes:
    """Un registro de 0x80 B con los campos del §3 del informe. Ceros en lo que no se conoce."""
    r = bytearray(REGISTRO)
    dp = dirpath.encode()[:0x12]
    nm = nombre.encode()[:0x0E]
    r[0x00:0x00 + len(dp)] = dp
    r[0x12:0x12 + len(nm)] = nm
    struct.pack_into("<I", r, 0x20, tamano)
    r[0x24] = valido & 0xFF
    struct.pack_into("<I", r, 0x28, ancho)
    struct.pack_into("<I", r, 0x2C, alto)
    struct.pack_into("<I", r, 0x30, ms)
    struct.pack_into("<I", r, 0x34, n90k)
    struct.pack_into("<I", r, 0x38, codec)
    struct.pack_into("<I", r, 0x3C, perfil)
    return bytes(r)


def avin(registros: list[bytes], cabecera: int = CABECERA, id_: bytes | None = None) -> bytes:
    """Fichero del índice AV: cabecera + registros de 0x80 B. El nº de registros lo da el tamaño."""
    cab = bytearray(cabecera)
    ident = ID if id_ is None else id_
    if ident and cabecera >= len(ident):
        cab[0:len(ident)] = ident[:cabecera]
    return bytes(cab) + b"".join(registros)


def exif(datos: bytes) -> bool:
    """¿lleva EXIF? (marcador APP1 de JPEG con la firma «Exif\\0\\0»)."""
    return b"Exif\x00\x00" in datos[:0x10000]


def tamano_jpeg(datos: bytes) -> tuple[int, int]:
    """(ancho, alto) del SOF del JPEG; (0, 0) si no se encuentra."""
    i = 2
    while i + 9 < len(datos):
        if datos[i] != 0xFF:
            i += 1
            continue
        m = datos[i + 1]
        if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            alto, ancho = struct.unpack_from(">HH", datos, i + 5)
            return ancho, alto
        if m in (0xD8, 0xD9):
            i += 2
            continue
        largo = struct.unpack_from(">H", datos, i + 2)[0]
        i += 2 + largo
    return 0, 0


def busca_foto(raiz: Path | None = None) -> Path | None:
    """Primera foto JPEG real del repo (con EXIF a ser posible): SD_MEDIA_FOTO manda."""
    if (p := os.environ.get("SD_MEDIA_FOTO")):
        return Path(p)
    base = raiz or Path(__file__).resolve().parents[3]
    for sub in BUSQUEDA_FOTO:
        d = base / sub
        if not d.is_dir():
            continue
        candidatas = sorted(p for p in d.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg") and p.stat().st_size > 4096)
        for p in candidatas:
            try:
                if exif(p.read_bytes()[:0x20000]):
                    return p
            except OSError:
                continue
        if candidatas:
            return candidatas[0]
    return None


def foto(destino: Path, origen: Path | None = None) -> bytes:
    """Escribe la foto en `destino` (nombre DCF) y devuelve sus bytes: copia del original o conversión."""
    origen = origen or busca_foto()
    if origen is not None and origen.suffix.lower() in (".jpg", ".jpeg"):
        datos = origen.read_bytes()
    elif origen is not None:  # PNG y demás: convertir conservando tamaño razonable
        from PIL import Image
        with Image.open(origen) as im:
            buf = destino.open("wb")
            with buf:
                im.convert("RGB").save(buf, "JPEG", quality=90)
        return destino.read_bytes()
    else:  # sin foto en el repo: JPEG sintético (marcado en el informe como tal)
        from PIL import Image, ImageDraw
        im = Image.new("RGB", (1616, 1080), (40, 60, 90))
        ImageDraw.Draw(im).rectangle([80, 80, 1536, 1000], outline=(255, 200, 0), width=12)
        im.save(destino, "JPEG", quality=90)
        return destino.read_bytes()
    destino.write_bytes(datos)
    return datos


def construye(destino: Path, origen: Path | None = None, cabecera: int = CABECERA) -> dict:
    """Crea el árbol de medios en `destino` (que será la raíz de la SD): foto real + `AVF_INFO` coherente.

    Devuelve el «mapa» escrito (para la evidencia y para los tests): nombres, tamaños y offsets del índice.
    """
    destino = Path(destino)
    dcim = destino / FICHERO_DIR / CARPETA
    avf = destino / "AVF_INFO"
    dcim.mkdir(parents=True, exist_ok=True)
    avf.mkdir(parents=True, exist_ok=True)
    datos = foto(dcim / NOMBRE_FOTO, origen)
    ancho, alto = tamano_jpeg(datos)
    reg = registro(f"{FICHERO_DIR}/{CARPETA}", NOMBRE_FOTO, len(datos), ancho, alto)
    indice = avin([reg], cabecera)
    for nombre in ("AVIN0001.INP", "AVIN0001.BNP"):  # primario y respaldo: mismo contenido
        (avf / nombre).write_bytes(indice)
    (avf / "AVIN0001.INT").write_bytes(b"")  # tabla interna: contenido no conocido, 0 B (no se inventa)
    (avf / "PRV00001.BIN").write_bytes(b"")  # propiedades por contenido: 0 B
    (avf / "STAT0000.BIN").write_bytes(b"")  # estado del índice: 0 B
    return {
        "foto": f"{FICHERO_DIR}/{CARPETA}/{NOMBRE_FOTO}",
        "foto_bytes": len(datos),
        "ancho": ancho,
        "alto": alto,
        "exif": exif(datos),
        "cabecera": cabecera,
        "registro": REGISTRO,
        "registros": 1,
        "indice_bytes": len(indice),
        "offset_registro0": cabecera,
        "id_indice": ID.hex(),
    }


if __name__ == "__main__":  # utilidad: volcar el mapa de un árbol ya construido
    import json
    import sys
    print(json.dumps(construye(Path(sys.argv[1])), indent=2))
