# E26-R39 — Investigación estática a fondo: emulación TPZL→LDEC, NAND física, arranque del actualizador, `MODE`, sesión USB y clave de `nflasha0`

Fecha: 31-10-2026. Continúa [R38](e26-r38-guard-y-entrada-updater.md). **Solo análisis offline y emulación** (Unicorn) de código de `bootloader.bin`; sin cámara, USB ni escritura. Pedido del usuario: «hazlas todas, mientras se pueda avanzar en modo estático sin uso de cámara» sobre las seis líneas propuestas tras R38.

Etiquetas: **EMULACIÓN** (código real en Unicorn) · **MODELO** (silicio sustituido por una regla) · **BINARIO** · **FUENTE** (GPL de Sony) · **DATOS** · **INFERENCIA**. Pruebas: [`tests/test_e26_r39_estatico_profundo.py`](../../tests/test_e26_r39_estatico_profundo.py) (9). Emulador: [`r39_tpzl_emu.py`](../../analysis/e26-recovery/r39_tpzl_emu.py) → [`r39-tpzl-emu.json`](../../analysis/e26-recovery/r39-tpzl-emu.json).

## 1. Resumen

| # | Línea | Resultado |
|---|---|---|
| 1 | Reproducir el fallo del 3.25 | **Reproducido en emulación.** Con el código real de Loader3 y del ARM7, el modelo del LDEC falla en **361 de 369** bloques del 3.25, empezando por el **bloque 0**. Pasan los 369 de Sony y los 369 del constructor corregido (R36). El residuo llega al trabajo (`+8 = 256`), pero el ARM7 nunca lo escribe en el LDEC |
| 2 | Sector 132 → NAND física | **No se puede calcular estáticamente, y el byte no se puede reprogramar en su sitio.** Las particiones son tramos lineales de `nflasha`, pero `nflasha` es un dispositivo lógico de MuMin, una capa de traducción completa con mapa lógico→virtual→físico, bloques malos, desgaste y ECC/extra en el área de repuesto. `0xE5 → 0x4D` exige pasar un bit de 0 a 1, y la NAND solo puede pasar bits de 1 a 0 sin borrar |
| 3 | Arranque del actualizador | **No lee `nflasha3`, `nflasha5` ni `nflasha7`.** Monta solo `nflasha2` y carga módulos del propio initrd. El Darwin del 3.25 difiere del de Sony en **22 bytes** (cueva en vectores 70–77 y dos llamadas del obturador mecánico); tras un reinicio se comporta como el de Sony |
| 4 | Persistencia de `MODE` | **Confirmada por el código fuente** (antes era INFERENCIA en R38). Kernel del actualizador = `Linux 3.0.27_nl-rt106`, la misma versión que el árbol GPL de Sony (con `posix_attr`). En ese árbol las búsquedas no distinguen mayúsculas (`name_check='n'` → `nls_strnicmp`) y `shortname=mixed` lista `MODE` tal cual |
| 5 | Sesión USB pmca↔`sauu` | El guard solo exige modelo = `dat2` (`0x41030035`), región = `dat3` (0) y la regla de versión de R38. El 3.26 cumple las tres. **No hay comprobación de batería** en `sauu` ni en el cuerpo: la carga es responsabilidad del operador |
| 6 | Clave de `nflasha0` | Ningún paquete ni volcado trae el bloque 0. **Fuente nueva:** ningún cargador escribe `0xc0001200`–`0xc00013ff`, donde el BootROM deja la tabla, y el actualizador ya lee páginas de arranque de la SRAM (`0xc0038000`, `0xc003d000`). En una sesión del actualizador, `pmca` podría leer la clave con `readMemory` sin escribir nada (INFERENCIA: que la SRAM la conserve hasta Linux) |

## 2. Emulación de la ruta TPZL → ARM7 → LDEC (EMULACIÓN + MODELO)

**Qué se ejecuta tal cual (Unicorn, código de `bootloader.bin`):**

- Loader3 `c01fe4ec`: registro TPZL (cabecera, TOC, `entradas = tamaño >> 3`).
- Loader3 `c01fdd8e`: petición por bloque, hasta la llamada a `c01fce8c`, donde se captura el trabajo de 0x18 B.
- ARM7 `0x3f4`: escritura de los registros del LDEC (`0xf2903000`), capturada con un hook de memoria.

**Qué se sustituye:**

- Funciones ausentes del volcado (`c020xxxx`: printf, división de libgcc) y servicios de E/S (`c01fd9d4` lectura cruda, `c01f9d10` malloc, `c01fdbe0` lista de sectores). Ninguno decide los campos capturados.
- El LDEC (silicio) se modela con la regla de R36. Le entra el flujo de **sectores enteros** desde `offset >> 9` y produce `registros` registros, cada uno de 4096 B en el formato de Sony (`0F 00 <u16>` almacenado o `F0` LZ77). Se compara con la salida del decodificador de software.

