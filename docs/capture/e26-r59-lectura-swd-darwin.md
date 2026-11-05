# E26-R59 — Lectura por SWD de Darwin (MCU FM3, IC5700): DESCARTADA (05-11-2026)

Fecha: 05-11-2026. **Resultado: sin respuesta del DAP; el usuario retiró los hilos y da la vía por descartada.** Procedimiento conservado como registro. Requiere autorización expresa del usuario para cada fase (CLAUDE.md). Solo lectura: no se usa ningún comando de escritura, borrado, desbloqueo ni reinicio.

Etiquetas: **ESQUEMA** · **LEÍDO** (R47) · **INFERENCIA** · **NO VERIFICADO**.

## 1. Por qué

R58 §6: `darwin_core` instalado = original; BK4 y firmware no contienen tiempos de cortina. Lo único por unidad que no hemos leído es la memoria de Darwin: arranque `0x0000-0x41ff` (no está en ningún paquete ni volcado, no se reescribe en las actualizaciones), flash de trabajo y SRAM (celdas `[0x20000050+canal]`, `[0x200002c0+canal]`, estructura `S`).

## 2. Qué se sabe

| Dato | Estado |
|---|---|
| Darwin = FM3 Cortex-M3 (IC5700), siempre alimentado desde la batería | ESQUEMA (E24-01) |
| Líneas de depuración de Darwin: `TCK_DWN`/`TMS_DWN` (SWCLK/SWDIO) en CN4906 pines 11/12, `TDO_DWN` pin 9, `TDI_DWN` pin 13, `TRST_DWN` pin 14, `XDWN_RESET` pin 8 (`NSRST`, directo a INITX; también pin 15 por R4917 XX), `MD0_DWN` pin 2 por R4927 XX, UART Darwin pines 6/7. Puntos de prueba en el lado MCU: CL704 (`TCK_DWN`), CL706 (`TMS_DWN`), CL701 (`XDWN_RESET`) | ESQUEMA (hoja 38 y hoja 23, revisadas en imagen 05-11; corrige pines 8/15 de R29) |
| Esos nodos 11/12 los comparten el SWD de BIONZ (por R4911/R4912) y Darwin (por R4915/R4916); **R4911, R4912, R4915, R4916 y CN4906 sin montar** | ESQUEMA + confirmado por el usuario 02-11 |
| Lógica ≈ 3,15 V | INFERENCIA |
| SWD de BIONZ ya funcionó con un hilo al pad del lado BIONZ de R4911/R4912 y una `debugprobe-zero` (RP2040) | LEÍDO (R47) |
| Si Darwin desactiva SWJ-DP o activa la protección de flash | **NO VERIFICADO** (E25-04) |

## 3. Plan

1. **Antes de nada, desconectar el hilo de BIONZ** de R4911/R4912: si no, no hay conflicto eléctrico (R4915/R4916 sin montar), pero se evita confundir los objetivos.
2. Hilos al **pad del lado Darwin** de R4915 (SWCLK) y R4916 (SWDIO), más masa común. Opcional: `TRST_DWN` (CN4906 pin 14) a un GPIO de la sonda para reiniciar solo el DP; **no tocar `XDWN_RESET` ni `MD0_DWN`** (entrarían al modo de escritura serie / reiniciarían Darwin).
3. Cámara con batería (apagada). Medir 3,0-3,3 V en ambos pads antes de conectar la sonda.
4. OpenOCD con `swd newdap` + `dap create` (como R47), 100 kHz, **sin `halt`** (parar Darwin en mitad de una transacción con BIONZ provoca temporizadores vencidos y posible `WDT`). Leer por AHB-AP con `apreg`, sin tocar `DHCSR`.
5. Primero solo DPIDR y IDR de los AP. Si el DAP no responde → parar y anotar (SWJ-DP deshabilitado o línea mal identificada).
6. Lecturas, en este orden, cada una con su hash:
   * `0x00000000-0x000041ff` (arranque, 16 896 B).
   * `0x00004200-0x0002665b` y comparar con `darwin_core.bin` (157 276 B): debe coincidir.
   * Resto de la flash principal (hasta el tamaño real del chip) y flash de trabajo (`0x00200000`, si existe).
   * SRAM `0x20000000-0x2000ffff`: celdas `0x20000050+canal`, `0x200002c0+canal`, `S = 0x200036d8`, tabla `0x20003818-0x20003848`.
7. Si una lectura de flash devuelve todo ceros/unos o falla de forma sistemática, **asumir protección de flash activa y detenerse**.

## 4. Prohibido

Escrituras, `flash write/erase`, **cualquier comando de desbloqueo o borrado total de seguridad** (destruiría el arranque y los datos y dejaría Darwin sin firmware), `reset`/`halt`, entrada en modo de escritura serie. Un FM3 protegido solo se «desbloquea» borrándolo: no hacerlo.

## 5. Qué decidirá

| Hallazgo | Consecuencia |
|---|---|
| Arranque/flash de trabajo con datos por unidad (tablas, offsets de cortina) | Comparar con otra A6000 si existe; probar si falta o difiere respecto de un Darwin sano |
| Celdas `[0x20000050+canal]` con valores | Cierra el origen del tipo de mecanismo (rea-tema3 §3) |
| Todo coincide con lo esperado | Descarta Darwin; queda el hardware del obturador (R58 §6) |
| Flash protegida / DAP cerrado | Cierra la vía; queda la prueba eléctrica y la medida del obturador |

## 6. Orden recomendado (de menor a mayor invasividad)

1. Prueba eléctrica a 1/1000 (batería nueva original, adaptador de CA, frío/calor): no abre la cámara.
2. Restauración de NVRAM sin reiniciar y volcado (R58 §1).
3. Esta lectura SWD de Darwin.

