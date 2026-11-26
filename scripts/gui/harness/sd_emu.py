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
import shutil
import threading
from pathlib import Path

from PIL import Image

SD_DEFECTO = Path.home() / "A6000-SD"
FOTO_RE = re.compile(r"^DSC(\d{5})\.(JPG|ARW|PNG|WEBP|BMP|GIF)$", re.IGNORECASE)
CARPETA_RE = re.compile(r"^(\d{3})MSDCF$")
CLIP_RE = re.compile(r"^C(\d{4})\.(MP4|WEBM)$", re.IGNORECASE)
MAX_POR_CARPETA = 9999  # NO_VERIFICADO: tope del contador de 4 dígitos de DCF
MAX_CLIP = 9999
CERROJO = threading.Lock()  # numerar + escribir, de uno en uno: dos subidas o dos disparos a la vez no deben pisarse (QA F08)
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
    if destino.is_symlink():  # escribir no sigue enlaces: un enlace en la SD no puede sacar el fichero fuera (QA F09)
        destino.unlink()
    tmp = destino.with_name(destino.name + ".tmp")
    tmp.write_bytes(datos)
    tmp.replace(destino)


def escribe_desde(destino: Path, origen: Path) -> None:
    """Copia un fichero a la SD sin cargarlo entero en memoria (un clip de 20 min no cabe en RAM, QA F11)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.is_symlink():
        destino.unlink()
    tmp = destino.with_name(destino.name + ".tmp")
    with origen.open("rb") as fi, tmp.open("wb") as fo:
        shutil.copyfileobj(fi, fo, 1 << 20)
    tmp.replace(destino)


def ruta_segura(raiz: Path, rel: str) -> Path:
    """Fichero de la SD a partir de su ruta relativa (`DCIM/100MSDCF/DSC00001.JPG`), sin salir de `raiz`."""
    p = (raiz / rel).resolve()
    if raiz.resolve() not in p.parents and p != raiz.resolve():
        raise ValueError("ruta fuera de la SD")
    return p


def lista(raiz: Path) -> list[dict]:
    """Contenido de la SD para la galería: fotos y clips con tamaño, fecha y si la extensión es de la cámara.

    Orden: lo más nuevo primero (la cámara reproduce del último al primero). `media` = la galería puede mostrarlo.
    """
    if not raiz.is_dir():
        return []
    out = []
    for f in raiz.rglob("*"):
        if not f.is_file() or f.name.endswith((".tmp", ".ok")):
            continue
        out.append({"ruta": f.relative_to(raiz).as_posix(), "bytes": f.stat().st_size, "mtime": int(f.stat().st_mtime),
                    "media": f.suffix.lower() in (".jpg", ".jpeg", ".arw", ".mp4", ".webm", ".mov", ".png")})
    return sorted(out, key=lambda d: (d["mtime"], d["ruta"]), reverse=True)


def borra(raiz: Path, rel: str) -> None:
    f = ruta_segura(raiz, rel)
    if not f.is_file():
        raise ValueError("no existe en la SD")
    f.unlink()
    for d in (f.parent, f.parent.parent):  # deja de existir una carpeta vacía de la cámara (100MSDCF, DCIM)
        if d != raiz.resolve() and d.is_dir() and not any(d.iterdir()) and d.name != "DCIM":
            d.rmdir()


def formatea(raiz: Path) -> int:
    """«Formatear» de la cámara: borra SOLO el árbol de la cámara (DCIM, PRIVATE, MP_ROOT, AVF_INFO) y lo recrea.

    No borra la carpeta del anfitrión ni nada que no sea de la cámara: si la ruta no parece una SD (ni DCIM ni
    PRIVATE y con otros ficheros dentro) se niega, para que una config equivocada no vacíe una carpeta de trabajo.
    """
    if raiz.exists() and not raiz.is_dir():
        raise ValueError("la SD configurada no es una carpeta")
    propios = ("DCIM", "PRIVATE", "MP_ROOT", "AVF_INFO")
    ajenos = [p.name for p in raiz.iterdir() if p.name not in propios] if raiz.is_dir() else []
    if ajenos and not any((raiz / d).exists() for d in ("DCIM", "PRIVATE")):
        raise ValueError("no parece una tarjeta SD (no hay DCIM ni PRIVATE): no se formatea")
    n = 0
    for d in propios:
        if not (raiz / d).exists():
            continue
        if (raiz / d).is_symlink():  # un enlace no se sigue: se quita el enlace
            (raiz / d).unlink()
            continue
        n += sum(1 for f in (raiz / d).rglob("*") if f.is_file())
        shutil.rmtree(raiz / d)
    for c in ("DCIM/100MSDCF", "PRIVATE/M4ROOT/CLIP", "PRIVATE/AVCHD"):
        (raiz / c).mkdir(parents=True, exist_ok=True)
    return n


def importa(raiz: Path, nombre: str, datos: bytes, cuota: int | None = None) -> Path:
    """Sube un fichero del anfitrión a la SD: fotos con la numeración de la cámara (DSCnnnnn), clips como Cnnnn.

    La cuota se comprueba con el tamaño definitivo (el JPEG reescrito con EXIF puede crecer, QA F07) y la numeración
    va bajo cerrojo para que dos subidas a la vez no elijan el mismo nombre (QA F08).
    """
    ext = Path(nombre).suffix.lower()
    with CERROJO:
        if ext in (".jpg", ".jpeg"):
            datos = jpeg_con_exif(datos)
            n, num = siguiente_foto(raiz)
            d = ruta_foto(raiz, n, num)
        elif ext in (".arw", ".png", ".webp", ".bmp", ".gif"):
            n, num = siguiente_foto(raiz)
            d = ruta_foto(raiz, n, num).with_suffix(ext.upper())
        else:  # un vídeo o cualquier otro fichero entra como clip de la cámara, no con su nombre original (QA F05)
            d = ruta_clip(raiz, siguiente_clip(raiz), ext.lstrip(".").upper() or "MP4")
        if cuota is not None and usado(raiz) + len(datos) > cuota:
            raise ValueError("SD llena (cuota superada)")
        escribe_atomico(d, datos)
    return d