| Imagen | Bloques | Avisos de residuo (`c020bd24`) | Fallos del modelo | Primer fallo |
|---|---:|---:|---:|---|
| Sony 3.21 | 369 | 0 | **0** | — |
| Instalada 3.25 (`bb9ce25a…`) | 369 | 359 | **361** | bloque **0** (sector de arranque FAT): un registro de 65 536 B |
| Corregida (R36, mismo contenido que el 3.25) | 369 | 0 | **0** | — |

**Bloque 240** (primera entrada del RAMCFG) del 3.25:

- Trabajo: `{residuo 256, registros 16, destino, tamaño 65536}`.
- Escrituras del ARM7 en el LDEC: `+0x0`, `+0x4`, `+0xc` (= 16), `+0x10` (destino), `+0x28`, `+0x2c` y `+0x30`. **Ninguna lleva el residuo.**
- El primer byte que recibe el LDEC es `0x00` (relleno anterior), que no es un tipo de registro válido.

**Qué cambia frente a R36:** antes era la lectura de las instrucciones; ahora el código real se ejecuta y produce exactamente esos campos. Lo único supuesto es el comportamiento del silicio ante un flujo mal alineado. En cualquier caso, el contenido que recibiría sería incorrecto.

## 3. De sector lógico a NAND física (DATOS + BINARIO)

- **Particiones lineales.** `dev_nflashaN.bin` = `dev_nflasha.bin[inicio : inicio + tamaño]` según `partinf.conf` para N = 1…7. El sector 132 de `nflasha2` es el desplazamiento lógico `0x6508A0` de `nflasha`.
- **`nflasha` es lógico.** Mide `0x1D900000` (473 MiB). `nand.ko` (MuMin) exporta, entre otras:
  - `mumin_ebi_get_ltu_tables`, `mumin_ebm_s_reconstruct_lblk_table_in_ebi`: mapa de bloques lógicos.
  - `mumin_vbm_*`, con `get_udb_of_least_erased_counts`: bloques virtuales y nivelación de desgaste.
  - `mumin_pbm_s_mark_bad_pblk`, `…_get_initial_bad_pblks`, `…_load_pbi`/`…_store_pbi`: bloques físicos, bloques malos y tablas de gestión.
  - `mumin_pbm_s_serach_pab_of_specified_extra_data`, `mumin_cmn_get_pagegp_extra_and_ecc_buff`: datos extra y ECC por página.

  La posición física de una página lógica depende de tablas guardadas en la propia NAND y del área de repuesto. No se deduce de un volcado lógico.
- **Programación en su sitio imposible.** `0x4D & ~0xE5 = 0x08`: el bit 3 tendría que pasar de 0 a 1, y una página NAND solo puede pasar bits de 1 a 0 sin borrar el bloque entero. Además cambiarían el ECC y los datos extra de la página.

**Consecuencia para `E26-FISICO-UPDATERMODE`:**
- **Lector externo:** casi inviable. Exigiría volcar en crudo la NAND con su área de repuesto, reconstruir MuMin, conocer el ECC del controlador y reescribir un bloque completo con datos extra coherentes.
- **Vía práctica:** escribir **dentro del sistema**, con código ejecutándose en el BIONZ que use MuMin. Por ejemplo, la vía serie del BootROM con la clave, o una sesión de depuración. Ahí sí vale el parche lógico de 1 byte (32 B en el peor caso) de R38.

## 4. Arranque del actualizador (BINARIO + DATOS)

**`/sbin/init` del initrd de `nflasha1`:**
- Hace `mkramdsk.sh`, `insmod.sh`, `us_darwin_init.sh` (si el IC es Darwin) y `UdtrMain.sh &`.
- `insmod.sh` carga módulos de `/kmod` (initrd), monta **solo `/dev/nflasha2`** en `/setting` (`Backup.bin`, `ulogio.bin`, `DmmConfig.bin`) y copia `MIS.bin`/`DGU.bin` de la SRAM.
- Ningún script de arranque nombra `nflasha3/5/7` ni `P3_DEV`/`P3_MNT_DIR`. `libInfraMediaCommon.so` tiene una tabla genérica de particiones, pero ningún script la usa al arrancar.

**Darwin 3.25 frente a 3.21:**
- **22 bytes**: `0x118`–`0x134` (cueva en `0x4318`, en vectores no usados) y las llamadas `0x20c78` (tipo de bobina) y `0x1fe6c` (compuerta del motor), las del selector de E25-24b.
- Con el byte del selector a 0, lo que ocurre en cada reinicio (R37 d), la cueva salta a `0x1b080` como el original.
- El arranque de Darwin (`0x0–0x41ff`), que reprograma su flash, no viene en ningún paquete. Por eso el 3.26 puede devolver el Darwin oficial.

## 5. Persistencia de `MODE` (FUENTE + BINARIO)

**El kernel:** `vmlinux.bin` de `nflasha1` (zImage) contiene `Linux version 3.0.27_nl-rt106` y las opciones `posix_attr` y `shortname=mixed`. Es la misma versión que el árbol GPL de Sony del repositorio (`analysis/session18/codex-g/oss-linux/linux/fs/fat`), que también trae `posix_attr`.

