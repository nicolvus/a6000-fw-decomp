# E26-R14 — RAMCFG, tabla BOS y geometría FAT de Loader3

Fecha: 30-10-2026. Continúa [R13](e26-r13-led-error-provenance.md) (`37976917`). **Solo análisis estático y lectura de archivos existentes.** No se interactuó con la cámara, no se escribió ninguna imagen y no se generó ningún artefacto instalable. Los volcados originales no se tocaron.

Etiquetas: **BINARIO** = desensamblado de `bootloader.bin` (Loader3) · **DATOS** = decodificado de volcados/paquetes reales · **SCRIPT** = lo dice un script del actualizador (no prueba que se ejecutara así) · **HIPÓTESIS** = sobre la cámara real, sin prueba física.

Código: [`r14_backup.py`](../../analysis/e26-recovery/r14_backup.py) (lector BK4, RAMCFG, BOS, FAT) · [`r14-ramcfg-bos-fat.py`](../../analysis/e26-recovery/r14-ramcfg-bos-fat.py) (ejecutor) · [`tests/test_e26_r14_ramcfg_bos.py`](../../tests/test_e26_r14_ramcfg_bos.py) (8 pruebas).

## 1. Resumen ejecutivo

1. **DATOS + BINARIO. RAMCFG está resuelto.** Es el elemento `0xfa0080` (9216 B = 64 entradas de `0x90` B) del Backup BK4, y las **33 copias** del repo (31 volcados + `\Backup.bin` y `\Backup.bak` de `nflasha2`) y las **22 plantillas** de los paquetes 3.21 oficial y 3.25 integrado tienen **el mismo RAMCFG** (SHA-256 `01b799a4…cd42`). Lista de 6 archivos: `\sabin\idt_cam.bin`, `\sabin\sa_dfdet.bin`, `\av-cam.bin`, `\kemco.txt` (partición 2), `\initrd.img`, `\vmlinux.bin` (partición 3).
2. **El «Backup» de Loader3 es un archivo FAT.** Loader3 monta la partición 2 (`nflasha2`, FAT12) y lee `\Backup.bin` (o `\Backup.bak`); RAMCFG sale de ahí. La partición 3 (`nflasha3`, tipo 3 en BOS) es un volumen FAT **dentro de un contenedor TPZL**. Es decir, **los datos que la actualización 3.25 recompone (`nflasha3`) son exactamente los que Loader3 lee para cargar `av-cam.bin`, `initrd.img` y `vmlinux.bin`.**
3. **BINARIO. −302 es el código de «fallo de FAT»:** el lector de sectores `c01f4690` convierte **cualquier** fallo de lectura de la partición 2 o 3 en −302 (nuevo respecto a R13), además de PBR/FAT con geometría no admitida, archivo ausente, archivo vacío y cadena de clústeres rota. La firma BOS incorrecta también da −302; un fallo de lectura de BOS da −1.
4. **DATOS. Todas las condiciones se cumplen en todas las imágenes disponibles.** Tabla BOS con firma `8246`; `nflasha2` FAT12 (512 B/sector, cluster 16 KiB, `0xAA55`, ID FAT = BPB); `nflasha3` (cámara 3.21, oficial 3.21, integrada 3.25) FAT12 con la misma geometría y los cinco archivos presentes, no vacíos y dentro de sus ventanas. La imagen integrada 3.25 difiere de la oficial 3.21 en **89 bytes de `av-cam.bin`** y nada más (BPB, FAT y directorios idénticos). **Por tanto ninguna imagen explica −302: haría falta un estado físico distinto del de las imágenes.**
5. **SCRIPT.** El actualizador **puede** escribir los tres conjuntos de datos: `edisx.elf /dev/nflasha partinf.conf` (tabla de particiones, según modo), `uc_mkfs.elf` (formateo FAT según modo), `ud_keep_backup`/`cp … /setting/Backup.bin` (el archivo con RAMCFG) y el volcado de `nflasha3`. No se demuestra qué ocurrió en la cámara del incidente.
6. **Decisión: C.** Ambas rutas quedan caracterizadas con sus condiciones exactas; la evidencia histórica no discrimina el estado físico actual (sección 14).

### Precisión trazable sobre R13 (no se altera R13)

