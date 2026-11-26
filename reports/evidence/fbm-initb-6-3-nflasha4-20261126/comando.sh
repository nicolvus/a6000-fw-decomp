#!/bin/sh
# InitB 6 3 con /dev/nflasha4 real emulado (NFLASH4=1) — repetición completa.
# Desde la raíz del repo. No toca la cámara ni el shim del arnés (sólo añade un 2º .so precargado).
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd); cd "$REPO"
EV=reports/evidence/fbm-initb-6-3-nflasha4-20261126
SR=analysis/gui/g22/harness/sysroot
CAM=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib
OUT=analysis/gui/g22/harness/live/nf4/overlay/cam/usr/lib/nf4inject.so
mkdir -p "$(dirname "$OUT")"

# 0) imágenes de trabajo en /tmp (10 MiB cada una; los volcados no se versionan)
python3 "$EV/make_page.py"

# 1) inyector (mismos flags que scripts/gui/harness/shim/build.sh, libc 2.11 del firmware)
touch "$SR/usr/include/arm-linux-gnueabihf/gnu/stubs-soft.h"
clang --target=armv7-linux-gnueabi -mfloat-abi=softfp -mcpu=cortex-a15 -O2 -fno-stack-protector \
  -fPIC -shared -fuse-ld=lld -nostdlib -nostdinc -isystem "$SR/usr/include/arm-linux-gnueabihf" \
  -isystem "$SR/usr/include" -isystem "$(clang -print-resource-dir)/include" -std=gnu99 \
  "$EV/nf4inject.c" -o "$OUT" -L"$CAM" -l:libc-2.11.2.so -l:libdl-2.11.2.so \
  -l:librt-2.11.2.so -l:libpthread-2.11.2.so

# 2) pasadas (cada una ~1 min hasta el volcado; el lanzador corta la VM al «[FBMC] FIN»)
#    main: InitB 6 3 + CreateSector32 + SetSMI + BkRead(0x04,3)     [run3]
NF4INJECT=30 python3 "$EV/pb_run_nf4.py" 300 "$EV/run3" /tmp/nflasha4-origen.bin 30
#    b21h: (0x21,3) con handle, primera lectura del proceso        [run6]
NF4MODE=b21h NF4INJECT=30 python3 "$EV/pb_run_nf4.py" 240 "$EV/run6" /tmp/nflasha4-origen.bin 30
#    b21 : (0x21,3) sin handle, primera lectura del proceso        [run7]
NF4MODE=b21 NF4INJECT=30 python3 "$EV/pb_run_nf4.py" 200 "$EV/run7" /tmp/nflasha4-origen.bin 30
#    ver : control con la imagen parcheada (la página 0x9D400 de run3) — no abre 0x31 [run5]
NF4MODE=ver NF4INJECT=30 python3 "$EV/pb_run_nf4.py" 300 "$EV/run5" /tmp/nflasha4-con-sector-31.bin 30

# Perfil: analysis/gui/g22/harness/live/nf4/  (overlay sólo con nf4inject.so; sonyshim.so sale de
# analysis/gui/g22/harness/overlay/cam/usr/lib/sonyshim.so, el del arnés, sin recompilar).
# La imagen se pasa por LIVE_NFLASH4 (lo pone pb_run_nf4.py con su 3er argumento) → SHIMENV lleva
# NFLASH4=<sha256[0:12]> y run.build_initrd la copia a cam/usr/share/nflasha4.img.
