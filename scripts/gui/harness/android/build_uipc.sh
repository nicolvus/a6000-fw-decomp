#!/bin/sh
# G22-E T5b/T6 (emulador, no cámara): compila uipc_shared.ko (/dev/uipc compartido entre procesos) para el kernel Debian 6.12.113 del invitado.
# Requiere el entorno que deja build_binder32.sh (cabeceras, clangw, envoltorios qemu-arm). Solo compila: no arranca la VM.
# Uso: build_uipc.sh DIR_TRABAJO   -> DIR_TRABAJO/uipcs/uipc_shared.ko
set -e
S=$(cd "$(dirname "$0")" && pwd); W=$(realpath "$1"); H=$W/hdr/usr/src/linux-headers-6.12.113+deb13-armmp
mkdir -p "$W/uipcs"; cp "$S/uipc_shared.c" "$S/uipc_core.c" "$S/uipc_core.h" "$W/uipcs/"
printf 'ccflags-y += -I$(src) -Wall\nobj-m += uipc_shared.o\nuipc_shared-y := uipc_main.o uipc_core.o\n' > "$W/uipcs/Makefile"
mv "$W/uipcs/uipc_shared.c" "$W/uipcs/uipc_main.c"   # el objeto compuesto no puede llamarse igual que un fuente
# clangw de build_binder32.sh añade -w; aquí se compila sin él para que los avisos se vean
sed 's/ -w -Wno-error//' "$W/clangw" > "$W/clangw_avisos"; chmod +x "$W/clangw_avisos"
make -C "$H" ARCH=arm LLVM=1 CC="$W/clangw_avisos" M="$W/uipcs" modules 2>&1 | grep -E "warning|error" || true
ls -la "$W/uipcs/uipc_shared.ko"
# prueba del invitado: binario ARM estático sin libc
clang --target=armv7a-linux-gnueabihf -marm -O1 -Wall -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -static -fuse-ld=lld \
  -o "$W/uipcs/uipc_guest_test" "$S/uipc_guest_test.c"
cp "$S/prueba_uipc.sh" "$W/uipcs/"
# lanzador del zygote (socket ANDROID_SOCKET_zygote sin init de Android); va a overlay/cam/and/zygote_launch
clang --target=armv7a-linux-gnueabihf -marm -O1 -Wall -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -static -fuse-ld=lld \
  -o "$W/uipcs/zygote_launch" "$S/zygote_launch.c"
# prueba de ashmem.ko en el invitado (mmap privado/compartido como dvmAllocRegion)
clang --target=armv7a-linux-gnueabihf -marm -O1 -Wall -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -static -fuse-ld=lld \
  -o "$W/uipcs/ashmem_guest_test" "$S/ashmem_guest_test.c"