- **Precisión de R13 §3 (P3–P6 «solo vía montaje de P2»):** además de `c01f2f24`, el montaje de la partición 2 ocurre en «Switch Bkup» (`c01f49d2`, `c01f4a42`), cuyo fallo sí llega al LED salvo que exista `\updater\mode`. R13 descartó los montajes de `159a`, `1d6a` y `068a`, y eso sigue siendo cierto.
- **Precisión de R13 §3 (P2 «`c01f4654` devuelve ≤ 0»):** `c01f4654` y `c01f45cc` también devuelven −302 por sí mismas (dirent no encontrado, cadena de clústeres, `c01f4690`); el lector de sectores `c01f4690` convierte cualquier fallo de la partición 2 o 3 en −302.

## 2. Inventario de fuentes y hashes

| Fuente | Procedencia | SHA-256 |
|---|---|---|
| `analysis/camera-dumps/updater-20261020-175427/bootloader.bin` | histórico, leído de la cámara (Loader3 en `0x22800`) | `eb420385120f2cd7c9b071f67ce5808721b7de44fb78e2884a856e3c438a327f` |
| `analysis/camera-dumps/nand-20261020/dev_nflasha.bin` (sector 0 = BOS) | histórico, NAND 3.21 (23:16 del 20-10) | `472514b9468b3d5cdbd2a8a78c2804a6e7bc2f7371525677e2572afaffacdfbf` |
| `…/nand-20261020/dev_nflasha2.bin` | histórico, FAT12 (`\Backup.bin`, `\kemco.txt`) | `ac08eecf452a090e59553ff7ce4dc72d98320d8244d7494b43ad03b5995e0b0c` |
| `…/nand-20261020/dev_nflasha3.bin` | histórico, TPZL 3.21 + relleno `0xFF` | `ea0a11fd90240d5df946f2a60ba335172db6790eae99f6ae7bde19bb00f8b5c6` |
| `firmware/extracted/fw321/…/0700_part_image/dev/nflasha3` | **oficial** 3.21 | `93d4a1f089e306d14a9c48732a0be33427951966db88b30ec48af24a92963765` |
| `analysis/e25-27/artifacts/nflasha3.integrated.bin` | **integrada/modificada** 3.25 (no oficial) | `bb9ce25a073d1ccc990d8ee1fdd75322c703d5d2a4020ab5e7daeaf8d23d546c` |
| `analysis/camera-dumps/20261020-first/backup_flash.bin` (y 30 copias más) | histórico, BK4 de 852 647 B | `60a810eb2f3d0348788851000f8678a1f24d9eced04f233c1802acc7f539a18b` |
| RAMCFG (`0xfa0080`) | idéntico en 55 BK4 | `01b799a4b697a0a9120f5aa6d53ac138c1f85747897c5916b02660aabf11cd42` |
| `firmware/extracted/fw321/updater.img_unpacked/bin/endupdate.sh` | **oficial** 3.21 | `f2a049e4f33cd9ce054bcee00014d2a2f66cb83162695f97a63080b58a37d47f` |
| `…/updater.img_unpacked/bin/us_mkfs.sh` | **oficial** 3.21 | `d5376365be890b72f2dd9f54a63f80b4d49302cf537539430adadcd937e6b901` |
| `…/0300_partconf/partinf.conf` | oficial 3.21 (= el del paquete integrado 3.25) | `c622e17b5aa83282b013a0d7b571243e30d7b8e39e8d3792ae2b1143feb80d26` |

Las 55 copias BK4 = 31 archivos de `camera-dumps` + 2 copias en `nflasha2` + 11 plantillas oficiales 3.21 + 11 integradas 3.25. **Límite:** el repo no contiene el `updater.img` ni el `endupdate.sh` de 3.25; los scripts citados son los de 3.21.

## 3. Formato de RAMCFG (Q1)

