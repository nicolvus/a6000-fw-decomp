#!/usr/bin/env python3
"""Arnés de la UI (G22): construye el initramfs base = initrd de Debian armhf (módulos) + rootfs de la cámara en /cam
(nflasha7 en / y nflasha15 en /usr, con los enlaces de soname que el extractor no conserva).

Uso: build_base.py DIR_DEV DESTINO_DIR VMLINUZ_INITRD_DEBIAN_EXTRAIDO
  DIR_DEV = .../0700_part_image/dev ; DESTINO_DIR = directorio de trabajo (se crea stage/ y base.cpio.gz)
  Debian initrd ya extraído (cpio -id) en el tercer argumento.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

dev, work, ird = (Path(a).resolve() for a in sys.argv[1:4])
stage = work / "stage"
shutil.rmtree(stage, ignore_errors=True)
shutil.copytree(ird, stage, symlinks=True, ignore_dangling_symlinks=True)
cam = stage / "cam"
shutil.copytree(dev / "nflasha7_unpacked_unpacked", cam, symlinks=True)
shutil.rmtree(cam / "usr", ignore_errors=True)
shutil.copytree(dev / "nflasha15_unpacked_unpacked", cam / "usr", symlinks=True)
for d in ("proc", "sys", "dev", "tmp", "mnt"):
    (cam / d).mkdir(exist_ok=True)
for lib_dir, rel in ((cam / "lib", ""), (cam / "usr/lib", "../usr/lib/")):
    for f in lib_dir.iterdir():
        if f.is_file() and ".so" in f.name:
            out = subprocess.run(["readelf", "-d", str(f)], capture_output=True, text=True, check=False).stdout
            soname = re.search(r"SONAME.*\[(.+?)\]", out)
            for name in {f.name, soname.group(1) if soname else f.name}:
                link = cam / "lib" / name
                if not link.exists() and not link.is_symlink():
                    link.symlink_to(rel + f.name)
(cam / "lib/ld-linux.so.3").unlink(missing_ok=True)
(cam / "lib/ld-linux.so.3").symlink_to("ld-2.11.2.so")
for d in ("bin", "sbin", "usr/bin", "usr/sbin", "lib", "usr/lib"):  # el extractor no conserva el bit de ejecución
    for f in (cam / d).rglob("*"):
        if f.is_file() and not f.is_symlink():
            f.chmod(0o755)
init = stage / "init"
init.write_text("""#!/bin/busybox sh
/bin/busybox mount -t proc proc /proc
/bin/busybox mount -t sysfs sys /sys
/bin/busybox mount -t devtmpfs dev /dev
for d in proc sys dev; do /bin/busybox mount --bind /$d /cam/$d; done
/bin/busybox mount -t tmpfs tmp /cam/tmp
[ -x /cam/harness.sh ] && /bin/busybox sh /cam/harness.sh
/bin/busybox poweroff -f
""")
init.chmod(0o755)
find = subprocess.Popen(["find", ".", "-not", "-path", "./dev/*"], cwd=stage, stdout=subprocess.PIPE)
cpio = subprocess.Popen(["cpio", "-o", "-H", "newc", "-R", "0:0", "--quiet"], cwd=stage, stdin=find.stdout, stdout=subprocess.PIPE)
with open(work / "base.cpio.gz", "wb") as out:
    subprocess.run(["gzip", "-1"], stdin=cpio.stdout, stdout=out, check=True)
print("ok", (work / "base.cpio.gz").stat().st_size)
