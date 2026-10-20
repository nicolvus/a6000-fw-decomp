# S18 — cruce FEA/DMM con OSS Sony: memoria y DMA

## Alcance y fuentes

**VERIFICADO — código fuente real.** Se examinó estáticamente `linux-kernel.tar.gz` (SHA-256 `b1c74cc1a0160a7fceced6f88fa35521adc431205ad1ebc8a413d20b653785b1`), cuya versión es Linux 3.0.27. La extracción adicional quedó limitada a `analysis/session18/codex-g/oss-linux/linux/`. No se ejecutó firmware, no se conectó ni flasheó una cámara, ni se modificó ningún binario original.

**NO VERIFICADO — atribución.** El paquete no identifica literalmente ILCE-6000 ni ILCE-6300. Sus resultados describen el código OSS distribuido, no prueban que un binario propietario concreto lo cargue o use.

**VERIFICADO — binarios propietarios, por evidencia previa recibida.** `MprIf::SetCallbackFunc` está en `libmpr.so:0x71f7b8`; `FeaIf::MprIfCallbackPoint` en `0x4502e8`. `FeaIf::EncodeStill` encola y no espera la lectura; no se localizó un liberador DMM real tras el callback. El candidato `0xc0000004` a `CBID_ENCODE_STILL` continúa siendo **INFERENCIA**, no confirmación.

## Memoria compartida y DMA-BUF

**VERIFICADO — código fuente real.** El mecanismo de memoria compartida Android presente es `ashmem`: `mm/ashmem.c` y `include/linux/ashmem.h`; `mm/Makefile:35` lo compila bajo `CONFIG_ASHMEM`. Los defconfigs Android CXD90014 habilitan `CONFIG_ASHMEM=y` (por ejemplo `arch/arm/configs/cxd90014_android_set_defconfig:137`). Cada `ashmem_area` conserva un `struct file *` de respaldo shmem; `ashmem_mmap()` crea el archivo con `shmem_file_setup()`, toma `get_file()`, y `ashmem_release()` ejecuta `fput()` (`mm/ashmem.c:39-50,198-210,284-335`).

**DESCARTADO — código fuente real.** No hay `ion`, `CONFIG_ION`, `dma_buf`, `DMA_SHARED_BUFFER`, ni `dmm.ko` en el archivo ni en el árbol extraído. Por tanto ION y DMA-BUF no son mecanismos disponibles en este OSS 3.0.27. Esto no prueba qué mecanismo usa DMM propietario.

**INFERENCIA — comparación conceptual.** Ashmem comparte backing de `shmem` entre mappings de procesos; puede ilustrar una categoría de memoria compartida Linux, pero no corresponde a la ABI, formato de unidad, duración ni semántica de `DmmShare`/`DmmClose`.

## Retención y contadores

**VERIFICADO — código fuente real.** El VFS usa `struct file::f_count` (`atomic_long_t`), `get_file()` y `fput_atomic()` en `include/linux/fs.h:949-1001`. El MM usa `struct page::_count` (`atomic_t`) y `get_user_pages()` toma una referencia que el llamador libera con `put_page()`; el propio comentario afirma que evita que la página sea liberada completamente durante la operación (`include/linux/mm_types.h:39`, `mm/memory.c:1625-1660,1934-1979`).

**VERIFICADO — código fuente real, ejemplos no Sony/cámara.** `drivers/video/udlfb.c` usa `kref_init/get/put` alrededor de un framebuffer USB; `drivers/dma/dmaengine.c` usa `atomic_t` para referencias de `idr`. Son ejemplos del kernel genérico, no drivers CXD ni evidencia de buffers de captura Sony.

**INFERENCIA — contexto solamente.** En un diseño de kernel, adquirir una referencia antes de DMA/IO asíncrono y liberarla al completarse es un patrón capaz de retener una región. No se halló una ruta que conecte ese patrón genérico con `DmmShare`, `DmmClose`, FEA o sus callbacks; por ello no explica el comportamiento real previamente observado de DMM.

## Coherencia de caché

**VERIFICADO — código fuente real.** `arch/arm/mm/dma-mapping.c:113-114` usa `dmac_flush_range()` y `outer_flush_range()` al preparar memoria DMA coherente. Sus rutas streaming hacen `dmac_map_area()` y, según dirección, `outer_inv_range()` o `outer_clean_range()` (`:520-570,650-690`). Las declaraciones/interfaz son ARM genéricas: `arch/arm/include/asm/cacheflush.h:140,163` y `arch/arm/include/asm/outercache.h:45-114`.

