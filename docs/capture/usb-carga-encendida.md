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
con la cámara encendida la corta **Darwin**. Se puede reactivar sin parche, con la orden de ajuste
`USB_CHG_IC_SET` (§3.1), o con un parche de Darwin (§3.2).

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
| `0xc8bc(buf)` | Guarda 3 B en `0x20002af9..afb` y los aplica con `0xc660` si el indicador `[0x20000029]` vale 0 (`0xcf14(9)`); si no, los aplica la tarea `0x7a36` del modo encendido en cada ciclo (`0xc6dc`). La llama el despachador de órdenes de BIONZ (`0x243a4`, caso `0xa0`, desde `0x245dc`) |
| `0xc6f0` | Informa a BIONZ del límite: código de reg4 → 0 = 100, 1 = 500, 2 = 1500, 3 = 900, 4 = 2000 mA (la enumeración de `usb_darwin.ko`) |

Llamadas a `0xc4e8` (barrido de todo `darwin_core.bin`):

| Sitio | Argumentos | Contexto |
|---|---|---|
| `0x8792` (máquina `0x8744..`) | `(1,0xc0,4)`, `(1,0x80,4)`, `(1,0xc0,0)`, `(2,0x80,0)` | modo apagado: carga |
| `0x85cc` | `(2,0,0)` | modo apagado: corte |
| `0x8c64` («`Off exit`», `0x8c42`) | `(2,0,?)` | **al encender la cámara: carga cortada** |

Semántica (los nombres salen de los mensajes de error de `0xc660`): reg4[2:0] = **límite de entrada** («`CUR LIMIT`»,
VERIFICADO por la traducción de `0xc6f0`); reg5 = «`BST_EN`» y bits de modo; reg6[2:0] = «`Wakeup Charge`».
INFERENCIA (la hoja de datos del OZ8072 no es pública): la carga activa del modo apagado es reg5 = `…|1|0xc0`,
reg6 = 4; al encender, «Off exit» deja reg5 = `…|2`, bits 6–7 = 0 y reg6 = 0, y ninguna rutina del modo encendido
vuelve a ponerlos. Eso cuadra con lo medido el 17-11 (g85: encendida no carga) y con la documentación de Sony.

## 3. Cómo cargar de verdad con la cámara encendida (USB-CARGA-3, NO PROBADO)

### 3.1 Vía sin parche: la orden `USB_CHG_IC_SET` (VERIFICADO en estático)

Sony dejó una orden de ajuste que escribe los tres registros desde fuera de Darwin, y funciona con la cámara encendida.

| Eslabón | Evidencia |
|---|---|
| Tabla de órdenes de `libsencore.so` y de `/bin/adjstctl.elf` | `be 04 28 00 20 0d a0 40 "USB_CHG_IC_SET"` = {mensaje OSAL `0x2804be`, bloque `0x0d20`, código `0xa0`}. Formato comprobado con `TERM_MODE` = (`0x601`, `0x1f`), igual que en pmca |
| av-cam | `0x2804be` registrado en `0x439883e6`; su manejador `0x4398886c` es el reenvío genérico de órdenes senser a Darwin |
| Darwin | El marco BIONZ→Darwin (`0x200032cc`, parser `0x11e06`) lleva en `+0x22` el canal de órdenes. `0x1b8cc` exige el tipo `0x0040`, una secuencia nueva y `0x20` (escribir; el bloque `0x0d20`), copia 8 B y llama al despachador `0x243a4`. Por emulación con Unicorn, **solo la orden `0xa0` llega a `0xc8bc`** |
| Aplicación | `0xc8bc` → `0xc660`: reg4 = `(reg4 & 0xf8)|d0`, reg5 = `(reg5 & 0x30)|d1`, reg6 = `(reg6 & 0xf8)|d2`, al momento o en el siguiente ciclo de la tarea `0x7a36` (encendido) |

Herramienta: `scripts/usb_carga/chg_ic_set.py` (test `tests/test_usb_chg_ic_set.py`). Por defecto solo simula. Con
`--execute`, entra en el modo de servicio por USB (como `scripts/senser_*`) y manda `AdjustControl(0x0d20, 0xa0, d)`.
- `carga --ma N`: d = {código de N mA, `0xc9`, 4}. Repite la configuración de carga del modo apagado,
  `0xc4e8(1,0xc0,4)`, y mantiene el bit 3 de reg5 (el USB alimenta el sistema).