**Contenedor BK4 (BINARIO `c01fa070`, `c01fa052`, `c01fa02c`, `c01fa0c0`, `c01fa0f2`, `c01f68bc`).** Cabecera: `BK4` en `+0xc`; `u32` en `+0x10` = número de grupos (403). Tabla de grupos en `+0x100`, filas de 6 B (`u16` cuenta, `u32` índice del primer elemento); tabla de elementos tras ella (`+0x100 + grupos·6`), filas de 6 B (`u16`, `u32` puntero). ID = `grupo<<16 | elemento`; puntero `0xFFFFFFFF` = ausente. Byte alto del puntero: `0x00` → tamaño `u16` en `off`, capacidad en `off+2`, datos en `off+4`; `0xFF` → tamaño en `off`, datos en `off+2`; otro → tamaño = ese byte, datos en `off`. Se verificó leyendo `0xfa0006` (4 B) y `0xfa0080`.

**RAMCFG (BINARIO `c01f2fe8`, `c01f2f24`; DATOS).** `0xfa0006 + 0x7a = 0xfa0080` se copia a `0xc005c000`. El tamaño debe ser ≤ `0x2400` (si no, `CFG_W:RAMCFG size overflow`, solo aviso). Número de entradas = tamaño/`0x90` = 64. Entrada:

| Offset | Campo | Uso verificado |
|---|---|---|
| `+0x00` | partición | `c01f3eb6(partición)`: 2 o 3 |
| `+0x04` | dirección destino | buffer de `c01f4654` |
| `+0x08` | dirección final | ventana = final − destino + 1; solo avisa si el archivo la excede |
| `+0x0c` | flags | bits 20–23: máscara de «fase»; bits 24–27: modos que la cargan; bit 31: es el kernel (`vmlinux`) |
| `+0x10…` | ruta ASCII (128 B) | se le quitan las comillas `"`; coincide el nombre 8.3 de 11 bytes |

- **Orden y fin:** secuencial desde la entrada 0; termina en la primera entrada con los cuatro primeros `u32` a cero (`c01f303a`–`c01f3046`) → en esta tabla, tras la entrada 5 (58 entradas vacías).
- **Selección por modo (`c01f304c`–`c01f307a`):** `(modo & 0xf00000) == (flags & 0xf00000)` y `flags & (modo & 0xf000000) != 0`; si además `c01f2282()` ≠ 0 la entrada se omite (`CFG:skip`). Los modos que pasan a `c01f2fe8`: `0x1000000` (arranque normal por defecto y «HotOFF»), `0x4000000` (arranque normal con modo de arranque `0xa`/`0xb`, y «Normal load OFF»), `0x2000000` (modo 2), y cada uno con `|0x100000` en la «Early load».
- **Efecto con este RAMCFG (SCRIPT/BINARIO, probado en pruebas):** `0x1000000` → las 6 entradas; `0x4000000` → solo `idt_cam.bin` y `av-cam.bin`; `0x2000000` y la «Early load» (bit 20) → ninguna.
- **Entrada kernel (bit 31):** tras cargarla, `(flags>>28)&7` se compara con el núcleo actual (`c01f0200`); si coincide, el destino se guarda como punto de entrada (`0xc00e0028`); si no, se despierta la otra CPU (`CFG:Wake cpu`).
- **Vacío/corrupto:** una entrada con ruta vacía no se detecta como error antes de `c01f4654`; una ruta inexistente → −302; un RAMCFG ausente (`0xfa0080` no está) → `c01f498c` falla → `c01f2fe8` devuelve −303.
- **Compuerta previa:** `c01f2fe8` solo continúa si el Backup activo vino de `\Backup.bin` (estado 1, `c01f4aec`); si vino de `\Backup.bak` (2) o de memoria (3) devuelve **−303** (patrón 0/3/3, no el observado).

## 4. Registros Backup localizados (Q2)

**DATOS.** `0xfa0080` está presente en **todas** las copias BK4 (31 volcados, 2 copias en `nflasha2`, 22 plantillas de paquete). Hay **un único** RAMCFG (hash `01b799a4…`). Clasificación: **evidencia real** (volcados de la cámara y plantillas oficiales/integradas); no hay candidatas ni coincidencias no demostradas. Los BK4 completos sí difieren entre sí (datos de usuario/calibración), pero ninguna diferencia toca `0xfa0080`.

Otros elementos que usa el mismo tronco de arranque (para el mapa): `0xf9014a` (PORTCFG, 4608 B), `0xfc0000` (INTCFG, 3072 B), `0xfb0000` (REGCFG, 768 B) — se aplican en `c01f3108` («Run Config(init HW)»), no producen −302.

