# S632 — `[MODE_*]`: sufijos de modo en los diagnósticos «CamCore acquire Error» y `[MODEFLG]`

**03-11-2026.** Documenta la familia `MODE` del censo S178: `[MODE_SNR_BUS_THROUGH]` (pendiente) y los cinco fragmentos `[MODE_CAP]`, `[MODE_CAP_DRP]`, `[MODE_CAP_PREREVIEW]`, `[MODE_CAP_SNR]`, `[MODE_CAP_SNR_PREREVIEW]` (descartados como módulo, [census.md](../../analysis/s178_census/census.md)), más `[MODE_SNR_BUS_THROUGH_PREREVIEW]` (no detectada por el censo: supera sus 24 caracteres) y la sub-etiqueta `[MODEFLG]` de [S144](s144-cam-util-sens.md). **No son módulos**: son el sufijo de siete mensajes de error del mismo bloque.

Datos: [mode.json](../../analysis/s632_mode/mode.json). Verificador: `analysis/s632_mode/verify_mode.py` (A6000 fw3.21, base `0x43541000`; referencias PIC estrictas, barrido `bl` por patrón de halfwords, `analysis/camera_closure/`). Prueba: [test_s632_mode.py](../../tests/test_s632_mode.py).

## Evidencia comprobada (VERIFICADO contra bytes)

Siete cadenas `[IMAGING_CAP]: CamCore Acquire Error!: %02x[MODE_…]` (la ortografía varía: `acquire`, `Acquire`, `Aquire`), 11 cargas `ldr`+`add pc` que resuelven exactamente a ellas, todas dentro de una sola función, `0x437f5a04`:

| Sufijo | Cadena | Cargas | Primera carga | Constante `r1` del `bl 0x43ae82e4` previo |
|---|---|---|---|---|
| `MODE_CAP_DRP` | `0x43cad970` | 1 | `0x437f5c32` | 14 |
| `MODE_CAP_PREREVIEW` | `0x43cad9df` | 2 | `0x437f5cb8` | 15 |
| `MODE_CAP` | `0x43cada50` | 3 | `0x437f5d48` | 17 |
| `MODE_CAP_SNR` | `0x43cadab6` | 2 | `0x437f5f20` | 3 |
| `MODE_SNR_BUS_THROUGH` | `0x43cadb22` | 1 | `0x437f6096` | 12 |
| `MODE_CAP_SNR_PREREVIEW` | `0x43cadb9d` | 1 | `0x437f61d2` | 11 |
| `MODE_SNR_BUS_THROUGH_PREREVIEW` | `0x43cadc15` | 1 | `0x437f627a` | 13 |

## Estructura (instrucciones)

Cada rama de `0x437f5a04` hace lo mismo: carga un identificador inmediato en `r1` (columna anterior), llama a `0x43ae82e4` (la adquisición) y, si devuelve distinto de cero (`cbz r0` salta a la ruta normal cuando es cero), carga la cadena `[MODE_…]` en `r3` y llama a `0x437f5414` con `r0=5`, `r1=1`, `r2=1` y el código devuelto en la pila (`str r0,[sp]`). El sufijo identifica la rama; el único dato que difiere entre ramas es el inmediato de `r1`. Ejemplo `MODE_SNR_BUS_THROUGH`: `movs r1,#0xc` → `bl 0x43ae82e4` (`0x437f6082`) → `cbz` → `movs r0,#5; movs r1,#1; mov r2,r1` → `bl 0x437f5414` (`0x437f6098`).

## `[MODEFLG]`

`[CAM_UTIL_SENS]:                    [MODEFLG]:%x` en `0x43cce251`, cargada desde `0x4390133a` (función `0x439012d0`). Texto sin equivalente en A7S fw3.20 ni A6300 fw2.01 (0 coincidencias del token `[MODEFLG]`).

## Diferencial

Los sufijos `[MODE_` aparecen 8 veces en A6000 fw3.21, 8 en A7S fw3.20 y 12 en A6300 fw2.01 (búsqueda exacta de bytes); los siete diagnósticos existen, por tanto, en los tres modelos. No se comparan cuerpos de función entre modelos.

## Relación con el obturador

Desde `0x437f5a04`, por llamadas `bl` directas hasta profundidad 3, no se alcanza ninguna de las 7 funciones de obturador conocidas (`C3-B`, productor de `r5`, `SetExposure`, `SetRead`, constructor normal, EFCS, BULB). Las llamadas indirectas (vtable/puntero) no se siguen. [S51](s51-decision.md) se mantiene.

## Alcance

Los nombres de modo (`CAP`, `DRP`, `SNR`, `BUS_THROUGH`, `PREREVIEW`) son texto del firmware; este informe no atribuye significado a ninguna sigla ni a los inmediatos de `r1` más allá de su valor.

## Reproducción

```bash
.venv/bin/python analysis/s632_mode/verify_mode.py
.venv/bin/python -m pytest -q tests/test_s632_mode.py
```
