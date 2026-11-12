#!/bin/sh
# T6 (emulador, no cámara): recompila el binder del kernel Debian 6.12.113 con la ABI antigua de 32 bits (protocolo 7, binder_size_t=u32)
# que usa el Android 2.3 de la cámara (el binder moderno usa u64: BINDER_WRITE_READ 0xc0306201 en vez de 0xc0186201 -> EINVAL).
# Sin gcc cruzado: clang (LLVM=1) y las herramientas armhf de kbuild (fixdep, modpost, recordmcount) por qemu-arm (user).
# Uso: build_binder32.sh DIR_TRABAJO   -> DIR_TRABAJO/b32/binder_linux.ko
set -e
W=$(realpath -m "$1"); V=6.12.113; KV=$V+deb13; P=https://deb.debian.org/debian/pool/main/l/linux
mkdir -p "$W/src" "$W/hdr" "$W/arlibc" "$W/b32"
for f in binder.c binder_alloc.c binder_alloc.h binder_internal.h binder_trace.h dbitmap.h; do
  [ -s "$W/b32/$f" ] || curl -sfL -o "$W/b32/$f" "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/plain/drivers/android/$f?h=v$V"
done
for f in linux-headers-$KV-armmp_$V-1_armhf.deb linux-headers-$KV-common_$V-1_all.deb linux-kbuild-${KV}_$V-1_armhf.deb; do
  [ -s "$W/hdr/$f" ] || { curl -sfL -o "$W/hdr/$f" "$P/$f"; bsdtar -xOf "$W/hdr/$f" 'data.tar.*' | bsdtar -xf - -C "$W/hdr"; }
done
[ -e "$W/arlibc/lib" ] || { curl -sfL -o "$W/arlibc/libc6.deb" https://deb.debian.org/debian/pool/main/g/glibc/libc6_2.44-3_armhf.deb
  bsdtar -xOf "$W/arlibc/libc6.deb" 'data.tar.*' | bsdtar -xf - -C "$W/arlibc"; ln -sfn usr/lib "$W/arlibc/lib"; }
H=$W/hdr/usr/src/linux-headers-$KV-armmp; C=$W/hdr/usr/src/linux-headers-$KV-common; K=$W/hdr/usr/lib/linux-kbuild-$KV/scripts
# herramientas armhf de kbuild -> envoltorios qemu-arm (idempotente)
wrap() { [ -e "$1.arm" ] || mv "$1" "$1.arm"; printf '#!/bin/sh\nQEMU_LD_PREFIX=%s exec qemu-arm %s "$@"\n' "$W/arlibc" "$1.arm" > "$1"; chmod +x "$1"; }
wrap "$K/basic/fixdep"; wrap "$K/recordmcount"; wrap "$K/mod/modpost.real-lsb-32"
# modpost (despachador armhf) se sustituye por una llamada directa a la variante lsb-32
printf '#!/bin/sh\nexec %s "$@"\n' "$K/mod/modpost.real-lsb-32" > "$K/mod/modpost"; chmod +x "$K/mod/modpost"
grep -q "^include /usr/src" "$H/Makefile" && sed -i "s|/usr/src/linux-headers-$KV-common|$C|" "$H/Makefile"
# clang en vez de gcc-14; fuera las opciones solo-gcc y -pg (clang emite «mcount», no __gnu_mcount_nc)
cat > "$W/clangw" <<'EOF'
#!/bin/sh
out=; for a in "$@"; do case "$a" in -fconserve-stack|-fno-allow-store-data-races|-mno-thumb-interwork|-pg|-mrecord-mcount|-fno-ipa-sra|-fno-ipa-cp-clone|-fno-partial-inlining|-mtp=cp15) ;; *) out="$out '$a'";; esac; done
eval exec clang $out -w -Wno-error -Wno-unknown-warning-option -Qunused-arguments
EOF
chmod +x "$W/clangw"; sed -i "s|^CC = .*|CC = $W/clangw|" "$H/.kernelvariables"
# el módulo junta binder.o+binder_alloc.o: dos «debug_mask» chocarían en sysfs -> se renombra el de binder_alloc
sed -i 's|module_param_named(debug_mask, binder_alloc_debug_mask|module_param_named(alloc_debug_mask, binder_alloc_debug_mask|' "$W/b32/binder_alloc.c"
cat > "$W/b32/Makefile" <<'EOF'
ccflags-y += -I$(src) -DBINDER_IPC_32BIT
obj-m += binder_linux.o
binder_linux-y := binder.o binder_alloc.o
EOF
make -C "$H" ARCH=arm LLVM=1 M="$W/b32" modules 2>&1 | tail -3
ls -la "$W/b32/binder_linux.ko"
# /dev/uipc mínimo (adición del emulador) con el mismo toolchain
mkdir -p "$W/uipc"; cp "$(dirname "$0")/uipc_stub.c" "$W/uipc/uipc_stub.c"; echo 'obj-m += uipc_stub.o' > "$W/uipc/Makefile"
make -C "$H" ARCH=arm LLVM=1 M="$W/uipc" modules 2>&1 | grep -iE "error" || true
ls -la "$W/uipc/uipc_stub.ko"
