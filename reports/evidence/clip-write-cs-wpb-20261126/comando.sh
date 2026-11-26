#!/bin/sh
# Repetición completa: camino de ESCRITURA de un clip (ChangeSector + WritePackBegin/Add/End) sobre
# /dev/nflasha4 emulado (NFLASH4=1), antes y después de crear el sector FBM 0x31, más la prueba
# causal del campo `fn` de la tabla estática 0x9D23FC.
# Desde la raíz del repo. No toca la cámara ni el shim del arnés (sólo añade un 2º .so precargado).
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd); cd "$REPO"
EV=reports/evidence/clip-write-cs-wpb-20261126
SR=analysis/gui/g22/harness/sysroot
CAM=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib
OUT=analysis/gui/g22/harness/live/nf4/overlay/cam/usr/lib/nf4clip.so
mkdir -p "$(dirname "$OUT")"

# 0) imágenes de trabajo en /tmp (10 MiB; los volcados de NAND no se versionan)
#    prístina = el volcado del repo; «post» = volcado + las 3 páginas de 1 KiB que dejó el parche C
python3 reports/evidence/fbm-sector31-c-20261126/reconstruye_imagen.py /tmp/nf4-post.img

# 1) sonda (mismos flags que scripts/gui/harness/shim/build.sh, libc 2.11 del firmware)
touch "$SR/usr/include/arm-linux-gnueabihf/gnu/stubs-soft.h"
clang --target=armv7-linux-gnueabi -mfloat-abi=softfp -mcpu=cortex-a15 -O2 -fno-stack-protector \
  -fPIC -shared -fuse-ld=lld -nostdlib -nostdinc -isystem "$SR/usr/include/arm-linux-gnueabihf" \
  -isystem "$SR/usr/include" -isystem "$(clang -print-resource-dir)/include" -std=gnu99 \
  "$EV/nf4clip.c" -o "$OUT" -L"$CAM" -l:libc-2.11.2.so -l:libdl-2.11.2.so \
  -l:librt-2.11.2.so -l:libpthread-2.11.2.so
sha256sum "$OUT"

# 2) «antes»: imagen prístina (tabla 1/30, sector 0x31 sin handle)
NF4MODE=pre  NF4INJECT=30 python3 "$EV/pb_run_clip.py" 240 "$EV/runPre"  analysis/camera-dumps/nand-20261020/dev_nflasha4.bin 30
# 3) «después»: imagen con el sector 0x31 ya creado y persistido (tabla 2/30, idx10 h1/om6)
NF4MODE=post NF4INJECT=30 python3 "$EV/pb_run_clip.py" 240 "$EV/runPost" /tmp/nf4-post.img 30
# 4) control con `FBM InitB 6 3` en el mismo proceso (sin fn: no crea nada)
NF4MODE=both NF4INJECT=30 python3 "$EV/pb_run_clip.py" 240 "$EV/runBoth" analysis/camera-dumps/nand-20261020/dev_nflasha4.bin 30
# 5) prueba causal A: `fn` en 0x9D23FC[13] SIN sector (ChangeSector no lo crea; WriteBaseData sí)
NF4MODE=fn   NF4INJECT=30 python3 "$EV/pb_run_clip.py" 240 "$EV/runFn"  analysis/camera-dumps/nand-20261020/dev_nflasha4.bin 30
# 6) prueba causal B: `fn` + sector 0x31 ya creado (el clip se escribe de verdad)
NF4MODE=fnpost NF4INJECT=30 python3 "$EV/pb_run_clip.py" 240 "$EV/runFnPost" /tmp/nf4-post.img 30

# Perfil: analysis/gui/g22/harness/live/nf4/  (overlay con nf4clip.so; sonyshim.so es el del arnés)
# La imagen se pasa por LIVE_NFLASH4 (pb_run_clip.py, 3.er argumento) → SHIMENV lleva NFLASH4=<sha256[0:12]>
# y run.build_initrd la copia a cam/usr/share/nflasha4.img (el shim la replica en /nflasha4.img escribible).
