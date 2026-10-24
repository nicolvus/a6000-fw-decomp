# Tabla de hallazgos S605–S627

**Fecha:** 23-10-2026  
**Firmware verificado:** A6000 fw3.21 `av-cam.bin` (base `0x43541000`, 11.4 MB)  
**Método:** Lectura directa de bytes (cadenas de traza), verificación de código (logger global), búsqueda de palabras clave del obturador en cadenas de traza.  
**NO verificado por este lote:** logger dual (requiere xrefs/REA), equivalencia funcional A7S/A6300 (requiere esos firmwares), equivalencia de código (requiere comparación de instrucciones).

## Resumen

| Categoría | Cantidad | Detalle |
|-----------|----------|---------|
| Aceptados (VERIFICADO) | 22 | Cadenas de traza verificadas byte-por-byte en firmware; logger global como código; línea del obturador negativa |
| Rechazados (X) | 1 | DET_DIR (S618): alias de S617, 0 trazas propias, no módulo independiente |
| Pendientes / NO_VERIFICADO | 3 × 23 | Logger dual, equivalencia funcional, equivalencia de código (en todos los 23 módulos) |

## Tabla detallada por módulo

| Módulo | Cadenas | Logger dual | Equiv. funcional | Equiv. código | Obturador | Estado general |
|--------|---------|-------------|------------------|---------------|-----------|----------------|
| S605 JPEG | V | NV | NV | NV | V | ACEPTADO |
| S606 NSX_VOT | V | NV | NV | NV | V | ACEPTADO |
| S607 CAM_CMD | V | NV | NV | NV | V | ACEPTADO |
| S608 MOUNT_INFO | V | NV | NV | NV | V | ACEPTADO |
| S609 CAMERA_IS/DIST | V | NV | NV | NV | V | ACEPTADO |
| S610 ACCY/INFO/HOUSING | V | NV | NV | NV | V | ACEPTADO |
| S611 IMAGING_RSRC | V | NV | NV | NV | V | ACEPTADO |
| S612 CAMERA_IS/MOUNT | V | NV | NV | NV | V | ACEPTADO |
| S613 MOUNT_WARNING | V | NV | NV | NV | V | ACEPTADO |
| S614 ZPD | V | NV | NV | NV | V | ACEPTADO |
| S615 CAMERA_IS/EIS | V | NV | NV | NV | V | ACEPTADO |
| S616 LENS_PDR | V | NV | NV | NV | V | ACEPTADO |
| S617 CAMERA_DEVICE/DET_DIR | V | NV | NV | NV | V | ACEPTADO |
| S618 DET_DIR | X | NV | NV | NV | V | RECHAZADO |
| S619 SENSER | V | NV | NV | NV | V | ACEPTADO |
| S620 STABILIZER | V | NV | NV | NV | V | ACEPTADO |
| S621 AVOUT | V | NV | NV | NV | V | ACEPTADO |
| S622 AVR | V | NV | NV | NV | V | ACEPTADO |
| S623 JIRO | V | NV | NV | NV | V | ACEPTADO |
| S624 UTILITY | V | NV | NV | NV | V | ACEPTADO |
| S625 ADR | V | NV | NV | NV | V | ACEPTADO |
| S626 CAMERA_DETECT_FC | V | NV | NV | NV | V | ACEPTADO |
| S627 EO_SW | V | NV | NV | NV | V | ACEPTADO |

Leyenda: **V** = Verificado contra firmware (bytes/instrucciones), **X** = Rechazado (no cumple), **NV** = NO_VERIFICADO (afirmación no demostrada por la evidencia disponible).

## Detalle de afirmaciones por categoría

### 1. Cadenas de traza (VERIFICADO en 22/23)

Cada cadena de traza reportada en los JSONs fue verificada byte-por-byte contra `av-cam.bin` en la dirección virtual declarada (base `0x43541000`). Todas coinciden exactamente (tras normalizar trailing whitespace).

**Excepción:** S618 DET_DIR tiene 0 cadenas propias (es alias de S617 CAMERA_DEVICE/DET_DIR), por lo que no hay cadenas que verificar.

### 2. Logger dual (NO_VERIFICADO en 22/23)

