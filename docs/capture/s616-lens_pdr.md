# S616 — `[LENS_PDR]`: módulo de comunicación PDR de lente exclusivo de la A6000 fw3.21

**4 trazas · 4 sitios (regla PIC estricta) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: `analysis/s616_lens_pdr/` (pendiente) / `.json` (pendiente).

## Qué es

`[LENS_PDR]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 4 mensajes del **módulo PDR (Power Data Receiver / Protocol Data Receiver?) de comunicación con lente** que gestiona el envío y recepción de datos a través del DSP "Bonobo" (probablemente un DSP propietario de Sony para comunicación de lente). La sigla **SÍ tiene base textual**: `LENS` → lente/objetivo; `PDR` → **P**ower **D**ata **R**eceiver / **P**rotocol **D**ata **R**eceiver / **P**hase **D**etection **R**eceiver (NO VERIF.); `BonoboDSP` → nombre interno del DSP de comunicación de lente (nombre en clave "Bonobo").

## Las 4 trazas (vaddr → texto corto)

```
0x43c9a822 [LENS_PDR]: BonoboDSP_Send: Data latch failed!
0x43c9a852 [LENS_PDR]: BonoboDSP_Send:[ch0]Data latch failed!
0x43c9a886 [LENS_PDR]: BonoboDSP_Send:[ch1]Data latch failed!
0x43c9a8ba [LENS_PDR]: BonoboDSP_Rcv: paritycheck_error!
```

## Hallazgos con dirección

- **DSP "Bonobo"**: nombre interno del DSP de comunicación de lente (nombre en clave "Bonobo" = bonobo/chimpancé, siguiendo nomenclatura de primates para DSPs de Sony).
- **Envío (Send)**: 3 trazas de error de "Data latch failed!" — fallo en el latch (retenedor) de datos al enviar:
  - Genérico: `BonoboDSP_Send: Data latch failed!`
  - Canal 0: `BonoboDSP_Send:[ch0]Data latch failed!`
  - Canal 1: `BonoboDSP_Send:[ch1]Data latch failed!`
- **Recepción (Rcv)**: 1 traza de error de paridad — `BonoboDSP_Rcv: paritycheck_error!` — error de checksum/paridad en recepción.
- **Logger dual (patrón S177/S179/S603–S615)**: la fw3.21 **duplica** la traza: nueva con prefijo `[LENS_PDR]: ` (logger de módulo) + vieja sin prefijo vía logger global `0x43902718`.
- **Longitud del prefijo**: 11 B (`[LENS_PDR]: `) → fija.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[LENS_PDR]` | **4** | **0** | **0** |
| núcleo sin prefijo (`BonoboDSP_Send/Rcv`, `Data latch failed`, `paritycheck_error`) | 0/4 como literal autónomo | **4/4** (idénticos) | **4/4** (idénticos) |
| prefijo alternativo A7S/A6300 | 0 | **ninguno** (strings sueltas) | **ninguno** (strings sueltas) |
| código equivalente (BonoboDSP) | `0x43c9a822`… | **sí** | **sí** |

→ **Cambio de *logging*, no de código.** El DSP "Bonobo" de comunicación de lente **existe igual** en los tres firmware (mismas 4 cadenas núcleo, mismas funciones `BonoboDSP_Send/Rcv`, mismos errores `Data latch failed` y `paritycheck_error`). Lo propio de la fw3.21 de la A6000 son **las 4 trazas con prefijo `[LENS_PDR]: `**. La fw3.21 **duplica** la traza (nueva con logger de módulo + vieja intacta con logger global `0x43902718`).

**Longitud del prefijo fija:** 11 B (`[LENS_PDR]: `) → fija, no variable.

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **comunicación DSP de lente (envío/recepción y errores de latch/paridad)**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 4/4 cadenas `[LENS_PDR]: ` confirmadas en `0x43c9a822`–`0x43c9a8ba`.
- 4/4 núcleos idénticos en A7S fw3.20 y A6300 fw2.01 (sin prefijo).
- 0/0 en A7S y A6300 para token `[LENS_PDR]`.
- Scripts: `analysis/s616_lens_pdr/` (pendiente) · Tests: `tests/test_s616_lens_pdr.py` (pendiente).