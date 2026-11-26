#!/bin/sh
# Reproduce el paquete 3.97 (libmpr del parche C) y el rollback 3.98. Todo offline; no toca la cámara.
# Ojo: /tmp suele estar lleno → TMPDIR dentro del repo.
set -e
cd "$(dirname "$0")/../../.."
P=build/cfw_fbm31_pkg397
mkdir -p "$P/work" "$P/tmp"
export TMPDIR=$PWD/$P/tmp

# 0) binario del parche C y comprobación de que la base 3.94 lleva el de fábrica
sha256sum build/cfw_fbm_sector31_c/libmpr.so            # 831142ae…e378e
python3 $P/work/extrae.py                              # vuelca nflasha15-394.bin, usr394.ext2 y libmpr-394.so (9a74a3bb…)
python3 $P/work/prepara_pkg.py                         # files/ (31 ficheros) con libmpr C + MANIFEST
python3 $P/work/diff_libmpr.py                         # rangos 0x7126E6 y 0x93B000 (81 B distintos)
python3 $P/work/desasm_cueva.py                        # desensamblado de la cueva del binario empaquetado

# 1) nflasha15 desde la imagen de FÁBRICA (no desde la 3.94: su bloque 0 hace fallar e2fsck)
python3 scripts/gui/build_nflasha15.py \
  firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15 \
  $P/files $P/nflasha15-397.bin
python3 $P/work/verifica_n15.py                        # diffs vs fábrica y vs 3.94, crc32 y TPZL

# 2) contenedor 3.97 encima del firmware.tar de la 3.94
python3 scripts/gui/build_package_nflasha15.py $P/nflasha15-397.bin $P/pkg-3.97 \
  --base-tar build/cfw_avcam_limpio/pkg-3.94/firmware.tar --version 3.97

# 3) auditoría (objetivo todo_ok)
python3 scripts/gui/audit_package_nflasha15.py $P/pkg-3.97/package-3.97/firmware_packed.dat \
  $P/files --base-dat build/cfw_avcam_limpio/pkg-3.94/package-3.94/firmware_packed.dat \
  > $P/work/auditoria-397.json

# 4) rollback 3.98 = contenido de la 3.94 con número mayor que 3.97
python3 scripts/gui/build_package_nflasha15.py $P/work/nflasha15-394.bin $P/pkg-3.98-rollback \
  --base-tar build/cfw_avcam_limpio/pkg-3.94/firmware.tar --version 3.98
python3 scripts/gui/audit_package_nflasha15.py $P/pkg-3.98-rollback/package-3.98/firmware_packed.dat \
  $P/files-rollback --base-dat $P/pkg-3.97/package-3.97/firmware_packed.dat \
  > $P/work/auditoria-398-rollback.json
python3 $P/work/diff_396_398.py                        # 3.96 y 3.98 solo difieren en la cabecera (36 B)
