# E26-R29 — Pinout completo de CN4001 (Multi) y CN4906 (servicio): los 33 pines mapeados a su red

Alcance acordado con el usuario: mapear **todos** los pines de los dos conectores ya usados en la investigación de arranque, no el esquema completo (54 páginas). Fuente: manual de servicio, PDF páginas 37 (CN4001) y 38 (CN4906); herramientas `scripts/schematic_pin_nets.py` (agrupación por fila) y, para el cableado que cruza filas, el nuevo `analysis/e26-recovery/r29_pinout_pixel_trace.py` (trazado por coordenadas de píxel sobre el render a 600 dpi). Test: `tests/test_e26_r29_pinout_cn4906.py` (5, reproduce el trazado automáticamente) + `tests/test_e26_r11_pinout.py` (14, corregido).

## 1. Corrige dos errores en el pinout ya publicado (R11)

El informe R11 original (y el script que lo generó) tenían **dos desplazamientos de numeración**, verificados ahora por bytes/texto del PDF:

| Conector | Error anterior | Corregido |
|---|---|---|
| CN4001 | pin1=USB_D-, pin2=USB_D+, **sin pin3** | **pin1=USB_VBUS, pin2=USB_D-, pin3=USB_D+**, pin4=USB_ID… (el resto, 4-15, ya era correcto) |
| CN4906 | pin10=TCK(SWCLK), pin11=TMS(SWDIO), pin12=TDI… **sin RTCK** | **pin10=RTCK**, pin11=TCK(SWCLK), pin12=TMS(SWDIO), pin13=TDI, pin14=NTRST, pin15=DEBUG_MODE (desplazado un lugar desde el pin10) |
| CN4906 | pines «31/32 = XS_2/XS_1» | **No existen**: CN4906 es un conector de **18 pines**. Esos números pertenecen a OTRO conector de la misma hoja (el flex del panel superior con el interruptor del disparador, ya documentado en `s21-claude-button-to-shutter-order.md`), confundido por estar en la misma página del esquema. |

Ninguna corrección afecta las direcciones/hallazgos de los informes que citan CN4001 pin9/10 o CM4002/CM4003 (R19, R20, R21): esos pines no cambiaron.

## 2. CN4001 — Multi Terminal, 15+4 pines (PDF pág. 37)