## 5. Lista de archivos de configuración (Q3, Q4)

| N | Part. | Ruta | Destino | Ventana | Modos | Si falta/está vacío | Observado (3.21 cam / 3.21 of. / 3.25 int.) |
|---:|---:|---|---|---:|---|---|---|
| 0 | 3 | `\sabin\idt_cam.bin` | `0x83501000` | 256 KiB | `0x1000000`, `0x4000000` | −302 | 214 496 B, idéntico en las 3 |
| 1 | 3 | `\sabin\sa_dfdet.bin` | `0x96800000` | 192 KiB | `0x1000000` | −302 | 155 780 B, idéntico |
| 2 | 3 | `\av-cam.bin` | `0x83541000` | 12 MiB | `0x1000000`, `0x4000000` | −302 | 11 427 236 B; la 3.25 integrada difiere en 89 B |
| 3 | 2 | `\kemco.txt` | `0x80033000` | 4 KiB | `0x1000000` | −302 | 2516 B (línea de arranque del kernel) |
| 4 | 3 | `\initrd.img` | `0x80628000` | 8 MiB | `0x1000000` | −302 | 4 079 616 B, idéntico |
| 5 | 3 | `\vmlinux.bin` | `0x80038000` | 5,94 MiB | `0x1000000` (kernel, bit 31) | −302 | 3 478 912 B, idéntico |

**¿Qué entradas pueden producir −302 (Q4)?** Todas, por la misma vía (`c01f2f24`, `c01f2f8c`/`c01f2f9a`): dirent no encontrado, archivo de longitud 0, o fallo de lectura de sector/cluster convertido por `c01f4690`/`c01f460c`. El desbordamiento de ventana **no** es error (solo `CFG_W`). **No es demostrable cuál** sin estado físico. Obligatorio frente a opcional: el código no distingue; todas las entradas seleccionadas son obligatorias (un valor `<0` aborta con ese código).

## 6. Estructura BOS (Q5, Q6)

**BINARIO.** `c01f2b7c(buf=0xc00e04ac, 0x200)` → `c01f2b2e`: abre el dispositivo (`0xc00e0314`, `c01f9d74`), se posiciona en 0, lee 0x200 B, cierra; cualquier fallo devuelve **−1**. `c01f2c98`: fallo → `BOS_E:Load partition error` y devuelve ese −1; firma `[0xc00e04ac] != 0x36343238` → `BOS_E:Partition signature error` y **−302**. **Sí distingue** lectura fallida (−1) de firma inválida (−302). Se invoca en la etapa «Init FAT» (`c01f3d50` desde `c01f117e`), la primera tras «Init BlkDev». No hay copia alternativa de BOS en el código.

**Firma:** `0x36343238` = ASCII `8246` (cabecera `82461.00`).

**Filas (DATOS, `dev_nflasha.bin[0:0x200]`; `c01f2c2a`):** `0x10 + 16·n`, campos `u32`: inicio (bytes), tamaño, tipo, `0xffffffff`. Tipo 3 → lectura por el camino TPZL (`c01f9a66`/`c01f9bd0`); otro → lectura directa.

| n | Inicio | Tamaño | Tipo | Identificado |
|---:|---:|---:|---:|---|
| 1 | `0x040000` | 6 MiB | 1 | `nflasha1` |
| 2 | `0x640000` | 13 MiB | 1 | `nflasha2` (FAT12: Backup, kemco) |
| 3 | `0x1340000` | 30 MiB | **3** | `nflasha3` (TPZL → FAT12) |
| 4 | `0x3140000` | 10 MiB | 0 | `nflasha4` (MPR) |
| 5 | `0x3b40000` | 60 MiB | 2 | `nflasha5` |
| 7 | `0x7c40000` | 4 MiB | 3 | `nflasha7` |

Un BOS verificable existe: **sector 0 del volcado `dev_nflasha.bin` 3.21** (firma correcta, tabla coincidente con `partinf.conf`). No existe BOS de la cámara después del incidente. «Firma incorrecta» no implica daño físico: solo dice que esos 512 B no empiezan por `8246` (pueden estar borrados, sin escribir, o ser una lectura incorrecta que no devolvió error).

## 7. Comparación FAT 3.21 / 3.25 (Q7, Q8)

