# S605 — JPEG: evidencia de cadenas

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S605. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [jpeg.json](../../analysis/s605_jpeg/jpeg.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

17 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43ce0692` | `"[JPEG]: [cbJpegDebugClose] err : %d"` |
| `0x43ce06b6` | `"[JPEG]: [cbJpegDebugOpen] err : %d"` |
| `0x43ce06d9` | `"[JPEG]: [cbJpegDebugOpen] uid : 0x%x"` |
| `0x43ce0704` | `"[JPEG]: %s"` |
| `0x43ce070f` | `"[JPEG]: 0x%x"` |
| `0x43ce071c` | `"[JPEG]: [f_sa_dummy_send_msg] Start"` |
| `0x43ce0740` | `"[JPEG]: ERR. osal_try_valloc_msg. err=0x%x, L=%d"` |
| `0x43ce0771` | `"[JPEG]: [f_sa_dummy_send_msg] error_status = %d, unique_id = %d"` |
| `0x43ce07b1` | `"[JPEG]: ERR. osal_snd_msg. err=0x%x, L=%d"` |
| `0x43ce07db` | `"[JPEG]: ERR. osal_free_msg. err=0x%x, L=%d"` |
| `0x43ce0806` | `"[JPEG]: [f_sa_dummy_send_msg] Comp"` |
| `0x43ce0829` | `"[JPEG]: [f_2open][NormalOpen] jpegErr : %d"` |
| `0x43ce0854` | `"[JPEG]: [f_2open][SortOpen] jpegErr : %d"` |
| `0x43ce087d` | `"[JPEG]: [f_2open][TanzOpen] jpegErr : %d"` |
| `0x43ce08a6` | `"[JPEG]: [f_2close] unique_id : 0x%x"` |
| `0x43ce08ca` | `"[JPEG]: [f_2close][NormalClose] jpegErr : %d"` |
| `0x43ce08f7` | `"[JPEG]: [f_2close][SortClose] jpegErr : %d"` |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 8}`.

## Afirmaciones cerradas (CAM-01, 03-11-2026)

| Afirmación | Estado y evidencia |
|---|---|
| Emisión (logger) | VERIFICADO (instrucciones): 20 sitios `ldr`+`add pc` cargan las cadenas (17) desde 10 funciones (`0x4393cfc2`, `0x4393cfdc`, `0x4393d008`, `0x4393d1ba`, `0x4393d26e`, `0x4393d322`, `0x4393d3da`, `0x4393d494`, `0x4393d59c`, `0x4393d618`); el primer `bl` tras cada carga va a `0x43932a98`, `0x43932b88`, `0x43932bf8`, `0x4393cf10`, `0x439c0640`. |
| Equivalencia funcional A7S/A6300 | VERIFICADO (bytes): el token `[JPEG]` tiene 0 coincidencias en A7S fw3.20 y 0 en A6300 fw2.01 (A6000 fw3.21: 17); se compara solo la presencia del token, no cuerpos de función. |
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
