# S636 — `[D0]`–`[D7]`: campos de dos trazas de `[CAM_UTIL_ADJ]`

**03-11-2026.** Documenta los ocho fragmentos del censo S178 que seguían descartados como «no módulo» (`[D0]`…`[D7]`). Son nombres de campo dentro de dos trazas de `[CAM_UTIL_ADJ]` ([S143](s143-cam-util-adj.md)); pasan a sub-etiquetas de `[CAM_UTIL_ADJ]`, igual que los `[MODE_CAP*]` de [S632](s632-mode.md) y los `[STK_*]` de [S633](s633-stk-sim.md).

Datos: [dfields.json](../../analysis/s636_dfields/dfields.json). Verificador: `analysis/s636_dfields/verify_dfields.py` (A6000 fw3.21, base `0x43541000`; `analysis/camera_closure/`). Prueba: [test_s636_dfields.py](../../tests/test_s636_dfields.py).

## Evidencia comprobada (VERIFICADO contra bytes)

| Cadena | Dirección | Campos | Sitio de carga | Función |
|---|---|---|---|---|
| `[CAM_UTIL_ADJ]:   : [D0]:%04x, [D1]:%04x,[D2]:%04x, [D3]:%04x` | `0x43ccde70` | `[D0]`–`[D3]` | `0x43900abc` | `0x43900a24` |
| `[CAM_UTIL_ADJ]:   : [D4]:%04x, [D5]:%04x,[D6]:%04x, [D7]:%04x` | `0x43ccdeae` | `[D4]`–`[D7]` | `0x43900ae2` | `0x43900a24` |

- Cada traza imprime cuatro valores de 16 bits (`%04x`) etiquetados con su índice; las dos están en la misma función.
- La función `0x43900a24` no tiene `bl` directo ni `movw`+`movt`; aparece como puntero literal de 32 bits en `0x4401f7a4`.
- **Modelos:** cada token `[Dn]:%04x` tiene 1 coincidencia en A6000 fw3.21 y 0 en A7S fw3.20 y en A6300 fw2.01.
- **Obturador:** desde `0x43900a24`, por `bl` directo hasta profundidad 3, no se alcanza ninguna de las 7 funciones de obturador conocidas. Las llamadas indirectas no se siguen. [S51](s51-decision.md) se mantiene.

## Alcance

El significado de los ocho valores (qué registro o tabla de ajuste se vuelca) no se afirma. No se ejecutó firmware.

## Reproducción

```bash
.venv/bin/python analysis/s636_dfields/verify_dfields.py
.venv/bin/python -m pytest -q tests/test_s636_dfields.py
```
