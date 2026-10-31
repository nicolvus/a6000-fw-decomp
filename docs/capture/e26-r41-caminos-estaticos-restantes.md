# E26-R41 — Verificación de los caminos estáticos restantes: consola serie de Loader3 y espera de ICE

Fecha: 31-10-2026. Continúa [R40](e26-r40-jtag-swd-bionz.md). **Solo análisis offline** de `bootloader.bin` (volcado del 20-10) y de los 12 volcados BK4. Sin cámara, sin escritura. Pedido del usuario: «verifica los caminos estáticos faltantes por descubrir».

Etiquetas: **BINARIO** (bytes releídos con Capstone) · **DATOS** (Backup) · **INFERENCIA**. Pruebas: [`tests/test_e26_r41_consola_loader3.py`](../../tests/test_e26_r41_consola_loader3.py) (4).

## 1. Resumen

| # | Camino revisado | Resultado |
|---|---|---|
| 1 | Funciones del bucle de LED tras −302 que R7 dejó «no examinadas» (`c01f3884`, `c01f5008`, `c01f379a`, `c01f6d18`, `c01f4f88`) | **Examinadas.** `c01f379a` no es un «sondeo UART» genérico (R13/R40): es una **consola de comandos serie** con dos órdenes, `beast` y `ldump`. El bucle reinicializa la UART en cada fallo (`c01f5008`) |
| 2 | ¿La consola da una vía de escritura? | **No.** `ldump <dir> <tamaño> [1\|2\|4]` solo lee memoria (`ldrb/ldrh/ldr`); `beast` vuelca el buffer de log de RAM. No hay orden de escritura, salto ni carga. Loader2 trae la misma consola (mismas dos órdenes) |
| 3 | ¿Sirve al menos para leer (p. ej. la clave en `0xc0001200`)? | **No con el Backup de fábrica.** `Backup[0x510015]=0` pone a 0 el nivel UART (`[0xc0060000]`) y la bandera de `beast` (`[0xc0060014]`): `ldump` escribe solo en el buffer de RAM y `beast` sale sin imprimir. La consola recibe, pero no contesta |
| 4 | Modo **«CFG:Wait ICE»** de Loader3 (nuevo) | `c01f48cc`, llamado en `c01f0cc2`, **antes** de la etapa que da −302. Si el GPIO que indica el Backup (`0xf90449` = banco **14**, `0xf9044a` = bit **17**; 12/12 volcados) lee 0, Loader3 inicializa la UART, limpia la caché y espera a que un depurador escriba `[0xc0045804] ≠ 0`. Confirma el diseño para ICE de R40, pero exige el depurador: no es una vía nueva |
| 5 | Resto de pendientes estáticos | Sin cambios: `E26-R30-HOSTRET0` (baja, no cambia la decisión), `E26-R5-FM3` (falta el manual de flash del MB9AF004B; solo está el de periféricos), cola INFO6 de Loader3 (no está en ningún volcado) |

**Conclusión:** no queda ningún camino estático sin examinar en la cadena BootROM → Loader2 → Loader3 que dé escritura en la NAND sin acceso físico. El último trozo sin examinar del bucle de error era una consola de solo lectura, muda con la configuración de fábrica. Se mantiene la conclusión de R37–R40: lo que falta es físico.

## 2. La consola serie de Loader3 (BINARIO)

`c01f379a` (234 B, R25 la nombró `log_ld3_w` por su cadena):

- Lee caracteres mientras `c01f508e` (bit RXFE de `UARTFR`, `+0x18`) indique datos, con `c01f50a4` (`UARTDR`). Los guarda en `0xc00e06ac` con índice global en `0xc00e0030` (máximo 30; el índice persiste entre llamadas).
- Con `\r` compara los 5 primeros bytes con `beast` (`c01f38d0`) y `ldump` (`c01f38d8`) mediante `c020c224` (**INFERENCIA:** `strncmp`; está en la parte de Loader3 que no se volcó, INFO6).
- `beast` → `c01f376e`: si `[0xc0060014] ≠ 0`, escribe por la UART (`c01f505a`, directo a `UARTDR`) el buffer de log `0xc006001c…[0xc0060008]`.
- `ldump` → tres `c020c0b8` (**INFERENCIA:** `strtoul(…, base 0)`): dirección, tamaño (`1…0x10000`) y orden opcional (1, 2 o 4). Errores: `LD3_W:invalid address`, `size is out of range`, `invalid order`. Luego `c01f3670(2, "LD3:\nMEM_DUMP …")` y `c01f3708`, que recorre la zona con `ldrb/ldrh/ldr [r4]` y la imprime con `c01f3670` de nivel 2. **Ninguna instrucción `str` sobre la dirección pedida.**

Bucle de LED (`c01f3b74`): `c01f3bb4: bl c01f3884` (devuelve `[0xc006000c]`, índice de UART) → `c01f3bb8: bl c01f5008` → en cada ciclo `c01f3bc8: bl c01f379a`, y luego el parpadeo.

