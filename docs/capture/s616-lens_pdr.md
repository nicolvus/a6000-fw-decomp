# S616 — LENS_PDR: evidencia de cadenas

**Actualización 24-10-2026 — logger dual VERIFICADO_ESTATICO.** REA localizó
referencias al texto completo y a su sufijo en los cuatro casos; las cargas
PIC y llamadas se contrastaron con bytes originales. El texto prefijado pasa
en `r3` a `0x437085b0`, que formatea y envía un mensaje por `0x4356120c`;
el sufijo pasa en `r0` a `0x43902718`. Las parejas de llamadas son:

| Traza | Emisor local | Logger global |
|---|---|---|
| `0x43c9a7ca` | `0x43708a5e` | `0x43708a6a` (salto de cola) |
| `0x43c9a7fa` | `0x43708b7a` | `0x43708b82` |
| `0x43c9a82e` | `0x43708be8` | `0x43708bf0` |
| `0x43c9a862` | `0x43708c28` | `0x43708c30` |

El [JSON](../../analysis/s616_lens_pdr/lens_pdr.json) conserva cargas, sumas
PIC y destinos por traza; el verificador común los vuelve a leer del firmware.
Las rutas están condicionadas por sus funciones. Las equivalencias con A7S/A6300 y el efecto en obturador
quedan medidos en la tabla «Afirmaciones cerradas»; la emisión efectiva en cámara no se afirma.

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S616. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [lens_pdr.json](../../analysis/s616_lens_pdr/lens_pdr.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

4 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43c9a7ca` | `"[LENS_PDR]: BonoboDSP_Send: Data latch failed!\n"` |
| `0x43c9a7fa` | `"[LENS_PDR]: BonoboDSP_Send:[ch0]Data latch failed!\n"` |
| `0x43c9a82e` | `"[LENS_PDR]: BonoboDSP_Send:[ch1]Data latch failed!\n"` |
| `0x43c9a862` | `"[LENS_PDR]: BonoboDSP_Rcv: paritycheck_error!\n"` |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 12}`.

Los cuatro `core_text` son sufijos NUL comprobados de estas cadenas; las
coincidencias textuales por firmware constan en `verification_status` y no
establecen equivalencia funcional.

## Afirmaciones cerradas (CAM-01, 03-11-2026)

| Afirmación | Estado y evidencia |
|---|---|
| Emisión (logger) | VERIFICADO (instrucciones): 4 sitios `ldr`+`add pc` cargan las cadenas (4) desde 2 funciones (`0x437089da`, `0x43708a8e`); el primer `bl` tras cada carga va a `0x437085b0`. |
| Equivalencia funcional A7S/A6300 | VERIFICADO (bytes): el token `[LENS_PDR]` tiene 0 coincidencias en A7S fw3.20 y 0 en A6300 fw2.01 (A6000 fw3.21: 4); se compara solo la presencia del token, no cuerpos de función. |
| Equivalencia de código | VERIFICADO (bytes): no se afirma equivalencia; solo la presencia del token por modelo (fila anterior). |
| Relación con el obturador | VERIFICADO (grafo `bl` directo, profundidad ≤ 3 desde cada emisora): alcanza 0 de las 7 funciones de obturador conocidas; el alcance excluye llamadas indirectas (vtable/puntero). [S51](s51-decision.md) se mantiene. |
| Recuentos de `differential` | VERIFICADO (reproducible): coincidencias exactas del token en `av-cam.bin` de cada modelo, con `analysis/camera_closure/closure3.py`. |
| Funciones emisoras, sitios y trazas sin uso | VERIFICADO: sitios y funciones en `analysis/camera_closure/closure3.json`; cadenas sin sitio: 0. El significado de los nombres no se afirma. |

Los campos históricos `logger_dual` y `shutter_line` (triaje léxico) quedan sustituidos por la tabla anterior.

## Reproducción

```bash
.venv/bin/python analysis/verify_s6xx.py
.venv/bin/python -m pytest -q tests/test_s60[5-9]_*.py tests/test_s61[0-9]_*.py tests/test_s62[0-7]_*.py tests/test_s6xx*.py
```

El JSON de resultados incluye rutas, tamaños y SHA-256 de los tres firmwares. las comprobaciones de esquema individuales no sustituyen la lectura del firmware.
