# S616 — LENS_PDR: evidencia de cadenas

**Actualización 24-10-2026 — logger dual VERIFICADO_ESTATICO.** REA localizó
referencias al texto completo y a su sufijo en los cuatro casos; las cargas
PIC y llamadas se contrastaron con bytes originales. El texto prefijado pasa
en `r3` a `0x437085b0`, que formatea y envía un mensaje por `0x4356120c`;
el sufijo pasa en `r0` a `0x43902718`. Las parejas de llamadas son:

| Traza | Emisor local | Logger global |
|---|---|---|
| `0x43c9a7ca` | `0x43708a5e` | `0x43708a6a` (salto de cola) |
| `0x43c9a7fa` | `0x43708b7a` | `0x43708b82` |
| `0x43c9a82e` | `0x43708be8` | `0x43708bf0` |
| `0x43c9a862` | `0x43708c28` | `0x43708c30` |

El [JSON](../../analysis/s616_lens_pdr/lens_pdr.json) conserva cargas, sumas
PIC y destinos por traza; el verificador común los vuelve a leer del firmware.
Las rutas están condicionadas por sus funciones. Emisión efectiva,
equivalencias con A7S/A6300 y efecto en obturador siguen NO_VERIFICADO.

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S616. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [lens_pdr.json](../../analysis/s616_lens_pdr/lens_pdr.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

4 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43c9a7ca` | `"[LENS_PDR]: BonoboDSP_Send: Data latch failed!\n"` |
| `0x43c9a7fa` | `"[LENS_PDR]: BonoboDSP_Send:[ch0]Data latch failed!\n"` |
| `0x43c9a82e` | `"[LENS_PDR]: BonoboDSP_Send:[ch1]Data latch failed!\n"` |
| `0x43c9a862` | `"[LENS_PDR]: BonoboDSP_Rcv: paritycheck_error!\n"` |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 12}`.

Los cuatro `core_text` son sufijos NUL comprobados de estas cadenas; las
coincidencias textuales por firmware constan en `verification_status` y no
establecen equivalencia funcional.

## Afirmaciones pendientes

| Afirmación | Estado y evidencia necesaria |
|---|---|
| Logger dual | VERIFICADO_ESTATICO para las cuatro rutas anteriores; emisión efectiva no observada. |
| Equivalencia funcional A7S/A6300 | NO_VERIFICADO: faltan contratos, entradas/salidas y callees comparados. |
| Equivalencia de código | NO_VERIFICADO: faltan cuerpos e instrucciones comparados entre modelos. |
| Ausencia de relación con el obturador | NO_VERIFICADO: el texto no excluye una ruta funcional. |
| Recuentos y semántica de differential | NO_VERIFICADO: los recuentos históricos carecen de criterio de selección reproducible. |
| Funciones emisoras, sitios, trazas muertas y significado de nombres | NO_VERIFICADO: requieren referencias e instrucciones propias. |

El campo `logger_dual=true` se limita a estas rutas estáticas. `shutter_line=NEGATIVO ACOTADO` es una etiqueta histórica de triaje léxico; su estado funcional es NO_VERIFICADO. Este lote no cambia la decisión S51.

## Reproducción

```bash
.venv/bin/python analysis/verify_s6xx.py
.venv/bin/python -m pytest -q tests/test_s60[5-9]_*.py tests/test_s61[0-9]_*.py tests/test_s62[0-7]_*.py tests/test_s6xx*.py
```

El JSON de resultados incluye rutas, tamaños y SHA-256 de los tres firmwares. Los campos adicionales no sustentados tienen cobertura explícita NO_VERIFICADO; las comprobaciones de esquema individuales no sustituyen la lectura del firmware.
