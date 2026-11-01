# E26-R43 — CL1000/`BOOT_MAIN` (bit 0) cerrado estáticamente: sin atajo por el conector Multi; corrige el pin de `BOOT_SERIAL_IN` en CN4001

Fecha: 31-10-2026. Continúa [R31](e26-r31-bootmain-bit0-cierre.md)/[R32](e26-r32-moderreg-valor-real.md). Pedido del usuario:
verificar si hay alguna alternativa a la clave de `nflasha0` y, en concreto, cerrar de forma estática si forzar `CL1000` a
masa es una vía viable — incluyendo revisar el código GPL de Sony. Método: **sin rasterizar a PNG** — `pdftotext -bbox`
(posición exacta de cada etiqueta) y `pdftocairo -svg` (trazos vectoriales reales) sobre `references/manuals/a6000_service_L3.pdf`,
páginas 24 ("CLK BOOT") y 37 ("MULTI TERMINAL"); código fuente GPL de Sony en
`analysis/session18/codex-g/oss-linux/linux/arch/arm/mach-cxd90014/`. Script:
[`r43_cl1000_cn4001_trace.py`](../../analysis/e26-recovery/r43_cl1000_cn4001_trace.py). Test:
[`test_e26_r43_cl1000_cn4001.py`](../../tests/test_e26_r43_cl1000_cn4001.py) (3). Solo lectura, sin cámara.

Etiquetas: **ESQUEMA** (vectores + texto del PDF, no el `.txt` OCR) · **FUENTE SONY** (GPL) · **DEDUCCIÓN**.

## 1. Resumen

| # | Pregunta | Resultado |
|---|---|---|
| 1 | ¿El código GPL de Sony define la polaridad de `CL1000`/`BOOT_MAIN` (bit 0)? | **No.** `regs-misc.h` (CXD90014 y CXD4132) solo nombra el bit 1 (`MISC_MODEREG_BOOT_SERIAL_IN` / `MODEREAD_BM1`). Ningún archivo del árbol GPL (`mach-cxd90014`, `mach-cxd4132`) menciona `BOOT_MAIN`, `CL1000` ni strap/pull de arranque. No hay alternativa en el código fuente: sigue siendo un strap de hardware sin reflejo en software. |
| 2 | ¿`CL1000` tiene alguna salida hacia un conector externo (Multi, CN4001), como la que sí tiene `BOOT_SERIAL_IN`? | **No.** Trazado vectorial exhaustivo de la hoja CLK BOOT: la fila de `P7`/`BOOT_MAIN` termina en el punto de prueba `CL1000` sin ningún salto de fila hacia la columna de exportación global (x≥500 pt). Sigue siendo un punto de prueba interno. |
| 3 | ¿A qué pin de CN4001 llega entonces `BOOT_SERIAL_IN` (bit 1, H21)? | **Al pin 10** (etiqueta de conector "AD_JACK_IN"), **no al pin 9** como daban por hecho R11/R19/R20/R29. El pin 9 solo lleva `DEBUG_UART0_RXD`, una señal distinta e independiente. |

**Conclusión operativa: `CL1000` a masa sigue siendo exclusivamente una intervención física interna** (abrir la cámara,
localizar P7/`CL1000` en la placa — visible en la página 50 del manual, vista de componentes `SY-1028 BOARD SIDE A`).
No hay atajo por el conector Multi externo. La polaridad necesaria para que forzarlo a masa ponga el bit en 0 sigue sin
poder determinarse sin hardware (mismo límite que R31 §3 y R32 §5; nada en este informe lo cambia).

## 2. Por qué hacía falta repetir el trazado (no agrupar por fila)

R11/R19/R20/R29 asignaban `BOOT_SERIAL_IN` al pin 9 de CN4001 usando `scripts/schematic_pin_nets.py`, que agrupa por
**fila de texto**. En la hoja CN4001 (página 37) eso falla exactamente igual que en CN4906 (razón por la que R29 ya tuvo
que escribir `r29_pinout_pixel_trace.py` para esa hoja, pero nunca lo aplicó a CN4001): la etiqueta global izquierda de
una fila y la descripción del pin a la derecha **no están a la misma altura que el propio nombre de fila que se lee**,
porque el trazo real queda ~3,5 pt por debajo de su etiqueta en toda esta hoja (y en la hoja CLK BOOT, de forma análoga).
Agrupar por texto-en-la-misma-línea confunde `DEBUG_UART0_RXD`/pin 9 con `BOOT_SERIAL_IN`/pin 10, que son la fila
siguiente.

Prueba por coordenadas (sin ambigüedad, bbox + trazo vectorial continuo hasta `x=379.43`, borde de la tabla de pines):

