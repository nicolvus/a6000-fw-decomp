#!/bin/sh
# Compila las herramientas de ptrace para la cámara (ARM EABI estático, sin libc). Requiere clang y lld.
cd "$(dirname "$0")"
clang --target=arm-linux-gnueabi -march=armv7-a -marm -O1 -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -static -fuse-ld=lld -Wl,--no-dynamic-linker sctrace.c -o sctrace
clang --target=arm-linux-gnueabi -march=armv7-a -marm -O1 -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -static -fuse-ld=lld -Wl,--no-dynamic-linker ptcall.c  -o ptcall
clang --target=arm-linux-gnueabi -march=armv7-a -marm -Os -ffreestanding -fno-builtin -fno-stack-protector -nostdlib -static -fuse-ld=lld -Wl,--no-dynamic-linker -Wl,-z,noseparate-code camrw.c -o camrw
