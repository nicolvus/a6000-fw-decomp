#!/bin/sh
# T6 (emulador, no cámara): prepara DIR_TRABAJO (p. ej. analysis/gui/g22/harness/t6) para run.py con el Android 2.3.7 de nflasha16.
# Reutiliza vmlinuz/base.cpio.gz de G22, pero con el kernel 6.12.113 de Debian (su .deb trae binder_linux; el netboot 6.12.107 ya no está en el pool).
# Uso: prep.sh DIR_TRABAJO [BASE_G22]
set -e
W=$(realpath -m "$1"); B=$(realpath -m "${2:-$(dirname "$W")}")
REPO=$(cd "$(dirname "$0")/../../../.." && pwd)
DEV=$REPO/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev
RD=$DEV/nflasha15_unpacked_unpacked/bin/ramdisk.img_unpacked_unpacked
KV=6.12.113+deb13-armmp
mkdir -p "$W/dl" "$W/overlay"
if [ ! -s "$W/dl/kimg.deb" ]; then curl -fL -o "$W/dl/kimg.deb" "https://deb.debian.org/debian/pool/main/l/linux/linux-image-${KV%%+*}+deb13-armmp_${KV%%+*}-1_armhf.deb"; fi
[ -d "$W/k" ] || { mkdir "$W/k"; bsdtar -xOf "$W/dl/kimg.deb" 'data.tar.*' | bsdtar -xf - -C "$W/k"; }
cp "$W/k/boot/vmlinuz-$KV" "$W/vmlinuz"; ln -sf "$B/base.cpio.gz" "$W/base.cpio.gz"
M=$W/k/usr/lib/modules/$KV/kernel; O=$W/overlay
rm -rf "$O"; mkdir -p "$O/cam/t6mod" "$O/cam/and"
for m in drivers/android/binder_linux drivers/usb/gadget/libcomposite drivers/usb/gadget/udc/udc-core drivers/usb/gadget/udc/dummy_hcd fs/configfs/configfs \
         drivers/usb/gadget/function/usb_f_fs drivers/usb/gadget/function/usb_f_mass_storage drivers/usb/usbip/usbip-core drivers/usb/usbip/vhci-hcd drivers/usb/usbip/usbip-vudc; do
  [ -f "$M/$m.ko.xz" ] && xz -dc "$M/$m.ko.xz" > "$O/cam/t6mod/$(basename $m).ko"
done
cp -a "$DEV/nflasha16_unpacked_unpacked" "$O/cam/and/system"          # /system de la cámara (Android 2.3.7 GWK74)
cp -a "$RD"/init "$RD"/init.rc "$RD"/default.prop "$RD"/ueventd.rc "$RD"/init.goldfish.rc "$RD"/ueventd.goldfish.rc "$O/cam/and/"
echo '/dev/uipc                 0666   root       root' >> "$O/cam/and/ueventd.rc"   # adición del emulador: osal_uipc lo abren procesos no root (system_server uid 1000)
printf '0 0 android\n' > "$O/cam/and/system/lib/egl/egl.cfg"                       # adición del emulador: EGL por software (no hay /dev/dmpgles2)
mkdir -p "$O"/cam/and/sbin "$O"/cam/and/data "$O"/cam/and/cache "$O"/cam/and/proc "$O"/cam/and/sys "$O"/cam/and/dev "$O"/cam/and/mnt
chmod -R a+rX "$O/cam/and"; chmod 755 "$O/cam/and/init" "$O"/cam/and/system/bin/* "$O"/cam/and/system/xbin/* 2>/dev/null || true
[ -f "$W/b32/binder_linux.ko" ] && cp "$W/b32/binder_linux.ko" "$O/cam/t6mod/binder32.ko"; [ -f "$W/uipc/uipc_stub.ko" ] && cp "$W/uipc/uipc_stub.ko" "$O/cam/t6mod/"  # build_binder32.sh
cp "$(dirname "$0")/android.sh" "$W/android.sh"
du -sh "$O"
