# Evidencia · paquete CFW 3.95 con el `libmpr.so` del sector FBM `0x31`

26-11-2026. Todo **offline**: sin cámara, sin instalar, sin `firmware/` modificado, sin `mcp_rea`.
Informe: [`reports/film-pb-1-sub-paquete-cfw395-fbm31-20261126.md`](../../film-pb-1-sub-paquete-cfw395-fbm31-20261126.md).

## Qué hay aquí

| Fichero | Qué es |
|---|---|
| `parche-sobre-base-394.txt` | salida íntegra de `parche_fbm31_v3.py` aplicado al `/lib/libmpr.so` **extraído de la base 3.94** (no al de fábrica): gancho, cueva, 132 021 relocaciones, `ldr/adr`, punteros, diff, ELF, desensamblado, sha256 |
| `build-nflasha15-395.txt` | informe de `scripts/gui/build_nflasha15.py` (2373 bloques, 329 recompuestos, crc32 `30d31076`, bloque 0 = Sony) |
| `nflasha15-395.json` | la imagen 3.95 frente a la 3.94 y frente a la de fábrica: bloques distintos, ficheros distintos, atributos y tamaño del `libmpr` dentro |
| `diff-arboles.json` | sha256 por fichero de los tres volcados ext2 (fábrica 3.21, 3.94, 3.95): `vs_394` = **solo** `lib/libmpr.so`; `vs_stock` = 31 |
| `MANIFEST-nflasha15-31-ficheros.json` | manifiesto usado para reconstruir `nflasha15` y por el auditor (30 heredados + `lib/libmpr.so`) |
| `build-package-395.txt` | salida de `build_package_nflasha15.py` para la 3.95 (versión, sha256 del `.dat`, línea de `part_image.sum`) |
| `build-package-396-rollback.txt` | lo mismo para la vuelta atrás 3.96 |
| `auditoria-395.json` | JSON del auditor del `.dat` **3.95** con `--base-dat` 3.94 → **`todo_ok: true`** (22/22) |
| `auditoria-396-rollback.json` | JSON del auditor del `.dat` **3.96** con `--base-dat` 3.95 → **`todo_ok: true`** (22/22) |
| `hashes.json` | resumen de sha256/tamaños de `.dat`, `.fdat`, `firmware.tar`, `nflasha15` y `libmpr` de ambos paquetes |

## Artefactos (fuera de `reports/`, en `build/`)

| Paquete | `.dat` | sha256 | Tamaño |
|---|---|---|---|
| **3.95** (con el parche) | `build/cfw_fbm31_pkg395/pkg-3.95/package-3.95/firmware_packed.dat` | `61bfcb793663a33cc5c116bfde12afa15aa57fa70ff60aa2d969152b114b442a` | 172 662 936 B |
| **3.96** (vuelta atrás) | `build/cfw_fbm31_pkg395/pkg-3.96-rollback/package-3.96/firmware_packed.dat` | `f5283bf97383dd07f60cb939474615d397141c8248e85211a40eae8c06b76c47` | 172 661 912 B |

Intermedios reproducibles: `build/cfw_fbm31_pkg395/work/nflasha15-394.bin` (imagen de la base, sha
`4dceb91c…`), `build/cfw_fbm31_pkg395/work/libmpr-394.so` (sha `9a74a3bb…`),
`build/cfw_fbm31_pkg395/libmpr.so` (parcheado, sha `9be37312…00640`),
`build/cfw_fbm31_pkg395/nflasha15-395.bin` (sha `30d8615d…`), `build/cfw_fbm31_pkg395/files/` (paquete de
`build_nflasha15`) y `build/cfw_fbm31_pkg395/files-rollback/` (manifiesto de 30 ficheros para auditar la 3.96).

## Cómo se reprodujo (resumen)

```bash
# libmpr de la base 3.94 → fuera de la imagen TPZL de nflasha15, con debugfs
# parche v3 sobre ESE binario (mismo script y criterio que el sub-encargo del parche)
python3 reports/evidence/film-pb-1-sub-fbm-create-20261126/parche_fbm31_v3.py \
  --lib build/cfw_fbm31_pkg395/work/libmpr-394.so --out build/cfw_fbm31_pkg395/libmpr.so
# nflasha15 desde la imagen de fábrica + 31 ficheros (los 30 del CFW y el libmpr nuevo)
python3 scripts/gui/build_nflasha15.py \
  firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15 \
  build/cfw_fbm31_pkg395/files build/cfw_fbm31_pkg395/nflasha15-395.bin
# contenedor 3.95 encima del firmware.tar de la 3.94
TMPDIR=$PWD/build/cfw_fbm31_pkg395/tmp python3 scripts/gui/build_package_nflasha15.py \
  build/cfw_fbm31_pkg395/nflasha15-395.bin build/cfw_fbm31_pkg395/pkg-3.95 \
  --base-tar build/cfw_avcam_limpio/pkg-3.94/firmware.tar --version 3.95
# auditoría
TMPDIR=$PWD/build/cfw_fbm31_pkg395/tmp python3 scripts/gui/audit_package_nflasha15.py \
  build/cfw_fbm31_pkg395/pkg-3.95/package-3.95/firmware_packed.dat \
  build/cfw_fbm31_pkg395/files \
  --base-dat build/cfw_avcam_limpio/pkg-3.94/package-3.94/firmware_packed.dat
```

Nota de entorno: `/tmp` estaba al 100 % (7,7 G, tmpfs) y `fwtool unpack` falla con `ENOSPC`; por eso todo se
lanzó con `TMPDIR` dentro del repo. No es un problema del paquete: el `.dat` 3.94 falla igual en `/tmp`.
