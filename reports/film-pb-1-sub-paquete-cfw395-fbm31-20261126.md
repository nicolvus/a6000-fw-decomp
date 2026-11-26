# FILM-PB-1 · Paquete CFW **3.95** con el `libmpr.so` que crea el sector FBM `0x31` (auditado, sin instalar)

26-11-2026. Paquete construido **offline**: no se ha instalado nada, no se ha tocado la cámara ni
`firmware/`, no se ha usado `mcp_rea`. Base = el **paquete instalado** 3.94
(`build/cfw_avcam_limpio/pkg-3.94`). Lo único que cambia en la partición `/usr` es **`/lib/libmpr.so`**,
que pasa a ser el del parche v3 (`build/cfw_fbm31_sector31_v3/libmpr.so`, probado en el arnés).

## Resumen (20 líneas)

1. **Entrega:** `build/cfw_fbm31_pkg395/pkg-3.95/package-3.95/firmware_packed.dat` — **172 662 936 B**,
   sha256 **`61bfcb79…442a`** — versión **3.95** (base instalada 3.94).
2. **Compatibilidad del parche (comprobada, no supuesta):** el `/lib/libmpr.so` de la 3.94 es **byte a byte** el de
   fábrica 3.21 (`9a74a3bb…4c30`), justo el binario del parche; reaplicado **sobre el de la base** da el mismo `9be37312…00640`.
3. **Cambia en el contenedor:** 2 miembros del `firmware.tar` (`dev/nflasha15` y `part_image.sum`); los otros 102, idénticos.
4. **Cambia en `/usr`:** **1 fichero** de 715 (`/lib/libmpr.so`); vs. el 3.21 de fábrica siguen siendo los 31 de siempre.
5. **Bytes en `libmpr.so`:** 68 B en 2 rangos — gancho `0x7126E6..0x7126E9` (`a2 f7 9b f0` → `28 f2 8b fc`) y cueva
   `0x93B000..0x93B03F` (0x40 B); 64 cambian de valor, 4 ya eran `00`. Tamaño y modo/uid/gid intactos.
6. **Auditoría:** `audit_package_nflasha15.py` con `--base-dat` = el `.dat` 3.94 → **`todo_ok: true`**, 22/22 comprobaciones.
7. **Advertencia:** crear el sector **NO rellena la base de datos** del FBM; tras instalar hay que dejar que la cámara la
   reconstruya (clip nuevo o menú de recuperación de BD) y **solo después** probar la reproducción (§5).
8. **Vuelta atrás:** `3.96` construido y auditado = **contenido exacto de la 3.94** (mismo `firmware.tar`, sha `92dfeb6a…`)
   con número mayor, porque el actualizador solo acepta versiones mayores (§6).
9. **Límite del arnés:** el efecto **no persiste solo**; el sector se recrea en cada arranque y el DFB rota una página de
   control por arranque (§7). Nada probado en cámara: la reproducción de vídeo sigue pendiente de medición física.

## 1. Lo entregado

| Dato | Valor |
|---|---|
| **`.dat`** | `build/cfw_fbm31_pkg395/pkg-3.95/package-3.95/firmware_packed.dat` (**172 662 936 B**) |
| **sha256 del `.dat`** | **`61bfcb793663a33cc5c116bfde12afa15aa57fa70ff60aa2d969152b114b442a`** |
| Versión del contenedor | **3.95** (`version: '3.95'`, modelo `0x41030035`, región 0) |
| `.fdat` | `…/firmware_packed.fdat`, 171 987 456 B, sha256 `ace748078ccc63bb0cfb71f03a0ad18ef9cecbc0fc67b412dc4e33d2faf85c6d` |
| `firmware.tar` de dentro | 171 843 584 B, sha256 `818229d5c0e84156e682d7e390af640893cdc4941edb5ce85d732e68e833141a` |
| `nflasha15` resultante | 86 169 600 B (antes 86 169 088), sha256 `30d8615d1a6a6a7da7f379fef2f58652b316bc6aac880342a9ff7c2c8dbfe3af`, crc32 `30d31076` |
| `libmpr.so` dentro | 10 321 204 B, sha256 **`9be3731213a776dbc5934e7f37d9a7a4ef50480e35b09a4e8b1d0727e0b00640`** |
| Estado | **CONSTRUIDO OFFLINE — INSTALACIÓN NO AUTORIZADA** |

