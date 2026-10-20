# Inventario de fuentes oficiales Sony OSS — sesión 18

Clasificación obligatoria: VERIFICADO / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO.
Extracción parcial en `analysis/session18/main/sony-oss-extracted/` (archivos originales en la raíz, sin modificar).

## 1. Archivos encontrados en la raíz del proyecto

| Archivo | Tamaño | SHA-256 | Formato |
|---|---|---|---|
| `linux-kernel.tar.gz` | 52.843.927 B | `b1c74cc1a0160a7fceced6f88fa35521adc431205ad1ebc8a413d20b653785b1` | gzip, mtime interno 2014-02-19 03:57 |
| `webkit.tar.gz` | 27.744.494 B | `04bbdf421be8e1de5c7b250d9631d11fde873d3214f6b962e3a254a81bc8571b` | gzip, mtime interno 2014-02-19 04:05 |
| `iproute2.tar.gz` | 464.217 B | `6f82fd70f8e130827f4f3114b670083075323cb2e753babea9f1de4959d754b7` | gzip, mtime interno 2014-02-19 04:05 |
| `iptables.tar.gz` | 242.158 B | `1b864a78a8a17c36984d58045aa1c4370b340c43538fe709fb83e2fbe77a13b0` | gzip, mtime interno 2014-02-19 04:05 |
| `libpng.tar.gz` | 875.241 B | `347b6a5714dd87c54ef888631ac41a7a54987ad0022123ce09e1e043dc83f3b4` | gzip, mtime interno 2014-02-19 04:05 |
| `wpa_supplicant.tar.gz` | 673.655 B | `b02342b79b9fc6696310be5d91f730656c1e4e2aebafaa5634858c72da579d67` | gzip, mtime interno 2014-02-19 04:07 |

Hashes verificados con `sha256sum`, 64 caracteres hexadecimales cada uno (confirmado programáticamente).

**No hay ningún archivo con "ILCE", "6000", "6300", "A6000" ni "A6300" en el nombre.** Son paquetes GPL/BSD genéricos típicos de un portal Sony OSS, identificables como pertenecientes a un modelo concreto solo por metadatos internos (defconfig, fechas, comentarios), no por el nombre del paquete.

## 2. ¿ILCE-6000 o ILCE-6300?

**NO VERIFICADO cuál modelo exacto corresponde.** Ningún archivo, Makefile ni defconfig contiene literalmente "ILCE-6000" o "ILCE-6300". El kernel incluye `arch/arm/mach-cxd90014` y `arch/arm/mach-cxd4132` con defconfigs `cxd90014_android_*` — "CXD" es la nomenclatura de SoC propios de Sony Semiconductor, usados en varias cámaras de la época (A6000 y A6300 comparten generación de procesador BIONZ X). Sin un defconfig o comentario que cite el modelo de cámara explícitamente, **no se puede atribuir el paquete a un modelo concreto sin comparar con el segundo paquete (A6300) cuando/si esté disponible** (§5). Solo hay un paquete de kernel presente — no hay base de comparación A6000 vs A6300 en este inventario.

## 3. Versión de kernel

**VERIFICADO**: `linux/Makefile` → `VERSION=3 PATCHLEVEL=0 SUBLEVEL=27` → **Linux 3.0.27** ("Sneaky Weasel"), arquitectura `arch/arm` (+ `arch/um` para pruebas en espacio de usuario, sin relevancia).

## 4. Componentes y controladores incluidos

- **VERIFICADO**: `arch/arm/mach-cxd90014/` (SoC principal: boot, clock, gic, pcie, hwtimer, dap, fiq, pmon — soporte de plataforma genérico de SoC, sin nada específico de cámara/imagen).
- **VERIFICADO (corregido tras lectura real por Codex G/H en sesión 18)**: `arch/arm/mach-cxd4132/` (SoC secundario). `sdc.c`/`sdc-zqcal*.c` **NO es un controlador de tarjeta SD** como se infirió inicialmente por el nombre — es el controlador de **calibración de impedancia ZQ de memoria LPDDR** (RAM del SoC), ajeno tanto a la tarjeta SD como al catálogo DCF. Corrección declarada, no oculta: mi primera lectura del inventario fue una inferencia apresurada por el nombre del archivo, refutada por lectura directa del código por los agentes. `fcs.c` sigue sin función confirmada.
- **VERIFICADO**: defconfigs `cxd90014_android_*` confirman que el kernel arranca un userspace Android — consistente con la arquitectura LIRO/ObjCamera ya conocida (Java/Binder sobre Linux).
- **DESCARTADO** (búsqueda realizada, sin resultado real): no existe ningún driver, módulo ni cabecera con nombre `dmm`, `fea` o `mpr` en `drivers/mmc`, `drivers/mtd`, `drivers/video`, `drivers/media` del árbol liberado — los dos resultados de la búsqueda inicial (`via-sdmmc.c`, `dss_features.c`) son coincidencias de subcadena (`sdMMc`, `FEAtures`), no hallazgos reales. **La capa DMM/FEA/MPR es propietaria de Sony y no forma parte del código liberado bajo GPL.**
- `iproute2`, `iptables`, `wpa_supplicant`: utilidades de red userspace estándar de Android/Linux (`Android.mk` presente en los tres) — sin relación con imagen, memoria o almacenamiento.
- `libpng`: biblioteca de códec PNG estándar — sin relación directa con el pipeline JPEG/EncodeStill investigado.
- `webkit`: motor de navegador Android (JavaScriptCore + WebCore) — sin relevancia para ninguna de las 8 ramas de investigación.

