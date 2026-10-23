# S175 — el módulo `[LIF_DEBUG]` (13 trazas): el sensor de luz de la cámara

> Hito de la **línea de RE general**. Solo bytes de la A6000 fw3.21, con la A7S fw3.20 y el
> A6300 fw2.01 como comparación.

## Veredicto

`[LIF_DEBUG]` es la traza de diagnóstico del **subsistema de sensor de luz de la cámara**
(`CAM LIF SENSER`): su inicialización, el registro/desregistro de los *callbacks* de **backup**
(`BK`, con identificador `BKID`) y las **copias «shadow»** entre el estado de *backup* y el
«shadow». Es el **último** de los 17 módulos «de contenido nuevo» que S130 identificó.

| etiqueta | cadenas | A6000 | A7S | A6300 | sitios PIC | funciones |
|---|---|---|---|---|---|---|
| `[LIF_DEBUG]` | 13 | 13 | **0** | **0** | 14 | 3 |

Las **13 cadenas están vivas** (0 muertas) en **3 funciones contiguas** (`0x43a1c9d8`,
`0x43a1cb0c`, `0x43a1cb3c`) y usan un **logger propio con id `0x125`** (`0x43a1c92c`): mensaje
OSAL de `0x9a` B, `vsnprintf` (`0x439c5a04`) y `osal_send_msg` (`0x43561244`).

**Los dos nombres de función aparecen SOLO dentro de las trazas**
(`cam_lif_senser_copy_bk2shadow` `0x43cfb14d`, `cam_lif_senser_copy_shadow2bk` `0x43cfb18a`): hay
**0** apariciones como símbolo independiente → son **texto literal**, no símbolos del enlazador.

## Contenido

* **Copia de seguridad bidireccional** entre el estado «shadow» y el «BK»: cada copia recorre
  **2** elementos (`cmp r7,#2` en `0x43a1caa2`, `cmp r4,#2` en `0x43a1cb9c`).
* Registro/desregistro de *callbacks* con resultado (`[BKID]`, `[Erro]`, `[HandleValue]`,
  `[HandlerValue]`, `[Count]`, `[DataSize]`).

## Diferencial

`[LIF_DEBUG]` **13/0/0**, pero el **subsistema existe en los tres** (`LIF` 64/43/81, `BKID`
28/23/22, `SENSER` 12/7/8) → lo propio de la fw3.21 de la A6000 es la **etiqueta** y los dos
nombres escritos como texto: otra vez «se reescribe el logging, no el firmware».

**Para la línea del obturador**: negativo acotado (0 menciones de obturador, disparo, lectura del
sensor o exposición) → **sin efecto en S51** (A/B/C = NO).

Informe: [analysis/s175_lif_debug/lif_debug.md](../../analysis/s175_lif_debug/lif_debug.md) ·
test: `tests/test_s175_lif_debug.py` (11 tests).