## 2. Comprobación previa: qué `libmpr.so` lleva la 3.94 y si el parche encaja

Medido, no inferido: se descomprimió el TPZL de `nflasha15` de la **3.94** (`4dceb91c…`, idéntico a
`build/cfw_func393/pp/nflasha15-393.bin`) y se volcó `/lib/libmpr.so` con `debugfs`:

| Binario | sha256 | Tamaño |
|---|---|---|
| `/lib/libmpr.so` de la **3.94** | `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30` | 10 321 204 B |
| `/lib/libmpr.so` de fábrica **3.21** (`firmware/extracted/fw321/…/nflasha15_unpacked_unpacked/lib/`) | `9a74a3bb…4c30` | 10 321 204 B |
| Parche v3 ya medido en el arnés | `9be37312…00640` | 10 321 204 B |

**La base 3.94 lleva el `libmpr.so` de fábrica, byte a byte.** Por tanto el parche (que se hizo sobre la
3.21) es compatible tal cual; aun así se reaplicó **sobre el binario extraído de la base** con el mismo
script y el mismo criterio de verificación (`reports/evidence/film-pb-1-sub-fbm-create-20261126/parche_fbm31_v3.py`),
y salió **el mismo sha256**:

| Comprobación del parche (sobre la base 3.94) | Resultado |
|---|---|
| sha256 del original | `9a74a3bb…4c30` (el esperado por el script) |
| Gancho `0x7126E6` | `a2 f7 9b f0` (`bl 0x2B4820`) → `28 f2 8b fc` (`bl 0x93B000`) |
| `0x7126EA` (siguiente) | `96 f5 bb f8`, **no se toca** |
| Cueva `0x93B000..0x93B03F` | 64 B a cero → 28 instrucciones Thumb verificadas una a una (capstone) |
| Relocaciones | **132 021** entradas `.rel*` revisadas, **ninguna** en los 68 B |
| `ldr/adr` pc-relativos a la cueva / punteros u32 a la cueva | **ninguno** (el único candidato, `0x495390`, cae dentro de otra instrucción) |
| Diff | 68 B escritos en 2 rangos, 64 con valor nuevo, **tamaño igual** |
| Cabeceras | cabecera ELF, 5 `PT_*` y 25 secciones idénticas |

## 3. Qué cambia exactamente respecto a la 3.94 (lista de miembros y rangos)

**Contenedor (`firmware.tar`, 104 miembros):** cambian **solo** dos; nada se elimina ni se añade:

| Miembro | Antes (3.94) | Después (3.95) |
|---|---|---|
| `0700_part_image/dev/nflasha15` | 86 169 088 B, crc32 `7d055639` | 86 169 600 B (+512), crc32 `30d31076` |
| `0701_part_image_sum/part_image.sum` | `0,7d055639,0522d600,…,-1,-1,dev/nflasha15,` | `0,30d31076,0522d800,…,-1,-1,dev/nflasha15,` |

**Partición `/usr` (ext2 dentro del TPZL):** 715 ficheros; difiere **1** respecto a la 3.94
(`lib/libmpr.so`), y los mismos **31** de siempre respecto al 3.21 de fábrica (los 30 del CFW heredados
+ `lib/libmpr.so`).

**Bytes cambiados dentro de `libmpr.so`** (offset = VA, la partición se mapea VA==offset):

| Rango | Bytes | Contenido |
|---|---|---|
| `0x7126E6..0x7126E9` | 4 | `a2 f7 9b f0` → `28 f2 8b fc` (gancho: `bl 0x2B4820` → `bl 0x93B000`, en `MprIf::Create 0x712530`) |
| `0x93B000..0x93B03F` | 64 | ceros → cueva (`FBM::Init` → `CreateSector32(0x31,0,&h,&id)` → alta en `0xA3699C[10]`) |

**TPZL:** 2 373 bloques de 64 KiB (los mismos que Sony), 329 recompuestos, contiguos, alineados a 512,
`max_sectores` 129 (= Sony), 0 violaciones del LDEC y **bloque 0 idéntico al de Sony** (R55).
Entre la 3.94 y la 3.95 solo difieren **13 de 2 373** bloques.

## 4. Auditoría (objetivo `todo_ok`)

