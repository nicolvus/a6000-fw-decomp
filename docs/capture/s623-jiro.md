# S623 — `[JIRO]`: módulo de audio (JIRO) exclusivo de la A6000 fw3.21

**2 trazas · 2 sitios (regla PIC estricta) · ~1 función emisora · 0 muertas.** Detalle + datos: `analysis/s623_jiro/` (pendiente) / `.json` (pendiente).

## Qué es

`[JIRO]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 2 mensajes del **módulo JIRO (probablemente controlador de audio/codec)** dentro del módulo ACCY (Accesorio). La sigla **SÍ tiene base textual**: `JIRO` → nombre en clave interno / **J**apanese **I**nternal **R**ecorder **O**rganizer / **J**oint **I**nternal **R**egister **O**peration (NO VERIF.). `ACCY` → **ACC**essor**Y** (accesorio).

## Las 2 trazas (vaddr → texto corto)

```
0x43c25b04 [ACCY][DEBUG][JIRO] NotifyDetached(%d)
0x43c25b2b [ACCY][DEBUG][JIRO] NotifyAttached(%d)
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[ACCY][DEBUG][JIRO]` — módulo padre `ACCY` (accesorio) + nivel `DEBUG` + sub-módulo `JIRO`. Longitud total: 20 B (`[ACCY][DEBUG][JIRO]`).
- **Notificaciones de conexión**: 2 trazas `DEBUG` — `NotifyAttached(%d)` (conectado) y `NotifyDetached(%d)` (desconectado), ambas con parámetro numérico (`%d`, probablemente ID de dispositivo o handle).
- **Logger dual (patrón S177/S179/S603–S622)**: la fw3.21 **duplica** la traza: nueva con prefijo `[ACCY][DEBUG][JIRO]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo fijo**: 20 B (`[ACCY][DEBUG][JIRO]`) → fijo (ambas trazas son nivel DEBUG).
- **Estructura ACCY**: en fw3.21 aparece como módulo con sub-módulos `HOUSING` (S610), `SENSER` (S619), `AVOUT` (S621), `AVR` (S622), `JIRO` (S623).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ACCY][DEBUG][JIRO]` | **2** | **0** | **0** |
| núcleos sin prefijo (`NotifyAttached`, `NotifyDetached`) | 0/2 como literal autónomo | **0** | **0** |
| strings relacionadas A7S (`AccyUmDeviceJiro`) | 0 | **1** | **1** |
| código equivalente (JIRO) | `0x43c25b04`… | **parcial** | **parcial** |

→ **Módulo *nuevo* en traza ACCY, código preexistente.** La funcionalidad JIRO **existe en los tres firmware** (string `16AccyUmDeviceJiro` en A7S/A6300). Lo propio de la fw3.21 de la A6000 son **las 2 trazas con prefijo `[ACCY][DEBUG][JIRO]`** y la **duplicación** con logger global `0x43902718`. A7S/A6300 solo tienen la string suelta `16AccyUmDeviceJiro` sin prefijo ni trazas de notificación.

**Longitud del prefijo fija:** 20 B (`[ACCY][DEBUG][JIRO]`) → fijo (ambas trazas son nivel DEBUG).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **notificaciones de conexión/desconexión de dispositivo JIRO (audio/codec?)**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 2/2 cadenas `[ACCY][DEBUG][JIRO]` confirmadas en `0x43c25b04`–`0x43c25b2b`.
- 0/0 en A7S y A6300 para token `[ACCY][DEBUG][JIRO]`; 1 string relacionada (`16AccyUmDeviceJiro`) en A7S/A6300 sin prefijo ACCY.
- Scripts: `analysis/s623_jiro/` (pendiente) · Tests: `tests/test_s623_jiro.py` (pendiente).