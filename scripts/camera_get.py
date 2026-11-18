#!/usr/bin/env python3
"""Trae ficheros de la cámara al PC por adb (adbd del Tweak, puerto 5555, sin claves) cuando el FTP de
camera_pull.py no llega (cortafuegos del PC). Como root (telnet) copia cada fichero a un tmpfs que el usuario
`shell` de adb puede leer (/android/mnt/obb, RAM: no escribe en la flash), lo descarga y lo borra.

Uso: camera_get.py DESTINO /ruta/en/camara [...]     (A6000_HOST=ip; por defecto 192.168.1.30)
     camera_get.py DESTINO --mem 0xFISICA 0xTAMAÑO NOMBRE   (vuelca RAM física con dd sobre /dev/mem)
Requiere `adb-shell` (pip)."""
import hashlib
import os
import re
import sys
from pathlib import Path

from adb_shell.adb_device import AdbDeviceTcp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from camera_telnet import run

HOST = os.environ.get("A6000_HOST", "192.168.1.30")
TMP_ROOT, TMP_ADB = "/android/mnt/obb", "/mnt/obb"


def traer(dest: Path, ruta: str, nombre: str | None = None) -> Path:
    nombre = nombre or os.path.basename(ruta)
    # Órdenes cortas por separado: una línea larga se parte en el eco del telnet y run() pierde la salida.
    copia = [] if ruta == f"{TMP_ROOT}/{nombre}" else [f"cp {ruta} {TMP_ROOT}/{nombre}"]
    out = run(HOST, copia + [f"chmod 644 {TMP_ROOT}/{nombre}", f"busybox md5sum {TMP_ROOT}/{nombre}"], timeout=120)[-1]
    m = re.search(r"\b([0-9a-f]{32})\s+" + re.escape(f"{TMP_ROOT}/{nombre}"), out)
    md5_cam = m.group(1) if m else ""
    adb = AdbDeviceTcp(HOST, 5555, default_transport_timeout_s=30.0)
    adb.connect(rsa_keys=None, auth_timeout_s=5)
    try:
        adb.pull(f"{TMP_ADB}/{nombre}", str(dest / nombre))
    finally:
        adb.close()
        run(HOST, [f"rm -f {TMP_ROOT}/{nombre}"])
    md5_pc = hashlib.md5((dest / nombre).read_bytes()).hexdigest()
    if md5_pc != md5_cam:
        raise SystemExit(f"ERROR: md5 distinto en {nombre}: cámara {md5_cam!r} ({out.strip()[-200:]!r}), PC {md5_pc}")
    print(f"{nombre}: {(dest / nombre).stat().st_size} B, md5 {md5_pc}")
    return dest / nombre


def main() -> None:
    dest = Path(sys.argv[1])
    dest.mkdir(parents=True, exist_ok=True)
    if sys.argv[2] == "--mem":
        base, size, nombre = int(sys.argv[3], 16), int(sys.argv[4], 16), sys.argv[5]
        assert base % 4096 == 0 and size % 4096 == 0, "base y tamaño múltiplos de 4096"
        # Directo al tmpfs de destino: /tmp se llena a ≈ 2,6 MiB y dd corta sin avisar (MEDIDO 17-11-2026).
        run(HOST, [f"dd if=/dev/mem of={TMP_ROOT}/{nombre} bs=4096 skip={base // 4096} count={size // 4096} 2>/dev/null"], timeout=120)
        f = traer(dest, f"{TMP_ROOT}/{nombre}")
        if f.stat().st_size != size:
            raise SystemExit(f"ERROR: {nombre} tiene {f.stat().st_size} B, se pidieron {size}")
        return
    for ruta in sys.argv[2:]:
        traer(dest, ruta)


if __name__ == "__main__":
    main()
