# E26-R19 — Capa USB de Darwin (USB Charger) y red de arranque en el esquema

Fecha: 30-10-2026. Continúa [R10](e26-r10-usb-charger-recovery.md) y [R11](e26-r11-bootrom-uart-physical-access.md). **Solo análisis estático y emulación offline.** Sin cámara, sin USB/UART, sin escritura. Pedido del usuario: avanzar hacia una solución (forzar modo de actualización) en vez de seguir R18-corpus; después, resolver el callback USB de clase/vendor.

Etiquetas: **BINARIO** = bytes/desensamblado de `darwin_core.bin` (SHA `5f2be06d…`, Cortex-M Thumb), con [`r19_darwin_usb.py`](../../analysis/e26-recovery/r19_darwin_usb.py), [`r19_darwin_usb_emu.py`](../../analysis/e26-recovery/r19_darwin_usb_emu.py) y sus pruebas en `tests/test_e26_r19_*` · **EMULACIÓN** = Unicorn, con las rutinas de transmisión/parada interceptadas · **ESQUEMA** = inspección visual del manual (págs. 24, 37, 38), no código · **INFERENCIA** · **NO VERIFICADO**. REA (Ghidra, `arm`, base 0) se abrió pero **no reconoce el Thumb** de este binario; el desensamblado es Capstone, sin cotejo REA.

## 0. Corrección de mapeo (importante)

**BINARIO. dirección = offset de archivo + `0x4200`.** Los descriptores USB del archivo (`0x239e4`, R10) son `0x27be4` en el código (puntero en `0x23a40`), y el vector de reset `0x45c9` lleva a `0x3c8` del archivo (`bl 0x438; ldr r0,=…; bx r0`). Los `bl`/`b`/`ldr [pc]` trabajan en offsets de archivo (por eso lo analizado antes sigue siendo válido), pero **los punteros absolutos hay que restarlos `0x4200`**. En la primera pasada de R19 traté `0x1079d…` y los 22 punteros DWN como offsets de archivo: eso daba rutinas «desalineadas» y un rango DWN erróneo (`0x7150–0x8dac`). Está corregido abajo.

## 1. Resumen

1. **BINARIO. Despachador USB EP0 de Darwin = `0xc90a`.** Lee el setup (8 B) a `0x20002df0` y bifurca por `(bmRequestType>>5)&3`: estándar → `0x19388`; clase/vendor → `0xd032`, que llama al callback `[0x200032a4]` si no es nulo; otro tipo → `0xc8d8` (parada). No hay otro manejador de EP0.
2. **BINARIO. Estándar (`0x19388`):** GET_DESCRIPTOR (6) → `0x193b0` (tipos 1, 2, 3 y `0x21`); 7 y `0xc` → callback; el resto → parada.
3. **BINARIO. Los cuatro callbacks** (`{0x1079d, 0x1077f, 0x10717, 0x106c1}`, registrados por `0xc650` → `0x19284` → `0xce54`) están en los offsets `0xc59c`, `0xc57e`, `0xc516`, `0xc4c0`:
   - `[0]` `0xc59c` — **solicitud de setup de clase/vendor** (detalle en §2).
   - `[4]` `0xc516` — evento de bus con código `r0` (3, 4, 5): en el 3 pone/borra el bit `0x4000` de `0x4004214c` (según el dato recibido) y marca estado; encadena a `[0x200032a8]`. No hay salida a periféricos más allá de ese bit USB.
   - `[8]` `0xc57e` — solo registro de depuración (`0x21090`) para códigos distintos de 3 y 4.
   - `[0xc]` `0xc4c0` — registro de depuración y aviso `post(0x13, …)` (`0xa930`) con la petición codificada; marca `[0x20002dbc]=1`.
