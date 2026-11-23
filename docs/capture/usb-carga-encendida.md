# USB-CARGA — Carga por USB con la A6000 encendida (23-11-2026)

Petición del usuario: buscar una manera real de cargar la batería de la A6000 por USB con la cámara encendida.
Etiquetas: **VERIFICADO** (bytes/instrucciones) · **WEB** (documentación oficial de Sony) · **INFERENCIA** · **NO PROBADO**.

## 0. Corrección (23-11-2026, a instancia del usuario)

La primera versión de este informe decía que los módulos de la A6300 daban «carga USB encendida». **Es falso.**

- **WEB:** la guía de la ILCE-6300 dice «As long as the power is on, the battery pack will not be charged even
  if the camera is connected to the AC Adaptor» ([suministro desde la red](https://helpguide.sony.net/ilc/1540/v1/en/contents/TP0000829921.html)).
  Su ajuste «USB Power Supply» solo alimenta la cámara por USB
  ([TP0000818612](https://helpguide.sony.net/ilc/1540/v1/en/contents/TP0000818612.html)), y aun así la batería
  puede aportar energía. Las notas de soporte de Sony repiten que la batería no carga con la cámara encendida, ni
  siquiera en reproducción ([00073605](https://www.sony.ca/en/electronics/support/articles/00073605)).
- **WEB:** la guía de la ILCE-6000 no tiene alimentación USB: con el adaptador incluido «power is not supplied» al
  disparar o reproducir; hace falta el AC-PW20 (batería simulada)
  ([TP0000226734](https://helpguide.sony.net/mig/Z001924611/EN/contents/TP0000226734.html)).
- **VERIFICADO en el binario:** en `usb_darwin.ko`, `usb_buspw_ic_set_charging_enable` (`0xe70`) solo escribe una
  traza (`osal_record_pro`) y no envía nada a Darwin. Desde Linux no se puede activar la carga.

Los módulos de la A6300 dan **alimentación USB** (la cámara gasta del USB en vez de la batería), no carga. La carga
con la cámara encendida la impide **Darwin**, y solo se puede cambiar parcheando Darwin (§3).

## 1. Cadena de alimentación (VERIFICADO salvo donde se indica)

| Eslabón | A6000 3.21 | A6300 2.01 |
|---|---|---|
| Cargador | IC5651 **OZ8072**, por I²C `USB_CHG_SDA/SCL` (P57/SOT1, P58/SCK1) y `IC_5651_EN` (P24) desde el **MCU Darwin IC5700**; `SUS` = `DWN_SUS` desde el SoC (manual de servicio) | mismo esquema |
| RTOS `av-cam.bin` | Servicio OSAL `0x2804d3` (`0x439884c4`, manejador `0x43b5ca2a`): get tipo de adaptador (búfer Darwin `+0xfd`), get/set límite de corriente (`+0xfe`, orden Darwin `0x38`) | igual |
| Kernel | **faltan** `usb_darwin.ko` y `usb_buspwr.ko` | presentes (`USB Power Supply`) |
| Userland | `libUsbBusPower.so` lee NVRAM `0x1210001` (6 = `usb_darwin.ko`); en la A6000 vale 0 | igual, más `libUsbChargingApp.so` |

Compatibilidad del módulo (VERIFICADO): mismo `vermagic`, `struct module` de `0x12c` B, sin `__versions`, los 54
símbolos importados existen en la A6000; las claves NVRAM que faltan caen en el valor 0.

## 2. Control del cargador en Darwin (VERIFICADO; dirección Darwin = archivo + `0x4200`)

Darwin conserva cadenas de depuración y hace él mismo la detección BC1.2 (`SDP/CDP/DCP`, `APPLE Charger(…)`,
`SONY Charger Detected.`).

| Función | Qué hace |
|---|---|
| `0xc390(reg, máscara, valor)` | Lee-modifica-escribe los registros 4, 5 y 6 del OZ8072 por I²C (sombras en `0x20002b00..02`), con verificación y 6 reintentos (`[ERR]BGL_S`) |
| `0xc470` | Inicialización: `P24 = 1` (`0x51c0(0x110,1)`: habilita el OZ8072), reg4 = `0xb8`, reg5 = `2`, reg6 = `0x28` |
| `0xc5bc(tipo)` | Encendido con USB («`USB PWR`», en `0x71c4`): reg4[2:0] = límite según el tipo de puerto (0–4) y **reg5 bit 3 = 1** (el USB alimenta el sistema) |
| `0xc50a` | Quita la alimentación USB: reg5 bit 3 = 0 y reg4 límite = 0 |
| `0xc4e8(a, b, c)` | reg5 = `(reg5 & 0x38) | a | b`; reg6[2:0] = `c`. **Es la única que toca los bits de carga** |
| `0xc660` | «BGL ON»: aplica reg4/reg5/reg6 desde `0x20002af9..afb` |
| `0xc8bc(buf)` | Guarda 3 B en `0x20002af9..afb` y aplica `0xc660` solo si el indicador `[0x20000029]` es 0 (`0xcf14(9)`); la llama el despachador de órdenes de BIONZ en `0x245dc` |

Llamadas a `0xc4e8` (barrido de todo `darwin_core.bin`):

| Sitio | Argumentos | Contexto |
|---|---|---|
| `0x8792` (máquina `0x8744..`) | `(1,0xc0,4)`, `(1,0x80,4)`, `(1,0xc0,0)`, `(2,0x80,0)` | modo apagado: carga |
| `0x85cc` | `(2,0,0)` | modo apagado: corte |
| `0x8c64` («`Off exit`», `0x8c42`) | `(2,0,?)` | **al encender la cámara: carga cortada** |

INFERENCIA (falta la hoja de datos del OZ8072, que no es pública): reg5 bit 0 = carga activada, bit 1 = carga
inhibida, bits 6–7 y reg6[2:0] = corriente o temporizador de carga. Con la cámara encendida Darwin nunca vuelve a
poner `a = 1`. Eso cuadra con lo medido el 17-11 (g85: encendida no carga) y con la documentación de Sony.

## 3. Cómo cargar de verdad con la cámara encendida (USB-CARGA-3, NO PROBADO)

La única vía es un **parche de Darwin**, con la misma cadena de parcheo ya probada en cámara en
[R84](e26-r84-darwin-v3-en-camara.md): `darwin_core.bin` + `darwin.sum` en un paquete de firmware. Requiere autorización de flasheo.

Parche mínimo propuesto: después de `0xc5bc` en la rama «`USB PWR`» de `0x71c4`, llamar a `0xc4e8(1, 0xc0, 4)`,
la misma configuración que usa el modo apagado. Al desconectar el USB, `0xc50a` ya corta la alimentación.

Antes de construirlo hace falta:
1. Confirmar el significado de los bits de reg5/reg6: por SWD, leyendo las sombras `0x20002b00..02` en modo apagado
   (cargando, carga terminada) y en encendido. El protocolo SWD está en R59/R84.
2. **Seguridad (riesgo real):** en modo apagado, la máquina `0x8744` supervisa la carga (estado de la batería
   `Batt ocv/ccv`, temperatura, fin de carga). Con la cámara encendida esa supervisión no corre y la batería está
   más caliente. El parche debe conservar el corte por temperatura y por fin de carga, o repetir la comprobación
   de esa máquina con la cámara encendida. Sin eso no se instala.
3. Potencia: un puerto de PC (SDP, 500 mA, 2,5 W) no basta para alimentar la cámara y además cargar. Hace falta un
   cargador DCP de 1,5–2 A (límite de reg4 = 3 o 4 según `0xc5bc`).

## 4. Lo que sí es inmediato: alimentación USB como la A6300 (USB-CARGA-1)

El kit ya hecho no carga la batería, pero puede dar la función de la A6300: la cámara funciona con energía del USB
y la batería apenas baja.

- `scripts/usb_carga/modulos.py`: módulos de la A6300 con las 4 llamadas GPIO de `usb_darwin.ko` anuladas (NOP y
  `R_ARM_NONE`). En la A6000 el pin de NVRAM `0xf90397/98` vale `ffffffff`. Test: `tests/test_usb_carga_modulos.py`.
- `scripts/usb_carga/prueba_camara.py`: telnet, `insmod` en `/tmp`, órdenes a `/proc/udm/usb_darwin`
  (`3` tipo, `4` límite, `5 04` 1500 mA) y registro del nivel de batería. **`orden E` no hace nada** (§0).
- Criterio: con el límite activo, el nivel baja claramente menos que en la línea base. No se probó porque la
  cámara no estaba en red. Aunque es INFERENCIA, Darwin ya pone «`USB PWR`» al encender si detecta USB (`0x71c4`):
  queda por medir si la A6000 de serie ya se alimenta del USB encendida y solo le falta un límite de entrada mayor.
