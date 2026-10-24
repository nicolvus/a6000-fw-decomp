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
