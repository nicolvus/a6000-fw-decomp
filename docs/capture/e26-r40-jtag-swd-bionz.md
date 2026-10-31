# E26-R40 — JTAG/SWD del BIONZ como vía de escritura: qué permite el estático, qué exige lo físico

Fecha: 31-10-2026. Continúa [R39](e26-r39-estatico-profundo.md). **Solo análisis offline** del árbol GPL de Sony (`analysis/session18`), de `bootloader.bin`/`bootrom.bin` y del kernel del actualizador (`nflasha1`). Sin cámara, sin sondas, sin escritura. Pedido del usuario: analizar la alternativa JTAG/SWD propuesta como vía 3 para escribir `\updater\mode` sin lector NAND externo (R39 §3).

Etiquetas: **BINARIO** (bytes releídos) · **FUENTE** (GPL de Sony) · **DATOS** (manual de servicio) · **INFERENCIA**. Pruebas: [`tests/test_e26_r40_jtag_swd.py`](../../tests/test_e26_r40_jtag_swd.py) (8).

## 1. Resumen

| Pregunta | Resultado |
|---|---|
| ¿Hay un puerto de depuración documentado para el BIONZ? | **Sí, dos, ya descritos en R5/R6/R29.** El JTAG convencional (TDI/TCK/TMS) está atado a alimentación y no sirve. El **SWD** (`SWCLK` W25, `SWDIO` W26) sí llega al conector de servicio CN4906 (pines 11/12), a través de R4911/R4912, que el esquema marca sin montar (`XX`) |
| ¿El software bloquea la depuración? | **No se encontró ningún bloqueo.** Ningún cargador (BootROM, Loader2, Loader3, ARM7) toca el DAP CoreSight (`0xf2710000`). El kernel del actualizador solo lo usa para enmascarar una IRQ de la PMU, con la secuencia de desbloqueo estándar de ARM (`0xC5ACCE55`) |
| ¿El silicio está preparado para depurarse así? | **Sí, de fábrica.** Hay `defconfig` de Sony (`cxd90014_ice_*`) que arrancan el kernel directamente por un depurador en circuito (ICE), con el núcleo y el `initrd` en direcciones fijas de RAM, sin pasar por `nflasha1` |
| ¿Queda ventana de tiempo para conectar tras el fallo? | **Sí, indefinida.** Tras el código −302, Loader3 entra en un bucle de parpadeo **sin apagarse**: ningún `wfi` ni apagado, solo un salto incondicional hacia atrás. La CPU sigue encendida y ejecutando hasta que se corte la alimentación |
| ¿Qué falta para saber si sirve? | **Todo físico.** Si R4911/R4912 están montadas en esta unidad, su tensión real, y sobre todo si los **eFuses** de seguridad (visibles en el esquema como `FUSE_EN`/`FUSE_CLK`, junto al bloque JTAG) deshabilitan la depuración en las unidades de serie. Eso no está en ningún binario volcado: el controlador de eFuse no aparece en el árbol GPL ni en el BootROM leído |

**Conclusión:** JTAG/SWD no añade una vía nueva sobre lo que R5/R6/R29 ya habían dejado como «posible en esquema, no demostrado». Lo que aporta esta sesión es que **nada en el software descarta la vía**, y que hay una ventana de tiempo sin presión tras el fallo. Sigue siendo indistinguible de «bloqueado por fusible» sin una prueba física.

## 2. El DAP CoreSight de la SoC (FUENTE, GPL de Sony)

`arch/arm/mach-cxd90014/include/mach/regs-dap.h` y `platform.h`:

```c
#define CXD90014_DAP_BASE   0xf2710000
#define N_DAP_CTI           4
#define DAP_CTI(x)          (0x8000 + 0x1000*(x))   /* CTI 0..3 en 0xf2718000..0xf271b000 */
#define DAP_CTILOCK         0xfb0
#define DAP_CTI_UNLOCK      0xc5acce55               /* valor de desbloqueo estándar de ARM CoreSight */
```

`dap.c` es el único archivo del árbol que toca este bloque, y solo para un uso: desenmascarar la IRQ de la PMU por el canal CTI de cada CPU (`DAP_CTICH_PMUIRQ`), sin relación con JTAG/SWD en sí. El literal `0xC5ACCE55` aparece **una sola vez** en el kernel, exactamente en ese archivo.

**Lectura:** el DAP es el bloque de depuración CoreSight estándar de un núcleo ARM Cortex-A (CTI = Cross-Trigger Interface, parte del mismo complejo de depuración que expone el puerto SWD/JTAG). Que el kernel lo use para algo tan trivial como una IRQ, sin ninguna comprobación de permiso antes, es consistente con que el bloque **no está bajo ningún candado de software** desde Linux.

## 3. Nadie, antes de Linux, escribe ni lee el DAP (BINARIO)

Barrido de literales de 32 bits en el rango `0xf2710000`–`0xf271ffff`:

| Código | Literales en el rango del DAP |
|---|---|
| BootROM (`bootrom.bin`) | 0 |
| Loader2 (`bootloader.bin[0x600:0x7200]`) | 0 |
| Loader3 (`bootloader.bin[0x22800:0x38000]`) | 0 |
| ARM7 (`bootloader.bin[0x18800:0x1c000]`) | 0 |

