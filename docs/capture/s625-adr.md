# S625 — ADR: evidencia de cadenas

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S625. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [adr.json](../../analysis/s625_adr/adr.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

1 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43cce3fa` | `"[CAM_UTIL_SENS]: >>[FILE_NUM]%x [ADR]%x [SIZE]%x"` |

CORRECCIÓN de esquema: `[ADR]` es un marcador interno a `0x43cce418`, no el prefijo de esta cadena. El prefijo real en `0x43cce3fa` es `[CAM_UTIL_SENS]: ` (17 bytes); JSON, test y verificador individual actualizados. Esto solo acredita texto, no una función ADR independiente.

## Afirmaciones cerradas (CAM-01, 03-11-2026)

| Afirmación | Estado y evidencia |
|---|---|
| Emisión (logger) | VERIFICADO (instrucciones): 4 sitios `ldr`+`add pc` cargan las cadenas (1) desde 3 funciones (`0x43901d50`, `0x43902168`, `0x43902418`); el primer `bl` tras cada carga va a `0x43901b7c`. |
| Equivalencia funcional A7S/A6300 | VERIFICADO (bytes): el token `[ADR]` tiene 0 coincidencias en A7S fw3.20 y 0 en A6300 fw2.01 (A6000 fw3.21: 1); se compara solo la presencia del token, no cuerpos de función. |
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