`c01f5008(n)`, solo si `n ∈ {0, 1}`: guarda `n` en `[0xc006000c]`, configura el pinmux (`0xf2910238`, `0xf2912204`) y programa una UART tipo PL011 en `0xf2000000 + n·0x1000`: `IBRD = 0x1a`, `FBRD = 3`, `LCRH = 0x70` (8N1, FIFO), `CR = 0x701` (UART, TX y RX activos). **INFERENCIA:** con reloj de 48 MHz da 115 200 baudios.

**Corrección de [R37](e26-r37-cierre-estatico-recuperacion.md) §4:** «el registro de la UART no se inicializa (`c01f5008` no se llama)» vale para el inicio del logger (`c01f35c0`), no para todo Loader3. El bucle de error (`c01f3bb8`) y la espera de ICE (`c01f48e6`) sí llaman a `c01f5008` con `[0xc006000c]`, cuyo valor con la consola apagada no se fija en Loader3 (**INFERENCIA:** heredado de Loader2 o del valor inicial de la SRAM). La conclusión de R37 no cambia: una UART pasiva no muestra nada.

**Corrección de [R13](e26-r13-led-error-provenance.md) (HIPÓTESIS «consume UART») y de [R40](e26-r40-jtag-swd-bionz.md) §6 («sondea la UART»):** es una consola de comandos, no un simple sondeo. La conclusión de R40 (la CPU no se apaga) no cambia.

## 3. Por qué la consola no contesta (BINARIO + DATOS)

`c01f35c0` (inicio del logger): si `c01f4edc` (Backup `0x510015 == 1`) devuelve 0, salta a `c01f3638`: `[+0x14] = 0`, `[+0x18] = 0`, `[+0] = 0`. Luego fija `[+4] = Backup[0x510006]` y `[+0x10] = Backup[0x510025]`.

`c01f3670(nivel, …)` imprime por la UART solo si `[0xc0060000] ≥ nivel`. Con 0 no imprime nada: ni el `ERROR: Blinking LED[…]` (nivel 1) ni el `MEM_DUMP` (nivel 2). Al buffer de RAM sí van, porque `[+4] = 6`.

**DATOS (12 volcados BK4):** `0x510015 = 00`, `0x510003 = 00`, `0x510006 = 06`, `0x510025 = 0`. Así, `beast` sale sin imprimir y `ldump` solo añade texto al buffer de RAM. Leer ese buffer exigiría un depurador, el mismo medio que R40.

## 4. Espera de ICE (BINARIO + DATOS)

- `c01f0cc2: bl c01f48cc`, justo antes de `c01f0cca` (inicio, BOS y `nflasha2`, donde nace el −302 de R13 §3).
- `c01f48cc` → `c01f4828` (pone a cero `0xc0045804…0xc0045818`) → `c01f488a`: lee Backup `0xf90449` (banco) y `0xf9044a` (bit). Si ninguno es `0xffffffff`, lee `0xf2910000 + banco·0x100 + 0x10` (datos de entrada del GPIO) y devuelve 1 si el bit está a **0**.
- Si devuelve 1: `CFG:Wait ICE` → `c01f3884`/`c01f5008` (UART) → `c01f025c` (limpieza de la caché D por conjunto/vía, ARM) → `c01f4852`: bucle que llama a la consola y espera `[0xc0045804] ≠ 0`. Después salta a `c020e0d8`, en la parte no volcada (INFO6).
- **DATOS:** banco 14, bit 17 en los 12 volcados. La cámara arrancaba con normalidad, así que ese GPIO está a 1 en uso normal (**INFERENCIA**). En el manual de servicio no se ha identificado qué bola o red es el GPIO 14.17 (aparece `GPIO_14 AC22`, pero no está demostrado que sea la misma numeración).

**Lectura:** Sony detiene Loader3 por una línea GPIO para que el depurador cargue o parchee la RAM. Refuerza R40 (silicio pensado para ICE). Para usarlo hace falta igualmente el SWD abierto, y entonces el bucle de error tras −302 ya da la misma ventana. No añade una vía sin depurador.

## 5. Inventario de lo estático (después de R41)

| Elemento | Estado |
|---|---|
| BootROM (57 rutinas, R22/R23), Loader2 (247/247, R24), Loader3 (674/674, R25) | Mapeados; con R41 no queda ninguna función del camino de error sin examinar |
| Prefijo de Loader3 (43 páginas, INFO5) | Completo. La cola INFO6 (21 páginas: `c020xxxx`, libc y destino tras ICE) no está en ningún volcado (`E26-R5-L3`) |
| Entradas por software a modo 3 | Solo `\updater\mode` (R37); modo 5 (`chk ank`/`chk adjust`) lee `nflasha3` |
| Canales de entrada sin abrir la cámara | USB = Darwin HID sin escritura (R10/R19); consola serie de Loader3 = muda y de solo lectura (R41); BootROM serie = con clave (R33) |
| Pendientes offline vivos | `E26-R30-HOSTRET0` (baja), `E26-R5-FM3` (falta el manual de flash) |

## 6. Límites

- `c020c224`/`c020c0b8` se identifican por su uso (`strncmp`/`strtoul`); su código no está en el volcado.
- El valor de `[0xc006000c]` con la consola apagada y la bola física del GPIO 14.17 no se han determinado.
- El reloj de la UART (48 MHz → 115 200 baudios) es inferencia.
- Nada de lo anterior autoriza ni prueba una conexión o una escritura.
