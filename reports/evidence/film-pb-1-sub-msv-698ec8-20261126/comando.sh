#!/bin/sh
# Repetición completa: ¿devuelve 0 el cargador del IFO (0x698EC8) y 0x3AFA94 con el sector 0x31 registrado?
# Desde la raíz del repo. Todo QEMU sobre COPIAS en /tmp: no se toca la cámara, ni el shim del arnés, ni git.
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd); cd "$REPO"
EV=reports/evidence/film-pb-1-sub-msv-698ec8-20261126
SR=analysis/gui/g22/harness/sysroot
CAM=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib
OUT=analysis/gui/g22/harness/live/nf4/overlay/cam/usr/lib/msvprobe.so
mkdir -p "$(dirname "$OUT")"

# 0) copia de trabajo de /dev/nflasha4 (10 MiB; el volcado no se versiona)
[ -s /tmp/nflasha4-origen.bin ] || cp analysis/camera-dumps/nand-20261020/dev_nflasha4.bin /tmp/nflasha4-origen.bin
sha256sum /tmp/nflasha4-origen.bin     # a5ab15ca743950d6a8c64c17a8ed024cddc6d5c94a24a08cf60ca5d4e9ac7247

# 1) inyector (mismos flags que scripts/gui/harness/shim/build.sh, libc 2.11 del firmware)
touch "$SR/usr/include/arm-linux-gnueabihf/gnu/stubs-soft.h"
clang --target=armv7-linux-gnueabi -mfloat-abi=softfp -mcpu=cortex-a15 -O2 -fno-stack-protector \
  -fPIC -shared -fuse-ld=lld -nostdlib -nostdinc -isystem "$SR/usr/include/arm-linux-gnueabihf" \
  -isystem "$SR/usr/include" -isystem "$(clang -print-resource-dir)/include" -std=gnu99 \
  "$EV/msvprobe.c" -o "$OUT" -L"$CAM" -l:libc-2.11.2.so -l:libdl-2.11.2.so \
  -l:librt-2.11.2.so -l:libpthread-2.11.2.so

# 2) pasadas (perfil live/nf4, NFLASH4=1 lo pone el lanzador con LIVE_NFLASH4)
#    run1/run2: 6 trampas en la cadena del IFO -> 0 capturas (la cadena no se ejecuta en el arnés)
MSVPROBE=30 python3 "$EV/pb_run_msv.py" 480 "$EV/run1" /tmp/nflasha4-origen.bin 30
MSVPROBE=25 MSVWAIT=240 python3 "$EV/pb_run_msv.py" 460 "$EV/run2" /tmp/nflasha4-origen.bin 25
#    run3: construye la clase con su ctor real 0x3B04A4 y llama a 0x3AFA94 (se bloquea en la traza OSAL)
MSVPROBE=40 MSVWAIT=5 python3 "$EV/pb_run_msv.py" 300 "$EV/run3" /tmp/nflasha4-origen.bin 40
#    run5: sólo las dos macros TRACE anuladas (bx lr) -> la llamada sigue sin volver
#    run6: la receta que sí funciona (sin llamadas inyectadas): sector + BkRead
MSVONLY=1 MSVPROBE=40 MSVWAIT=5 python3 "$EV/pb_run_msv.py" 260 "$EV/run6" /tmp/nflasha4-origen.bin 40
MSVPROBE=40 MSVWAIT=5 python3 "$EV/pb_run_msv.py" 300 "$EV/run5" /tmp/nflasha4-origen.bin 40

# Perfil: analysis/gui/g22/harness/live/nf4/ (overlay sólo con msvprobe.so; sonyshim.so es el del arnés).
# Desensamblados citados: $EV/dis/*.txt  (elfhelper.py de film-pb-1-sub-tabla-readers-20261126).
