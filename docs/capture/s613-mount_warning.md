# S613 — MOUNT_WARNING: evidencia de cadenas

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S613. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [mount_warning.json](../../analysis/s613_mount_warning/mount_warning.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

5 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43c95691` | `"[MOUNT_WARNING]: [MOUNT AM]NO MEMBER CHECK_DATA:%d"` |
| `0x43c956c4` | `"[MOUNT_WARNING]: [MOUNT AM]NO MEMBER ERR_INFO:%d"` |
| `0x43c970fc` | `"[MOUNT_WARNING]: [BL]LIF Command : Illegal Command Received!!! : cmd=%04X"` |
| `0x43c97858` | `"[MOUNT_WARNING]: [MOUNT DRV]NO MEMBER PWR_MODE:%d"` |
| `0x43c98714` | `"[MOUNT_WARNING]: [BL]cam_cmd change!! reason=%03x now=%03x (0xC05:PB 0xC06:POFF)"` |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 17}`.

CORRECCIÓN de cobertura: Cinco campos `sub_prefix` contrastados como marcadores ASCII dentro de las trazas NUL; direcciones en `verification_status.trace_annotations`. La pertenencia a `sub_prefixes` también se valida.

## Afirmaciones cerradas (S-CAMERA, 03-11-2026)

| Afirmación | Estado y evidencia |
|---|---|
| Emisión (logger) | VERIFICADO (instrucciones): 5 sitios `ldr`+`add pc` cargan las cadenas (5) desde 5 funciones (`0x436dffe0`, `0x436e0004`, `0x436e2e32`, `0x436e4156`, `0x436e5e3c`); el primer `bl` tras cada carga va a `0x436dff34`, `0x436e03b0`, `0x436e40a8`, `0x436e41e4`. «Dual» no es una propiedad medida: se sustituye por estos recuentos. |
| Equivalencia funcional A7S/A6300 | VERIFICADO (bytes): el token `[MOUNT_WARNING]` tiene 0 coincidencias en A7S fw3.20 y 0 en A6300 fw2.01 (A6000 fw3.21: 5); no hay contraparte con este token que comparar. |
| Equivalencia de código | VERIFICADO (bytes): sin contraparte por token en A7S/A6300 (fila anterior); no se afirma equivalencia. |
| Relación con el obturador | VERIFICADO (grafo `bl` directo, profundidad ≤ 3 desde cada emisora): alcanza 0 de las 7 funciones de obturador conocidas; el alcance excluye llamadas indirectas (vtable/puntero). [S51](s51-decision.md) se mantiene. |
| Recuentos de `differential` | VERIFICADO (reproducible): coincidencias exactas del token en `av-cam.bin` de cada modelo, con `analysis/camera_closure/closure.py`. |
| Funciones emisoras, sitios y trazas sin uso | VERIFICADO: sitios y funciones en `analysis/camera_closure/closure.json`; cadenas sin sitio: 0. El significado de los nombres no se afirma. |

Los campos históricos `logger_dual` y `shutter_line` (triaje léxico) quedan sustituidos por la tabla anterior.

## Reproducción

```bash
.venv/bin/python analysis/verify_s6xx.py
.venv/bin/python -m pytest -q tests/test_s60[5-9]_*.py tests/test_s61[0-9]_*.py tests/test_s62[0-7]_*.py tests/test_s6xx*.py
```

El JSON de resultados incluye rutas, tamaños y SHA-256 de los tres firmwares. las comprobaciones de esquema individuales no sustituyen la lectura del firmware.
