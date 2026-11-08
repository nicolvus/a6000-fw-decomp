#!/usr/bin/env python3
"""Crea un sysroot de enlaces simbólicos (rootfs `nflasha7` + `/usr` = `nflasha15`) para `qemu-arm -L` con el glibc 2.11.2 de la cámara.

Uso: qemu_sysroot.py DIR_DEV DESTINO     (DIR_DEV = .../0700_part_image/dev)
Prueba de carga:  qemu-arm -E LD_DEBUG=files -E LD_PRELOAD="/usr/lib/libObj.so PARCHEADO.so" -L DESTINO DESTINO/bin/busybox true
(el guest termina con SIGSEGV tras iniciar `libObj`: no hay hardware; basta con ver «calling init» del `.so` y leer la memoria con gdb).
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

dev, dest = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
root, usr = dev / "nflasha7_unpacked_unpacked", dev / "nflasha15_unpacked_unpacked"
(dest / "lib").mkdir(parents=True, exist_ok=True)
(dest / "bin").mkdir(exist_ok=True)
if not (dest / "usr").exists():
    (dest / "usr").symlink_to(usr)
shutil.copy(root / "bin/busybox", dest / "bin/busybox")  # qemu exige permiso de ejecución en el binario principal
(dest / "bin/busybox").chmod(0o755)
for lib_dir in (root / "lib", usr / "lib"):
    for f in lib_dir.iterdir():
        if f.is_file() and ".so" in f.name:
            out = subprocess.run(["readelf", "-d", str(f)], capture_output=True, text=True, check=True).stdout
            soname = re.search(r"SONAME.*\[(.+?)\]", out)
            for name in {f.name, soname.group(1) if soname else f.name}:
                if not (dest / "lib" / name).is_symlink():
                    (dest / "lib" / name).symlink_to(f)
(dest / "lib/ld-linux.so.3").unlink(missing_ok=True)
(dest / "lib/ld-linux.so.3").symlink_to(root / "lib/ld-2.11.2.so")
