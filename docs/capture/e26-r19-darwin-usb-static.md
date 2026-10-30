# E26-R19 — Capa USB de Darwin (USB Charger) y red de arranque en el esquema

Fecha: 30-10-2026. Continúa [R10](e26-r10-usb-charger-recovery.md) y [R11](e26-r11-bootrom-uart-physical-access.md). **Solo análisis estático.** Sin cámara, sin USB/UART, sin escritura. Pedido del usuario: avanzar hacia una solución (forzar modo de actualización) en vez de seguir R18-corpus.

Etiquetas: **BINARIO** = bytes/desensamblado de `darwin_core.bin` (SHA `5f2be06d…`, Cortex-M Thumb, base 0), con [`r19_darwin_usb.py`](../../analysis/e26-recovery/r19_darwin_usb.py) y [`tests/test_e26_r19_darwin_usb.py`](../../tests/test_e26_r19_darwin_usb.py) · **ESQUEMA** = inspección visual del manual (págs. 24, 37, 38), no código · **INFERENCIA** · **NO VERIFICADO**. REA (Ghidra, `arm`, base 0) se abrió pero **no reconoce el Thumb** de este binario; el desensamblado es Capstone, sin cotejo REA.

## 1. Resumen

1. **BINARIO. Despachador USB EP0 de Darwin = `0xc90a`.** Lee el setup (8 B) a `0x20002df0` y bifurca por `(bmRequestType>>5)&3`: estándar → `0x19388`; clase/vendor → `0xd032`, que llama al callback `[0x200032a4]` si no es nulo; otro tipo → `0xc8d8`. No hay otro manejador de EP0.
2. **BINARIO. Estándar (`0x19388`):** solo GET_DESCRIPTOR (6) → `0x193b0` (tipos 1, 2, 3 y `0x21` = HID); 7 y `0xc` → callback; el resto → `0xc8d8`.
3. **BINARIO. Callbacks:** `0xc650` los apila `{0x1079d, 0x1077f, 0x10717, 0x106c1}` y llama a `0x19284` (`0xc66a`), que los registra con `0xce54`. **Qué hace el callback de clase/vendor no está resuelto**: tres de los cuatro punteros caen en mitad de rutinas contiguas (p. ej. `0x1077e` es el segundo halfword de un `bl`), y las rutinas vecinas solo escriben un búfer de estado en `0x20003632` y llaman a `0xe9b8`.
4. **BINARIO. Darwin no tiene código de programación de flash:** ningún literal hacia el controlador de flash FM3 (`0x4000_0000–0x4000_2fff`) en `0x0–0x21000`, y ninguno hacia MFS (`0x40038000…`; las bases MFS solo están en tablas de datos `0x236d4–0x239bc`).
5. **BINARIO. Módulo «DWN» (`DWN_VER0.78`, tabla de 22 punteros en `0x21950`, rutinas `0x7150–0x8dac`) no es un descargador:** solo toca un periférico (GPIO `0x40033000`, `0x7ff6`), sin flash ni MFS, y **ninguna instrucción referencia la tabla** (sin literales a `0x21900–0x21a80`). Nada la vincula con USB.
6. **ESQUEMA (corrige R11).** En las páginas 24 y 37, junto a cada `R… XX` hay un `CM…` en paralelo **sin `XX`**; el mismo patrón está en redes que deben conducir (`R6000 XX`+`CM6000` en XRESET del BIONZ; `R1003 XX`+`CM1003` en CLK_SYS_IN). **INFERENCIA:** el `CM` es la opción montada; entonces `R4002/CM4002` y `R4003/CM4003` unen el pin 9 del Multi (`UART_RX/BOOT_IN`) con `DEBUG_UART0_RXD` y con `BOOT_SERIAL_IN` (H21 del BIONZ). R11 Q2/Q3 («sin camino») dependía de leer solo la `XX`. Contraste: `R4910`, `R4927`, `R4911–R4917` de CN4906 no tienen `CM` paralelo.
7. **ESQUEMA.** `BOOT_MAIN` (P7 del BIONZ) va solo al punto de prueba `CL1000` (pág. 24; ubicado en pág. 50). **Hipótesis, sin probar:** sería el bit 0 de `MODEREG` (`0xf2915010`), el selector del BootROM. `regs-misc.h` no define ese bit.
8. **ESQUEMA.** CN4906: pines 4/5 = `DEBUG_UART0_RXD/TXD` directos; `DEBUG_UART0_RXD` y `BOOT_SERIAL_IN` solo se unen en el nodo del pin 9 del Multi (vía CM4002/CM4003). **CN4906 no alimenta `BOOT_SERIAL_IN`**; el camino al receptor del BootROM es el Multi. `BOOT_MODE_1` (pin 2) solo llega a FIQ por `R4910 XX` y a MD0 de Darwin por `R4927 XX`: sin montaje probable. «CN4908» no aparece en el manual (¿CN4906?).

## 2. Decisión: C (USB Charger cerrado con límite)

- **Vía USB Charger: sin canal demostrado.** HID solo Input (R10) y capa USB sin escritura de flash ni de GPIO de modo en los literales analizados. **Límite:** el callback de clase/vendor y sus llamadas indirectas no están resueltas; no se descarta que acepte peticiones que muevan estado, solo que ninguna alcanza flash o UART en lo trazado.
- **Vía DWN: no demostrada y sin referencias.**
- **Vía Multi:** reabierta por §1.6 (antes descartada en R11).
- **Vía CN4906:** no sirve para el BootROM serie (§1.8).

## 3. Pendientes

Ver `E26-R19-*` en [PENDIENTES](../PENDIENTES.md): montaje de `CM4002/CM4003`, nivel de `BOOT_MAIN`, callback USB, texto del BootROM `ffff1062–109e`.
