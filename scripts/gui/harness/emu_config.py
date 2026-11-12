#!/usr/bin/env python3
"""Lógica pura del configurador del emulador (G22-E/T3): config JSON, mapa de teclas e importación de paquetes `.dat` de Sony.

Sin servidor ni QEMU: lo usa `lanzador.py` y lo prueban los tests rápidos. El `.dat` se descifra con las herramientas del repo
(`scripts/e25_06` + claves de `references/fwtool`), se extrae `nflasha15` y `pkg_usr.py` lo reduce a un overlay; nada se instala.
"""
import ast
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONFIG_RUTA = Path.home() / ".config/a6000-emu/config.json"

# Códigos de evento del navegador (KeyboardEvent.code) por botón de la cámara; la lista de botones sale de TECLAS de live.py.
TECLAS_DEFECTO = {"arriba": ["ArrowUp"], "abajo": ["ArrowDown"], "izquierda": ["ArrowLeft"], "derecha": ["ArrowRight"],
                  "intro": ["Enter", "NumpadEnter"], "menu": ["Escape", "KeyM"], "disparador": ["Space"]}
BOTONES_DEFECTO = tuple(TECLAS_DEFECTO)
RE_TECLA = re.compile(r"^[A-Za-z0-9]{1,24}$")

CONFIG_DEFECTO = {
    "version": 1,
    "firmware": {"origen": "sony", "overlay": "", "dat": ""},  # origen: sony | overlay | dat
    "teclas": TECLAS_DEFECTO,
    # sensor, sd (T4) y red (T5) los aplica live.py; red.puerto = puerto del anfitrión que reenvía al telnet (23) del invitado
    "sensor": {"fuente": "imagen", "ruta": ""},  # imagen | video | webcam
    "sd": {"tamano_gb": 4, "carpeta": ""},
    "red": {"telnet": False, "wifi": False, "puerto": 2323},
}

MODELO_A6000 = 0x41030035  # build.MODEL (e25_27); región 0
FDAT_HDR, BLOCK = 512, 1024
N15 = "dev/nflasha15"


class DatError(ValueError):
    """Paquete no válido o no compatible: el mensaje va tal cual a la página."""


def botones_conocidos(live_py: Path = HERE / "live.py") -> list[str]:
    """Botones con código de cámara verificado: las claves del literal TECLAS de live.py (otras tareas lo ampliarán)."""
    try:
        for n in ast.parse(live_py.read_text()).body:
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "TECLAS" for t in n.targets) and isinstance(n.value, ast.Dict):
                return [k.value for k in n.value.keys if isinstance(k, ast.Constant)]
    except (OSError, SyntaxError):
        pass
    return list(BOTONES_DEFECTO)


def valida_teclas(teclas: object, botones: list[str]) -> dict[str, list[str]]:
    if not isinstance(teclas, dict):
        raise ValueError("«teclas» debe ser un objeto botón → lista de teclas")  # noqa: TRY004 - ValueError: es el error que la API devuelve
    out: dict[str, list[str]] = {}
    visto: dict[str, str] = {}
    for b, lista in teclas.items():
        if b not in botones:
            raise ValueError(f"botón desconocido: {b!r}")
        if not isinstance(lista, list) or not all(isinstance(c, str) and RE_TECLA.match(c) for c in lista):
            raise ValueError(f"teclas inválidas para {b!r}")
        for c in lista:
            if c in visto and visto[c] != b:
                raise ValueError(f"la tecla {c} está asignada a {visto[c]!r} y a {b!r}")
            visto[c] = b
        out[b] = list(dict.fromkeys(lista))
    return out


def mapa_inverso(teclas: dict[str, list[str]]) -> dict[str, str]:
    return {c: b for b, lista in teclas.items() for c in lista}