## 5. Código fuente, cabeceras, parches, configuración o binarios

Todos los seis paquetes son **código fuente + configuración** (Makefiles, `.c`/`.h`, `defconfig`, `Android.mk`). **No se encontraron binarios precompilados ni parches sueltos (`.patch`/`.diff`) en el primer nivel inspeccionado.** No se ha hecho una búsqueda exhaustiva recursiva de `.patch` dentro de los 20.623 entradas del kernel por coste de tiempo — queda **NO VERIFICADO** a nivel exhaustivo, declarado explícitamente en vez de asumir que no existen.

## 6. Módulos relevantes para memoria, DMA, comunicaciones, imagen o almacenamiento

- **Memoria/DMA**: sin hallazgo de DMM real (§4). `mach-cxd90014` tiene gestión de PCIe (`pcie*.c`) y caché L2 (`pl310.S`) — genérico de SoC, no específico de imagen.
- **Comunicaciones**: `wpa_supplicant` (WiFi userspace), `iproute2`/`iptables` (red). Sin relación con IPC interno del firmware (RelMgr/ObjMsg no son parte del kernel liberado).
- **Imagen**: ningún driver V4L2 de sensor ni codificador JPEG/ISP localizado en `drivers/media` con nombre reconocible de Sony; **no se ha hecho inventario exhaustivo de todo `drivers/media`** (cientos de archivos) — NO VERIFICADO a nivel exhaustivo.
- **Almacenamiento**: `drivers/mmc/host/` contiene el host genérico SD estándar de Linux. **Corrección (sesión 18, Codex H)**: `mach-cxd4132/sdc.c` NO es el controlador SD — es calibración de LPDDR (ver §4). El controlador SD real de este SoC, si existe en el árbol liberado, no se ha identificado todavía. En cualquier caso, ninguna pieza del kernel liberado **contiene el catálogo DCF propietario** (eso es de MPR, capa de firmware no liberada).

## 7. Duplicados o versiones distintas

No hay duplicados — seis paquetes únicos, un solo conjunto. **No hay un segundo paquete etiquetado A6300** disponible en la raíz: la comparación A6000 vs A6300 exigida en el encargo **queda pendiente** por ausencia de la segunda fuente, tal como prevé el propio encargo ("Si solo está disponible el paquete de la A6000, limitar el análisis a esa fuente y dejar la comparación pendiente").


## 8. Licencias por paquete

| Paquete | Licencia |
|---|---|
| `linux-kernel.tar.gz` | GPLv2 (`linux/COPYING`) |
| `iproute2.tar.gz` | GPLv2 |
| `iptables.tar.gz` | GPLv2 |
| `wpa_supplicant.tar.gz` | GPLv2 |
| `libpng.tar.gz` | BSD-like (`libpng/LICENSE`, `MODULE_LICENSE_BSD_LIKE`) |
| `webkit.tar.gz` | No verificado en este inventario (típicamente LGPL/BSD mixto en WebKit; no se extrajo `COPYING` por bajo valor para las 8 ramas) |

## 9. Advertencia obligatoria

**Ninguno de estos paquetes contiene `libObj.so`, `libMWF.so`, `libmpr.so`, RelMgr, CaptureManager, ObjCamera/ObjEffect/ObjStillRecorder, EncodeStill, DMM, FEA ni CameraSequence/CameraEx.** Son la base GPL/BSD del sistema operativo (kernel Linux 3.0.27 + utilidades de red + codecs + motor web), no las piezas propietarias del stack de cámara ya analizado por desensamblado. Cualquier hallazgo de las 8 ramas sobre estos paquetes es, como máximo, **contexto de plataforma** (SoC, arranque, drivers genéricos de SD/red), nunca prueba directa del comportamiento de los binarios propietarios.
