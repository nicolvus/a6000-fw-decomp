# S620 — STABILIZER: evidencia de cadenas

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S620. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [stabilizer.json](../../analysis/s620_stabilizer/stabilizer.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

3 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43c9a1f3` | `"[CAMERA_IS][AS]: [STABILIZER][AS][osal_reg_sync_msg_queue_cb] %x"` |
| `0x43c9a234` | `"[CAMERA_IS][AS]: [STABILIZER][AS][upm_get_hcrn_ura] %x"` |
| `0x43c9a26b` | `"[CAMERA_IS][AS]: [STABILIZER][AS][osal_unreg_sync_msg_queue_cb] %x"` |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 33}`.

## Afirmaciones cerradas (CAM-01, 03-11-2026)

| Afirmación | Estado y evidencia |
|---|---|
| Emisión (logger) | VERIFICADO (instrucciones): 6 sitios `ldr`+`add pc` cargan las cadenas (3) desde 4 funciones (`0x436fecbe`, `0x436fee80`, `0x436ffab4`, `0x4371e4cc`); el primer `bl` tras cada carga va a `0x436febc4`, `0x4371e39c`. |
| Equivalencia funcional A7S/A6300 | VERIFICADO (bytes): el token `[STABILIZER]` tiene 0 coincidencias en A7S fw3.20 y 0 en A6300 fw2.01 (A6000 fw3.21: 3); se compara solo la presencia del token, no cuerpos de función. |
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