def valida_config(d: object, botones: list[str] | None = None) -> dict:
    """Devuelve la config completa y normalizada (rellena lo que falte con los valores por defecto); ValueError si algo no vale."""
    if not isinstance(d, dict):
        raise ValueError("la configuración debe ser un objeto JSON")  # noqa: TRY004
    botones = botones or botones_conocidos()
    fw = {**CONFIG_DEFECTO["firmware"], **(d.get("firmware") or {})}
    if fw["origen"] not in ("sony", "overlay", "dat"):
        raise ValueError("firmware.origen debe ser sony, overlay o dat")
    if fw["origen"] != "sony" and not (fw["overlay"] if fw["origen"] == "overlay" else fw["dat"]):
        raise ValueError("falta elegir el overlay o importar el .dat")
    teclas = valida_teclas({**TECLAS_DEFECTO, **(d.get("teclas") or {})}, botones)
    sensor = {**CONFIG_DEFECTO["sensor"], **(d.get("sensor") or {})}
    if sensor["fuente"] not in ("imagen", "video", "webcam"):
        raise ValueError("sensor.fuente debe ser imagen, video o webcam")
    if not isinstance(sensor["ruta"], str):
        raise ValueError("sensor.ruta debe ser texto")  # noqa: TRY004
    sd = {**CONFIG_DEFECTO["sd"], **(d.get("sd") or {})}
    if not isinstance(sd["tamano_gb"], (int, float)) or isinstance(sd["tamano_gb"], bool) or not 0 < sd["tamano_gb"] <= 2048:
        raise ValueError("sd.tamano_gb debe estar entre 0 y 2048")
    if not isinstance(sd["carpeta"], str):
        raise ValueError("sd.carpeta debe ser texto")  # noqa: TRY004
    red = {**CONFIG_DEFECTO["red"], **(d.get("red") or {})}
    if not isinstance(red["puerto"], int) or isinstance(red["puerto"], bool) or not 1024 <= red["puerto"] <= 65535:
        raise ValueError("red.puerto debe estar entre 1024 y 65535")
    return {"version": 1, "firmware": fw, "teclas": teclas, "sensor": sensor, "sd": sd,
            "red": {"telnet": bool(red["telnet"]), "wifi": bool(red["wifi"]), "puerto": red["puerto"]}}


def carga_config(ruta: Path = CONFIG_RUTA) -> dict:
    try:
        return valida_config(json.loads(ruta.read_text()))
    except (OSError, ValueError):
        return valida_config({})


def guarda_config(cfg: dict, ruta: Path = CONFIG_RUTA) -> dict:
    cfg = valida_config(cfg)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    tmp.replace(ruta)
    return cfg


def overlays(work: Path) -> list[str]:
    """Overlays CFW ya extraídos (`pkg*` con cam/usr) en el directorio de trabajo, incluidos los importados de un .dat."""
    return sorted(str(p.relative_to(work)) for p in [*work.glob("pkg*"), *work.glob("pkgdat/*")] if (p / "cam/usr").is_dir())