```bash
TMPDIR=$PWD/build/cfw_fbm31_pkg395/tmp python3 scripts/gui/audit_package_nflasha15.py \
  build/cfw_fbm31_pkg395/pkg-3.95/package-3.95/firmware_packed.dat \
  build/cfw_fbm31_pkg395/files \
  --base-dat build/cfw_avcam_limpio/pkg-3.94/package-3.94/firmware_packed.dat
```

Resultado: **`todo_ok: true`**, 22/22 comprobaciones (contenedor ×7, `tar` ×4, `nflasha15` ×8, `ext2` ×3).
JSON: `reports/evidence/film-pb-1-pkg-cfw395-fbm31-20261126/auditoria-395.json`.
Destacan: descifrado == `.fdat`, `updater.img` oficial 3.21, `version_mayor_que_base` (3.95 > 3.94),
`solo_cambian_los_miembros_previstos` (los 2 de arriba), las 65 líneas de suma verifican,
`bloque_0_identico_a_sony`, `decodificador_independiente_coincide` (`fwtool.lz77`),
`ext2.solo_cambian_los_ficheros_del_paquete` (31), hashes y modo/uid/gid como Sony.

**Comprobaciones del auditor que aquí NO se activan, y por qué no aplican:**
- `--darwin-v3` (2 comprobaciones): verifica el parche EFCS de Darwin. Ese parche **ya está** en la base y no
  se toca: el auditor demuestra que el `tar` solo cambia 2 miembros, así que el Darwin es idéntico byte a byte
  al de la 3.94 (que ya se auditó con la bandera). Activarla solo repetiría una comprobación ya cubierta.
- `--bionz-g22` (3 comprobaciones): lo mismo con `nflasha3`/`AV-CAM.BIN`; tampoco se toca.
- `--sin-wbi`: la 3.94 ya se construyó sin `nflasha5`, así que el chequeo sale como «no se quita nada»
  (`tar.solo_se_quitan_los_previstos` con lista vacía) en lugar de «se quita nflasha5».
- `ext2.fsck_solo_contadores_de_libres`: pasa **por diseño** con avisos de contadores de libres
  (`Free inodes/blocks count wrong`), herencia de restaurar el bloque 0 de Sony en TPZL (R55); no son
  ficheros corruptos ni bloques perdidos.

## 5. AVISO IMPRESCINDIBLE: crear el sector no rellena la base de datos

El parche **solo crea el sector FBM `0x31`** (y lo registra en `0xA3699C[10]`, con lo que `BkRead` deja de
devolver `0x10100001` y devuelve `0x10100003`, que el llamante tolera). **No rellena la base de datos de
sectores**: las entradas de foto/vídeo siguen sin contenido hasta que algo las escriba.

Por eso, después de instalar y **antes** de dar la reproducción por arreglada:

1. Dejar que la cámara **reconstruya la BD**: grabar **un clip nuevo** (con lo que se crea y escribe el
   sector de vídeo con datos reales) **o** usar el **menú de recuperación de BD** del servicio.
2. Reiniciar el MPR (o la cámara) para que `FBM::Init` relea la tabla.
3. **Solo entonces** probar la reproducción de ese clip nuevo y después la de los antiguos.

Si se prueba la reproducción justo tras instalar, sin reconstruir, el síntoma puede seguir igual y **no**
significa que el parche haya fallado.

## 6. Cómo volver atrás (reinstalar la versión anterior con número mayor)

El actualizador **solo acepta versiones mayores** que la instalada, así que no se puede reinstalar la 3.94.
Se construyó ya el paquete de vuelta atrás, con **el contenido exacto de la 3.94** y número **3.96**:

| Dato | Valor |
|---|---|
| `.dat` de vuelta atrás | `build/cfw_fbm31_pkg395/pkg-3.96-rollback/package-3.96/firmware_packed.dat` (**172 661 912 B**) |
| sha256 | **`f5283bf97383dd07f60cb939474615d397141c8248e85211a40eae8c06b76c47`** |
| `firmware.tar` | sha256 `92dfeb6a…` = **el mismo** que el de la 3.94 (mismos `nflasha3`, `nflasha15`, Darwin…) |
| Efecto | deja la cámara exactamente como la 3.94: vuelve el `libmpr.so` de fábrica `9a74a3bb…` |

Comando reproducible (base = `firmware.tar` de la 3.94, **sin** `--darwin-v3`/`--sin-wbi`, que ya están
aplicados en la base):

