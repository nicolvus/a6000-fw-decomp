#!/bin/sh
# FILM-PB-1 / sub-consola-fbm: compila el shim instrumentado (consola FBM) y arranca el perfil nuevo `fbm`
# del arnés con la inyección. Desde la raíz del repo.
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd); cd "$REPO"
SR=analysis/gui/g22/harness/sysroot
CAM=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib
OUT=analysis/gui/g22/harness/live/fbm/overlay/cam/usr/lib/sonyshim.so
EV=reports/evidence/film-pb-1-sub-consola-fbm-20261127
mkdir -p "$(dirname "$OUT")"
touch "$SR/usr/include/arm-linux-gnueabihf/gnu/stubs-soft.h"
clang --target=armv7-linux-gnueabi -mfloat-abi=softfp -mcpu=cortex-a15 -O2 -fno-stack-protector \
  -fPIC -shared -fuse-ld=lld -nostdlib -nostdinc -Iscripts/gui/harness/shim \
  -isystem "$SR/usr/include/arm-linux-gnueabihf" -isystem "$SR/usr/include" \
  -isystem "$(clang -print-resource-dir)/include" -std=gnu99 "$EV/sonyshim-fbm.c" -o "$OUT" \
  -L"$CAM" -l:libc-2.11.2.so -l:libdl-2.11.2.so -l:librt-2.11.2.so -l:libpthread-2.11.2.so
# PBINJECT=25: los hilos del shim esperan 25 s + 20 s de margen y ejecutan la consola; la VM se corta al «[FBMC] FIN».
PBINJECT=25 python3 "$EV/pb_run_fbm.py" 420 "$EV/run1"
