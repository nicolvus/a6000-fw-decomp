# S610 — `[ACCY][INFO][HOUSING]`: módulo de carcasa/accesorio acuático exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**5 trazas · 5 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: [JSON](../../analysis/s610_housing/housing.json).

## Qué es

`[ACCY][INFO][HOUSING]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 5 mensajes del **gestor de carcasa acuática / accesorio de buceo (Water Housing)** dentro del módulo **ACCY** (Accesorio). La sigla **SÍ tiene base textual**: `ACCY` → **ACC**essor**Y** (accesorio); `INFO` → nivel informativo; `HOUSING` → **carcasa** / **caja estanca** / **water housing** (accesorio para fotografía subacuática).

## Las 5 trazas (vaddr → texto corto)

```
0x43c25380 [ACCY][INFO][HOUSING]:%d:NotifyAttached
0x43c253a8 [ACCY][INFO][HOUSING]:%d:NotifyContinuousAttached
0x43c253da [ACCY][INFO][HOUSING]:%d:RestoreInfo...Savedata:%02X %02X
0x43c25414 [ACCY][INFO][HOUSING]:%d:NotifyDetached
0x43c2543c [ACCY][INFO][HOUSING]:%d:NotifyUartTimedOut... %d
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[ACCY][INFO][HOUSING]:` — módulo padre `ACCY` (accesorio) + nivel `INFO` + sub-módulo `HOUSING` (carcasa acuática). Longitud total: 22 B (`[ACCY][INFO][HOUSING]:`) → el prefijo más largo de la serie.
- **Ciclo de vida del accesorio**: 4 notificaciones de estado — `Attached` (conectado), `ContinuousAttached` (conectado continuo), `Detached` (desconectado), `UartTimedOut` (timeout UART).
- **Restauración de datos**: `RestoreInfo...Savedata:%02X %02X` — recuperación de datos guardados (2 bytes) al reconectar.
- **Timeout UART**: `NotifyUartTimedOut... %d` — detección de timeout en comunicación serie con la carcasa.
- **Logger dual (patrón S177/S179/S603–S609)**: la fw3.21 **duplica** la traza: nueva con prefijo `[ACCY][INFO][HOUSING]: ` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Módulo ACCY**: en fw3.21 aparece por primera vez como módulo estructurado con sub-módulo `HOUSING` (y posiblemente otros). En A7S solo existe `24AccyUmDeviceWaterHousing` (string suelta sin prefijo).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ACCY][INFO][HOUSING]` | **5** | **0** | **0** |
| token `[ACCY]` (padre) | **5** | **0** | **0** |
| núcleo sin prefijo (`NotifyAttached`, `NotifyDetached`, `RestoreInfo`, `NotifyUartTimedOut`) | 0/5 como literal autónomo | **0** | **0** |
| string relacionada `WaterHousing` | 0 | **1** (`24AccyUmDeviceWaterHousing`) | **0** |
| código equivalente (HOUSING/UART) | `0x43c25380`… | **parcial** | **parcial** |

→ **Módulo *nuevo* en traza y código.** El gestor de carcasa acuática **no existe en A7S/A6300** (ni en traza ni con esas funciones `NotifyAttached/Detached/ContinuousAttached/RestoreInfo/UartTimedOut`). A7S solo tiene una string suelta `24AccyUmDeviceWaterHousing` sin prefijo ni estructura. La fw3.21 de la A6000 **introduce** el módulo ACCY con sub-módulo HOUSING completo.

**Longitud del prefijo jerárquico fija:** 22 B (`[ACCY][INFO][HOUSING]:`) → no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **detección y comunicación con carcasa acuática (accesorio)**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 5/5 cadenas `[ACCY][INFO][HOUSING]: ` confirmadas en `0x43c25380`–`0x43c2543c`.
- 0/0 en A7S y A6300 para token `[ACCY][INFO][HOUSING]` y `[ACCY]`.
- Scripts: `analysis/s610_housing/` (pendiente) · Tests: `tests/test_s610_housing.py`.
