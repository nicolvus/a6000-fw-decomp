# S615 — CAMERA_IS/EIS: evidencia de cadenas

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S615. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [eis.json](../../analysis/s615_eis/eis.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

4 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43c9a2b2` | `"[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzPower error!"` |
| `0x43c9a2eb` | `"[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzGridH error!"` |
| `0x43c9a324` | `"[CAMERA_IS][EIS]: GyroAD[p],GyroAD[y], %d, %d"` |
| `0x43c9a352` | `"[CAMERA_IS][EIS]: %x, %d, %d"` |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 17}`.

## Afirmaciones cerradas (S-CAMERA, 03-11-2026)

| Afirmación | Estado y evidencia |
|---|---|
| Emisión (logger) | VERIFICADO (instrucciones): 5 sitios `ldr`+`add pc` cargan las 4 cadenas desde 3 funciones (`0x43702dac`, `0x43704d90`, `0x437046a4`); el primer `bl` tras cada carga va a `0x437026ac`, `0x437041dc`. «Dual» no es una propiedad medida: se sustituye por estos recuentos. |
| Equivalencia funcional A7S/A6300 | VERIFICADO (bytes): el token `[CAMERA_IS][EIS]` tiene 0 coincidencias en A7S fw3.20 y 0 en A6300 fw2.01 (A6000 fw3.21: 4); no hay contraparte con este token que comparar. |
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
