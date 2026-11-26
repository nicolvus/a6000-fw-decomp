#!/bin/sh
# Compila el shim instrumentado (sonyshim-fbm.c -> sonyshim.so) con la receta de
# scripts/gui/harness/shim/build.sh (mismo clang/target/--sysroot), cambiando sólo el .c de entrada.
set -e
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd)
SR=$R/analysis/gui/g22/harness/sysroot
CAM=$R/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib
touch "$SR/usr/include/arm-linux-gnueabihf/gnu/stubs-soft.h"
clang --target=armv7-linux-gnueabi -mfloat-abi=softfp -mcpu=cortex-a15 -O2 -fno-stack-protector -fPIC -shared -fuse-ld=lld -nostdlib -nostdinc \
  -I"$R/scripts/gui/harness/shim" -isystem "$SR/usr/include/arm-linux-gnueabihf" -isystem "$SR/usr/include" -isystem "$(clang -print-resource-dir)/include" -std=gnu99 \
  "$D/sonyshim-fbm.c" -o "$D/sonyshim.so" -L"$CAM" -l:libc-2.11.2.so -l:libdl-2.11.2.so -l:librt-2.11.2.so -l:libpthread-2.11.2.so
echo "OK $D/sonyshim.so $(sha256sum "$D/sonyshim.so" | cut -c1-16)"
