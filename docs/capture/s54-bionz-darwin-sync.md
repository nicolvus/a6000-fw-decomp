# S54-B — Recepción en BIONZ X: lo demostrado y la frontera (20-10-2026)

REA 6.5.0 + Ghidra 12.1.4 sobre `av-cam.bin` (SHA `b60c845c…56bb9`, base `0x43541000`; sesión única, análisis en frío 440 s, cerrada al terminar)
+ capstone (Thumb, `skipdata`) + texto de esquemas. Complementa [s54-p4c-signal-trace.md](s54-p4c-signal-trace.md).

## 1. Cadena buscada y eslabones

`Darwin P4C → IC6000 SENS_B/GPIO_9 → ??? → control de captura → sensor`

| Eslabón | Estado |
|---|---|
| Darwin P4C←0 en todas las capturas | VERIFICADO (informe 1) |
| P4C → IC6000 pines `SENS_B` (AA13) y `GPIO_9` (AD21) | VERIFICADO (esquema) |
| Primitivas GPIO de BIONZ en `av-cam` | **VERIFICADO** (§2) |
| Pin `GPIO_9`/`SENS_B` → par (canal, bit) usado por el código | **NO VERIFICADO** (§3) |
| Lector de ese pin / manejador / callback | **NO LOCALIZADO** |
| Acción sobre el sensor o solo informe de fase | **NO DECIDIBLE** con la evidencia actual |

## 2. Primitivas GPIO de BIONZ (VERIFICADO)

Literales de la zona `0x4398f904–0x4398fa30`: base `0xf2910000` (coincide con `CXD90014_GPIO_BASE` del OSS Linux `mach-cxd90014`; el A6000 usa un
CXD90027, la identidad de mapa es **INFERENCIA**), offsets `+0x20` (INEN), `+0x30` (PORT), `+0x40` (WDATA), canal `ch<<8`.

| Función (av-cam) | Semántica (pseudocódigo REA) |
|---|---|
| `0x43b5e2bc(ch,bit)` | **`gpio_get`**: `ch≤0x11`; lee RDATA (`+0x10`) si DIR=0, si no WDATA (`+0x40`) |
| `0x43b5e22e(ch,bit,cfg*)` | configuración de pin (DIR/INEN/PORT/…), 11 puntos de llamada |
| `0x43b5e29a` | `gpio_set(ch,bit,val)` |

Hay 97 llamadas a estas funciones (`analysis/s54/bionz_gpio_calls.py`): 50 `get`, 4 `set`, 43 `cfg`. Solo 10 tienen canal inmediato
(p. ej. `cfg 7/4,5,6` en `0x43727e6e…`, `set 15/5` en `0x436d670a`); ningún `get` tiene canal inmediato; el resto lee el par de variables globales.

## 3. Por qué el consumidor no está cerrado

Los lectores de la tarea CAIF/CA (`0x436b945c`, `0x436ba67c`, `0x436bb088`, `0x436bb9d8`, `0x436bc0a0`, `0x436bcb60`; trazas «S2REQ HI/LO», «CamSioSnd InRel H»,
`0x144/0x157`) llaman a `gpio_get` con **variables globales** (`0x43e77298…0x43e772cc`, accedidas por GOT `0x4402xxxx`). Esas celdas valen 0 en la imagen
y **ningún código de av-cam las escribe** (xrefs solo de lectura): el par (canal, bit) lo inyecta el entorno (módulo/arranque) y no es recuperable
estáticamente. Por tanto no se puede afirmar ni negar que alguno de esos lectores muestree `GPIO_9`; la lectura natural (líneas de petición REQ/S2REQ del
enlace MSS) apunta a **otros** pines. `SENS_B` es una función dedicada del bloque mecánico de BIONZ: no se encontró su registro.

## 4. Eventos CAIF relacionados (VERIFICADO el contenido de la tabla; el uso, INFERENCIA)

Tabla de nombres de traza `0x43fe8138+12·i` `{nombre, código, tamaño}`: `CaptureRequest 0x121`, `CaptureStartRes 0x122`, `ExposureReady 0x129`,
`ExposureEndNotify 0x12a` (2 B), `ExposureEndRes 0x12b`, `ExpBefore 0x135`, **`ExpStartComp 0x136`** (clase 4, evento interno), `ImageReadStartNotfy 0x12d`,
`ImageReadCompNorify 0x130`, `ReleaseLock 0x131`, `S2REQ HI 0x13a`. `0x436b8aec` (callers sin xref directo) responde a `ExposureEndNotify`
enviando op `0x40300` con 2 bytes a 0. Conclusión prudente: BIONZ y Darwin intercambian por **mensajes** el fin de exposición; la existencia de
`ExpStartComp` sugiere una notificación de «inicio de exposición completado», pero **no se demuestra** que dependa de P4C.

## 5. Hipótesis

| H | Estado | Evidencia a favor | En contra / límite | Próxima prueba |
|---|---|---|---|---|
| H54-1 P4C informa del inicio | **INFERENCIA** | única operación común a todas las ramas; nombre de la red; cableado a BIONZ | consumidor no hallado; polaridad/idle NO VERIFICADO | traza lógica pasiva de P4C y `GPIO_9` (autorizada) |
| H54-2 A7S la usa en Silent | **PARCIAL** | Darwin A7S Silent mantiene P4C←0 (VERIFICADO) | lado BIONZ no comparado | repetir §2–3 en `av-cam` A7S |
| H54-3 BIONZ la usa para iniciar acciones del sensor | **NO VERIFICADO** | — | no hay consumidor; `ExpStartComp` es solo etiqueta | resolver pares de pines (módulo de arranque) |
| H54-4 recepción equivalente A7S/A6000 | **NO VERIFICADO** | emisión Darwin idéntica; cableado idéntico (SENS_B+GPIO_9) | BIONZ distinto (G01A vs G11D) | diff de `av-cam` A7S vs A6000 |

Límites: pseudocódigo REA, sin cámara; una consulta vacía no prueba ausencia (el lector podría usar el pin dedicado `SENS_B` vía registros no mapeados).
