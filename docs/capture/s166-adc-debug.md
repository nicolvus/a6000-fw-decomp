# S166 — `[ADC_DEBUG]`: la capa de depuración del ADC (14 trazas)

> Línea de RE general. Solo bytes de `av-cam.bin` de la **A6000 fw3.21**
> (`vaddr = 0x43541000 + file_offset`), comparado con **A7S fw3.20** y **A6300 fw2.01**.
> Referencias a cadenas: **regla estricta** (canónica del repo).
## Veredicto
`[ADC_DEBUG]` **no es un módulo autónomo**: es la traza que la fw3.21 de la A6000 añadió a
los *handlers* de los comandos de fábrica (`ADJ`) del **driver LIRO del ADC**. Las 14
cadenas las emiten **solo dos funciones**, y esas dos son los handlers de `get_d` y
`get_da` (verificado contra el registro ADJ en `0x440189bc`).

- **14** cadenas (`0x43ce50dd`–`0x43ce5273`); **15** sitios PIC, **15/15 verificados a
  mano**; **2** funciones emisoras: `0x4398eb20` (`get_da`) y `0x4398ec7c` (`get_d`).
  Comandos ADJ del driver: `get_d`, `get_da`, `set_da` (+`exit`).
- Canales ADC: **2 unidades × 12 canales**, u16, array `0x43f84b80`; HW `0xf2406000` (u0) /
  `0xf2407000` (u1), registro por canal `0xf2406014`+`4·ch`.
- Servicio: handle `0x720018`; mensajes `0xfff0` (1 ch) / `0xfff1` (12 ch) / `0xfff2` (set);
  **11** clientes de 282 llamadas al helper genérico `0x43561228`: `[ACCY]`, `[ILLUMI]`,
  panel/EVF (`CNF_ADC_CH_EVF_TEMP`), `[CAMERA_MAIN]` (`liro_adc`), `[CAMERA_MAIN_SYNC]`
  (`ADC::Initialize`, `SendToADCTask`, `int_ADC_Handler`, jitter).
- Contenido: `few arg` (2 sitios) · `ADC DATA0  = %04x` … `ADC DATA11 = %04x` (12) ·
  `ADC DATA = %04x` (1, canal único pedido).

## Relación con `[CAMERA_IS]` (S164): **NO es el mismo servicio**
El giroscopio del IS **no** usa el driver LIRO ADC: en las dos regiones de código del IS
(`0x436e8000`–`0x43708000`, `0x4371d000`–`0x43721000`) hay **0 y 1** llamadas al servicio
y **ninguna** con el handle `0x720018`. El "acceso ADC" del giroscopio (`0x436eace0`) lee
una **tabla de constantes en .rodata** (`0x43bdc0a6`) y aplica las tablas de calibración
`0x43be6336`/`0x43be6518`.
## Diferencial
| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| `[ADC_DEBUG]` | **14** | **0** | **0** |
| `ADJ_CMD_LIRO_DRIVERS_ADC_*` | **6** | **0** | **0** |
| `get_d`/`get_da`/`set_da`, `TSK_ADC` | sí | sí | sí |
| trazas internas del driver | 4 | **0** | **0** |
| `liro_adc`, `CNF_ADC_CH_EVF_TEMP`, `int_ADC_Handler`, `jitter NG` | sí | sí | sí |

**El driver y sus comandos ADJ existen en los tres firmwares** (mismo layout, mismos ids
`0xfff0`/`0xfff1`/`0xfff2`); los handlers de la A7S (`0x4397c860`/`0x4397c89c`) y del
A6300 (`0x43a23480`/`0x43a234bc`) son **idénticos pero no imprimen**: lo nuevo de la
fw3.21 de la A6000 es la **capa de traza**, no el ADC.
## Línea del obturador
- Las 14 trazas: **0** menciones de `shut`/`silent`/`electro`/`rolling`/`readout`/`exposure`
  → **sin efecto en S51 (A/B/C = NO)**.
- Fuera de `[ADC_DEBUG]`, el ADC **sí** participa en la línea temporal: `HS_Main`
  (`0x4378fef4`) llama a `SendToADCTask` (`0x43790866`) y espera la bandera
  (`HS_Main:(TC::Last1st) ADC flg timeout %dV #%d, %04x` `0x43ca30fd`), e
  `int_ADC_Handler` (`0x4378d444`) mide **jitter** (`jitter NG …` `0x43ca241e`, umbral
  `cmp.w r8,#0x320` en `0x4378d4b4`).
- **Ningún canal del ADC LIRO está ligado a la decisión mecánico/electrónico**: el A6300
  fw2.01, que **sí** tiene `ElecShutter/` (S135), tiene el **mismo** ADC y no añade
  ningún canal de obturador.
## NO VERIFICADO / abierto
Sin fichero fuente ni clase RTTI embebidos para el driver; qué sensor hay detrás de cada
canal (la numeración llega en runtime desde parámetros `0x43561508`; sólo se conoce el
nombre `CNF_ADC_CH_EVF_TEMP`); cómo se registra `int_ADC_Handler` (`0x4378d444`, 0
llamadas `bl` y 0 punteros absolutos); alcance real de los comandos ADJ en runtime.
[Informe](../../analysis/s166_adc_debug/adc_debug.md) · JSON `analysis/s166_adc_debug/adc_debug.json`
· tests `tests/test_s166_adc_debug.py`.
