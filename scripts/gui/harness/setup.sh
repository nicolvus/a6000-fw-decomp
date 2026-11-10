#!/bin/sh
# Arnés de la UI (G22-B): prepara DIR_TRABAJO desde cero: descargas de Debian (kernel/initrd del instalador netboot de trixie,
# cabeceras libc6-dev/linux-libc-dev para compilar el shim), initramfs base (build_base.py), sonyshim.so (shim/build.sh) y
# /usr/share/bk.tbl (gen_bk.py) en overlay/. Reutiliza lo ya descargado en DIR_TRABAJO/dl.
# Uso: setup.sh DIR_TRABAJO [DIR_DEV] [backup_flash.bin]
#   DIR_DEV = .../0700_part_image/dev del firmware extraído (por defecto fw321); backup_flash.bin = volcado NVRAM (BK4).
set -e
W=$(realpath -m "$1"); HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$HERE/../../.." && pwd)
DEV=${2:-$REPO/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev}
NV=${3:-$REPO/analysis/camera-dumps/20261105-volcado-total-nvram/backup_flash.bin}
D=https://deb.debian.org/debian
mkdir -p "$W/dl" "$W/sysroot" "$W/overlay/cam/usr/lib" "$W/overlay/cam/usr/share"
get() { [ -s "$W/dl/$1" ] || curl -fL --retry 3 -o "$W/dl/$1" "$2"; }
get vmlinuz "$D/dists/trixie/main/installer-armhf/current/images/netboot/vmlinuz"      # 6.12 armmp; «current» cambia con cada punto de trixie
get initrd.gz "$D/dists/trixie/main/installer-armhf/current/images/netboot/initrd.gz"
get libc6-dev_2.44-3_armhf.deb "$D/pool/main/g/glibc/libc6-dev_2.44-3_armhf.deb"
get linux-libc-dev_7.3.3-1_all.deb "$D/pool/main/l/linux/linux-libc-dev_7.3.3-1_all.deb"
(cd "$W/dl" && sha256sum vmlinuz initrd.gz ./*.deb > SHA256SUMS && cat SHA256SUMS)
cp "$W/dl/vmlinuz" "$W/vmlinuz"
rm -rf "$W/ird"; mkdir "$W/ird"
(cd "$W/ird" && zcat "$W/dl/initrd.gz" | cpio -id --quiet --no-preserve-owner 2>&1 | grep -v "Operation not permitted" || true)  # los nodos de /dev no se pueden crear sin root y no hacen falta (devtmpfs)
for p in "$W"/dl/*.deb; do bsdtar -xOf "$p" 'data.tar.*' | bsdtar -xf - -C "$W/sysroot"; done
python3 "$HERE/build_base.py" "$DEV" "$W" "$W/ird"
sh "$HERE/shim/build.sh" "$W/sysroot" "$DEV/nflasha7_unpacked_unpacked/lib" "$W/overlay/cam/usr/lib/sonyshim.so"
python3 "$HERE/gen_bk.py" "$NV" "$W/overlay/cam/usr/share/bk.tbl"
echo "listo: $W. Ejecutar: SHIMENV='WAIT=60 CVWAIT=0 POKE=fef348' python3 $HERE/run.py $W $HERE/im.sh 90"
