#!/bin/sh
# FILM-PB-1 / sub-arnés-orden: compila el shim instrumentado y ejecuta la inyección de la orden
# de reproducción (0x4000001D) contra el FeaCore real del arnés. Desde la raíz del repo.
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd); cd "$REPO"
SR=analysis/gui/g22/harness/sysroot
CAM=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib
OUT=analysis/gui/g22/harness/live/pbo/overlay/cam/usr/lib/sonyshim.so
EV=reports/evidence/film-pb-1-sub-arnes-orden-20261126
mkdir -p "$(dirname "$OUT")"
touch "$SR/usr/include/arm-linux-gnueabihf/gnu/stubs-soft.h"
clang --target=armv7-linux-gnueabi -mfloat-abi=softfp -mcpu=cortex-a15 -O2 -fno-stack-protector \
  -fPIC -shared -fuse-ld=lld -nostdlib -nostdinc -Iscripts/gui/harness/shim \
  -isystem "$SR/usr/include/arm-linux-gnueabihf" -isystem "$SR/usr/include" \
  -isystem "$(clang -print-resource-dir)/include" -std=gnu99 "$EV/sonyshim-orden.c" -o "$OUT" \
  -L"$CAM" -l:libc-2.11.2.so -l:libdl-2.11.2.so -l:librt-2.11.2.so -l:libpthread-2.11.2.so
# Vía (a)+(b): orden por FeaIf::PlayMovie y, si el estado no es 5, llamada directa a 0x437BC0.
PBINJECT=30 python3 "$EV/pb_run.py" 420 "$EV/run"
# Vía (a) con el estado 5 puesto antes (precondición documentada):
# PBINJECT=30 PBFORCE=1 python3 "$EV/pb_run.py" 420 "$EV/run-forzado"