| Etiqueta global (izquierda) | Pin CN4001 | Descripción del pin (derecha) |
|---|---|---|
| `XRESET_REQ` | 7 | `XRESET_REQ` |
| `DEBUG_UART0_RXD` | **9** | `UART_RX/BOOT_IN` |
| `BOOT_SERIAL_IN` | **10** | `AD_JACK_IN` |
| `AD_JACK_IN` | 11 | `ROUT/XAELOCK` |

`R4002` (XX) / `CM4002` (montado, sin XX) alimentan el pin 9; `R4003` (XX) / `CM4003` (montado, sin XX) alimentan el
pin 10 — cada par queda dentro de su propia fila, sin fusión entre pines 9 y 10 (se comprobó que ningún segmento conecta
ambas filas: cada una llega a la tabla por un trazo recto independiente).

## 3. Trazado de la hoja CLK BOOT (página 24): H21 sí exporta, P7 no

Cada fila de pin (`K6`, `N6`, `AD1`, `P8`, `H21`, `P7`) repite su propio nombre interno dos veces (a la izquierda del
número de bola y de nuevo a la derecha, antes del cableado) y, **solo si el trazo sigue más allá**, una tercera etiqueta
en la columna x≈520–550 es la exportación global real — con un nombre que en esta hoja **no coincide** con el nombre
interno del pin (patrón ya visto en R42 para `N6`/`XRESET_REQ`→`XMSS_RESET`, verificado aquí para `H21` y `P7`):

- **H21** (nombre interno `BOOT_SERIAL_IN`, bit 1): su trazo sale de la fila, sube/baja por una columna vertical en
  `x=495.24` y llega a la etiqueta global **`BOOT_SERIAL_IN`** (`x≈526`, `y≈253.6`) — que es la misma etiqueta que, en
  la página 37, alimenta el pin 10 de CN4001 (§2). Cierra el camino externo de bit 1.
- **P7** (nombre interno `BOOT_MAIN`, bit 0): su trazo llega hasta el símbolo de punto de prueba `CL1000`
  (`x≈471–480`) y **ahí termina**: no hay ningún segmento posterior, ni horizontal ni vertical, dentro de la hoja
  completa (`x` hasta 560 pt, todo el ancho útil de la columna de exportación). `CL1000` es un punto de prueba interno
  sin pista hacia ningún conector.

## 4. Límites

- Cubre páginas 24 y 37 del manual (las únicas con `BOOT_MAIN`/`CL1000`/`BOOT_SERIAL_IN`/CN4001, confirmado por
  búsqueda de texto en las 55 páginas: `CL1000` solo aparece además en la vista de componentes, página 50, sin
  información eléctrica). No se repitió el barrido para CN4906 (ya cubierto por R29 con pixel-trace propio).
- Asume que `CM4002`/`CM4003` (sin marca `XX`) están realmente montados en esta unidad — convención del manual, no
  verificado físicamente (mismo límite que `E26-R19-CM-MONTAJE`).
- No determina la polaridad de `BOOT_MAIN`: sigue siendo imposible sin hardware (R31 §3, R32 §5). Este informe cierra
  la pregunta de **acceso** (¿hay atajo externo?), no la de **polaridad** (¿qué nivel hay que forzar?).
- El hallazgo del pin 10 (bit 1) es nuevo y **no verificado físicamente**: abre `E26-R43-PIN10-CONTINUIDAD` como
  cierre físico, igual que ya pedía `E26-R19-CM-MONTAJE` para el pin 9 (ahora corregido a pin 10).

## 5. Correcciones a otros informes

- **Corrige R11/R19/R20/R29 (tabla CN4001):** `BOOT_SERIAL_IN` llega al **pin 10** de CN4001 (etiqueta de conector
  `AD_JACK_IN`), no al pin 9. El pin 9 (`UART_RX/BOOT_IN` en el conector) solo lleva `DEBUG_UART0_RXD`, una señal de
  consola distinta, sin relación con `MODEREG`.
- **Corrige la lectura implícita de R19/R29 de `E26-R19-CM-MONTAJE`:** la vía «Multi pin 9 ↔ H21» no existe; es «Multi
  pin 10 ↔ H21». El cierre físico pendiente (continuidad sin energía) pasa a ser sobre el pin 10.
- **No corrige R31/R32/R33** (bit 0 = `BOOT_MAIN` = `CL1000`, valor en reposo, clave en `nflasha0`): quedan vigentes.
  Este informe solo añade que `CL1000` no tiene salida externa, lo que **descarta** la hipótesis (propuesta y no
  verificada en esta misma sesión, antes de este informe) de que se pudiera forzar bit 0 sin abrir la cámara.
