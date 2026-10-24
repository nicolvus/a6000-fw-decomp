# S607 — CAM_CMD: evidencia de cadenas

**Actualización 24-10-2026 — logger dual VERIFICADO_ESTATICO.** Las seis
trazas cargan por PIC el texto prefijado en `r3`, llaman a un constructor
local de mensaje (`0x437fc0d4` para cinco; `0x437fc6a0` para la sexta),
cargan en `r0` el sufijo de la misma cadena y llaman o hacen salto de cola
a `0x43902718`. Las parejas de llamadas son:

| Traza | Constructor local | Logger global |
|---|---|---|
| `0x43caeb10` | `0x437fc374` | `0x437fc37e` |
| `0x43caeb3d` | `0x437fc3c2` | `0x437fc3d4` |
| `0x43caeb7d` | `0x437fc43c` | `0x437fc448` |
| `0x43caebc1` | `0x437fc468` | `0x437fc476` |
| `0x43caebe6` | `0x437fc4e2` | `0x437fc4ee` |
| `0x43caec20` | `0x437fc76c` | `0x437fc774` |

`logger_paths` en el [JSON](../../analysis/s607_cam_cmd/cam_cmd.json)
registra LDR/ADD, destinos de llamada y texto núcleo de cada par. El
verificador comprueba esas instrucciones contra el `av-cam.bin` original.
La primera ruta depende de las condiciones de su función y la segunda
puede ser un `b.w`; no se ha observado emisión en ejecución real. Las
equivalencias A7S/A6300 y el efecto en obturador siguen NO_VERIFICADO.

**Auditoría de la validación de OpenCode — 23-10-2026.** Este informe corrige las conclusiones históricas de S607. La presencia de texto no demuestra funciones, llamadas ni equivalencia entre modelos.

Datos: [cam_cmd.json](../../analysis/s607_cam_cmd/cam_cmd.json). Auditoría conjunta: [hallazgos S605–S627](S605-S627_tabla_hallazgos.md).

## Evidencia comprobada

6 cadenas principales verificadas contra A6000 fw3.21, base `0x43541000`, incluidos espacios, saltos de línea y NUL. Las direcciones son virtuales. El texto se muestra escapado como JSON.

| Dirección | Texto |
|---|---|
| `0x43caeb10` | `"[CAM_CMD]: Warning! Now rocessing... req[%d]"` |
| `0x43caeb3d` | `"[CAM_CMD]: Error! Can't Transfer Request cur_state[%d] req[%d]\n"` |
| `0x43caeb7d` | `"[CAM_CMD]: Error! s_path_selector SetupTable cur_state[%d] req[%d]\n"` |
| `0x43caebc1` | `"[CAM_CMD]: Error! s_request is NULL!"` |
| `0x43caebe6` | `"[CAM_CMD]: Error! s_mode_sequencer SetupTable [%d]->[%d]\n"` |
| `0x43caec20` | `"[CAM_CMD]: Error! CheckReturnAllModlueResponse\n"` |

Longitudes declaradas comprobadas como bytes ASCII: `{"prefix_length": 11}`.

## Afirmaciones pendientes

| Afirmación | Estado y evidencia necesaria |
|---|---|
| Logger dual | VERIFICADO_ESTATICO para las seis rutas anteriores; emisión efectiva no observada. |
| Equivalencia funcional A7S/A6300 | NO_VERIFICADO: faltan contratos, entradas/salidas y callees comparados. |
| Equivalencia de código | NO_VERIFICADO: faltan cuerpos e instrucciones comparados entre modelos. |
| Ausencia de relación con el obturador | NO_VERIFICADO: el texto no excluye una ruta funcional. |
| Recuentos y semántica de differential | NO_VERIFICADO: los recuentos históricos carecen de criterio de selección reproducible. |
| Funciones emisoras, sitios, trazas muertas y significado de nombres | NO_VERIFICADO: requieren referencias e instrucciones propias. |

El campo `logger_dual=true` se limita a las rutas estáticas descritas. `shutter_line=NEGATIVO ACOTADO` es una etiqueta histórica de triaje léxico; su estado funcional es NO_VERIFICADO. Este lote no cambia la decisión S51.

## Reproducción

```bash
.venv/bin/python analysis/verify_s6xx.py
.venv/bin/python -m pytest -q tests/test_s60[5-9]_*.py tests/test_s61[0-9]_*.py tests/test_s62[0-7]_*.py tests/test_s6xx*.py
```

El JSON de resultados incluye rutas, tamaños y SHA-256 de los tres firmwares. Los campos adicionales no sustentados tienen cobertura explícita NO_VERIFICADO; las comprobaciones de esquema individuales no sustituyen la lectura del firmware.
