# S622 — `[AVR]`: módulo de audio/video rendezvous exclusivo de la A6000 fw3.21

**2 trazas · 2 sitios (regla PIC estricta) · ~1 función emisora · 0 muertas.** Detalle + datos: `analysis/s622_avr/` (pendiente) / `.json` (pendiente).

## Qué es

`[AVR]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 2 mensajes del **módulo AVR (Audio/Video Rendezvous)** dentro del módulo ACCY (Accesorio). La sigla **SÍ tiene base textual**: `AVR` → **A**udio **V**ideo **R**endezvous / **R**esource / **R**ecorder (rendezvous de audio/video para sincronización de streams).

## Las 2 trazas (vaddr → texto corto)

```
0x43c2555a [ACCY][DEBUG][AVR] NotifyDetached(%d)
0x43c25580 [ACCY][DEBUG][AVR] NotifyAttached(%d)
```

## Hallazgos con dirección

- **Triple prefijo jerárquico**: `[ACCY][DEBUG][AVR]` — módulo padre `ACCY` (accesorio) + nivel `DEBUG` + sub-módulo `AVR` (Audio/Video Rendezvous). Longitud total: 19 B (`[ACCY][DEBUG][AVR]`).
- **Notificaciones de conexión**: 2 trazas `DEBUG` — `NotifyAttached(%d)` (conectado) y `NotifyDetached(%d)` (desconectado), ambas con parámetro numérico (`%d`, probablemente ID de dispositivo o handle).
- **Logger dual (patrón S177/S179/S603–S621)**: la fw3.21 **duplica** la traza: nueva con prefijo `[ACCY][DEBUG][AVR]` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Prefijo fijo**: 19 B (`[ACCY][DEBUG][AVR]`) → fijo (ambas trazas son nivel DEBUG).
- **Estructura ACCY**: en fw3.21 aparece como módulo con sub-módulos `HOUSING` (S610), `SENSER` (S619), `AVOUT` (S621), `AVR` (S622).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ACCY][DEBUG][AVR]` | **2** | **0** | **0** |
| núcleos sin prefijo (`NotifyAttached`, `NotifyDetached`) | 0/2 como literal autónomo | **0** | **0** |
| strings relacionadas A7S (`AccyUmDeviceAvr`, `AVRendezvous*`) | 0 | **6+** | **6+** |
| código equivalente (AVRendezvous, etc.) | `0x43c2555a`… | **sí** | **sí** |

→ **Módulo *nuevo* en traza ACCY, código preexistente.** La funcionalidad de rendezvous AV (AVRendezvous, AVRendezvousNotifier, etc.) **existe en los tres firmware** (múltiples strings AVR en A7S/A6300). Lo propio de la fw3.21 de la A6000 son **las 2 trazas con prefijo `[ACCY][DEBUG][AVR]`** y la **duplicación** con logger global `0x43902718`. A7S/A6300 usan strings sueltas sin prefijo ACCY.

**Longitud del prefijo fija:** 19 B (`[ACCY][DEBUG][AVR]`) → fijo (ambas trazas son nivel DEBUG).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **notificaciones de conexión/desconexión de rendezvous AV**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 2/2 cadenas `[ACCY][DEBUG][AVR]` confirmadas en `0x43c2555a`–`0x43c25580`.
- 0/0 en A7S y A6300 para token `[ACCY][DEBUG][AVR]`; 6+ strings AVR relacionadas en A7S/A6300 sin prefijo ACCY.
- Scripts: `analysis/s622_avr/` (pendiente) · Tests: `tests/test_s622_avr.py` (pendiente).