Ninguna de las cuatro etapas que se ejecutan antes de Linux inicializa, bloquea ni consulta el DAP. Si hubiera una comprobación de depuración por software (frecuente en otros SoC: leer un bit de eFuse y, si está puesto, deshabilitar el DAP o resetearlo), tendría que acceder a este rango o al controlador de eFuse, y ninguno de los dos aparece.

## 4. El kernel del actualizador no bloquea nada, solo lo usa (BINARIO)

Mismo barrido sobre el `vmlinux.bin` descomprimido de `nflasha1` (actualizador 3.21, kernel `3.0.27_nl-rt106`, R39 §4): los únicos literales en el rango coinciden con los desplazamientos de `dap.c` dentro del primer CTI (`DAP_CTI(0) = 0xf2718000`): `CTIINTACK` (`+0x10`), `CTIGATE` (`+0x140`) y `CTILOCK` (`+0xfb0`). No hay ninguna escritura que **apague** o **bloquee** el DAP; solo la secuencia de desbloqueo que cualquier controlador CoreSight necesita para tocar sus propios registros de IRQ.

## 5. El silicio está pensado para depurarse así (FUENTE)

El árbol de `arch/arm/configs/` de Sony trae, junto a los `defconfig` de producción, una familia `cxd90014_ice_*` (`ice_initrd`, `ice_nfs`). Frente al `defconfig` de producción:

- `CONFIG_CMDLINE_FROM_BOOTLOADER` se sustituye por una línea de arranque **fija**, con `root=/dev/ram0 initrd=0x81000000,0x1400000` y direcciones de memoria explícitas (`memrsv=…`, `klog.addr=…`).
- No activa ni desactiva `CONFIG_ARM_DAP` de forma distinta a producción (está en ambos salvo una variante concreta, sin relación con seguridad).

Esto es exactamente lo que se necesita para arrancar un kernel **cargado por el propio depurador** en RAM, sin pasar por el BootROM/Loader2/Loader3/`nflasha1`: así depuraba Sony el chip en fábrica. No es una vía «distinta» a escribir `\updater\mode`: si funcionara, dejaría obsoleta la necesidad del byte, porque se podría cargar el kernel del actualizador directamente en RAM y saltar a él.

## 6. Tras el fallo, la CPU no se apaga (BINARIO)

`c01f3bf6: b #0xc01f3bc8` (bytes `e7 e7`) es un salto Thumb incondicional **hacia atrás**, dentro del bucle de parpadeo de LED de `c01f3b74` (documentado en [R13](e26-r13-led-error-provenance.md)). No hay ninguna instrucción `wfi`, `halt` ni llamada a apagado en todo el cuerpo del bucle: sondea la UART (`c01f379a`), parpadea y vuelve a empezar. **La CPU sigue encendida y ejecutando** hasta que se retire la batería o se desconecte la fuente. Para un intento de conexión SWD, esto da una ventana sin presión de tiempo (a diferencia de, por ejemplo, el bucle de 30 min del actualizador, R39 §5).

## 7. Qué sigue siendo desconocido (límite real)

- **Población física.** R4911/R4912 y la propia huella de CN4906 figuran «XX» en el esquema (R5 §4, R11 §3.4). Sin foto ni continuidad medida, no se sabe si esta unidad las tiene soldadas.
- **eFuses de seguridad.** El esquema sitúa `FUSE_EN`/`FUSE_CLK`/eFuse justo junto al bloque JTAG/SWD (manual de servicio, bloque de `AB22`–`N29`). Qué fusible lee el controlador de depuración, y si está programado para desactivarla en unidades de producción, es una decisión de diseño de ARM/Sony que **no está en ningún binario accesible**: el controlador de eFuse no aparece en el árbol GPL (ni Linux lo necesita) ni en el BootROM volcado. Es la misma situación que la clave de `nflasha0` (R33): la respuesta vive en una zona que nunca se ha leído.
- **AP/protocolo expuesto.** Aun con el puerto físicamente accesible y sin fusible, falta identificar qué Access Port expone (de memoria, de depuración de núcleo), si permite detener la CPU y leer/escribir RAM, y sobre todo si eso basta para ejecutar código que use MuMin (R39 §2) para escribir el byte de `\updater\mode` — la primitiva de almacenamiento sigue siendo la de R39, no una nueva.

## 8. Relación con las vías ya propuestas

- No sustituye a la vía serie del BootROM (R33): esa necesita una clave en `nflasha0` que tampoco se ha leído, pero es *la* vía que el propio fabricante deja accesible sin abrir el eFuse de depuración.
- Si SWD estuviera abierto, sería **más directo** que la vía serie: no hace falta clave, y permite cargar y ejecutar código arbitrario (como el kernel `ice_*`) en vez de depender del protocolo cerrado del BootROM.
- Comparte con la clave de `nflasha0` (R39 §7) el mismo tipo de límite: ambas dependen de un dato que solo una prueba física revela, y en ambos casos la pregunta es «¿lo dejó Sony abierto en esta unidad?», no algo que el código resuelva.

## 9. Límites de esta sesión

- No se ha ejecutado ninguna sonda ni se ha medido continuidad, tensión ni fusible alguno.
- No se ha identificado el controlador de eFuse en ningún binario disponible.
- Nada de lo anterior autoriza una conexión física.
