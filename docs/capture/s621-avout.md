# S621 — `[AVOUT]`: módulo de salida AV (Audio/Video Output) exclusivo de la A6000 fw3.21

**2 trazas · 2 sitios (regla PIC estricta) · ~1 función emisora · 0 muertas.** Detalle + datos: `analysis/s621_avout/` (pendiente) / `.json` (pendiente).

## Qué es

`[AVOUT]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 2 mensajes del **módulo de salida AV (Audio/Video Output)** dentro del módulo ACCY (Accesorio). La sigla **SÍ tiene base textual**: `AV` → **A**udio **V**ideo; `OUT` → **OUT**put (salida); `AVOUT` → **AV Out** (salida de audio/video, probablemente para HDMI/monitor externo).

## Las 2 trazas (vaddr → texto corto)

```
0x43c254f6 [ACCY][DEBUG][AVOUT] NotifyDetached(%d)
0x43c2551e [ACCY][DEBUG][AVOUT] NotifyAttached(%d)
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[ACCY][DEBUG][AVOUT]` — módulo padre `ACCY` (accesorio) + nivel `DEBUG` + sub-módulo `AVOUT` (salida AV). Longitud total: 21 B (`[ACCY][DEBUG][AVOUT]`).
- **Notificaciones de conexión**: 2 trazas `DEBUG` — `NotifyAttached(%d)` (conectado) y `NotifyDetached(%d)` (desconectado), ambas con parámetro numérico (`%d`, probablemente ID de dispositivo o handle).
- **Logger dual (patrón S177/S179/S603–S620)**: la fw3.21 **duplica** la traza: nueva con prefijo `[ACCY][DEBUG][AVOUT]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo fijo**: 21 B (`[ACCY][DEBUG][AVOUT]`) → fijo (ambas trazas son nivel DEBUG).
- **Estructura ACCY**: en fw3.21 aparece como módulo con sub-módulos `HOUSING` (S610), `SENSER` (S619), y `AVOUT` (S621).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ACCY][DEBUG][AVOUT]` | **2** | **0** | **0** |
| núcleos sin prefijo (`NotifyAttached`, `NotifyDetached`) | 0/2 como literal autónomo | **0** | **0** |
| strings relacionadas A7S (`AccyUmDeviceAvOut`) | 0 | **1** | **1** |
| código equivalente (AVOUT) | `0x43c254f6`… | **parcial** | **parcial** |

→ **Módulo *nuevo* en traza ACCY, código preexistente.** La funcionalidad de salida AV (AVOUT) **existe en los tres firmware** (string `AccyUmDeviceAvOut` en A7S/A6300). Lo propio de la fw3.21 de la A6000 son **las 2 trazas con prefijo `[ACCY][DEBUG][AVOUT]`** y la **duplicación** con logger global `0x43902718`. A7S/A6300 solo tienen la string suelta `17AccyUmDeviceAvOut` sin prefijo ni trazas de notificación.

**Longitud del prefijo fija:** 21 B (`[ACCY][DEBUG][AVOUT]`) → fijo (ambas trazas son nivel DEBUG).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **notificaciones de conexión/desconexión de salida AV (HDMI/monitor externo)**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 2/2 cadenas `[ACCY][DEBUG][AVOUT]` confirmadas en `0x43c254f6`–`0x43c2551e`.
- 0/0 en A7S y A6300 para token `[ACCY][DEBUG][AVOUT]`; 1 string relacionada (`AccyUmDeviceAvOut`) en A7S/A6300 sin prefijo ACCY.
- Scripts: `analysis/s621_avout/` (pendiente) · Tests: `tests/test_s621_avout.py` (pendiente).