Todos los informes afirman que la fw3.21 "duplica la traza" (nueva con prefijo de módulo + vieja con logger global `0x43902718`). **Esta afirmación NO está demostrada** por la presencia de cadenas. Requiere:
- Xrefs desde el código a cada dirección de cadena
- Confirmación de instrucciones `bl 0x43902718` (llamada al logger global)
- Análisis de literal pools para verificar que se cargan tanto la cadena con prefijo como la sin prefijo

El logger global `0x43902718` **sí existe como código** en el firmware (no son cerros ni relleno 0xFF), verificado en offset `0x3c1718`.

### 3. Equivalencia funcional A7S/A6300 (NO_VERIFICADO en 23/23)

Los informes afirman que el código subyacente "existe igual" en A7S fw3.20 y A6300 fw2.01 con diferente prefijo de traza. **Esta afirmación NO está demostrada**. Requiere análisis de los firmwares A7S y A6300 con los mismos métodos (cadenas + xrefs + instrucciones). La presencia de cadenas núcleo similares no demuestra equivalencia de código.

### 4. Equivalencia de código (NO_VERIFICADO en 23/23)

Los informes afirman "código equivalente" entre modelos. **Esta afirmación NO está demostrada**. Requiere comparación de instrucciones (disassembly) entre A6000 fw3.21 y A7S/A6300 para demostrar que las funciones son equivalentes más allá del prefijo de traza.

### 5. Línea del obturador (VERIFICADO en 23/23)

Ninguna de las cadenas de traza de los 23 módulos contiene palabras clave del obturador electrónico (`shutter`, `silent`, `curtain`, `electro`, `mech`, `obtur`, `sensor`, `readout`, `imager`, `iso`, `apert`, `expos`, `brack`, `drive`, `release`, `flash`, `sync`, `vsync`, `capture`, `shot`, `still`, `movie`, `focus`, `svd`, `shd`, `spl`, `frame`) como palabras completas. Se excluyeron falsos positivos conocidos:
- "shot" en "Shot Timing Transform" (S611): contexto de ráfaga GOLFSHOT, no obturador
- "sync" en "osal_reg_sync_msg_queue_cb" (S620): registro sincrónico, no vsync

Esto mantiene **S51 (A=NO, B=NO, C=NO)**: no hay camino de exposición electrónica demostrado.

## Archivos modificados/creados

### Creados
- `analysis/verify_s6xx.py` — Script de verificación masiva contra firmware
- `analysis/update_s6xx_json.py` — Script de actualización de JSONs con verification_status
- `analysis/fix_s6xx_md.py` — Script de corrección de informes .md
- `analysis/fix_s6xx_tests.py` — Script de corrección de tests individuales
- `analysis/fix_s6xx_tests2.py` — Script de corrección de mensajes de error en tests
- `analysis/s6xx_verification_results.json` — Resultados de verificación
- `tests/test_s6xx_firmware_verification.py` — Test unificado de verificación contra firmware

### Modificados (23 JSONs)
- `analysis/s60{5,6,7,8,9}_*/*.json` y `analysis/s61{0..9}_*/*.json` y `analysis/s62{0..7}_*/*.json` — Agregado `verification_status`

### Modificados (23 informes .md)
- `docs/capture/s60{5,6,7,8,9}-*.md` y `docs/capture/s61{0..9}-*.md` y `docs/capture/s62{0..7}-*.md` — Afirmaciones de logger dual, equivalencia funcional y equivalencia de código marcadas como NO_VERIFICADO

### Modificados (22 tests individuales)
- `tests/test_s60{5,6,7,8,9}_*.py` y `tests/test_s61{0..9}_*.py` y `tests/test_s62{0..7}_*.py` — `test_logger_dual` verifica `verification_status.logger_dual.status == "NO_VERIFICADO"`

### No modificados
- `tests/test_s618_det_dir.py` — Ya no tenía `test_logger_dual` (alias de S617)

## Próximos pasos pendientes

1. **Resolver logger dual** mediante REA: xrefs a direcciones de cadena, verificación de `bl 0x43902718`, análisis de literal pools.
2. **Resolver equivalencia funcional/código** mediante análisis de A7S fw3.20 y A6300 fw2.01 con los mismos métodos.
3. Los 22 módulos ACEPTADOS quedan sujetos a revisión si los pasos 1-2 revelan inconsistencias.