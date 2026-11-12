#!/bin/sh
# T6 (emulador, no cámara): compila ashmem (drivers/staging/android de Linux 5.15, retirado del kernel en 5.18) como módulo para el
# kernel Debian 6.12.113 del arnés T6. El Dalvik de la cámara (libdvm.so: «dalvik-heap», LinearAlloc, caché JIT) y libcutils exigen /dev/ashmem.
# Port mínimo a 6.12: mm_get_unmapped_area, vm_flags_clear, sin shrinker (las regiones «unpinned» nunca se purgan; basta para arrancar).
# Requiere el entorno que deja build_binder32.sh (cabeceras, clangw, envoltorios qemu-arm). Solo compila: no arranca la VM.
# Uso: build_ashmem.sh DIR_TRABAJO   -> DIR_TRABAJO/ash/ashmem.ko
set -e
W=$(realpath "$1"); V=5.15.170; H=$W/hdr/usr/src/linux-headers-6.12.113+deb13-armmp
B="https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/plain/drivers/staging/android"
mkdir -p "$W/ash/uapi"; cd "$W/ash"
for f in ashmem.c ashmem.h uapi/ashmem.h; do [ -s "$f.orig" ] || curl -sfL -o "$f.orig" "$B/$f?h=v$V"; cp "$f.orig" "$f"; done
sed -i -e 's|current->mm->get_unmapped_area(file, addr|mm_get_unmapped_area(current->mm, file, addr|' \
       -e 's|vma->vm_flags &= ~calc_vm_may_flags(~asma->prot_mask);|vm_flags_clear(vma, calc_vm_may_flags(~asma->prot_mask));|' \
       -e 's|ret = register_shrinker(&ashmem_shrinker);|ret = 0; /* shortcut: sin shrinker en 6.12 (API shrinker_alloc); añadirlo si hiciera falta purgar */|' \
       -e 's|^\t\t\tvmfile_fops = \*vmfile->f_op;|&\n\t\t\tshmem_mmap_orig = vmfile->f_op->mmap;|' \
       -e 's|ret = shmem_zero_setup(vma);|ret = shmem_mmap_orig(asma->file, vma); /* shmem_zero_setup ya no se exporta */|' \
       -e 's|^static int ashmem_mmap(struct file \*file, struct vm_area_struct \*vma)$|static int (*shmem_mmap_orig)(struct file *, struct vm_area_struct *);\n&|' ashmem.c
echo 'MODULE_LICENSE("GPL");' >> ashmem.c
echo 'obj-m += ashmem.o' > Makefile
make -C "$H" ARCH=arm LLVM=1 M="$W/ash" modules 2>&1 | grep -E "error" || true
ls -la "$W/ash/ashmem.ko"
