"""SD emulada del arnés (G22-E/T4): carpeta del anfitrión con la estructura de la A6000, numeración, cuota y EXIF. Lógica pura, sin servidor.

Evidencia de cada elemento (ver docs/gui/g22-emulador-uso.md § «Sensor, SD y grabación»):
  VERIFICADO (firmware 3.21, `av-cam.bin`): `DCIM/100MSDCF/DSC%05d.ARW` (analysis/s87_storage/storage_filesystem.md §1); carpetas
    `100MSDCF`, `101MSDCF`… (analysis/s92_mediadb/media_database.md §4); cadena `PRIVATE/M4ROOT/CLIP` en la documentación del repo.
  NORMA (DCF 2.0, JEITA CP-3461): carpeta `NNNxxxxx` con NNN = 100…999; el nombre del fichero del fabricante lleva el contador.
  NO_VERIFICADO: extensión `.JPG` con prefijo `DSC` (lo habitual de Sony; el firmware solo da la cadena `.ARW`), `C%04d.MP4` de XAVC S,
    paso a la carpeta siguiente a los 9999 ficheros, «Número archivo» Serie/Reset (aquí siempre Serie), sidecar `C0001M01.XML`, tamaño medio.
"""
import datetime as dt
import io
import re
from pathlib import Path

from PIL import Image

SD_DEFECTO = Path.home() / "A6000-SD"
FOTO_RE = re.compile(r"^DSC(\d{5})\.(JPG|ARW)$", re.IGNORECASE)
CARPETA_RE = re.compile(r"^(\d{3})MSDCF$")
CLIP_RE = re.compile(r"^C(\d{4})\.(MP4|WEBM)$", re.IGNORECASE)
MAX_POR_CARPETA = 9999  # NO_VERIFICADO: tope del contador de 4 dígitos de DCF
MAX_CLIP = 9999
FOTO_MEDIA = 6 << 20  # NO_VERIFICADO: JPEG de 24 Mpx ≈ 6 MB; solo para el «disparos restantes» aproximado
VIDEO_BPS = 50_000_000 / 8  # XAVC S 50 Mbps (máximo de la A6000); solo para los «minutos restantes» aproximados


def raiz_sd(carpeta: str) -> Path:
    return Path(carpeta).expanduser() if carpeta else SD_DEFECTO


def cuota_bytes(tamano_gb: float) -> int:
    return int(tamano_gb * (1 << 30))


def usado(raiz: Path) -> int:
    return sum(f.stat().st_size for f in raiz.rglob("*") if f.is_file()) if raiz.is_dir() else 0


def libre(raiz: Path, tamano_gb: float) -> int:
    return max(0, cuota_bytes(tamano_gb) - usado(raiz))


def cabe(raiz: Path, tamano_gb: float, nuevos: int) -> bool:
    """Cuota: no se escribe si el contenido actual + lo nuevo supera el tamaño de la tarjeta."""
    return usado(raiz) + nuevos <= cuota_bytes(tamano_gb)


def siguiente_foto(raiz: Path) -> tuple[int, int]:
    """(carpeta NNN, contador) del siguiente `DCIM/NNNMSDCF/DSCnnnnn`: modo «Serie» = máximo existente (JPG o ARW) + 1."""
    dcim = raiz / "DCIM"
    carpetas = sorted(int(m.group(1)) for d in dcim.iterdir() if d.is_dir() and (m := CARPETA_RE.match(d.name))) if dcim.is_dir() else []
    n = carpetas[-1] if carpetas else 100
    usados = [int(m.group(1)) for f in (dcim / f"{n}MSDCF").glob("*") if (m := FOTO_RE.match(f.name))] if carpetas else []
    num = max(usados, default=0) + 1
    if num > MAX_POR_CARPETA:
        n, num = n + 1, 1
    if n > 999:
        raise ValueError("DCF: no caben más carpetas (999MSDCF llena)")
    return n, num


def ruta_foto(raiz: Path, n: int, num: int) -> Path:
    return raiz / "DCIM" / f"{n}MSDCF" / f"DSC{num:05d}.JPG"


def siguiente_clip(raiz: Path) -> int:
    d = raiz / "PRIVATE/M4ROOT/CLIP"
    n = max((int(m.group(1)) for f in d.glob("*") if (m := CLIP_RE.match(f.name))), default=0) + 1 if d.is_dir() else 1
    if n > MAX_CLIP:
        raise ValueError("XAVC S: no caben más clips (C9999)")
    return n


def ruta_clip(raiz: Path, n: int, ext: str = "MP4") -> Path:
    return raiz / "PRIVATE/M4ROOT/CLIP" / f"C{n:04d}.{ext}"


def jpeg_con_exif(jpeg: bytes, ahora: dt.datetime | None = None, calidad: int = 92) -> bytes:
    """Reescribe el JPEG con EXIF mínimo: Make SONY, Model ILCE-6000, DateTime/DateTimeOriginal = hora del ordenador (formato EXIF)."""
    f = (ahora or dt.datetime.now()).strftime("%Y:%m:%d %H:%M:%S")
    img = Image.open(io.BytesIO(jpeg)).convert("RGB")
    ex = Image.Exif()
    ex[0x010F], ex[0x0110], ex[0x0132] = "SONY", "ILCE-6000", f
    ex.get_ifd(0x8769)[0x9003] = f
    out = io.BytesIO()
    img.save(out, "JPEG", quality=calidad, exif=ex)
    return out.getvalue()


def estado(raiz: Path, tamano_gb: float) -> dict:
    u = usado(raiz)
    lib = max(0, cuota_bytes(tamano_gb) - u)
    fotos = [f.stat().st_size for f in (raiz / "DCIM").rglob("*") if f.is_file() and FOTO_RE.match(f.name)] if (raiz / "DCIM").is_dir() else []
    media = sum(fotos) // len(fotos) if fotos else FOTO_MEDIA
    return {"raiz": str(raiz), "cuota": cuota_bytes(tamano_gb), "usado": u, "libre": lib, "fotos": len(fotos),
            "disparos_aprox": lib // max(media, 1), "minutos_xavcs_aprox": int(lib / VIDEO_BPS // 60)}


def escribe_atomico(destino: Path, datos: bytes) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_name(destino.name + ".tmp")
    tmp.write_bytes(datos)
    tmp.replace(destino)
