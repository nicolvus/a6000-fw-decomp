# E26-R59 — Lectura por SWD de Darwin (MCU FM3, IC5700): objetivo y procedimiento (BORRADOR, sin ejecutar)

Fecha: 05-11-2026. **Ninguna conexión hecha.** Requiere autorización expresa del usuario para cada fase (CLAUDE.md). Solo lectura: no se usa ningún comando de escritura, borrado, desbloqueo ni reinicio.

Etiquetas: **ESQUEMA** · **LEÍDO** (R47) · **INFERENCIA** · **NO VERIFICADO**.

## 1. Por qué

R58 §6: `darwin_core` instalado = original; BK4 y firmware no contienen tiempos de cortina. Lo único por unidad que no hemos leído es la memoria de Darwin: arranque `0x0000-0x41ff` (no está en ningún paquete ni volcado, no se reescribe en las actualizaciones), flash de trabajo y SRAM (celdas `[0x20000050+canal]`, `[0x200002c0+canal]`, estructura `S`).

## 2. Qué se sabe

| Dato | Estado |
|---|---|
| Darwin = FM3 Cortex-M3 (IC5700), siempre alimentado desde la batería | ESQUEMA (E24-01) |
| Líneas de depuración de Darwin: `TCK_DWN`/`TMS_DWN` (SWCLK/SWDIO) en CN4906 pines 11/12, `TDO_DWN` pin 9, `TDI_DWN` pin 13, `TRST_DWN` pin 14, `XDWN_RESET` pin 15, `MD0_DWN` pin 8, UART Darwin pines 6/7 | ESQUEMA (R29) |
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
