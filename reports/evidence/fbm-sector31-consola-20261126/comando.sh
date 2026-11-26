#!/bin/sh
# Vía de consola que registra el sector 0x31 en 0xA3699C (FBM LTC 1 / EWBDFD + InitB) — repetición completa.
# Desde la raíz del repo. Todo es QEMU sobre COPIAS en /tmp: no se toca la cámara ni el shim del arnés.
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd); cd "$REPO"
EV=reports/evidence/fbm-sector31-consola-20261126
SR=analysis/gui/g22/harness/sysroot
CAM=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib
OUT=analysis/gui/g22/harness/live/nf4/overlay/cam/usr/lib/nf6inject.so
mkdir -p "$(dirname "$OUT")"

# 0) imágenes de trabajo (10 MiB; los volcados no se versionan)
python3 "$EV/make_page.py"          # /tmp/nflasha4-origen.bin (+ la de run3, no se usa aquí)

# 1) inyector (mismos flags que scripts/gui/harness/shim/build.sh, libc 2.11 del firmware)
touch "$SR/usr/include/arm-linux-gnueabihf/gnu/stubs-soft.h"
clang --target=armv7-linux-gnueabi -mfloat-abi=softfp -mcpu=cortex-a15 -O2 -fno-stack-protector \
  -fPIC -shared -fuse-ld=lld -nostdlib -nostdinc -isystem "$SR/usr/include/arm-linux-gnueabihf" \
  -isystem "$SR/usr/include" -isystem "$(clang -print-resource-dir)/include" -std=gnu99 \
  "$EV/nf6inject.c" -o "$OUT" -L"$CAM" -l:libc-2.11.2.so -l:libdl-2.11.2.so \
  -l:librt-2.11.2.so -l:libpthread-2.11.2.so

# 2) pasadas (cada una ~1 min; el lanzador corta la VM al «[FBMC] FIN»)
#    A) los comandos pedidos, en orden: ChgSec 6 3 / ChgSec 4 3 / CRFB / INRFB / DRWBI / WBI
NF4MODE=orden  NF4INJECT=30 python3 "$EV/pb_run_nf6.py" 300 "$EV/runA-orden" /tmp/nflasha4-origen.bin 30
#    C) la ruta que funciona: EWBDFD 4 3 0 + InitB 6 3 (+ WBI de control y volcado del diff)
NF4MODE=ewbdfd NF4INJECT=30 python3 "$EV/pb_run_nf6.py" 400 "$EV/runC-ewbdfd-wbi" /tmp/nflasha4-origen.bin 30
#    E) ChgSec 4 3 tras EWBDFD: NO crea (handle de origen 0 -> 0x10100006)
NF4MODE=ewchg  NF4INJECT=30 python3 "$EV/pb_run_nf6.py" 360 "$EV/runE-ewbdfd-chgsec" /tmp/nflasha4-origen.bin 30
#    G) la ruta de fábrica: LTC 1 + InitB 6 3 (BkRead = 0)
NF4MODE=ltc    NF4INJECT=30 python3 "$EV/pb_run_nf6.py" 400 "$EV/runG-ltc1" /tmp/nflasha4-origen.bin 30

# 3) imagen resultante en el host (la copia del invitado no sale del QEMU) y reinicio real
python3 "$EV/patch_desde_log.py" "$EV/runC-ewbdfd-wbi/consola.log"    /tmp/nflasha4-tras-ewbdfd.bin
python3 "$EV/patch_desde_log.py" "$EV/runG-ltc1/consola.log"          /tmp/nflasha4-tras-ltc1.bin
NF4MODE=ver    NF4INJECT=30 python3 "$EV/pb_run_nf6.py" 300 "$EV/runD-reinicio"      /tmp/nflasha4-tras-ewbdfd.bin 30
NF4MODE=ver    NF4INJECT=30 python3 "$EV/pb_run_nf6.py" 300 "$EV/runH-reinicio-ltc1" /tmp/nflasha4-tras-ltc1.bin 30
#    F) control: sin la página de datos base 0x380000 (el sector existe, +8 = 0)
python3 - <<'PY'
o = open("/tmp/nflasha4-origen.bin", "rb").read(); n = open("/tmp/nflasha4-tras-ewbdfd.bin", "rb").read()
img = bytearray(o)
for lo, hi in ((0x9D000, 0x9E000), (0xBD000, 0xBE000)):
    i = lo
    while i < hi:
        if o[i] != n[i]:
            j = i
            while j < hi and o[j] != n[j]:
                j += 1
            img[i:j] = n[i:j]; i = j
        else:
            i += 1
open("/tmp/nflasha4-sin-pagina-datos.bin", "wb").write(img)
PY
NF4MODE=ver    NF4INJECT=30 python3 "$EV/pb_run_nf6.py" 240 "$EV/runF-sin-pagina-datos" /tmp/nflasha4-sin-pagina-datos.bin 30

# Perfil: analysis/gui/g22/harness/live/nf4/ (overlay sólo con nf6inject.so; sonyshim.so sale de
# analysis/gui/g22/harness/overlay/cam/usr/lib/sonyshim.so, el del arnés, sin recompilar).
