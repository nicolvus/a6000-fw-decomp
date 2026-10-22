# S173 — `[CAM_UTIL]` (10) y `[CAMERA_ADJ]` (3): las utilidades compartidas

> Hito de la **línea de RE general**. Solo bytes de la A6000 fw3.21, con la A7S fw3.20 y el
> A6300 fw2.01 como comparación.

## Veredicto

`[CAM_UTIL]` y `[CAMERA_ADJ]` **no son un módulo propio**: son el rótulo de **utilidades
compartidas** por la familia `CAM_UTIL` (los módulos `[CAM_UTIL_ADJ]` de S143 y
`[CAM_UTIL_SENS]` de S144) y por el gestor de memoria **DMM** de `[CAMERA_MAIN]`.

| etiqueta | cadenas | A6000 | A7S | A6300 | sitios PIC | funciones |
|---|---|---|---|---|---|---|
| `[CAM_UTIL]` | 10 | 10 | **0** | **0** | 13 | 10 |
| `[CAMERA_ADJ]` | 3 | 3 | **0** | **0** | 3 | 3 |

Las **13 cadenas están vivas** (0 muertas) y sus **16 sitios** caen en **13 funciones**: 5 en la
zona **DMM** (`0x437e3c92`–`0x437e446e`) y 8 en la zona **`CAM_UTIL`** (`0x43900234`–`0x43904092`),
en funciones que **S143 y S144 no habían cubierto** porque emitían con otra etiqueta.

**Coherencia**: la inicialización (`0x4390178e`) escribe el **id de módulo `0xb5`** — exactamente
el **módulo `0xb5`** que S144 identificó como compartido por `[CAM_UTIL_ADJ]` y `[CAM_UTIL_SENS]`.

## Contenido

* **DMM** (5 sitios): `MemPool Free Err`, `Dmm Open Err hdl`, `Dmm Close Err hdl`.
* **AV DDS** (2): fallo al asignar y al enviar un mensaje OSAL.
* **`[CAMERA_ADJ]`** (3): `Utility Adjust Ctrl`, `Utility MS Mount Start` y
  `Utility MS UnMount Start` — fallos de reserva OSAL.
* **EvtDrvnTsk** (3): errores y registro de tareas del **driver de eventos**.
* **`osal_try_valloc_msg`** (2): contador de fallos al pedir un mensaje (con reintento: si el
  bit 0 del byte de estado `[r6,#0xfc]` está activo, traza y limpia el bit).

## Para la línea del obturador

**Negativo verificado**: 0 menciones de obturador, disparo, sensor, exposición o tiempos de
exposición → **sin efecto en S51** (A/B/C = NO).

Informe: [analysis/s173_cam_util_labels/cam_util_labels.md](../analysis/s173_cam_util_labels/cam_util_labels.md) ·
test: `tests/test_s173_cam_util_labels.py` (21 tests).
