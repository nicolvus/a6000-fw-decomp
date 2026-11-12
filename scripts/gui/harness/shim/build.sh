#!/bin/sh
# Uso: build.sh SYSROOT_DEBIAN_ARMHF DIR_LIB_CAMARA SALIDA.so   (SYSROOT = headers de libc6-dev armhf + linux-libc-dev extraídos)
set -e
SR=$1; CAM=$2; OUT=$3
touch "$SR/usr/include/arm-linux-gnueabihf/gnu/stubs-soft.h"
clang --target=armv7-linux-gnueabi -mfloat-abi=softfp -mcpu=cortex-a15 -O2 -fno-stack-protector -fPIC -shared -fuse-ld=lld -nostdlib -nostdinc \
  -isystem "$SR/usr/include/arm-linux-gnueabihf" -isystem "$SR/usr/include" -isystem "$(clang -print-resource-dir)/include" -std=gnu99 \
  "$(dirname "$0")/sonyshim.c" -o "$OUT" -L"$CAM" -l:libc-2.11.2.so -l:libdl-2.11.2.so -l:librt-2.11.2.so -l:libpthread-2.11.2.so
