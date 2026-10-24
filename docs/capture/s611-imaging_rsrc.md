# S611 — IMAGING_RSRC: evidencia de cadenas

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S611. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [imaging_rsrc.json](../../analysis/s611_imaging_rsrc/imaging_rsrc.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

5 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43ca492f` | `"[IMAGING_RSRC]: [GOLFSHOT]SA_LPF Exec[%02d] Err: sa_err[0x%x] intfct[0x%x] mbox1[%x]"` |
| `0x43ca4984` | `"[IMAGING_RSRC]: [GOLFSHOT]SA_BGEST Exec Err: sa_err[0x%x] intfct[0x%x] mbox1[%x]"` |
| `0x43ca49d5` | `"[IMAGING_RSRC]: [GOLFSHOT]SA_SSP Exec[%03d] Err: sa_err[0x%x] intfct[0x%x] mbox1[%x]"` |
| `0x43ca4a2a` | `"[IMAGING_RSRC]: [GOLFSHOT] correctSndDetResult(WARNING): Corrected Value is Out of SoundDetBuff"` |
| `0x43ca4a8a` | `"[IMAGING_RSRC]: [GOLFSHOT]vfc2indx: Shot Timing Transform Error"` |

### Esquema core_text

Cada núcleo coincide con el sufijo NUL de la cadena A6000. Estas son las coincidencias exactas por firmware; una coincidencia puede ser sufijo y no implica un literal autónomo ni equivalencia de código.

| Núcleo A6000 | Coincidencias A7S fw3.20 | Coincidencias A6300 fw2.01 |
|---|---|---|
| `0x43ca493f` | 0x43ca9dfa | 0x43db05a8 |
| `0x43ca4994` | 0x43ca9e3f | 0x43db05ed |
| `0x43ca49e5` | 0x43ca9e80 | 0x43db062e |
| `0x43ca4a3a` | 0x43ca9ec5 | ninguna |
| `0x43ca4a9a` | 0x43ca9f15 | 0x43db0673 |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 16, "core_prefix_length": 10, "composite_prefix_length": 26}`.

## Afirmaciones pendientes

| Afirmación | Estado y evidencia necesaria |
|---|---|
| Logger dual | VERIFICADO_ESTATICO para las cinco trazas: la ruta con prefijo llama a `0x4379a274` y la ruta sin prefijo a `0x43902718`; ejecución real NO_VERIFICADO. |
| Equivalencia funcional A7S/A6300 | NO_VERIFICADO: faltan contratos, entradas/salidas y callees comparados. |
| Equivalencia de código | NO_VERIFICADO: faltan cuerpos e instrucciones comparados entre modelos. |
| Ausencia de relación con el obturador | NO_VERIFICADO: el texto no excluye una ruta funcional. |
| Recuentos y semántica de differential | NO_VERIFICADO: los recuentos históricos carecen de criterio de selección reproducible. |
| Funciones emisoras, sitios, trazas muertas y significado de nombres | NO_VERIFICADO: requieren referencias e instrucciones propias. |

Las cinco parejas de cargas PC-relativas, sus llamadas y el salto compartido de la primera
traza se comprueban contra bytes de `av-cam.bin` en `analysis/verify_s6xx.py`.
La primera usa `0x4379a35e/0x4379a360 → 0x4379a362` y
`0x4379a370/0x4379a374 → 0x4379a3e4`; `0x4379a376` une los bloques.
El emisor local `0x4379a274` construye y envía un mensaje con
`0x4356120c` (`0x4379a308`); las otras cuatro parejas se enumeran en
`logger_paths` del JSON. Esto acredita **dos rutas estáticas** por traza,
no que ambas se ejecuten en una cámara ni que tengan la misma entrega final.
`shutter_line=NEGATIVO ACOTADO` sigue siendo una etiqueta histórica de triaje
léxico; su estado funcional es NO_VERIFICADO. S51 no cambia.

## Reproducción

```bash
.venv/bin/python analysis/verify_s6xx.py
.venv/bin/python -m pytest -q tests/test_s60[5-9]_*.py tests/test_s61[0-9]_*.py tests/test_s62[0-7]_*.py tests/test_s6xx*.py
```

El JSON de resultados incluye rutas, tamaños y SHA-256 de los tres firmwares. Los campos adicionales no sustentados tienen cobertura explícita NO_VERIFICADO; las comprobaciones de esquema individuales no sustituyen la lectura del firmware.