- `normal`: d = {0, `0x0a`, 0}. Deja el cargador como «Off exit», es decir, como queda al encender.
- Desde la propia cámara (telnet) la orden equivalente sería `adjstctl 0xd20 0xa0 …`. `adjstctl` lee el bloque y el
  código como dos identificadores (`cmdline_get_id`) y luego los datos, pero el formato exacto de los datos no está
  verificado: primero hay que ejecutarlo sin argumentos para ver su ayuda.

Límites de la vía sin parche:
1. **Seguridad (riesgo real):** con la cámara encendida, Darwin no ejecuta la máquina de carga del modo apagado
   (`0x8908`→`0x8692`→`0xbb2e`, una cadena de una docena de comprobaciones: batería, autenticación, tiempos y
   probablemente temperatura). El OZ8072 no tiene entrada de termistor en el esquema (`BATT_TEMP` va a IC5700), así
   que **nadie corta por temperatura**. Uso solo vigilado, con la cámara fresca, y `normal` al terminar.
2. Potencia: un puerto USB 2.0 de PC (500 mA, 2,5 W) apenas cubre el consumo de la cámara. Con un USB 3.0 (900 mA)
   o un cargador DCP de 1,5–2 A sobra margen para cargar. El canal senser exige que la cámara esté conectada al PC;
   con un cargador de pared la vía es `adjstctl` por telnet.
3. Que el bit 0 de reg5 con la cámara encendida no provoque un apagón no está verificado. Si lo provocara, la cámara
   se apagaría y el modo apagado reescribiría los registros: no es destructivo.

### 3.2 Vía permanente: parche de Darwin (sin construir)

Con la cadena de parcheo ya probada en cámara ([R84](e26-r84-darwin-v3-en-camara.md)), en la tarea `0x7a36` del
modo encendido se cambiaría la llamada `bl 0xc6dc` (`0x7aa6`) por una rutina en una cueva de código. La rutina,
cuando hay USB (`0xc626`), decidiría la carga con las mismas comprobaciones del modo apagado (`0xbb2e`) y aplicaría
`0xc4e8`. No se construye hasta medir la vía 3.1: `0xbb2e` y `0x8692` tienen efectos secundarios (temporizadores,
LED, `0x118b2` «PwrCtrl», `0x14e92`) cuyo comportamiento con la cámara encendida no está analizado.

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

## 5. Prueba en cámara (23-11-2026, autorizada por el usuario; MEDIDO)

Cámara encendida con el firmware 3.21 de serie, unida al PC por un concentrador USB 2.0 (480M), con telnet en
`192.168.1.30`. Datos en `analysis/camera-dumps/20261123-usb-carga-senser/` (no versionados).

| Paso | Resultado |
|---|---|
| Canal senser, solo lectura | `BATT_V` (`0x0d01/0x10`) devuelve 1 B (AD de la batería, `0xca`); `IB_SYSINF` 0, `ACV_V` 0, `IBCHECK` 1. `IB_TEMPERATURE`, `GeneralAD`, `SystemAD`, `DD_BATCHG_GET` y `BattInfoSW` dan error 128/136: **no hay temperatura por este canal** |
| `USB_CHG_IC_SET carga` 500 mA en modo servicio (8 min) | Darwin acepta (eco `01 c9 04 …`) y la cámara sigue estable. `BATT_V` `0xc9` → `0xcb` y luego oscila `c9–cb`; nivel real 60 → 58 % en ~12 min (base + carga): **sin carga neta** |
| `carga` 900 mA y salida del modo servicio (20 min, nivel por telnet) | 58 → **60 %** a los 3 min y **60 % fijo** 17 min. No basta: con el bit 3 de reg5 el USB también alimenta la cámara, y la meseta puede ser solo alimentación USB. Falta el control con `normal` |
| Final | El último cambio a modo servicio dejó la cámara sin USB (no vuelve a enumerarse; telnet sigue). `normal` se restauró por telnet con `adjstctl.elf 0xd20 0xa0 b:0x00 b:0x0a b:0x00 b:0 …` (eco y `rc=0`): **la vía por telnet funciona** |

Uso medido de `adjstctl.elf`: `adjstctl.elf <opciones> [bloque] [código] [tamaño]:[dato] …` (tamaño `b|w|d|n`).

Siguiente paso (`scripts/usb_carga/prueba_telnet.py`, todo por telnet y sin modo servicio): con la cámara en USB
(mejor un cargador de pared), 20 min de `normal` como control y 40 min de `carga` con el mismo límite. Hay carga
real si con `carga` el nivel **sube** o cae claramente menos que en el control.