Condiciones (BINARIO `c01f3e54`, `c01f3d8a`, `c01f3f6a`): `0xAA55` en `0x1fe`; 512 B/sector; sectores/cluster × 512 = `0x4000`; sectores/FAT16 ≠ 0; `FAT[0]` = byte de medio del BPB; nº de clústeres < `0xff5` → FAT12, < `0xfff5` → FAT16, si no → error.

| Volumen | Procedencia | `0xAA55` | 512 B | 16 KiB | FAT ID | Tipo | Archivos RAMCFG |
|---|---|:-:|:-:|:-:|:-:|---|---|
| `nflasha2` | histórico cámara 3.21 | sí | sí | sí | `0xf8`=`0xf8` | FAT12 (830 cl.) | `\Backup.bin` 852 647 B, `\Backup.bak`, `\kemco.txt` 2516 B presentes |
| `nflasha3` | histórico cámara 3.21 | sí | sí | sí | sí | FAT12 (1470 cl.) | 5/5 presentes, no vacíos |
| `nflasha3` | oficial 3.21 | sí | sí | sí | sí | FAT12 (1470 cl.) | 5/5 |
| `nflasha3` | **integrada 3.25 (modificada)** | sí | sí | sí | sí | FAT12 (1470 cl.) | 5/5 |

- Volumen descomprimido de la cámara = oficial 3.21 byte a byte; 3.25 integrada difiere en 89 bytes, todos en `av-cam.bin` (BPB, FAT, raíz y subdirectorio `sabin` idénticos).
- `\updater\mode` y `\updater\uincomp` **no existen** en `nflasha2` (histórico). `\updater` contiene `comp` y `dat4`.
- **No se extrapola**: lo anterior describe imágenes y un volcado previo al incidente, no la NAND actual. No existe imagen oficial 3.25 `nflasha3` en el repo: la «3.25» comparada es la integrada.

## 8. Grafo de errores hasta Loader3 (Q10)

Secuencia de `c01f0cca` (init) hasta el LED, con cada retorno distinto de 0 llevado a `c01f1262 → c01f3b74` (R13), salvo la excepción de `159a`:

| Etapa | Función | Condición | Retorno | ¿LED? |
|---|---|---|---|---|
| Init FAT, leer BOS | `c01f3d50 → c01f2c92` | lectura falla | −1 (0/0/1) | sí |
| | | firma ≠ `8246` | **−302** (0/3/2) | sí |
| Switch Bkup | `c01f4a9a → c01f49d2` | montar partición 2 falla (PBR/FAT/lectura) | −302 u otro código de `c01f3eb6` | sí **salvo** que `c01f159a` devuelva ≠ 0 |
| | | ni `\Backup.bin` ni `\Backup.bak` legibles | −303 (0/3/3) | ídem |
| Run Config | `c01f2fe8` | Backup no en estado 1, o sin `0xfa0080` | −303 | sí |
| | `c01f2f24` (por entrada) | montar partición n | código de `3eb6` (−302 por PBR/FAT/lectura) | sí |
| | | archivo ausente / vacío / error de clúster o sector | **−302** | sí |

**Matiz nuevo (BINARIO `c01f159a`, `c01f11a8`):** si «Switch Bkup» falla, Loader3 solo continúa cuando `\updater\mode` **existe** en `nflasha2` (`BOM:chk updater`); si no existe, el error llega al LED. En el volcado histórico ese archivo no existe (estado normal).

Condiciones en `c01f4690` (sector reader; único llamador de `c01f2c2a`): `2c2a ≠ 0` → `ldr =0xfffffece; adds #4` = −302. Llamadores: `c01f3db8` (FAT), `c01f3e62` (PBR), `c01f4016`, `c01f4064` (cluster/dir), `c01f46e2` (raíz). `c01f2c2a`/tipo 3 entra por `c01f9a66/9a90/9bd0` (lectura TPZL; devuelve −5 si falla, y ese −5 se transforma en −302).

Sin resolver: `c01f2282` (omisión por modo, depende de un valor en RAM y del Backup `0xfa0033`) y llamadas indirectas; el grafo sigue siendo de llamadas directas.

## 9. Relación con el actualizador (Q9)

