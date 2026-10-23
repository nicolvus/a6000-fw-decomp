# S627 — `[EO_SW]`: módulo de switch EO (End-of-Switch?) exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**1 traza · 1 sitio (regla PIC estricta) · ~1 función emisora · 0 muertas.** Detalle + datos: [JSON](../../analysis/s627_eo_sw/eo_sw.json).

## Qué es

`[EO_SW]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 1 mensaje del **módulo de switch EO (End-of-Switch / Electronic Optical Switch?)**. La sigla **SÍ tiene base textual**: `EO` → **E**nd-**O**f / **E**lectro-**O**ptical / **E**xternal **O**ptical; `SW` → **SW**itch (interruptor). `EO_SW` → probable **End-Of-Switch** / **Electro-Optical Switch** (interruptor electro-óptico).

## La traza (vaddr → texto corto)

```
0x43c37b40 [EO_SW] Port=%d, Bit=%d, Data=%d
```

## Hallazgos con dirección

- **Triple prefijo**: `[EO_SW]` — módulo switch EO. Longitud: 7 B (`[EO_SW]`).
- **Parámetros de puerto**: `Port=%d, Bit=%d, Data=%d` — puerto, bit y dato (probablemente estado del switch: on/off, posición, etc.).
- **Logger dual (patrón S177/S179/S603–S626)**: la fw3.21 **duplica** la traza: nueva con prefijo `[EO_SW]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo fijo**: 7 B (`[EO_SW]`) → fijo.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[EO_SW]` | **1** | **0** | **0** |
| núcleo sin prefijo (`Port=%d, Bit=%d, Data=%d`) | 0/1 como literal autónomo | **0** | **0** |
| strings relacionadas switch/port/bit | 0 | **pocas** | **pocas** |
| código equivalente (switch port/bit) | `0x43c37b40`… | **parcial** | **parcial** |

→ **Módulo *nuevo* en traza, código preexistente.** El manejo de switches puerto/bit **existe en los tres firmware** (funcionalidad de GPIO/puerto) pero **sin el módulo EO_SW estructurado ni prefijo `[EO_SW]`**. La fw3.21 de la A6000 **introduce** el módulo EO_SW con logging formateado y **duplica** la traza (nueva con logger de módulo + vieja con logger global `0x43902718`).

**Longitud del prefijo fija:** 7 B (`[EO_SW]`) → fijo.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **lectura de estado de switch/puerto (GPIO)**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 1/1 cadena `[EO_SW]` confirmada en `0x43c37b40`.
- 0/0 en A7S y A6300 para token `[EO_SW]`; strings relacionadas switch/port/bit en A7S/A6300 sin prefijo estructurado.
- Scripts: `analysis/s627_eo_sw/` (pendiente) · Tests: `tests/test_s627_eo_sw.py`.