# ---------------------------------------------------------------------------------------------------- paquetes .dat
def _audit():
    import sys
    for p in (ROOT / "scripts", ROOT / "references/fwtool"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    from e25_06 import audit_packages as A
    return A


def descifra(dat: bytes, A, bloques: int | None = None) -> bytes:
    """FDAT en claro (esquema CXD90014, igual que `decrypt_fdat` pero devolviendo los bytes); `bloques` limita a los primeros."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    info = A.parse_dat(dat)
    if not info.get("magic_ok"):
        raise DatError("No es un paquete .dat de Sony (cabecera incorrecta).")
    if info.get("dend_stored") != info.get("dend_computed") or "fdat_offset" not in info:
        raise DatError("Paquete .dat dañado o incompleto (CRC o bloque FDAT).")
    total = info["fdat_size"]
    if total % BLOCK:
        raise DatError("Bloque FDAT con tamaño inválido.")
    n = min(bloques or total // BLOCK, total // BLOCK)
    k1, k2 = A.load_keys()
    enc = bytes(dat[info["fdat_offset"]:info["fdat_offset"] + n * BLOCK])
    p1 = Cipher(algorithms.AES(k1), modes.ECB()).decryptor().update(enc)
    plain = Cipher(algorithms.AES(k2), modes.ECB()).decryptor().update(p1)
    plain = p1[:512] + plain[512:]  # los 512 B iniciales del primer bloque solo llevan la primera capa
    out = bytearray()
    for i in range(n):
        blk = plain[i * BLOCK:(i + 1) * BLOCK]
        stored, flag = struct.unpack_from("<HH", blk)
        ultimo = i == total // BLOCK - 1
        ln = flag & 0x7FFF
        if sum(struct.unpack_from("<511H", blk, 2)) & 0xFFFF != stored or bool(flag & 0x8000) != ultimo and bloques is None or ln > BLOCK - 4:
            raise DatError(f"Bloque {i} del FDAT corrupto o cifrado con otra clave.")
        out += blk[4:4 + ln]
    return bytes(out)


def cabecera_dat(dat: bytes) -> dict:
    """Valida que sea un paquete de la A6000 leyendo solo la cabecera FDAT (descifra 2 bloques): versión, modelo y región."""
    A = _audit()
    hdr = A.parse_fdat_header(descifra(dat, A, bloques=2)[:FDAT_HDR])
    if hdr["magic"] != "FDAT" and not hdr["magic"].strip("\0"):
        raise DatError("Cabecera FDAT ilegible.")
    if hdr["checksum_stored"] != hdr["checksum_computed"]:
        raise DatError("Cabecera FDAT con CRC erróneo: no es un paquete de Sony intacto.")
    if hdr["model"] != MODELO_A6000:
        raise DatError(f"Paquete de otro modelo (código 0x{hdr['model']:08x}); la A6000 es 0x{MODELO_A6000:08x}.")
    return {"version": hdr["version"], "region": hdr["region"], "modelo": f"0x{hdr['model']:08x}"}


def importa_dat(dat: bytes, work: Path) -> dict:
    """Valida el .dat, extrae `nflasha15` y lo deja como overlay `work/pkgdat/dat-<versión>-<hash>`; devuelve {overlay, version, ficheros}."""
    info = cabecera_dat(dat)
    A = _audit()
    from e25_27 import tarball
    fdat = descifra(dat, A)
    hdr = A.parse_fdat_header(fdat[:FDAT_HDR])
    tar = fdat[hdr["firmware_offset"]:hdr["firmware_offset"] + hdr["firmware_size"]]
    try:
        miembros = {e.name: e.data for e in tarball.parse(tar)[0]}
    except Exception as e:
        raise DatError(f"El contenido del paquete no es un tar válido: {e}") from e
    nombre = next((n for n in miembros if n.endswith(N15)), None)
    if nombre is None:
        raise DatError("El paquete no contiene nflasha15 (partición /usr): no es un paquete de firmware completo.")
    from e25_27 import tpzl
    img = miembros[nombre]
    try:
        tpzl.TpzlImage.parse(img)
    except Exception as e:
        raise DatError(f"nflasha15 no es una imagen TPZL válida: {e}") from e
    stock = work / "stage/cam/usr"
    if not stock.is_dir():
        raise DatError(f"Falta el /usr de Sony en {stock} (ejecuta setup.sh del arnés).")
    nombre_ov = f"dat-{info['version']}-{hashlib.sha256(img).hexdigest()[:8]}"
    dest = work / "pkgdat" / nombre_ov
    tmp = work / "pkgdat" / (nombre_ov + ".bin")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(img)
    try:
        import sys
        sys.path.insert(0, str(HERE))
        import pkg_usr
        try:
            ficheros = pkg_usr.main(tmp, stock, dest)
        except AssertionError as e:
            raise DatError("nflasha15 idéntico al de Sony (o no coincide con el /usr base): no hay nada que superponer; usa «Sony de serie».") from e
    finally:
        tmp.unlink(missing_ok=True)
    return {"overlay": str(dest.relative_to(work)), "version": info["version"], "region": info["region"], "ficheros": len(ficheros),
            "crc_nflasha15": f"{zlib.crc32(img):08x}"}
