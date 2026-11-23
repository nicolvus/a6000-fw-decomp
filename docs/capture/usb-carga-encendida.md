# USB-CARGA — Carga por USB con la A6000 encendida (23-11-2026)

Petición del usuario: buscar una manera real de cargar la A6000 por USB con la cámara encendida.
Etiquetas: **VERIFICADO** (bytes/instrucciones) · **MEDIDO** · **INFERENCIA** · **NO PROBADO**.

## 1. Resultado

La A6000 tiene el hardware y casi todo el software de la carga USB encendida de la A6300; solo le faltan
**dos módulos de kernel** y un valor de NVRAM. El kit para probarlo en la cámara (sin flasheo ni NVRAM) está
hecho; la prueba real queda pendiente porque la cámara no estaba en red (`USB-CARGA-1`).

Trabajo previo: [g85](../gui/g85-plan-trazas-camara-vm.md) midió el 17-11-2026 que la A6000 encendida no carga
(«USB powered: false», el nivel baja); [S68](s68-battery-power.md) no encontró un modelo de carga en `av-cam.bin`
(la carga no vive ahí, ver §2).

## 2. Cadena de la carga (VERIFICADO salvo donde se indica)

| Eslabón | A6000 3.21 | A6300 2.01 |
|---|---|---|
| Cargador | IC5651 **OZ8072** «USB power management», I²C `USB_CHG_SDA/SCL` y `IC_5651_EN` al **MCU Darwin IC5700** (P57/SOT1, P58/SCK1, P24); `SUS` = `DWN_SUS` desde el SoC (manual de servicio, hoja de alimentación) | igual (mismo esquema de MCU) |
| Darwin | MFS1 en I²C a 400 kHz (tabla de canales `0x27b8c`: base `0x40038100`, `0x61a80`) | igual |
| RTOS `av-cam.bin` | Servicio OSAL `0x2804d3` registrado en `0x439884c4` (manejador `0x43b5ca2a`): `[0]=0/1` get/set, `[1]=1` tipo de adaptador (lee búfer Darwin `+0xfd`), `[1]=2` límite de corriente (`+0xfe`; set → orden Darwin `0x38` vía `0x43987b8c`, tabla de 0x3b ids) | mismo servicio |
| Kernel | **falta** `usb_darwin.ko` y `usb_buspwr.ko` | `usb_darwin.ko` («USB Darwin IF Driver» 0.9.0.0) y `usb_buspwr.ko` (1.0.3) |
| Userland | `libUsbBusPower.so` (iniciada por `libIMDB`) lee NVRAM `0x1210001` (tipo de cargador: 1–5 Maxim/SMB, **6 = `/usr/kmod/usb_darwin.ko`**) y `0x1210002` (conmutador) | igual, más `libUsbChargingApp.so` (menú «Alimentación USB») |
| NVRAM A6000 | `0x1210001 = 0`, `0x1210002 = 0` (sin driver), grupo `0x123` **sí configurado** (`0x1230000=1000`, `0x1230002=200`, `0x1230007=75`…), `0xf90397/98 = ffffffff` (volcado `updater-20261020-175427`) | — |

`usb_darwin.ko` habla con el servicio `0x2804d3` con exactamente ese protocolo (`osal_snd_sync_msg`, 8 B:
`{get/set, ítem, estado, …, valor}`), expone `usb_buspw_ic_*` (limitar a 100/500 mA, activar/desactivar carga,
suspender) y `/proc/udm/usb_darwin` (límite 0/100/500/900/1500/2000 mA, tipo SDP/CDP/DCP/Apple/Sony).

**Compatibilidad del módulo (VERIFICADO):** mismo `vermagic` (`3.0.27_nl-rt106 SMP preempt mod_unload ARMv7`),
`struct module` de `0x12c` B, sin `__versions`; los 54 símbolos importados existen en el kernel o en módulos de la
A6000. Las claves NVRAM que faltan (`0x123000b`, `0x920065`) caen en la rama de error con valor 0 sin abortar.