**VERIFICADO — integración Sony específica de plataforma.** CXD4132 instala operaciones PL310 en `outer_cache` y `outer_cache_unlocked` (`arch/arm/mach-cxd4132/cache-pl310.c:308-324`); sus defconfigs seleccionan `CONFIG_OUTER_CACHE` y `CONFIG_CACHE_PL310S`. CXD90014 usa la API genérica, por ejemplo `dma_sync_single_for_device()` en `mach-cxd90014/cmpr.c:153`, y sus defconfigs seleccionan `CONFIG_OUTER_CACHE`/`CONFIG_CACHE_PL310`.

**INFERENCIA — límite.** La existencia de estas operaciones hace plausible que controladores de ese kernel deban mantener coherencia antes/después de DMA; no demuestra una operación DMA de DMM/FEA, un buffer de imagen concreto, ni una omisión de caché en los binarios propietarios.

## Asincronía y controladores de imagen

**VERIFICADO — código fuente real.** El ejemplo Sony CXD de `completion` es CPU hotplug, no imagen: `mach-cxd4132/hotplug.c:19,96,121` declara, espera y completa `cpu_killed`. Como ejemplo genérico de DMA asíncrono, `drivers/dma/imx-sdma.c:252,374,378,492` combina `struct completion`, espera con timeout y `complete()` desde la ruta de terminación.

**INFERENCIA — analogía conceptual exclusivamente.** Una pareja «conservar recurso → lanzar DMA → callback/IRQ → completar → liberar» es análoga al problema de duración de un buffer compartido hasta fin de operación. No es evidencia de que `DmmShare` ni `DmmClose` estén implementados con `completion`, `wait_queue`, IRQ o DMAengine.

**VERIFICADO — código fuente real.** En CXD4132, `udif/platform.c:444-459,506-526,625-646` registra dispositivos llamados `ldec` y `mia`, con IRQ y canal DMAC respectivamente. No existen ficheros de controlador CXD llamados `ldec`, `mia`, `camera`, `imager`, `sensor` o `isp`, ni usos de esos nombres fuera del descriptor UDIF.

**NO VERIFICADO.** La función de `ldec` y `mia` no está documentada por el código liberado; no se les asigna semántica de decodificador, ISP o captura. Tampoco se halló un driver Sony de sensor/V4L2/JPEG/ISP que constituya un análogo real de DMM/FEA. Las apariciones de Sony en `drivers/media`/`drivers/video` corresponden a componentes genéricos o de otros productos, no a una ruta CXD de cámara demostrada.

## Búsqueda literal de DMM

**DESCARTADO — módulo/interfaz DMM Sony en OSS.** No existe entrada de archivo `dmm.ko`, fuente/cabecera con nombre `dmm`, `CONFIG_*DMM` aplicable a Sony ni regla de compilación que produzca un módulo DMM en los directorios CXD. Las coincidencias literales `dmm` restantes son ajenas: metadatos OMAP4 para un bloque hardware llamado DMM (`arch/arm/mach-omap2/omap_hwmod_44xx_data.c`) y una referencia a `pmgr/dmm.o` bajo `drivers/staging/tidspbridge/Makefile` para TI DSPBridge; el archivo fuente `pmgr/dmm.c` ni siquiera está presente en este tar. No son la interfaz Sony DMM.

## Comparación A6000 frente a A6300

**PENDIENTE / NO VERIFICADO.** Solo hay un paquete de kernel OSS; no existe una segunda fuente A6300 con la que comparar. No se infieren diferencias A6000/A6300 de memoria, DMA, cache o DMM.

## Conclusión acotada

**VERIFICADO.** El OSS contiene mecanismos genéricos de retención, memoria compartida y coherencia DMA, además de integración PL310 para plataformas CXD.

**DESCARTADO.** El OSS no contiene un módulo/interfaz Sony DMM ni ION/DMA-BUF.

**NO VERIFICADO.** Ninguno de estos datos resuelve la duración real de un buffer DMM tras `EncodeStill`, confirma el callback `0xc0000004`, ni demuestra una ruta de captura electrónica. En particular, este cruce no permite afirmar que SilentShutter funcione.
