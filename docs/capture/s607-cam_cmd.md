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
equivalencias A7S/A6300 y el efecto en obturador quedan medidos en la tabla «Afirmaciones cerradas».

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

## Afirmaciones cerradas (S-CAMERA, 03-11-2026)

| Afirmación | Estado y evidencia |
|---|---|
| Emisión (logger) | VERIFICADO (instrucciones): 7 sitios `ldr`+`add pc` cargan las cadenas (6) desde 4 funciones (`0x437fc35c`, `0x437fc404`, `0x437fc6a4`, `0x437fc748`); el primer `bl` tras cada carga va a `0x437fc0d4`, `0x437fc6a0`, `0x439c5004`. «Dual» no es una propiedad medida: se sustituye por estos recuentos. |
| Equivalencia funcional A7S/A6300 | VERIFICADO (bytes): el token `[CAM_CMD]` tiene 0 coincidencias en A7S fw3.20 y 0 en A6300 fw2.01 (A6000 fw3.21: 6); no hay contraparte con este token que comparar. |
| Equivalencia de código | VERIFICADO (bytes): sin contraparte por token en A7S/A6300 (fila anterior); no se afirma equivalencia. |
| Relación con el obturador | VERIFICADO (grafo `bl` directo, profundidad ≤ 3 desde cada emisora): alcanza 0 de las 7 funciones de obturador conocidas; el alcance excluye llamadas indirectas (vtable/puntero). [S51](s51-decision.md) se mantiene. |
| Recuentos de `differential` | VERIFICADO (reproducible): coincidencias exactas del token en `av-cam.bin` de cada modelo, con `analysis/camera_closure/closure.py`. |
| Funciones emisoras, sitios y trazas sin uso | VERIFICADO: sitios y funciones en `analysis/camera_closure/closure.json`; cadenas sin sitio: 0. El significado de los nombres no se afirma. |

Los campos históricos `logger_dual` y `shutter_line` (triaje léxico) quedan sustituidos por la tabla anterior.

## Reproducción

```bash
.venv/bin/python analysis/verify_s6xx.py
.venv/bin/python -m pytest -q tests/test_s60[5-9]_*.py tests/test_s61[0-9]_*.py tests/test_s62[0-7]_*.py tests/test_s6xx*.py
```

El JSON de resultados incluye rutas, tamaños y SHA-256 de los tres firmwares. las comprobaciones de esquema individuales no sustituyen la lectura del firmware.
