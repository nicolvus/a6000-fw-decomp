# S613 — `[MOUNT_WARNING]`: módulo de advertencias de montura exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**5 trazas · 5 sitios (regla PIC estricta) · ~3 funciones emisoras · 0 muertas.** Detalle + datos: [JSON](../../analysis/s613_mount_warning/mount_warning.json).

## Qué es

`[MOUNT_WARNING]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 5 mensajes de **advertencia del subsistema de montura** que cubren: miembros faltantes en AM (Automatic Mount?) y DRV (Driver), comandos ilegales LIF (Lens Interface), y cambios de comando de cámara. La sigla **SÍ tiene base textual**: `MOUNT` → montura del objetivo; `WARNING` → nivel de advertencia; `AM` → **A**utomatic **M**ount / **A**ttachment **M**anager; `DRV` → **DR**i**V**er; `BL` → **B**oot**L**oader / **B**us **L**ink; `LIF` → **L**ens **I**nter**F**ace.

## Las 5 trazas (vaddr → texto corto)

```
0x43c95691 [MOUNT_WARNING]: [MOUNT AM]NO MEMBER CHECK_DATA:%d
0x43c956c4 [MOUNT_WARNING]: [MOUNT AM]NO MEMBER ERR_INFO:%d
0x43c970fc [MOUNT_WARNING]: [BL]LIF Command : Illegal Command Received!!! : cmd=%04X
0x43c97858 [MOUNT_WARNING]: [MOUNT DRV]NO MEMBER PWR_MODE:%d
0x43c98714 [MOUNT_WARNING]: [BL]cam_cmd change!! reason=%03x now=%03x (0xC05:PB 0xC06:POFF)
```

## Hallazgos con dirección

- **Prefijos heterogéneos**: 3 sub-prefijos distintos — `[MOUNT AM]` (2 trazas), `[BL]` (2 trazas), `[MOUNT DRV]` (1 traza) — todos bajo el prefijo común `[MOUNT_WARNING]: `.
- **AM (Automatic Mount/Attachment Manager)**: 2 trazas de "NO MEMBER" — `CHECK_DATA` (validación de datos) y `ERR_INFO` (información de error).
- **BL (BootLoader/Bus Link)**: 2 trazas — comando LIF ilegal (`Illegal Command Received!!! : cmd=%04X`) y cambio de comando de cámara (`cam_cmd change!! reason=%03x now=%03x (0xC05:PB 0xC06:POFF)` donde PB=Power Button?, POFF=Power Off?).
- **DRV (Driver)**: 1 traza — `NO MEMBER PWR_MODE` (modo de potencia faltante).
- **Logger dual (patrón S177/S179/S603–S612)**: la fw3.21 **afirma duplicar** la traza (NO_VERIFICADO - requiere xrefs/REA): nueva con prefijo `[MOUNT_WARNING]: ` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Nivel WARNING**: todas las trazas son de nivel advertencia (no error crítico).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[MOUNT_WARNING]` | **5** | **0** | **0** |
| núcleos sin prefijo (`NO MEMBER CHECK_DATA`, `Illegal Command`, `cam_cmd change`, `NO MEMBER PWR_MODE`) | 0/5 como literal autónomo | **0** | **0** |
| strings relacionadas montura A7S | 0 | **70+** (`[BL]MOUNT_*`, `Mount: `, etc.) | **70+** |
| código equivalente (NO_VERIFICADO - requiere comparación de instrucciones) (AM/DRV/BL/LIF) | `0x43c95691`… | **parcial (BL mount/LIF)** | **parcial (BL mount/LIF)** |

→ **Módulo *nuevo* en traza y código.** El gestor de advertencias de montura **no existe en A7S/A6300** (ni en traza ni con esas funciones `NO MEMBER CHECK_DATA/ERR_INFO/PWR_MODE`, `Illegal Command`, `cam_cmd change`). A7S/A6300 tienen un subsistema de montura BL (`[BL]MOUNT_*`, `Mount: `) pero **sin módulo WARNING estructurado ni sub-módulos AM/DRV**. La fw3.21 de la A6000 **introduce** el módulo MOUNT_WARNING con sub-módulos AM, DRV y BL/LIF.

**Longitud del prefijo fija:** 17 B (`[MOUNT_WARNING]: `) → no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **advertencias de comunicación y estado de montura**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 5/5 cadenas `[MOUNT_WARNING]: ` confirmadas en `0x43c95691`–`0x43c98714`.
- 0/0 en A7S y A6300 para token `[MOUNT_WARNING]`.
- Scripts: `analysis/s613_mount_warning/` (pendiente) · Tests: `tests/test_s613_mount_warning.py`.
