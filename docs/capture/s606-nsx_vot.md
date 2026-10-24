# S606 — NSX_VOT: evidencia de cadenas

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S606. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [nsx_vot.json](../../analysis/s606_nsx_vot/nsx_vot.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

7 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43cfdb1e` | `"[NSX_VOT]: almhdl : bt stop error: %d"` |
| `0x43cfdb66` | `"[NSX_VOT]: osal_alloc_timer(): %d"` |
| `0x43cfdba6` | `"[NSX_VOT]: osal_alloc_timer(): handle alloc again!!"` |
| `0x43cfdc0a` | `"[NSX_VOT]: osal_free_timer(): handle NULL!!"` |
| `0x43cfdc5e` | `"[NSX_VOT]: osal_free_timer(): %d"` |
| `0x43cfdc9c` | `"[NSX_VOT]: osal_set_timer(): %d"` |
| `0x43cfdcd8` | `"[NSX_VOT]: osal_can_timer(): %d"` |

### Cadenas gemelas y deltas

Se verifican datos, sin afirmar que ambos mensajes se emitan.

| Principal | Gemela | Delta (B) |
|---|---|---|
| `0x43cfdb1e` | `0x43cfdb44` | 38 |
| `0x43cfdb66` | `0x43cfdb88` | 34 |
| `0x43cfdba6` | `0x43cfdbda` | 52 |
| `0x43cfdc0a` | `0x43cfdc36` | 44 |
| `0x43cfdc5e` | `0x43cfdc7f` | 33 |
| `0x43cfdc9c` | `0x43cfdcbc` | 32 |
| `0x43cfdcd8` | `0x43cfdcf8` | 32 |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 11, "twin_prefix_length": 7}`.

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
