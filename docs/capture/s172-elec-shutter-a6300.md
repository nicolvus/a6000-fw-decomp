# S172 — el módulo `ElecShutter` del A6300: qué hace realmente

> Hito de la **línea de RE general** con valor directo para la **línea del obturador electrónico**.
> Solo bytes del `av-cam.bin` del A6300 fw2.01, con la A6000 fw3.21 y la A7S fw3.20 como
> comparación.

## Veredicto

**S135** localizó el subsistema `ElecShutter/` en el HAL del A6300 por sus **nombres de
fichero** y sus ajustes, sin decodificar el comportamiento. Este hito **localiza el código** (los
nombres de fichero son cadenas `__FILE__` de un `EC_ASSERT %s:%d`) y **caracteriza las dos
funciones**:

1. **`EC_ElecShutter_Main.cpp`** (`0x4391d67c`): lee un **u16** de una tabla global y devuelve un
   **código de modo de obturador**: `0x80` → **3**, `0x100` → **4**; otro valor → `EC_ASSERT`
   con línea **0x421** (1057) y devuelve 3.
2. **`EC_NonlinearElecShutter_MechShutterTable.cpp`**: la **equivalencia no lineal entre
   velocidad electrónica y mecánica**:
   * **interpolación por tramos**: lee una fila con `ldr.w r3,[r2,r6,lsl #2]` (**32 bits por
     fila**), interpola con escalas **10000** (`0x2710`) y **1000** (`0x3e8`), helper `0x435586f8`
     y setters `0x4391da74`/`0x4391da9c`; `EC_ASSERT` línea **0x23c** (572);
   * **búsqueda en punto fijo 16.16**: escala `0x8000` y **15 bits fraccionarios**; `EC_ASSERT`
     línea **0x24f** (591).

## Corrección a S135

Los **128 bytes** que S135 identificó como «tabla de índices de velocidad de obturación» en
`0x43dcfa9e` **no tienen ninguna referencia de código** (ni PIC ni puntero absoluto de 4 B) y
forman una tabla byte→byte **no decreciente** (más compatible con caracteres imprimibles). La
tabla real se indexa **por fila, con 32 bits por entrada**. Lo que S135 acertó (la existencia
del módulo `ElecShutter/`, sus ficheros y sus ajustes) **se mantiene**.

## Colateral

`EC_ASSERT` es **0/1/1** y `EC_ERR_PRINT` **0/0/5** (A6000/A7S/A6300): el motor EC de la A6000
**no instrumenta sus aserciones** — otra diferencia de *logging*, coherente con S128/S130.

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** La ausencia del módulo en la fw3.21 de
la A6000 no demuestra incapacidad del hardware.

Informe: [analysis/s172_elec_shutter_a6300/elec_shutter_a6300.md](../../analysis/s172_elec_shutter_a6300/elec_shutter_a6300.md) ·
test: `tests/test_s172_elec_shutter_a6300.py` (15 tests).