```bash
TMPDIR=$PWD/build/cfw_fbm31_pkg395/tmp python3 scripts/gui/build_package_nflasha15.py \
  build/cfw_fbm31_pkg395/work/nflasha15-394.bin build/cfw_fbm31_pkg395/pkg-3.96-rollback \
  --base-tar build/cfw_avcam_limpio/pkg-3.94/firmware.tar --version 3.96
```

Y su auditoría (base = el `.dat` 3.95, manifiesto de 30 ficheros sin `libmpr`):

```bash
TMPDIR=$PWD/build/cfw_fbm31_pkg395/tmp python3 scripts/gui/audit_package_nflasha15.py \
  build/cfw_fbm31_pkg395/pkg-3.96-rollback/package-3.96/firmware_packed.dat \
  build/cfw_fbm31_pkg395/files-rollback \
  --base-dat build/cfw_fbm31_pkg395/pkg-3.95/package-3.95/firmware_packed.dat
```

Medido: **`todo_ok: true`**, 22/22 (JSON `…/auditoria-396-rollback.json`); cambian los mismos 2 miembros,
nada se elimina, y `/usr` difiere del 3.21 de fábrica en 30 ficheros (sin `libmpr`).

## 7. Límites conocidos (medidos en el arnés, no en cámara)

- El efecto **no persiste solo**: con el `libmpr.so` de fábrica en el 2º arranque, `CheckExistSector(0x31)`
  vuelve a `0x48`; con el parche se **recrea** en cada arranque y el DFB **rota 1 KiB** de página de control
  por arranque (`0x9D400` → `0x3D800`). La cueva **no** escribe la página de datos base `0x380000`
  (`FlashLib::TermSectorData 0x2B4164`), que sí escribe la vía de consola.
- Por eso **la reconstrucción de la BD (§5) no es opcional**: es lo que aporta los datos del sector.
- No se ha instalado ni probado en cámara: la reproducción de vídeo sigue pendiente de medición física.

## 8. Reproducir el paquete 3.95 (comandos exactos)

```bash
# 0) entorno: ojo, /tmp está lleno (7,7 G); usar TMPDIR en el repo
# 1) parche sobre el libmpr de la base 3.94 (ya volcado de la imagen)
python3 reports/evidence/film-pb-1-sub-fbm-create-20261126/parche_fbm31_v3.py \
  --lib build/cfw_fbm31_pkg395/work/libmpr-394.so --out build/cfw_fbm31_pkg395/libmpr.so
# 2) nflasha15: solo /lib/libmpr.so (31 ficheros = 30 heredados + libmpr)
python3 scripts/gui/build_nflasha15.py \
  firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15 \
  build/cfw_fbm31_pkg395/files build/cfw_fbm31_pkg395/nflasha15-395.bin
# 3) contenedor 3.95 encima del firmware.tar de la 3.94
TMPDIR=$PWD/build/cfw_fbm31_pkg395/tmp python3 scripts/gui/build_package_nflasha15.py \
  build/cfw_fbm31_pkg395/nflasha15-395.bin build/cfw_fbm31_pkg395/pkg-3.95 \
  --base-tar build/cfw_avcam_limpio/pkg-3.94/firmware.tar --version 3.95
```

Nota: `build_nflasha15` exige construir desde la imagen **de fábrica** (el manifiesto reescribe los 30
ficheros heredados con el mismo contenido); partir de la imagen de la 3.94 **falla** porque su bloque 0
lleva a propósito los contadores de libres de Sony (R55) y `e2fsck -fn` devuelve error solo por eso.

## 9. Evidencia

`reports/evidence/film-pb-1-pkg-cfw395-fbm31-20261126/`:

| Fichero | Qué es |
|---|---|
| `parche-sobre-base-394.txt` | salida íntegra del parche reaplicado sobre el libmpr de la 3.94 |
| `build-nflasha15-395.txt` | informe de `build_nflasha15` (bloques recompuestos, crc32, bloque 0) |
| `nflasha15-395.json` | diffs de la imagen nueva contra la 3.94 y contra la de fábrica |
| `diff-arboles.json` | hash por fichero de los 3 volcados ext2 (fábrica, 3.94, 3.95) |
| `build-package-395.txt` / `build-package-396-rollback.txt` | salidas de los empaquetados |
| `auditoria-395.json` / `auditoria-396-rollback.json` | JSON del auditor (objetivo `todo_ok`) |
