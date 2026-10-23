# S608 — `[MOUNT_INFO]`: módulo de traza de montura/bootloader exclusivo de la A6000 fw3.21

**6 trazas · 6 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: `analysis/s608_mount_info/` (pendiente) / `.json` (pendiente).

## Qué es

`[MOUNT_INFO]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 6 mensajes del **subsistema de comunicación montura/bootloader (BL = BootLoader / Mount Link)** que gestiona comandos LIF (Lens Interface), callbacks UUD (Universal Update Device), y mensajes de versión/firmware/prepare update/unplug USB. La sigla **SÍ tiene base textual**: `MOUNT` → montura del objetivo; `INFO` → información; `BL` → **B**oot**L**oader / **B**us **L**ink; `LIF` → **L**ens **I**nter**F**ace; `UUD` → **U**niversal **U**pdate **D**evice.

## Las 6 trazas (vaddr → texto corto)

```
0x43c9711f [MOUNT_INFO]: [BL]LIF Command Change : 0x%X >>> 0x%X
0x43c98259 [MOUNT_INFO]: [BL]UUD CallBack : MSGID_GET_VERSION
0x43c9828c [MOUNT_INFO]: [BL]UUD CallBack : MSGID_GET_FORCE_FIRMUP
0x43c982c4 [MOUNT_INFO]: [BL]UUD CallBack : MSGID_FIRM_UP_REQ
0x43c982f7 [MOUNT_INFO]: [BL]UUD CallBack : MSGID_PREPARE_UPDATE
0x43c9832d [MOUNT_INFO]: [BL]UUD CallBack : MSGID_UNPLUG_USB
```

## Hallazgos con dirección

- **Doble prefijo**: cada traza tiene **dos prefijos** — `[MOUNT_INFO]: ` (nuevo, fw3.21) + `[BL] ` (original, preexistente) — patrón único en la serie (S177/S179/S603–S607 usan prefijo simple o logger dual).
- **LIF Command Change**: notificación de cambio de comando LIF (lente) con códigos hex antes/después.
- **UUD CallBacks**: 5 callbacks del Universal Update Device:
  - `MSGID_GET_VERSION` — solicitud de versión
  - `MSGID_GET_FORCE_FIRMUP` — solicitud de firmware forzado
  - `MSGID_FIRM_UP_REQ` — petición de actualización de firmware
  - `MSGID_PREPARE_UPDATE` — preparación de actualización
  - `MSGID_UNPLUG_USB` — desconexión USB
- **Logger dual (patrón S177/S179/S603–S607)**: la fw3.21 **duplica** la traza: nueva con prefijo `[MOUNT_INFO]: ` (logger de módulo) + vieja con prefijo `[BL] ` vía logger global `0x43902718` (idéntico a S177/S179/S603–S607). El string original en A7S/A6300 ya tiene `[BL] `.
- **Longitud del prefijo**: 12 B (`[MOUNT_INFO]: `) + 4 B (`[BL] `) = 16 B totales → el prefijo compuesto más largo de la serie.
- **Estructura BL**: el subsistema `[BL]` en A7S/A6300 tiene 70+ trazas (errores de firmware update, sync, async, VSYNC, mount error, lens error, power seq, etc.). La fw3.21 **añade capa `[MOUNT_INFO]: `** a 6 strings específicas de LIF/UUD.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[MOUNT_INFO]` | **6** | **0** | **0** |
| token `[BL]` (mismo núcleo) | **6** (doble prefijo) | **70+** | **70+** |
| núcleo `[BL]LIF Command Change...` / `[BL]UUD CallBack...` | 6/6 con doble prefijo | **0/6** (strings distintos) | **0/6** (strings distintos) |
| código equivalente (BL/LIF/UUD) | `0x43c97xxx`… | **sí, otro conjunto** | **sí, otro conjunto** |

→ **Capa de logging *nueva* sobre subsistema preexistente.** El subsistema BL/LIF/UUD **existe en los tres firmware** (comunicación montura/bootloader, firmware update, lentes), pero la fw3.21 de la A6000 **añade una nueva etiqueta `[MOUNT_INFO]: `** a 6 strings específicas de LIF/UUD y **duplica** la traza (nueva con logger de módulo + vieja con logger global `[BL] ` + `0x43902718`). Los strings `[BL]LIF...` y `[BL]UUD...` **no existen en A7S/A6300** (el BL allí tiene otros 70+ mensajes distintos).

**Longitud del prefijo compuesto:** 16 B (`[MOUNT_INFO]: [BL] `) → fijo, no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **comunicación montura/bootloader y firmware update de lente**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 6/6 cadenas `[MOUNT_INFO]: [BL]...` confirmadas en `0x43c9711f`–`0x43c9832d`.
- 0/0 en A7S y A6300 para token `[MOUNT_INFO]`; 70+ `[BL]` en A7S/A6300 (strings distintos).
- Scripts: `analysis/s608_mount_info/` (pendiente) · Tests: `tests/test_s608_mount_info.py` (pendiente).