**Lo único que difiere:** el GPIO de `usb_darwin.ko` (puerto/bit de NVRAM `0xf90397/98`; INFERENCIA: `DWN_SUS`).
En la A6000 vale `ffffffff` y ningún binario lo usa, así que el kit neutraliza esas 4 llamadas (§3).

**NO PROBADO:** que el Darwin de la A6000 atienda la orden `0x38` y rellene `+0xfd/+0xfe`. Indicios a favor: el
RTOS de la A6000 trae el servicio completo, `libsencore` de ambos modelos lista las mismas órdenes Darwin
(`USB_CHG_IC_SET`, `LOG_BCHRG_*`) y la NVRAM de la A6000 trae la configuración `0x123`. La prueba lo decide en
un paso (§4, `orden 3`/`orden 4`).

## 3. Kit (offline, hecho)

- `scripts/usb_carga/modulos.py`: copia los dos módulos de la A6300 a `analysis/usb-carga/build/` (no versionado)
  y en `usb_darwin.ko` cambia cada `bl gpio_set_*` por NOP y su reubicación a `R_ARM_NONE` (el cargador de módulos
  de Sony la ignora, `arch/arm/kernel/module.c`). SHA-256: `usb_darwin.ko` `20b6de0b…13b5b2`,
  `usb_buspwr.ko` `ce7cbbbc…66b9ed`.
- `tests/test_usb_carga_modulos.py`: solo cambian esos 4 sitios (16 B de instrucción + 4 B de tipo).
- `scripts/usb_carga/prueba_camara.py`: subir, `insmod`, órdenes a `/proc/udm/usb_darwin`, vigilar el nivel
  (`dumpsys battery`) a CSV, `rmmod`. Todo en `/tmp` (tmpfs): apagar la cámara lo deshace.

## 4. Prueba en cámara (USB-CARGA-1)

Requisitos: cámara encendida con el Tweak (telnet), Wi-Fi en `A6000_HOST`, cargador USB de pared (DCP, ≥ 1,5 A)
y luego un puerto de PC. Cada paso es reversible apagando la cámara.

1. Línea base: `prueba_camara.py vigilar 20 base` con el cargador conectado y sin módulos.
2. `subir`, `cargar` (solo `usb_darwin`).
3. `orden 3` y `orden 4`: si el dmesg da un tipo válido (p. ej. DCP) y un límite, el Darwin de la A6000 implementa
   el canal → seguir. Si da «Fail to get…», el Darwin no lo implementa: parar (vía Darwin, §6).
4. `orden 5 04` (1500 mA) y `orden E`; `vigilar 20 carga`. Éxito = el nivel sube o baja claramente menos que en la
   línea base, con la misma pantalla y modo.
5. Repetir con el PC (SDP: el estándar limita a 500 mA) y `orden 5 02`.
6. Opcional: `cargar --buspwr` para la lógica de estados de la A6300.

## 5. Límites y riesgos

- Potencia: un puerto USB 2.0 da 2,5 W; con vista en vivo la cámara gasta del orden de eso (INFERENCIA), así que con
  PC lo esperable es frenar la descarga; cargar de verdad encendida pide un cargador DCP de 1,5–2 A.
- El OZ8072 y Darwin conservan sus protecciones de batería (temperatura, fin de carga); el kit no toca registros del
  cargador ni la NVRAM, solo pide límite y activación por la vía de Sony.
- Si `DWN_SUS` estuviera en suspensión por defecto en la A6000, el límite no surtiría efecto: habría que localizar ese
  pin del SoC y rellenar `0xf90397/98` (pendiente solo si el paso 4 falla con el canal Darwin vivo).

## 6. Siguiente fase (tras una prueba positiva)

Integración permanente (`USB-CARGA-2`, requiere autorización de flasheo): CFW con los dos módulos en `/usr/kmod` y
NVRAM `0x1210001 = 6`, para que la propia `libUsbBusPower` los cargue al arrancar. Si la prueba muestra el canal
Darwin muerto, la alternativa es un parche de Darwin (cadena de parcheo ya probada en
[R84](e26-r84-darwin-v3-en-camara.md)) que fije el límite del OZ8072 por I²C con la cámara encendida.