| Pin | Señal externa | Red interna / puente | Montaje |
|---|---|---|---|
| 1 | USB_VBUS | — (F4001, fusible 2A/36V) | — |
| 2 | USB_D- | USB_D-_UM (filtro E) | — |
| 3 | USB_D+ | USB_D+_UM (filtro E) | — |
| 4 | USB_ID | — | — |
| 5 | GND | — | — |
| 6 | D_3.1V/LANC_DC | D_3.15V (R4001, XX) | no |
| 7 | XRESET_REQ | XRESET_REQ (R4008, XX) | no |
| 8 | UART_TX/LANC_SIG | DEBUG_UART0_TXD (CM4008) | **sí** |
| 9 | UART_RX/BOOT_IN | DEBUG_UART0_RXD (R4002, XX, no) **/** BOOT_SERIAL_IN (CM4002, sí — se une al nodo del pin 10) | mixto, ver R19 |
| 10 | AD_JACK_IN | AD_JACK_IN (CM4003, sí) — mismo nodo que BOOT_SERIAL_IN del pin 9 | **sí** |
| 11 | ROUT/XAELOCK | — | — |
| 12 | LOUT/XSHUT | XS_1 (R4004, XX) | no |
| 13 | VIDEO | XS_2 (CM4004/CM4005) | sí |
| 14 | AV_GND | — | — |
| 15 | XPWR_ON | — | — |
| 16-19 | REG_GND | masa/blindaje vía D4001 (XX) | no |

## 3. CN4906 — huella de servicio, 18 pines (PDF pág. 38): conector combinado BIONZ + Darwin

Hallazgo nuevo de este informe: **CN4906 no es solo un puerto de depuración de BIONZ**. Tres de sus pines (11, 12, 15) **unen** (con un punto de conexión visible en el esquema, verificado por píxel) la vía de servicio de BIONZ con el bus interno de depuración de Darwin (prefijo `_DWN`, IC5700). Los pines 6, 7, 8, 9, 13, 14 están dedicados cada uno a una señal `_DWN` distinta, y el pin 10 (RTCK) no tiene ninguna red externa.

| Pin | Señal | Origen (ALTA = verificado por bytes/píxel; MEDIA = inferido) |
|---|---|---|
| 1 | REG_GND | masa |
| 2 | BOOT_MODE_1 | FIQ, vía R4910 (XX) — ALTA |
| 3 | EVER_3.15V | EVER_3.15V, vía CL4910/CL4911 (cruce resaltado en el esquema) — ALTA |
| 4 | UART_RXD_MSS | DEBUG_UART0_RXD (directo) — ALTA |
| 5 | UART_TXD_MSS | DEBUG_UART0_TXD (directo) — ALTA |
| 6 | UART_RXD_DWN | DWN_UART_RXD (Darwin) — ALTA (trazado por píxel) |
| 7 | UART_TXD_DWN | DWN_UART_TXD (Darwin) — ALTA (trazado por píxel) |
| 8 | NSRST | MD0_DWN (Darwin) — MEDIA (única candidata sin resistencia por nombrar; alineación vertical con pequeño margen) |
| 9 | TDO | TDO_DWN (Darwin) — ALTA (trazado por píxel) |
| 10 | RTCK | **sin red externa** — ALTA (ningún trazo llega a esta fila) |
| 11 | TCK(SWCLK) | SWCLK (R4911, XX) **+** TCK_DWN (Darwin, unidos en el mismo nodo) — ALTA |
| 12 | TMS(SWDIO) | SWDIO (R4912, XX) **+** TMS_DWN (Darwin, unidos) — ALTA |
| 13 | TDI | TDI_DWN (Darwin) — ALTA (trazado por píxel) |
| 14 | NTRST | TRST_DWN (Darwin) — ALTA (trazado por píxel) |
| 15 | DEBUG_MODE | VIO_FLD (R4913, XX) **+** XDWN_RESET (Darwin, unidos) — ALTA |
| 16 | REG_GND | masa |
| 17-18 | REG_GND | sin etiqueta propia; une al bus de masa del conector |

**Método del trazado por píxel (pines 6-15):** cada señal `_DWN` corre como línea horizontal propia a la izquierda del esquema y sube en una columna vertical dedicada (coordenada x fija) que se dobla hacia su pin exacto. `scripts/schematic_pin_nets.py` agrupa por fila y no distingue esto (confunde filas que solo se cruzan); `r29_pinout_pixel_trace.py` sigue cada columna x con Pillow sobre el render a 600 dpi y localiza el segmento continuo más largo (el tramo real; los demás son cruces con otras líneas horizontales). Las 9 columnas encontradas casan, con una precisión de 1-3 px, con las filas de pin y de etiqueta esperadas — confirmado para 8 de 9 (pin8/MD0_DWN con un margen algo mayor, de ahí la confianza MEDIA).

## 4. Qué cambia para la investigación de arranque

- **No cambia nada de lo ya usado:** BOOT_SERIAL_IN (CN4001 pin9/10), BOOT_MODE_1 (CN4906 pin2), y el UART de servicio (CN4906 pin4/5) mantienen las mismas direcciones y conclusiones de R5/R8/R9/R11/R19/R20/R21.
- **Nuevo:** CN4906 da acceso, por el mismo conector de 18 pines, tanto al JTAG/SWD de BIONZ (pines 11/12/15, compartidos) como al bus de depuración completo de Darwin (pines 6-9/13/14, dedicados) — útil si en algún momento se autoriza instrumentar Darwin además de BIONZ.
- Los pines `_DWN` dependen de las mismas resistencias **XX (no montadas)** que el resto del conector de servicio: acceder a ellos requiere la misma soldadura/puente que ya estaba fuera de alcance sin autorización física.

## 5. Límites

- No se resolvió el pin 8 (NSRST←MD0_DWN) con la misma certeza que el resto; el margen de alineación es mayor y no hay una segunda confirmación independiente.
- Montaje físico real de `CM4002/CM4003/CM4008` y de las resistencias XX: no verificado en esta unidad (solo el esquema).
- No se tocó ningún otro conector del esquema (fuera del alcance acordado).
