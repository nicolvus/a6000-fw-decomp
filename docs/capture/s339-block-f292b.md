# S339 — Qué se puede afirmar de `0xf292b000..8` (carril B)

22-10-2026. Carril B. Sesión S339. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S335 midió que las máscaras escriben `0xf292b004`/`0xf292b008` y leen `0xf292b000`, pero no identificó el bloque. ¿Qué se puede afirmar por bytes?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| Solo hay **6 literales** de `0xf292b000/4/8` en el A7S (1/2/3) y **todos** están en los accesores `0x436f8290..0x436f82d0` | **VERIFICADO** | Barrido de literales; ningún otro código toca el bloque directamente |
| La interfaz es de **3 registros** (`+0`, `+4`, `+8`) con campos de **12 bits** y valores de control `0x1000`/`0x10000` | **VERIFICADO** | `lsls #0x14 / lsrs #0x14`, `mov.w r2,#0x1000`, `mov.w r3,#0x10000` |
| La A6000 repite la interfaz con los mismos literales y el mismo número de sitios | **VERIFICADO** | 1/2/3 en ambos |
| El bloque está en la ventana `0xf292x000` (bloques cada 4 KB); los vecinos documentados son GPIO `0xf2910000` (S54/S55) y DSP de lente `0xf292d000` (S66) | **VERIFICADO** | Recuento de literales por bloque de 4 KB |
| `0xf292b000` **no** aparece en la documentación del repo | **VERIFICADO** | `grep` en `docs/` y `analysis/` |
| **Identidad/función** del bloque | **NO_VERIFICADO** | Sin datasheet, sin símbolos, sin cadena asociada |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. Uso del bloque

| Registro | Accesor | Operación |
|---|---|---|
| `0xf292b000` | `0x436f82b0` | lectura (12 bits) |
| `0xf292b004` | `0x436f82a0` | escritura (12 bits) |
| `0xf292b008` | `0x436f8290`, `0x436f82c0`, `0x436f82d0` | escritura (12 bits), `0x1000`, `0x10000` |

Los seis literales caen dentro de `0x436f8290..0x436f82e4`; ningún otro sitio del blob los referencia.

## 2. Ventana `0xf292x000` (A7S)

| Bloque | Literales | Nota |
|---|---:|---|
| `0xf2922000` | 1 | — |
| `0xf2924000` | 7 | — |
| `0xf2929000` | 3 | — |
| `0xf292a000` | 5 | — |
| **`0xf292b000`** | **6** | este bloque |
| `0xf292c000` | 1 | — |
| `0xf292d000` | 1 | DSP de lente (S66) |
| `0xf292f000` | 14 | — |

La A6000 usa los mismos bloques salvo `0xf2922000`/`0xf2927000` (uno cada uno) y `0xf292c000` (no aparece).

## Límites

- Sin runtime, sin cámara, sin flasheo.
- El bloque no aparece en la documentación del repo ni en ningún símbolo; **no** se afirma que sea sensor, P2S, ADC ni GPIO.
- Los vecinos `0xf2910000` (GPIO) y `0xf292d000` (DSP de lente) están documentados, pero no implican la función de `0xf292b000`.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s339_block_f292b/build_block_f292b.py
.venv/bin/python analysis/s339_block_f292b/verify_block_f292b.py  # 29 comprobaciones
.venv/bin/python -m unittest tests.test_s339_block_f292b           # 7 tests
```

Artefactos: `analysis/s339_block_f292b/block_f292b.json`, `build_block_f292b.py`, `verify_block_f292b.py`, `tests/test_s339_block_f292b.py`.