**SCRIPT (3.21 oficial; el de 3.25 no está en el repo).**
- `endupdate.sh:25–75`: monta `nflasha2`; si el paquete trae `update/backup/*/*/*.bin`, **`cp` sobre `/setting/Backup.bin`** (`:60`); ejecuta `ud_backup_write.elf` (`:63`) y `ud_keep_backup.elf $BACKUP_OPT` (`:70`); un fallo («Failed rewrite Backup.bin») devuelve el código LED `0x46`. Después `ud_lerase.elf /dev/nflasha 4` (`:83`) (partición 4/MPR, **no** el sector 0) y, en modos PRODUCT/VERSKIP, formatea `nflasha24`.
- `us_mkfs.sh:44,66,93–98`: `edisx.elf /dev/nflasha partinf.conf` (**escribe la tabla de particiones**) salvo en modos SERVICE/USER/MINOR; `uc_mkfs.elf -m full|app -f mount.conf` (**formatea** los FAT); `ud_keep_backup -s` (**restaura Backup.bin** tras formatear); `ud_wbi_drop.elf`.
- El paquete 3.25 integrado trae `partinf.conf` y `mount.conf` **idénticos** a los de 3.21 y plantillas Backup con el **mismo RAMCFG**: por diseño, el contenido objetivo de BOS/RAMCFG/geometría FAT no cambia entre versiones. Solo cambia `nflasha3` (89 B de `av-cam.bin` + recompresión TPZL, R2).

**Respuesta.** *Capacidad documentada:* sí, el actualizador escribe `nflasha2` (Backup.bin), la tabla de particiones (según modo) y `nflasha3`. *Escritura ordenada efectivamente:* depende de `UPDATER_ACTION_MODE`, **no determinado** en este repo para la cámara del incidente. *Resultado esperado:* mismas estructuras que 3.21. *Estado físico posterior:* **no medido**. **No se demuestra causalidad.**

## 10. Hipótesis compatibles y descartadas

| Hipótesis | Estado | Motivo |
|---|---|---|
| BOS: firma de sector 0 ≠ `8246` | **compatible** | produce exactamente −302; los datos históricos la cumplen; requeriría un sector 0 distinto del volcado |
| CFG/FAT: fallo de lectura o estructura en `nflasha2`/`nflasha3` | **compatible**, rutas más numerosas | cubre PBR, FAT, archivo ausente/vacío, error de sector (por TPZL o NAND) |
| RAMCFG alterado | **improbable** | idéntico en 55 BK4; si se escribiera con otro contenido, no habría −302 sino rutas inexistentes (también −302) |
| Backup no en estado 1 / sin RAMCFG | **descartada para el patrón observado** | produce −303 (0/3/3) |
| BOS lectura fallida | **descartada** | produce −1 (0/0/1) |
| `\updater\mode` ausente como causa | no es causa, es condición | solo quita la vía de escape cuando «Switch Bkup» ya falló |
| Causa 3.25 | **no demostrada** | las imágenes 3.25 integradas cumplen todo |

## 11. Matriz de evidencia

| Afirmación | Fuente | Tipo |
|---|---|---|
| RAMCFG = 6 entradas, mismo hash en 55 BK4 | pruebas 1–2 | DATOS |
| Entrada de `0x90` B, campos, orden, fin | `c01f2fe8`/`c01f2f24` | BINARIO |
| Selección por modo | `c01f304c–307a`; prueba 3 | BINARIO |
| −302 en `c01f4690` | `c01f469a–46a4`; prueba 4 | BINARIO |
| Backup estado 1 requerido (−303 si no) | `c01f2ff4–2ff6`; prueba 4 | BINARIO |
| BOS firma `8246`, filas, tipo 3 = TPZL | `c01f2c98`, `c01f2c2a`; prueba 5 | BINARIO + DATOS |
| Condiciones FAT cumplidas en 4 volúmenes | prueba 6 | DATOS |
| −302 por vacío o ausente | prueba 7 (sintética) | SINTÉTICO |
| Actualizador reescribe Backup.bin, tabla y FAT | `endupdate.sh`, `us_mkfs.sh`; prueba 8 | SCRIPT |
| Causa física del patrón | — | **sin evidencia** |

## 12. Resultados de validación

