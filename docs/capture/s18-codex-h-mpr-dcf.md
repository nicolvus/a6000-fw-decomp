# S18 — Codex H: MPR, DCF y la pila de almacenamiento

## Alcance y método

Análisis exclusivamente estático. No se conectó ni se modificó una cámara, no se instaló software y no se modificó ningún binario original ni `CONTEXT.md`.

Se inspeccionaron las fuentes GPL de `linux-kernel.tar.gz` (SHA-256 `b1c74cc1a0160a7fceced6f88fa35521adc431205ad1ebc8e413d20b653785b1`) y, en modo de solo lectura, `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so` (SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`). La extracción adicional se limitó a `analysis/session18/codex-h/sony-oss-extracted/`.

## Hallazgos

| Clasificación | Hallazgo | Evidencia estática |
|---|---|---|
| **VERIFICADO** | `mach-cxd4132/sdc.c` **no es un controlador de tarjeta SD/MMC**. Es un controlador del DMC para memoria LPDDR: lee `SDC_MEMORY`, prueba `SDC_MODE_DDR`/`SDC_MODE2RANK` y emite `SDC_DDR2_MRW_*` contra `SDC_COMMAND2`. | `sdc.c:126-176`; `include/mach/regs-dmc.h:43-57` nombra los registros como LPDDR1/LPDDR2. |
| **VERIFICADO** | Su manejo de errores es local a comandos DDR: espera el bit `SDC_DDR2_BUSY` hasta 100 ms y fija `SDC_ERR_TIMEOUT`; no procesa sectores, bloques, comandos SD/MMC ni rutas de archivos. | `sdc.c:44,146-178`; `sdc.h:56-57`. |
| **VERIFICADO** | `sdc-zqcal.c` ejecuta calibración ZQ de LPDDR2, no de una tarjeta. Envía MR10 (`LPDDR2_ZQREG`) con ZQ long una vez por rango y ZQ short después, alternando rangos y reprogramando un temporizador. Las constantes declaran 312 MHz y tiempos LPDDR2. | `sdc-zqcal.c:47-72,126-145,210-229`; `sdc-zqcal.h:58-71`. |
| **DESCARTADO** | Interpretar la sigla `sdc` y su ZQ calibration como evidencia de un driver SD o de integridad DCF. La propia definición de registros la contradice: es DMC/DDR. | `regs-dmc.h:37-65`; hallazgos anteriores. |
| **VERIFICADO** | El árbol Linux 3.0.27 contiene FAT y VFAT: `fs/fat/{file.c,inode.c,namei_vfat.c,...}`, con `CONFIG_FAT_FS` y `CONFIG_VFAT_FS` en sus Kconfig. | `fs/fat/Kconfig:1-88`; `fs/fat/Makefile:5-7`. |
| **VERIFICADO** | Los tres defconfig CXD inspeccionados habilitan FAT y VFAT (`CONFIG_FAT_FS=y`, `CONFIG_VFAT_FS=y`). Los dos defconfig Android CXD90014 también habilitan `CONFIG_SNSC_FS_FAT_BATCH_SYNC=y`; el WLAN además declara `CONFIG_MMC=m`. | `arch/arm/configs/cxd4132a_nfs_defconfig:991-993`; `cxd90014_android_set_defconfig:1337-1339,1467`; `cxd90014_android_wlan_set_defconfig:1573,1736-1738,1894`. |
| **INFERENCIA** | FAT/VFAT es el candidato respaldado por el paquete OSS para el medio extraíble de este entorno Android/CXD. | Se deriva de las opciones activadas y del código presente; no equivale a observar el montaje real del medio de una ILCE-6000. |
| **NO VERIFICADO** | Que esos defconfig sean exactamente el que arrancó el firmware ILCE-6000 3.21, ni el tipo de sistema de archivos montado realmente en su tarjeta. No hay prueba de ejecución, tabla de particiones ni registro de montaje en este análisis. | Limitación de evidencia estática y de atribución del paquete OSS al modelo concreto. |
| **VERIFICADO** | El VFS implementa `fsync` y `fdatasync`: espera writeback del rango, toma `i_mutex` y llama a la operación `fsync` del archivo. | `fs/sync.c:156-228`. |
| **VERIFICADO** | FAT implementa `fat_file_fsync`; la ruta normal llama `generic_file_fsync` y sincroniza los buffers del inode FAT. Cuando se compila `CONFIG_SNSC_FS_FAT_BATCH_SYNC`, una opción de montaje `batch_sync` puede elegir `fat_clean_inode` en vez de esa ruta. | `fs/fat/file.c:446-500`; configuración indicada arriba. |
| **VERIFICADO** | FAT implementa sincronización del superblock (`fat_sync_fs`) y writeback de clusters sucios. | `fs/fat/inode.c:539-552`. |
| **INFERENCIA** | El kernel ofrece primitivas que una capa superior puede usar para reducir datos pendientes ante un error o apagado: writeback, `fsync`/`fdatasync` y errores devueltos por esas rutas. | Es una capacidad de la capa base; no demuestra que MPR las invoque en un orden concreto ni garantiza una transacción entre varios archivos. |
| **DESCARTADO** | Que FAT/VFAT proporcione por sí solo un journal transaccional de catálogo DCF. El código FAT inspeccionado muestra writeback/sincronización, no una prueba de journaling DCF; JBD2/ext3 existentes en el árbol son componentes distintos. | `fs/fat/*`, `fs/sync.c`; presencia separada de `fs/jbd2/` y `fs/ext3/` en el tarball. |
| **VERIFICADO** | `libmpr.so` es un ELF ARM dinámico y depende de `libInfraFsys.so`, `libInfraMediaDetect.so`, `libInfraMediaMount.so` y libc, entre otras. | `readelf -d libmpr.so` (`NEEDED`); `file` identifica ELF ARM EABI5 stripped. |
| **VERIFICADO** | `libmpr.so` importa las funciones POSIX `open`, `read`, `write`, `close`, `lseek`, `rename`, `mkdir`, `fsync`, `fdatasync`, `fopen`/`fwrite`/`fflush` y también la familia propietaria `Fsys_Open`, `Fsys_Write`, `Fsys_WriteAndFlush`, `Fsys_Flush`, `Fsys_Mkdir`, `Fsys_Rename`, etc. | `nm -D libmpr.so`; son símbolos indefinidos/importados. |
| **VERIFICADO** | El binario exporta una abstracción propia `MprFileIfCore` con `Open`, `Write`, `WriteAndFlush`, `Mkdir`, `Remove`, `Seek`, `Stat`, `Close` y `GetFileSize`. | `nm -D --defined-only libmpr.so` (símbolos C++ en torno a `0x00725xxx`–`0x007262xx`). |
| **VERIFICADO** | Sus cadenas contienen componentes DCF, rutas DCIM y operaciones de catálogo/reproducción, por ejemplo `DCIM`, `\\DCIM\\%3ldMSDCF\\DSC0%04ld.JPG`, variantes `.MPO`/`.ARW`, `RegisterDCFContent`, `SetBasicThumbnailData`, `GetDCFContentAttribute` y `DCF ContentCount`. | `strings -a libmpr.so`; evidencia de cadenas, no de flujo de control. |
| **INFERENCIA** | Las importaciones POSIX pueden llegar al VFS/FAT descrito arriba si el soporte inferior `libInfraFsys.so` usa las llamadas POSIX directas; las importaciones `Fsys_*` indican además una capa de abstracción entre MPR y el sistema de archivos. | La dependencia y los símbolos prueban interfaces, no el destino dinámico de cada llamada ni el tipo de filesystem montado. |
| **NO VERIFICADO** | Que una llamada concreta de MPR a `fsync`/`fdatasync` ocurra al terminar cada JPEG, antes/después de registrar catálogo, o en una ruta de error determinada. `nm`/`strings` no reconstruyen esos call sites, sus condiciones ni sus resultados. | Binario stripped; no se realizó desensamblado ni trazado dinámico en esta tarea. |

## Límite explícito sobre DCF y reproducción

**NO VERIFICADO:** no hay evidencia de código fuente GPL que implemente en MPR la cadena DCF completa: creación de `DCIM` y de directorios numerados, asignación de nombre/número de archivo, generación o inserción de miniatura EXIF, ni alta/actualización del catálogo usado por reproducción. `libmpr.so` aporta evidencia binaria limitada de interfaces, cadenas y símbolos relacionados, pero no código fuente y no reconstruye una cadena completa hasta la escritura del catálogo de reproducción.

Por tanto, la lógica de catálogo DCF permanece **propietaria de MPR** y está por encima del kernel GPL. El kernel sólo aporta el bloque, VFS, FAT/VFAT y sus primitivas de sincronización; no define la política de catálogo DCF. No se afirma que SilentShutter funcione.

## Conclusión

El límite arquitectónico queda claro: DMC/LPDDR (`sdc*`) es ajeno tanto a SD como a DCF; FAT/VFAT y `fsync` son servicios base disponibles; MPR posee interfaces de archivo, DCF, miniaturas y catálogo, pero la secuencia semántica completa y su recuperación ante error no se ha demostrado estáticamente con código fuente.
