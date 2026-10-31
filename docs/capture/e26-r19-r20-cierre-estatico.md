# E26-R19 / E26-R20 — Cierre estático de los pendientes restantes (30-10-2026)

Cierra `E26-R19-USB-EVT13`, `E26-R19-CM-MONTAJE`, `E26-R20-BOOTMAIN-NIVEL` y `E26-R20-GPIO4` solo con código y esquema; sin hardware. Test: `tests/test_e26_r19_r20_cierre.py`.

## 1. E26-R19-USB-EVT13 — CERRADO

- **BINARIO.** El callback `[0xc]` de Darwin (dirección `0x106c0`; ver nota de mapeo en R19 §0: direcciones = offset de archivo + `0x4200`) escribe un registro de depuración y llama `0xeb30` con id `0x13` (`movs r0,#0x13` en `0x10708`), luego `[0x20002dbc]=1`.
- **BINARIO.** `0xeb30` (el «post») compone un registro de 8 bytes (id, tarea, marca de tiempo `0x8e7e`, 2 parámetros) y lo copia (`0x255a6`) a anillos de traza (`0x26d2c`/`0x26d5c`, vía `0xebf8`/`0x6c3a`). **No es un mensaje a un manejador de estado: es traza.**
- **BINARIO.** `0x20002dbc` solo se referencia desde el literal `0x1093c` del módulo USB (`0x10716–0x10860`): estado interno del driver, sin consumidores fuera.
- **BINARIO.** El descriptor de configuración (archivo `0x239e4`) define un único endpoint: `0x81` IN, interrupt, 8 B, intervalo 1 (HID). **No hay endpoint OUT**: desde el host solo entra EP0 (ya resuelto en R19).
- **Conclusión:** ningún mensaje USB cambia estado más allá de la señal HID/bit USB; no hay ruta de datos hacia flash/UART en Darwin. Límite: Darwin 3.21 de archivo, no el firmware vivo.

## 2. E26-R19-CM-MONTAJE — CERRADO (convención de esquema)

- **ESQUEMA (pág. 37, imagen).** `R4002`/`R4003` llevan `XX`; `CM4002`/`CM4003` (símbolo de puente de dos pastillas) están **en paralelo y sin `XX`**. En el mismo esquema, `R6000 XX`+`CM6000` (XRESET) y `R1003 XX`+`CM1003` (reloj) siguen el patrón en redes que deben conducir. Por convención Sony, `XX` = no montado y los `CM` sin marca = montados.
- **Consecuencia:** `BOOT_SERIAL_IN` (IC6000 H21) ↔ nodo del pin 9 del Multi (`UART_RX/BOOT_IN`) conduce vía `CM4003`; `DEBUG_UART0_RXD` llega al mismo nodo por `CM4002`. Corrige la lectura R11 («abierto por R4003 XX»).
- **Límite:** inferencia de convención; no hay lista de partes por referencia ni comparación con A6300/A7S. La continuidad pin 9 ↔ H21 sigue siendo la confirmación definitiva (opcional, sin energía).

## 3. E26-R20-BOOTMAIN-NIVEL — CERRADO (límite)

- **ESQUEMA (pág. 24).** `BOOT_MAIN` (IC6000 P7) conecta solo a la isleta de prueba `CL1000`; en todo el texto del manual no aparece otra referencia a la red (ni resistencia de pull externa).
- **Conclusión:** el nivel por defecto lo fija el propio IC6000 (pull interno o dato de hoja de datos), no determinable con las fuentes del repo. Que `MODEREG` bit 0 = `BOOT_MAIN` sigue siendo inferencia (R20).
- **Hecho útil:** forzar el nivel requiere tocar `CL1000` (no hay resistencia que retirar); acción física, fuera de alcance sin autorización.

## 4. E26-R20-GPIO4 — CERRADO (roles resueltos; pines no identificables)

- **BINARIO (`0xffff0554`).** GPIO(4,RDATA) `0xf2910410` bit 21 elige un perfil de la estructura `0xc0010218` (consumida por `0x634` recepción y `0x87a`): `+0x10` (1 / `0x14`), `+0x14/+0x18` (`0x15f900` = 1 440 000 / `0x44aa20` = 4 500 000) y `+0x1c` = puntero a tabla.
- **BINARIO.** Las tablas de `+0x1c` tienen 11 instantes de muestreo (inicio + 8 datos + paridad + parada): bit21=0 → `0xffff19f0`, paso **250** ticks/bit (primer instante 100); bit21=1 → `0xffff1a1c`, paso **84** ticks/bit (primero 28). Relación 2,98: el perfil bit21=1 es ≈3× más rápido sobre el mismo temporizador `0xf2403000+0x10c`. La recepción es por software: `0x5da` muestrea `MODEREG` (`0xf2915010`) bit 1 en cada instante.
- **Significado de los «dos juegos»:** son dos velocidades de recepción serie por bit-banging, seleccionadas por un strap. Baudios absolutos: **NO VERIFICADO** (falta la frecuencia del temporizador); el papel de `+0x14/+0x18` no se trazó.
- **Pines:** bits 21/22 del banco 4 no tienen nombre de red en el firmware ni en el esquema (redes `GPIO_S_0..16`, `GPIO_SB_0..6`, `GPIO_0..16` sin mapa a banco/bit). Sin hoja de datos del IC6000 no se pueden identificar; no hay otra fuente estática.

## 5. Efecto sobre la solución práctica

El camino serie más plausible queda: Multi pin 9 (`BOOT_IN`) → `BOOT_SERIAL_IN` (CM4003 montado) → `MODEREG` bit 1, con `BOOT_MAIN`/`MODEREG` bit 0 a 1 para entrar en la ruta de servicio, y la tabla de clave `0xc0001200` (E26-R20-KEYTABLE) sin determinar. Todo lo que queda es físico (nivel real de `CL1000`, continuidad, contenido de `nflasha0`) y requiere autorización expresa.
