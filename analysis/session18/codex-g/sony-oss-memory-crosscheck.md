# Sony OSS Linux 3.0.27 — cruce memoria/DMA para FEA-DMM

| Área | Estado | Evidencia de fuente real | Límite frente a binarios propietarios |
|---|---|---|---|
| Versión y procedencia | VERIFICADO | `linux/Makefile` indica 3.0.27; SHA del tar en inventario S18 | NO VERIFICADO que corresponda a un modelo ILCE exacto o al kernel en ejecución. |
| Memoria compartida | VERIFICADO | `mm/ashmem.c`, `include/linux/ashmem.h`, `CONFIG_ASHMEM=y` en defconfigs Android CXD90014 | Ashmem no identifica DMM ni su ABI. |
| ION / DMA-BUF | DESCARTADO | Sin ruta, símbolo de configuración o definición literal en el tar/árbol de Linux 3.0.27 revisado | Su ausencia OSS no excluye un asignador propietario fuera del kernel. |
| Retención VFS/MM | VERIFICADO | `get_file`/`fput`, `get_user_pages`/`put_page` y contadores atómicos | INFERENCIA solamente que DMM pueda seguir un patrón análogo. |
| Caché DMA ARM | VERIFICADO | `arch/arm/mm/dma-mapping.c` combina `dmac_*` y `outer_*` | No hay llamada FEA/DMM demostrada. |
| PL310 CXD | VERIFICADO | CXD4132 instala callbacks PL310; CXD90014 configura outer cache y usa API DMA | Integración de plataforma, no prueba de pipeline de cámara. |
| Asincronía | VERIFICADO | CXD hotplug usa `completion`; DMA genérico IMX-SDMA usa espera/completado | ANALOGÍA CONCEPTUAL: no se atribuye a `DmmShare`/`DmmClose`. |
| Dispositivo de imagen Sony | NO VERIFICADO | UDIF declara `ldec` y `mia` con IRQ/DMAC; no existe su controlador fuente CXD | No nombrarlos decoder, ISP ni sensor. |
| DMM literal | DESCARTADO | Sin `dmm.ko` ni módulo/interfaz Sony; ocurrencias OMAP/TI ajenas | La DMM propietaria queda fuera del OSS. |
| A6000 vs A6300 | PENDIENTE / NO VERIFICADO | Solo un tar de kernel disponible | No hay comparación posible. |

## Detalle verificable

### 1. Mecanismo de compartición existente

**VERIFICADO — fuente real.** Ashmem se crea como `miscdevice` llamado `ashmem` (`mm/ashmem.c:691-724`). En el `mmap`, usa un archivo shmem de respaldo y toma una referencia (`:284-335`). Es el mecanismo de memoria compartida Android presente de forma explícita. Los mappings no fijan el `ashmem_area` por sí mismos; su comentario de ciclo de vida dice que muere al cerrar (`:39-50`).

**DESCARTADO — fuente real.** Las búsquedas de rutas y tokens de configuración no encuentran ION, `dma_buf` ni `DMA_SHARED_BUFFER`; tampoco hay `dmm.ko`. Esta conclusión se limita a este tar OSS exacto.

### 2. Contadores y retención general

**VERIFICADO — fuente real.** `struct file` posee `atomic_long_t f_count`; `get_file()` incrementa y `fput_atomic()` decrementa (`include/linux/fs.h:949-1001`). `struct page` posee `_count` atómico (`include/linux/mm_types.h:39`); `get_user_pages()` toma referencias y exige `put_page()` al terminar (`mm/memory.c:1625-1660,1934-1979`). El comentario especifica que la página no se libera completamente mientras la referencia exista.

**VERIFICADO — fuente real, no Sony.** El framebuffer USB `udlfb` usa `kref` y DMAengine usa `atomic_t` para objetos internos. Son pruebas de patrones del kernel, no de una unidad DMM.

**INFERENCIA.** Estos mecanismos son el tipo de retención que podría proteger una región durante IO/DMA asíncrono. No se puede deducir de ellos que DMM retenga, comparta o libere igual.

### 3. Coherencia

**VERIFICADO — fuente real.** Las primitivas `dmac_flush_range` y `outer_*` pertenecen a la arquitectura ARM genérica (`arch/arm/include/asm/cacheflush.h`, `outercache.h`); `arch/arm/mm/dma-mapping.c` las usa para memoria coherente y DMA streaming. CXD4132 aporta una implementación/inicialización PL310 específica de plataforma que rellena `outer_cache` (`mach-cxd4132/cache-pl310.c:308-324`).

**INFERENCIA.** Que haya PL310/CXD y APIs DMA confirma un contexto donde coherencia es relevante; no identifica dueño, dirección ni vida de un buffer FEA.

### 4. Asincronía

**VERIFICADO — fuente real.** `mach-cxd4132/hotplug.c` hace `wait_for_completion_timeout()` y `complete()` para CPU hotplug. `drivers/dma/imx-sdma.c` ofrece un caso genérico de finalización DMA con `struct completion`.

**INFERENCIA — analogía conceptual.** Esperar una terminación antes de soltar una referencia sería un diseño posible para `DmmShare`/`DmmClose`; no hay evidencia de que sea su diseño real.

### 5. Imagen y DMM

**VERIFICADO — fuente real.** `ldec` y `mia` aparecen únicamente como registros UDIF en `mach-cxd4132/udif/platform.c`; `ldec` lleva IRQ y DMAC canal 3; `mia`, IRQ y DMAC canal 2. Los Makefiles CXD no compilan controlador de sensor, ISP, JPEG ni esos dos nombres.

**NO VERIFICADO.** No hay significado funcional recuperable para esos nombres ni una ruta de imagen que los conecte a FEA/DMM.

**DESCARTADO — módulo/interfaz literal.** No existe DMM Sony como `dmm.ko` ni definición de módulo. Las escasas coincidencias de `dmm` pertenecen a OMAP4 y TI DSPBridge, arquitecturas ajenas a CXD y sin vínculo con el firmware de cámara.

## Separación obligatoria de evidencia

- **Código fuente real:** todos los paths y líneas anteriores, extraídos del tar OSS sin modificación.
- **Binarios propietarios ya analizados:** registro FEA/MPR y carácter asíncrono de `EncodeStill`, declarados en el informe S18 como antecedentes, no corroborados por este kernel.
- **Inferencias comparativas:** solo las marcadas como INFERENCIA; no constituyen prueba de `DmmShare`, `DmmClose`, callback de codificación ni comportamiento de SilentShutter.
