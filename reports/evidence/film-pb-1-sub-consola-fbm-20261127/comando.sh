#!/bin/sh
# FILM-PB-1 / sub-consola-fbm: compila el shim instrumentado (consola FBM + anillo + ptrace) y lanza el
# perfil nuevo `fbm` del arnés con la inyección. Desde la raíz del repo.
#
#   sh comando.sh                 # pasada completa (consola FBM + anillo + ptrace), ~3 min
#   PBINJECT=8 python3 pb_run_fbm.py 160 runNN "PBSKIP=1"   # sólo la prueba de ptrace (~40 s)
#   PBINJECT=8 python3 pb_run_fbm.py 120 runNN "PBSKIP=2"   # sólo el volcado de la tabla (línea base)
#
# El 3.er argumento de pb_run_fbm.py es SHIMEXTRA (va a /cam/harness.env); PBSKIP por entorno del host NO
# siempre llega. El shim usa /usr/bin/{ptcall,fbm_ring.sh} y un /bin/sh copia de busybox: el /cam de la
# cámara no tiene enlaces de applets y su busybox no trae awk (ver README de la evidencia).
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd); cd "$REPO"
SR=analysis/gui/g22/harness/sysroot
CAM=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib
OUT=analysis/gui/g22/harness/live/fbm/overlay/cam/usr/lib/sonyshim.so
OV=analysis/gui/g22/harness/live/fbm/overlay/cam
EV=reports/evidence/film-pb-1-sub-consola-fbm-20261127
mkdir -p "$(dirname "$OUT")" "$OV/usr/bin" "$OV/bin"
touch "$SR/usr/include/arm-linux-gnueabihf/gnu/stubs-soft.h"
clang --target=armv7-linux-gnueabi -mfloat-abi=softfp -mcpu=cortex-a15 -O2 -fno-stack-protector \
  -fPIC -shared -fuse-ld=lld -nostdlib -nostdinc -Iscripts/gui/harness/shim \
  -isystem "$SR/usr/include/arm-linux-gnueabihf" -isystem "$SR/usr/include" \
  -isystem "$(clang -print-resource-dir)/include" -std=gnu99 "$EV/sonyshim-fbm.c" -o "$OUT" \
  -L"$CAM" -l:libc-2.11.2.so -l:libdl-2.11.2.so -l:librt-2.11.2.so -l:libpthread-2.11.2.so
sh tools/camera-ptrace/build.sh
cp -f tools/camera-ptrace/ptcall      "$OV/usr/bin/ptcall"
cp -f tools/camera-ptrace/fbm_ring.sh "$OV/usr/bin/fbm_ring.sh"
# /bin/sh del invitado (copia del busybox de la cámara): sin él, system() devuelve 127 y no se puede lanzar
# ni ptcall ni fbm_ring.sh dentro del chroot de im.elf.
[ -x "$OV/bin/sh" ] || {
  T=$(mktemp -d)
  ( cd "$T" && zcat "$REPO/analysis/gui/g22/harness/base.cpio.gz" | cpio -id --quiet cam/bin/busybox )
  cp "$T/cam/bin/busybox" "$OV/bin/sh"; chmod 755 "$OV/bin/sh"; rm -rf "$T"
}
PBINJECT=25 python3 "$EV/pb_run_fbm.py" 420 "$EV/run1"