**Qué hace ese código:**
- **Búsqueda:** `fat_name_match` usa `nls_strnicmp` si `name_check != 's'`, y el valor por defecto es `'n'` (`inode.c`). `test -f …/mode` y el `unlink` de `ModeFlagFile::Delete` encuentran `MODE`.
- **Listado:** `shortname=mixed` = `VFAT_SFN_DISPLAY_WINNT`. Sin la bandera de minúsculas, `fat_shortname2uni` devuelve el nombre tal cual: `readdir` da `MODE`. El glob `mode*` de busybox distingue mayúsculas y no lo borra.

**Límite:** se usó el árbol GPL de la misma versión, no el binario exacto del actualizador. La opción `CONFIG_SNSC_FS_VFAT_COMPARE_UNICODE` está desactivada en todos los defconfig `cxd90014` del árbol.

## 6. Sesión USB con la cámara ya en el actualizador (BINARIO + DATOS)

**Lado `pmca`:** `firmwareUpdateCommandInternal` con un `SonyUpdaterDevice` hace `init` → `CMD_CHK_GUARD` → `CMD_QUERY_VERSION` → `CMD_WRITE_FIRM` por ventanas → `CMD_COMPLETE`, sin `switchMode`.

**`UpdaterHandler::SetChkGuardResult` (`0xd46c`):**
- `isModelOK` (`0xd3b2`): igualdad con `dat2`. Si falla, `0x140`.
- `isRegionOK` (`0xd394`): igualdad con `dat3`. Si falla, `0x141`.
- `isVersionOK`: la regla de R38. Si falla, `0x142`.

**Con los datos de la cámara:** `dat2 = 35 00 03 41` (`0x41030035`), `dat3 = 0`, y el FDAT 3.26 trae modelo `0x41030035`, región 0 y versión `3.26` > `3.25`. **Pasa.**

**Batería:** ni `sauu`, ni `libupdaterufunc.so`, ni `libupdaterbody.so` contienen comprobaciones de batería. Los estados `STAT_LOW_BATTERY`/`STAT_AC_ADAPTER_REQUIRED` del protocolo vienen del modo normal. En modo actualizador nada impide escribir con la batería baja, y un corte durante la escritura de `nflasha3` repetiría el problema.

## 7. Clave de `nflasha0` (BINARIO + DATOS)

- Ni el A6000 3.21, ni el α7S 3.20, ni el α6300 2.01 traen `loader_sum`/`loader_mpt.tar`. Ningún paquete disponible contiene el área de arranque.
- Literales en `0xc0000000`–`0xc0001fff`:

| Código | Literales |
|---|---|
| BootROM | `0xc0000600` (destino de los 3 sectores) y `0xc0001200` (tabla) |
| Loader2 | `0xc0000c00`, `0xc0001400`, `0xc0001500` (tabla de medias palabras que recorre hasta `0xffff` y escribe hacia delante desde `0xc0001500`) |
| Loader3 | `0xc0001500` |
| ARM7 | ninguno |

  **Nadie apunta a `0xc0001200`–`0xc00013ff`.**
- El actualizador copia de la SRAM páginas del área de arranque (`ud_get_mem2file.elf … 0xc003d000` = «page 7» MIS, `0xc0038000` = «page 8» DGU) para conservarlas al reescribir los loaders (`loader_writer.sh`). La SRAM baja sobrevive al menos hasta el inicio del actualizador.
- **Propuesta (no autorizada):** en la primera sesión del actualizador que se consiga, antes de instalar, usar el shell de `pmca` (`updaterShellCommand`, que no escribe `dat4`, como muestra el volcado posterior al del 20-10) para leer `readMemory(0xc0001200, 8)` y comprobarlo con `~crc32` (R33 §4). Eso daría la clave de la vía serie para futuras recuperaciones. No sirve para la recuperación actual, que es la que necesita la clave.

## 8. Correcciones

- [R36](e26-r36-causa-fallo-325.md) §1: la causa ya no se apoya solo en la lectura del código. Está **reproducida en emulación** con el LDEC modelado; la confirmación física sigue pendiente.
- [R38](e26-r38-guard-y-entrada-updater.md) §5: la persistencia de `MODE` pasa de INFERENCIA a **FUENTE**. La frase «la traducción del sector 132 a página física pertenece a `E26-FISICO-BOOT`» se corrige: esa traducción no se puede calcular estáticamente y la escritura con lector externo deja de ser la vía recomendada (§3).
- [R38](e26-r38-guard-y-entrada-updater.md) y [R37](e26-r37-cierre-estatico-recuperacion.md) d: el Darwin del 3.25 difiere en 22 bytes, no solo en la cueva y el literal.

## 9. Límites

- El LDEC es un modelo: no se ha ejecutado el silicio.
- El estado actual de la NAND (MuMin, `nflasha2`) no se ha leído.
- La conservación de `0xc0001200` hasta Linux es una inferencia.
- Nada de lo anterior autoriza ni prueba una escritura.
