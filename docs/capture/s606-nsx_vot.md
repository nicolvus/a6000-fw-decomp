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

## Afirmaciones cerradas (CAM-01, 03-11-2026)

| Afirmación | Estado y evidencia |
|---|---|
| Emisión (logger) | VERIFICADO (instrucciones): 7 sitios `ldr`+`add pc` cargan las cadenas (7) desde 5 funciones (`0x43a37bb8`, `0x43a37c02`, `0x43a37d0c`, `0x43a37dd6`, `0x43a37e2c`); el primer `bl` tras cada carga va a `0x43a37b0c`. |
| Equivalencia funcional A7S/A6300 | VERIFICADO (bytes): el token `[NSX_VOT]` tiene 0 coincidencias en A7S fw3.20 y 0 en A6300 fw2.01 (A6000 fw3.21: 7); se compara solo la presencia del token, no cuerpos de función. |
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