`pytest tests/test_e26_r14_ramcfg_bos.py` → 8 pasan (con R9, R11, R12 y R13: 51). `ruff check/format` y `mypy` sin avisos en los archivos nuevos. Todo opera sobre archivos; la prueba 7 modifica solo una copia en memoria.

## 13. Incertidumbres restantes

- Estado físico actual de BOS, `nflasha2` y `nflasha3`: no medido.
- `UPDATER_ACTION_MODE` de la actualización 3.25 y el `endupdate.sh`/`us_mkfs.sh` de 3.25: no están en el repo.
- Camino de lectura TPZL (`c01f9a66`–`9bd0`) y su comportamiento con el residuo de 256 B de la 3.25 (R2): no auditado en Loader3.
- `c01f2282`/`c01f16b0` (omisión por modo) y llamadas indirectas.
- INFO 6 de Loader3 no adquirida; integridad global de Loader3 no validada.
- Reloj del LED (R13) no medido.

## 14. Preguntas, decisión y R15

- **Q1. ¿Se reconstruyó completamente el formato RAMCFG?** **SÍ** en lo que lee Loader3 (entradas `0x90`, campos, orden, fin, selección). Límite: semántica fina de `flags` bits 28–30 y de `c01f2282`.
- **Q2. ¿Se localizó `0xfa0080` en algún respaldo histórico?** **SÍ**, en las 55 copias BK4 (idénticas).
- **Q3. ¿Archivos y particiones que Loader3 intenta cargar?** **SÍ**: los 6 de la sección 5 (partición 2: `kemco.txt`; partición 3: los otros cinco).
- **Q4. ¿Qué entradas de RAMCFG podrían producir −302?** Cualquiera de las 6 seleccionadas, si falta, está vacía o su lectura falla; el desbordamiento de ventana no. No se puede ordenar cuál sin estado físico.
- **Q5. ¿Se reconstruyó la carga de BOS (`c01f2b7c`)?** **SÍ**: sector 0, 0x200 B, firma `8246`, lectura fallida = −1, firma = −302.
- **Q6. ¿Metadatos BOS verificables en respaldos?** **SÍ**, el sector 0 del volcado 3.21 (`dev_nflasha.bin`); **NO** posterior al incidente.
- **Q7. ¿Las imágenes FAT cumplen las condiciones?** **SÍ**, las cuatro (nflasha2 histórico; nflasha3 histórico, oficial y integrada).
- **Q8. ¿Diferencias relevantes oficial/histórica/integrada?** Histórica = oficial; integrada 3.25 = oficial salvo 89 B de `av-cam.bin`. Ninguna afecta a lo que Loader3 comprueba.
- **Q9. ¿Se demostró que el actualizador 3.25 puede alterar los datos implicados?** **NO** como hecho; **SÍ como capacidad en los scripts de 3.21** (Backup.bin, `edisx`, `uc_mkfs`, `nflasha3`). Faltan los scripts de 3.25 y el modo de acción.
- **Q10. ¿BOS o CFG/FAT?** **CFG/FAT** queda mejor respaldada *estructuralmente* (más rutas hacia −302, incluida cualquier lectura fallida de `nflasha2`/`nflasha3` y la ruta TPZL que 3.25 modifica). **No está respaldada por datos**: todas las imágenes cumplen. BOS se mantiene viable con un solo mecanismo (sector 0).
- **Q11. ¿Qué evidencia falta?** El estado real de la cámara (UART/log `LD3_E:`/`BOS_E:`/`FAT_E:`/`CFG_E:`), que distingue de inmediato las cinco vías; sin eso, el `endupdate.sh`/`us_mkfs.sh` y el modo de 3.25.
- **Q12. ¿R15 offline?** (1) Auditar el camino TPZL de Loader3 (`c01f9a66`, `9a90`, `9bd0`) y reproducir con el volumen 3.25 (residuo 256 B) si `c01f2c2a` puede fallar; (2) buscar y comparar el `updater.img` de 3.25 (modo de acción, `us_mkfs`); (3) resolver `c01f2282`/`c01f16b0`.

**Decisión: C.** Ambas rutas están caracterizadas con sus condiciones exactas (incluida la lista real de archivos) y los datos históricos las satisfacen todas: no discriminan el fallo físico actual. Ninguna acción física en esta sesión.
