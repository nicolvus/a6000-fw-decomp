# S608 — MOUNT_INFO: evidencia de cadenas

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S608. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [mount_info.json](../../analysis/s608_mount_info/mount_info.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

6 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43c970c7` | `"[MOUNT_INFO]: [BL]LIF Command Change : 0x%X >>> 0x%X"` |
| `0x43c98201` | `"[MOUNT_INFO]: [BL]UUD CallBack : MSGID_GET_VERSION"` |
| `0x43c98234` | `"[MOUNT_INFO]: [BL]UUD CallBack : MSGID_GET_FORCE_FIRMUP"` |
| `0x43c9826c` | `"[MOUNT_INFO]: [BL]UUD CallBack : MSGID_FIRM_UP_REQ"` |
| `0x43c9829f` | `"[MOUNT_INFO]: [BL]UUD CallBack : MSGID_PREPARE_UPDATE"` |
| `0x43c982d5` | `"[MOUNT_INFO]: [BL]UUD CallBack : MSGID_UNPLUG_USB"` |

### Esquema core_text

Cada núcleo coincide con el sufijo NUL de la cadena A6000. Estas son las coincidencias exactas por firmware; una coincidencia puede ser sufijo y no implica un literal autónomo ni equivalencia de código.

| Núcleo A6000 | Coincidencias A7S fw3.20 | Coincidencias A6300 fw2.01 |
|---|---|---|
| `0x43c970d5` | ninguna | ninguna |
| `0x43c9820f` | ninguna | ninguna |
| `0x43c98242` | ninguna | ninguna |
| `0x43c9827a` | ninguna | ninguna |
| `0x43c982ad` | ninguna | ninguna |
| `0x43c982e3` | ninguna | ninguna |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 14, "core_prefix_length": 4, "composite_prefix_length": 18}`.

**Ampliación estática 24-10-2026.** Una búsqueda PIC seguida de lectura de
instrucciones originales encuentra una carga del texto prefijado por cada una
de las seis trazas. La primera (`0x43c970c7`) se forma en `0x436e2e48/50`
y llama a `0x436e03b0` desde `0x436e2e52`. Las otras cinco forman sus
direcciones en `0x436fe64a`, `0x436fe672`, `0x436fe726`, `0x436fe80c` y
`0x436fe842`; todas llegan a la llamada `0x436fe844 → 0x436fe410`.
Este último formatea un mensaje y lo envía por `0x4356120c`; no es por sí
solo una segunda llamada a `0x43902718`. Por ejemplo, la llamada global
`0x436fe63c` usa otro texto, `0x43c97fc3` (`[BL]GetLensVersion Error`).
La búsqueda PIC no encontró una carga independiente de los seis sufijos,
pero ese negativo se limita al método y no descarta otras construcciones.
Por ello logger dual sigue **NO_VERIFICADO**. REA `xrefs` excedió 300 s en
el binario original; los resultados anteriores se comprobaron con Capstone
contra los bytes, sin ejecutar el firmware.

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
