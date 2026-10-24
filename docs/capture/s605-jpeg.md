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

## Afirmaciones pendientes

| Afirmación | Estado y evidencia necesaria |
|---|---|
| Logger dual | NO_VERIFICADO: faltan cargas de argumentos, llamadas y flujo que acrediten las dos emisiones. |
| Equivalencia funcional A7S/A6300 | NO_VERIFICADO: faltan contratos, entradas/salidas y callees comparados. |
| Equivalencia de código | NO_VERIFICADO: faltan cuerpos e instrucciones comparados entre modelos. |
| Ausencia de relación con el obturador | NO_VERIFICADO: el texto no excluye una ruta funcional. |
| Recuentos y semántica de differential | NO_VERIFICADO: los recuentos históricos carecen de criterio de selección reproducible. |
| Funciones emisoras, sitios, trazas muertas y significado de nombres | NO_VERIFICADO: requieren referencias e instrucciones propias. |

El campo `logger_dual=null` significa desconocido. `shutter_line=NEGATIVO ACOTADO` es una etiqueta histórica de triaje léxico; su estado funcional es NO_VERIFICADO. Este lote no cambia la decisión S51.

## Reproducción

```bash
.venv/bin/python analysis/verify_s6xx.py
.venv/bin/python -m pytest -q tests/test_s60[5-9]_*.py tests/test_s61[0-9]_*.py tests/test_s62[0-7]_*.py tests/test_s6xx*.py
```

El JSON de resultados incluye rutas, tamaños y SHA-256 de los tres firmwares. Los campos adicionales no sustentados tienen cobertura explícita NO_VERIFICADO; las comprobaciones de esquema individuales no sustituyen la lectura del firmware.