4. **BINARIO + EMULACIÓN. Respuesta por tipo de petición** (callback `[0]`, setup sintético): GET_DESCRIPTOR estándar con `wValue>>8 = 0x22` (informe HID) → EP0 envía `0x20002dc4`, longitud `min(wLength, 0x13)`; cualquier otro descriptor estándar → parada. Clase: GET_REPORT (`bRequest=1`) → EP0 con longitud 0; SET_IDLE (`0x21`, `bRequest=0x0a`) → solo borra el bit `0x400` de `0x40042144`; SET_REPORT, GET_IDLE, GET_PROTOCOL y cualquier otra clase → parada. **Vendor (tipo 2) → parada siempre**, sin efectos en periféricos ([`tests/test_e26_r19_darwin_usb_emu.py`](../../tests/test_e26_r19_darwin_usb_emu.py)).
5. **BINARIO. Darwin no tiene código de programación de flash:** ningún literal hacia el controlador de flash FM3 (`0x4000_0000–0x4000_2fff`) en `0x0–0x21000`, y ninguno hacia MFS (`0x40038000…`; las bases MFS solo están en tablas de datos `0x236d4–0x239bc`).
6. **BINARIO. Módulo «DWN» (`DWN_VER0.78`, tabla de 22 punteros en `0x21950`, rutinas en los offsets `0x2f50–0x4ba8`):** solo hay un literal de periférico, `0x40010000` (bloque de reloj/reinicio), sin flash ni MFS, y **ningún literal apunta a la tabla** (`0x25b50`). Primera rutina (`0x2f50`): registro y tres llamadas a `0x2a0c`; el despachador de la tabla no está localizado. Nada lo vincula con USB.
7. **ESQUEMA (corrige R11).** En las páginas 24 y 37, junto a cada `R… XX` hay un `CM…` en paralelo **sin `XX`**; el mismo patrón está en redes que deben conducir (`R6000 XX`+`CM6000` en XRESET del BIONZ; `R1003 XX`+`CM1003` en CLK_SYS_IN). **INFERENCIA:** el `CM` es la opción montada; entonces `R4002/CM4002` y `R4003/CM4003` unen el pin 9 del Multi (`UART_RX/BOOT_IN`) con `DEBUG_UART0_RXD` y con `BOOT_SERIAL_IN` (H21 del BIONZ). R11 Q2/Q3 («sin camino») dependía de leer solo la `XX`. Contraste: `R4910`, `R4927`, `R4911–R4917` de CN4906 no tienen `CM` paralelo.
8. **ESQUEMA.** `BOOT_MAIN` (P7 del BIONZ) va solo al punto de prueba `CL1000` (pág. 24; ubicado en pág. 50). **Hipótesis, sin probar:** sería el bit 0 de `MODEREG` (`0xf2915010`), el selector del BootROM. `regs-misc.h` no define ese bit.
9. **ESQUEMA.** CN4906: pines 4/5 = `DEBUG_UART0_RXD/TXD` directos; `DEBUG_UART0_RXD` y `BOOT_SERIAL_IN` solo se unen en el nodo del pin 9 del Multi. **CN4906 no alimenta `BOOT_SERIAL_IN`**. `BOOT_MODE_1` (pin 2) solo llega a FIQ por `R4910 XX` y a MD0 de Darwin por `R4927 XX`. «CN4908» no aparece en el manual (¿CN4906?).

## 2. Callback de setup clase/vendor (`0xc59c`)

`bmRequestType = [r0]`, `tipo = (bmRequestType>>5)&3`:

| Tipo | Petición | Acción | Evidencia |
|---|---|---|---|
| 0 estándar | `wValue>>8 == 0x22` | EP0 envía `0x20002dc4` (informe HID, 19 B) | BINARIO `0xc5ca–0xc5e2`; EMULACIÓN |
| 0 estándar | otro | parada | `0xc5e6` → `0x1932e(0,0)` → `0xc8d8` |
| 1 clase | `bRequest=1` (GET_REPORT) | EP0 con longitud 0 | `0xc5aa–0xc5b4`, `r1=0` |
| 1 clase | `bRequest=0x0a` y `bmRT=0x21` (SET_IDLE) | borra bit `0x400` de `0x40042144` | `0xc5b6–0xc5c8` |
| 1 clase | resto | parada | `0xc5e6` |
| 2 vendor | cualquiera | **parada** (`cmp r3,#1; bne 0xc5e6`) | `0xc5a6–0xc5a8`; EMULACIÓN |

No hay etapa de datos OUT: ninguna petición acepta datos del host hacia la cámara, y ningún camino escribe flash, UART ni GPIO.

## 3. Decisión: B para el USB Charger (cerrado), C para el resto

- **USB Charger: cerrado para recuperación.** Descriptor HID solo-Input (R10), callback de clase/vendor que solo atiende GET_DESCRIPTOR HID, GET_REPORT y SET_IDLE, vendor siempre parado, sin código de flash. **Límites:** análisis de la capa USB de Darwin 3.21 (no del firmware actual de la cámara); no se ha examinado el consumidor del aviso `post(0x13)` ni el uso de EP1; la emulación intercepta transmisión y parada y no ejecuta el resto de la pila.
- **Vía DWN:** sin referencias ni acceso a flash; no demostrada.
- **Vía Multi↔`BOOT_SERIAL_IN`:** reabierta por §1.7, sin verificar (inferencia de esquema).
- **Vía CN4906:** no sirve para el BootROM serie (§1.9).

## 4. Pendientes

Ver `E26-R19-*` en [PENDIENTES](../PENDIENTES.md).
