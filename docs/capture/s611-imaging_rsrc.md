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

## Afirmaciones cerradas (CAM-01, 03-11-2026)

| Afirmación | Estado y evidencia |
|---|---|
| Emisión (logger) | VERIFICADO (instrucciones): 6 sitios `ldr`+`add pc` cargan las cadenas (5) desde 3 funciones (`0x4379a32c`, `0x4379a41c`, `0x4379a5d4`); el primer `bl` tras cada carga va a `0x4379a274`. Las dos rutas estáticas por traza (con prefijo → `0x4379a274`, sin prefijo → `0x43902718`) se detallan abajo. |
| Equivalencia funcional A7S/A6300 | VERIFICADO (bytes): el token `[IMAGING_RSRC]` tiene 0 coincidencias en A7S fw3.20 y 0 en A6300 fw2.01 (A6000 fw3.21: 5); no hay contraparte con este token que comparar. |
| Equivalencia de código | VERIFICADO (bytes): sin contraparte por token en A7S/A6300 (fila anterior); no se afirma equivalencia. |
| Relación con el obturador | VERIFICADO (grafo `bl` directo, profundidad ≤ 3 desde cada emisora): alcanza 0 de las 7 funciones de obturador conocidas; el alcance excluye llamadas indirectas (vtable/puntero). [S51](s51-decision.md) se mantiene. |
| Recuentos de `differential` | VERIFICADO (reproducible): coincidencias exactas del token en `av-cam.bin` de cada modelo, con `analysis/camera_closure/closure.py`. |
| Funciones emisoras, sitios y trazas sin uso | VERIFICADO: sitios y funciones en `analysis/camera_closure/closure.json`; cadenas sin sitio: 0. El significado de los nombres no se afirma. |

Las cinco parejas de cargas PC-relativas, sus llamadas y el salto compartido de la primera
traza se comprueban contra bytes de `av-cam.bin` en `analysis/verify_s6xx.py`.
La primera usa `0x4379a35e/0x4379a360 → 0x4379a362` y
`0x4379a370/0x4379a374 → 0x4379a3e4`; `0x4379a376` une los bloques.
El emisor local `0x4379a274` construye y envía un mensaje con
`0x4356120c` (`0x4379a308`); las otras cuatro parejas se enumeran en
`logger_paths` del JSON. Esto acredita **dos rutas estáticas** por traza,
no que ambas se ejecuten en una cámara ni que tengan la misma entrega final.
`shutter_line` era una etiqueta histórica de triaje léxico, sustituida por la fila «Relación con el obturador». S51 no cambia.

## Reproducción

```bash
.venv/bin/python analysis/verify_s6xx.py
.venv/bin/python -m pytest -q tests/test_s60[5-9]_*.py tests/test_s61[0-9]_*.py tests/test_s62[0-7]_*.py tests/test_s6xx*.py
```

El JSON de resultados incluye rutas, tamaños y SHA-256 de los tres firmwares. las comprobaciones de esquema individuales no sustituyen la lectura del firmware.
