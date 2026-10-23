# S620 — `[STABILIZER]`: submódulo de estabilizador exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**3 trazas · 3 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: [JSON](../../analysis/s620_stabilizer/stabilizer.json).

## Qué es

`[STABILIZER]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 3 mensajes del **submódulo de estabilizador (AS = Anti-Shake / Auto-Stabilization?)** dentro del módulo **CAMERA_IS**. La sigla **SÍ tiene base textual**: `STABILIZER` → **STABILIZER** (estabilizador); `AS` → **A**nti-**S**hake / **A**uto-**S**tabilization / **A**ctive **S**tabilization.

## Las 3 trazas (vaddr → texto corto)

```
0x43c9a1f3 [CAMERA_IS][AS]: [STABILIZER][AS][osal_reg_sync_msg_queue_cb] %x
0x43c9a234 [CAMERA_IS][AS]: [STABILIZER][AS][upm_get_hcrn_ura] %x
0x43c9a26b [CAMERA_IS][AS]: [STABILIZER][AS][osal_unreg_sync_msg_queue_cb] %x
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[CAMERA_IS][AS]: [STABILIZER][AS]` — módulo padre `CAMERA_IS` + sub-módulo `AS` (Auto-Stabilization?) + sub-sub-módulo `STABILIZER`. Longitud total: 33 B (`[CAMERA_IS][AS]: [STABILIZER][AS]`).
- **Operaciones de cola de mensajes OSAL**: 2 trazas — `osal_reg_sync_msg_queue_cb` (registrar callback de cola sincrónica) y `osal_unreg_sync_msg_queue_cb` (desregistrar callback).
- **UPM (Unified Power Management?)**: `upm_get_hcrn_ura` — obtener URA (Unified Resource Allocator?) de HCRN (Hardware Control Resource Node?).
- **Logger dual (patrón S177/S179/S603–S619)**: la fw3.21 **duplica** la traza: nueva con prefijo `[CAMERA_IS][AS]: [STABILIZER][AS]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo cuádruple jerárquico**: `[CAMERA_IS][AS]: [STABILIZER][AS]` — 4 niveles. Longitud total: 33 B.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[STABILIZER]` con prefijo CAMERA_IS | **3** | **0** | **0** |
| núcleos sin prefijo (`osal_reg_sync_msg_queue_cb`, `upm_get_hcrn_ura`, `osal_unreg_sync_msg_queue_cb`) | 0/3 como literal autónomo | **0** | **0** |
| strings estabilizador relacionadas A7S | 0 | **4** (`recInfo.imageStabilizerValid`, `recInfo.imageStabilizer`, `camInfo.imageStabilizerValid`, `camInfo.imageStabilizer`) | **4** (iguales) |
| código equivalente (estabilizador) | `0x43c9a1f3`… | **parcial** | **parcial** |

→ **Submódulo *nuevo* en traza, código preexistente.** El estabilizador **existe en A7S/A6300** (strings `imageStabilizerValid`, `imageStabilizer`) pero **sin el submódulo STABILIZER estructurado ni prefijo `[CAMERA_IS][AS]: [STABILIZER][AS]`**. La fw3.21 de la A6000 **introduce** el submódulo STABILIZER con prefijo cuádruple y **duplica** la traza (nueva con logger de módulo + vieja con logger global `0x43902718`).

**Longitud del prefijo cuádruple fija:** 33 B (`[CAMERA_IS][AS]: [STABILIZER][AS]`) → no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **callbacks OSAL y UPM para estabilizador**, no el obturador per se. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 3/3 cadenas `[CAMERA_IS][AS]: [STABILIZER][AS]` confirmadas en `0x43c9a1f3`–`0x43c9a26b`.
- 0/0 en A7S y A6300 para token `[STABILIZER]` con prefijo CAMERA_IS; 4 strings estabilizador relacionadas en A7S/A6300 sin prefijo estructurado.
- Scripts: `analysis/s620_stabilizer/` (pendiente) · Tests: `tests/test_s620_stabilizer.py`.