## 7. Primer intento físico (05-11-2026)

| Hecho | Estado |
|---|---|
| Hilos en el lado Darwin de R4915/R4916: 3,10 V cada uno con la cámara encendida; `NSRST` (pin 8 = `XDWN_RESET`) 3,09 V | MEDIDO (usuario) |
| Dos RP2040 intercambiadas: ambas leen el BIONZ, ninguna lee Darwin (sin DPIDR) | MEDIDO (usuario) |
| `darwin_core` no reconfigura P00–P04 salvo en el grupo de pines 6: tabla `0x25bfc`, grupos 0–5 con `40/01/001f` = modo 8 de `0x55d0` (`0x567c`: PFR=1, PCR=1) → función JTAG/SWD con pull-up, coherente con los 3,10 V. El grupo 6 los pone como salida GPIO a 0 (`08/00/4a7f`). No hay literal de `EPFR00` (`0x40033600`) | LEÍDO (bytes) |
| `darwin_core` entra en bajo consumo con `SCR.SLEEPDEEP` + `wfi` (`0x516c–0x5182`, `0x83f6–0x8402`, `0x8436–0x8442`); el manual FM3 dice que en TIMER/RTC/STOP/deep standby la función de depuración se detiene | LEÍDO (bytes + manual) |
| Que Darwin esté en esos modos con la cámara encendida, y qué selecciona el grupo 6 | **NO VERIFICADO** |

Hipótesis principal: Darwin pasa la mayor parte del tiempo en STOP/TIMER y el DAP no contesta. Prueba siguiente (solo lectura, sin reset): repetir la lectura de DPIDR en bucle mientras se generan eventos (botones, encendido) para cazar a Darwin despierto.

**Lectura rápida (05-11, 18:37–18:39):** CMSIS-DAP crudo (line reset + JTAG→SWD + lectura de DPIDR, ~1000 intentos/s por sonda, 1 MHz, sin escrituras). BIONZ: `0x3ba02477` estable de 18:38:10 a 18:39:03 (cámara encendida, ~50 000 lecturas). Darwin: **ninguna respuesta en todo el intervalo**, ni siquiera ruido; SWDIO nunca devuelve ACK. Con muestreo cada ~1 ms, la hipótesis de despertares cortos queda **muy debilitada**. Abiertos: TCK/TMS intercambiados en la soldadura, continuidad pad↔bola del MCU, protección de flash/depuración del MB9AF004 (manual de flash ausente).

## 8. Vía BIONZ: ver el tráfico con Darwin por el SWD del BIONZ (05-11-2026)

Herramientas en `analysis/e26-r59/`: `dpidr_fast.py` (DPIDR en bucle, CMSIS-DAP crudo) y `bz_mon.py` (vigila regiones de la DRAM del BIONZ por AHB-AP a ~70 barridos/s; solo escribe registros de depuración, sin halt). Paquete CMSIS-DAP de la `debugprobe-zero`: 64 B (bloques de 15 palabras).

Captura `bz_mon_20261105_1846.log` (firmware instalado según R58: `darwin_core` original), regiones `0x83f91e20` (+0x110, envío BIONZ→Darwin, paquete en `0x83f91e32`) y `0x83e77280` (+0x40). MEDIDO:

| Hora | Cambio en el paquete (`pkt[i]` = byte en `0x83f91e32+i`) |
|---|---|
| 18:47:07 | aparece: `pkt[1]=0x02`, `pkt[2..3]=00 1b`, `pkt[5]=0x10`, `pkt[0xa..0xd]=53 0e 00 40`, `pkt[0x13]=0x90` |
| 18:47:16 | `pkt[3]` 0x1b → 0x1c; 18:47:47 `pkt[2..3]` → `80 17` |
| 18:47:21 | `pkt[7]=0x01`, `pkt[8]=0x5a`, `pkt[0xc]=0x01`, **`pkt[0x0e]=0xff`** (valor de Sony, R56) |
| 18:47:31 | `pkt[8]=0xa6`; 18:47:35 vuelve a reposo (`pkt[7]=0x1a`, `pkt[0x0e]=0`) |
| 18:47:59 | `pkt[7]=0x02`, `pkt[0xc]=0x02`, `pkt[0x0e]` 5 → 4 → 3 en ~130 ms |
| 18:48:26 | todo a cero; después el AP0 devuelve WAIT (cámara apagándose) |

En `0x83e77284` el byte 0 alterna 0x13–0x16 y `0x83e77290` toma y suelta `0x43b1f0d3` (dirección de código de av-cam) en 15–30 ms. **NO VERIFICADO:** qué acción del usuario corresponde a cada hora, la semántica de `pkt[7]`, `pkt[8]`, `pkt[0xc]` y de la cuenta 5→3, y si `0x83e77280` es el buzón de recepción o un objeto temporizador. No da acceso a la RAM ni a la flash de Darwin.

## 7. Resultado (05-11-2026, MEDIDO, solo lectura)

* Con los hilos en el lado Darwin de R4915/R4916 (esquema y placa comprobados por el usuario), 3,09-3,10 V en TCK/TMS y 3,10 V en `TRST_DWN`, masa común, cámara encendida y hilos en ambas orientaciones: **0 respuestas** a 50, 100, 200 y 400 kHz (más de 150 intentos). OpenOCD: `SWD ack not OK @ 0 JUNK` en cada lectura de DPIDR.
* Descartado: velocidad, tensión, masa, cruce de hilos, `TRSTX` en bajo. No se llegó a medir `XDWN_RESET` (`CL701`) ni se probó la conexión bajo reset.
* Causa no determinada: Darwin dormido, SWJ-DP desactivado por su arranque `0x0000-0x41ff` o protección. La vía se da por cerrada por decisión del usuario.

