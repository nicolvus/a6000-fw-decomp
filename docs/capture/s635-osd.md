# S635 — `[OSD]`: una cadena de `[VDF]` y su función

**03-11-2026.** Documenta la última etiqueta del censo S178 cuyo único hito era el propio censo: `[OSD]`. No es un módulo: aparece una sola vez, como segunda etiqueta de una traza de `[VDF]`.

Datos: [osd.json](../../analysis/s635_osd/osd.json). Verificador: `analysis/s635_osd/verify_osd.py` (A6000 fw3.21, base `0x43541000`; `analysis/camera_closure/labels.py`). Prueba: [test_s635_osd.py](../../tests/test_s635_osd.py).

## Evidencia comprobada (VERIFICADO contra bytes)

| Cadena | Dirección | Sitios de carga | Función contenedora |
|---|---|---:|---|
| `[VDF][OSD] VDF_EVF_OUT_MODE_ON_LR_THROUGH` | `0x43c8757e` | 1 (`ldr`+`add pc`, regla estricta) | `0x4368e31a` |

- **Referencias a la función** `0x4368e31a`: 0 por `bl`/`b.w` (barrido por patrón de halfwords), literal de 32 bits (con y sin bit Thumb), `ldr`+`add pc` en la misma función y `movw`+`movt`. El inicio de función es el primer `push {…lr}` hacia atrás (≤ 0x2000 B).
- **Ficheros fuente** citados por esa función: ninguno.
- **Modelos** (coincidencias exactas de bytes): `[OSD]` 1 en A6000, 1 en A7S fw3.20 y 0 en A6300 fw2.01; `[VDF][OSD]` 1 / 1 / 0; `VDF_EVF_OUT_MODE` 1 / 1 / 0. Los tres números coinciden porque es la misma cadena.
- **Obturador:** desde `0x4368e31a`, por `bl` directo hasta profundidad 3, no se alcanza ninguna de las 7 funciones de obturador conocidas. Las llamadas indirectas no se siguen. [S51](s51-decision.md) se mantiene.

La etiqueta `[VDF]` y su relación con el visor están en [S500](s500-vdf.md).

## Alcance

El texto (`VDF_EVF_OUT_MODE_ON_LR_THROUGH`) es del firmware; este informe no atribuye significado a `OSD`, `LR` ni al modo, ni afirma qué módulo ejecuta la función. No se ejecutó firmware.

## Reproducción

```bash
.venv/bin/python analysis/s635_osd/verify_osd.py
.venv/bin/python -m pytest -q tests/test_s635_osd.py
```
